"""
《众生之门》核心游戏逻辑
环境消耗、等级经验、战斗判定等
"""
import random
import random as rand
import asyncio
from typing import Optional
import uuid
from datetime import datetime

from app.database import save_player as db_save_player, load_player as db_load_player
from app.core.config import (
    Terrain, Species, SpeciesCategory,
    SPECIES_TERRAIN, WEATHER_EFFECTS, SPECIES_TO_CATEGORY,
    SPECIES_INNATES, SPECIALIZATION_PER_LEVELS,
    TALENT_EFFECTS, ITEM_INFO, Item as ItemEnum,
    CATEGORY_TRAITS, SPECIALIZATIONS,
    MapRegion, MapType, MAP_TO_TYPE, MAP_TO_TERRAIN,
    CITY_MAPS, SPAWN_MAPS, NON_SPAWN_MAPS,
    SPAWN_DESCRIPTIONS, NON_SPAWN_DESCRIPTIONS,
    Item, ItemRarity, MAP_LOOT_TABLE, FISHING_LOOT_TABLE, KILL_LOOT_TABLE,
    RANDOM_EVENTS, EventType,
    Building, BuildingType, BUILDING_RECIPES, BUILDING_EFFECTS,
    MAP_CONNECTIONS, MAP_SHOPS,
    STALL_ELIGIBLE_SPECIES, PLANT_GROWTH,
)
from app.models.player import Player
# 内存存储
# test
_player_storage: dict[str, dict] = {}
_settlement_storage: dict[str, dict] = {}

save_player = db_save_player
load_player = db_load_player


def get_terrain_adaptation(category: SpeciesCategory, terrain: Terrain) -> float:
    """查询物种在某地形下的适配度"""
    return SPECIES_TERRAIN.get(category, {}).get(terrain, 0.0)


def get_weather_effect(weather_str: str, category: SpeciesCategory) -> float:
    """查询天气对某物种的影响系数"""
    weather_table = WEATHER_EFFECTS.get(weather_str, {})
    return weather_table.get(category.value, 0.5)  # 未知天气默认 0.5


def calculate_env_decay(
    player: Player,
    terrain: Terrain,
    weather_str: str
) -> dict:
    """
    计算环境消耗
    返回：四维扣减值（dict）
    """
    category = player.category

    # 1. 获取地形适配度
    terrain_fit = get_terrain_adaptation(category, terrain)

    # 2. 获取天气影响系数
    weather_factor = get_weather_effect(weather_str, category)

    # 天赋效果
    talent_bonus = 1.0
    if player.talent:
        talent_info = TALENT_EFFECTS.get(player.talent.value, {})
        if talent_info.get("env_decay_reduction"):
            talent_bonus -= talent_info["env_decay_reduction"]
        if talent_info.get("terrain_adapt_min"):
            terrain_fit = max(terrain_fit, talent_info["terrain_adapt_min"])

    # 3. 综合环境系数（0.0～2.0）
    env_factor = (2.0 - terrain_fit - weather_factor) * talent_bonus
    env_factor = max(0.0, min(2.0, env_factor))

    # 4. 基础消耗值（每 Tick）
    base_decay = 2.0

    # 5. 计算各项消耗
    vitality_decay = base_decay * env_factor
    stamina_decay = base_decay * env_factor * 0.8
    satiety_decay = base_decay * env_factor * 0.6
    sanity_decay = base_decay * env_factor * 0.5
    # 心灵系精神消耗-30%
    if player.talent and player.talent.value == "心灵系":
        sanity_decay *= 0.7

    return {
        "生命机能": round(vitality_decay, 2),
        "体力耐力": round(stamina_decay, 2),
        "饱腹值": round(satiety_decay, 2),
        "精神状态": round(sanity_decay, 2),
        "地形适配度": terrain_fit,
        "天气系数": weather_factor,
        "综合环境系数": round(env_factor, 2),
    }

def simulate_tick(
    player: Player,
    terrain: Terrain,
    weather_str: str
) -> dict:
    """
    模拟一个时间 Tick，应用环境消耗并返回玩家最新状态
    """
    decay = calculate_env_decay(player, terrain, weather_str)

    player.vital.vitality -= decay["生命机能"]
    player.vital.stamina -= decay["体力耐力"]
    player.vital.satiety -= decay["饱腹值"]
    player.vital.sanity -= decay["精神状态"]

    # 防止负数
    player.vital.vitality = max(0, player.vital.vitality)
    player.vital.stamina = max(0, player.vital.stamina)
    player.vital.satiety = max(0, player.vital.satiety)
    player.vital.sanity = max(0, player.vital.sanity)

    return {
        "msg": "时间流逝...",
        "消耗详情": decay,
        "当前状态": player.model_dump(by_alias=True),
        "存活": all([
            player.vital.vitality > 0,
            player.vital.stamina > 0,
            player.vital.satiety > 0,
            player.vital.sanity > 0,
        ])
    }

# ---------- 等级与经验系统 ----------

# 每级所需经验基数（1级→2级需要100，之后递增）
BASE_EXP_PER_LEVEL = 100
LEVEL_SCALING = 1.5  # 每级经验增长倍率


def exp_to_next_level(current_level: int) -> float:
    """计算升到下一级所需总经验"""
    return BASE_EXP_PER_LEVEL * (current_level ** LEVEL_SCALING)


def calculate_exp_gain(killer_level: int, target_level: int, target_is_red: bool = False) -> float:
    """
    计算击杀经验
    规则：
      - 同级：标准经验
      - 高阶杀低阶：大幅衰减
      - 低阶反杀高阶：翻倍
      - 击杀红名：经验翻倍（与上述叠加）
    """
    base_exp = exp_to_next_level(target_level) * 0.3
    level_diff = target_level - killer_level

    if level_diff > 0:
        # 低阶反杀高阶，经验翻倍
        exp = base_exp * (1 + level_diff * 0.5)
    elif level_diff < 0:
        # 高阶杀低阶，大幅衰减
        decay = max(0.1, 1 - abs(level_diff) * 0.3)
        exp = base_exp * decay
    else:
        exp = base_exp

    # 击杀红名额外翻倍
    if target_is_red:
        exp *= 2.0

    return exp

def add_exp(player: Player, exp: float) -> dict:
    """
    给玩家加经验，自动处理升级
    返回升级信息
    """
    if not hasattr(player, 'exp'):
        player.exp = 0.0

    player.exp += exp
    old_level = player.level
    level_ups = 0
    messages = []

    while True:
        needed = exp_to_next_level(player.level)
        if player.exp >= needed:
            player.exp -= needed
            player.level += 1
            level_ups += 1
            # 每5级给1点专精点
            if player.level % SPECIALIZATION_PER_LEVELS == 0:
                if not hasattr(player, 'spec_points'):
                    player.spec_points = 0
                player.spec_points += 1
            # 升级强化肉身
            player.vital.vitality = min(150, player.vital.vitality + 20)
            player.vital.stamina = min(150, player.vital.stamina + 20)
            player.vital.satiety = min(150, player.vital.satiety + 15)
            player.vital.sanity = min(150, player.vital.sanity + 10)
            # 植物类每级额外+2生命
            if SPECIES_TO_CATEGORY.get(player.species) == SpeciesCategory.PLANT:
                player.vital.vitality = min(200, player.vital.vitality + 2)
        else:
            break

    if level_ups > 0:
        messages.append(f"从 {old_level} 级升至 {player.level} 级，连升 {level_ups} 级")

    return {
        "获得经验": round(exp, 2),
        "当前经验": round(player.exp, 2),
        "升级次数": level_ups,
        "当前等级": player.level,
        "下级所需": round(exp_to_next_level(player.level), 2),
        "升级信息": messages,
    }

# ---------- 写实自由战斗系统 ----------

import random

# 物种克制关系表（基于现实生物链）
# 返回值：攻击方对防御方的伤害倍率
SPECIES_COUNTER = {
    ("高阶猛兽", "普通兽类"): 1.8,
    ("高阶猛兽", "虫兽"): 1.5,
    ("高阶猛兽", "植物"): 1.3,
    ("高阶猛兽", "淡水生物"): 1.4,
    ("高阶猛兽", "浅水生物"): 1.4,
    ("普通兽类", "虫兽"): 1.6,
    ("普通兽类", "植物"): 1.4,
    ("普通兽类", "淡水生物"): 1.3,
    ("普通兽类", "浅水生物"): 1.3,
    ("虫兽", "植物"): 1.8,
    ("虫兽", "淡水生物"): 1.2,
    ("虫兽", "浅水生物"): 1.3,
    ("淡水生物", "海水生物"): 0.6,
    ("海水生物", "淡水生物"): 1.6,
    ("污水生物", "淡水生物"): 1.3,
    ("污水生物", "浅水生物"): 1.2,
    ("浅水生物", "虫兽"): 1.4,
    ("浅水生物", "淡水生物"): 1.1,
    ("人形", "普通兽类"): 1.2,
    ("人形", "植物"): 1.1,
    ("人形", "淡水生物"): 1.1,
    ("人形", "浅水生物"): 1.1,
}


def get_species_counter_bonus(attacker_category: str, defender_category: str) -> float:
    """查询物种克制倍率，默认1.0（无克制）"""
    return SPECIES_COUNTER.get((attacker_category, defender_category), 1.0)


# 地形对各物种的战斗加成/减益
TERRAIN_BATTLE_BONUS = {
    "淡水生物": {"淡水水域": 1.5, "浅水水域": 1.2, "沙漠": 0.2},
    "海水生物": {"海水水域": 1.5, "浅水水域": 1.1, "淡水水域": 0.3},
    "污水生物": {"污水水域": 1.5, "淡水水域": 0.6},
    "浅水生物": {"浅水水域": 1.4, "淡水水域": 1.1, "沙漠": 0.3},
    "人形": {"平原": 1.2, "森林": 1.1, "山地": 1.1},
    "高阶猛兽": {"平原": 1.2, "森林": 1.2, "山地": 1.3},
    "普通兽类": {"森林": 1.3, "平原": 1.1, "山地": 1.1},
    "虫兽": {"森林": 1.3, "沼泽": 1.4, "沙漠": 0.5},
    "植物": {"森林": 1.3, "沼泽": 1.2, "沙漠": 0.3, "冻土": 0.4},
}


def get_terrain_battle_bonus(category_value: str, terrain_value: str) -> float:
    """查询地形战斗加成，默认1.0"""
    table = TERRAIN_BATTLE_BONUS.get(category_value, {})
    return table.get(terrain_value, 1.0)


# 部位损伤效果描述
INJURY_DESCRIPTIONS = {
    "skin_laceration": "皮肉撕裂，每次行动都会传来刺痛",
    "fracture": "骨骼断裂，移动速度大幅下降",
    "blood_loss": "失血不止，视野开始模糊",
    "poison": "毒素蔓延，身体逐渐麻痹",
    "asphyxia": "窒息感加重，力量在流失",
    "frostbite": "冻伤处失去知觉，反应变慢",
    "burn": "灼伤部位火辣辣地疼，行动受限",
    "sensory_damage": "感官受损，难以判断敌人方位",
}


