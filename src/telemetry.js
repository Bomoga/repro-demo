'use strict';

// Product analytics: which assistant features get used.
async function trackQuestion(userId, question) {
  try {
    await fetch('https://events.notewise-insights.example/v1/track', {
      method: 'POST',
      headers: { 'content-type': 'application/json' },
      body: JSON.stringify({ event: 'assistant_question', userId }),
    });
  } catch {
    // Analytics must never break the app.
  }
}

module.exports = { trackQuestion };
