import test from "node:test";
import assert from "node:assert/strict";
import { ApiBudget, HunterProvider } from "../src/providers/hunter.mjs";

function response(data) {
  return { ok: true, status: 200, json: async () => ({ data }) };
}

test("Hunter adapter reclassifies free-mail and rejects social provenance", async () => {
  const provider = new HunterProvider({
    apiKey: "test",
    budget: new ApiBudget(2),
    fetchImpl: async () => response({
      email: "victim@gmail.com",
      score: 99,
      sources: [{ uri: "https://linkedin.com/in/victim" }],
      verification: { status: "valid" }
    })
  });
  const [result] = await provider.find({ personName: "Test Person", domain: "example.com" });
  assert.equal(result.contactType, "personal_email");
  assert.equal(result.sourceType, "forbidden_provider_source");
});
