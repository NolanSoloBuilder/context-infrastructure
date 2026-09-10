import test from "node:test";
import assert from "node:assert/strict";
import {
  applyForkChoice,
  getLevelProgress,
  isHiddenRouteUnlocked,
  shouldTriggerFork,
} from "./levelGame.js";

test("fork event triggers once after the second correct letter", () => {
  assert.equal(shouldTriggerFork({ cityIndex: 0, typedLength: 1, resolved: false }), false);
  assert.equal(shouldTriggerFork({ cityIndex: 0, typedLength: 2, resolved: false }), true);
  assert.equal(shouldTriggerFork({ cityIndex: 0, typedLength: 3, resolved: true }), false);
});

test("fork choices clamp resource values", () => {
  const result = applyForkChoice(
    { money: 20, stamina: 59, luck: 95 },
    { moneyDelta: -40, staminaDelta: 4, luckDelta: 15 },
  );
  assert.deepEqual(result, { money: 0, stamina: 60, luck: 100 });
});

test("level and easter egg progress use deterministic thresholds", () => {
  assert.equal(Math.round(getLevelProgress(1, 0.5, 4)), 50);
  assert.equal(isHiddenRouteUnlocked(11), false);
  assert.equal(isHiddenRouteUnlocked(12), true);
});
