import { classifyEmail } from "../extract/contact_points.mjs";
import { normalizeDomain, parseBoolean, sha256 } from "../utils.mjs";

const FORBIDDEN_DOMAINS = new Set(["linkedin.com", "x.com", "twitter.com", "facebook.com", "instagram.com"]);
const ALLOWED_SOURCES = new Set([
  "official_company_website", "public_web", "first_party_optin", "first_party_demo_request",
  "first_party_webinar", "linkedin_leadgen_submitted", "inbound", "licensed_b2b_vendor",
  "hunter_public", "hunter_inferred"
]);
export const RED_SOURCES = new Set([
  "linkedin_scraped", "x_scraped", "browser_extension_export", "bulk_email_permutation",
  "smtp_spray", "people_search_personal_email", "breach_or_dump", "broker_without_provenance",
  "third_party_referral_email", "spreadsheet_without_source", "suppressed_reimport"
]);

export function normalizeTarget(row, index) {
  const domain = normalizeDomain(row.domain || row.website_url);
  if (!domain) throw new Error(`Row ${index + 2}: domain is required`);
  if ([...FORBIDDEN_DOMAINS].some((blocked) => domain === blocked || domain.endsWith(`.${blocked}`))) {
    throw new Error(`Row ${index + 2}: social platforms cannot be target domains`);
  }
  const acquisitionSourceType = (row.acquisition_source_type || "official_company_website").toLowerCase();
  if (!ALLOWED_SOURCES.has(acquisitionSourceType) && !RED_SOURCES.has(acquisitionSourceType)) {
    throw new Error(`Row ${index + 2}: unknown acquisition_source_type=${acquisitionSourceType}`);
  }
  const target = {
    targetId: row.target_id || sha256(`${domain}:${row.person_name || "account"}`).slice(0, 16),
    company: row.company || domain,
    domain,
    websiteUrl: row.website_url || "",
    personName: row.person_name || "",
    inputEmail: row.input_email?.toLowerCase() || "",
    emailSourceUrl: row.email_source_url || "",
    country: row.country || "",
    subscriberType: (row.subscriber_type || "unknown").toLowerCase(),
    discoveryChannel: row.discovery_channel || "",
    proofUrl: row.proof_url || "",
    acquisitionSourceType,
    optIn: parseBoolean(row.opt_in),
    marketingPermission: row.marketing_permission || (parseBoolean(row.opt_in) ? "opt_in" : "unknown"),
    consentEventId: row.consent_event_id || "",
    consentedAt: row.consented_at || "",
    consentTextVersion: row.consent_text_version || "",
    inboundEventId: row.inbound_event_id || "",
    inboundAt: row.inbound_at || "",
    canSpamReady: parseBoolean(row.can_spam_ready),
    privacyNoticeReady: parseBoolean(row.privacy_notice_ready)
  };
  target.targetKey = sha256(JSON.stringify(target));
  return target;
}

export function inputEmailEndpoint(target, observedAt) {
  if (!target.inputEmail) return null;
  return {
    contactType: classifyEmail(
      target.inputEmail,
      target.domain,
      Boolean(target.emailSourceUrl) && ["official_company_website", "first_party_optin", "inbound"].includes(target.acquisitionSourceType)
    ),
    contactValue: target.inputEmail,
    sourceUrl: target.emailSourceUrl,
    sourceType: target.acquisitionSourceType,
    evidenceType: "input_record",
    verificationStatus: "unknown",
    observedAt
  };
}
