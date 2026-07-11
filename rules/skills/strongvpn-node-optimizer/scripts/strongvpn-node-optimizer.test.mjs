import test from 'node:test';
import assert from 'node:assert/strict';

import {
  classifyPreferredRegion,
  fetchServerCatalog,
  generateConfig,
  parseServersModule,
  readCredentials,
  redactSensitive,
  isFreshCache,
  scoreCandidate,
} from './strongvpn-node-optimizer.mjs';

const fixture = `
export const serverMapping = {
  'str-sin303': { ip: atob('MjAzLjAuMTEzLjEw') },
  'str-nrt301': { ip: atob('MjAzLjAuMTEzLjEx') },
  'str-lax311': { ip: atob('MjAzLjAuMTEzLjEy') },
};
export const servers = {
  'Singapore': [{ value: 'str-sin303', label: 'Singapore' }],
  'Japan': [{ value: 'str-nrt301', label: 'Tokyo, Japan' }],
  'USA': [{ value: 'str-lax311', label: 'Los Angeles, USA' }],
};`;

test('parses StrongVPN catalog without executing remote code', () => {
  const parsed = parseServersModule(fixture);

  assert.deepEqual(
    parsed.map(({ id, country, ip }) => ({ id, country, ip })),
    [
      { id: 'str-sin303', country: 'Singapore', ip: '203.0.113.10' },
      { id: 'str-nrt301', country: 'Japan', ip: '203.0.113.11' },
      { id: 'str-lax311', country: 'USA', ip: '203.0.113.12' },
    ],
  );
  assert.equal(classifyPreferredRegion(parsed[0]), 'singapore');
  assert.equal(classifyPreferredRegion(parsed[1]), 'japan');
  assert.equal(classifyPreferredRegion(parsed[2]), 'us-west');
});

test('rejects executable expressions outside supported atob mappings', () => {
  assert.throws(
    () => parseServersModule("export const serverMapping = {}; export const servers = {}; fetch('x')"),
    /unsupported/i,
  );
});

test('rejects a server without an IP mapping', () => {
  const missingMapping = `
    export const serverMapping = {};
    export const servers = { 'Japan': [{ value: 'str-nrt301', label: 'Tokyo' }] };
  `;
  assert.throws(() => parseServersModule(missingMapping), /mapping/i);
});

test('ignores servers that are commented out in the official catalog', () => {
  const withDisabledServer = `
    export const serverMapping = {
      'str-lax308': { ip: atob('MjAzLjAuMTEzLjEz') },
      'str-lax311': { ip: atob('MjAzLjAuMTEzLjEy') },
    };
    export const servers = {
      'USA': [
        // { value: 'str-lax308', label: 'Los Angeles, USA' },
        { value: 'str-lax311', label: 'Los Angeles, USA' },
      ],
    };
  `;

  assert.deepEqual(parseServersModule(withDisabledServer).map(({ id }) => id), ['str-lax311']);
});

test('falls back to the secondary catalog source', async () => {
  const calls = [];
  const fetchImpl = async (url) => {
    calls.push(String(url));
    if (String(url).includes('strongvpn.asia')) throw new Error('primary unavailable');
    return new Response(fixture, { status: 200 });
  };

  const result = await fetchServerCatalog({
    baseUrls: [
      'https://tools.strongvpn.asia/share/strong-wg',
      'https://tools.strongtech.org/share/strong-wg',
    ],
    fetchImpl,
  });

  assert.equal(result.baseUrl, 'https://tools.strongtech.org/share/strong-wg');
  assert.equal(result.servers.length, 3);
  assert.equal(calls.length, 2);
});

test('builds a full-tunnel config and falls back between generator APIs', async () => {
  const fetchImpl = async (url, options) => {
    if (String(url).includes('strongvpn.asia')) throw new Error('primary unavailable');
    assert.equal(options.method, 'POST');
    return Response.json({
      success: true,
      config: {
        Interface: { Address: '10.0.0.2/32', DNS: ['1.1.1.1', '1.0.0.1'] },
        Peer: { PublicKey: 'peer-public-key', AllowedIPs: ['0.0.0.0/0'] },
      },
    });
  };

  const result = await generateConfig({
    baseUrls: [
      'https://tools.strongvpn.asia/share/strong-wg',
      'https://tools.strongtech.org/share/strong-wg',
    ],
    server: { id: 'str-sin303', ip: '203.0.113.10', label: 'Singapore', country: 'Singapore' },
    credentials: { username: 'a000000', password: '0123456789' },
    keyPair: { privateKey: 'private-key', publicKey: 'public-key' },
    fetchImpl,
    randomPort: () => 55001,
  });

  assert.match(result.config, /AllowedIPs = 0\.0\.0\.0\/0, ::\/0/);
  assert.match(result.config, /Endpoint = 203\.0\.113\.10:55001/);
  assert.match(result.config, /DNS = 1\.1\.1\.1, 1\.0\.0\.1/);
  const redacted = JSON.stringify(redactSensitive(result, ['private-key', '0123456789']));
  assert.equal(redacted.includes('private-key'), false);
  assert.equal(redacted.includes('0123456789'), false);
});

test('rejects malformed generator API responses', async () => {
  await assert.rejects(
    () => generateConfig({
      baseUrls: ['https://example.test'],
      server: { id: 'str-sin303', ip: '203.0.113.10' },
      credentials: { username: 'a000000', password: '0123456789' },
      keyPair: { privateKey: 'private-key', publicKey: 'public-key' },
      fetchImpl: async () => Response.json({ success: true, config: {} }),
      randomPort: () => 55001,
    }),
    /schema/i,
  );
});

test('reads credentials from Keychain without exposing security stderr', async () => {
  const runner = async (_command, args) => {
    if (args.includes('-w')) return { stdout: '0123456789\n', stderr: '' };
    return {
      stdout: '',
      stderr: 'keychain: "/Users/test/Library/Keychains/login.keychain-db"\nacct<blob>="a000000"\n',
    };
  };

  assert.deepEqual(await readCredentials(runner), {
    username: 'a000000',
    password: '0123456789',
  });
});

test('ranks a stable node above a one-off fast node', () => {
  const stable = scoreCandidate([
    { ok: true, coreOk: true, tls: 0.14, ttfb: 0.20, total: 0.30, throughput: 8 },
    { ok: true, coreOk: true, tls: 0.15, ttfb: 0.21, total: 0.31, throughput: 8 },
    { ok: true, coreOk: true, tls: 0.15, ttfb: 0.22, total: 0.32, throughput: 8 },
  ]);
  const flaky = scoreCandidate([
    { ok: true, coreOk: true, tls: 0.08, ttfb: 0.10, total: 0.20, throughput: 12 },
    { ok: false, coreOk: false },
    { ok: true, coreOk: true, tls: 0.80, ttfb: 1.20, total: 2.00, throughput: 3 },
  ]);

  assert.ok(stable.score > flaky.score);
  assert.equal(stable.eligible, true);
  assert.equal(flaky.eligible, false);
  assert.equal(stable.successRate, 1);
});

test('cache expires exactly after 24 hours', () => {
  const base = Date.parse('2026-07-11T00:00:00Z');
  assert.equal(isFreshCache('2026-07-11T00:00:00Z', base + 86_399_999), true);
  assert.equal(isFreshCache('2026-07-11T00:00:00Z', base + 86_400_000), false);
  assert.equal(isFreshCache('invalid', base), false);
});
