"""
数据库模块 - SQLite 持久化
"""
import sqlite3
import os
import json

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "gate_of_all_living.db")

from sqlite3 import connect
from threading import Lock

_conn_pool = None
_conn_lock = Lock()

def get_connection():
    global _conn_pool
    if _conn_pool is None:
        os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
        _conn_pool = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn_pool.row_factory = sqlite3.Row
    return _conn_pool


def init_db():
    """初始化数据库表"""
    conn = get_connection()
    cursor = conn.cursor()

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
        CREATE TABLE IF NOT EXISTS trade_listings (
            id TEXT PRIMARY KEY,
            seller_id TEXT,
            seller_species TEXT,
            offer_item TEXT,
            offer_qty INTEGER,
            want_item TEXT,
            want_qty INTEGER,
            status TEXT DEFAULT 'active',
            buyer_id TEXT,
            buyer_species TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
    print("[数据库] 初始化完成")


def save_player(player):
    """保存玩家数据到数据库"""
    from app.models.player import Player as P
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR REPLACE INTO players (id, species, level, talent, exp, spec_points, current_map, 
        is_online, inventory, settlement, plant_growth, quests, specializations, debuffs, instance_ticks, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
    """, (
        player.id,
        str(player.species.value) if hasattr(player.species, 'value') else str(player.species),
        player.level,
        player.talent.value if player.talent and hasattr(player.talent, 'value') else str(
            player.talent) if player.talent else None,
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


def load_player(player_id):
    """从数据库加载玩家"""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM players WHERE id = ?", (player_id,))
    row = cursor.fetchone()
    if not row:
        return None

    cursor.execute("SELECT * FROM player_vitals WHERE player_id = ?", (player_id,))
    vital_row = cursor.fetchone()

    cursor.execute("SELECT * FROM player_injuries WHERE player_id = ?", (player_id,))
    injury_row = cursor.fetchone()


    from app.models.player import Player, VitalStats, InjuryState
    from app.core.config import Species

    species_str = row["species"]
    species = None
    for s in Species:
        if s.value == species_str:
            species = s
            break
    if species is None:
        species = Species.TIGER
    player = Player(
        id=row["id"],
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

    # 天赋
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
            INSERT OR REPLACE INTO settlement_buildings (player_id, building_name, quantity)
            VALUES (?, ?, ?)
        """, (player_id, name, qty))
    conn.commit()


def load_settlement(player_id):
    """加载营地建筑"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT building_name, quantity FROM settlement_buildings WHERE player_id = ?", (player_id,))
    rows = cursor.fetchall()
    return {row["building_name"]: row["quantity"] for row in rows} if rows else {}

async def save_trade_to_db(trade: dict):
    """保存交易记录到数据库"""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO trade_listings (id, seller_id, seller_species, offer_item, offer_qty, want_item, want_qty, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        trade["id"], trade["seller_id"], trade["seller_species"],
        trade["offer_item"], trade["offer_qty"], trade["want_item"],
        trade["want_qty"], trade.get("status", "active")
    ))
    conn.commit()