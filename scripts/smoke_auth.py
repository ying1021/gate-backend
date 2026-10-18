"""冒烟测试：注册、登录、角色归属与鉴权。只用标准库。"""
import argparse
import json
import random
import string
import urllib.error
import urllib.request
from urllib.parse import urlencode

DEFAULT_BASE = "https://gate-backend-hq8w.onrender.com"


def call(base, method, path, token=None, body=None):
    url = base + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=90) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8") or "{}")
    except urllib.error.HTTPError as exc:
        payload = exc.read().decode("utf-8")
        try:
            payload = json.loads(payload)
        except ValueError:
            pass
        return exc.code, payload


def rand_name():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return "smoke_" + suffix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    args = parser.parse_args()
    base = args.base_url.rstrip("/")

    passed = 0
    failed = 0

    def check(name, condition, extra=""):
        nonlocal passed, failed
        if condition:
            passed += 1
            print("PASS " + name)
        else:
            failed += 1
            print("FAIL " + name + " " + str(extra))

    password = "secret123"
    user_a = rand_name()
    status, data = call(base, "POST", "/auth/register", body={"username": user_a, "password": password})
    check("注册 A", status == 200 and isinstance(data, dict) and "access_token" in data, f"status={status} data={data}")
    token_a = data.get("access_token", "") if isinstance(data, dict) else ""

    status, data = call(base, "GET", "/auth/me", token=token_a)
    username = data.get("username") if isinstance(data, dict) else None
    check("A 的 /auth/me", status == 200 and username == user_a, f"status={status}")

    status, data = call(base, "POST", "/player/new_life", token=token_a)
    check("A 创建角色", status == 200 and "玩家状态" in data, f"status={status} data={data}")
    player_a = (data.get("玩家状态") or {}).get("id", "") if isinstance(data, dict) else ""

    status, data = call(base, "GET", "/player/list", token=token_a)
    ids = [p.get("id") for p in (data.get("players") or [])] if isinstance(data, dict) else []
    check("角色列表包含新角色", status == 200 and player_a in ids, f"status={status} ids={ids}")

    status, data = call(base, "GET", "/player/state" + "?" + urlencode({"player_id": player_a}), token=token_a)
    check("读取角色状态", status == 200 and "玩家状态" in data, f"status={status}")

    status, data = call(
        base,
        "POST",
        "/game/explore?" + urlencode({"player_id": player_a, "map_region": "城郊青草地"}),
        token=token_a,
    )
    check("探索", status == 200, f"status={status} data={data}")

    status, data = call(base, "GET", "/inventory/view?" + urlencode({"player_id": player_a}), token=token_a)
    check("查看背包", status == 200, f"status={status}")

    status, data = call(base, "GET", "/map/moves?" + urlencode({"player_id": player_a, "map_region": "城郊青草地"}), token=token_a)
    check("查看可前往地图", status == 200, f"status={status}")

    status, data = call(base, "GET", "/shop/info?" + urlencode({"map_region": "都市商业街"}), token=token_a)
    check("查看商店", status == 200, f"status={status}")

    status, data = call(base, "GET", "/settlement/view?" + urlencode({"player_id": player_a}), token=token_a)
    check("查看营地", status == 200, f"status={status}")

    user_b = rand_name()
    status, data = call(base, "POST", "/auth/register", body={"username": user_b, "password": password})
    check("注册 B", status == 200 and isinstance(data, dict) and "access_token" in data, f"status={status}")
    token_b = data.get("access_token", "") if isinstance(data, dict) else ""

    status, data = call(base, "GET", "/player/state?" + urlencode({"player_id": player_a}), token=token_b)
    check("B 访问 A 的角色被拒绝", status == 403, f"status={status}")

    status, data = call(base, "GET", "/player/list")
    check("无 token 被拒绝", status == 401, f"status={status}")

    status, data = call(base, "POST", "/auth/login", body={"username": user_a, "password": "wrongpass"})
    check("错误密码被拒绝", status == 401, f"status={status}")

    status, data = call(base, "POST", "/auth/login", body={"username": user_a, "password": password})
    check("正确密码登录", status == 200 and isinstance(data, dict) and "access_token" in data, f"status={status}")

    status, data = call(base, "POST", "/auth/register", body={"username": user_a, "password": password})
    check("重复用户名返回 409", status == 409, f"status={status}")

    print(f"\n结果：{passed} 通过，{failed} 失败")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
