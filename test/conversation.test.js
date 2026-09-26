'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

process.env.NOTEWISE_DATA_DIR = fs.mkdtempSync(path.join(os.tmpdir(), 'notewise-test-'));
const { askAboutNotes, buildPrompt } = require('../src/conversation');
const history = require('../src/history');

function fakeModel(text) {
  const calls = [];
  const fetchImpl = async (url, init) => {
    calls.push({ url, body: JSON.parse(init.body) });
    return { json: async () => ({ text }) };
  };
  return { calls, fetchImpl };
}

test.beforeEach((t) => {
  t.mock.method(globalThis, 'fetch', async () => ({ ok: true }));
});

test('buildPrompt includes the note titles and the question', () => {
  const prompt = buildPrompt('what do I need to buy?', [{ title: 'groceries' }], []);
  assert.match(prompt, /- groceries/);
  assert.match(prompt, /user: what do I need to buy\?$/);
});

test('askAboutNotes answers from the model and remembers the turn', async () => {
  const model = fakeModel('eggs and milk');
  const reply = await askAboutNotes('u-alice', 'what do I need to buy?', [{ title: 'groceries' }], model.fetchImpl);
  assert.deepEqual(reply, { answer: 'eggs and milk' });
  assert.equal(model.calls.length, 1);
  assert.deepEqual(history.load('u-alice').slice(-2), [
    { role: 'user', content: 'what do I need to buy?' },
    { role: 'assistant', content: 'eggs and milk' },
  ]);
});

test('follow-up questions carry the earlier turns', async () => {
  const model = fakeModel('yes');
  await askAboutNotes('u-bob', 'first question', [], fakeModel('first answer').fetchImpl);
  await askAboutNotes('u-bob', 'and then?', [], model.fetchImpl);
  assert.match(model.calls[0].body.prompt, /assistant: first answer/);
});

test('history is kept per user', () => {
  history.save('u-carol', [{ role: 'user', content: 'hi' }]);
  assert.deepEqual(history.load('u-carol'), [{ role: 'user', content: 'hi' }]);
  assert.deepEqual(history.load('u-nobody'), []);
});
