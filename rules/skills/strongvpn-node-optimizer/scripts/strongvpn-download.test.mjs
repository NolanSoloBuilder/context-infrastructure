import test from 'node:test';
import assert from 'node:assert/strict';
import { createPrivateKey, createPublicKey } from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { mkdtemp, readFile, rm, stat, symlink, writeFile } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  SOURCES, createWireGuardKeys, formatDownloadedConfig, generateDownload,
  downloadToFile, parseDownloadArgs, runDownloader,
} from './strongvpn-download.mjs';

const server = { id: 'str-nrt301', ip: '192.0.2.1' };
const response = () => ({
  success: true,
  config: {
    Interface: { Address: '10.0.0.2/32, fd00::2/128', DNS: ['1.1.1.1', '2606:4700:4700::1111'] },
    Peer: { PublicKey: Buffer.alloc(32, 7).toString('base64'), AllowedIPs: ['0.0.0.0/0'] },
  },
});

test('built-in X25519 keys have WireGuard clamping and the matching public key', () => {
  const keys = createWireGuardKeys();
  const raw = Buffer.from(keys.privateKey, 'base64');
  assert.equal(raw.length, 32);
  assert.equal(raw[0] & 7, 0);
  assert.equal(raw[31] & 128, 0);
  assert.equal(raw[31] & 64, 64);
  const privateKey = createPrivateKey({ key: { kty: 'OKP', crv: 'X25519', d: raw.toString('base64url'), x: Buffer.from(keys.publicKey, 'base64').toString('base64url') }, format: 'jwk' });
  const derived = createPublicKey(privateKey).export({ format: 'jwk' });
  assert.equal(Buffer.from(derived.x, 'base64url').toString('base64'), keys.publicKey);
});

test('config follows API AllowedIPs and supports IPv6 endpoint formatting', () => {
  const keys = createWireGuardKeys();
  const config = formatDownloadedConfig(response(), { ...server, ip: '2001:db8::1' }, keys, 55000);
  assert.match(config, /^AllowedIPs = 0\.0\.0\.0\/0$/m);
  assert.match(config, /^Endpoint = \[2001:db8::1\]:55000$/m);
});

test('rejects newline directive injection and invalid CIDRs from the generator', () => {
  for (const mutate of [
    (data) => { data.config.Interface.Address = '10.0.0.2/32\nPostUp = bad'; },
    (data) => { data.config.Interface.DNS = ['1.1.1.1\nPostUp = bad']; },
    (data) => { data.config.Peer.AllowedIPs = ['0.0.0.0/33']; },
    (data) => { data.config.Peer.PublicKey += '\n'; },
  ]) {
    const data = response();
    mutate(data);
    assert.throws(() => formatDownloadedConfig(data, server, createWireGuardKeys()), /无效/);
  }
});

test('sends only public key to the exact generator and refuses redirects', async () => {
  const keys = createWireGuardKeys();
  await generateDownload({ baseUrl: SOURCES.strongvpn, server, keys, credentials: { username: 'a000000', password: 'test-only-password' }, fetchImpl: async (url, options) => {
    assert.equal(url, 'https://tools.strongvpn.asia/wg-generate');
    assert.equal(options.redirect, 'error');
    const body = JSON.parse(options.body);
    assert.equal(body.publickey, keys.publicKey);
    assert.equal(body.server, server.id);
    assert.ok(!options.body.includes(keys.privateKey));
    return { ok: true, json: async () => response() };
  } });
});

test('uncertain POST and failed API responses are never retried or echoed', async () => {
  for (const kind of ['timeout', 'http', 'rejected', 'json']) {
    let calls = 0;
    const options = {
      baseUrl: SOURCES.strongvpn, server, keys: createWireGuardKeys(), credentials: { username: 'a000000', password: 'test-only-password' },
      fetchImpl: async () => {
        calls += 1;
        if (kind === 'timeout') throw new Error('sensitive response content');
        return { ok: kind !== 'http', status: 403, json: async () => {
          if (kind === 'json') throw new Error('sensitive response content');
          return { success: false, message: 'sensitive response content' };
        } };
      },
    };
    await assert.rejects(generateDownload(options), (error) => !error.message.includes('sensitive response content'));
    assert.equal(calls, 1);
  }
});

