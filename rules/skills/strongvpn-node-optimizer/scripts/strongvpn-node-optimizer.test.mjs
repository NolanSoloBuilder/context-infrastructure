import test from 'node:test';
import assert from 'node:assert/strict';

import {
  classifyPreferredRegion,
  fetchServerCatalog,
  generateConfig,
  parseServersModule,
  readCredentials,
  redactSensitive,
  runPrivileged,
  isFreshCache,
  isProtectedVpnApp,
  scoreCandidate,
  promoteWinningConfig,
  parseCurlMetrics,
  parseVpnConnections,
  selectCandidates,
  withNetworkTransaction,
} from './strongvpn-node-optimizer.mjs';

test('treats REDpass as a protected network base instead of a conflicting VPN', () => {
  assert.equal(isProtectedVpnApp('REDpass'), true);
  assert.equal(isProtectedVpnApp('OpenVPN Connect'), false);
  assert.equal(isProtectedVpnApp('StrongVPN'), false);
});

test('parses only connected macOS VPN services', () => {
  const output = `
Available network connection services in the current set (*=enabled):
* (Connected)      8C95BBD3-1111-2222-3333-123456789ABC VPN (com.example) "StrongVPN" [VPN:com.example]
* (Disconnected)   AAAAAAAA-1111-2222-3333-123456789ABC VPN (net.openvpn) "OpenVPN" [VPN:net.openvpn]
`;

  assert.deepEqual(parseVpnConnections(output), [
    { id: '8C95BBD3-1111-2222-3333-123456789ABC', name: 'StrongVPN' },
  ]);
});

test('parses curl metrics and treats reachable HTTP errors as transport success', () => {
  const parsed = parseCurlMetrics('{"http_code":401,"time_appconnect":0.12,"time_starttransfer":0.20,"time_total":0.25,"speed_download":4000000}');

  assert.deepEqual(parsed, {
    ok: true,
    httpCode: 401,
    tls: 0.12,
    ttfb: 0.20,
    total: 0.25,
    throughput: 32,
  });
  assert.equal(parseCurlMetrics('{"http_code":000,"time_total":10}').ok, false);
});

test('falls back to the macOS authorization dialog when sudo is not cached', async () => {
  const calls = [];
  const runner = async (command, args) => {
    calls.push({ command, args });
    return command === 'sudo' ? { code: 1, stdout: '', stderr: '' } : { code: 0, stdout: '', stderr: '' };
  };

  await runPrivileged('wg', ['show', 'svpn0'], runner);

  assert.equal(calls[0].command, 'sudo');
  assert.equal(calls[1].command, 'osascript');
  assert.match(calls[1].args.at(-1), /^'\/opt\/homebrew\/bin\/wg' 'show' 'svpn0'$/);
});

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

const generatorPage = (specifier = './servers.js') => `
<select id="serverSelect"></select>
<script type="module">import { servers, serverMapping } from '${specifier}';</script>`;

async function catalogFromPage(page, source = fixture) {
  const calls = [];
  const result = await fetchServerCatalog({
    baseUrls: ['https://primary.test/share/strong-wg'],
    fetchImpl: async (url, options) => {
      calls.push(String(url));
      assert.equal(options.redirect, 'error');
      return new Response(calls.length === 1 ? page : source, { status: 200 });
    },
  });
  return { result, calls };
}

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

test('ignores inline and block comments without deleting comment markers inside strings', () => {
  const source = `
    export const serverMapping = {
      'str-old001': { ip: atob('MTkyLjAuMi4x') },
      'str-old002': { ip: atob('MTkyLjAuMi4y') },
      'str-live001': { ip: atob('MTkyLjAuMi4z') },
    };
    export const servers = { 'Test': [
      /* { value: 'str-old001', label: 'Old block entry' }, */
      { value: 'str-live001', label: 'https://example.test/a/*b*/' }, // { value: 'str-old002', label: 'Old inline entry' }
    ] };
  `;
  const parsed = parseServersModule(source);
  assert.deepEqual(parsed.map(({ id }) => id), ['str-live001']);
  assert.equal(parsed[0].label, 'https://example.test/a/*b*/');
});

test('rejects unterminated block comments instead of returning a partial catalog', () => {
  assert.throws(() => parseServersModule(`${fixture}\n/* old catalog`), /unterminated.*comment/i);
});

test('does not add mapping-only servers and rejects unsafe selectable IDs', () => {
  const mappingOnly = fixture.replace("'USA': [{ value: 'str-lax311', label: 'Los Angeles, USA' }],", '');
  assert.deepEqual(parseServersModule(mappingOnly).map(({ id }) => id), ['str-sin303', 'str-nrt301']);
  assert.throws(() => parseServersModule(fixture.replaceAll('str-lax311', '../str-lax311')), /ID shape/i);
});

