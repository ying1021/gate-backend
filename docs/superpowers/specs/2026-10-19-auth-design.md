# 众生之门 · 登录与鉴权功能设计

- 日期：2026-10-19
- 状态：待实现
- 仓库：`ying1021/gate-backend`
- 前端：`ying1021/gate-of-life`（GitHub Pages）
- 后端：FastAPI + PostgreSQL（Render）

## 1. 背景与目标

当前项目没有账号体系：前端通过 `player_id` 标识玩家，后端所有接口直接接受任意 `player_id`，任何人只要知道角色 ID 就能读写该角色。这既不符合真实应用的安全要求，也无法支撑简历中“身份认证、权限控制”的描述。

本次目标是加入一套最小但完整的账号系统：

1. 用户可注册、登录、退出；
2. 登录后只能看到并操作自己账号下的角色；
3. 现有游戏功能和数据结构不被破坏；
4. 代码结构和接口设计能支撑面试讲解。

## 2. 范围

### 本次包含

- 用户名 + 密码注册、登录；
- bcrypt 密码哈希；
- JWT 访问令牌（有效期 7 天）；
- 登录中间件统一鉴权；
- 角色归属校验（防 IDOR）；
- 当前账号的角色列表、角色状态读取；
- 前端登录页、注册页、角色选择页；
- 现有“新生命”逻辑绑定当前账号；
- 启动时幂等数据库迁移；
- 端到端冒烟测试脚本。

### 本次不包含

- 邮箱验证、找回密码、修改密码；
- 第三方登录（GitHub / Google）；
- 刷新 token、token 吊销列表；
- 限流、验证码、登录失败锁定；
- 多设备会话管理；
- 角色删除、角色转移。

以上均作为已知限制写入 README。

## 3. 关键决策

| 决策点 | 选择 | 理由 |
| --- | --- | --- |
| 登录范围 | 完整账号系统 | 注册 + 登录 + JWT + 角色归属，能支撑“身份认证、权限控制” |
| 登录界面 | HTML 覆盖层 | 手机键盘、密码遮蔽、输入法直接可用，改动小于 Canvas 自绘输入 |
| 账号与角色 | 先选角色再进入 | 登录后展示角色列表，手动选择“继续”或“新建” |
| 鉴权实现 | 中间件统一鉴权 | 38 个现有接口一次性覆盖，不易漏接口 |
| token 存储 | localStorage | 前后端跨域，避免 cookie 的 SameSite/credentials 复杂度；XSS 风险在 README 中说明 |
| 密码哈希 | bcrypt | 成熟、自带盐、Python 生态常用 |
| token 格式 | JWT HS256 | 无状态、实现简单、便于讲解 |

## 4. 架构

```
GitHub Pages (前端)                Render (后端)                PostgreSQL
┌──────────────────┐   HTTPS    ┌──────────────────┐        ┌──────────┐
│ HTML 登录/注册    │ ─────────> │ FastAPI           │ ─────> │ users    │
│ HTML 角色选择     │  Bearer     │  ├─ /auth/*       │        │ players  │
│ Canvas 游戏       │  JWT        │  ├─ 鉴权中间件     │        │ ...      │
└──────────────────┘             │  └─ 现有游戏接口   │        └──────────┘
                                 └──────────────────┘
```

### 后端模块划分

| 文件 | 职责 |
| --- | --- |
| `app/auth.py` | 密码哈希/校验、JWT 签发/解析、输入校验 |
| `app/database.py` | users 表、players 表迁移、用户与角色查询 |
| `app/main.py` | 注册/登录/我的信息、角色列表/状态接口、鉴权中间件 |
| `app/models/player.py` | Player 增加可选 `user_id` 字段 |
| `app/services/game_service.py` | `create_new_life` 接收并保存 `user_id` |

## 5. 数据模型

### 5.1 users

