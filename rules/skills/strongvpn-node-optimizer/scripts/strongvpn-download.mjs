#!/usr/bin/env node

import { generateKeyPairSync, randomInt } from 'node:crypto';
import { mkdir, open, rm, chmod } from 'node:fs/promises';
import { isIP } from 'node:net';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { createInterface } from 'node:readline';
import { fileURLToPath } from 'node:url';
import { fetchServerCatalog, readCredentials } from './strongvpn-node-optimizer.mjs';
import { runCommand } from './strongvpn-node-optimizer.mjs';

export const SOURCES = {
  strongvpn: 'https://tools.strongvpn.asia/share/strong-wg',
  strongtech: 'https://tools.strongtech.org/share/strong-wg',
};

export function createWireGuardKeys() {
  const { privateKey, publicKey } = generateKeyPairSync('x25519');
  const raw = Buffer.from(privateKey.export({ format: 'jwk' }).d, 'base64url');
  // WireGuard private keys use the RFC 7748 clamping convention.
  raw[0] &= 248;
  raw[31] &= 127;
  raw[31] |= 64;
  return {
    privateKey: raw.toString('base64'),
    publicKey: Buffer.from(publicKey.export({ format: 'jwk' }).x, 'base64url').toString('base64'),
  };
}

function isCidr(value) {
  if (typeof value !== 'string') return false;
  const parts = value.split('/');
  if (parts.length !== 2 || !/^\d+$/.test(parts[1])) return false;
  const family = isIP(parts[0]);
  return family !== 0 && Number(parts[1]) <= (family === 4 ? 32 : 128);
}

export function formatDownloadedConfig(data, server, keys, port = randomInt(55000, 60001)) {
  const iface = data?.config?.Interface;
  const peer = data?.config?.Peer;
  const addresses = typeof iface?.Address === 'string' ? iface.Address.split(',').map((x) => x.trim()) : [];
  const keyPattern = /^[A-Za-z0-9+/]{43}=$/;
  if (data?.success !== true
    || addresses.length === 0 || !addresses.every(isCidr)
    || !Array.isArray(iface?.DNS) || iface.DNS.length === 0 || !iface.DNS.every((x) => typeof x === 'string' && isIP(x))
    || !keyPattern.test(peer?.PublicKey ?? '')
    || !Array.isArray(peer?.AllowedIPs) || peer.AllowedIPs.length === 0 || !peer.AllowedIPs.every(isCidr)
    || !isIP(server?.ip ?? '') || !keyPattern.test(keys?.privateKey ?? '')
    || !Number.isInteger(port) || port < 55000 || port > 60000) {
    throw new Error('生成接口返回了无效的 WireGuard 配置；未保存响应正文。');
  }
  const endpoint = isIP(server.ip) === 6 ? `[${server.ip}]:${port}` : `${server.ip}:${port}`;
  return [
    '[Interface]', `PrivateKey = ${keys.privateKey}`,
    `Address = ${addresses.join(', ')}`, `DNS = ${iface.DNS.join(', ')}`, '',
    '[Peer]', `PublicKey = ${peer.PublicKey}`, `AllowedIPs = ${peer.AllowedIPs.join(', ')}`,
    `Endpoint = ${endpoint}`, '',
  ].join('\n');
}

export async function generateDownload({ baseUrl, server, credentials, keys, fetchImpl = fetch }) {
  if (!Object.values(SOURCES).includes(baseUrl)) throw new Error('下载来源必须是两个已知 HTTPS 站点之一。');
  if (!/^a\d{6}$/.test(credentials?.username ?? '') || typeof credentials?.password !== 'string' || !credentials.password) {
    throw new Error('缺少有效凭据。请设置 Keychain 或通过标准输入提供密码。');
  }
  let response;
  try {
    // A timeout can mean the server already registered this public key. Never retry this POST automatically.
    response = await fetchImpl(`${new URL(baseUrl).origin}/wg-generate`, {
      method: 'POST', redirect: 'error', signal: AbortSignal.timeout(30000),
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ aiouser: credentials.username, aiopass: credentials.password, server: server.id, publickey: keys.publicKey }),
    });
  } catch {
    throw new Error('生成请求未确认完成，未自动重试；请先核查服务端状态。');
  }
  if (!response.ok) throw new Error(`生成接口 HTTP ${response.status}；未自动重试，未输出响应正文。`);
  let data;
  try { data = await response.json(); } catch { throw new Error('生成接口返回非 JSON 数据；未自动重试。'); }
  if (data?.success !== true) throw new Error('生成接口拒绝请求，请核查账号、密码或节点；未自动重试。');
  return formatDownloadedConfig(data, server, keys);
}

export async function downloadToFile({ output, generate }) {
  // Reserve the destination before contacting the generator. Existing files and symlinks are rejected.
  let file;
  try { file = await open(output, 'wx', 0o600); } catch (error) {
    if (error.code === 'EEXIST') throw new Error('输出文件已存在，请选择另一个文件名。');
    throw new Error('无法创建输出文件，请检查目标目录和权限。');
  }
  try {
    const config = await generate();
    await file.writeFile(config, 'utf8');
    await file.sync();
  } catch (error) {
    await file.close();
    await rm(output, { force: true });
    throw error;
  }
  await file.close();
  return output;
}

