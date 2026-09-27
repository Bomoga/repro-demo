"""Password-protected share links for a single note."""
import hashlib
import hmac
import os

from .db import get_db
from .events import HttpError, current_user, handles_errors, json_body, respond

# Signs share-link tokens.
SHARE_SIGNING_SECRET = os.environ.get("SHARE_SIGNING_SECRET", "")


def _token(note_id):
    secret = os.environ.get("SHARE_SIGNING_SECRET") or SHARE_SIGNING_SECRET
    return hmac.new(secret.encode(), str(note_id).encode(), hashlib.sha256).hexdigest()[:24]


def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()


@handles_errors
def create_share(event, context):
    """POST /notes/{id}/share {"password": ...} -> a link anyone with the password can open"""
    owner = current_user(event)
    note_id = (event.get("pathParameters") or {}).get("id", "")
    password = json_body(event).get("password") or ""
    if len(password) < 8:
        raise HttpError(400, "password must be at least 8 characters")
    db = get_db()
    if db.execute("SELECT 1 FROM notes WHERE id = ? AND owner_id = ?", (note_id, owner)).fetchone() is None:
        raise HttpError(404, "note not found")
    token = _token(note_id)
    db.execute(
        "INSERT OR REPLACE INTO shares (token, note_id, password_hash) VALUES (?, ?, ?)",
        (token, note_id, hash_password(password)),
    )
    db.commit()
    return respond(201, {"url": f"/shared/{token}"})


@handles_errors
def open_share(event, context):
    """POST /shared/{token} {"password": ...} -> the shared note"""
    token = (event.get("pathParameters") or {}).get("token", "")
    password = json_body(event).get("password") or ""
    db = get_db()
    share = db.execute("SELECT note_id, password_hash FROM shares WHERE token = ?", (token,)).fetchone()
    if share is None or not hmac.compare_digest(share["password_hash"], hash_password(password)):
        raise HttpError(403, "wrong link or password")
    note = db.execute("SELECT title, body FROM notes WHERE id = ?", (share["note_id"],)).fetchone()
    return respond(200, {"title": note["title"], "body": note["body"]})
