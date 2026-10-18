# 众生之门（Gate of All Living Beings）· 后端

基于 **FastAPI + PostgreSQL** 的 Web 文字冒险游戏后端，提供玩家属性、背包、战斗、商店、建造、地图、种植、秘境等模块的 REST 接口。

> A FastAPI + PostgreSQL backend for a browser-based text adventure game, exposing nearly 40 REST endpoints for player stats, inventory, combat, shops, building, maps, farming and instanced dungeons.

- 前端仓库：[ying1021/gate-of-life](https://github.com/ying1021/gate-of-life)
- 线上前端：[https://ying1021.github.io/gate-of-life/](https://ying1021.github.io/gate-of-life/)
- 接口文档：本地启动后访问 `http://127.0.0.1:8000/docs`（FastAPI 自动生成 Swagger）

## 技术栈

| 层次 | 技术 |
| --- | --- |
| 语言 | Python 3.10+ |
| Web 框架 | FastAPI + Uvicorn |
| 数据校验 | Pydantic |
| 数据库 | PostgreSQL（psycopg2） |
| 部署 | Render（后端）+ PostgreSQL + GitHub Pages（前端） |
| 版本控制 | Git / GitHub |

## 功能模块

| 模块 | 路由前缀 | 主要能力 |
| --- | --- | --- |
| 玩家 | `/player` | 创建角色、上线/离线、死亡与重生、红名、属性点分配 |
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
│   ├── core/config.py          # 物种、地形、建筑、道具等配置
│   ├── models/player.py        # 玩家与天赋数据模型
│   ├── routers/player.py       # 玩家路由
│   └── services/game_service.py# 核心游戏逻辑
├── Procfile                    # Render 启动命令
├── requirements.txt
└── README.md
```

数据库包含 5 张表：`players`、`player_vitals`、`player_injuries`、`settlement_buildings`、`death_records`。

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

## 部署

- **后端**：Render，启动命令见 `Procfile`：
  `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- **数据库**：PostgreSQL，连接串通过 `DATABASE_URL` 环境变量注入；
- **前端**：GitHub Pages，代码位于 [gate-of-life](https://github.com/ying1021/gate-of-life)；
- 前端通过 `fetch` 调用后端接口，接口基址配置在 [gate-of-life](https://github.com/ying1021/gate-of-life) 仓库的 `js/api.js` 中。

## 已知限制

- 当前版本使用 `player_id` 标识玩家，尚未实现 token 鉴权；生产环境应补充登录、会话与权限校验。
- 每次请求创建 PostgreSQL 连接，未接入连接池；并发量上升时需要引入连接池（如 `psycopg2.pool`）。
- Render 免费实例长时间无请求会休眠，首次访问存在冷启动延迟，前端已加入重试与提示。

## 开发说明

本项目在开发过程中使用 Claude Code / Cursor 等 AI 编程工具辅助生成与迭代代码；作者负责玩法规则梳理、代码走查、逻辑修改、前后端联调与功能测试。