test('exclusive output is 0600, never overwrites files/symlinks or generates on collision', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'strongvpn-download-'));
  try {
    const output = join(dir, 'node.conf');
    await downloadToFile({ output, generate: async () => 'private test fixture' });
    assert.equal((await stat(output)).mode & 0o777, 0o600);
    let calls = 0;
    const generate = async () => { calls += 1; return 'replacement'; };
    await assert.rejects(downloadToFile({ output, generate }), /已存在/);
    const link = join(dir, 'link.conf');
    await symlink(output, link);
    await assert.rejects(downloadToFile({ output: link, generate }), /已存在/);
    assert.equal(calls, 0);
    assert.equal(await readFile(output, 'utf8'), 'private test fixture');
  } finally { await rm(dir, { recursive: true, force: true }); }
});

test('generation failure removes only the reserved output', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'strongvpn-download-'));
  try {
    const output = join(dir, 'failed.conf');
    const previous = join(dir, 'current.conf');
    await writeFile(previous, 'previous configuration');
    await assert.rejects(downloadToFile({ output, generate: async () => { throw new Error('rejected'); } }), /rejected/);
    await assert.rejects(stat(output), { code: 'ENOENT' });
    assert.equal(await readFile(previous, 'utf8'), 'previous configuration');
  } finally { await rm(dir, { recursive: true, force: true }); }
});

test('CLI rejects ambiguous arguments and requires username with stdin', () => {
  assert.equal(parseDownloadArgs(['servers', '日本']).selector, '日本');
  assert.equal(parseDownloadArgs(['download', server.id, '--output', '/tmp/node.conf']).output, '/tmp/node.conf');
  assert.throws(() => parseDownloadArgs(['download', server.id, '--source', 'other']), /source/);
  assert.throws(() => parseDownloadArgs(['download', server.id, '--password-stdin']), /username/);
  assert.throws(() => parseDownloadArgs(['download', server.id, 'extra']), /一次/);
});

test('public servers JSON includes the actual page and imported catalog URLs', async () => {
  const originalFetch = globalThis.fetch;
  const originalLog = console.log;
  const output = [];
  const calls = [];
  globalThis.fetch = async (url) => {
    calls.push(url);
    if (url.endsWith('/strong-wg.html')) return new Response(`<select id="serverSelect"></select>
      <script type="module">import { servers, serverMapping } from './live.js?v=3';</script>`);
    assert.equal(url, `${SOURCES.strongvpn}/live.js?v=3`);
    return new Response(`export const serverMapping = {'str-nrt301': {ip: atob('MTkyLjAuMi4x')}};
      export const servers = {'Japan': [{value:'str-nrt301',label:'Tokyo'}]};`);
  };
  console.log = (value) => output.push(value);
  try {
    await runDownloader(['servers', '日本', '--json']);
    const parsed = JSON.parse(output[0]);
    assert.equal(parsed.pageUrl, `${SOURCES.strongvpn}/strong-wg.html`);
    assert.equal(parsed.catalogUrl, `${SOURCES.strongvpn}/live.js?v=3`);
    assert.deepEqual(parsed.servers.map(({ id }) => id), ['str-nrt301']);
    assert.equal(calls.length, 2);
  } finally {
    globalThis.fetch = originalFetch;
    console.log = originalLog;
  }
});

test('global symlink CLI works and importing from stdin causes no CLI side effects', async () => {
  const dir = await mkdtemp(join(tmpdir(), 'strongvpn-cli-'));
  try {
    const source = fileURLToPath(new URL('./strongvpn-node-optimizer.mjs', import.meta.url));
    const link = join(dir, 'cli.mjs');
    await symlink(source, link);
    const cli = spawnSync(process.execPath, [link, '--help'], { encoding: 'utf8' });
    assert.equal(cli.status, 0, cli.stderr);
    assert.match(cli.stdout, /download <节点ID>/);
    const imported = spawnSync(process.execPath, ['--input-type=module', '-'], {
      encoding: 'utf8', input: `await import(${JSON.stringify(new URL('./strongvpn-download.mjs', import.meta.url).href)});`,
    });
    assert.equal(imported.status, 0, imported.stderr);
    assert.equal(imported.stdout, '');
  } finally { await rm(dir, { recursive: true, force: true }); }
});
