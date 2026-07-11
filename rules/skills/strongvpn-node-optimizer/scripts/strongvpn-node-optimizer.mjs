#!/usr/bin/env node

import { spawn } from 'node:child_process';
import { chmod, mkdir, readFile, readdir, rename, rm, writeFile } from 'node:fs/promises';
import { isIP } from 'node:net';
import { homedir } from 'node:os';
import { basename, dirname, join, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const REGION_PATTERNS = [
  ['singapore', /singapore|\bsin\b/i],
  ['japan', /japan|tokyo|osaka|\btyo\b|\bnrt\b|\bkix\b/i],
  ['taiwan', /taiwan|taipei|\btpe\b/i],
  ['us-west', /los angeles|san jose|seattle|\blax\b|\bsjc\b|\bsea\b/i],
];

const UNSUPPORTED_SOURCE = /\b(?:fetch|function|eval|require|process|globalThis|import)\b|=>|\bnew\s+/;

export function classifyPreferredRegion(server) {
  const haystack = `${server.country ?? ''} ${server.label ?? ''} ${server.id ?? ''}`;
  return REGION_PATTERNS.find(([, pattern]) => pattern.test(haystack))?.[0] ?? null;
}

function extractObject(source, name) {
  const marker = `export const ${name}`;
  const start = source.indexOf(marker);
  if (start === -1) throw new Error(`Missing ${name} mapping`);
  const open = source.indexOf('{', start + marker.length);
  if (open === -1) throw new Error(`Missing ${name} object`);

  let depth = 0;
  let quote = null;
  let escaped = false;
  for (let index = open; index < source.length; index += 1) {
    const char = source[index];
    if (quote) {
      if (escaped) escaped = false;
      else if (char === '\\') escaped = true;
      else if (char === quote) quote = null;
      continue;
    }
    if (char === "'" || char === '"') {
      quote = char;
      continue;
    }
    if (char === '{') depth += 1;
    if (char === '}') {
      depth -= 1;
      if (depth === 0) return source.slice(open + 1, index);
    }
  }
  throw new Error(`Unterminated ${name} object`);
}

export function parseServersModule(source) {
  if (typeof source !== 'string') {
    throw new Error('Unsupported server catalog type');
  }
  const sanitizedSource = source.replace(/^\s*\/\/.*$/gm, '');
  if (UNSUPPORTED_SOURCE.test(sanitizedSource)) {
    throw new Error('Unsupported executable expression in server catalog');
  }

  const mappingBody = extractObject(sanitizedSource, 'serverMapping');
  const serversBody = extractObject(sanitizedSource, 'servers');
  const mappings = new Map();
  const mappingPattern = /['"]([^'"]+)['"]\s*:\s*\{\s*ip\s*:\s*atob\(\s*['"]([A-Za-z0-9+/=]+)['"]\s*\)\s*\}/g;
  for (const match of mappingBody.matchAll(mappingPattern)) {
    const ip = Buffer.from(match[2], 'base64').toString('utf8');
    if (!isIP(ip)) throw new Error(`Invalid IP mapping for ${match[1]}`);
    if (mappings.has(match[1])) throw new Error(`Duplicate server mapping: ${match[1]}`);
    mappings.set(match[1], ip);
  }

  const result = [];
  const seen = new Set();
  const countryPattern = /['"]([^'"]+)['"]\s*:\s*\[([\s\S]*?)\](?:\s*,|\s*$)/g;
  const entryPattern = /\{\s*value\s*:\s*['"]([^'"]+)['"]\s*,\s*label\s*:\s*['"]([^'"]+)['"]\s*\}/g;
  for (const countryMatch of serversBody.matchAll(countryPattern)) {
    const country = countryMatch[1];
    for (const entryMatch of countryMatch[2].matchAll(entryPattern)) {
      const id = entryMatch[1];
      const ip = mappings.get(id);
      if (!ip) throw new Error(`Missing IP mapping for ${id}`);
      if (seen.has(id)) throw new Error(`Duplicate server ID: ${id}`);
      seen.add(id);
      const server = { id, label: entryMatch[2], country, ip };
      result.push({ ...server, region: classifyPreferredRegion(server) });
    }
  }

  if (result.length === 0) throw new Error('Server catalog contained no usable servers');
  return result;
}

export async function fetchServerCatalog({ baseUrls, fetchImpl = fetch }) {
  const errors = [];
  for (const baseUrl of baseUrls) {
    try {
      const response = await fetchImpl(`${baseUrl}/servers.js`);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return { baseUrl, servers: parseServersModule(await response.text()) };
    } catch (error) {
      errors.push(`${new URL(baseUrl).host}: ${error.message}`);
    }
  }
  throw new Error(`StrongVPN server catalog unavailable (${errors.join('; ')})`);
}

function assertCredentials(credentials) {
  const passwordLength = String(credentials?.password ?? '').length;
  if (!/^a\d{6}$/.test(credentials?.username ?? '') || passwordLength < 8 || passwordLength > 128) {
    throw new Error('StrongVPN credentials are invalid');
  }
}

export async function readCredentials(runner) {
  const metadata = await runner('security', [
    'find-generic-password',
    '-s',
    'strongvpn-node-optimizer',
    '-g',
  ], { captureStderr: true });
  const metadataText = `${metadata?.stdout ?? ''}\n${metadata?.stderr ?? ''}`;
  const accountMatch = metadataText.match(/"?acct"?<blob>="([^"]+)"/);
  const passwordResult = await runner('security', [
    'find-generic-password',
    '-s',
    'strongvpn-node-optimizer',
    '-w',
  ], { captureStderr: true });
  const credentials = {
    username: accountMatch?.[1] ?? '',
    password: String(passwordResult?.stdout ?? '').trim(),
  };
  assertCredentials(credentials);
  return credentials;
}

function assertGeneratorSchema(data) {
  const interfaceConfig = data?.config?.Interface;
  const peerConfig = data?.config?.Peer;
  if (
    data?.success !== true
    || typeof interfaceConfig?.Address !== 'string'
    || !Array.isArray(interfaceConfig?.DNS)
    || interfaceConfig.DNS.some((entry) => typeof entry !== 'string')
    || typeof peerConfig?.PublicKey !== 'string'
    || peerConfig.PublicKey.length === 0
  ) {
    throw new Error('StrongVPN generator response schema was invalid');
  }
  return { interfaceConfig, peerConfig };
}

export async function generateConfig({
  baseUrls,
  server,
  credentials,
  keyPair,
  fetchImpl = fetch,
  randomPort = () => Math.floor(Math.random() * 5001) + 55000,
}) {
  assertCredentials(credentials);
  if (!server?.id || !isIP(server?.ip ?? '')) throw new Error('StrongVPN server mapping was invalid');
  if (!keyPair?.privateKey || !keyPair?.publicKey) throw new Error('WireGuard key pair was invalid');

  const errors = [];
  for (const baseUrl of baseUrls) {
    try {
      const response = await fetchImpl(`${baseUrl}/wg-generate`, {
        method: 'POST',
        headers: { 'content-type': 'application/json' },
        body: JSON.stringify({
          aiouser: credentials.username,
          aiopass: credentials.password,
          server: server.id,
          publickey: keyPair.publicKey,
        }),
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const { interfaceConfig, peerConfig } = assertGeneratorSchema(await response.json());
      const port = Number(randomPort());
      if (!Number.isInteger(port) || port < 55000 || port > 60000) {
        throw new Error('WireGuard endpoint port was invalid');
      }
      const config = [
        '[Interface]',
        `PrivateKey = ${keyPair.privateKey}`,
        `Address = ${interfaceConfig.Address}`,
        `DNS = ${interfaceConfig.DNS.join(', ')}`,
        '',
        '[Peer]',
        `PublicKey = ${peerConfig.PublicKey}`,
        'AllowedIPs = 0.0.0.0/0, ::/0',
        `Endpoint = ${server.ip}:${port}`,
        '',
      ].join('\n');
      return { server, config, publicKey: keyPair.publicKey, baseUrl };
    } catch (error) {
      errors.push(`${new URL(baseUrl).host}: ${error.message}`);
    }
  }
  throw new Error(`StrongVPN config generation failed (${errors.join('; ')})`);
}

export function redactSensitive(value, secrets = []) {
  const normalizedSecrets = secrets.filter(Boolean).map(String);
  if (typeof value === 'string') {
    return normalizedSecrets.reduce(
      (text, secret) => text.split(secret).join('[REDACTED]'),
      value,
    );
  }
  if (Array.isArray(value)) return value.map((item) => redactSensitive(item, normalizedSecrets));
  if (value && typeof value === 'object') {
    return Object.fromEntries(
      Object.entries(value).map(([key, item]) => [key, redactSensitive(item, normalizedSecrets)]),
    );
  }
  return value;
}

function median(values) {
  const sorted = values.filter(Number.isFinite).toSorted((a, b) => a - b);
  if (sorted.length === 0) return null;
  const middle = Math.floor(sorted.length / 2);
  return sorted.length % 2 === 0
    ? (sorted[middle - 1] + sorted[middle]) / 2
    : sorted[middle];
}

function coefficientOfVariation(values) {
  const finite = values.filter(Number.isFinite);
  if (finite.length < 2) return 0;
  const mean = finite.reduce((sum, value) => sum + value, 0) / finite.length;
  if (mean === 0) return 0;
  const variance = finite.reduce((sum, value) => sum + ((value - mean) ** 2), 0) / finite.length;
  return Math.sqrt(variance) / mean;
}

export function scoreCandidate(samples) {
  const totalSamples = samples.length;
  const successful = samples.filter((sample) => sample.ok === true);
  const successRate = totalSamples === 0 ? 0 : successful.length / totalSamples;
  const medianTls = median(successful.map((sample) => sample.tls));
  const medianTtfb = median(successful.map((sample) => sample.ttfb));
  const medianTotal = median(successful.map((sample) => sample.total));
  const medianThroughput = median(successful.map((sample) => sample.throughput));
  const jitter = coefficientOfVariation(successful.map((sample) => sample.total));
  const stability = Math.max(0, Math.min(100, successRate * 100 * (1 - Math.min(jitter, 1) * 0.5)));
  const latency = medianTtfb === null || medianTotal === null
    ? 0
    : Math.max(0, Math.min(100, 100 / (1 + (medianTtfb * 4) + (medianTotal * 2) + ((medianTls ?? 0) * 2))));
  const throughput = medianThroughput === null
    ? 0
    : Math.max(0, Math.min(100, (medianThroughput / 20) * 100));
  const score = (stability * 0.50) + (latency * 0.35) + (throughput * 0.15);
  const eligible = totalSamples >= 3
    && successRate >= 0.9
    && samples.every((sample) => sample.ok === true && sample.coreOk !== false);

  return {
    eligible,
    successRate,
    stability,
    latency,
    throughput,
    score,
    medians: {
      tls: medianTls,
      ttfb: medianTtfb,
      total: medianTotal,
      throughput: medianThroughput,
    },
  };
}

export function rankCandidates(results) {
  return results.toSorted((left, right) => {
    if (left.eligible !== right.eligible) return left.eligible ? -1 : 1;
    return right.score - left.score;
  });
}

export function isFreshCache(testedAt, now = Date.now()) {
  const timestamp = Date.parse(testedAt);
  return Number.isFinite(timestamp) && now >= timestamp && (now - timestamp) < 86_400_000;
}

export async function snapshotNetworkState(adapter) {
  return adapter.snapshot();
}

export async function stopConflictingVpns(snapshot, adapter) {
  return adapter.stopConflicts(snapshot);
}

export async function restoreNetworkState(snapshot, adapter) {
  return adapter.restore(snapshot);
}

export async function withNetworkTransaction(adapter, operation) {
  const snapshot = await snapshotNetworkState(adapter);
  await stopConflictingVpns(snapshot, adapter);
  try {
    return await operation(snapshot);
  } catch (error) {
    let cleanupError = null;
    let restoreResult = null;
    try {
      await adapter.cleanupManagedTunnel();
    } catch (caught) {
      cleanupError = caught;
    }
    try {
      restoreResult = await restoreNetworkState(snapshot, adapter);
    } catch (caught) {
      throw new AggregateError([error, cleanupError, caught].filter(Boolean), 'VPN switch failed and rollback failed');
    }
    if (cleanupError || restoreResult?.complete === false) {
      throw new AggregateError(
        [error, cleanupError].filter(Boolean),
        'VPN switch failed and rollback was incomplete',
      );
    }
    throw error;
  }
}

const PREFERRED_REGIONS = ['singapore', 'japan', 'taiwan', 'us-west'];

export function selectCandidates(servers, preflightResults, limit = 6) {
  const groups = new Map(PREFERRED_REGIONS.map((region) => [region, []]));
  for (const server of servers) {
    if (groups.has(server.region)) groups.get(server.region).push(server);
  }
  for (const group of groups.values()) {
    group.sort((left, right) => {
      const leftLatency = preflightResults.get(left.id)?.latency ?? Number.POSITIVE_INFINITY;
      const rightLatency = preflightResults.get(right.id)?.latency ?? Number.POSITIVE_INFINITY;
      return leftLatency - rightLatency;
    });
  }

  const selected = [];
  let index = 0;
  while (selected.length < limit) {
    let added = false;
    for (const region of PREFERRED_REGIONS) {
      const candidate = groups.get(region)[index];
      if (candidate && selected.length < limit) {
        selected.push(candidate);
        added = true;
      }
    }
    if (!added) break;
    index += 1;
  }
  return selected;
}

export async function promoteWinningConfig(store, config) {
  const current = await store.read('configs/current.conf');
  if (current !== null) await store.write('configs/previous.conf', current);
  await store.write('configs/current.conf', config);
  const keep = new Set(['configs/current.conf', 'configs/previous.conf']);
  for (const path of await store.list('configs/')) {
    if (!keep.has(path)) await store.remove(path);
  }
}

export function parseVpnConnections(output) {
  const connections = [];
  for (const line of String(output).split('\n')) {
    if (!line.includes('(Connected)')) continue;
    const id = line.match(/\)\s+([0-9A-F-]{36})\b/i)?.[1];
    const name = line.match(/"([^"]+)"/)?.[1];
    if (id && name) connections.push({ id, name });
  }
  return connections;
}

export function parseCurlMetrics(output) {
  try {
    const data = JSON.parse(String(output).trim());
    const httpCode = Number(data.http_code);
    const total = Number(data.time_total);
    const speed = Number(data.speed_download);
    return {
      ok: httpCode >= 200 && httpCode < 500 && Number.isFinite(total) && total > 0,
      httpCode,
      tls: Number(data.time_appconnect) || 0,
      ttfb: Number(data.time_starttransfer) || 0,
      total: total || 0,
      throughput: Number.isFinite(speed) ? (speed * 8) / 1_000_000 : 0,
    };
  } catch {
    return { ok: false, httpCode: 0, tls: 0, ttfb: 0, total: 0, throughput: 0 };
  }
}

export async function runCommand(command, args = [], options = {}) {
  return new Promise((resolvePromise, rejectPromise) => {
    const child = spawn(command, args, {
      stdio: options.inherit ? 'inherit' : ['pipe', 'pipe', 'pipe'],
      env: { ...process.env, ...options.env },
    });
    let stdout = '';
    let stderr = '';
    if (!options.inherit) {
      child.stdout.setEncoding('utf8');
      child.stderr.setEncoding('utf8');
      child.stdout.on('data', (chunk) => { stdout += chunk; });
      child.stderr.on('data', (chunk) => { stderr += chunk; });
      if (options.input !== undefined) child.stdin.end(options.input);
      else child.stdin.end();
    }
    child.on('error', rejectPromise);
    child.on('close', (code, signal) => {
      const result = { code: code ?? 1, signal, stdout, stderr };
      if ((code ?? 1) !== 0 && !options.allowFailure) {
        const error = new Error(`${command} failed with exit code ${code ?? 1}`);
        error.result = result;
        rejectPromise(error);
      } else {
        resolvePromise(result);
      }
    });
  });
}

function shellQuote(value) {
  return `'${String(value).replaceAll("'", `'\\''`)}'`;
}

const PRIVILEGED_BIN = {
  wg: '/opt/homebrew/bin/wg',
  'wg-quick': '/opt/homebrew/bin/wg-quick',
};

export async function runPrivileged(command, args = [], runner = runCommand, options = {}) {
  const nonInteractive = await runner('sudo', ['-n', command, ...args], { ...options, allowFailure: true });
  if (nonInteractive.code === 0) return nonInteractive;
  const executable = PRIVILEGED_BIN[command] ?? command;
  const shellCommand = [executable, ...args].map(shellQuote).join(' ');
  return runner('osascript', [
    '-e', 'on run argv',
    '-e', 'do shell script (item 1 of argv) with administrator privileges',
    '-e', 'end run',
    '--', shellCommand,
  ], options);
}

export class FileStore {
  constructor(root) {
    this.root = root;
  }

  path(relativePath) {
    const path = resolve(this.root, relativePath);
    if (!path.startsWith(`${resolve(this.root)}/`)) throw new Error('Unsafe data path');
    return path;
  }

  async ensure() {
    await mkdir(this.root, { recursive: true, mode: 0o700 });
    await chmod(this.root, 0o700);
  }

  async read(relativePath) {
    try {
      return await readFile(this.path(relativePath), 'utf8');
    } catch (error) {
      if (error.code === 'ENOENT') return null;
      throw error;
    }
  }

  async write(relativePath, value) {
    await this.ensure();
    const path = this.path(relativePath);
    await mkdir(dirname(path), { recursive: true, mode: 0o700 });
    await writeFile(path, value, { mode: 0o600 });
    await chmod(path, 0o600);
  }

  async remove(relativePath) {
    await rm(this.path(relativePath), { force: true });
  }

  async list(relativePrefix) {
    const directory = this.path(relativePrefix);
    try {
      return (await readdir(directory)).map((name) => `${relativePrefix}${name}`);
    } catch (error) {
      if (error.code === 'ENOENT') return [];
      throw error;
    }
  }
}

const VPN_APPS = ['StrongVPN', 'WireGuard', 'OpenVPN Connect', 'REDpass'];

async function appIsRunning(name, runner) {
  const escaped = name.replaceAll('"', '\\"');
  const result = await runner('osascript', ['-e', `application "System Events" to (name of processes) contains "${escaped}"`], { allowFailure: true });
  return result.stdout.trim() === 'true';
}

export function createMacNetworkAdapter(runner = runCommand) {
  let managedConfigPath = null;
  return {
    setManagedConfig(path) {
      managedConfigPath = path;
    },
    async snapshot() {
      const [connections, route, dns, apps] = await Promise.all([
        runner('scutil', ['--nc', 'list']),
        runner('route', ['-n', 'get', 'default'], { allowFailure: true }),
        runner('scutil', ['--dns'], { allowFailure: true }),
        Promise.all(VPN_APPS.map(async (name) => ({ name, running: await appIsRunning(name, runner) }))),
      ]);
      return {
        connectedServices: parseVpnConnections(connections.stdout),
        runningApps: apps.filter(({ running }) => running).map(({ name }) => name),
        routeFingerprint: route.stdout,
        dnsFingerprint: dns.stdout,
      };
    },
    async stopConflicts(snapshot) {
      for (const service of snapshot.connectedServices) {
        await runner('scutil', ['--nc', 'stop', service.id], { allowFailure: true });
      }
      for (const app of snapshot.runningApps) {
        await runner('osascript', ['-e', `tell application "${app.replaceAll('"', '\\"')}" to quit`], { allowFailure: true });
      }
      await new Promise((resolvePromise) => setTimeout(resolvePromise, 1200));
      for (const app of snapshot.runningApps) {
        await runner('pkill', ['-TERM', '-x', app], { allowFailure: true });
      }
    },
    async cleanupManagedTunnel() {
      if (!managedConfigPath) return;
      await runPrivileged('wg-quick', ['down', managedConfigPath], runner, { allowFailure: true });
    },
    async restore(snapshot) {
      let complete = true;
      for (const app of snapshot.runningApps) {
        const result = await runner('open', ['-a', app], { allowFailure: true });
        complete = complete && result.code === 0;
      }
      for (const service of snapshot.connectedServices) {
        const result = await runner('scutil', ['--nc', 'start', service.id], { allowFailure: true });
        complete = complete && result.code === 0;
      }
      return { complete };
    },
  };
}

async function commandExists(command, runner = runCommand) {
  return (await runner('sh', ['-c', `command -v ${command}`], { allowFailure: true })).code === 0;
}

async function generateKeyPair(runner = runCommand) {
  const privateKey = (await runner('wg', ['genkey'])).stdout.trim();
  const publicKey = (await runner('wg', ['pubkey'], { input: `${privateKey}\n` })).stdout.trim();
  if (!privateKey || !publicKey) throw new Error('WireGuard key generation failed');
  return { privateKey, publicKey };
}

async function pingLatency(ip, runner = runCommand) {
  const result = await runner('ping', ['-n', '-c', '2', '-W', '1000', ip], { allowFailure: true });
  const match = result.stdout.match(/(?:round-trip|rtt).*?=\s*[\d.]+\/([\d.]+)\//);
  return { ok: result.code === 0 && Boolean(match), latency: match ? Number(match[1]) : Number.POSITIVE_INFINITY };
}

const CURL_FORMAT = '{"http_code":%{http_code},"time_appconnect":%{time_appconnect},"time_starttransfer":%{time_starttransfer},"time_total":%{time_total},"speed_download":%{speed_download}}';
const TEST_TARGETS = [
  { name: 'openai-api', url: 'https://api.openai.com/v1/models', core: true },
  { name: 'chatgpt', url: 'https://chatgpt.com/', core: true },
  { name: 'claude', url: 'https://claude.ai/', core: true },
  { name: 'github', url: 'https://github.com/' },
  { name: 'gemini', url: 'https://gemini.google.com/' },
  { name: 'cloudflare', url: 'https://speed.cloudflare.com/__down?bytes=1000000', throughput: true },
];

async function curlMetric(target, runner = runCommand) {
  const result = await runner('curl', [
    '--location', '--silent', '--show-error', '--output', '/dev/null',
    '--connect-timeout', '8', '--max-time', '20', '--write-out', CURL_FORMAT,
    target.url,
  ], { allowFailure: true });
  const metric = parseCurlMetrics(result.stdout);
  return { ...metric, ok: result.code === 0 && metric.ok, name: target.name, core: target.core === true };
}

function aggregateRound(metrics) {
  const successful = metrics.filter(({ ok }) => ok);
  return {
    ok: successful.length === metrics.length,
    coreOk: metrics.filter(({ core }) => core).every(({ ok }) => ok),
    tls: median(successful.map(({ tls }) => tls)),
    ttfb: median(successful.map(({ ttfb }) => ttfb)),
    total: median(successful.map(({ total }) => total)),
    throughput: median(metrics.filter(({ name, ok }) => name === 'cloudflare' && ok).map(({ throughput }) => throughput)),
  };
}

async function readCloudflareTrace(runner = runCommand) {
  const result = await runner('curl', ['--silent', '--show-error', '--connect-timeout', '8', '--max-time', '15', 'https://www.cloudflare.com/cdn-cgi/trace'], { allowFailure: true });
  const fields = Object.fromEntries(result.stdout.split('\n').map((line) => line.split('=')).filter((parts) => parts.length === 2));
  return { loc: fields.loc ?? null, colo: fields.colo ?? null, warp: fields.warp ?? null };
}

async function validateTunnel(runner = runCommand) {
  const [handshake, dns] = await Promise.all([
    runPrivileged('wg', ['show', 'svpn0', 'latest-handshakes'], runner, { allowFailure: true }),
    runner('dscacheutil', ['-q', 'host', '-a', 'name', 'api.openai.com'], { allowFailure: true }),
  ]);
  const handshakeOk = handshake.stdout.trim().split(/\s+/).some((value) => /^\d{10,}$/.test(value) && Number(value) > 0);
  return { handshakeOk, dnsOk: dns.code === 0 && /ip_address:/.test(dns.stdout) };
}

async function tunnelUp(configPath, adapter, runner = runCommand) {
  adapter.setManagedConfig(configPath);
  await runPrivileged('wg-quick', ['up', configPath], runner);
}

async function tunnelDown(configPath, runner = runCommand) {
  await runPrivileged('wg-quick', ['down', configPath], runner, { allowFailure: true });
}

const BASE_URLS = [
  'https://tools.strongvpn.asia/share/strong-wg',
  'https://tools.strongtech.org/share/strong-wg',
];

async function benchmarkCandidate({ server, credentials, store, adapter, runner, emit }) {
  const keyPair = await generateKeyPair(runner);
  const generated = await generateConfig({ baseUrls: BASE_URLS, server, credentials, keyPair });
  const configPath = store.path('runtime/svpn0.conf');
  await store.write('runtime/svpn0.conf', generated.config);
  let trace = { loc: null, colo: null, warp: null };
  const samples = [];
  try {
    await tunnelUp(configPath, adapter, runner);
    trace = await readCloudflareTrace(runner);
    for (let round = 1; round <= 3; round += 1) {
      const metrics = [];
      for (const target of TEST_TARGETS) metrics.push(await curlMetric(target, runner));
      samples.push(aggregateRound(metrics));
      emit?.(`  第 ${round}/3 轮完成`);
    }
    const validation = await validateTunnel(runner);
    for (const sample of samples) sample.coreOk = sample.coreOk && validation.handshakeOk && validation.dnsOk;
  } finally {
    await tunnelDown(configPath, runner);
  }
  const scored = scoreCandidate(samples);
  return {
    id: server.id,
    label: server.label,
    country: server.country,
    region: server.region,
    trace,
    samples,
    ...scored,
    config: generated.config,
  };
}

async function runBenchmark({ force, store, adapter, runner = runCommand, emit = console.log }) {
  const cachedText = await store.read('latest.json');
  if (!force && cachedText) {
    const cached = JSON.parse(cachedText);
    if (isFreshCache(cached.testedAt) && await store.read('configs/current.conf')) return { ...cached, cached: true };
  }
  const credentials = await readCredentials(runner);
  const catalog = await fetchServerCatalog({ baseUrls: BASE_URLS });
  const preferred = catalog.servers.filter(({ region }) => region !== null);
  const preflight = new Map();
  emit(`预检 ${preferred.length} 个候选节点…`);
  for (const server of preferred) preflight.set(server.id, await pingLatency(server.ip, runner));
  const candidates = selectCandidates(preferred, preflight, 6);
  if (candidates.length === 0) throw new Error('No preferred StrongVPN candidates were reachable');

  return withNetworkTransaction(adapter, async () => {
    const results = [];
    for (const [index, server] of candidates.entries()) {
      emit(`[${index + 1}/${candidates.length}] 测试 ${server.label} (${server.id})`);
      try {
        results.push(await benchmarkCandidate({ server, credentials, store, adapter, runner, emit }));
      } catch (error) {
        results.push({
          id: server.id, label: server.label, country: server.country, region: server.region,
          trace: { loc: null, colo: null, warp: null }, samples: [], ...scoreCandidate([]),
          error: error.message,
        });
        await adapter.cleanupManagedTunnel();
      }
    }
    const ranked = rankCandidates(results);
    const winner = ranked.find(({ eligible, config }) => eligible && config);
    if (!winner) throw new Error('No StrongVPN node passed all stability and core service checks');
    await promoteWinningConfig(store, winner.config);
    await store.write('runtime/svpn0.conf', winner.config);
    await tunnelUp(store.path('runtime/svpn0.conf'), adapter, runner);
    const validation = await validateTunnel(runner);
    if (!validation.handshakeOk || !validation.dnsOk) throw new Error('Winning tunnel failed final validation');

    const latest = {
      testedAt: new Date().toISOString(),
      winner: winner.id,
      results: ranked.map(({ config: _config, samples, error, ...item }) => ({
        ...item,
        rounds: samples.length,
        error: error ?? null,
      })),
    };
    await store.write('latest.json', `${JSON.stringify(latest, null, 2)}\n`);
    return latest;
  });
}

async function secureCredentialSet(username, runner = runCommand) {
  if (!/^a\d{6}$/.test(username)) throw new Error('StrongVPN username must match a followed by six digits');
  console.error('请在系统提示处输入 StrongVPN 密码（输入不会显示）：');
  await runner('security', [
    'add-generic-password', '-U', '-a', username, '-s', 'strongvpn-node-optimizer', '-w',
  ], { inherit: true });
}

function printResult(value, json) {
  if (json) {
    console.log(JSON.stringify(value, null, 2));
    return;
  }
  if (value.winner) console.log(`已连接最优节点：${value.winner}${value.cached ? '（使用 24 小时内缓存）' : ''}`);
  else console.log(value.message ?? String(value));
}

async function cli(argv = process.argv.slice(2)) {
  const json = argv.includes('--json');
  const force = argv.includes('--force');
  const args = argv.filter((arg) => !arg.startsWith('--'));
  const command = args[0] ?? 'status';
  const dataRoot = process.env.STRONGVPN_OPTIMIZER_HOME ?? join(homedir(), '.local', 'share', 'strongvpn-node-optimizer');
  const store = new FileStore(dataRoot);
  await store.ensure();
  const adapter = createMacNetworkAdapter();

  if (command === 'credentials' && args[1] === 'set') {
    const username = args[2];
    if (!username) throw new Error('Usage: credentials set <username>');
    await secureCredentialSet(username);
    printResult({ message: 'StrongVPN 凭据已安全保存到 macOS Keychain。' }, json);
    return;
  }
  if (command === 'status') {
    const [wg, wgQuick, keychain, latest] = await Promise.all([
      commandExists('wg'), commandExists('wg-quick'),
      runCommand('security', ['find-generic-password', '-s', 'strongvpn-node-optimizer'], { allowFailure: true }),
      store.read('latest.json'),
    ]);
    const status = {
      dependencies: { wg, wgQuick },
      credentials: keychain.code === 0 ? 'configured' : 'missing',
      latest: latest ? JSON.parse(latest) : null,
    };
    console.log(JSON.stringify(status, null, 2));
    return;
  }
  if (command === 'benchmark') {
    if (!(await commandExists('wg')) || !(await commandExists('wg-quick'))) {
      const error = new Error('WireGuard tools are missing; install with brew install wireguard-tools');
      error.exitCode = 3;
      throw error;
    }
    const result = await runBenchmark({ force, store, adapter });
    printResult(result, json);
    return;
  }
  if (command === 'switch' && args[1] === 'best') {
    const config = await store.read('configs/current.conf');
    if (!config) throw new Error('No tested configuration exists; run benchmark first');
    const result = await withNetworkTransaction(adapter, async () => {
      await store.write('runtime/svpn0.conf', config);
      await tunnelUp(store.path('runtime/svpn0.conf'), adapter);
      const validation = await validateTunnel();
      if (!validation.handshakeOk || !validation.dnsOk) throw new Error('Cached best tunnel failed validation');
      return JSON.parse(await store.read('latest.json'));
    });
    printResult(result, json);
    return;
  }
  if (command === 'restore') {
    const previous = await store.read('configs/previous.conf');
    const current = await store.read('configs/current.conf');
    if (!previous) throw new Error('No previous configuration is available');
    await withNetworkTransaction(adapter, async () => {
      await store.write('runtime/svpn0.conf', previous);
      await tunnelUp(store.path('runtime/svpn0.conf'), adapter);
      const validation = await validateTunnel();
      if (!validation.handshakeOk || !validation.dnsOk) throw new Error('Previous tunnel failed validation');
      await store.write('configs/current.conf', previous);
      if (current) await store.write('configs/previous.conf', current);
    });
    printResult({ message: '已恢复到上一个 StrongVPN 配置。' }, json);
    return;
  }
  throw new Error('Usage: status | credentials set <username> | benchmark [--force] | switch best | restore [--json]');
}

const isMain = process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url));
if (isMain) {
  cli().catch((error) => {
    const safeMessage = redactSensitive(error.message, []);
    console.error(`错误：${safeMessage}`);
    process.exitCode = error.exitCode ?? (/Keychain|credentials/i.test(error.message) ? 2 : /rollback/i.test(error.message) ? 5 : 4);
  });
}
