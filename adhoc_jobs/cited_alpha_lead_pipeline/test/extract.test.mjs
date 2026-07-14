import test from "node:test";
import assert from "node:assert/strict";
import { extractContactPoints } from "../src/extract/contact_points.mjs";

test("extracts public contact endpoints and ignores script text", () => {
  const html = `
    <html><body>
      <script>hidden@example.com</script>
      <p>For research inquiries email research@example.com</p>
      <a href="mailto:alex@example.com?subject=Hello">Email Alex</a>
      <a href="/team">Team</a>
      <a href="https://x.com/example">X</a>
      <a href="https://www.linkedin.com/company/example">LinkedIn</a>
      <a href="https://cal.com/example/demo">Book</a>
      <form action="/contact"><input type="email"></form>
    </body></html>`;
  const result = extractContactPoints(html, "https://example.com/contact", "example.com");
  const types = result.endpoints.map((endpoint) => endpoint.contactType);
  assert.ok(types.includes("role_business_email"));
  assert.ok(types.includes("named_work_email"));
  assert.ok(types.includes("x_profile"));
  assert.ok(types.includes("linkedin_profile"));
  assert.ok(types.includes("booking_url"));
  assert.ok(types.includes("contact_form"));
  assert.equal(result.endpoints.some((endpoint) => endpoint.contactValue === "hidden@example.com"), false);
  assert.deepEqual(result.internalLinks, ["https://example.com/team"]);
});

test("public free-mail address is held as a creator contact", () => {
  const result = extractContactPoints('<p>Business inquiries: creator [at] gmail [dot] com</p>', "https://creator.example/contact", "creator.example");
  assert.equal(result.endpoints[0].contactType, "public_creator_email");
  assert.equal(result.endpoints[0].contactValue, "creator@gmail.com");
});

test("newsletter and external form actions are not promoted as contact endpoints", () => {
  const newsletter = extractContactPoints('<form action="/subscribe"><input type="email"><button>Subscribe to newsletter</button></form>', "https://example.com/", "example.com");
  assert.equal(newsletter.endpoints.some((endpoint) => endpoint.contactType === "contact_form"), false);

  const external = extractContactPoints('<form action="https://attacker.example/collect"><input type="email"><button>Contact us</button></form>', "https://example.com/", "example.com");
  assert.equal(external.endpoints.some((endpoint) => endpoint.contactValue.includes("attacker.example")), false);
});

test("malformed mailto does not discard the page", () => {
  const result = extractContactPoints('<a href="mailto:%">bad</a><a href="https://x.com/example">X</a>', "https://example.com/contact", "example.com");
  assert.equal(result.endpoints.some((endpoint) => endpoint.contactType === "x_profile"), true);
});

test("generic local part on another domain remains an external email", () => {
  const result = extractContactPoints('<p>Contact contact@evil.example</p>', "https://example.com/contact", "example.com");
  assert.equal(result.endpoints[0].contactType, "external_work_email");
});
