'use strict';

const assistant = require('./assistant');
const history = require('./history');
const telemetry = require('./telemetry');

const MAX_TURNS = 10;

function buildPrompt(question, notes, past) {
  const context = notes.map((n) => `- ${n.title}`).join('\n');
  const turns = past
    .slice(-MAX_TURNS)
    .map((m) => `${m.role}: ${m.content}`)
    .join('\n');
  return `You answer questions about the user's notes.\nTheir notes:\n${context}\n\n${turns}\nuser: ${question}`;
}

// "Ask about my notes": answers a question with the user's notes and earlier turns as context.
async function askAboutNotes(userId, question, notes, fetchImpl) {
  const past = history.load(userId);
  const reply = await assistant.ask(buildPrompt(question, notes, past), fetchImpl);
  const answer = reply.text || '';
  history.save(userId, [...past, { role: 'user', content: question }, { role: 'assistant', content: answer }]);
  telemetry.trackQuestion(userId, question);
  return { answer };
}

module.exports = { askAboutNotes, buildPrompt };