test('fetches the current page and follows its actual named import with version query', async () => {
  const page = generatorPage('./current-catalog.js?v=20261015');
  const { result, calls } = await catalogFromPage(page);
  assert.deepEqual(calls, [
    'https://primary.test/share/strong-wg/strong-wg.html',
    'https://primary.test/share/strong-wg/current-catalog.js?v=20261015',
  ]);
  assert.equal(result.pageUrl, calls[0]);
  assert.equal(result.catalogUrl, calls[1]);
  assert.equal(result.servers.length, 3);
});

test('only follows real module imports, ignoring imports inside comments and strings', async () => {
  const page = `<select id='serverSelect'></select>
    <!-- <script type="module">import { servers, serverMapping } from './old-html.js';</script> -->
    <script>const irrelevant = "import { servers, serverMapping } from './classic.js'";</script>
    <script type='module'>
      // import { servers, serverMapping } from './old-line.js';
      /* import { servers, serverMapping } from './old-block.js'; */
      const note = "import { servers, serverMapping } from './inside-string.js'";
      import { serverMapping, /* current */ servers, } from './live.js?v=2';
    </script>`;
  const { calls } = await catalogFromPage(page);
  assert.equal(calls[1], 'https://primary.test/share/strong-wg/live.js?v=2');
});

test('fails closed on cross-origin imports, missing select, and ambiguous or changed page formats', async () => {
  const pages = [
    generatorPage('https://other.test/catalog.js'),
    generatorPage('http://primary.test/catalog.js'),
    generatorPage('servers.js'),
    generatorPage().replace('<select id="serverSelect"></select>', ''),
    generatorPage().replace('<select id="serverSelect">', '<select id="serverSelect" disabled>'),
    generatorPage().replace('type="module"', 'type="text/javascript"'),
    `${generatorPage()}<script type="module">import { servers, serverMapping } from './other.js';</script>`,
    `${generatorPage()}<script type="module">import { servers as otherServers, serverMapping as otherMapping } from './other.js';</script>`,
    generatorPage().replace('servers, serverMapping', 'servers, serverMapping, extra'),
    `${generatorPage()}<base href="/different/">`,
    '<select id="serverSelect"></select><script type="module" src="./app.js"></script>',
    generatorPage().replace("import {", "/* import {"),
  ];
  for (const page of pages) {
    let calls = 0;
    await assert.rejects(fetchServerCatalog({
      baseUrls: ['https://primary.test/share/strong-wg'],
      fetchImpl: async () => { calls += 1; return new Response(page); },
    }), /catalog unavailable/i);
    assert.equal(calls, 1, 'must not guess or fetch a data module after page validation fails');
  }
});

