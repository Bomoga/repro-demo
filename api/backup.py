"""Import a notes backup exported by Notewise 1.x.

1.x wrote backups with pickle, so that's the format this endpoint accepts.
"""
import base64
import pickle

from .db import get_db
from .events import HttpError, current_user, handles_errors, respond


@handles_errors
def import_backup(event, context):
    """POST /backups (body: a 1.x backup file, base64-encoded by API Gateway)"""
    owner = current_user(event)
    if not event.get("isBase64Encoded"):
        raise HttpError(400, "upload the backup file as binary")
    notes = pickle.loads(base64.b64decode(event["body"]))
    db = get_db()
    for note in notes:
        db.execute(
            "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
            (owner, note["title"], note.get("body", "")),
        )
    db.commit()
    return respond(201, {"imported": len(notes)})
