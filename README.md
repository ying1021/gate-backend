# 众生之门（Gate of All Living Beings）· 后端

基于 **FastAPI + PostgreSQL** 的 Web 文字冒险游戏后端，提供玩家属性、背包、战斗、商店、建造、地图、种植、秘境等模块的 REST 接口。

> A FastAPI + PostgreSQL backend for a browser-based text adventure game, exposing more than 40 REST endpoints for player stats, inventory, combat, shops, building, maps, farming and instanced dungeons.

- 前端仓库：[ying1021/gate-of-life](https://github.com/ying1021/gate-of-life)
- 线上前端：[https://ying1021.github.io/gate-of-life/](https://ying1021.github.io/gate-of-life/)
- 线上后端：[https://gate-backend-hq8w.onrender.com](https://gate-backend-hq8w.onrender.com)
- 接口文档：[https://gate-backend-hq8w.onrender.com/docs](https://gate-backend-hq8w.onrender.com/docs)（本地：`http://127.0.0.1:8000/docs`）

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI + Uvicorn |
| 数据校验 | Pydantic |
| 数据库 | PostgreSQL（psycopg2） |
| 认证 | bcrypt + JWT（HS256） |
| 部署 | Render（后端）+ PostgreSQL + GitHub Pages（前端） |
| 版本控制 | Git / GitHub |

## 功能模块

| 模块 | 路由前缀 | 主要能力 |
| --- | --- | --- |
| 玩家 | `/player` | 创建角色、上线/离线、死亡与重生、红名、专精点成长 |
| 背包 | `/inventory` | 道具增删、查看、使用 |
| 战斗与事件 | `/game` | 战斗结算、探索、钓鱼、随机事件、仙女问斧、击杀掉落 |
| 商店 | `/shop` | 按地图查询商店、购买道具 |
| 建造 | `/settlement` | 营地建造、拆除、查看 |
| 地图 | `/map` | 地图移动、可见区域、节点探索 |
| 摊位 | `/stall` | 开启/关闭营业 |
| 秘境 | `/instance` | 进入、Tick、退出 |
| 种植 | `/plant` | 生长 Tick、收获 |
| 城市规则 | `/city` | 城区行为校验与环境描述 |

## 项目结构

```text
.
├── app/
│   ├── main.py                 # 应用入口与 REST 路由
│   ├── database.py             # PostgreSQL 连接、建表与玩家读写
│   ├── auth.py                 # 密码哈希、JWT、鉴权规则
│   ├── core/config.py          # 物种、地形、建筑、道具等配置
│   ├── models/player.py        # 玩家与天赋数据模型
│   └── services/game_service.py # 核心游戏逻辑
├── Procfile                    # Render 启动命令
├── requirements.txt
├── scripts/smoke_auth.py       # 登录与鉴权冒烟测试
├── tests/                      # 单元测试与集成测试
└── README.md
```

数据库运行后共 6 张表：`users`、`players`、`player_vitals`、`player_injuries`、`settlement_buildings`、`death_records`（`death_records` 在首次写入死亡记录时创建）。`players.user_id` 外键关联 `users.id`，用于角色归属校验。

## 本地运行

1. 准备一个 PostgreSQL 数据库；
2. 安装依赖并设置 `DATABASE_URL`：

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate
# macOS / Linux
# source .venv/bin/activate

pip install -r requirements.txt

# Windows PowerShell
$env:DATABASE_URL="postgresql://user:password@localhost:5432/gate"
# macOS / Linux
# export DATABASE_URL="postgresql://user:password@localhost:5432/gate"

uvicorn app.main:app --reload
```

启动后访问：

- 接口文档：`http://127.0.0.1:8000/docs`
- 健康检查：`http://127.0.0.1:8000/`

> `DATABASE_URL` 未设置时，`app/database.py` 会直接抛出 `RuntimeError`，避免应用在无数据库的情况下启动。

## 测试

```bash
python -m unittest discover -s tests -v
python scripts/smoke_auth.py --base-url http://127.0.0.1:8000
```

> 未设置 `TEST_DATABASE_URL` 时数据库测试会自动跳过；冒烟脚本每次运行会在目标服务创建两个一次性账号和一个角色。

## 账号与登录

- `POST /auth/register`：注册，返回 JWT 与用户信息；
- `POST /auth/login`：登录，返回 JWT 与用户信息；
- `GET /auth/me`：当前用户；
- `POST /player/new_life`：创建角色（前端使用的新生命流程，自动归属当前账号）；
- `POST /player/create`：创建角色（兼容接口，随机物种与天赋，同样归属当前账号）；
- `GET /player/list`：当前账号的角色列表；
- `GET /player/state?player_id=`：读取角色状态。

除 `/`、`/docs`、`/docs/oauth2-redirect`、`/openapi.json`、`/redoc`、`/auth/register`、`/auth/login` 外，所有接口都需要
`Authorization: Bearer <token>`。带 `player_id` 的接口会校验角色是否属于当前账号。

token 使用 HS256 签名，有效期 7 天；过期后需重新登录，当前没有刷新 token 或服务端吊销机制。

未携带或 token 无效返回 401，需要 `player_id` 的接口缺少该参数时返回 400，访问他人角色返回 403。

本地开发可不设置 `JWT_SECRET`（会使用随机临时密钥，重启后需重新登录）；线上必须在环境变量中配置（建议 32 字节以上随机字符串），否则每次重启或部署后所有 token 都会失效。生成方式：

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 部署

- **后端**：Render，启动命令见 `Procfile`：
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **数据库**：PostgreSQL，连接串通过 `DATABASE_URL` 环境变量注入；
- **前端**：GitHub Pages，代码位于 [gate-of-life](https://github.com/ying1021/gate-of-life)；
- 前端通过 `fetch` 调用后端接口，接口基址配置在 [gate-of-life](https://github.com/ying1021/gate-of-life) 仓库的 `js/api.js` 中。

## 已知限制

- token 保存在浏览器 `localStorage`，存在 XSS 风险；当前未接入 httpOnly cookie。
- JWT 有效期 7 天，无刷新与吊销机制；退出登录仅清除本地 token，服务端在过期前仍会接受该 token。
- 没有找回密码、修改密码、邮箱验证、第三方登录、登录限流、失败锁定与多设备会话管理。
- 每次请求创建 PostgreSQL 连接，未接入连接池；并发量上升时需要引入连接池（如 `psycopg2.pool`）。
- Render 免费实例长时间无请求会休眠，首次访问存在冷启动延迟，前端已加入重试与提示。

## 开发说明

本项目在开发过程中使用 Claude Code / Cursor 等 AI 编程工具辅助生成与迭代代码；作者负责玩法规则梳理、代码走查、逻辑修改、前后端联调与功能测试。
