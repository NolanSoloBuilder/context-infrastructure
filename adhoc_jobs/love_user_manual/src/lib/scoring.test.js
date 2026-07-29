import test from 'node:test';
import assert from 'node:assert/strict';
import { questions, questionCountByAxis } from '../data/questions.js';
import { calculateScores, getBand, getResultKey, isComplete } from './scoring.js';

test('each axis has six questions and each question has five ordered options', () => {
  assert.deepEqual(questionCountByAxis, { recovery: 6, expression: 6, clarity: 6, repair: 6 });
  questions.forEach((question) => {
    assert.deepEqual(question.options.map((option) => option.value), [0, 25, 50, 75, 100]);
  });
});

test('all-low and all-high answers produce boundary scores', () => {
  const low = Object.fromEntries(questions.map((question) => [question.id, 0]));
  const high = Object.fromEntries(questions.map((question) => [question.id, 100]));
  assert.deepEqual(calculateScores(low), { recovery: 0, expression: 0, clarity: 0, repair: 0 });
  assert.deepEqual(calculateScores(high), { recovery: 100, expression: 100, clarity: 100, repair: 100 });
  assert.equal(isComplete(low), true);
});

test('dominant result follows the farthest direction from the midpoint', () => {
  assert.deepEqual(getResultKey({ recovery: 72, expression: 48, clarity: 51, repair: 55 }).key, 'recovery_high');
  assert.deepEqual(getResultKey({ recovery: 45, expression: 12, clarity: 51, repair: 55 }).key, 'expression_low');
});

test('near-center result is marked as a light tendency', () => {
  assert.equal(getResultKey({ recovery: 56, expression: 50, clarity: 50, repair: 50 }).light, true);
  assert.equal(getBand(37), 'low');
  assert.equal(getBand(63), 'high');
  assert.equal(getBand(50), 'mid');
});
