"""Import a notes backup exported by Notewise 1.x.

1.x wrote backups with pickle, so that's the format this endpoint accepts.
"""
import base64
import builtins
import io
import pickle

from .db import get_db
from .events import HttpError, current_user, handles_errors, respond

SAFE_BUILTINS = {
    "dict",
    "list",
    "set",
    "frozenset",
    "str",
    "int",
    "float",
    "bool",
    "bytes",
    "tuple",
}


class RestrictedUnpickler(pickle.Unpickler):
    def find_class(self, module, name):
        if module in ("builtins", "__builtin__") and name in SAFE_BUILTINS:
            return getattr(builtins, name)
        raise pickle.UnpicklingError(f"global '{module}.{name}' is forbidden")


@handles_errors
def import_backup(event, context):
    """POST /backups (body: a 1.x backup file, base64-encoded by API Gateway)"""
    owner = current_user(event)
    if not event.get("isBase64Encoded"):
        raise HttpError(400, "upload the backup file as binary")
    try:
        raw = base64.b64decode(event["body"])
        notes = RestrictedUnpickler(io.BytesIO(raw)).load()
    except Exception:
        raise HttpError(400, "invalid backup file")

    if not isinstance(notes, list):
        raise HttpError(400, "invalid backup file")

    db = get_db()
    for note in notes:
        if not isinstance(note, dict) or "title" not in note:
            raise HttpError(400, "invalid note format")
        db.execute(
            "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
            (owner, note["title"], note.get("body", "")),
        )
    db.commit()
    return respond(201, {"imported": len(notes)})
