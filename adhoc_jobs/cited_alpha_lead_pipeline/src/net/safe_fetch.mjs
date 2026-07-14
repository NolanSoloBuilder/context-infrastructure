import dns from "node:dns/promises";
import http from "node:http";
import https from "node:https";
import { BlockList, isIP } from "node:net";

const blocked = new BlockList();
for (const [network, prefix] of [
  ["0.0.0.0", 8], ["10.0.0.0", 8], ["100.64.0.0", 10], ["127.0.0.0", 8],
  ["169.254.0.0", 16], ["172.16.0.0", 12], ["192.0.0.0", 24], ["192.0.2.0", 24],
  ["192.168.0.0", 16], ["198.18.0.0", 15], ["198.51.100.0", 24], ["203.0.113.0", 24],
  ["224.0.0.0", 4], ["240.0.0.0", 4]
]) blocked.addSubnet(network, prefix, "ipv4");

for (const [network, prefix] of [
  ["::", 128], ["::1", 128], ["64:ff9b::", 96], ["64:ff9b:1::", 48],
  ["100::", 64], ["2001::", 32], ["2001:2::", 48], ["2001:10::", 28], ["2001:20::", 28],
  ["2001:db8::", 32], ["2002::", 16], ["fc00::", 7], ["fe80::", 10], ["ff00::", 8]
]) blocked.addSubnet(network, prefix, "ipv6");

export function hostAllowed(hostname, canonicalDomain) {
  const host = hostname.toLowerCase().replace(/\.$/, "");
  const domain = canonicalDomain.toLowerCase().replace(/\.$/, "");
  return host === domain || host === `www.${domain}`;
}

export function validatePublicUrl(value, canonicalDomain, { allowPrivateNetwork = false } = {}) {
  const url = value instanceof URL ? value : new URL(value);
  if (!["http:", "https:"].includes(url.protocol)) throw new Error(`Forbidden URL scheme: ${url.protocol}`);
  if (url.username || url.password) throw new Error("URL credentials are forbidden");
  if (!allowPrivateNetwork && url.port && !["80", "443"].includes(url.port)) throw new Error(`Forbidden port: ${url.port}`);
  if (!hostAllowed(url.hostname, canonicalDomain)) throw new Error(`Host is outside target domain: ${url.hostname}`);
  if (["localhost", "localhost.localdomain"].includes(url.hostname.toLowerCase())) throw new Error("Local hosts are forbidden");
  return url;
}

export function isPublicAddress(address, family) {
  const normalizedFamily = typeof family === "number" ? `ipv${family}` : String(family).toLowerCase();
  if (!isIP(address)) return false;
  if (normalizedFamily === "ipv6" && address.toLowerCase().startsWith("::ffff:")) return false;
  return !blocked.check(address, normalizedFamily);
}

async function resolvePublicAddress(hostname, allowPrivateNetwork) {
  const addresses = await dns.lookup(hostname, { all: true, verbatim: true });
  if (addresses.length === 0) throw new Error(`DNS returned no addresses for ${hostname}`);
  if (allowPrivateNetwork) return addresses[0];
  const publicAddresses = addresses.filter(({ address, family }) => isPublicAddress(address, family));
  if (publicAddresses.length !== addresses.length) throw new Error(`Blocked private or reserved address for ${hostname}`);
  return publicAddresses[0];
}

function readBody(response, maxBytes) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    let bytes = 0;
    response.on("data", (chunk) => {
      bytes += chunk.length;
      if (bytes > maxBytes) {
        response.destroy(new Error(`Response exceeds ${maxBytes} bytes`));
        return;
      }
      chunks.push(chunk);
    });
    response.on("end", () => resolve(Buffer.concat(chunks).toString("utf8")));
    response.on("error", reject);
  });
}

async function requestOnce(url, options) {
  const address = await resolvePublicAddress(url.hostname, options.allowPrivateNetwork);
  const transport = url.protocol === "https:" ? https : http;
  const family = typeof address.family === "string" ? Number.parseInt(address.family.replace("IPv", ""), 10) : address.family;

  return new Promise((resolve, reject) => {
    let deadline;
    const request = transport.request(url, {
      method: "GET",
      headers: {
        Accept: options.accept,
        "Accept-Encoding": "identity",
        "User-Agent": options.userAgent
      },
      lookup: (_hostname, lookupOptions, callback) => {
        if (lookupOptions?.all) callback(null, [{ address: address.address, family }]);
        else callback(null, address.address, family);
      },
      servername: url.hostname
    }, async (response) => {
      try {
        const body = await readBody(response, options.maxBytes);
        clearTimeout(deadline);
        resolve({
          url: url.href,
          status: response.statusCode ?? 0,
          headers: response.headers,
          body
        });
      } catch (error) {
        clearTimeout(deadline);
        reject(error);
      }
    });
    deadline = setTimeout(() => request.destroy(new Error(`Request timed out after ${options.timeoutMs}ms`)), options.timeoutMs);
    request.on("error", (error) => {
      clearTimeout(deadline);
      reject(error);
    });
    request.end();
  });
}

export async function safeFetch(value, {
  canonicalDomain,
  userAgent,
  accept = "text/html,application/xhtml+xml;q=0.9,text/plain;q=0.5",
  maxBytes = 1_500_000,
  timeoutMs = 15_000,
  maxRedirects = 5,
  allowPrivateNetwork = false,
  redirectMode = "follow"
}) {
  let url = validatePublicUrl(value, canonicalDomain, { allowPrivateNetwork });
  for (let redirect = 0; redirect <= maxRedirects; redirect += 1) {
    const response = await requestOnce(url, { userAgent, accept, maxBytes, timeoutMs, allowPrivateNetwork });
    if (![301, 302, 303, 307, 308].includes(response.status)) return response;
    if (redirectMode === "manual") return response;
    const location = response.headers.location;
    if (!location) return response;
    if (redirect === maxRedirects) throw new Error(`Too many redirects for ${value}`);
    url = validatePublicUrl(new URL(location, url), canonicalDomain, { allowPrivateNetwork });
  }
  throw new Error(`Unable to fetch ${value}`);
}
