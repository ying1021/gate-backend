"""冒烟测试：注册、登录、角色归属与鉴权。只用标准库。

注意：每次运行都会在目标服务器上创建两个一次性账号和一个角色。
"""
import argparse
import json
import random
import string
import urllib.error
import urllib.request
from urllib.parse import urlencode

DEFAULT_BASE = "https://gate-backend-hq8w.onrender.com"


def call(base, method, path, token=None, body=None, timeout=90):
    url = base + path
    data = json.dumps(body).encode("utf-8") if body is not None else None
    req = urllib.request.Request(url, data=data, method=method)
    req.add_header("Content-Type", "application/json")
    if token:
        req.add_header("Authorization", "Bearer " + token)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            status = resp.status
            raw = resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        status = exc.code
        raw = exc.read().decode("utf-8", errors="replace")
    except (urllib.error.URLError, TimeoutError, ConnectionError, OSError) as exc:
        return 0, {"error": str(exc)}
    try:
        payload = json.loads(raw) if raw.strip() else {}
    except ValueError:
        payload = {"raw": raw[:500]}
    return status, payload


def rand_name():
    suffix = "".join(random.choices(string.ascii_lowercase + string.digits, k=8))
    return "smoke_" + suffix


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE)
    parser.add_argument("--timeout", type=int, default=90)
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

    def warm_up():
        for attempt in range(2):
            status, _ = call(base, "GET", "/", timeout=args.timeout)
            if status == 200:
                return True
            if attempt == 0:
                print("服务唤醒中，重试一次...")
        return False

    check("服务可访问", warm_up())

    password = "secret123"
    user_a = rand_name()
    status, data = call(base, "POST", "/auth/register", body={"username": user_a, "password": password}, timeout=args.timeout)
    check("注册 A", status == 200 and isinstance(data, dict) and "access_token" in data, f"status={status} data={data}")
    token_a = data.get("access_token", "") if isinstance(data, dict) else ""

    status, data = call(base, "GET", "/auth/me", token=token_a, timeout=args.timeout)
    username = data.get("username") if isinstance(data, dict) else None
    check("A 的 /auth/me", status == 200 and username == user_a, f"status={status}")

    status, data = call(base, "POST", "/player/new_life", token=token_a, timeout=args.timeout)
    state = data.get("玩家状态") if isinstance(data, dict) else None
    check(
        "A 创建角色",
        status == 200 and isinstance(state, dict) and bool(state.get("id")),
        f"status={status} data={data}",
    )
    player_a = state.get("id", "") if isinstance(state, dict) else ""

    status, data = call(base, "GET", "/player/list", token=token_a, timeout=args.timeout)
    players = data.get("players") if isinstance(data, dict) else None
    ids = [p.get("id") for p in players if isinstance(p, dict)] if isinstance(players, list) else []
    check("角色列表包含新角色", status == 200 and player_a in ids, f"status={status} ids={ids}")

    status, data = call(base, "GET", "/player/state" + "?" + urlencode({"player_id": player_a}), token=token_a, timeout=args.timeout)
    check(
        "读取角色状态",
        status == 200 and isinstance(data, dict)
        and (data.get("玩家状态") or {}).get("id") == player_a,
        f"status={status}",
    )

    status, data = call(
        base,
        "POST",
        "/game/explore?" + urlencode({"player_id": player_a, "map_region": "城郊青草地"}),
        token=token_a,
        timeout=args.timeout,
    )
    check("探索", status == 200 and data.get("探索地图") == "城郊青草地", f"status={status} data={data}")

    status, data = call(base, "GET", "/inventory/view?" + urlencode({"player_id": player_a}), token=token_a, timeout=args.timeout)
    check(
        "查看背包",
        status == 200 and "背包" in data and data.get("物品种类数", 0) >= 1,
        f"status={status} data={data}",
    )

    status, data = call(base, "GET", "/map/moves?" + urlencode({"player_id": player_a, "map_region": "城郊青草地"}), token=token_a, timeout=args.timeout)
    check(
        "查看可前往地图",
        status == 200 and data.get("当前地图") == "城郊青草地" and bool(data.get("可前往")),
        f"status={status} data={data}",
    )

    status, data = call(base, "GET", "/shop/info?" + urlencode({"map_region": "都市商业街"}), token=token_a, timeout=args.timeout)
    check("查看商店", status == 200 and data.get("有商店") is True, f"status={status} data={data}")

    status, data = call(base, "GET", "/settlement/view?" + urlencode({"player_id": player_a}), token=token_a, timeout=args.timeout)
    check("查看营地", status == 200 and "营地" in data, f"status={status} data={data}")

    user_b = rand_name()
    status, data = call(base, "POST", "/auth/register", body={"username": user_b, "password": password}, timeout=args.timeout)
    check("注册 B", status == 200 and isinstance(data, dict) and "access_token" in data, f"status={status}")
    token_b = data.get("access_token", "") if isinstance(data, dict) else ""

    status, data = call(base, "GET", "/player/state?" + urlencode({"player_id": player_a}), token=token_b, timeout=args.timeout)
    check("B 访问 A 的角色被拒绝", status == 403, f"status={status}")

    status, data = call(base, "GET", "/player/list", token=token_b, timeout=args.timeout)
    players = data.get("players") if isinstance(data, dict) else None
    ids_b = [p.get("id") for p in players if isinstance(p, dict)] if isinstance(players, list) else []
    check("B 的角色列表不含 A 的角色", status == 200 and player_a not in ids_b, f"status={status} ids={ids_b}")

    status, data = call(base, "GET", "/inventory/view?" + urlencode({"player_id": player_a}), token=token_b, timeout=args.timeout)
    check("B 访问 A 的背包被拒绝", status == 403, f"status={status}")

    status, data = call(base, "GET", "/player/list", timeout=args.timeout)
    check("无 token 被拒绝", status == 401, f"status={status}")

    status, data = call(base, "GET", "/player/list", token="not.a.jwt", timeout=args.timeout)
    check("伪造 token 被拒绝", status == 401, f"status={status}")

    status, data = call(base, "POST", "/auth/login", body={"username": user_a, "password": "wrongpass"}, timeout=args.timeout)
    check("错误密码被拒绝", status == 401, f"status={status}")

    status, data = call(base, "POST", "/auth/login", body={"username": user_a, "password": password}, timeout=args.timeout)
    check("正确密码登录", status == 200 and isinstance(data, dict) and "access_token" in data, f"status={status}")
    login_token = data.get("access_token", "") if isinstance(data, dict) else ""
    status, data = call(base, "GET", "/auth/me", token=login_token, timeout=args.timeout)
    check("登录令牌可用", status == 200 and data.get("username") == user_a, f"status={status}")

    status, data = call(base, "POST", "/auth/register", body={"username": user_a, "password": password}, timeout=args.timeout)
    check("重复用户名返回 409", status == 409, f"status={status}")

    print(f"本次账号：{user_a} / {user_b}")
    print(f"\n结果：{passed} 通过，{failed} 失败")
    raise SystemExit(1 if failed else 0)


if __name__ == "__main__":
    main()
