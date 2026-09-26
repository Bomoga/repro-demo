'use strict';

// "Save to Google Drive": exports a note as a document in the user's Drive.
const GOOGLE_OAUTH = {
  clientId: 'notewise-demo.apps.googleusercontent.example',
  redirectUri: 'http://localhost:3000/auth/google/callback',
  scopes: ['https://www.googleapis.com/auth/drive'],
};

function consentUrl(state) {
  const params = new URLSearchParams({
    client_id: GOOGLE_OAUTH.clientId,
    redirect_uri: GOOGLE_OAUTH.redirectUri,
    response_type: 'code',
    access_type: 'offline',
    scope: GOOGLE_OAUTH.scopes.join(' '),
    state,
  });
  return `https://accounts.google.com/o/oauth2/v2/auth?${params}`;
}

module.exports = { GOOGLE_OAUTH, consentUrl };