test('falls back to the secondary catalog source', async () => {
  const calls = [];
  const fetchImpl = async (url) => {
    calls.push(String(url));
    if (String(url).includes('strongvpn.asia')) throw new Error('primary unavailable');
    return new Response(String(url).endsWith('/strong-wg.html') ? generatorPage('./mirror.js?rev=2') : fixture, { status: 200 });
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
  assert.deepEqual(calls, [
    'https://tools.strongvpn.asia/share/strong-wg/strong-wg.html',
    'https://tools.strongtech.org/share/strong-wg/strong-wg.html',
    'https://tools.strongtech.org/share/strong-wg/mirror.js?rev=2',
  ]);
});

const generatorKeys = {
  privateKey: Buffer.alloc(32, 1).toString('base64'),
  publicKey: Buffer.alloc(32, 2).toString('base64'),
};
const generatorResponse = () => ({
  success: true,
  config: {
    Interface: { Address: '10.0.0.2/32', DNS: ['1.1.1.1', '1.0.0.1'] },
    Peer: { PublicKey: Buffer.alloc(32, 7).toString('base64'), AllowedIPs: ['0.0.0.0/0'] },
  },
});
const generationOptions = () => ({
  baseUrls: ['https://tools.strongtech.org/share/strong-wg', 'https://tools.strongvpn.asia/share/strong-wg'],
  server: { id: 'str-sin303', ip: '2001:db8::10', label: 'Singapore', country: 'Singapore' },
  credentials: { username: 'a000000', password: '0123456789' },
  keyPair: generatorKeys,
  randomPort: () => 55001,
});

test('benchmark generation shares validated routes and IPv6 formatting with downloads', async () => {
  let calls = 0;
  const result = await generateConfig({
    ...generationOptions(),
    fetchImpl: async (url, options) => {
      calls += 1;
      assert.equal(url, 'https://tools.strongtech.org/wg-generate');
      assert.equal(options.method, 'POST');
      assert.equal(options.redirect, 'error');
      assert.ok(!options.body.includes(generatorKeys.privateKey));
      return Response.json(generatorResponse());
    },
  });
  assert.equal(calls, 1);
  assert.match(result.config, /^AllowedIPs = 0\.0\.0\.0\/0$/m);
  assert.match(result.config, /Endpoint = \[2001:db8::10\]:55001/);
  assert.match(result.config, /DNS = 1\.1\.1\.1, 1\.0\.0\.1/);
  const redacted = JSON.stringify(redactSensitive(result, [generatorKeys.privateKey, '0123456789']));
  assert.equal(redacted.includes(generatorKeys.privateKey), false);
  assert.equal(redacted.includes('0123456789'), false);
});

test('benchmark generation never retries mirrors or echoes uncertain errors', async () => {
  for (const failure of ['timeout', 'http', 'schema']) {
    let calls = 0;
    await assert.rejects(generateConfig({
      ...generationOptions(),
      fetchImpl: async () => {
        calls += 1;
        if (failure === 'timeout') throw new Error('private response content');
        if (failure === 'http') return new Response('private response content', { status: 503 });
        return Response.json({ success: true, config: {} });
      },
    }), (error) => error.stopBenchmark === true && !error.message.includes('private response content'));
    assert.equal(calls, 1);
  }
});

test('invalid benchmark endpoint is rejected before registration', async () => {
  let calls = 0;
  await assert.rejects(generateConfig({
    ...generationOptions(), randomPort: () => 0,
    fetchImpl: async () => { calls += 1; return Response.json(generatorResponse()); },
  }), /port/i);
  assert.equal(calls, 0);
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

test('accepts StrongVPN passwords that are not exactly ten characters', async () => {
  const runner = async (_command, args) => args.includes('-w')
    ? { stdout: '01234567890\n', stderr: '' }
    : { stdout: '', stderr: 'acct<blob>="a000000"\n' };

  assert.equal((await readCredentials(runner)).password.length, 11);
});

test('parses the quoted acct field emitted by current macOS security', async () => {
  const runner = async (_command, args) => args.includes('-w')
    ? { stdout: '01234567890\n', stderr: '' }
    : { stdout: '    "acct"<blob>="a000000"\n', stderr: '' };

  assert.equal((await readCredentials(runner)).username, 'a000000');
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

function fakeNetworkAdapter(events) {
  return {
    async snapshot() {
      events.push('snapshot');
      return { connectedServices: ['company-vpn'] };
    },
    async stopConflicts() {
      events.push('stop-conflicts');
    },
    async cleanupManagedTunnel() {
      events.push('cleanup-new');
    },
    async restore() {
      events.push('restore');
      return { complete: true };
    },
  };
}

test('commits a successful switch without restoring conflicting VPNs', async () => {
  const events = [];
  const result = await withNetworkTransaction(fakeNetworkAdapter(events), async () => {
    events.push('new-tunnel-up');
    return { winner: 'str-sin303' };
  });

  assert.deepEqual(result, { winner: 'str-sin303' });
  assert.deepEqual(events, ['snapshot', 'stop-conflicts', 'new-tunnel-up']);
});

test('cleans up and restores previous VPN state when switching fails', async () => {
  const events = [];
  await assert.rejects(
    () => withNetworkTransaction(fakeNetworkAdapter(events), async () => {
      events.push('new-tunnel-failed');
      throw new Error('handshake timeout');
    }),
    /handshake timeout/,
  );

  assert.deepEqual(events, [
    'snapshot',
    'stop-conflicts',
    'new-tunnel-failed',
    'cleanup-new',
    'restore',
  ]);
});

test('selects at most six candidates with preferred-region diversity', () => {
  const servers = [
    { id: 'sin-1', region: 'singapore' },
    { id: 'sin-2', region: 'singapore' },
    { id: 'jp-1', region: 'japan' },
    { id: 'jp-2', region: 'japan' },
    { id: 'tw-1', region: 'taiwan' },
    { id: 'tw-2', region: 'taiwan' },
    { id: 'us-1', region: 'us-west' },
    { id: 'us-2', region: 'us-west' },
  ];
  const preflight = new Map(servers.map((server, index) => [server.id, { latency: 10 + index }]));

  const selected = selectCandidates(servers, preflight, 6);

  assert.equal(selected.length, 6);
  assert.deepEqual(selected.slice(0, 4).map(({ region }) => region), [
    'singapore',
    'japan',
    'taiwan',
    'us-west',
  ]);
});

class MemoryStore {
  constructor() {
    this.files = new Map();
  }

  async read(path) {
    return this.files.get(path) ?? null;
  }

  async write(path, value) {
    this.files.set(path, value);
  }

  async remove(path) {
    this.files.delete(path);
  }

  async list(prefix) {
    return [...this.files.keys()].filter((path) => path.startsWith(prefix)).toSorted();
  }
}

test('keeps only current and previous winning configs', async () => {
  const store = new MemoryStore();
  await promoteWinningConfig(store, 'winner-config');
  await promoteWinningConfig(store, 'new-winner-config');

  assert.equal(await store.read('configs/current.conf'), 'new-winner-config');
  assert.equal(await store.read('configs/previous.conf'), 'winner-config');
  assert.deepEqual(await store.list('configs/'), [
    'configs/current.conf',
    'configs/previous.conf',
  ]);
});
