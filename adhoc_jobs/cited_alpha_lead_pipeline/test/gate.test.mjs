import test from "node:test";
import assert from "node:assert/strict";
import { evaluateContact } from "../src/policy/gate.mjs";

const endpoint = {
  contactType: "named_work_email",
  sourceType: "official_website",
  sourceUrl: "https://example.com/contact",
  observedAt: "2026-07-14T00:00:00.000Z",
  verificationStatus: "deliverable"
};

test("US verified work email reaches manual review only when controls are ready", () => {
  assert.equal(evaluateContact({ domain: "example.com", country: "US", canSpamReady: true }, endpoint).decision, "eligible_for_manual_review");
  assert.equal(evaluateContact({ domain: "example.com", country: "US", canSpamReady: false }, endpoint).decision, "hold");
});

test("vendor, opt-in and inbound labels do not self-prove provenance", () => {
  for (const sourceType of ["licensed_b2b_vendor", "first_party_optin", "inbound"]) {
    const result = evaluateContact({ domain: "example.com", country: "US", canSpamReady: true, marketingPermission: "unknown" }, {
      ...endpoint, sourceType, sourceUrl: "", provider: ""
    });
    assert.equal(result.decision, "hold");
  }
});

test("first-party opt-in and inbound require auditable event evidence", () => {
  const optInTarget = {
    domain: "example.com", country: "US", canSpamReady: true, marketingPermission: "opt_in",
    consentEventId: "consent_123", consentedAt: "2026-07-01T10:00:00.000Z", consentTextVersion: "privacy-v3"
  };
  assert.equal(evaluateContact(optInTarget, {
    ...endpoint, sourceType: "first_party_optin", sourceUrl: "https://unrelated.example/form"
  }).decision, "hold");
  assert.equal(evaluateContact(optInTarget, {
    ...endpoint, sourceType: "first_party_optin", sourceUrl: "https://example.com/newsletter"
  }).decision, "eligible_for_manual_review");

  const inboundTarget = {
    domain: "example.com", country: "US", canSpamReady: true, marketingPermission: "inbound",
    inboundEventId: "demo_456", inboundAt: "2026-07-02T11:00:00.000Z"
  };
  assert.equal(evaluateContact(inboundTarget, {
    ...endpoint, sourceType: "inbound", sourceUrl: "https://example.com/demo"
  }).decision, "eligible_for_manual_review");
  assert.equal(evaluateContact({ ...inboundTarget, inboundAt: "not-a-time" }, {
    ...endpoint, sourceType: "inbound", sourceUrl: "https://example.com/demo"
  }).decision, "hold");
});

test("EU cold email is held unless opt-in exists", () => {
  assert.equal(evaluateContact({ domain: "example.com", country: "DE", marketingPermission: "unknown" }, endpoint).decision, "hold");
  const target = {
    domain: "example.com", country: "DE", marketingPermission: "opt_in", privacyNoticeReady: true,
    consentEventId: "consent_eu_1", consentedAt: "2026-07-01T10:00:00.000Z", consentTextVersion: "privacy-v3"
  };
  assert.equal(evaluateContact(target, { ...endpoint, sourceType: "first_party_optin" }).decision, "eligible_for_manual_review");
  assert.equal(evaluateContact({ ...target, consentEventId: "" }, { ...endpoint, sourceType: "first_party_optin" }).decision, "hold");
});

test("private email is rejected and official social profile is manual only", () => {
  assert.equal(evaluateContact({ country: "US" }, { contactType: "personal_email" }).decision, "reject");
  const social = evaluateContact({ domain: "example.com", country: "US" }, { contactType: "x_profile", sourceType: "official_website", sourceUrl: "https://example.com/contact" });
  assert.equal(social.decision, "eligible_for_manual_review");
  assert.ok(social.reasons.includes("NATIVE_PLATFORM_MANUAL_ONLY"));
});

test("unknown verifier status, missing provenance and suppression fail closed", () => {
  assert.equal(evaluateContact({ domain: "example.com", country: "US", canSpamReady: true }, { ...endpoint, verificationStatus: "risky" }).decision, "hold");
  assert.equal(evaluateContact({ domain: "example.com", country: "US", canSpamReady: true }, { ...endpoint, sourceUrl: "" }).decision, "hold");
  assert.equal(evaluateContact({ domain: "example.com", country: "US", canSpamReady: true }, endpoint, { suppressed: true }).decision, "reject");
});
