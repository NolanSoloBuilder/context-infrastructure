import { randomUUID } from "node:crypto";
import { chmod } from "node:fs/promises";
import { readCsv, writeCsv } from "../csv.mjs";
import { normalizeTarget, inputEmailEndpoint, RED_SOURCES } from "./targets.mjs";
import { crawlOfficialSite } from "../discovery/official_site.mjs";
import { evaluateContact } from "../policy/gate.mjs";
import { contactSuppressed, loadSuppression } from "../policy/suppression.mjs";
import { ApiBudget, HunterProvider } from "../providers/hunter.mjs";
import {
  acquireAttemptMarker, acquireLock, appendEvent, clearAttemptMarker, readEvents,
  readJsonIfExists, writePrivateJson, writePrivateJsonAtomic
} from "../runtime/event_store.mjs";
import { ensureDir, nowIso, sha256 } from "../utils.mjs";

const PIPELINE_POLICY_VERSION = "2026-07-14.3";

export const OUTPUT_HEADERS = [
  "run_id", "target_id", "company", "person_name", "domain", "country", "contact_type", "contact_value",
  "source_type", "source_url", "source_observed_at", "provider", "provider_confidence", "verification_status",
  "verified_at", "jurisdiction", "gate_decision", "gate_reasons", "discovery_channel", "proof_url", "position"
];

function endpointKey(endpoint) {
  return `${endpoint.contactType}:${String(endpoint.contactValue).toLowerCase()}`;
}

function recentCompletedCacheKeys(events, refreshAfterDays) {
  const cutoff = Date.now() - refreshAfterDays * 86_400_000;
  return new Set(events
    .filter((event) => event.type === "target_completed" && Date.parse(event.at) >= cutoff)
    .map((event) => event.cacheKey)
    .filter(Boolean));
}

function cacheFresh(cache, maxAgeDays) {
  return Boolean(cache?.cachedAt) && Date.now() - Date.parse(cache.cachedAt) <= maxAgeDays * 86_400_000;
}

export function verificationFresh(endpoint, maxAgeDays, now = Date.now()) {
  const verifiedAt = Date.parse(endpoint?.verifiedAt);
  return ["deliverable", "undeliverable", "risky", "disposable"].includes(endpoint?.verificationStatus) &&
    Number.isFinite(verifiedAt) && now >= verifiedAt && now - verifiedAt <= maxAgeDays * 86_400_000;
}

function safeContactValue(endpoint, gate) {
  if (gate.decision === "reject" && ["personal_email", "invalid"].includes(endpoint.contactType)) {
    return "[redacted]";
  }
  return endpoint.contactValue;
}

function baseRecord(runId, target, endpoint, gate) {
  return {
    run_id: runId,
    target_id: target.targetId,
    company: target.company,
    person_name: endpoint.personName || target.personName,
    domain: target.domain,
    country: target.country,
    contact_type: endpoint.contactType,
    contact_value: safeContactValue(endpoint, gate),
    source_type: endpoint.sourceType,
    source_url: endpoint.sourceUrl,
    source_observed_at: endpoint.observedAt,
    provider: endpoint.provider || "",
    provider_confidence: endpoint.providerConfidence ?? "",
    verification_status: endpoint.verificationStatus || "not_applicable",
    verified_at: endpoint.verifiedAt || "",
    jurisdiction: gate.jurisdiction,
    gate_decision: gate.decision,
    gate_reasons: gate.reasons.join("|"),
    discovery_channel: target.discoveryChannel,
    proof_url: target.proofUrl,
    position: endpoint.position || ""
  };
}

function unresolvedRecord(runId, target, reason, decision = "hold") {
  return {
    run_id: runId, target_id: target.targetId, company: target.company, person_name: target.personName,
    domain: target.domain, country: target.country, contact_type: "unresolved", contact_value: "",
    source_type: target.acquisitionSourceType, source_url: "", source_observed_at: nowIso(), provider: "",
    provider_confidence: "", verification_status: "not_applicable", verified_at: "", jurisdiction: "UNKNOWN",
    gate_decision: decision, gate_reasons: reason, discovery_channel: target.discoveryChannel,
    proof_url: target.proofUrl, position: ""
  };
}

