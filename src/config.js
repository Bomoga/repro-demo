'use strict';

module.exports = {
  providerUrl: 'https://api.example-llm.test/v1/chat',
  // FAKE: a random value generated for this demo repo. It has never been a valid key anywhere.
  OPENAI_API_KEY: '8307c1cadcd80247d691da88b17169cdf7b8e641',
  model: 'demo-chat-1',
  notesApiUrl: process.env.NOTES_API_URL || 'http://localhost:8000',
  port: Number(process.env.PORT) || 3000,
};