export function parseDownloadArgs(argv) {
  const options = { command: argv[0] ?? 'help', json: false, passwordStdin: false };
  const positional = [];
  for (let index = 1; index < argv.length; index += 1) {
    const arg = argv[index];
    if (arg === '--json') options.json = true;
    else if (arg === '--password-stdin') options.passwordStdin = true;
    else if (['--output', '--source', '--username'].includes(arg)) {
      const value = argv[++index];
      if (!value || value.startsWith('--')) throw new Error(`${arg} 需要一个值。`);
      options[arg.slice(2)] = value;
    } else if (arg.startsWith('--')) throw new Error(`未知参数：${arg}`);
    else positional.push(arg);
  }
  if (positional.length > 1) throw new Error('一次只支持一个筛选词或一个节点 ID。');
  options.selector = positional[0];
  if (options.source && !SOURCES[options.source]) throw new Error('--source 只支持 strongvpn 或 strongtech。');
  if (options.passwordStdin && !options.username) throw new Error('--password-stdin 需要 --username。');
  return options;
}

async function passwordFromStdin() {
  if (process.stdin.isTTY) throw new Error('--password-stdin 只接受管道输入，避免终端显示密码。');
  const reader = createInterface({ input: process.stdin, crlfDelay: Infinity });
  try {
    for await (const line of reader) return line;
    throw new Error('标准输入没有提供密码。');
  } finally { reader.close(); }
}

export async function runDownloader(argv = process.argv.slice(2)) {
  const options = parseDownloadArgs(argv);
  if (['help', '--help', '-h'].includes(options.command)) {
    console.log('servers [筛选词] [--source strongvpn|strongtech] [--json]\ndownload <节点ID> [--output 路径] [--source strongvpn|strongtech] [--username 用户名] [--password-stdin] [--json]');
    return;
  }
  if (!['servers', 'download'].includes(options.command)) throw new Error('命令必须是 servers 或 download；用 --help 查看用法。');
  if (options.command === 'download' && !/^str-[a-z0-9]+$/.test(options.selector ?? '')) {
    throw new Error('download 需要完整节点 ID；先运行 servers japan 查看日本节点。');
  }
  const urls = options.source ? [SOURCES[options.source]] : Object.values(SOURCES);
  const catalog = await fetchServerCatalog({ baseUrls: urls, fetchImpl: (url) => fetch(url, { redirect: 'error', signal: AbortSignal.timeout(15000) }) });
  if (options.command === 'servers') {
    const aliases = { 日本: 'japan', 新加坡: 'singapore', 美国: 'united states', 台湾: 'taiwan', 香港: 'hong kong' };
    const query = (aliases[options.selector] ?? options.selector ?? '').toLowerCase();
    const servers = catalog.servers.filter((s) => `${s.id} ${s.country} ${s.label} ${s.region ?? ''}`.toLowerCase().includes(query));
    console.log(options.json ? JSON.stringify({ source: catalog.baseUrl, servers }, null, 2) : servers.map((s) => `${s.id}\t${s.country}\t${s.label}`).join('\n') || '没有匹配的节点。');
    return;
  }
  const server = catalog.servers.find((s) => s.id === options.selector);
  if (!server) throw new Error('节点 ID 不在当前目录中；请重新运行 servers。');
  const credentials = options.passwordStdin
    ? { username: options.username, password: await passwordFromStdin() }
    : await readCredentials(runCommand);
  if (options.username && credentials.username !== options.username) throw new Error('Keychain 中的账号与指定用户名不一致。');
  const dataRoot = process.env.STRONGVPN_OPTIMIZER_HOME ?? join(homedir(), '.local', 'share', 'strongvpn-node-optimizer');
  const stamp = new Date().toISOString().replace(/[:.]/g, '-');
  const output = options.output ? resolve(options.output) : join(resolve(dataRoot), 'downloads', `${server.id}-${stamp}.conf`);
  if (!options.output) {
    await mkdir(dataRoot, { recursive: true, mode: 0o700 });
    await chmod(dataRoot, 0o700);
    await mkdir(dirname(output), { recursive: true, mode: 0o700 });
    await chmod(dirname(output), 0o700);
  }
  const keys = createWireGuardKeys();
  await downloadToFile({ output, generate: () => generateDownload({ baseUrl: catalog.baseUrl, server, credentials, keys }) });
  const result = { server: server.id, label: server.label, source: new URL(catalog.baseUrl).origin, output };
  console.log(options.json ? JSON.stringify(result, null, 2) : `已下载 ${server.label} (${server.id})\n${output}`);
}

if (process.argv[1] && resolve(process.argv[1]) === resolve(fileURLToPath(import.meta.url))) {
  runDownloader().catch((error) => { console.error(`错误：${error.message}`); process.exitCode = 1; });
}
