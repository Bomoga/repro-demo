"""Notes endpoints: list, search, read, and create the caller's notes."""
from .db import get_db
from .events import HttpError, current_user, handles_errors, json_body, query, respond

ALLOWED_SORTS = {
    "updated_at": "updated_at",
    "updated_at asc": "updated_at ASC",
    "updated_at desc": "updated_at DESC",
    "-updated_at": "updated_at DESC",
    "+updated_at": "updated_at ASC",
    "title": "title",
    "title asc": "title ASC",
    "title desc": "title DESC",
    "-title": "title DESC",
    "+title": "title ASC",
    "id": "id",
    "id asc": "id ASC",
    "id desc": "id DESC",
    "-id": "id DESC",
    "+id": "id ASC",
    "body": "body",
    "body asc": "body ASC",
    "body desc": "body DESC",
    "-body": "body DESC",
    "+body": "body ASC",
}

SORT_QUERIES = {
    sort_key: f"SELECT id, title, updated_at FROM notes WHERE owner_id = ? ORDER BY {clause}"
    for sort_key, clause in ALLOWED_SORTS.items()
}


def _note(row):
    return {key: row[key] for key in row.keys()}


@handles_errors
def list_notes(event, context):
    """GET /notes?sort=title -- the caller's notes, most recently edited first by default."""
    owner = current_user(event)
    sort = str(query(event).get("sort") or "updated_at desc")
    normalized = " ".join(sort.strip().lower().split())
    sql = SORT_QUERIES.get(normalized)
    if not sql:
        raise HttpError(400, "invalid sort parameter")
    rows = get_db().execute(sql, (owner,)).fetchall()
    return respond(200, [_note(r) for r in rows])


@handles_errors
def search_notes(event, context):
    """GET /notes/search?q=groceries -- the caller's notes whose title contains q."""
    owner = current_user(event)
    term = query(event).get("q") or ""
    rows = get_db().execute(
        "SELECT id, title, updated_at FROM notes WHERE owner_id = ? AND title LIKE ?",
        (owner, f"%{term}%"),
    ).fetchall()
    return respond(200, [_note(r) for r in rows])


@handles_errors
def get_note(event, context):
    """GET /notes/{id} -- one of the caller's notes."""
    owner = current_user(event)
    note_id = (event.get("pathParameters") or {}).get("id", "")
    row = get_db().execute(
        "SELECT id, title, body, updated_at FROM notes WHERE id = ? AND owner_id = ?",
        (note_id, owner),
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