async function secureCsv(path, rows) {
  await writeCsv(path, rows, OUTPUT_HEADERS);
  await chmod(path, 0o600);
}

export async function validateInput(inputPath) {
  const rows = await readCsv(inputPath);
  const targets = rows.map(normalizeTarget);
  const duplicateIds = targets.filter((target, index) => targets.findIndex((candidate) => candidate.targetId === target.targetId) !== index);
  if (duplicateIds.length > 0) throw new Error(`Duplicate target_id values: ${duplicateIds.map((target) => target.targetId).join(", ")}`);
  return targets;
}

function decisionCounts(targetRecords) {
  return Object.fromEntries(["eligible_for_manual_review", "hold", "reject"].map((decision) => [
    decision,
    targetRecords.filter((record) => record.gate_decision === decision).length
  ]));
}

export async function runPipeline({ inputPath, outputDir, config, dryRun = false }) {
  const releaseLock = await acquireLock(outputDir);
  const eventPath = `${outputDir}/events.jsonl`;
  const runId = `${nowIso().replace(/[:.]/g, "-")}_${randomUUID().slice(0, 8)}`;
  const startedAt = nowIso();
  const runDir = `${outputDir}/runs/${runId}`;
  const cacheDir = `${outputDir}/cache`;
  const markerDir = `${outputDir}/attempts`;
  const budget = new ApiBudget(config.maxApiCalls);
  const providerCacheDays = config.providerCacheDays ?? 30;
  const verificationCacheDays = config.verificationCacheDays ?? 7;
  const hunter = new HunterProvider({
    apiKey: dryRun ? "" : process.env.HUNTER_API_KEY,
    budget,
    timeoutMs: Math.min(config.requestTimeoutMs * 2, 30_000)
  });
  const records = [];
  const pageEvidence = [];
  const errors = [];

  try {
    await Promise.all([ensureDir(runDir), ensureDir(cacheDir), ensureDir(markerDir)]);
    await Promise.all([chmod(runDir, 0o700), chmod(cacheDir, 0o700), chmod(markerDir, 0o700)]);
    const targets = await validateInput(inputPath);
    if (targets.length > config.maxTargets) throw new Error(`Input has ${targets.length} targets, exceeding maxTargets=${config.maxTargets}`);
    const suppression = await loadSuppression(
      config.suppressionPath || `${outputDir}/suppression.csv`,
      { required: Boolean(config.suppressionRequired || config.suppressionPath) }
    );
    const priorEvents = await readEvents(eventPath);
    const completedKeys = recentCompletedCacheKeys(priorEvents, Math.min(config.refreshAfterDays, verificationCacheDays));
    const executionFingerprint = sha256(JSON.stringify({
      policyVersion: PIPELINE_POLICY_VERSION,
      dryRun,
      hunterConfigured: hunter.configured,
      maxPagesPerDomain: config.maxPagesPerDomain,
      suppressionFingerprint: suppression.fingerprint
    }));
    await appendEvent(eventPath, {
      eventId: randomUUID(), runId, type: "run_started", at: startedAt,
      inputHash: sha256(JSON.stringify(targets)), executionFingerprint, dryRun
    });

    for (const target of targets) {
      if ((Date.now() - Date.parse(startedAt)) / 1000 > config.maxRuntimeSeconds) {
        errors.push({ targetId: target.targetId, error: "MAX_RUNTIME_EXCEEDED" });
        break;
      }
      const cacheKey = sha256(`${target.targetKey}:${executionFingerprint}`);
      const targetCachePath = `${cacheDir}/target_${cacheKey}.json`;
      if (suppression.targetIds.has(target.targetId)) {
        const targetRecords = [unresolvedRecord(runId, target, "SUPPRESSED_TARGET", "reject")];
        records.push(...targetRecords);
        await writePrivateJsonAtomic(targetCachePath, { cachedAt: nowIso(), records: targetRecords });
        await appendEvent(eventPath, { eventId: randomUUID(), runId, type: "target_completed", at: nowIso(), cacheKey, counts: decisionCounts(targetRecords) });
        continue;
      }
      if (completedKeys.has(cacheKey)) {
        const cached = await readJsonIfExists(targetCachePath);
        if (cacheFresh(cached, Math.min(config.refreshAfterDays, verificationCacheDays)) && cached?.records) {
          records.push(...cached.records.map((record) => contactSuppressed(suppression, record.contact_value)
            ? { ...record, run_id: runId, gate_decision: "reject", gate_reasons: "SUPPRESSED" }
            : { ...record, run_id: runId }));
          await appendEvent(eventPath, { eventId: randomUUID(), runId, type: "target_reused_cache", at: nowIso(), cacheKey });
          continue;
        }
      }

      await appendEvent(eventPath, { eventId: randomUUID(), runId, type: "target_started", at: nowIso(), cacheKey });
      if (RED_SOURCES.has(target.acquisitionSourceType)) {
        const targetRecords = [unresolvedRecord(runId, target, "FORBIDDEN_ACQUISITION_SOURCE", "reject")];
        records.push(...targetRecords);
        await writePrivateJsonAtomic(targetCachePath, { cachedAt: nowIso(), records: targetRecords });
        await appendEvent(eventPath, { eventId: randomUUID(), runId, type: "target_completed", at: nowIso(), cacheKey, counts: decisionCounts(targetRecords) });
        continue;
      }
      const endpoints = [];
      const inputEndpoint = inputEmailEndpoint(target, nowIso());
      if (inputEndpoint) endpoints.push(inputEndpoint);

      const crawl = await crawlOfficialSite(target, config);
      endpoints.push(...crawl.endpoints);
      pageEvidence.push(...crawl.pages.map((page) => ({ targetKey: target.targetKey, ...page })));
      let deferred = crawl.crawlStatus !== "COMPLETE";
      let providerIndeterminate = false;

      const publicEmailFound = endpoints.some((endpoint) => endpoint.contactType.endsWith("email"));
      if (!publicEmailFound && crawl.crawlStatus === "COMPLETE" && hunter.configured) {
        const providerCachePath = `${cacheDir}/hunter_find_v2_${target.targetKey}.json`;
        const providerMarkerPath = `${markerDir}/hunter_find_v2_${target.targetKey}.marker`;
        const cachedProvider = await readJsonIfExists(providerCachePath);
        if (cacheFresh(cachedProvider, providerCacheDays) && cachedProvider?.endpoints) {
          endpoints.push(...cachedProvider.endpoints);
        } else if (await acquireAttemptMarker(providerMarkerPath, { targetKey: target.targetKey, at: nowIso() })) {
          try {
            const found = await hunter.find(target, config.maxProviderContactsPerTarget);
            await writePrivateJsonAtomic(providerCachePath, { cachedAt: nowIso(), endpoints: found });
            await clearAttemptMarker(providerMarkerPath);
            endpoints.push(...found);
          } catch (error) {
            providerIndeterminate = true;
            errors.push({ targetId: target.targetId, stage: "hunter_find", error: error.message });
          }
        } else {
          providerIndeterminate = true;
          errors.push({ targetId: target.targetId, stage: "hunter_find", error: "PROVIDER_ATTEMPT_INDETERMINATE" });
        }
      }

      const deduped = [...new Map(endpoints.map((endpoint) => [endpointKey(endpoint), endpoint])).values()];
      for (const endpoint of deduped) {
        const suppressed = contactSuppressed(suppression, endpoint.contactValue);
        const workEmail = ["named_work_email", "role_business_email"].includes(endpoint.contactType);
        const needsVerification = workEmail && !verificationFresh(endpoint, verificationCacheDays);
        if (!suppressed && needsVerification && hunter.configured) {
          const emailKey = sha256(endpoint.contactValue.toLowerCase());
          const verificationCachePath = `${cacheDir}/hunter_verify_v2_${emailKey}.json`;
          const verificationMarkerPath = `${markerDir}/hunter_verify_v2_${emailKey}.marker`;
          const cachedVerification = await readJsonIfExists(verificationCachePath);
          if (cacheFresh(cachedVerification, verificationCacheDays) && cachedVerification?.verification) {
            Object.assign(endpoint, cachedVerification.verification);
          } else if (await acquireAttemptMarker(verificationMarkerPath, { emailKey, at: nowIso() })) {
            try {
              const result = await hunter.verify(endpoint.contactValue);
              const verification = {
                verificationStatus: result.status,
                verifiedAt: result.checkedAt,
                provider: endpoint.provider || result.provider,
                providerConfidence: endpoint.providerConfidence || result.score
              };
              await writePrivateJsonAtomic(verificationCachePath, { cachedAt: nowIso(), verification });
              await clearAttemptMarker(verificationMarkerPath);
              Object.assign(endpoint, verification);
            } catch (error) {
              providerIndeterminate = true;
              endpoint.verificationStatus = "unknown";
              errors.push({ targetId: target.targetId, stage: "hunter_verify", error: error.message });
            }
          } else {
            providerIndeterminate = true;
            endpoint.verificationStatus = "unknown";
            errors.push({ targetId: target.targetId, stage: "hunter_verify", error: "VERIFIER_ATTEMPT_INDETERMINATE" });
          }
        } else if (!suppressed && needsVerification) {
          endpoint.verificationStatus = "unknown";
          endpoint.verifiedAt = "";
        }
        const gate = evaluateContact(target, endpoint, { suppressed });
        records.push(baseRecord(runId, target, endpoint, gate));
      }

      if (deduped.length === 0) {
        records.push(unresolvedRecord(runId, target, providerIndeterminate ? "PROVIDER_ATTEMPT_INDETERMINATE" : (crawl.deferredReason || "NO_PUBLIC_CONTACT_FOUND")));
      }
      deferred ||= providerIndeterminate;
      const targetRecords = records.filter((record) => record.target_id === target.targetId);
      if (deferred) {
        await appendEvent(eventPath, {
          eventId: randomUUID(), runId, type: "target_deferred", at: nowIso(), cacheKey,
          reason: providerIndeterminate ? "PROVIDER_ATTEMPT_INDETERMINATE" : crawl.deferredReason,
          counts: decisionCounts(targetRecords)
        });
      } else {
        await writePrivateJsonAtomic(targetCachePath, { cachedAt: nowIso(), records: targetRecords });
        await appendEvent(eventPath, { eventId: randomUUID(), runId, type: "target_completed", at: nowIso(), cacheKey, counts: decisionCounts(targetRecords) });
      }
    }

    const eligible = records.filter((record) => record.gate_decision === "eligible_for_manual_review");
    const holds = records.filter((record) => record.gate_decision === "hold");
    const rejected = records.filter((record) => record.gate_decision === "reject");
    await Promise.all([
      secureCsv(`${runDir}/eligible_for_manual_review.csv`, eligible),
      secureCsv(`${runDir}/holds.csv`, holds),
      secureCsv(`${runDir}/rejected.csv`, rejected),
      writePrivateJson(`${runDir}/page_evidence.json`, pageEvidence),
      writePrivateJson(`${runDir}/manifest.json`, {
        runId, startedAt, finishedAt: nowIso(), inputPath, dryRun, executionFingerprint,
        config: { ...config, userAgent: config.userAgent },
        counts: { inputTargets: targets.length, contactRecords: records.length, eligible: eligible.length, holds: holds.length, rejected: rejected.length },
        apiCalls: budget.used, apiCallsByProvider: budget.byProvider, errors
      }),
      writePrivateJson(`${outputDir}/latest.json`, { runId, runDir, finishedAt: nowIso() })
    ]);
    await appendEvent(eventPath, {
      eventId: randomUUID(), runId, type: "run_completed", at: nowIso(),
      counts: { eligible: eligible.length, holds: holds.length, rejected: rejected.length }, errors: errors.length
    });
    return { runId, runDir, eligible: eligible.length, holds: holds.length, rejected: rejected.length, errors };
  } finally {
    await releaseLock();
  }
}
