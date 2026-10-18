"""认证工具：密码哈希、JWT、输入校验与鉴权规则。"""
import os
import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
import jwt

JWT_SECRET = os.environ.get("JWT_SECRET") or secrets.token_hex(32)
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

if not os.environ.get("JWT_SECRET"):
    print("[警告] 未设置 JWT_SECRET，使用临时密钥，服务重启后所有登录会失效")

USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")

# 无需登录即可访问
PUBLIC_PATHS = frozenset({
    "/",
    "/docs",
    "/docs/oauth2-redirect",
    "/openapi.json",
    "/redoc",
    "/auth/register",
    "/auth/login",
})

# 需要登录，但不强制携带 player_id
NO_PLAYER_ID_PATHS = frozenset({
    "/auth/me",
    "/player/list",
    "/player/new_life",
    "/player/create",
    "/game/tick",
    "/game/kill",
    "/game/battle",
    "/game/kill_loot",
    "/shop/info",
})


def validate_credentials(username: str, password: str):
    """返回错误信息；合法时返回 None。"""
    if not USERNAME_RE.match(username or ""):
        return "用户名需为 3-20 位字母、数字或下划线"
    if not password:
        return "密码不能为空"
    length = len(password.encode("utf-8"))
    if length < 6 or length > 72:
        return "密码长度需为 6-72 字节"
    return None


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_token(user_id: str) -> str:
    now = datetime.now(timezone.utc)
    payload = {"sub": user_id, "iat": now, "exp": now + timedelta(days=JWT_EXPIRE_DAYS)}
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])


def authenticate_request(path, method, authorization, player_id, owner_lookup):
    """返回 (user_id, error)。

    error 为 None 表示放行；否则为 (status_code, detail)。
    公开路径返回 (None, None)。
    """
    if method == "OPTIONS" or path in PUBLIC_PATHS:
        return None, None

    if not authorization or not authorization.startswith("Bearer "):
        return None, (401, "未登录")

    try:
        payload = decode_token(authorization[7:].strip())
    except Exception:
        return None, (401, "登录已过期，请重新登录")

    user_id = payload.get("sub")
    if not user_id:
        return None, (401, "登录已过期，请重新登录")

    if path not in NO_PLAYER_ID_PATHS and not player_id:
        return None, (400, "缺少 player_id")

    if player_id and owner_lookup(player_id) != user_id:
        return None, (403, "无权访问该角色")

    return user_id, None
