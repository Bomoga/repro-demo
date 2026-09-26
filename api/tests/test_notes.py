from api.notes import create_note, get_note, list_notes, search_notes
from api.tests.helpers import DbTestCase, event, payload


class ListNotesTest(DbTestCase):
    def test_lists_only_the_callers_notes(self):
        self.add_note("groceries")
        self.add_note("trip ideas")
        self.add_note("bob's diary", owner="u-bob")
        res = list_notes(event(), None)
        self.assertEqual(res["statusCode"], 200)
        self.assertEqual({n["title"] for n in payload(res)}, {"groceries", "trip ideas"})

    def test_accepts_a_sort_parameter(self):
        self.add_note("groceries")
        res = list_notes(event(query={"sort": "title"}), None)
        self.assertEqual(res["statusCode"], 200)
        self.assertEqual(len(payload(res)), 1)

    def test_requires_a_signed_in_user(self):
        self.assertEqual(list_notes(event(user=None), None)["statusCode"], 401)


class SearchNotesTest(DbTestCase):
    def test_matches_titles_containing_the_term(self):
        self.add_note("weekly groceries")
        self.add_note("trip ideas")
        self.add_note("groceries", owner="u-bob")
        res = search_notes(event(query={"q": "grocer"}), None)
        self.assertEqual([n["title"] for n in payload(res)], ["weekly groceries"])


class GetNoteTest(DbTestCase):
    def test_returns_the_callers_note(self):
        note_id = self.add_note("groceries", body="eggs")
        res = get_note(event(path={"id": str(note_id)}), None)
        self.assertEqual(payload(res)["body"], "eggs")

    def test_hides_other_users_notes(self):
        note_id = self.add_note("bob's diary", owner="u-bob")
        self.assertEqual(get_note(event(path={"id": str(note_id)}), None)["statusCode"], 404)


class CreateNoteTest(DbTestCase):
    def test_creates_a_note(self):
        res = create_note(event(body={"title": "  standup  ", "body": "notes"}), None)
        self.assertEqual(res["statusCode"], 201)
        self.assertEqual(payload(res)["title"], "standup")
        self.assertEqual({n["title"] for n in payload(list_notes(event(), None))}, {"standup"})

    def test_requires_a_title(self):
        self.assertEqual(create_note(event(body={"title": " "}), None)["statusCode"], 400)
