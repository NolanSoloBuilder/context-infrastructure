const EU_COUNTRIES = new Set([
  "AT", "BE", "BG", "HR", "CY", "CZ", "DK", "EE", "FI", "FR", "DE", "GR", "EL", "HU",
  "IE", "IT", "LV", "LT", "LU", "MT", "NL", "PL", "PT", "RO", "SK", "SI", "ES", "SE",
  "AUSTRIA", "BELGIUM", "BULGARIA", "CROATIA", "CYPRUS", "CZECHIA", "DENMARK", "ESTONIA",
  "FINLAND", "FRANCE", "GERMANY", "GREECE", "HUNGARY", "IRELAND", "ITALY", "LATVIA",
  "LITHUANIA", "LUXEMBOURG", "MALTA", "NETHERLANDS", "POLAND", "PORTUGAL", "ROMANIA",
  "SLOVAKIA", "SLOVENIA", "SPAIN", "SWEDEN"
]);
const US_VALUES = new Set(["US", "USA", "UNITED STATES", "UNITED STATES OF AMERICA"]);
const UK_VALUES = new Set(["UK", "GB", "GBR", "UNITED KINGDOM"]);
const SOCIAL_TYPES = new Set(["x_profile", "linkedin_profile"]);
const PUBLIC_CHANNEL_TYPES = new Set(["contact_form", "booking_url", ...SOCIAL_TYPES]);

function jurisdiction(country) {
  const value = String(country ?? "").trim().toUpperCase();
  if (EU_COUNTRIES.has(value)) return "EU";
  if (US_VALUES.has(value)) return "US";
  if (UK_VALUES.has(value)) return "UK";
  return "UNKNOWN";
}

function validHttpUrl(value) {
  try { return ["http:", "https:"].includes(new URL(value).protocol); } catch { return false; }
}

function sourceHostForbidden(value) {
  if (!validHttpUrl(value)) return false;
  const host = new URL(value).hostname.toLowerCase().replace(/^www\./, "");
  return ["linkedin.com", "x.com", "twitter.com", "facebook.com", "instagram.com"].some((blocked) => host === blocked || host.endsWith(`.${blocked}`));
}

function sourceMatchesTarget(value, targetDomain) {
  if (!validHttpUrl(value)) return false;
  const host = new URL(value).hostname.toLowerCase().replace(/^www\./, "");
  return host === targetDomain || host.endsWith(`.${targetDomain}`);
}

function validTimestamp(value) {
  return Boolean(value) && Number.isFinite(Date.parse(value));
}

function optInEvidenceComplete(target, endpoint) {
  return sourceMatchesTarget(endpoint.sourceUrl, target.domain) &&
    String(target.marketingPermission).toLowerCase() === "opt_in" &&
    Boolean(target.consentEventId) && validTimestamp(target.consentedAt) && Boolean(target.consentTextVersion);
}

function inboundEvidenceComplete(target, endpoint) {
  return sourceMatchesTarget(endpoint.sourceUrl, target.domain) &&
    String(target.marketingPermission).toLowerCase() === "inbound" &&
    Boolean(target.inboundEventId) && validTimestamp(target.inboundAt);
}

