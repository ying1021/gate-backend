"""
数据库模块 - PostgreSQL 持久化
"""
import os
import json
import psycopg2
import psycopg2.extras
from urllib.parse import urlparse

DATABASE_URL = os.environ.get("DATABASE_URL", "")

if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL 环境变量未设置")


def get_connection():
    """获取数据库连接"""
    conn = psycopg2.connect(DATABASE_URL)
    return conn


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id TEXT PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id TEXT PRIMARY KEY,
            species TEXT NOT NULL,
            level INTEGER DEFAULT 1,
            talent TEXT,
            exp REAL DEFAULT 0,
            spec_points INTEGER DEFAULT 0,
            current_map TEXT,
            is_online INTEGER DEFAULT 1,
            inventory TEXT DEFAULT '{}',
            settlement TEXT DEFAULT '{}',
            plant_growth TEXT DEFAULT '{}',
            quests TEXT DEFAULT '{}',
            specializations TEXT DEFAULT '{}',
            debuffs TEXT DEFAULT '[]',
            instance_ticks INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        ALTER TABLE players
        ADD COLUMN IF NOT EXISTS user_id TEXT REFERENCES users(id)
    """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_players_user_id ON players(user_id)
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_vitals (
            player_id TEXT PRIMARY KEY,
            vitality REAL DEFAULT 100,
            stamina REAL DEFAULT 100,
            satiety REAL DEFAULT 100,
            sanity REAL DEFAULT 100,
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_injuries (
            player_id TEXT PRIMARY KEY,
            skin_laceration REAL DEFAULT 0,
            fracture REAL DEFAULT 0,
            blood_loss REAL DEFAULT 0,
            poison REAL DEFAULT 0,
            asphyxia REAL DEFAULT 0,
            frostbite REAL DEFAULT 0,
            burn REAL DEFAULT 0,
            sensory_damage REAL DEFAULT 0,
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS settlement_buildings (
            player_id TEXT,
            building_name TEXT,
            quantity INTEGER DEFAULT 1,
            PRIMARY KEY (player_id, building_name),
            FOREIGN KEY (player_id) REFERENCES players(id)
        )
    """)

    conn.commit()
    conn.close()
    print("[数据库] 初始化完成")


def save_player(player):
    """保存玩家数据到数据库"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO players (id, user_id, species, level, talent, exp, spec_points, current_map,
        is_online, inventory, settlement, plant_growth, quests, specializations, debuffs, instance_ticks, updated_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)
        ON CONFLICT (id) DO UPDATE SET
            user_id = COALESCE(EXCLUDED.user_id, players.user_id),
            species = EXCLUDED.species,
            level = EXCLUDED.level,
            talent = EXCLUDED.talent,
            exp = EXCLUDED.exp,
            spec_points = EXCLUDED.spec_points,
            current_map = EXCLUDED.current_map,
            is_online = EXCLUDED.is_online,
            inventory = EXCLUDED.inventory,
            settlement = EXCLUDED.settlement,
            plant_growth = EXCLUDED.plant_growth,
            quests = EXCLUDED.quests,
            specializations = EXCLUDED.specializations,
            debuffs = EXCLUDED.debuffs,
            instance_ticks = EXCLUDED.instance_ticks,
            updated_at = CURRENT_TIMESTAMP
    """, (
        player.id,
        getattr(player, 'user_id', None),
        str(player.species.value) if hasattr(player.species, 'value') else str(player.species),
        player.level,
        player.talent.value if player.talent and hasattr(player.talent, 'value') else str(player.talent) if player.talent else None,
        getattr(player, 'exp', 0),
        getattr(player, 'spec_points', 0),
        getattr(player, 'current_map', None),
        1 if player.is_online else 0,
        json.dumps(getattr(player, 'inventory', {}) or {}),
        json.dumps(getattr(player, 'settlement', {}) or {}),
        json.dumps(getattr(player, 'plant_growth', {}) or {}),
        json.dumps(getattr(player, 'quests', {}) or {}),
        json.dumps(getattr(player, 'specializations', {}) or {}),
        json.dumps(getattr(player, 'debuffs', []) or []),
        getattr(player, 'instance_ticks', 0),
    ))

    cursor.execute("""
        INSERT INTO player_vitals (player_id, vitality, stamina, satiety, sanity)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (player_id) DO UPDATE SET
            vitality = EXCLUDED.vitality,
            stamina = EXCLUDED.stamina,
            satiety = EXCLUDED.satiety,
            sanity = EXCLUDED.sanity
    """, (player.id, player.vital.vitality, player.vital.stamina, player.vital.satiety, player.vital.sanity))

    cursor.execute("""
        INSERT INTO player_injuries (player_id, skin_laceration, fracture, blood_loss, poison, asphyxia, frostbite, burn, sensory_damage)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (player_id) DO UPDATE SET
            skin_laceration = EXCLUDED.skin_laceration,
            fracture = EXCLUDED.fracture,
            blood_loss = EXCLUDED.blood_loss,
            poison = EXCLUDED.poison,
            asphyxia = EXCLUDED.asphyxia,
            frostbite = EXCLUDED.frostbite,
            burn = EXCLUDED.burn,
            sensory_damage = EXCLUDED.sensory_damage
    """, (
        player.id,
        player.injury.skin_laceration, player.injury.fracture, player.injury.blood_loss,
        player.injury.poison, player.injury.asphyxia, player.injury.frostbite,
        player.injury.burn, player.injury.sensory_damage,
    ))

    conn.commit()
    conn.close()
    return True


