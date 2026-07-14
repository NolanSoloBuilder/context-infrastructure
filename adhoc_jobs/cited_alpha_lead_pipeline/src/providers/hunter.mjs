import { splitPersonName, nowIso } from "../utils.mjs";
import { classifyEmail } from "../extract/contact_points.mjs";

const BASE_URL = "https://api.hunter.io/v2";

function normalizedVerification(status) {
  const value = String(status ?? "").toLowerCase();
  if (["valid", "deliverable"].includes(value)) return "deliverable";
  if (["accept_all", "accept-all", "catch_all", "catch-all"].includes(value)) return "catch_all";
  if (["invalid", "undeliverable"].includes(value)) return "undeliverable";
  if (value === "disposable") return "disposable";
  return "unknown";
}

function safeSourceUrl(raw) {
  if (!raw) return "";
  try {
    const url = new URL(raw);
    if (!["http:", "https:"].includes(url.protocol)) return "";
    const host = url.hostname.toLowerCase().replace(/^www\./, "");
    if (["linkedin.com", "x.com", "twitter.com", "facebook.com", "instagram.com"].some((blocked) => host === blocked || host.endsWith(`.${blocked}`))) return "";
    return url.href;
  } catch {
    return "";
  }
}

export class HunterProvider {
  constructor({ apiKey, budget, fetchImpl = fetch, timeoutMs = 25_000 }) {
    this.apiKey = apiKey;
    this.budget = budget;
    this.fetchImpl = fetchImpl;
    this.timeoutMs = timeoutMs;
  }

  get configured() {
    return Boolean(this.apiKey);
  }

  async request(path, params) {
    this.budget.consume("hunter");
    const url = new URL(`${BASE_URL}/${path}`);
    for (const [key, value] of Object.entries(params)) {
      if (value != null && value !== "") url.searchParams.set(key, String(value));
    }
    const response = await this.fetchImpl(url, {
      headers: { Accept: "application/json", "X-API-KEY": this.apiKey },
      signal: AbortSignal.timeout(this.timeoutMs)
    });
    const body = await response.json().catch(() => ({}));
    if (!response.ok) {
      const message = body.errors?.[0]?.details ?? body.errors?.[0]?.id ?? `HTTP ${response.status}`;
      const error = new Error(`Hunter ${path} failed: ${message}`);
      error.status = response.status;
      throw error;
    }
    return body.data;
  }

  async find(target, limit = 10) {
    if (!this.configured) return [];
    return target.personName ? this.findPerson(target) : this.findDomain(target, limit);
  }

  async findPerson(target) {
    const { firstName, lastName } = splitPersonName(target.personName);
    if (!firstName || !lastName) return [];
    const data = await this.request("email-finder", { domain: target.domain, first_name: firstName, last_name: lastName });
    if (!data?.email) return [];
    const sources = data.sources ?? [];
    const sourceUrl = safeSourceUrl(sources[0]?.uri);
    return [{
      contactType: classifyEmail(data.email.toLowerCase(), target.domain, false),
      contactValue: data.email.toLowerCase(),
      sourceUrl,
      sourceType: sourceUrl ? "hunter_public" : (sources.length > 0 ? "forbidden_provider_source" : "hunter_inferred"),
      evidenceType: sourceUrl ? "provider_public_source" : "provider_domain_pattern",
      provider: "hunter",
      providerConfidence: data.score ?? "",
      verificationStatus: normalizedVerification(data.verification?.status),
      verifiedAt: nowIso(),
      observedAt: nowIso()
    }];
  }

  async findDomain(target, limit) {
    const data = await this.request("domain-search", { domain: target.domain, limit });
    return (data?.emails ?? []).slice(0, limit).map((record) => {
      const sourceUrl = safeSourceUrl(record.sources?.[0]?.uri);
      return {
        contactType: classifyEmail(record.value.toLowerCase(), target.domain, false),
        contactValue: record.value.toLowerCase(),
        sourceUrl,
        sourceType: sourceUrl ? "hunter_public" : (record.sources?.length > 0 ? "forbidden_provider_source" : "hunter_inferred"),
        evidenceType: sourceUrl ? "provider_public_source" : "provider_domain_pattern",
        provider: "hunter",
        providerConfidence: record.confidence ?? "",
        verificationStatus: normalizedVerification(record.verification?.status),
        verifiedAt: record.verification?.date ?? nowIso(),
        observedAt: nowIso(),
        personName: [record.first_name, record.last_name].filter(Boolean).join(" "),
        position: record.position ?? ""
      };
    });
  }

  async verify(email) {
    if (!this.configured) return { status: "unknown", checkedAt: "", provider: "" };
    const data = await this.request("email-verifier", { email });
    return {
      status: normalizedVerification(data?.status),
      checkedAt: nowIso(),
      provider: "hunter",
      score: data?.score ?? ""
    };
  }
}

export class ApiBudget {
  constructor(maxCalls) {
    this.maxCalls = maxCalls;
    this.used = 0;
    this.byProvider = {};
  }

  consume(provider) {
    if (this.used >= this.maxCalls) {
      const error = new Error(`API call budget ${this.maxCalls} exhausted`);
      error.code = "API_BUDGET_EXHAUSTED";
      throw error;
    }
    this.used += 1;
    this.byProvider[provider] = (this.byProvider[provider] ?? 0) + 1;
  }
}
