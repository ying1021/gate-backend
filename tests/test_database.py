import asyncio
import os
import unittest
import uuid

TEST_DATABASE_URL = os.environ.get("TEST_DATABASE_URL", "")
HAS_DB = bool(TEST_DATABASE_URL) and "dummy" not in TEST_DATABASE_URL

if HAS_DB:
    os.environ["DATABASE_URL"] = TEST_DATABASE_URL
    import app.database as db


@unittest.skipUnless(HAS_DB, "需要真实的 TEST_DATABASE_URL")
class DatabaseTests(unittest.TestCase):
    def setUp(self):
        db.init_db()

    def _cleanup_user(self, user_id):
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
        conn.commit()
        conn.close()

    def test_user_roundtrip(self):
        username = "test_" + uuid.uuid4().hex[:10]
        user_id = uuid.uuid4().hex
        self.assertTrue(db.create_user(user_id, username, "hash"))
        self.addCleanup(self._cleanup_user, user_id)
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
        self.addCleanup(self._cleanup_user, user_id)

        player = Player(id=uuid.uuid4().hex[:8], species=Species.TIGER, user_id=user_id)
        db.save_player(player)
        self.addCleanup(lambda: asyncio.run(db.delete_player_from_db(player.id)))

        self.assertEqual(db.get_player_owner(player.id), user_id)
        listed = db.list_players_by_user(user_id)
        self.assertEqual(len(listed), 1)
        self.assertEqual(
            set(listed[0]),
            {"id", "species", "level", "current_map", "created_at", "updated_at"},
        )
        self.assertEqual(listed[0]["id"], player.id)

        loaded = db.load_player(player.id)
        self.assertEqual(loaded.user_id, user_id)

        player.user_id = None
        db.save_player(player)
        self.assertEqual(db.get_player_owner(player.id), user_id)


if __name__ == "__main__":
    unittest.main()
