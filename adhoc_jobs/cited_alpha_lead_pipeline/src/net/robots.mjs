import { safeFetch } from "./safe_fetch.mjs";

function globToRegExp(pattern) {
  const anchored = pattern.endsWith("$");
  const source = (anchored ? pattern.slice(0, -1) : pattern)
    .replace(/[.+?^${}()|[\]\\]/g, "\\$&")
    .replaceAll("*", ".*");
  return new RegExp(`^${source}${anchored ? "$" : ""}`);
}

function normalizePercentEncoding(value) {
  return value.replace(/%([0-9a-fA-F]{2})/g, (match, hex) => {
    const byte = Number.parseInt(hex, 16);
    const char = String.fromCharCode(byte);
    return /[A-Za-z0-9\-._~]/.test(char) ? char : `%${hex.toUpperCase()}`;
  });
}

export function parseRobots(text, userAgent) {
  const groups = [];
  let agents = [];
  let rules = [];
  let crawlDelayMs = 0;
  let sawDirective = false;

  const flush = () => {
    if (agents.length > 0) groups.push({ agents, rules, crawlDelayMs });
    agents = [];
    rules = [];
    crawlDelayMs = 0;
    sawDirective = false;
  };

  for (const rawLine of text.split(/\r?\n/)) {
    const line = rawLine.replace(/#.*$/, "").trim();
    if (!line) continue;
    const separator = line.indexOf(":");
    if (separator < 0) continue;
    const field = line.slice(0, separator).trim().toLowerCase();
    const value = line.slice(separator + 1).trim();
    if (field === "user-agent") {
      if (sawDirective) flush();
      agents.push(value.toLowerCase());
    } else if (["allow", "disallow"].includes(field) && agents.length > 0) {
      sawDirective = true;
      if (value) rules.push({ type: field, pattern: value, length: value.replace(/[*$]/g, "").length });
    } else if (field === "crawl-delay" && agents.length > 0) {
      sawDirective = true;
      const seconds = Number.parseFloat(value);
      if (Number.isFinite(seconds) && seconds >= 0) crawlDelayMs = Math.ceil(seconds * 1000);
    }
  }
  flush();

  const normalizedAgent = userAgent.toLowerCase();
  const scored = groups.map((group) => ({
    group,
    score: Math.max(...group.agents.map((agent) => agent === "*" ? 0 : (normalizedAgent.includes(agent) ? agent.length : -1)))
  })).filter(({ score }) => score >= 0);
  if (scored.length === 0) return { rules: [], crawlDelayMs: 0 };
  const bestScore = Math.max(...scored.map(({ score }) => score));
  const selected = scored.filter(({ score }) => score === bestScore).map(({ group }) => group);
  return {
    rules: selected.flatMap((group) => group.rules),
    crawlDelayMs: Math.max(...selected.map((group) => group.crawlDelayMs), 0)
  };
}

export function robotsAllows(policy, url) {
  const path = normalizePercentEncoding(`${url.pathname}${url.search}` || "/");
  const matches = policy.rules.filter((rule) => globToRegExp(normalizePercentEncoding(rule.pattern)).test(path));
  if (matches.length === 0) return true;
  matches.sort((left, right) => right.length - left.length || (left.type === "allow" ? -1 : 1));
  return matches[0].type === "allow";
}

export async function fetchRobots(origin, options) {
  const robotsUrl = new URL("/robots.txt", origin);
  try {
    const response = await safeFetch(robotsUrl, {
      ...options,
      accept: "text/plain,*/*;q=0.1",
      maxBytes: 512_000,
      maxRedirects: 2
    });
    if ([404, 410].includes(response.status)) return { allowed: true, policy: { rules: [], crawlDelayMs: 0 }, status: response.status };
    if (response.status >= 200 && response.status < 300) {
      return { allowed: true, policy: parseRobots(response.body, options.userAgent), status: response.status };
    }
    return { allowed: false, policy: null, status: response.status, reason: `robots_http_${response.status}` };
  } catch (error) {
    return { allowed: false, policy: null, status: 0, reason: `robots_error:${error.message}` };
  }
}
