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
