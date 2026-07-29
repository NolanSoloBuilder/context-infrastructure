import { axes, questions } from '../data/questions.js';

export function calculateScores(answers) {
  const totals = Object.fromEntries(Object.keys(axes).map((axis) => [axis, []]));

  questions.forEach((question) => {
    const answer = answers[question.id];
    if (Number.isFinite(answer)) totals[question.axis].push(answer);
  });

  return Object.fromEntries(
    Object.entries(totals).map(([axis, values]) => [
      axis,
      values.length ? Math.round(values.reduce((sum, value) => sum + value, 0) / values.length) : 50,
    ]),
  );
}

export function getResultKey(scores) {
  const dominant = Object.entries(scores)
    .map(([axis, score]) => ({ axis, score, distance: Math.abs(score - 50) }))
    .sort((a, b) => b.distance - a.distance)[0];

  return {
    key: `${dominant.axis}_${dominant.score >= 50 ? 'high' : 'low'}`,
    axis: dominant.axis,
    light: dominant.distance < 8,
    distance: dominant.distance,
  };
}

export function getBand(score) {
  if (score < 38) return 'low';
  if (score > 62) return 'high';
  return 'mid';
}

export function isComplete(answers) {
  return questions.every((question) => Number.isFinite(answers[question.id]));
}
