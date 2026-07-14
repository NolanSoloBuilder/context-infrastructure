import { extractContactPoints } from "../extract/contact_points.mjs";
import { fetchRobots, robotsAllows } from "../net/robots.mjs";
import { safeFetch } from "../net/safe_fetch.mjs";
import { nowIso, sha256, sleep } from "../utils.mjs";

const COMMON_PATHS = ["/", "/contact", "/about", "/team", "/research", "/press", "/media", "/partnerships", "/consulting"];

function uniqueEndpoints(endpoints) {
  return [...new Map(endpoints.map((endpoint) => [
    `${endpoint.contactType}:${endpoint.contactValue.toLowerCase()}`,
    endpoint
  ])).values()];
}

function htmlResponse(response) {
  const contentType = String(response.headers["content-type"] ?? "").toLowerCase();
  return response.status >= 200 && response.status < 300 && (contentType.includes("text/html") || contentType.includes("application/xhtml+xml") || contentType === "");
}

export async function crawlOfficialSite(target, config) {
  const fetchOptions = {
    canonicalDomain: target.domain,
    userAgent: config.userAgent,
    maxBytes: config.maxPageBytes,
    timeoutMs: config.requestTimeoutMs,
    allowPrivateNetwork: config.allowPrivateNetwork
  };
  const robotsCache = new Map();
  const lastRequestAt = new Map();
  const waitForOrigin = async (origin, minimumDelayMs) => {
    const elapsed = Date.now() - (lastRequestAt.get(origin) ?? 0);
    if (elapsed < minimumDelayMs) await sleep(minimumDelayMs - elapsed);
  };
  const getRobots = async (origin) => {
    if (robotsCache.has(origin)) return robotsCache.get(origin);
    await waitForOrigin(origin, config.requestDelayMs);
    const result = await fetchRobots(origin, fetchOptions);
    lastRequestAt.set(origin, Date.now());
    robotsCache.set(origin, result);
    return result;
  };
  const chooseOrigin = async () => {
    if (target.websiteUrl) {
      const origin = new URL(target.websiteUrl).origin;
      return { origin, robots: await getRobots(origin) };
    }
    const httpsOrigin = `https://${target.domain}`;
    const httpsRobots = await getRobots(httpsOrigin);
    if (httpsRobots.status !== 0) return { origin: httpsOrigin, robots: httpsRobots };
    const httpOrigin = `http://${target.domain}`;
    return { origin: httpOrigin, robots: await getRobots(httpOrigin) };
  };
  const fetchPage = async (initialUrl) => {
    let url = new URL(initialUrl);
    for (let redirect = 0; redirect <= 5; redirect += 1) {
      const robots = await getRobots(url.origin);
      if (!robots.allowed) return { deferredReason: robots.reason ?? "robots_unavailable", url: url.href };
      if (!robotsAllows(robots.policy, url)) return { robotsBlocked: true, url: url.href };
      const delayMs = Math.max(config.requestDelayMs, robots.policy.crawlDelayMs);
      await waitForOrigin(url.origin, delayMs);
      const response = await safeFetch(url, { ...fetchOptions, maxRedirects: 0, redirectMode: "manual" });
      lastRequestAt.set(url.origin, Date.now());
      if (![301, 302, 303, 307, 308].includes(response.status) || !response.headers.location) return { response };
      if (redirect === 5) throw new Error(`Too many redirects for ${initialUrl}`);
      url = new URL(response.headers.location, url);
    }
    throw new Error(`Unable to fetch ${initialUrl}`);
  };

  const chosen = await chooseOrigin();
  if (!chosen.robots.allowed) {
    return { endpoints: [], pages: [], crawlStatus: "DEFERRED", deferredReason: chosen.robots.reason ?? "robots_unavailable" };
  }

  const startUrl = target.websiteUrl || `${chosen.origin}/`;
  const queue = [startUrl, ...COMMON_PATHS.map((path) => new URL(path, chosen.origin).href)];
  const queued = new Set(queue);
  const visited = new Set();
  const endpoints = [];
  const pages = [];
  let successfulHtmlPages = 0;
  let terminalDeferredReason = "";

  while (queue.length > 0 && visited.size < config.maxPagesPerDomain) {
    const url = new URL(queue.shift());
    if (visited.has(url.href)) continue;
    visited.add(url.href);
    const observedAt = nowIso();
    try {
      const fetched = await fetchPage(url);
      if (fetched.deferredReason) {
        terminalDeferredReason ||= fetched.deferredReason;
        pages.push({ url: fetched.url, observedAt, status: 0, robotsAllowed: false, contentSha256: "", error: fetched.deferredReason });
        continue;
      }
      if (fetched.robotsBlocked) {
        pages.push({ url: fetched.url, observedAt, status: 0, robotsAllowed: false, contentSha256: "" });
        continue;
      }
      const response = fetched.response;
      const page = {
        url: response.url,
        observedAt,
        status: response.status,
        robotsAllowed: true,
        contentSha256: response.body ? sha256(response.body) : ""
      };
      pages.push(page);
      if (!htmlResponse(response)) continue;
      successfulHtmlPages += 1;
      const extracted = extractContactPoints(response.body, response.url, target.domain);
      endpoints.push(...extracted.endpoints.map((endpoint) => ({ ...endpoint, observedAt })));
      for (const link of extracted.internalLinks) {
        if (!queued.has(link) && !visited.has(link)) {
          queue.push(link);
          queued.add(link);
        }
      }
    } catch (error) {
      pages.push({ url: url.href, observedAt, status: 0, robotsAllowed: true, contentSha256: "", error: error.message });
    }
  }

  const crawlStatus = successfulHtmlPages > 0 ? "COMPLETE" : (terminalDeferredReason ? "DEFERRED" : "INCOMPLETE");
  return {
    endpoints: uniqueEndpoints(endpoints),
    pages,
    crawlStatus,
    deferredReason: terminalDeferredReason || (crawlStatus === "INCOMPLETE" ? "FETCH_INCOMPLETE" : "")
  };
}
