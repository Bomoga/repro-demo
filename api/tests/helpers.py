import base64
import json
import unittest

from api import db


def event(user="u-alice", query=None, path=None, body=None, raw_body=None):
    """An API Gateway proxy event, as the Lambda handlers receive it."""
    evt = {
        "requestContext": {"authorizer": {"principalId": user}} if user else {},
        "queryStringParameters": query,
        "pathParameters": path,
        "body": json.dumps(body) if body is not None else None,
    }
    if raw_body is not None:
        evt["body"] = base64.b64encode(raw_body).decode()
        evt["isBase64Encoded"] = True
    return evt


def payload(response):
    return json.loads(response["body"])


class DbTestCase(unittest.TestCase):
    """Each test gets a fresh in-memory database."""

    def setUp(self):
        self.db = db.connect(":memory:")
        db.use(self.db)

    def tearDown(self):
        self.db.close()

    def add_note(self, title, owner="u-alice", body=""):
        cur = self.db.execute("INSERT INTO notes (owner_id, title, body) VALUES (?, ?, ?)", (owner, title, body))
        self.db.commit()
        return cur.lastrowid