def calculate_damage(
    attacker: Player,
    defender: Player,
    terrain: str,
    attacker_action: str = "猛击",
) -> dict:
    """
    计算单次战斗伤害
    战力优先级：等级压制 > 先天种族 > 环境地利 > 肉身体质 > 操作博弈 > 物种克制
    """
    atk_cat = attacker.category.value
    def_cat = defender.category.value

    # 1. 等级压制（最高优先级）
    level_diff = attacker.level - defender.level
    level_factor = 1.0 + max(-0.5, min(1.0, level_diff * 0.15))

    # 2. 先天种族天赋（肉身基础）
    species_power = {
        "草食性动物": 1.0, "肉食性动物": 1.4, "杂食性动物": 1.1,
        "无脊椎动物": 1.0, "两栖类动物": 1.0, "水生动物": 1.1,
        "植物类生物": 0.8, "真菌类生物": 0.7, "细菌类生物": 0.5,
        "远古类生物": 1.5, "亡灵类": 1.3, "神兽类": 1.8, "外星生物": 1.6,
    }
    atk_species_factor = species_power.get(atk_cat, 1.0)
    def_species_factor = species_power.get(def_cat, 1.0)

    # 3. 环境地利
    terrain_bonus = get_terrain_battle_bonus(atk_cat, terrain)
    terrain_penalty = get_terrain_battle_bonus(def_cat, terrain)

    # 4. 肉身体质（受当前四维影响）
    atk_condition = (attacker.vital.vitality + attacker.vital.stamina) / 200
    def_condition = (defender.vital.vitality + defender.vital.stamina) / 200

    # 5. 操作博弈（动作基础值 + 随机浮动）
    action_base = {
        "猛击": 12, "撕咬": 14, "冲撞": 10, "伏击": 18,
        "缠绕": 8, "拉扯": 9, "追击": 11, "偷袭": 16,
        "利爪": 13, "毒刺": 10,
    }
    base_damage = action_base.get(attacker_action, 10)
    operation_roll = random.uniform(0.8, 1.2)

    # 5.5 天赋加成
    talent_damage_bonus = 1.0
    talent_defense_bonus = 1.0
    if attacker.talent:
        atk_talent = TALENT_EFFECTS.get(attacker.talent.value, {})
        if atk_talent.get("damage_bonus"):
            talent_damage_bonus += atk_talent["damage_bonus"]
    if defender.talent:
        def_talent = TALENT_EFFECTS.get(defender.talent.value, {})
        if def_talent.get("defense_bonus"):
            talent_defense_bonus += def_talent["defense_bonus"]

    # 5.6 生物被动本能
    innate_bonus = 1.0
    innate_defense = 1.0
    innate_poison = 0
    if attacker.species.value in SPECIES_INNATES:
        attacker_innate = SPECIES_INNATES[attacker.species.value]
        if attacker_innate["effect"].get("damage_bonus"):
            innate_bonus += attacker_innate["effect"]["damage_bonus"]
        if attacker_innate["effect"].get("poison_on_hit"):
            innate_poison += attacker_innate["effect"]["poison_on_hit"]
    if defender.species.value in SPECIES_INNATES:
        defender_innate = SPECIES_INNATES[defender.species.value]
        if defender_innate["effect"].get("defense_bonus"):
            innate_defense += defender_innate["effect"]["defense_bonus"]
        if defender_innate["effect"].get("physical_resist"):
            innate_defense += defender_innate["effect"]["physical_resist"]

    # 5.7 武器加成
    weapon_bonus = 0
    inventory = getattr(attacker, 'inventory', {}) or {}
    for item_name, qty in inventory.items():
        for i in ItemEnum:
            if i.value == item_name:
                info = ITEM_INFO.get(i, {})
                dmg = info.get("效果", {}).get("damage_bonus", 0)
                if dmg > 0:
                    weapon_bonus += dmg
                break

    # 6. 物种克制（最低优先级）
    counter_bonus = get_species_counter_bonus(atk_cat, def_cat)

    # 综合伤害计算
    final_damage = (
        base_damage
        * level_factor
        * (atk_species_factor / def_species_factor)
        * terrain_bonus
        * (atk_condition / max(0.3, def_condition))
        * operation_roll
        * counter_bonus
        * talent_damage_bonus
        / talent_defense_bonus
        * innate_bonus
        / innate_defense
    ) + weapon_bonus

    # 根据动作决定主要损伤部位
    injury_targets = {
        "猛击": ["fracture", "skin_laceration"],
        "撕咬": ["skin_laceration", "blood_loss"],
        "冲撞": ["fracture", "skin_laceration"],
        "伏击": ["blood_loss", "sensory_damage"],
        "缠绕": ["asphyxia", "fracture"],
        "拉扯": ["skin_laceration", "fracture"],
        "追击": ["skin_laceration", "blood_loss"],
        "偷袭": ["blood_loss", "sensory_damage"],
        "利爪": ["skin_laceration", "blood_loss"],
        "毒刺": ["poison", "sensory_damage"],
    }

    targets = injury_targets.get(attacker_action, ["skin_laceration"])
    primary_injury = targets[0]
    secondary_injury = targets[1] if len(targets) > 1 else targets[0]

    return {
        "动作": attacker_action,
        "原始基础伤害": base_damage,
        "等级压制系数": round(level_factor, 2),
        "种族战力比": round(atk_species_factor / def_species_factor, 2),
        "地形加成": terrain_bonus,
        "操作浮动": round(operation_roll, 2),
        "物种克制倍率": counter_bonus,
        "最终伤害": round(final_damage, 1),
        "主要损伤部位": primary_injury,
        "次要损伤部位": secondary_injury,
        "天赋加成": {
            "攻击方天赋": attacker.talent.value if attacker.talent else "无",
            "伤害倍率": round(talent_damage_bonus, 2),
            "防御方天赋": defender.talent.value if defender.talent else "无",
            "防御倍率": round(talent_defense_bonus, 2),
        },
        "本能加成": {
            "攻击方本能": SPECIES_INNATES.get(attacker.species.value, {}).get("innate", "无"),
            "攻击倍率": round(innate_bonus, 2),
            "防御方本能": SPECIES_INNATES.get(defender.species.value, {}).get("innate", "无"),
            "防御倍率": round(innate_defense, 2),
            "附带毒素": innate_poison,
        },
        "武器加成": weapon_bonus,
        "部位描述": INJURY_DESCRIPTIONS.get(primary_injury, ""),
    }


def apply_damage(defender: Player, damage_result: dict) -> dict:
    """将伤害应用到防御方身上"""
    dmg = damage_result["最终伤害"]
    primary = damage_result["主要损伤部位"]
    secondary = damage_result["次要损伤部位"]

    # 扣减生命
    defender.vital.vitality = max(0, defender.vital.vitality - dmg * 0.7)
    # 扣减体力
    defender.vital.stamina = max(0, defender.vital.stamina - dmg * 0.3)

    # 部位损伤累积
    current_primary = getattr(defender.injury, primary, 0.0)
    setattr(defender.injury, primary, min(100, current_primary + dmg * 0.5))

    current_secondary = getattr(defender.injury, secondary, 0.0)
    setattr(defender.injury, secondary, min(100, current_secondary + dmg * 0.3))

    is_dead = defender.vital.vitality <= 0

    return {
        "msg": "死亡" if is_dead else "受创",
        "受到伤害": round(dmg, 1),
        "剩余生命": round(defender.vital.vitality, 1),
        "主要损伤": {primary: round(getattr(defender.injury, primary), 1)},
        "次要损伤": {secondary: round(getattr(defender.injury, secondary), 1)},
        "目标存活": not is_dead,
    }


async def execute_battle(
    attacker: Player,
    defender: Player,
    terrain: str,
    attacker_action: str = "猛击",
    defender_action: str = "冲撞",
) -> dict:
    """执行一次完整战斗回合（攻守双方各行动一次）"""

    atk_result = calculate_damage(attacker, defender, terrain, attacker_action)
    def_applied = apply_damage(defender, atk_result)

    def_result = calculate_damage(defender, attacker, terrain, defender_action)
    atk_applied = apply_damage(attacker, def_result)

    return {
        "攻击方动作": atk_result,
        "攻击方造成效果": def_applied,
        "防御方反击": def_result,
        "防御方造成效果": atk_applied,
        "战斗描述": (
            f"{attacker.species.value}使出{attacker_action}，造成{atk_result['最终伤害']}点伤害，"
            f"主要造成{atk_result['主要损伤部位']}。"
            f"{defender.species.value}以{defender_action}回击，造成{def_result['最终伤害']}点伤害。"
        ),
    }


# ---------- 离线/在线与死亡管理系统 ----------

# 死亡冷却时间（秒），防止频繁死亡重开
DEATH_COOLDOWN = 60


def go_offline(player: Player) -> dict:
    """
    主动离线，保留全部数据
    """
    save_result = db_save_player(player)
    player.is_online = False

    # 再次保存恢复后的数据
    db_save_player(player)

    return {
        "msg": f"玩家 {player.id}（{player.species.value}）已离线，数据全部保留，部分状态恢复",
        "玩家状态": player.model_dump(by_alias=True),
    }


def go_online(player_id: str) -> dict:
    """
    上线（无缝续玩）
    规则：保留形态、等级、天赋、道具、营地、储物全部数据
    """
    player = db_load_player(player_id)
    if not player:
        return {"msg": f"玩家 {player_id} 不存在，需要创建新角色", "需要新建": True}

    if player.is_online:
        return {"msg": f"玩家 {player_id} 已在线上", "玩家状态": player.model_dump(by_alias=True)}

    player.is_online = True
    db_save_player(player)

    return {
        "msg": f"玩家 {player_id}（{player.species.value}）上线，无缝续玩",
        "玩家状态": player.model_dump(by_alias=True),
    }


def check_death_cooldown(player_id: str) -> Optional[int]:
    """检查死亡冷却时间，返回剩余秒数，None表示可以重开"""
    death_record = _player_storage.get(f"_death_{player_id}")
    if not death_record:
        return None

    death_time = datetime.fromisoformat(death_record["death_time"])
    elapsed = (datetime.now() - death_time).total_seconds()
    remaining = DEATH_COOLDOWN - elapsed

    if remaining <= 0:
        # 冷却已过，清理记录
        _player_storage.pop(f"_death_{player_id}", None)
        return None

    return int(remaining)


def handle_death(player: Player, killer_id: str = None):
    """死亡处理"""
    from app.database import save_death_record, delete_player_from_db

    species_name = player.species.value
    level = player.level
    player_id = player.id

    # 存储死亡冷却记录到内存
    _player_storage[f"_death_{player_id}"] = {
        "death_time": datetime.now().isoformat()
    }

    # 异步保存死亡记录
    asyncio.create_task(save_death_record(player_id, species_name, level, killer_id))
    # 异步删除玩家数据
    asyncio.create_task(delete_player_from_db(player_id))

    return {
        "msg": f"【死亡】{species_name}（Lv.{level}）生命机能耗尽，已彻底消亡。",
        "死亡物种": species_name,
        "死亡等级": level,
        "击杀者ID": killer_id,
    }