```sql
CREATE TABLE IF NOT EXISTS users (
    id            TEXT PRIMARY KEY,
    username      TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

- `id`：`uuid.uuid4().hex`；
- `username`：3–20 位，仅允许字母、数字、下划线；
- `password_hash`：bcrypt 哈希，永不通过接口返回。

### 5.2 players 迁移

```sql
ALTER TABLE players ADD COLUMN IF NOT EXISTS user_id TEXT REFERENCES users(id);
CREATE INDEX IF NOT EXISTS idx_players_user_id ON players(user_id);
```

- 迁移在 `init_db()` 中执行，可重复运行；执行顺序为：建 `users` 表 → `ALTER TABLE players` → 建索引；
- 现有玩家 `user_id` 为 `NULL`，保留不动，不会出现在任何账号的角色列表；
- `save_player` 的 INSERT 增加 `user_id` 列；`ON CONFLICT` 时使用
  `user_id = COALESCE(EXCLUDED.user_id, players.user_id)`，避免更新角色时清空归属。

### 5.3 Player 模型

增加可选字段：

```python
user_id: Optional[str] = None
```

`load_player` 读取 `row["user_id"]` 并写入模型；`save_player` 写入该字段。

## 6. 接口设计

### 6.1 公开接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/` | 健康检查 |
| GET | `/docs` | Swagger UI |
| GET | `/openapi.json` | OpenAPI 描述 |
| GET | `/redoc` | ReDoc |
| POST | `/auth/register` | 注册 |
| POST | `/auth/login` | 登录 |

### 6.2 需要登录的接口

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| GET | `/auth/me` | 返回当前用户 |
| GET | `/player/list` | 当前账号的角色列表 |
| GET | `/player/state?player_id=` | 角色完整状态（归属校验） |
| POST | `/player/new_life` | 为当前账号创建角色 |
| POST | `/player/create` | 保留旧接口，绑定当前账号 |
| 其他现有接口 | 见 `main.py` | 中间件统一鉴权 |

#### 注册

```http
POST /auth/register
Content-Type: application/json

{"username": "player1", "password": "secret123"}
```

成功（200）：

```json
{
  "access_token": "<jwt>",
  "token_type": "bearer",
  "user": {"id": "<uuid>", "username": "player1"}
}
```

失败：

- 400：用户名或密码格式不合法；
- 409：用户名已存在。

#### 登录

```http
POST /auth/login
Content-Type: application/json

{"username": "player1", "password": "secret123"}
```

成功返回结构同注册；失败统一返回 401 `{"detail": "用户名或密码错误"}`。

#### 当前用户

```http
GET /auth/me
Authorization: Bearer <jwt>
```

```json
{"id": "<uuid>", "username": "player1"}
```

#### 角色列表

```http
GET /player/list
Authorization: Bearer <jwt>
```

```json
{
  "players": [
    {
      "id": "abcd1234",
      "species": "虎",
      "level": 1,
      "current_map": "城郊青草地",
      "created_at": "2026-10-19T12:00:00",
      "updated_at": "2026-10-19T12:30:00"
    }
  ]
}
```

按 `updated_at DESC` 排序。

#### 角色状态

```http
GET /player/state?player_id=abcd1234
Authorization: Bearer <jwt>
```

```json
{"玩家状态": { "...": "与 /player/new_life 返回中的 玩家状态 同构" }}
```

即 `player.model_dump(by_alias=True)` 的完整结果。

### 6.3 路由签名调整

中间件解析出用户后写入 `request.state.user_id`。需要读取当前用户的接口显式声明 `request: Request`：

```python
@app.post("/player/new_life")
async def new_life(request: Request):
    result = create_new_life(user_id=request.state.user_id)
    return result
```

- `/player/new_life`：把 `user_id` 传给 `create_new_life`；
- `/player/create`：创建 `Player` 时设置 `player.user_id = request.state.user_id`；
- 其他路由签名不变。

`create_new_life` 增加参数：

```python
def create_new_life(user_id: str | None = None) -> dict:
    ...
    player = Player(id=str(uuid.uuid4())[:8], species=new_species, level=1, user_id=user_id)
```

