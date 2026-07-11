#!/usr/bin/env node

import { isIP } from 'node:net';

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
  if (!/^a\d{6}$/.test(credentials?.username ?? '') || String(credentials?.password ?? '').length !== 10) {
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
  const accountMatch = String(metadata?.stderr ?? '').match(/acct<blob>="([^"]+)"/);
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