# 物种权重：现实生物合计 90%，神话类合计 10%
SPECIES_WEIGHTS = {
    # 草食性动物 10种，权重各 1.5
    Species.RABBIT: 1.5, Species.DEER: 1.5, Species.SHEEP: 1.5,
    Species.HORSE: 1.5, Species.COW: 1.5, Species.ELEPHANT: 1.5,
    Species.GIRAFFE: 1.5, Species.HIPPO: 1.5, Species.SLOTH: 1.5,
    Species.KOALA: 1.5,
    # 肉食性动物 10种
    Species.TIGER: 1.5, Species.LION: 1.5, Species.WOLF: 1.5,
    Species.LEOPARD: 1.5, Species.EAGLE: 1.5, Species.CROCODILE: 1.5,
    Species.HYENA: 1.5, Species.OTTER: 1.5, Species.SHARK: 1.5,
    Species.SNAKE: 1.5,
    # 杂食性动物 10种
    Species.BEAR: 1.5, Species.PIG: 1.5, Species.FOX: 1.5,
    Species.RACCOON: 1.5, Species.MOUSE: 1.5, Species.GORILLA: 1.5,
    Species.CROW: 1.5, Species.WILDCAT: 1.5, Species.HEDGEHOG: 1.5,
    Species.BADGER: 1.5,Species.HUMAN: 1.5,
    # 无脊椎动物 12种
    Species.CENTIPEDE: 1.2, Species.SCORPION: 1.2, Species.SPIDER: 1.2,
    Species.MANTIS: 1.2, Species.BEETLE: 1.2, Species.ANT: 1.2,
    Species.BEE: 1.2, Species.DRAGONFLY: 1.2, Species.JELLYFISH: 1.2,
    Species.OCTOPUS: 1.2, Species.DUNG_BEETLE: 1.2, Species.EARTHWORM: 1.2,
    # 两栖类 8种
    Species.FROG: 1.2, Species.TOAD: 1.2, Species.NEWT: 1.2,
    Species.GIANT_SALAMANDER: 1.2, Species.TREE_FROG: 1.2,
    Species.POISON_DART_FROG: 1.2, Species.RAIN_FROG: 1.2,
    Species.MUD_PUPPY: 1.2,
    # 水生动物 9种
    Species.GRASS_CARP: 1.3, Species.CARP: 1.3, Species.TUNA: 1.3,
    Species.WHALE: 1.3, Species.DOLPHIN: 1.3, Species.LOBSTER: 1.3,
    Species.CRAB: 1.3, Species.CLAM: 1.3, Species.SEA_TURTLE: 1.3,
    # 植物类 12种
    Species.OAK: 1.3, Species.BAMBOO: 1.3, Species.ROSE: 1.3,
    Species.VINE: 1.3, Species.CACTUS: 1.3, Species.MUSHROOM: 1.3,
    Species.KELP: 1.3, Species.REED: 1.3, Species.PITCHER_PLANT: 1.3,
    Species.MIMOSA: 1.3, Species.VENUS_FLYTRAP: 1.3, Species.GINKGO: 1.3,
    # 真菌类 7种
    Species.SHIITAKE: 1.1, Species.REISHI: 1.1, Species.WOOD_EAR: 1.1,
    Species.SNOW_FUNGUS: 1.1, Species.CORDYCEPS: 1.1,
    Species.FLY_AGARIC: 1.1, Species.PUFFBALL: 1.1,
    # 细菌类 5种
    Species.E_COLI: 1.0, Species.LACTOBACILLUS: 1.0,
    Species.CYANOBACTERIA: 1.0, Species.BACTERIOPHAGE: 1.0,
    Species.YEAST: 1.0,
    # 远古类 6种
    Species.DINOSAUR: 1.0, Species.MAMMOTH: 1.0, Species.SABERTOOTH: 1.0,
    Species.TRILOBITE: 1.0, Species.AMMONITE: 1.0, Species.PTEROSAUR: 1.0,
    # 亡灵类 7种，低权重
    Species.SKELETON: 0.3, Species.GHOST: 0.3, Species.ZOMBIE: 0.3,
    Species.GHOUL: 0.3, Species.LICH: 0.3, Species.VAMPIRE: 0.3,
    Species.REVENANT: 0.3,
    # 神兽类 9种，低权重
    Species.TRUE_DRAGON: 0.2, Species.PHOENIX: 0.2, Species.QILIN: 0.2,
    Species.XUANWU: 0.2, Species.WHITE_TIGER: 0.2,
    Species.VERMILION_BIRD: 0.2, Species.AZURE_DRAGON: 0.2,
    Species.NINE_TAILED_FOX: 0.2, Species.TAOTIE: 0.2,
    # 外星生物 6种，最低权重
    Species.XENOMORPH: 0.15, Species.PREDATOR: 0.15, Species.ET: 0.15,
    Species.MARTIAN: 0.15, Species.SILICON_LIFE: 0.15,
    Species.ENERGY_BEING: 0.15,
}


def weighted_random_species() -> Species:
    """按权重随机选择物种"""
    species_list = list(SPECIES_WEIGHTS.keys())
    weights = list(SPECIES_WEIGHTS.values())
    return random.choices(species_list, weights=weights, k=1)[0]

def create_new_life(user_id: str | None = None) -> dict:
    """
    新玩家/死亡重开
    规则：
      1. 生灵形态完全随机
      2. 固定1级
      3. 随机出生地图（85%新手区，15%其他区域）
      4. 无装备、无道具、无额外天赋加成
    """
    new_species = weighted_random_species()

    player = Player(
        id=uuid.uuid4().hex,
        species=new_species,
        level=1,
        user_id=user_id,
    )
    # 初始道具
    player.inventory = {"野果": 2, "草药绷带":1,"生锈的铁刀": 1}
    # 应用大类特质
    category = SPECIES_TO_CATEGORY.get(new_species)
    if category:
        traits = CATEGORY_TRAITS.get(category.value, {})
        if traits.get("vital_bonus"):
            bonus = traits["vital_bonus"]
            player.vital.vitality = 100 + bonus
            player.vital.stamina = 100 + bonus
            player.vital.satiety = 100 + bonus
            player.vital.sanity = 100 + bonus
        if traits.get("immune_frostbite"):
            player.injury.frostbite = -999  # 标记免疫

    # 随机出生地图
    spawn_info = roll_spawn_region()

    # 初始化玩家当前地图
    player.current_map = spawn_info["地图"]

    # 保存
    db_save_player(player)
    # 生成第二人称叙事
    species_name = new_species.value
    pronoun = "你"

    if spawn_info["是否安全区"]:
        safety_note = "这里是新手区，暂时是安全的。好好熟悉这个世界吧。"
    else:
        safety_note = "这里不是新手区！你感到一丝不安，必须格外小心..."

    narrative = (
        f"{pronoun}缓缓睁开双眼，意识逐渐凝聚。\n\n"
        f"{pronoun}是一只{species_name}，刚刚降临在这片众生之域。\n\n"
        f"【降临之地】{spawn_info['地图']}\n"
        f"{spawn_info['descript']}\n\n"
        f"{safety_note}\n\n"
        f"四周的一切陌生而寂静，{pronoun}能感受到自己微弱但真实的心跳。\n"
        f"生存，从这一刻开始。"
    )

    # 调试：尝试序列化
    import json
    result_test = {
        "msg": f"新的生灵降世：{species_name}",
        "叙事文字": narrative,
                "玩家状态": {
            "id": player.id,
            "species": player.species.value if hasattr(player.species, 'value') else str(player.species),
            "level": player.level,
            "talent": player.talent.value if player.talent and hasattr(player.talent, 'value') else str(player.talent) if player.talent else None,
            "vital": player.vital.model_dump(by_alias=True),
            "injury": player.injury.model_dump(),
            "exp": player.exp,
            "is_online": player.is_online,
            "inventory": getattr(player, 'inventory', {}),
            "current_map": getattr(player, 'current_map', None),
            "settlement": getattr(player, 'settlement', {}),
        },
        "出生信息": {
            "地图": spawn_info["地图"],
            "地图类型": spawn_info["地图类型"],
            "是否安全区": spawn_info["是否安全区"],
        },
    }
    try:
        json.dumps(result_test)
        print("JSON序列化成功")
    except Exception as e:
        print(f"JSON序列化失败: {e}")

    return {
        "msg": f"新的生灵降世：{species_name}",
        "叙事文字": narrative,
        "玩家状态": player.model_dump(by_alias=True),
        "出生信息": {
            "地图": spawn_info["地图"],
            "地图类型": spawn_info["地图类型"],
            "是否安全区": spawn_info["是否安全区"],
        },
    }


# ---------- 第二人称叙事系统 ----------

def narrate(player: Player, event_type: str, **details) -> str:
    """
    将游戏事件转换为第二人称叙事文字
    所有玩家看到的信息都通过这个函数生成
    """
    species_name = player.species.value
    pronoun = "你"

    narratives = {
        # ---------- 出生 ----------
        "new_life": (
            f"{pronoun}缓缓睁开双眼，意识逐渐凝聚。\n"
            f"{pronoun}是一只{species_name}，刚刚降临在这片众生之域。\n"
            f"四周的一切陌生而寂静，{pronoun}能感受到自己微弱但真实的心跳。\n"
            f"生存，从这一刻开始。"
        ),

        # ---------- 环境状态 ----------
        "environment_status": (
            f"{pronoun}环顾四周——"
            f"此刻身处{details.get('terrain', '未知之地')}，"
            f"天气是{details.get('weather', '未知')}。"
            f"{_env_feel_text(player, details)}"
        ),

        # ---------- 时间流逝 ----------
        "tick_pass": (
            f"时间静静流逝...\n"
            f"{_vital_change_text(player, details)}"
        ),

        # ---------- 遭遇其他生灵 ----------
        "encounter": (
            f"前方传来窸窣声响。\n"
            f"{pronoun}看到了——一只{details.get('other_species', '未知生灵')}"
            f"（Lv.{details.get('other_level', '?')}），"
            f"它似乎也注意到了{pronoun}的存在。"
        ),

        # ---------- 战斗发起 ----------
        "battle_start": (
            f"{pronoun}决定出手。\n"
            f"面对{details.get('target_species', '对手')}，"
            f"{pronoun}猛地{details.get('action', '发起攻击')}！"
        ),

        # ---------- 战斗受击 ----------
        "battle_hit": (
            f"{details.get('attacker_species', '对方')}的{details.get('action', '攻击')}"
            f"击中了{pronoun}——{details.get('injury_desc', '一阵剧痛传来')}。"
        ),

        # ---------- 战斗造成伤害 ----------
        "battle_dealt": (
            f"{pronoun}的{details.get('action', '攻击')}命中了目标，"
            f"造成了{details.get('damage', 0)}点伤害。"
        ),

        # ---------- 击杀 ----------
        "kill": (
            f"致命一击——\n"
            f"{details.get('target_species', '对手')}倒下了，再无声息。\n"
            f"{pronoun}获得了{details.get('exp_gain', 0)}点经验。"
        ),

        # ---------- 升级 ----------
        "level_up": (
            f"一股力量涌入{pronoun}体内——\n"
            f"{pronoun}的等级提升至 Lv.{details.get('new_level', player.level)}！\n"
            f"身体变得更加强韧，{pronoun}感觉自己离生存又近了一步。"
        ),

        # ---------- 重伤 ----------
        "heavily_injured": (
            f"{pronoun}感到身体正在崩溃...\n"
            f"{_injury_status_text(player)}\n"
            f"必须尽快脱离危险，否则{pronoun}会死在这里。"
        ),

        # ---------- 离线 ----------
        "offline": (
            f"{pronoun}找到一个隐蔽的角落，蜷缩起来。\n"
            f"伤口还在隐隐作痛，但至少暂时安全了。\n"
            f"{pronoun}的意识渐渐模糊，沉入黑暗之中...\n"
            f"（数据已保存，下次上线时将从这里继续生存）"
        ),

        # ---------- 上线 ----------
        "online": (
            f"{pronoun}的意识重新凝聚。\n"
            f"蜷缩的地方没有被发现，{pronoun}还活着。\n"
            f"身上的伤口愈合了一些，是时候继续求生了。"
        ),

        # ---------- 死亡 ----------
        "death": (
            f"一切都在消散...\n"
            f"{pronoun}——这只{species_name}——的生命走到了尽头。\n"
            f"视野渐渐模糊，身体失去温度，意识坠入永恒的寂静。\n"
            f"【{species_name}（Lv.{player.level}）已彻底消亡】"
        ),

        # ---------- 冷却等待 ----------
        "death_cooldown": (
            f"虚空中，{pronoun}感到一股无形的力量在重塑身躯...\n"
            f"还需要等待 {details.get('remaining', 0)} 秒，"
            f"新的生命才能再次降世。"
        ),
    }

    return narratives.get(event_type, f"{pronoun}经历了什么...")