def load_player(player_id):
    """从数据库加载玩家"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute("SELECT * FROM players WHERE id = %s", (player_id,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return None

    cursor.execute("SELECT * FROM player_vitals WHERE player_id = %s", (player_id,))
    vital_row = cursor.fetchone()

    cursor.execute("SELECT * FROM player_injuries WHERE player_id = %s", (player_id,))
    injury_row = cursor.fetchone()

    conn.close()

    from app.models.player import Player, VitalStats, InjuryState
    from app.core.config import Species

    species_str = row["species"]
    species = None
    for s in Species:
        if s.value == species_str:
            species = s
            break
    if species is None:
        species = Species.HUMAN

    player = Player(
        id=row["id"],
        user_id=row["user_id"],
        species=species,
        level=row["level"],
        exp=row["exp"] or 0,
        spec_points=row["spec_points"] or 0,
        current_map=row["current_map"],
        is_online=bool(row["is_online"]),
        quests=json.loads(row["quests"] or "{}"),
        inventory=json.loads(row["inventory"] or "{}"),
        settlement=json.loads(row["settlement"] or "{}"),
        plant_growth=json.loads(row["plant_growth"] or "{}"),
        specializations=json.loads(row["specializations"] or "{}"),
        debuffs=json.loads(row["debuffs"] or "[]"),
        instance_ticks=row["instance_ticks"] or 0,
    )

    talent_str = row["talent"]
    if talent_str:
        from app.models.player import Talent
        for t in Talent:
            if t.value == talent_str:
                player.talent = t
                break

    if vital_row:
        player.vital.vitality = vital_row["vitality"]
        player.vital.stamina = vital_row["stamina"]
        player.vital.satiety = vital_row["satiety"]
        player.vital.sanity = vital_row["sanity"]

    if injury_row:
        player.injury.skin_laceration = injury_row["skin_laceration"]
        player.injury.fracture = injury_row["fracture"]
        player.injury.blood_loss = injury_row["blood_loss"]
        player.injury.poison = injury_row["poison"]
        player.injury.asphyxia = injury_row["asphyxia"]
        player.injury.frostbite = injury_row["frostbite"]
        player.injury.burn = injury_row["burn"]
        player.injury.sensory_damage = injury_row["sensory_damage"]

    return player


def save_settlement(player_id, buildings):
    """保存营地建筑"""
    conn = get_connection()
    cursor = conn.cursor()
    for name, qty in buildings.items():
        cursor.execute("""
            INSERT INTO settlement_buildings (player_id, building_name, quantity)
            VALUES (%s, %s, %s)
            ON CONFLICT (player_id, building_name) DO UPDATE SET quantity = EXCLUDED.quantity
        """, (player_id, name, qty))
    conn.commit()
    conn.close()


def load_settlement(player_id):
    """加载营地建筑"""
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT building_name, quantity FROM settlement_buildings WHERE player_id = %s", (player_id,))
    rows = cursor.fetchall()
    conn.close()
    return {row["building_name"]: row["quantity"] for row in rows} if rows else {}


async def save_death_record(player_id: str, species_name: str, level: int, killer_id: str = None):
    """保存死亡记录"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS death_records (
            id SERIAL PRIMARY KEY,
            player_id TEXT,
            species TEXT,
            level INTEGER,
            killer_id TEXT,
            death_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("""
        INSERT INTO death_records (player_id, species, level, killer_id)
        VALUES (%s, %s, %s, %s)
    """, (player_id, species_name, level, killer_id))
    conn.commit()
    conn.close()


async def delete_player_from_db(player_id: str):
    """删除玩家数据"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM player_vitals WHERE player_id = %s", (player_id,))
    cursor.execute("DELETE FROM player_injuries WHERE player_id = %s", (player_id,))
    cursor.execute("DELETE FROM settlement_buildings WHERE player_id = %s", (player_id,))
    cursor.execute("DELETE FROM players WHERE id = %s", (player_id,))
    conn.commit()
    conn.close()


def create_user(user_id, username, password_hash):
    """创建账号；用户名重复时返回 False"""
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (id, username, password_hash) VALUES (%s, %s, %s)",
            (user_id, username, password_hash),
        )
        conn.commit()
        return True
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        return False
    finally:
        conn.close()


def get_user_by_username(username):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        "SELECT id, username, password_hash FROM users WHERE username = %s",
        (username,),
    )
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_user_by_id(user_id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute("SELECT id, username FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_player_owner(player_id):
    """返回角色所属用户 ID；角色不存在时返回 None"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM players WHERE id = %s", (player_id,))
    row = cursor.fetchone()
    conn.close()
    return row[0] if row else None


def list_players_by_user(user_id):
    conn = get_connection()
    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    cursor.execute(
        """
        SELECT id, species, level, current_map, created_at, updated_at
        FROM players
        WHERE user_id = %s
        ORDER BY updated_at DESC
        """,
        (user_id,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "species": row["species"],
            "level": row["level"],
            "current_map": row["current_map"],
            "created_at": row["created_at"].isoformat() if row["created_at"] else None,
            "updated_at": row["updated_at"].isoformat() if row["updated_at"] else None,
        }
        for row in rows
    ]
