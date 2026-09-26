'use strict';

module.exports = {
  providerUrl: 'https://api.example-llm.test/v1/chat',
  OPENAI_API_KEY: process.env.OPENAI_API_KEY,
  model: 'demo-chat-1',
  notesApiUrl: process.env.NOTES_API_URL || 'http://localhost:8000',
  port: Number(process.env.PORT) || 3000,
};
