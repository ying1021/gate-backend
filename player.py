from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field

from app.core.config import Species, SpeciesCategory


# ---------- 天赋枚举 ----------
class Talent(str, Enum):
    SPIRIT = "生灵系"
    CONTROL = "御灵系"
    CREATION = "造物系"
    SPACE = "空间系"
    MIND = "心灵系"
    SEAL = "锁御系"


# ---------- 天气枚举 ----------
class Weather(str, Enum):
    SUNNY = "晴天"
    SCORCHING = "酷暑"
    COLD_WAVE = "寒潮"
    RAINSTORM = "暴雨"
    FOG = "大雾"
    GALE = "狂风"
    PLUM_RAIN = "梅雨"


# ---------- 核心：玩家生存属性 ----------
class VitalStats(BaseModel):
    vitality: float = Field(default=100.0, alias="生命机能")
    stamina: float = Field(default=100.0, alias="体力耐力")
    satiety: float = Field(default=100.0, alias="饱腹值")
    sanity: float = Field(default=100.0, alias="精神状态")


# ---------- 部位损伤状态 ----------
class InjuryState(BaseModel):
    skin_laceration: float = 0.0
    fracture: float = 0.0
    blood_loss: float = 0.0
    poison: float = 0.0
    asphyxia: float = 0.0
    frostbite: float = 0.0
    burn: float = 0.0
    sensory_damage: float = 0.0


# ---------- 玩家完整状态模型 ----------
class Player(BaseModel):
    id: str
    species: Species
    level: int = 1
    talent: Optional[Talent] = None
    vital: VitalStats = VitalStats()
    injury: InjuryState = InjuryState()
    exp: float = 0.0
    is_online: bool = True
    inventory: dict = {}  # 背包：{道具名称: 数量}
    current_map: Optional[str] = None
    settlement: dict = {}
    debuffs: list = []
    instance_ticks: int = 0
    red_name: bool = False
    same_category_kills: int = 0
    penance_ticks: int = 0
    explored_maps: list = []  # 已探索的地图列表
    plant_growth: dict = {"阶段": "种子", "进度": 0, "总Tick": 0, "已收获": False}
    specializations: dict = {
        "气候抗性": 0,
        "水域适应": 0,
        "体质强化": 0,
        "生态适应": 0,
        "生存博弈": 0,
        "野外捕猎": 0,
    }
    spec_points: int = 0  # 可用专精点数

    @property
    def category(self) -> SpeciesCategory:
        """自动获取所属大类，用于适配地形和天气"""
        from app.core.config import SPECIES_TO_CATEGORY
        return SPECIES_TO_CATEGORY[self.species]