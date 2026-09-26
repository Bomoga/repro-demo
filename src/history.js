'use strict';

const fs = require('node:fs');
const path = require('node:path');

// Each user's assistant conversation, kept so follow-up questions have context.
function dataDir() {
  return process.env.NOTEWISE_DATA_DIR || path.join(__dirname, '..', 'data');
}

function historyFile(userId) {
  return path.join(dataDir(), 'history', `${userId}.json`);
}

function load(userId) {
  try {
    return JSON.parse(fs.readFileSync(historyFile(userId), 'utf8'));
  } catch {
    return [];
  }
}

function save(userId, messages) {
  fs.mkdirSync(path.dirname(historyFile(userId)), { recursive: true });
  fs.writeFileSync(historyFile(userId), JSON.stringify(messages));
}

module.exports = { load, save };
