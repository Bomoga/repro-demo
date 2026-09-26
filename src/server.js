'use strict';

// The assistant service behind Notewise's editor. Run: npm install && npm start
const express = require('express');
const config = require('./config');
const { askAboutNotes } = require('./conversation');
const drive = require('./integrations/drive');

const app = express();
app.use(express.json());

// "Ask about my notes"
app.post('/assistant/ask', async (req, res) => {
  const userId = req.get('x-user');
  if (!userId) return res.status(401).json({ error: 'not signed in' });
  try {
    const notes = await fetch(`${config.notesApiUrl}/notes`, { headers: { 'x-user': userId } });
    res.json(await askAboutNotes(userId, req.body.question, await notes.json()));
  } catch (err) {
    res.status(502).json({ error: `assistant unavailable: ${err.message}` });
  }
});

// Live preview for inline calculations in the editor, e.g. "= 12 * 4.5".
app.get('/preview/formula', (req, res) => {
  res.send('<output>' + eval(req.query.expr) + '</output>');
});

// "Save to Google Drive" starts here.
app.get('/auth/google', (req, res) => {
  res.redirect(drive.consentUrl(req.query.state || ''));
});

// After signing in, send the user back to the page they came from.
app.get('/auth/done', (req, res) => {
  if (!req.query.next) return res.redirect('/');
  res.redirect(req.query.next);
});

if (require.main === module) {
  app.listen(config.port, () => console.log(`assistant service on http://localhost:${config.port}`));
}

module.exports = app;
