"""Export a note as a document, converted with pandoc."""
import os
import subprocess
import tempfile

from .db import get_db
from .events import HttpError, current_user, handles_errors, query, respond

FORMATS = {"pdf", "docx", "html"}


@handles_errors
def export_note(event, context):
    """GET /notes/{id}/export?format=pdf"""
    owner = current_user(event)
    note_id = (event.get("pathParameters") or {}).get("id", "")
    fmt = query(event).get("format", "pdf")
    row = get_db().execute(
        "SELECT title, body FROM notes WHERE id = ? AND owner_id = ?", (note_id, owner)
    ).fetchone()
    if row is None:
        raise HttpError(404, "note not found")

    workdir = tempfile.mkdtemp(prefix="notewise-export-")
    source = os.path.join(workdir, "note.md")
    with open(source, "w") as fh:
        fh.write(row["body"])
    output = os.path.join(workdir, "note." + fmt)
    subprocess.run(
        f'pandoc {source} -o {output} --metadata title="{row["title"]}"',
        shell=True,
        check=True,
    )
    return respond(200, {"file": output, "format": fmt})