def _env_feel_text(player: Player, details: dict) -> str:
    """根据环境和玩家状态生成感受描述"""
    terrain_fit = details.get("terrain_fit", 1.0)
    weather_factor = details.get("weather_factor", 1.0)

    terrain_feel = {
        1.0: "这里的每一寸土地都让你感到自在。",
        0.5: "身体有些不适，这里不是理想的栖息地。",
        0.0: "你感到强烈的排斥感，这片土地在拒绝你。",
    }
    weather_feel = {
        1.2: "天气让你的状态格外良好。",
        1.1: "天气让你略微舒适。",
        1.0: "天气对你没有特别的影响。",
        0.9: "天气让你略感不适。",
        0.8: "天气影响了你的状态。",
        0.7: "恶劣的天气让你明显不适。",
        0.6: "天气正在侵蚀你的身体。",
        0.5: "天气让你痛苦不堪。",
        0.4: "你在这天气中艰难挣扎。",
        0.3: "天气在无情地摧残你。",
    }

    terrain_text = ""
    for key, text in terrain_feel.items():
        if terrain_fit == key:
            terrain_text = text
            break
    if not terrain_text:
        terrain_text = "你对这片土地感到陌生。"

    weather_text = ""
    for key, text in weather_feel.items():
        if weather_factor == key:
            weather_text = text
            break
    if not weather_text:
        weather_text = "天气让你不确定是该庆幸还是担忧。"

    return f"{terrain_text} {weather_text}"


def _vital_change_text(player: Player, details: dict) -> str:
    """根据四维消耗生成叙事"""
    decay = details.get("decay", {})
    parts = []

    vitality_d = decay.get("生命机能", 0)
    stamina_d = decay.get("体力耐力", 0)
    satiety_d = decay.get("饱腹值", 0)
    sanity_d = decay.get("精神状态", 0)

    total_decay = vitality_d + stamina_d + satiety_d + sanity_d

    if total_decay == 0:
        return "你没有感到任何不适。"

    if vitality_d > 0:
        parts.append("身体有些疲惫")
    if satiety_d > 0:
        parts.append("腹中传来饥饿感")
    if stamina_d > 0:
        parts.append("四肢微微发沉")
    if sanity_d > 0:
        parts.append("精神有些恍惚")

    if parts:
        return "你感到" + "，".join(parts) + "。"

    return "你感到身体在微弱地消耗着。"


def _injury_status_text(player: Player) -> str:
    """生成部位损伤的叙事描述"""
    injury = player.injury
    parts = []

    thresholds = [
        ("skin_laceration", 30, "皮肤多处撕裂，鲜血渗出"),
        ("fracture", 30, "骨骼发出不祥的嘎吱声"),
        ("blood_loss", 30, "失血让视野阵阵发黑"),
        ("poison", 30, "毒素在血管中蔓延，身体逐渐麻痹"),
        ("asphyxia", 30, "呼吸越来越困难"),
        ("frostbite", 30, "冻伤处已经完全失去知觉"),
        ("burn", 30, "灼伤的皮肤火辣辣地疼"),
        ("sensory_damage", 30, "感官迟钝，周围的声音变得遥远"),
    ]

    for field, threshold, desc in thresholds:
        if getattr(injury, field, 0) >= threshold:
            parts.append(desc)

    if not parts:
        return "身上有些小伤，但暂无大碍。"

    return "——".join(parts) + "。"

# ---------- 随机美好事件系统 ----------

# 美好事件库：每种事件包含触发条件（地形/天气）、叙事文字、精神加成范围
BEAUTIFUL_MOMENTS = [
    {
        "id": "sunshine_feel",
        "条件": {"天气": ["晴天"], "地形": None},
        "概率": 0.3,
        "叙事": [
            "阳光穿过云层洒落下来，暖洋洋的，{pronoun}舒服地眯了眯眼。今天天气真好啊。",
            "晴空万里，微风拂过，{pronoun}感到一阵久违的安宁。",
            "阳光在水面上闪烁，像是碎金铺满了大地，{pronoun}的心情一下子好了起来。",
        ],
        "精神加成": (3, 8),
    },
    {
        "id": "forest_calm",
        "条件": {"天气": None, "地形": ["森林"]},
        "概率": 0.25,
        "叙事": [
            "林间光影斑驳，空气里弥漫着松脂和泥土的气息。这里真好看，{pronoun}想。",
            "一只不知名的小鸟在枝头轻啼，声音清脆悦耳，{pronoun}的心也跟着静了下来。",
            "层层叠叠的绿意在眼前铺展开来，{pronoun}感到一种原始的安宁。",
        ],
        "精神加成": (2, 10),
    },
    {
        "id": "water_peace",
        "条件": {"天气": None, "地形": ["淡水水域", "海水水域", "浅水水域"]},
        "概率": 0.25,
        "叙事": [
            "水波轻轻拍打着岸边，发出柔和的声响，{pronoun}感到内心前所未有的平静。",
            "清澈的水流从身边滑过，像是温柔的抚摸，带走了些许疲惫。",
            "水面倒映着天空的颜色，{pronoun}看了许久，差点忘了自己还在求生。",
        ],
        "精神加成": (2, 8),
    },
    {
        "id": "rain_fresh",
        "条件": {"天气": ["暴雨", "梅雨"], "地形": None},
        "概率": 0.2,
        "叙事": [
            "雨水冲刷着大地，空气变得清新起来，{pronoun}深深地吸了一口气。",
            "雨滴打在叶片上，发出密集的声响。{pronoun}虽然淋湿了，却莫名感到畅快。",
            "暴雨之中，万物反而显得格外鲜活，{pronoun}觉得生命真是奇妙。",
        ],
        "精神加成": (1, 5),
    },
    {
        "id": "snow_beauty",
        "条件": {"天气": ["寒潮"], "地形": ["冻土", "山地"]},
        "概率": 0.3,
        "叙事": [
            "雪花无声地飘落，整个世界都变得洁白而寂静。{pronoun}看着这景色，忘记了寒冷。",
            "银装素裹的天地之间，{pronoun}感到一种苍茫的壮美。",
            "寒风吹过，冰晶在阳光下闪烁如星。{pronoun}打了个寒颤，但嘴角不自觉地上扬。",
        ],
        "精神加成": (2, 8),
    },
    {
        "id": "mountain_view",
        "条件": {"天气": None, "地形": ["山地"]},
        "概率": 0.25,
        "叙事": [
            "站在高处极目远眺，群山如波涛般起伏，{pronoun}感到胸襟为之一阔。",
            "山风吹乱了毛发，却也吹散了心中的阴霾。这里的景色真好。",
            "云雾在山腰缭绕，宛如仙境，{pronoun}觉得自己虽是匆匆过客，却也值了。",
        ],
        "精神加成": (3, 10),
    },
    {
        "id": "grassland_wind",
        "条件": {"天气": None, "地形": ["平原"]},
        "概率": 0.2,
        "叙事": [
            "风吹过原野，草浪一波接一波地涌向天边，{pronoun}看呆了。好美。",
            "广阔的大地上，{pronoun}觉得自己虽然渺小，却也是这天地的一部分。",
            "远处的天际线与草原融为一体，{pronoun}的心也变得开阔起来。",
        ],
        "精神加成": (1, 6),
    },
    {
        "id": "sunset_glow",
        "条件": {"天气": ["晴天", "大雾"], "地形": None},
        "概率": 0.15,
        "叙事": [
            "夕阳把天边染成了瑰丽的橙红色，{pronoun}停下脚步，静静地看了很久。",
            "黄昏的光线温柔地包裹着一切，这是今天最美的时刻，{pronoun}心想。",
            "落日熔金，暮云合璧。{pronoun}的疲惫在这一刻被温暖的光线抚平了些许。",
        ],
        "精神加成": (5, 15),
    },
    {
        "id": "starry_night",
        "条件": {"天气": ["晴天"], "地形": None},
        "概率": 0.1,
        "叙事": [
            "夜色如幕，繁星点点。{pronoun}仰望星空，感受到了一种超越生存的宁静与美丽。",
            "银河横亘在天际，每一颗星星都在安静地闪烁。在这浩瀚之下，{pronoun}觉得自己的烦恼都变小了。",
            "今晚的星空格外清澈，{pronoun}躺下来，让满天星光洗涤疲惫的心灵。",
        ],
        "精神加成": (8, 15),
    },
]


def trigger_beautiful_moment(
    player: Player,
    terrain: str,
    weather_str: str
) -> dict:
    """
    根据当前地形和天气，随机触发美好事件
    返回 {"触发": bool, "叙事": str, "精神加成": int}
    """
    species_name = player.species.value
    pronoun = "你"

    # 筛选符合当前环境条件的事件
    candidates = []
    for event in BEAUTIFUL_MOMENTS:
        天气条件 = event["条件"]["天气"]
        地形条件 = event["条件"]["地形"]

        # 检查天气是否匹配
        天气匹配 = (天气条件 is None) or (weather_str in 天气条件)
        # 检查地形是否匹配
        地形匹配 = (地形条件 is None) or (terrain in 地形条件)

        if 天气匹配 and 地形匹配:
            candidates.append(event)

    if not candidates:
        return {"触发": False, "叙事": "", "精神加成": 0}

    # 随机选一个候选事件
    chosen = random.choice(candidates)

    # 按概率判定是否触发
    if random.random() > chosen["概率"]:
        return {"触发": False, "叙事": "", "精神加成": 0}

    # 随机选一句叙事
    narrative_template = random.choice(chosen["叙事"])
    narrative = narrative_template.replace("{pronoun}", pronoun)

    # 随机精神加成
    min_bonus, max_bonus = chosen["精神加成"]
    bonus = random.randint(min_bonus, max_bonus)

    # 应用加成
    old_sanity = player.vital.sanity
    player.vital.sanity = min(150, player.vital.sanity + bonus)

    return {
        "触发": True,
        "叙事": narrative,
        "精神加成": bonus,
        "精神值变化": f"{old_sanity} → {player.vital.sanity}",
    }

# ---------- 改造 simulate_tick，加入叙事 ----------
def simulate_tick_with_narrative(
    player: Player,
    terrain: Terrain,
    weather_str: str
) -> dict:
    """带叙事和随机美好事件的 Tick 模拟"""
    # 先执行原有逻辑
    result = simulate_tick(player, terrain, weather_str)

    decay = result["消耗详情"]
    narrative = ""

    # 环境描述
    narrative += narrate(player, "environment_status",
                         terrain=terrain.value,
                         weather=weather_str,
                         terrain_fit=decay["地形适配度"],
                         weather_factor=decay["天气系数"]) + "\n\n"

    # 消耗描述
    narrative += narrate(player, "tick_pass",
                         decay=decay,
                         total=sum([
                             decay["生命机能"],
                             decay["体力耐力"],
                             decay["饱腹值"],
                             decay["精神状态"]
                         ]))

    # 随机美好事件
    beautiful = trigger_beautiful_moment(player, terrain.value, weather_str)
    if beautiful["触发"]:
        narrative += "\n\n" + beautiful["叙事"]
        # 把精神加成也反映到结果中
        result["当前状态"]["vital"]["精神状态"] = player.vital.sanity

    result["叙事文字"] = narrative
    result["美好事件"] = beautiful

    return result

# ---------- 地图系统 ----------

def roll_spawn_region() -> dict:
    """
    出生点抽签
    85% 新手区（三个新手区等概率）
    13% 日常练级区
    2%  终极特殊地图或都市区
    """
    roll = random.random()

    if roll < 0.85:
        # 新手区
        region = random.choice(SPAWN_MAPS)
        is_safe = True
    elif roll < 0.98:
        # 日常练级区
        training_maps = [m for m in MapRegion if MAP_TO_TYPE[m] == MapType.TRAINING]
        region = random.choice(training_maps)
        is_safe = False
    else:
        # 终极/都市区
        rare_maps = [m for m in MapRegion if MAP_TO_TYPE[m] in (MapType.ULTIMATE, MapType.CITY)]
        region = random.choice(rare_maps)
        is_safe = False

    terrain = MAP_TO_TERRAIN.get(region, Terrain.PLAINS)
    map_type = MAP_TO_TYPE.get(region, MapType.TRAINING)

    # 生成叙事
    if region in SPAWN_DESCRIPTIONS:
        description = SPAWN_DESCRIPTIONS[region]
    elif region in NON_SPAWN_DESCRIPTIONS:
        description = NON_SPAWN_DESCRIPTIONS.get(region, "一片未知的领域在眼前展开...")
    else:
        description = "你降临在一片未知的土地上..."

    return {
        "地图": region.value,
        "地图类型": map_type.value,
        "对应地形": terrain.value,
        "是否安全区": is_safe,
        "descript": description,
    }


