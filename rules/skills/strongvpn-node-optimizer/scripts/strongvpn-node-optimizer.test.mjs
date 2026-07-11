import test from 'node:test';
import assert from 'node:assert/strict';

import {
  classifyPreferredRegion,
  parseServersModule,
} from './strongvpn-node-optimizer.mjs';

const fixture = `
export const serverMapping = {
  'str-sin303': { ip: atob('MjAzLjAuMTEzLjEw') },
  'str-nrt301': { ip: atob('MjAzLjAuMTEzLjEx') },
  'str-lax311': { ip: atob('MjAzLjAuMTEzLjEy') },
};
export const servers = {
  'Singapore': [{ value: 'str-sin303', label: 'Singapore' }],
  'Japan': [{ value: 'str-nrt301', label: 'Tokyo, Japan' }],
  'USA': [{ value: 'str-lax311', label: 'Los Angeles, USA' }],
};`;

test('parses StrongVPN catalog without executing remote code', () => {
  const parsed = parseServersModule(fixture);

  assert.deepEqual(
    parsed.map(({ id, country, ip }) => ({ id, country, ip })),
    [
      { id: 'str-sin303', country: 'Singapore', ip: '203.0.113.10' },
      { id: 'str-nrt301', country: 'Japan', ip: '203.0.113.11' },
      { id: 'str-lax311', country: 'USA', ip: '203.0.113.12' },
    ],
  );
  assert.equal(classifyPreferredRegion(parsed[0]), 'singapore');
  assert.equal(classifyPreferredRegion(parsed[1]), 'japan');
  assert.equal(classifyPreferredRegion(parsed[2]), 'us-west');
});

test('rejects executable expressions outside supported atob mappings', () => {
  assert.throws(
    () => parseServersModule("export const serverMapping = {}; export const servers = {}; fetch('x')"),
    /unsupported/i,
  );
});

test('rejects a server without an IP mapping', () => {
  const missingMapping = `
    export const serverMapping = {};
    export const servers = { 'Japan': [{ value: 'str-nrt301', label: 'Tokyo' }] };
  `;
  assert.throws(() => parseServersModule(missingMapping), /mapping/i);
});

test('ignores servers that are commented out in the official catalog', () => {
  const withDisabledServer = `
    export const serverMapping = {
      'str-lax308': { ip: atob('MjAzLjAuMTEzLjEz') },
      'str-lax311': { ip: atob('MjAzLjAuMTEzLjEy') },
    };
    export const servers = {
      'USA': [
        // { value: 'str-lax308', label: 'Los Angeles, USA' },
        { value: 'str-lax311', label: 'Los Angeles, USA' },
      ],
    };
  `;

  assert.deepEqual(parseServersModule(withDisabledServer).map(({ id }) => id), ['str-lax311']);
});