## 7. 中间件鉴权规则

请求进入后按以下顺序处理：

1. `OPTIONS` 预检直接放行；
2. 路径在公开集合中直接放行；
3. 读取 `Authorization: Bearer <token>`，缺失或无效返回 401；
4. 解析 JWT，取得 `sub`（用户 ID）；
5. 若查询参数含 `player_id`：
   - 查询 `players.user_id` 是否等于当前用户；
   - 不存在或不属于当前用户，返回 403；
6. 不在下方列表中的路径必须携带 `player_id`，否则返回 400；
7. 放行到具体路由。

### 无需 player_id 的路径

- `/auth/me`
- `/player/list`
- `/player/new_life`
- `/player/create`
- `/game/tick`
- `/game/kill`
- `/game/battle`
- `/game/kill_loot`
- `/shop/info`

说明：该列表只表示“不强制要求 `player_id`”。如果请求仍携带了 `player_id`，第 5 条的归属校验照常执行（例如 `/game/tick?player_id=<他人的角色>` 返回 403）。

`/game/tick`、`/game/kill`、`/game/battle`、`/game/kill_loot`、`/shop/info` 为纯计算或只读接口，不读写玩家存档；其中 `/game/tick` 与 `/game/kill` 虽有 `player_id` 参数，但只用于构造临时对象。

其余游戏接口（`/inventory/*`、`/settlement/*`、`/map/*`、`/shop/buy`、`/stall/*`、`/city/*`、`/instance/*`、`/plant/*`、`/player/online|offline|death|suicide|death_cooldown|red_name|state` 等）均要求携带 `player_id`。

### 错误响应

| 状态码 | 场景 | detail |
| --- | --- | --- |
| 401 | 缺少 token | 未登录 |
| 401 | token 无效或过期 | 登录已过期，请重新登录 |
| 403 | 角色不属于当前账号 | 无权访问该角色 |
| 400 | 缺少 player_id | 缺少 player_id |
| 409 | 注册用户名重复 | 用户名已存在 |
| 422 | 请求体字段缺失 | FastAPI 默认校验信息 |

## 8. 前端流程

### 8.1 页面结构

在现有 `index.html` 中新增两个覆盖层：

```html
<div id="authOverlay">   <!-- 登录 / 注册 -->
<div id="charOverlay">   <!-- 角色选择 -->
<canvas id="gameCanvas">
```

- 未登录时显示 `authOverlay`，Canvas 隐藏；
- 登录后显示 `charOverlay`；
- 选择角色后隐藏覆盖层，显示 Canvas，进入现有游戏循环。

### 8.2 登录 / 注册

- 表单字段：用户名、密码；注册模式增加确认密码；
- 登录 / 注册通过页签或按钮切换；
- 成功后把 token 写入 `localStorage`，键名 `authToken`；
- 失败在表单下方显示服务器返回的 `detail`；
- 注册成功后直接登录，不要求再输入一次密码。

### 8.3 角色选择

- 进入页面时调用 `GET /player/list`；
- 每个角色卡片显示：物种、等级、当前地图、最后更新时间；
- 点击卡片：调用 `GET /player/state`，成功后进入游戏；
- “新建角色”：调用 `POST /player/new_life`，刷新列表并直接进入新角色；
- “退出登录”：清除 `authToken`，回到登录页；
- 列表为空时显示空状态和“新建角色”按钮。

### 8.4 游戏内变化

- `api.js` 的 `request()` 自动附加 `Authorization: Bearer <token>`；
- 任意接口返回 401：清除 token，显示登录页并提示“登录已过期”；
- 死亡流程由“回到旧的 login 画布”改为“显示角色选择层并刷新列表”；
- 旧 Canvas 登录按钮（新生命/继续）不再可达，保留代码不删除；
- `localStorage.playerData` 不再作为存档依据，角色状态以服务器为准；
- 退出游戏（`beforeunload`）仍然调用 `/player/offline`。

