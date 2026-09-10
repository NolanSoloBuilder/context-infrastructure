import test from "node:test";
import assert from "node:assert/strict";
import {
  buildRouteNodeGeoJson,
  getJourneyCursor,
  getRouteJourney,
} from "./routeJourney.js";

const points = [
  { name: "甲", coordinates: [100, 30] },
  { name: "乙", coordinates: [101, 30] },
  { name: "丙", coordinates: [102, 31] },
];
const road = [
  [100, 30],
  [100.5, 30.2],
  [101, 30],
  [101.5, 30.4],
  [102, 31],
];

test("typing progress becomes a continuous route cursor", () => {
  assert.equal(getJourneyCursor(1, 0.25), 1.25);
  assert.equal(getJourneyCursor(0, 2), 1);
});

test("vehicle position follows stored road geometry", () => {
  const journey = getRouteJourney(road, points, 0.5);
  assert.deepEqual(journey.position, [100.5, 30.2]);
  assert.deepEqual(journey.completed.at(-1), journey.position);
});

test("route nodes expose passed, current, and next states", () => {
  const nodes = buildRouteNodeGeoJson(points, 0.5, false);
  assert.deepEqual(
    nodes.features.map((feature) => feature.properties.state),
    ["passed", "current", "next"],
  );
});
