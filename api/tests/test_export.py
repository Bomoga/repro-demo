from unittest import mock

from api.export import export_note
from api.tests.helpers import DbTestCase, event, payload


class ExportNoteTest(DbTestCase):
    @mock.patch("api.export.subprocess.run")
    def test_converts_the_note_with_pandoc(self, run):
        note_id = self.add_note("standup", body="# notes")
        res = export_note(event(path={"id": str(note_id)}, query={"format": "docx"}), None)
        self.assertEqual(res["statusCode"], 200)
        self.assertTrue(payload(res)["file"].endswith("note.docx"))
        self.assertIn("pandoc", run.call_args.args[0])

    @mock.patch("api.export.subprocess.run")
    def test_hides_other_users_notes(self, run):
        note_id = self.add_note("bob's diary", owner="u-bob")
        self.assertEqual(export_note(event(path={"id": str(note_id)}), None)["statusCode"], 404)
        run.assert_not_called()
