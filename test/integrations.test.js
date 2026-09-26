'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { consentUrl } = require('../src/integrations/drive');
const { trackQuestion } = require('../src/telemetry');

test('the Drive consent URL asks for offline access and carries the state', () => {
  const url = new URL(consentUrl('abc123'));
  assert.equal(url.origin, 'https://accounts.google.com');
  assert.equal(url.searchParams.get('state'), 'abc123');
  assert.equal(url.searchParams.get('access_type'), 'offline');
  assert.ok(url.searchParams.get('scope'));
});

test('analytics failures never break the app', async (t) => {
  t.mock.method(globalThis, 'fetch', async () => {
    throw new Error('offline');
  });
  await assert.doesNotReject(trackQuestion('u-alice', 'hello'));
});
