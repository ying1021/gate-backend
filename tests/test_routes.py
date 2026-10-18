import os
import unittest
from unittest.mock import patch

os.environ.setdefault("DATABASE_URL", "postgresql://dummy:dummy@localhost/dummy")

from fastapi.testclient import TestClient

import app.main as main_module
from app.auth import create_token


class RouteTests(unittest.TestCase):
    def test_auth_routes_registered(self):
        paths = {route.path for route in main_module.app.routes}
        for path in [
            "/",
            "/auth/register",
            "/auth/login",
            "/auth/me",
            "/player/list",
            "/player/state",
        ]:
            self.assertIn(path, paths)

    def test_cors_is_outermost(self):
        # 最后添加的中间件在最外层；CORS 必须排在最前，才能给 401/403 响应加跨域头
        first = main_module.app.user_middleware[0]
        self.assertEqual(first.cls.__name__, "CORSMiddleware")


class MiddlewareTests(unittest.TestCase):
    def setUp(self):
        # 不使用 with TestClient(...)，避免触发 startup 去连接数据库
        self.client = TestClient(main_module.app)

    def _auth_header(self, user_id: str) -> dict:
        return {"Authorization": f"Bearer {create_token(user_id)}"}

    def test_both_middlewares_installed(self):
        self.assertEqual(len(main_module.app.user_middleware), 2)

    def test_protected_routes_require_token(self):
        self.assertEqual(self.client.get("/player/list").status_code, 401)
        self.assertEqual(
            self.client.get("/player/state", params={"player_id": "x"}).status_code,
            401,
        )

    def test_public_root_needs_no_token(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)

    def test_cross_account_access_is_forbidden(self):
        with patch.object(main_module, "get_player_owner", return_value="u2"):
            response = self.client.get(
                "/player/state",
                params={"player_id": "abc"},
                headers=self._auth_header("u1"),
            )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(response.json()["detail"], "无权访问该角色")

    def test_valid_token_and_owner_pass_through(self):
        with patch.object(main_module, "get_player_owner", return_value="u1"), \
                patch.object(main_module, "list_players_by_user", return_value=[]):
            response = self.client.get(
                "/player/list",
                headers=self._auth_header("u1"),
            )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"players": []})

    def test_missing_player_id_returns_400(self):
        response = self.client.post(
            "/game/fairy_choice",
            headers=self._auth_header("u1"),
        )
        self.assertEqual(response.status_code, 400)


if __name__ == "__main__":
    unittest.main()
