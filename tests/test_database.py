import asyncio
import os
import unittest
import uuid

DATABASE_URL = os.environ.get("DATABASE_URL", "")
HAS_DB = bool(DATABASE_URL) and "dummy" not in DATABASE_URL

if HAS_DB:
    import app.database as db


@unittest.skipUnless(HAS_DB, "需要真实的 DATABASE_URL")
class DatabaseTests(unittest.TestCase):
    def setUp(self):
        db.init_db()

    def test_user_roundtrip(self):
        username = "test_" + uuid.uuid4().hex[:10]
        user_id = uuid.uuid4().hex
        self.assertTrue(db.create_user(user_id, username, "hash"))
        self.assertFalse(db.create_user(uuid.uuid4().hex, username, "hash"))
        user = db.get_user_by_username(username)
        self.assertEqual(user["id"], user_id)
        self.assertEqual(db.get_user_by_id(user_id)["username"], username)

    def test_player_owner_and_list(self):
        from app.core.config import Species
        from app.models.player import Player

        username = "test_" + uuid.uuid4().hex[:10]
        user_id = uuid.uuid4().hex
        db.create_user(user_id, username, "hash")

        player = Player(id=uuid.uuid4().hex[:8], species=Species.TIGER, user_id=user_id)
        db.save_player(player)

        self.assertEqual(db.get_player_owner(player.id), user_id)
        listed = db.list_players_by_user(user_id)
        self.assertTrue(any(item["id"] == player.id for item in listed))

        player.user_id = None
        db.save_player(player)
        self.assertEqual(db.get_player_owner(player.id), user_id)

        asyncio.run(db.delete_player_from_db(player.id))


if __name__ == "__main__":
    unittest.main()