export function evaluateContact(target, endpoint, { suppressed = false } = {}) {
  const reasons = [];
  const region = jurisdiction(target.country);
  const permission = String(target.marketingPermission ?? "unknown").toLowerCase();

  if (suppressed) return { decision: "reject", reasons: ["SUPPRESSED"], jurisdiction: region };
  if (endpoint.sourceType === "forbidden_provider_source") {
    return { decision: "reject", reasons: ["FORBIDDEN_PROVIDER_SOURCE"], jurisdiction: region };
  }

  if (PUBLIC_CHANNEL_TYPES.has(endpoint.contactType)) {
    if (endpoint.sourceType !== "official_website" || !sourceMatchesTarget(endpoint.sourceUrl, target.domain)) {
      return { decision: "hold", reasons: ["PUBLIC_CHANNEL_PROVENANCE_MISSING"], jurisdiction: region };
    }
    reasons.push("OFFICIAL_PUBLIC_CHANNEL", SOCIAL_TYPES.has(endpoint.contactType) ? "NATIVE_PLATFORM_MANUAL_ONLY" : "MANUAL_OUTREACH_ONLY");
    return { decision: "eligible_for_manual_review", reasons, jurisdiction: region };
  }

  if (["personal_email", "invalid"].includes(endpoint.contactType)) {
    return { decision: "reject", reasons: ["PERSONAL_OR_INVALID_EMAIL"], jurisdiction: region };
  }
  if (endpoint.contactType === "external_work_email") {
    return { decision: "reject", reasons: ["EMAIL_DOMAIN_MISMATCH"], jurisdiction: region };
  }
  if (endpoint.contactType === "public_creator_email") {
    reasons.push("PUBLIC_CREATOR_EMAIL_REQUIRES_CONTEXT_REVIEW");
  }
  if (["undeliverable", "disposable"].includes(endpoint.verificationStatus)) {
    return { decision: "reject", reasons: [`VERIFICATION_${endpoint.verificationStatus.toUpperCase()}`], jurisdiction: region };
  }
  if (endpoint.verificationStatus !== "deliverable") {
    reasons.push(`VERIFICATION_${String(endpoint.verificationStatus ?? "unknown").toUpperCase()}`);
  }
  if (endpoint.sourceType === "hunter_inferred") reasons.push("INFERRED_EMAIL");
  if (endpoint.sourceType === "hunter_public" && (!validHttpUrl(endpoint.sourceUrl) || sourceHostForbidden(endpoint.sourceUrl))) {
    reasons.push("PROVIDER_PROVENANCE_INVALID");
  }
  if (endpoint.sourceType === "official_website" && !sourceMatchesTarget(endpoint.sourceUrl, target.domain)) reasons.push("SOURCE_URL_INVALID_OR_MISMATCHED");
  if (endpoint.sourceType === "licensed_b2b_vendor" && (!validHttpUrl(endpoint.sourceUrl) || !endpoint.provider)) reasons.push("VENDOR_PROVENANCE_INCOMPLETE");
  const optInEvidence = optInEvidenceComplete(target, endpoint);
  const inboundEvidence = inboundEvidenceComplete(target, endpoint);
  if ((endpoint.sourceType === "first_party_optin" || permission === "opt_in") && !optInEvidence) reasons.push("OPT_IN_EVIDENCE_INCOMPLETE");
  if ((endpoint.sourceType === "inbound" || permission === "inbound") && !inboundEvidence) reasons.push("INBOUND_EVIDENCE_INCOMPLETE");
  if (!endpoint.observedAt) reasons.push("SOURCE_OBSERVED_AT_MISSING");
  if (!["official_website", "hunter_public", "hunter_inferred", "licensed_b2b_vendor", "first_party_optin", "inbound"].includes(endpoint.sourceType)) {
    reasons.push("SOURCE_TYPE_UNAPPROVED");
  }

  if (region === "EU") {
    if (!optInEvidence && !inboundEvidence) reasons.push("EU_REQUIRES_OPT_IN");
    if (!target.privacyNoticeReady) reasons.push("PRIVACY_NOTICE_NOT_READY");
  }
  if (region === "UK") {
    const corporateAllowed = permission === "corporate_rule" && target.subscriberType === "corporate";
    if (!optInEvidence && !inboundEvidence && !corporateAllowed) reasons.push("UK_PERMISSION_OR_ENTITY_UNCONFIRMED");
    if (!target.privacyNoticeReady) reasons.push("PRIVACY_NOTICE_NOT_READY");
  }
  if (region === "US" && !target.canSpamReady) reasons.push("CAN_SPAM_CONTROLS_NOT_READY");
  if (region === "UNKNOWN") reasons.push("JURISDICTION_UNKNOWN");

  const blockingReview = reasons.some((reason) => [
    "PUBLIC_CREATOR_EMAIL_REQUIRES_CONTEXT_REVIEW", "INFERRED_EMAIL",
    "EU_REQUIRES_OPT_IN", "UK_PERMISSION_OR_ENTITY_UNCONFIRMED",
    "PRIVACY_NOTICE_NOT_READY", "CAN_SPAM_CONTROLS_NOT_READY", "JURISDICTION_UNKNOWN",
    "PROVIDER_PROVENANCE_INVALID", "SOURCE_URL_INVALID_OR_MISMATCHED", "SOURCE_TYPE_UNAPPROVED",
    "VENDOR_PROVENANCE_INCOMPLETE", "OPT_IN_EVIDENCE_INCOMPLETE", "INBOUND_EVIDENCE_INCOMPLETE",
    "SOURCE_OBSERVED_AT_MISSING"
  ].includes(reason) || reason.startsWith("VERIFICATION_"));
  return {
    decision: blockingReview ? "hold" : "eligible_for_manual_review",
    reasons: reasons.length > 0 ? reasons : ["WORK_EMAIL_VERIFIED_AND_POLICY_FIELDS_PRESENT"],
    jurisdiction: region
  };
}
