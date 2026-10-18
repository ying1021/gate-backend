import os
import unittest

os.environ.setdefault("DATABASE_URL", "postgresql://dummy:dummy@localhost/dummy")

import app.main as main_module


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


if __name__ == "__main__":
    unittest.main()