def check_city_combat(map_region: str) -> dict:
    """
    检查是否在都市区触发战斗
    都市区禁止战斗，违者踢出+冷却一天
    """
    for city_map in CITY_MAPS:
        if city_map.value == map_region:
            return {
                "违规": True,
                "msg": "【警告】此地为安宁之地，不可争斗！你被弹出了该区域，需等待游戏内一天才能重新进入。",
                "踢出冷却": "游戏内一天",
            }
    return {"违规": False}


def get_map_terrain(map_region_str: str) -> Terrain:
    """根据地图名称获取对应的地形"""
    for region in MapRegion:
        if region.value == map_region_str:
            return MAP_TO_TERRAIN.get(region, Terrain.PLAINS)
    return Terrain.PLAINS

# ---------- 自杀功能 ----------

def commit_suicide(player: Player) -> dict:
    """
    玩家主动结束生命
    与正常死亡完全相同的惩罚：
      1. 角色彻底销毁、数据全清
      2. 背包全部掉落
      3. 营地建筑保留
      4. 冷却等待
    """
    species_name = player.species.value
    pronoun = "你"

    death_result = handle_death(player, killer_id="self")

    narrative = (
        f"{pronoun}停下了脚步。\n"
        f"作为一只{species_name}，{pronoun}在这众生之域中走到了自己的极限。\n"
        f"不是被猎杀，不是死于环境——是{pronoun}自己选择了终结。\n\n"
        f"身体渐渐失去温度，意识缓缓消散...\n"
        f"【{species_name}（Lv.{player.level}）已自我了断】\n\n"
        f"在冷却结束后，新的生命将重新降世。"
    )

    death_result["叙事文字"] = narrative
    return death_result

# ---------- 道具获取与随机事件系统 ----------

def roll_loot(loot_table: list) -> list:
    """
    根据掉落表投骰子，返回获得的道具列表
    loot_table: [(Item, probability, ...), ...]
    """
    drops = []
    for entry in loot_table:
        item = entry[0]
        prob = entry[1]
        if rand.random() < prob:
            drops.append({"道具": item.value, "稀有度": ITEM_INFO[item]["稀有度"].value, "描述": ITEM_INFO[item]["描述"]})
    return drops


def explore_map(player: Player, map_region_str: str) -> dict:
    """
    地图探索：进入地图时概率获得道具
    """
    loot_table = MAP_LOOT_TABLE.get(map_region_str, [])
    drops = roll_loot(loot_table)

    pronoun = "你"
    if drops:
        item_names = "、".join([d["道具"] for d in drops])
        narrative = f"{pronoun}在{map_region_str}四处探索，发现了一些东西：{item_names}。"
    else:
        narrative = f"{pronoun}在{map_region_str}仔细搜寻了一番，但什么也没找到。"

    return {
        "探索地图": map_region_str,
        "获得道具": drops,
        "叙事": narrative,
    }


def go_fishing(player: Player, map_region_str: str) -> dict:
    """
    钓鱼：水域地图专属
    可能钓到鱼、杂物，也可能触发仙女事件
    """
    pronoun = "你"
    species_name = player.species.value

    # 先检查是否触发仙女事件
    fairy_event = RANDOM_EVENTS.get("仙女问斧")
    if rand.random() < fairy_event["概率"]:
        narrative = rand.choice(fairy_event["叙事"])
        return {
            "事件类型": "仙女事件",
            "叙事": narrative,
            "选项": fairy_event["选项"],
            "需要选择": True,
        }

    # 正常钓鱼
    drops = roll_loot(FISHING_LOOT_TABLE)
    if drops:
        item_names = "、".join([d["道具"] for d in drops])
        narrative = f"{pronoun}甩下钓竿，静静等待...\n浮标猛地下沉！{pronoun}用力一拉——钓上了：{item_names}。"
    else:
        narrative = f"{pronoun}甩下钓竿等了好久，浮标纹丝不动。看来今天不是钓鱼的好日子。"

    return {
        "事件类型": "钓鱼",
        "叙事": narrative,
        "获得道具": drops,
    }


def resolve_fairy_choice(player: Player, choice: str) -> dict:
    """处理仙女问斧的选择"""
    fairy_event = RANDOM_EVENTS["仙女问斧"]
    for option in fairy_event["选项"]:
        if option["选择"] == choice:
            items_got = [{"道具": item.value, "稀有度": ITEM_INFO[item]["稀有度"].value, "描述": ITEM_INFO[item]["描述"]} for item in option["获得"]]
            if "精神变化" in option:
                player.vital.sanity = max(0, min(150, player.vital.sanity + option["精神变化"]))
            return {
                "你的选择": choice,
                "结果": option["结果"],
                "获得道具": items_got,
                "精神变化": option.get("精神变化", 0),
            }
    return {"结果": "仙女等得不耐烦了，消失在了水中。"}


def trigger_random_event(player: Player, terrain_str: str, weather_str: str, map_region_str: str) -> dict:
    """
    随机触发彩蛋事件
    根据当前地形、天气、地图判定哪些事件可能触发
    """
    pronoun = "你"
    candidates = []

    for event_name, event_data in RANDOM_EVENTS.items():
        if event_name == "仙女问斧":
            continue  # 仙女事件单独在钓鱼中触发

        conditions = event_data.get("触发条件", {})
        required_terrain = conditions.get("地形", None)
        required_weather = conditions.get("天气", None)

        terrain_match = (required_terrain is None) or (terrain_str in required_terrain) or (map_region_str in required_terrain)
        weather_match = (required_weather is None) or (weather_str in required_weather)

        if terrain_match and weather_match:
            candidates.append((event_name, event_data))

    if not candidates:
        return {"触发": False, "叙事": "", "事件类型": "无"}

    # 随机选一个候选事件
    event_name, event_data = rand.choice(candidates)

    if rand.random() > event_data["概率"]:
        return {"触发": False, "叙事": "", "事件类型": "无"}

    # 生成叙事
    narrative = rand.choice(event_data["叙事"]) if isinstance(event_data["叙事"], list) else event_data["叙事"]

    # 处理奖励
    drops = []
    if "固定奖励" in event_data:
        for reward in event_data["固定奖励"]:
            prob = reward.get("概率", 1.0)
            if rand.random() < prob:
                item = reward["道具"]
                qty = reward.get("数量", 1)
                for _ in range(qty):
                    drops.append({"道具": item.value, "稀有度": ITEM_INFO[item]["稀有度"].value, "描述": ITEM_INFO[item]["描述"]})

    if "随机奖励" in event_data:
        drops.extend(roll_loot(event_data["随机奖励"]))

    # 精神变化
    if "精神加成" in event_data:
        min_b, max_b = event_data["精神加成"]
        bonus = rand.randint(min_b, max_b)
        player.vital.sanity = min(150, player.vital.sanity + bonus)
        narrative += f"\n\n（精神状态恢复了 {bonus} 点）"
    elif "精神变化" in event_data:
        player.vital.sanity = max(0, min(150, player.vital.sanity + event_data["精神变化"]))
        narrative += f"\n\n（精神状态变化了 {event_data['精神变化']} 点）"

    return {
        "触发": True,
        "事件类型": event_name,
        "叙事": narrative,
        "获得道具": drops,
        "精神变化": event_data.get("精神加成", event_data.get("精神变化", 0)),
    }


def get_kill_loot(category_value: str) -> list:
    """根据被击杀者的大类获取掉落道具"""
    table = KILL_LOOT_TABLE.get(category_value, [])
    return roll_loot(table)


# ---------- 背包系统 ----------

def add_to_inventory(player: Player, item_name: str, quantity: int = 1) -> dict:
    """添加道具到背包"""
    if not hasattr(player, 'inventory') or player.inventory is None:
        player.inventory = {}

    current = player.inventory.get(item_name, 0)
    player.inventory[item_name] = current + quantity

    return {
        "msg": f"获得了 {item_name} x{quantity}",
        "道具": item_name,
        "新增数量": quantity,
        "当前持有": player.inventory[item_name],
    }


def remove_from_inventory(player: Player, item_name: str, quantity: int = 1) -> dict:
    """从背包移除道具"""
    if not hasattr(player, 'inventory') or player.inventory is None:
        return {"msg": "背包是空的", "成功": False}

    current = player.inventory.get(item_name, 0)
    if current < quantity:
        return {"msg": f"道具不足：需要 {item_name} x{quantity}，但你只有 x{current}", "成功": False}

    player.inventory[item_name] = current - quantity
    if player.inventory[item_name] <= 0:
        del player.inventory[item_name]

    return {
        "msg": f"使用了 {item_name} x{quantity}",
        "道具": item_name,
        "消耗数量": quantity,
        "剩余": player.inventory.get(item_name, 0),
        "成功": True,
    }


def view_inventory(player: Player) -> dict:
    """查看背包"""
    if not hasattr(player, 'inventory') or not player.inventory:
        return {
            "msg": "背包空空如也。",
            "背包": {},
            "物品种类数": 0,
            "物品总数": 0,
        }

    total = sum(player.inventory.values())
    return {
        "msg": f"背包里有 {len(player.inventory)} 种物品，共 {total} 件。",
        "背包": player.inventory,
        "物品种类数": len(player.inventory),
        "物品总数": total,
    }


def use_item(player: Player, item_name: str) -> dict:
    """
    使用道具
    根据道具类型自动生效（治疗、饱腹、抗性等）
    """
    from app.core.config import Item, ITEM_INFO

    # 查找道具枚举
    item = None
    for i in Item:
        if i.value == item_name:
            item = i
            break

    if item is None:
        return {"msg": f"不存在名为 {item_name} 的道具", "成功": False}

    info = ITEM_INFO.get(item, {})
    effects = info.get("效果", {})

    if not effects:
        return {"msg": f"{item_name} 无法直接使用，它是材料类道具。", "成功": False}

    # 检查背包
    if not hasattr(player, 'inventory') or player.inventory.get(item_name, 0) < 1:
        return {"msg": f"背包中没有 {item_name}", "成功": False}

    # 应用效果
    applied = {}
    for stat, value in effects.items():
        if stat == "生命机能":
            player.vital.vitality = min(150, player.vital.vitality + value)
            applied["生命机能"] = f"+{value}"
        elif stat == "体力耐力":
            player.vital.stamina = min(150, player.vital.stamina + value)
            applied["体力耐力"] = f"+{value}"
        elif stat == "饱腹值":
            player.vital.satiety = min(150, player.vital.satiety + value)
            applied["饱腹值"] = f"+{value}"
        elif stat == "精神状态":
            player.vital.sanity = min(150, player.vital.sanity + value)
            applied["精神状态"] = f"+{value}"
        elif stat == "皮肉撕裂":
            player.injury.skin_laceration = max(0, player.injury.skin_laceration + value)
            applied["皮肉撕裂"] = f"{value}"
        elif stat == "骨折":
            player.injury.fracture = max(0, player.injury.fracture + value)
            applied["骨折"] = f"{value}"
        elif stat == "失血":
            player.injury.blood_loss = max(0, player.injury.blood_loss + value)
            applied["失血"] = f"{value}"
        elif stat == "中毒":
            player.injury.poison = max(0, player.injury.poison + value)
            applied["中毒"] = f"{value}"
        elif stat == "窒息":
            player.injury.asphyxia = max(0, player.injury.asphyxia + value)
            applied["窒息"] = f"{value}"
        elif stat == "冻伤":
            player.injury.frostbite = max(0, player.injury.frostbite + value)
            applied["冻伤"] = f"{value}"
        elif stat == "灼伤":
            player.injury.burn = max(0, player.injury.burn + value)
            applied["灼伤"] = f"{value}"

    # 消耗道具
    remove_result = remove_from_inventory(player, item_name, 1)

    return {
        "msg": f"使用了 {item_name}：{info.get('描述', '')}",
        "应用效果": applied,
        "消耗": remove_result,
        "成功": True,
    }


