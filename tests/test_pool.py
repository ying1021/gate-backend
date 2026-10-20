import os
import time
import unittest
from unittest.mock import MagicMock, patch

os.environ.setdefault("DATABASE_URL", "postgresql://dummy:dummy@localhost/dummy")

import app.database as db


class FakeCursor:
    def __init__(self):
        self.executed = []
        self.closed = False

    def execute(self, sql):
        self.executed.append(sql)

    def close(self):
        self.closed = True


class FakeConn:
    def __init__(self, closed=False, cursor_error=None):
        self.closed = closed
        self.cursor_error = cursor_error
        self.rollbacks = 0
        self.closed_real = False
        self.cursors = []

    def cursor(self):
        if self.cursor_error:
            raise self.cursor_error
        cursor = FakeCursor()
        self.cursors.append(cursor)
        return cursor

    def rollback(self):
        self.rollbacks += 1

    def close(self):
        self.closed_real = True


class FakePool:
    def __init__(self):
        self.returned = []

    def putconn(self, conn, close=False):
        self.returned.append((conn, close))


class PooledConnectionTests(unittest.TestCase):
    def test_close_returns_connection_to_pool(self):
        conn, pool = FakeConn(), FakePool()
        wrapped = db._PooledConnection(pool, conn)

        wrapped.close()

        self.assertEqual(pool.returned, [(conn, False)])
        self.assertEqual(conn.rollbacks, 1)
        self.assertFalse(conn.closed_real)

    def test_double_close_is_noop(self):
        conn, pool = FakeConn(), FakePool()
        wrapped = db._PooledConnection(pool, conn)

        wrapped.close()
        wrapped.close()

        self.assertEqual(len(pool.returned), 1)

    def test_closed_connection_is_discarded(self):
        conn, pool = FakeConn(closed=True), FakePool()
        db._PooledConnection(pool, conn).close()

        self.assertEqual(pool.returned, [(conn, True)])
        self.assertEqual(conn.rollbacks, 0)

    def test_unpooled_connection_is_closed_for_real(self):
        conn = FakeConn()
        db._PooledConnection(None, conn).close()

        self.assertTrue(conn.closed_real)

    def test_attributes_are_forwarded(self):
        conn = FakeConn()
        wrapped = db._PooledConnection(FakePool(), conn)

        cursor = wrapped.cursor()

        self.assertIs(cursor, conn.cursors[0])


class HealthCheckTests(unittest.TestCase):
    def setUp(self):
        db._last_used.clear()
        self.conn = FakeConn()

    def tearDown(self):
        db._last_used.clear()

    def test_closed_connection_is_unhealthy(self):
        self.assertFalse(db._is_healthy(FakeConn(closed=True)))

    def test_recently_used_connection_skips_ping(self):
        db._last_used[id(self.conn)] = time.monotonic()

        self.assertTrue(db._is_healthy(self.conn))
        self.assertEqual(self.conn.cursors, [])

    def test_idle_connection_is_pinged(self):
        db._last_used[id(self.conn)] = time.monotonic() - db._IDLE_CHECK_SECONDS - 1

        self.assertTrue(db._is_healthy(self.conn))
        self.assertEqual(len(self.conn.cursors), 1)
        self.assertEqual(self.conn.cursors[0].executed, ["SELECT 1"])
        self.assertTrue(self.conn.cursors[0].closed)
        self.assertEqual(self.conn.rollbacks, 1)

    def test_ping_failure_marks_unhealthy(self):
        db._last_used[id(self.conn)] = time.monotonic() - db._IDLE_CHECK_SECONDS - 1
        broken = FakeConn(cursor_error=RuntimeError("gone"))

        self.assertFalse(db._is_healthy(broken))


class OwnerCacheTests(unittest.TestCase):
    def setUp(self):
        db._owner_cache.clear()

    def tearDown(self):
        db._owner_cache.clear()

    def _fake_connection(self, owner):
        conn = MagicMock()
        conn.cursor.return_value.fetchone.return_value = (
            (owner,) if owner is not None else None
        )
        return conn

    def test_owner_lookup_is_cached(self):
        conn = self._fake_connection("u1")
        with patch.object(db, "get_connection", return_value=conn) as get_conn:
            self.assertEqual(db.get_player_owner("p1"), "u1")
            self.assertEqual(db.get_player_owner("p1"), "u1")
        self.assertEqual(get_conn.call_count, 1)

    def test_missing_owner_is_not_cached(self):
        conn = self._fake_connection(None)
        with patch.object(db, "get_connection", return_value=conn) as get_conn:
            self.assertIsNone(db.get_player_owner("p1"))
            self.assertIsNone(db.get_player_owner("p1"))
        self.assertEqual(get_conn.call_count, 2)

    def test_invalidate_forces_next_lookup(self):
        conn = self._fake_connection("u1")
        with patch.object(db, "get_connection", return_value=conn) as get_conn:
            db.get_player_owner("p1")
            db.invalidate_player_owner("p1")
            db.get_player_owner("p1")
        self.assertEqual(get_conn.call_count, 2)


if __name__ == "__main__":
    unittest.main()
