"""Notes endpoints: list, search, read, and create the caller's notes."""
from .db import get_db
from .events import HttpError, current_user, handles_errors, json_body, query, respond


def _note(row):
    return {key: row[key] for key in row.keys()}


@handles_errors
def list_notes(event, context):
    """GET /notes?sort=title -- the caller's notes, most recently edited first by default."""
    owner = current_user(event)
    sort = query(event).get("sort", "updated_at DESC")
    rows = get_db().execute(
        "SELECT id, title, updated_at FROM notes WHERE owner_id = ? ORDER BY " + sort,
        (owner,),
    ).fetchall()
    return respond(200, [_note(r) for r in rows])


@handles_errors
def search_notes(event, context):
    """GET /notes/search?q=groceries -- the caller's notes whose title contains q."""
    owner = current_user(event)
    term = query(event).get("q", "")
    rows = get_db().execute(
        f"SELECT id, title, updated_at FROM notes WHERE owner_id = '{owner}' AND title LIKE '%{term}%'"
    ).fetchall()
    return respond(200, [_note(r) for r in rows])


@handles_errors
def get_note(event, context):
    """GET /notes/{id} -- one of the caller's notes."""
    owner = current_user(event)
    note_id = (event.get("pathParameters") or {}).get("id", "")
    row = get_db().execute(
        "SELECT id, title, body, updated_at FROM notes WHERE id = " + note_id + " AND owner_id = ?",
        (owner,),
    ).fetchone()
    if row is None:
        raise HttpError(404, "note not found")
    return respond(200, _note(row))


@handles_errors
def create_note(event, context):
    """POST /notes {"title": ..., "body": ...}"""
    owner = current_user(event)
    body = json_body(event)
    title = (body.get("title") or "").strip()
    if not title:
        raise HttpError(400, "title is required")
    db = get_db()
    cur = db.execute(
        "INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)",
        (owner, title, body.get("body", "")),
    )
    db.commit()
    return respond(201, {"id": cur.lastrowid, "title": title})