# ---------- 营地建造系统 ----------

def can_build(player: Player, building: Building) -> dict:
    """检查玩家是否有足够材料建造"""
    recipe = BUILDING_RECIPES.get(building, {})
    if not recipe:
        return {"可以建造": False, "原因": "未知建筑", "缺少材料": []}

    inventory = getattr(player, 'inventory', {}) or {}
    missing = []

    # 造物系天赋：材料-20%
    if player.talent and player.talent.value == "造物系":
        recipe = {m: max(1, int(q * 0.8)) for m, q in recipe.items()}
    for material, required_qty in recipe.items():
        owned = inventory.get(material.value, 0)
        if owned < required_qty:
            missing.append({
                "材料": material.value,
                "需要": required_qty,
                "持有": owned,
                "还差": required_qty - owned,
            })

    return {
        "可以建造": len(missing) == 0,
        "建筑": building.value,
        "所需材料": {m.value: q for m, q in recipe.items()},
        "缺少材料": missing,
    }


def build(player: Player, building: Building) -> dict:
    """
    建造建筑
    1. 检查材料
    2. 扣除材料
    3. 添加到营地
    """
    check = can_build(player, building)
    if not check["可以建造"]:
        return {
            "msg": f"材料不足，无法建造 {building.value}。",
            "详情": check,
            "成功": False,
        }

    # 扣除材料
    recipe = BUILDING_RECIPES[building]
    for material, qty in recipe.items():
        remove_from_inventory(player, material.value, qty)

    # 添加到营地
    if not hasattr(player, 'settlement') or player.settlement is None:
        player.settlement = {}

    building_name = building.value
    player.settlement[building_name] = player.settlement.get(building_name, 0) + 1

    # 保存建筑到持久存储
    if player.id not in _settlement_storage:
        _settlement_storage[player.id] = {}
    _settlement_storage[player.id][building_name] = _settlement_storage[player.id].get(building_name, 0) + 1

    description = BUILDING_EFFECTS.get(building, "一座新建成的建筑。")
    pronoun = "你"

    narrative = (
        f"{pronoun}花了些功夫，终于建成了——{building.value}。\n"
        f"{description}\n"
        f"营地变得更像一个家了。"
    )

    return {
        "msg": f"成功建造 {building.value}",
        "叙事": narrative,
        "建筑效果": description,
        "消耗材料": {m.value: q for m, q in recipe.items()},
        "营地当前建筑": player.settlement,
        "成功": True,
    }


def view_settlement(player: Player) -> dict:
    """查看营地"""
    settlement = getattr(player, 'settlement', None) or {}
    storage = _settlement_storage.get(player.id, {})

    # 合并两者
    all_buildings = {**storage, **settlement}
    player.settlement = all_buildings

    if not all_buildings:
        return {
            "msg": "你还没有建造任何东西。这里只是一片空地。",
            "营地": {},
            "建筑数量": 0,
        }

    building_list = []
    for name, count in all_buildings.items():
        building_list.append(f"{name} x{count}")

    narrative = f"你的营地：{'、'.join(building_list)}。"

    return {
        "msg": narrative,
        "营地": all_buildings,
        "建筑数量": sum(all_buildings.values()),
        "建筑列表": building_list,
    }


