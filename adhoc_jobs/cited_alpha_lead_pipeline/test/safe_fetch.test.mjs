import test from "node:test";
import assert from "node:assert/strict";
import { hostAllowed, isPublicAddress, validatePublicUrl } from "../src/net/safe_fetch.mjs";

test("SSRF policy blocks private and reserved IP ranges", () => {
  assert.equal(isPublicAddress("127.0.0.1", 4), false);
  assert.equal(isPublicAddress("169.254.169.254", 4), false);
  assert.equal(isPublicAddress("10.0.0.1", 4), false);
  assert.equal(isPublicAddress("8.8.8.8", 4), true);
  assert.equal(isPublicAddress("::1", 6), false);
  assert.equal(isPublicAddress("64:ff9b::7f00:1", 6), false);
  assert.equal(isPublicAddress("2002:7f00:1::", 6), false);
});

test("URL policy restricts schemes, hosts, credentials and ports", () => {
  assert.equal(hostAllowed("www.example.com", "example.com"), true);
  assert.equal(hostAllowed("private.example.com", "example.com"), false);
  assert.throws(() => validatePublicUrl("https://evil.example.net", "example.com"), /outside target domain/);
  assert.throws(() => validatePublicUrl("file:///etc/passwd", "example.com"), /Forbidden URL scheme/);
  assert.throws(() => validatePublicUrl("https://user:pass@example.com", "example.com"), /credentials/);
  assert.throws(() => validatePublicUrl("https://example.com:8443", "example.com"), /Forbidden port/);
});
