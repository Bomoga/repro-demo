import pickle

from api.backup import import_backup
from api.notes import list_notes
from api.tests.helpers import DbTestCase, event, payload


class ImportBackupTest(DbTestCase):
    def test_imports_a_1x_backup(self):
        backup = pickle.dumps([{"title": "groceries", "body": "eggs"}, {"title": "trip ideas"}])
        res = import_backup(event(raw_body=backup), None)
        self.assertEqual(res["statusCode"], 201)
        self.assertEqual(payload(res), {"imported": 2})
        self.assertEqual({n["title"] for n in payload(list_notes(event(), None))}, {"groceries", "trip ideas"})

    def test_rejects_a_non_binary_upload(self):
        self.assertEqual(import_backup(event(body={"notes": []}), None)["statusCode"], 400)