### 8.5 新增前端文件

- `js/auth.js`：登录、注册、token 管理、角色列表、角色选择、退出登录；
- `index.html`：覆盖层 HTML 与 CSS；
- `js/api.js`：新增 `register`、`login`、`me`、`playerList`、`playerState`，统一加鉴权头与 401 处理。

## 9. 安全设计

- 密码使用 `bcrypt.hashpw`，默认 cost；接口只返回 token 和用户名；
- 登录失败统一提示，避免用户名枚举；
- JWT：HS256，`sub` 为用户 ID，`iat` 签发时间，`exp` 7 天；
- `JWT_SECRET` 从环境变量读取；本地未设置时生成随机密钥并打印警告（重启后 token 失效）；Render 上必须配置固定值；
- 用户输入校验：
  - 用户名：3–20 位，`^[A-Za-z0-9_]+$`；
  - 密码：6–72 字节（bcrypt 72 字节上限）；
- 所有带 `player_id` 的请求校验归属，防止越权访问；
- SQL 全部使用参数化查询；
- 已知限制：token 存 localStorage 存在 XSS 风险；无限流、无找回密码、无邮箱验证。这些写入 README。

## 10. 迁移与兼容

- `init_db()` 启动时执行建表和加列，幂等；
- 现有玩家保留，`user_id` 为空；
- 现有前端如果未登录，所有接口返回 401，属于预期行为；
- 现有 `localStorage` 中的旧角色数据不再读取，但不删除；
- `/player/create` 保留，行为改为绑定当前登录账号。

## 11. 验证计划

### 11.1 自动化冒烟测试

新增 `scripts/smoke_auth.py`，仅使用标准库 `urllib`，默认指向线上地址，可传 `--base-url`：

1. 注册账号 A（随机用户名）；
2. 用 A 的 token 调用 `/auth/me`；
3. A 调用 `/player/new_life`，拿到角色 ID；
4. A 调用 `/player/list`，确认包含该角色；
5. A 调用 `/player/state`、`/game/explore`、`/inventory/view`；
6. 注册账号 B；
7. B 调用 `/player/state?player_id=<A 的角色>`，断言 403；
8. 不带 token 调用 `/player/list`，断言 401；
9. 错误密码登录，断言 401；
10. 输出 PASS/FAIL 汇总。

### 11.2 浏览器手动验证

1. 打开前端，注册新账号；
2. 角色列表为空，点击“新建角色”；
3. 进入游戏，执行探索、背包、战斗；
4. 退出登录，重新登录，角色仍在；
5. 再注册一个账号，确认看不到前一个账号的角色；
6. 死亡后回到角色列表；
7. 刷新页面，token 有效时直接进入角色列表。

### 11.3 回归验证

- 现有 38 个业务接口在带 token 的情况下仍返回 200；
- `/docs` 可正常打开；
- CORS 预检正常。

## 12. 部署

- `requirements.txt` 增加：

```text
bcrypt
PyJWT
```

- Render 环境变量增加 `JWT_SECRET`（随机 32 位以上字符串）；
- 重新部署后，启动日志应出现 `[数据库] 初始化完成`；
- 前端 GitHub Pages 无需构建，推送后刷新即可；
- README 增加登录说明、账号接口、`JWT_SECRET` 配置和已知限制。

## 13. 风险与后续

| 风险 | 处理 |
| --- | --- |
| localStorage token 被 XSS 窃取 | 游戏文本通过 Canvas 渲染，不使用 innerHTML；README 说明；后续可换 httpOnly cookie |
| JWT_SECRET 未配置导致重启后全员掉线 | 部署文档明确要求配置 |
| 免费 Render 冷启动 | 前端已有唤醒提示；README 说明 |
| 旧玩家无归属 | 保留数据，不迁移、不删除 |
| 无速率限制 | 作为已知限制，后续可加 slowapi |

后续可扩展：修改密码、刷新 token、角色删除、账号注销、登录日志。
