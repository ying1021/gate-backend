import unittest

from app.auth import (
    authenticate_request,
    create_token,
    decode_token,
    hash_password,
    validate_credentials,
    verify_password,
)

PROTECTED = "/inventory/view"


class PasswordTests(unittest.TestCase):
    def test_hash_and_verify(self):
        hashed = hash_password("secret123")
        self.assertTrue(hashed.startswith("$2"))
        self.assertTrue(verify_password("secret123", hashed))
        self.assertFalse(verify_password("wrongpass", hashed))

    def test_verify_rejects_bad_hash(self):
        self.assertFalse(verify_password("secret123", "not-a-hash"))


class ValidationTests(unittest.TestCase):
    def test_valid_credentials(self):
        self.assertIsNone(validate_credentials("player_1", "secret123"))

    def test_username_too_short(self):
        self.assertIsNotNone(validate_credentials("ab", "secret123"))

    def test_username_bad_chars(self):
        self.assertIsNotNone(validate_credentials("玩家一号", "secret123"))

    def test_password_too_short(self):
        self.assertIsNotNone(validate_credentials("player1", "12345"))

    def test_password_too_long(self):
        self.assertIsNotNone(validate_credentials("player1", "a" * 73))

    def test_password_empty(self):
        self.assertEqual(validate_credentials("player1", ""), "密码不能为空")


class TokenTests(unittest.TestCase):
    def test_roundtrip(self):
        token = create_token("user-123")
        self.assertEqual(decode_token(token)["sub"], "user-123")

    def test_garbage_token_rejected(self):
        with self.assertRaises(Exception):
            decode_token("not-a-token")


class AuthRuleTests(unittest.TestCase):
    def owner(self, player_id):
        return {"p-own": "user-1"}.get(player_id)

    def test_public_path_allowed_without_token(self):
        user, error = authenticate_request("/", "GET", None, None, self.owner)
        self.assertIsNone(error)
        self.assertIsNone(user)

    def test_options_allowed(self):
        _, error = authenticate_request(PROTECTED, "OPTIONS", None, None, self.owner)
        self.assertIsNone(error)

    def test_missing_token(self):
        _, error = authenticate_request(PROTECTED, "GET", None, "p-own", self.owner)
        self.assertEqual(error, (401, "未登录"))

    def test_invalid_token(self):
        _, error = authenticate_request(PROTECTED, "GET", "Bearer bad", "p-own", self.owner)
        self.assertEqual(error, (401, "登录已过期，请重新登录"))

    def test_missing_player_id(self):
        token = create_token("user-1")
        _, error = authenticate_request(PROTECTED, "GET", "Bearer " + token, None, self.owner)
        self.assertEqual(error, (400, "缺少 player_id"))

    def test_other_users_player(self):
        token = create_token("user-2")
        _, error = authenticate_request(PROTECTED, "GET", "Bearer " + token, "p-own", self.owner)
        self.assertEqual(error, (403, "无权访问该角色"))

    def test_owner_allowed(self):
        token = create_token("user-1")
        user, error = authenticate_request(PROTECTED, "GET", "Bearer " + token, "p-own", self.owner)
        self.assertIsNone(error)
        self.assertEqual(user, "user-1")

    def test_no_player_id_path_allowed(self):
        token = create_token("user-1")
        user, error = authenticate_request("/player/list", "GET", "Bearer " + token, None, self.owner)
        self.assertIsNone(error)
        self.assertEqual(user, "user-1")

    def test_token_without_sub(self):
        from unittest.mock import patch
        with patch("app.auth.decode_token", return_value={}):
            _, error = authenticate_request(PROTECTED, "GET", "Bearer whatever", "p-own", self.owner)
        self.assertEqual(error, (401, "登录已过期，请重新登录"))


if __name__ == "__main__":
    unittest.main()
