export const INITIAL_RESOURCES = Object.freeze({
  money: 1240,
  stamina: 56,
  luck: 75,
});

export function shouldTriggerFork({ cityIndex, typedLength, resolved }) {
  return cityIndex === 0 && typedLength >= 2 && !resolved;
}

export function applyForkChoice(resources, choice) {
  return {
    money: Math.max(0, resources.money + choice.moneyDelta),
    stamina: Math.min(60, Math.max(0, resources.stamina + choice.staminaDelta)),
    luck: Math.min(100, Math.max(0, resources.luck + choice.luckDelta)),
  };
}

export function getLevelProgress(cityIndex, typedProgress, cityCount) {
  const completedSegments = Math.max(cityCount - 1, 1);
  return Math.min(100, ((cityIndex + typedProgress) / completedSegments) * 100);
}

export function isHiddenRouteUnlocked(totalCorrectLetters) {
  return totalCorrectLetters >= 12;
}
