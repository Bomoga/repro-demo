from api.share import create_share, open_share
from api.tests.helpers import DbTestCase, event, payload


class ShareTest(DbTestCase):
    def test_a_share_link_opens_with_the_right_password(self):
        note_id = self.add_note("trip ideas", body="lisbon")
        url = payload(create_share(event(path={"id": str(note_id)}, body={"password": "correct horse"}), None))["url"]
        token = url.rsplit("/", 1)[1]
        res = open_share(event(user=None, path={"token": token}, body={"password": "correct horse"}), None)
        self.assertEqual(payload(res), {"title": "trip ideas", "body": "lisbon"})

    def test_a_wrong_password_is_refused(self):
        note_id = self.add_note("trip ideas")
        url = payload(create_share(event(path={"id": str(note_id)}, body={"password": "correct horse"}), None))["url"]
        res = open_share(event(user=None, path={"token": url.rsplit("/", 1)[1]}, body={"password": "wrong"}), None)
        self.assertEqual(res["statusCode"], 403)

    def test_short_passwords_are_rejected(self):
        note_id = self.add_note("trip ideas")
        self.assertEqual(create_share(event(path={"id": str(note_id)}, body={"password": "short"}), None)["statusCode"], 400)

    def test_only_the_owner_can_share(self):
        note_id = self.add_note("bob's diary", owner="u-bob")
        res = create_share(event(path={"id": str(note_id)}, body={"password": "correct horse"}), None)
        self.assertEqual(res["statusCode"], 404)