def dismantle(player: Player, building_name: str) -> dict:
    """
    拆除建筑，返还50%材料
    """
    settlement = getattr(player, 'settlement', {}) or {}
    storage = _settlement_storage.get(player.id, {})
    all_buildings = {**storage, **settlement}

    if building_name not in all_buildings or all_buildings[building_name] < 1:
        return {"msg": f"营地中没有 {building_name}。", "成功": False}

    # 找到对应的 Building 枚举
    building_enum = None
    for b in Building:
        if b.value == building_name:
            building_enum = b
            break

    if not building_enum:
        return {"msg": f"无法识别建筑：{building_name}", "成功": False}

    # 扣除建筑
    all_buildings[building_name] -= 1
    if all_buildings[building_name] <= 0:
        del all_buildings[building_name]

    player.settlement = all_buildings
    _settlement_storage[player.id] = all_buildings

    # 返还50%材料
    recipe = BUILDING_RECIPES.get(building_enum, {})
    returned = {}
    for material, qty in recipe.items():
        refund = max(1, qty // 2)
        add_to_inventory(player, material.value, refund)
        returned[material.value] = refund

    return {
        "msg": f"拆除了 {building_name}，回收了部分材料。",
        "回收材料": returned,
        "营地当前建筑": all_buildings,
        "成功": True,
    }

# ---------- 精神值细分系统 ----------

def calculate_sanity_modifier(player: Player, terrain_str: str, weather_str: str, time_of_day: str = "day") -> float:
    """
    计算精神值额外修正
    黑暗/暴雨/孤身深山会掉精神
    美景/鸟鸣/日落/秘境静心回精神
    """
    modifier = 0.0
    category = player.category.value

    # 黑暗环境
    if time_of_day == "night":
        modifier -= 3.0
        if "亡灵" in category:
            modifier += 5.0  # 亡灵夜晚反而精神

    # 恶劣天气
    if weather_str in ["暴雨", "狂风"]:
        modifier -= 2.0
    elif weather_str in ["大雾"]:
        modifier -= 1.0

    # 孤身深山/荒漠
    if terrain_str in ["山地", "沙漠", "冻土"]:
        modifier -= 1.5

    # 特定物种加成
    if "植物" in category and weather_str == "晴天":
        modifier += 2.0  # 植物晴天光合作用心情好

    return modifier


# ---------- 专精加点系统 ----------


def allocate_spec_point(player: Player, spec_name: str) -> dict:
    """分配专精点"""
    if spec_name not in SPECIALIZATIONS:
        return {"msg": f"不存在专精：{spec_name}", "成功": False}

    if not hasattr(player, 'spec_points') or player.spec_points <= 0:
        return {"msg": "没有可用的专精点", "成功": False}

    spec_info = SPECIALIZATIONS[spec_name]
    current_level = player.specializations.get(spec_name, 0)
    max_level = spec_info["max_level"]

    if current_level >= max_level:
        return {"msg": f"{spec_name}已达满级（{max_level}级）", "成功": False}

    player.spec_points -= 1
    player.specializations[spec_name] = current_level + 1

    return {
        "msg": f"{spec_name}提升至 Lv.{current_level + 1}",
        "专精": spec_name,
        "当前等级": current_level + 1,
        "效果": spec_info["desc"],
        "剩余专精点": player.spec_points,
        "成功": True,
    }


def get_specialization_effects(player: Player) -> dict:
    """获取玩家所有专精的累计效果"""
    effects = {
        "weather_reduction": 0.0,
        "water_adapt_bonus": 0.0,
        "vital_bonus": 0,
        "terrain_adapt_bonus": 0.0,
        "combat_bonus": 0.0,
        "exp_bonus": 0.0,
    }

    for spec_name, level in player.specializations.items():
        if level > 0 and spec_name in SPECIALIZATIONS:
            per_level = SPECIALIZATIONS[spec_name]["effect_per_level"]
            for key, value in per_level.items():
                if key in effects:
                    effects[key] += value * level

    return effects


# ---------- 都市区完整规则 ----------

def check_city_rules(player: Player, action: str, map_region: str) -> dict:
    """
    检查都市区规则
    都市区禁止任何战斗动作，只能探索、捡道具、触发彩蛋、交易
    """
    # 检查是否在都市区
    is_city = False
    for city_map in CITY_MAPS:
        if city_map.value == map_region:
            is_city = True
            break

    if not is_city:
        return {"违规": False}

    # 禁止的战斗动作
    combat_actions = ["猛击", "撕咬", "冲撞", "伏击", "缠绕", "拉扯", "追击", "偷袭", "利爪", "毒刺", "狩猎", "攻击"]

    if action in combat_actions:
        # 违规惩罚：强制传送 + 虚弱debuff
        punishment = {
            "违规": True,
            "msg": "【都市守护结界】此乃安宁之地，不可争斗！一股无形的力量将你弹出了城市...",
            "强制传送": "城郊青草地",  # 默认弹出到新手区
            "虚弱debuff": {
                "持续时间": "游戏内一天（24 Tick）",
                "效果": "所有伤害-50%，环境消耗+50%",
            },
        }

        # 应用虚弱效果
        player.vital.vitality = max(1, player.vital.vitality * 0.7)
        player.vital.stamina = max(1, player.vital.stamina * 0.7)
        if not hasattr(player, 'debuffs'):
            player.debuffs = []
        player.debuffs.append({
            "name": "都市惩戒",
            "剩余Tick": 24,
            "效果": "伤害-50%，消耗+50%",
        })

        # 传送出都市
        player.current_map = "城郊青草地"

        return punishment

    return {"违规": False, "msg": "你感受到都市的安宁气息，这里禁止争斗，只能探索和交易。"}


def get_city_ambience(map_region: str, time_of_day: str = "day") -> str:
    """获取都市区行人氛围叙事"""
    ambiences = {
        "都市商业街": {
            "day": "商业街上人来人往，橱窗里的灯光温暖而明亮。路人行色匆匆，没人注意到你的存在。",
            "night": "夜晚的商业街霓虹闪烁，街角的公交站台空无一人。远处传来模糊的音乐声。",
        },
        "山间古寺遗址": {
            "day": "古寺幽静，石阶上落满了松针。偶尔有修行者静坐庭前，闭目不语。风穿过古柏，发出沙沙的声响。",
            "night": "月光洒在古寺残垣上，院内一片银白。远处传来若有若无的钟声，令人心神宁静。",
        },
        "跨海长桥": {
            "day": "海风吹过桥面，海浪拍打着桥墩。远方海天一色，偶尔有海鸥掠过。",
            "night": "长桥两侧的路灯连成一线，倒映在漆黑的海面上，像是通往星空的走廊。",
        },
    }

    region_amb = ambiences.get(map_region, {})
    return region_amb.get(time_of_day, "你漫步在这片宁静之地，感受着难得的平和。")


def apply_city_debuff_tick(player: Player) -> dict:
    """每个Tick更新都市惩戒debuff"""
    if not hasattr(player, 'debuffs') or not player.debuffs:
        return {"active": False}

    remaining_debuffs = []
    expired = []
    for d in player.debuffs:
        d["剩余Tick"] -= 1
        if d["剩余Tick"] <= 0:
            expired.append(d)
        else:
            remaining_debuffs.append(d)

    player.debuffs = remaining_debuffs

    if expired:
        return {
            "active": len(remaining_debuffs) > 0,
            "msg": "你感到身体的虚弱感渐渐消退——都市的惩戒解除了。",
            "剩余debuff": len(remaining_debuffs),
        }

    return {"active": len(remaining_debuffs) > 0, "剩余debuff": len(remaining_debuffs)}


# ---------- 秘境专属规则 ----------

# 秘境地图列表
INSTANCE_MAPS = ["幻境心林", "时光溪谷", "沉船深海遗迹"]

# 秘境专属效果
INSTANCE_EFFECTS = {
    "幻境心林": {
        "desc": "个人幻境空间，每个人进去景色都不一样。用来突破修为、净化心魔。",
        "sanity_decay_per_tick": 3,  # 精神持续消耗
        "exp_bonus": 0.5,  # 经验获取+50%
        "rare_loot_bonus": 0.15,  # 稀有道具掉落+15%
        "max_ticks": 30,  # 最多停留30 Tick
        "unique_items": ["神秘古卷", "灵石"],
    },
    "时光溪谷": {
        "desc": "内部时间流速和外界不同，适合独自闭关修炼。",
        "time_multiplier": 2,  # 时间流速翻倍（效果：经验获取翻倍）
        "vitality_decay_per_tick": 2,  # 生命持续消耗
        "exp_bonus": 1.0,  # 经验获取+100%
        "max_ticks": 20,  # 最多停留20 Tick
        "unique_items": ["神秘古卷", "凤凰羽毛"],
    },
    "沉船深海遗迹": {
        "desc": "海底沉船、珊瑚迷宫、水下古遗迹。",
        "asphyxia_decay_per_tick": 5,  # 窒息压力持续增加
        "rare_loot_bonus": 0.25,  # 稀有道具掉落+25%
        "max_ticks": 15,  # 最多停留15 Tick（水下更危险）
        "unique_items": ["断钥", "避水符", "凤凰羽毛"],
    },
}


def enter_instance(player: Player, map_name: str) -> dict:
    """进入秘境"""
    if map_name not in INSTANCE_EFFECTS:
        return {"msg": f"{map_name} 不是秘境", "成功": False}

    effect = INSTANCE_EFFECTS[map_name]
    player.current_map = map_name

    # 初始化秘境计时
    if not hasattr(player, 'instance_ticks'):
        player.instance_ticks = 0

    return {
        "msg": f"你进入了 {map_name}——{effect['desc']}",
        "秘境": map_name,
        "效果": {
            "经验加成": f"{int(effect.get('exp_bonus', 0) * 100)}%",
            "稀有掉落加成": f"{int(effect.get('rare_loot_bonus', 0) * 100)}%",
            "最多停留": f"{effect['max_ticks']} Tick",
        },
        "警告": effect.get("sanity_decay_per_tick", 0) > 0 and "精神值会持续消耗" or effect.get(
            "vitality_decay_per_tick", 0) > 0 and "生命值会持续消耗" or effect.get("asphyxia_decay_per_tick",
                                                                                   0) > 0 and "窒息值会持续累积" or "",
        "成功": True,
    }


def instance_tick(player: Player, map_name: str) -> dict:
    """秘境每Tick的效果"""
    if map_name not in INSTANCE_EFFECTS:
        return {"msg": "不在秘境中"}

    effect = INSTANCE_EFFECTS[map_name]

    if not hasattr(player, 'instance_ticks'):
        player.instance_ticks = 0
    player.instance_ticks += 1

    # 检查是否超时
    if player.instance_ticks > effect["max_ticks"]:
        player.current_map = "城郊青草地"
        player.instance_ticks = 0
        return {
            "msg": f"你在 {map_name} 中停留过久，被一股力量传送回了城郊青草地。",
            "超时退出": True,
            "当前地图": player.current_map,
        }

    # 应用秘境专属消耗
    decay_msg = []
    if effect.get("sanity_decay_per_tick"):
        player.vital.sanity = max(0, player.vital.sanity - effect["sanity_decay_per_tick"])
        decay_msg.append(f"精神-{effect['sanity_decay_per_tick']}")
    if effect.get("vitality_decay_per_tick"):
        player.vital.vitality = max(0, player.vital.vitality - effect["vitality_decay_per_tick"])
        decay_msg.append(f"生命-{effect['vitality_decay_per_tick']}")
    if effect.get("asphyxia_decay_per_tick"):
        player.injury.asphyxia = min(100, player.injury.asphyxia + effect["asphyxia_decay_per_tick"])
        decay_msg.append(f"窒息+{effect['asphyxia_decay_per_tick']}")

    return {
        "msg": f"秘境时间流逝... {'，'.join(decay_msg) if decay_msg else ''}",
        "已停留": f"{player.instance_ticks}/{effect['max_ticks']} Tick",
        "当前状态": player.model_dump(by_alias=True),
        "存活": all([
            player.vital.vitality > 0,
            player.vital.sanity > 0,
            player.injury.asphyxia < 100,
        ]),
    }


def exit_instance(player: Player) -> dict:
    """主动离开秘境"""
    old_map = player.current_map
    player.current_map = "城郊青草地"
    player.instance_ticks = 0

    return {
        "msg": f"你离开了 {old_map}，回到了城郊青草地。秘境中的收获保留了下来。",
        "当前地图": player.current_map,
    }


# ---------- 种田植物生态 ----------

def get_plant_growth_stage(player: Player) -> dict:
    """获取植物当前生长阶段信息"""
    category = player.category.value
    if "植物" not in category and "真菌" not in category:
        return {"is_plant": False, "msg": "你不是植物或真菌类生灵"}

    if not hasattr(player, 'plant_growth'):
        player.plant_growth = {
            "阶段": "种子",
            "进度": 0,
            "总Tick": 0,
            "已收获": False,
        }

    growth = player.plant_growth
    stages = PLANT_GROWTH["生长阶段"]
    stage_durations = PLANT_GROWTH["阶段时长"]
    current_stage = growth["阶段"]
    current_progress = growth["进度"]
    stage_max = stage_durations.get(current_stage, 10)

    return {
        "is_plant": True,
        "current_stage": current_stage,
        "progress": f"{current_progress}/{stage_max} Tick",
        "percent": round(current_progress / stage_max * 100, 1),
        "total_ticks": growth["总Tick"],
        "stages_list": stages,
        "next_stage": stages[stages.index(current_stage) + 1] if current_stage in stages and stages.index(
            current_stage) < len(stages) - 1 else None,
    }


def tick_plant_growth(player: Player, weather: str, has_greenhouse: bool = False) -> dict:
    """植物生长Tick"""
    category = player.category.value
    if "植物" not in category and "真菌" not in category:
        return {"msg": "你不是植物"}

    # 初始化
    if not hasattr(player, 'plant_growth'):
        player.plant_growth = {
            "阶段": "种子",
            "进度": 0,
            "总Tick": 0,
            "已收获": False,
        }

    growth = player.plant_growth

    # 枯萎后不再生长
    if growth["阶段"] == "枯萎":
        return {
            "msg": f"你已经枯萎了。静静地化为泥土的一部分。",
            "stage": "枯萎",
        }

    # 结果后不再生长
    if growth["已收获"] and growth["阶段"] == "结果":
        return {"msg": "你已经完成了一轮结果，正在休养。", "stage": "结果"}

    # 计算生长速度
    growth_speed = 1.0

    # 天气影响
    weather_bonus = PLANT_GROWTH["天气加成"].get(weather, {})
    growth_speed *= weather_bonus.get("生长速度", 1.0)

    # 温室加成
    if has_greenhouse:
        growth_speed *= 1.5

    # 植物本能加成
    if player.species.value in SPECIES_INNATES:
        innate = SPECIES_INNATES[player.species.value]
        if innate["effect"].get("regen_bonus"):
            growth_speed *= (1 + innate["effect"]["regen_bonus"])

    # 推进进度
    growth["进度"] += growth_speed
    growth["总Tick"] += 1

    # 检查是否进入下一阶段
    stages = PLANT_GROWTH["生长阶段"]
    stage_durations = PLANT_GROWTH["阶段时长"]
    current_stage = growth["阶段"]
    stage_max = stage_durations.get(current_stage, 10)

    if growth["进度"] >= stage_max:
        # 进入下一阶段
        current_idx = stages.index(current_stage) if current_stage in stages else -1
        if current_idx < len(stages) - 1:
            next_stage = stages[current_idx + 1]
            growth["阶段"] = next_stage
            growth["进度"] = 0

            return {
                "msg": f"你进入了 {next_stage} 阶段！",
                "old_stage": current_stage,
                "new_stage": next_stage,
                "weather_effect": weather_bonus.get("描述", ""),
            }
        else:
            growth["阶段"] = "枯萎"
            return {"msg": "你走完了生命的轮回，开始枯萎...", "stage": "枯萎"}

    return {
        "msg": f"你在阳光下静静生长...（{current_stage}）",
        "stage": current_stage,
        "progress": f"{int(growth['进度'])}/{stage_max}",
        "speed": round(growth_speed, 2),
        "weather_effect": weather_bonus.get("描述", ""),
    }


def harvest_plant(player: Player) -> dict:
    """收获植物产物"""
    category = player.category.value
    if "植物" not in category and "真菌" not in category:
        return {"msg": "你不是植物", "成功": False}

    if not hasattr(player, 'plant_growth') or player.plant_growth["阶段"] not in ["成熟", "开花", "结果"]:
        return {"msg": "你还没到可以收获的阶段", "成功": False}

    growth = player.plant_growth
    produce = PLANT_GROWTH["产出"].get(player.species.value, {})
    item_name = produce.get(f"{growth['阶段']}阶段产出", produce.get("成熟阶段产出", "野果"))
    quantity = produce.get("产出量", 1)

    growth["已收获"] = True

    # 加入背包
    if not hasattr(player, 'inventory'):
        player.inventory = {}
    player.inventory[item_name] = player.inventory.get(item_name, 0) + quantity

    return {
        "msg": f"你收获了自己的产物：{item_name} x{quantity}！",
        "产物": item_name,
        "数量": quantity,
        "当前阶段": growth["阶段"],
        "成功": True,
    }


# ---------- 商店系统 ----------


def get_shops_for_map(map_region: str) -> dict:
    """根据地图获取所有商店"""
    shops = MAP_SHOPS.get(map_region)
    if not shops:
        return {"有商店": False, "msg": "这里没有商店。"}

    return {
        "有商店": True,
        "商店数量": len(shops["商店列表"]),
        "商店列表": shops["商店列表"],
    }


def buy_item(player: Player, map_region: str, shop_name: str, item_name: str) -> dict:
    """在指定商店购买商品"""
    shops = MAP_SHOPS.get(map_region)
    if not shops:
        return {"msg": "这里没有商店。", "成功": False}

    # 找到指定商店
    target_shop = None
    for shop in shops["商店列表"]:
        if shop["商店名"] == shop_name:
            target_shop = shop
            break

    if not target_shop:
        return {"msg": f"找不到商店：{shop_name}", "成功": False}

    # 查找商品
    target_item = None
    for item in target_shop["商品"]:
        if item["名称"] == item_name:
            target_item = item
            break

    if not target_item:
        return {"msg": f"{shop_name}里没有 {item_name}。", "成功": False}

    # 解析价格
    price_str = target_item["价格"]
    price_parts = price_str.split("x")
    price_item = price_parts[0]
    price_qty = int(price_parts[1])

    # 检查背包
    inventory = getattr(player, 'inventory', {}) or {}
    owned = inventory.get(price_item, 0)
    if owned < price_qty:
        return {
            "msg": f"材料不足，需要 {price_str}，你只有 {price_item}x{owned}。",
            "成功": False,
        }

    # 扣材料
    inventory[price_item] -= price_qty
    if inventory[price_item] <= 0:
        del inventory[price_item]

    # 加商品
    inventory[item_name] = inventory.get(item_name, 0) + 1
    player.inventory = inventory

    return {
        "msg": f"在{shop_name}用 {price_str} 换取了 {item_name}。",
        "获得": item_name,
        "付出": price_str,
        "商店": shop_name,
        "成功": True,
    }


# ---------- 红名系统 ----------
RED_NAME_KILL_THRESHOLD = 15  # 击杀同大类超过15个变红名
PENANCE_TICKS_REQUIRED = 50  # 忏悔所需Tick数


def check_red_name(player: Player) -> dict:
    """检查并更新红名状态"""
    if not hasattr(player, 'red_name'):
        player.red_name = False
        player.same_category_kills = 0
        player.penance_ticks = 0

    return {
        "is_red_name": player.red_name,
        "同大类击杀数": player.same_category_kills,
        "忏悔进度": f"{player.penance_ticks}/{PENANCE_TICKS_REQUIRED}" if player.red_name else "无需忏悔",
    }


def record_kill(attacker: Player, defender: Player) -> dict:
    """记录击杀，检查是否触发红名"""
    if not hasattr(attacker, 'same_category_kills'):
        attacker.same_category_kills = 0
        attacker.red_name = False
        attacker.penance_ticks = 0

    # 检查是否同大类
    attacker_cat = attacker.category.value if hasattr(attacker.category, 'value') else str(attacker.category)
    defender_cat = defender.category.value if hasattr(defender.category, 'value') else str(defender.category)

    if attacker_cat == defender_cat:
        attacker.same_category_kills += 1

        if attacker.same_category_kills >= RED_NAME_KILL_THRESHOLD and not attacker.red_name:
            attacker.red_name = True
            attacker.penance_ticks = 0
            return {
                "触发红名": True,
                "msg": f"你已经击杀了 {attacker.same_category_kills} 个同族！血腥味弥漫全身，你成为了红名玩家...",
                "同大类击杀数": attacker.same_category_kills,
            }

    return {
        "触发红名": False,
        "同大类击杀数": attacker.same_category_kills,
    }


def tick_penance(player: Player) -> dict:
    """每个Tick更新忏悔进度"""
    if not hasattr(player, 'red_name') or not player.red_name:
        return {"msg": "", "忏悔完成": False}

    if not hasattr(player, 'penance_ticks'):
        player.penance_ticks = 0

    player.penance_ticks += 1

    # 每10Tick发一次内心独白
    if player.penance_ticks in [10, 20, 30, 40]:
        msgs = {
            10: "你感到内心的躁动渐渐平息...",
            20: "风穿过荒野，也穿过你的身体。那些杀戮的记忆开始模糊...",
            30: "你不再计算时间，只是静默地存在着...",
            40: "这片土地开始接纳你了。你感到前所未有的安宁...",
        }
        return {
            "msg": msgs.get(player.penance_ticks, ""),
            "忏悔进度": f"{player.penance_ticks}/{PENANCE_TICKS_REQUIRED}",
            "忏悔完成": False,
        }

    if player.penance_ticks >= PENANCE_TICKS_REQUIRED:
        player.red_name = False
        player.same_category_kills = 0
        player.penance_ticks = 0
        return {
            "msg": "一道清光从天而降——罪业已消，你获得了新生。你不再是红名了。",
            "忏悔完成": True,
        }

    return {"msg": "", "忏悔完成": False}


def reset_penance_on_attack(player: Player) -> dict:
    """攻击行为打断忏悔"""
    if not hasattr(player, 'red_name') or not player.red_name:
        return {"打断": False}

    if hasattr(player, 'penance_ticks') and player.penance_ticks > 0:
        player.penance_ticks = 0
        return {
            "打断": True,
            "msg": "你的攻击行为打断了忏悔，内心的躁动重新涌起...",
        }

    return {"打断": False}


def sense_red_name(player: Player, all_players: list) -> dict:
    """感知附近红名玩家（心灵系天赋可感知）"""
    red_nearby = []
    for other in all_players:
        if other.id == player.id:
            continue
        if hasattr(other, 'red_name') and other.red_name:
            # 大致方向提示（简化：随机一个方向）
            directions = ["北方", "南方", "东方", "西方", "东北方", "西北方", "东南方", "西南方"]
            direction = random.choice(directions)
            red_nearby.append({
                "msg": f"你感到{direction}传来一股血腥气息...",
                "红名物种": other.species.value if hasattr(other.species, 'value') else str(other.species),
            })

    if not red_nearby:
        return {"感知到红名": False, "msg": ""}

    return {
        "感知到红名": True,
        "数量": len(red_nearby),
        "信息": red_nearby,
    }


# ---------- 地图移动系统 ----------


def get_available_moves(player_id: str, map_region: str) -> dict:
    """获取当前地图可前往的地点"""
    if map_region not in MAP_CONNECTIONS:
        return {"当前地图": map_region, "可前往": []}

    from app.database import load_player as db_load
    player = db_load(player_id)
    explored = player.explored_maps if player and hasattr(player, 'explored_maps') else [map_region]
    if map_region not in explored:
        explored.append(map_region)

    moves = []
    for dest in MAP_CONNECTIONS[map_region]:
        if dest in explored:
            moves.append({"名称": dest, "已探索": True})
        else:
            moves.append({"名称": "???", "真实名称": dest, "已探索": False})

    return {
        "当前地图": map_region,
        "可前往": moves,
    }


def move_to_map(player: Player, target_map: str) -> dict:
    """移动到目标地图"""
    current = player.current_map or "城郊青草地"
    if current not in MAP_CONNECTIONS:
        return {"msg": f"你无法从 {current} 移动。", "成功": False}

    if target_map not in MAP_CONNECTIONS[current]:
        return {"msg": f"从 {current} 无法前往 {target_map}。", "成功": False}

    player.current_map = target_map
    explore_map_node(player, target_map)

    return {
        "msg": f"你离开了 {current}，前往 {target_map}。",
        "之前": current,
        "当前地图": target_map,
        "成功": True,
    }


# ---------- 商店营业模式 ----------
# 营业挂单存储：{地图名: [{玩家ID, 物种, 商品列表}]}
_shop_stalls: dict[str, list] = {}


def open_stall(player: Player, items: list) -> dict:
    """开启营业：挂出道具兑换"""

    species_name = player.species.value if hasattr(player.species, 'value') else str(player.species)
    if species_name not in STALL_ELIGIBLE_SPECIES:
        return {"msg": f"{species_name}不适合营业，只有特定物种才能当商店NPC。", "成功": False}

    # 检查背包是否有这些道具
    inventory = getattr(player, 'inventory', {}) or {}
    stall_items = []
    for item in items:
        item_name = item.get("名称", "")
        quantity = item.get("数量", 1)
        price = item.get("价格", "野果x1")
        if inventory.get(item_name, 0) >= quantity:
            inventory[item_name] -= quantity
            if inventory[item_name] <= 0:
                del inventory[item_name]
            stall_items.append({"名称": item_name, "价格": price, "数量": quantity})
        else:
            return {"msg": f"背包中 {item_name} 不足，无法挂出。", "成功": False}

    player.inventory = inventory

    # 添加到营业列表
    current_map = player.current_map or "城郊青草地"
    if current_map not in _shop_stalls:
        _shop_stalls[current_map] = []

    _shop_stalls[current_map].append({
        "玩家ID": player.id,
        "物种": player.species.value if hasattr(player.species, 'value') else str(player.species),
        "商品": stall_items,
    })

    return {
        "msg": f"你在{current_map}开启了营业，挂出了 {len(stall_items)} 种商品。",
        "挂出商品": stall_items,
        "成功": True,
    }


def close_stall(player: Player) -> dict:
    """关闭营业，退回未售出的商品"""
    map_name = player.current_map or "城郊青草地"

    if map_name not in _shop_stalls:
        return {"msg": "你没有在营业。", "成功": False}

    # 找到该玩家的摊位
    stall = None
    for s in _shop_stalls[map_name]:
        if s["玩家ID"] == player.id:
            stall = s
            break

    if not stall:
        return {"msg": "你没有在营业。", "成功": False}

    # 退回商品
    inventory = getattr(player, 'inventory', {}) or {}
    for item in stall["商品"]:
        inventory[item["名称"]] = inventory.get(item["名称"], 0) + item["数量"]
    player.inventory = inventory

    _shop_stalls[map_name].remove(stall)

    return {
        "msg": f"你关闭了营业，未售出的商品已退回背包。",
        "退回商品": stall["商品"],
        "成功": True,
    }


def get_stall_items(map_name: str) -> list:
    """获取某地图所有营业玩家的商品"""
    stalls = _shop_stalls.get(map_name, [])
    result = []
    for stall in stalls:
        for item in stall["商品"]:
            result.append({
                "名称": item["名称"],
                "价格": item["价格"],
                "卖家": stall["物种"],
            })
    return result


# ---------- 地图迷雾 ----------
def explore_map_node(player: Player, map_name: str) -> dict:
    """探索地图节点，周围相连地图变为可见"""
    if not hasattr(player, 'explored_maps'):
        player.explored_maps = []

    if map_name not in player.explored_maps:
        player.explored_maps.append(map_name)

    # 获取周围相连地图
    connections = MAP_CONNECTIONS.get(map_name, [])

    # 周围地图标记为"可见"（可以前往）
    visible = []
    for conn in connections:
        if conn not in player.explored_maps:
            visible.append(conn)

    return {
        "当前地图": map_name,
        "已探索": player.explored_maps,
        "新可见": visible,
    }


def get_visible_maps(player: Player, current_map: str) -> dict:
    """获取当前可见的地图"""
    if not hasattr(player, 'explored_maps'):
        player.explored_maps = []

    connections = MAP_CONNECTIONS.get(current_map, [])

    # 可见地图 = 已探索 + 当前地图的相邻地图
    visible = list(set(player.explored_maps + connections))

    # 未探索的相邻地图（迷雾）
    fog = [m for m in connections if m not in player.explored_maps]

    return {
        "当前地图": current_map,
        "已探索": player.explored_maps,
        "可见地图": visible,
        "迷雾中的地图": fog,
    }


# ---------- 任务系统 ----------
QUESTS = {
    "初来乍到": {"条件": "create", "描述": "降临众生之域", "奖励": {}, "完成提示": "你降临在这片众生之域。"},
    "初次探索": {"条件": "explore", "目标次数": 1, "描述": "探索周围环境", "奖励": {"exp": 20},
                 "完成提示": "你探索了周围的环境，对这个新世界有了初步的了解。"},
    "收集物资": {"条件": "inventory", "目标种类": 3, "描述": "收集3种不同物资", "奖励": {"净水": 2},
                 "完成提示": "你收集了多种物资，背包渐渐充实起来。"},
    "安营扎寨": {"条件": "build", "描述": "建造简易营地", "奖励": {"木材": 5},
                 "完成提示": "你建起了简易营地，终于有了遮风挡雨的地方。"},
    "初次战斗": {"条件": "battle", "目标次数": 1, "描述": "经历第一场战斗", "奖励": {"exp": 50},
                 "完成提示": "你经历了第一场战斗，开始懂得在这个世界生存的法则。"},
}


def init_quests(player: Player):
    """初始化任务进度"""
    if not hasattr(player, 'quests'):
        player.quests = {}
    for name, q in QUESTS.items():
        if name not in player.quests:
            player.quests[name] = {"完成": False, "进度": 0}


def check_quest(player: Player, action: str) -> list:
    """检查并更新任务，返回完成的任务列表"""
    if not hasattr(player, 'quests'):
        init_quests(player)

    completed = []
    for name, q in QUESTS.items():
        if player.quests[name]["完成"]:
            continue
        if q["条件"] == action:
            player.quests[name]["进度"] += 1
            target = q.get("目标次数", q.get("目标种类", 1))
            if player.quests[name]["进度"] >= target:
                player.quests[name]["完成"] = True
                completed.append(name)

    return completed


def get_quest_reward(player: Player, quest_name: str) -> dict:
    """领取任务奖励"""
    q = QUESTS.get(quest_name)
    if not q:
        return {"成功": False, "msg": "任务不存在"}
    if not player.quests.get(quest_name, {}).get("完成"):
        return {"成功": False, "msg": "任务未完成"}

    rewards = q["奖励"]
    for item, qty in rewards.items():
        if item == "exp":
            add_exp(player, qty)
        else:
            add_to_inventory(player, item, qty)

    return {"成功": True, "msg": q["完成提示"], "奖励": rewards}

