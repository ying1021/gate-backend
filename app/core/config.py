from enum import Enum


class Terrain(str, Enum):
    PLAINS = "平原"
    FOREST = "森林"
    MOUNTAIN = "山地"
    SWAMP = "沼泽"
    DESERT = "沙漠"
    TUNDRA = "冻土"
    FRESHWATER = "淡水水域"
    SALTWATER = "海水水域"
    SEWAGE = "污水水域"
    SHALLOW = "浅水水域"


# ---------- 物种大类枚举 ----------
class SpeciesCategory(str, Enum):
    HERBIVORE = "草食性动物"
    CARNIVORE = "肉食性动物"
    OMNIVORE = "杂食性动物"
    INVERTEBRATE = "无脊椎动物"
    AMPHIBIAN = "两栖类动物"
    AQUATIC = "水生动物"
    PLANT = "植物类生物"
    FUNGI = "真菌类生物"
    BACTERIA = "细菌类生物"
    ANCIENT = "远古类生物"
    UNDEAD = "亡灵类"
    MYTHICAL = "神兽类"
    ALIEN = "外星生物"


# ---------- 具体物种枚举 ----------
class Species(str, Enum):
    # 草食性动物
    RABBIT = "兔"
    DEER = "鹿"
    SHEEP = "羊"
    HORSE = "马"
    COW = "牛"
    ELEPHANT = "象"
    GIRAFFE = "长颈鹿"
    HIPPO = "河马"
    SLOTH = "树懒"
    KOALA = "考拉"
    # 肉食性动物
    TIGER = "虎"
    LION = "狮"
    WOLF = "狼"
    LEOPARD = "豹"
    EAGLE = "鹰"
    CROCODILE = "鳄鱼"
    HYENA = "鬣狗"
    OTTER = "水獭"
    SHARK = "鲨鱼"
    SNAKE = "蛇"
    # 杂食性动物
    BEAR = "熊"
    PIG = "猪"
    FOX = "狐"
    RACCOON = "浣熊"
    MOUSE = "鼠"
    GORILLA = "猩猩"
    CROW = "乌鸦"
    WILDCAT = "野猫"
    HEDGEHOG = "刺猬"
    BADGER = "獾"
    # 无脊椎动物
    CENTIPEDE = "蜈蚣"
    SCORPION = "蝎"
    SPIDER = "蜘蛛"
    MANTIS = "螳螂"
    BEETLE = "甲虫"
    ANT = "蚁"
    BEE = "蜜蜂"
    DRAGONFLY = "蜻蜓"
    JELLYFISH = "水母"
    OCTOPUS = "章鱼"
    DUNG_BEETLE = "屎壳郎"
    EARTHWORM = "蚯蚓"
    # 两栖类动物
    FROG = "蛙"
    TOAD = "蟾蜍"
    NEWT = "蝾螈"
    GIANT_SALAMANDER = "大鲵"
    TREE_FROG = "树蛙"
    POISON_DART_FROG = "箭毒蛙"
    RAIN_FROG = "雨蛙"
    MUD_PUPPY = "泥螈"
    # 水生动物
    GRASS_CARP = "草鱼"
    CARP = "鲤鱼"
    TUNA = "金枪鱼"
    WHALE = "鲸"
    DOLPHIN = "海豚"
    LOBSTER = "龙虾"
    CRAB = "河蟹"
    CLAM = "蛤蜊"
    SEA_TURTLE = "海龟"
    # 植物类生物
    OAK = "橡树"
    BAMBOO = "竹"
    ROSE = "蔷薇"
    VINE = "藤蔓"
    CACTUS = "仙人掌"
    MUSHROOM = "菌菇"
    KELP = "海带"
    REED = "芦苇"
    PITCHER_PLANT = "猪笼草"
    MIMOSA = "含羞草"
    VENUS_FLYTRAP = "捕蝇草"
    GINKGO = "银杏"
    # 真菌类生物
    SHIITAKE = "香菇"
    REISHI = "灵芝"
    WOOD_EAR = "木耳"
    SNOW_FUNGUS = "银耳"
    CORDYCEPS = "冬虫夏草"
    FLY_AGARIC = "毒蝇伞"
    PUFFBALL = "马勃菌"
    # 细菌类生物
    E_COLI = "大肠杆菌"
    LACTOBACILLUS = "乳酸菌"
    CYANOBACTERIA = "蓝藻"
    BACTERIOPHAGE = "噬菌体"
    YEAST = "酵母菌"
    # 远古类生物
    DINOSAUR = "恐龙"
    MAMMOTH = "猛犸象"
    SABERTOOTH = "剑齿虎"
    TRILOBITE = "三叶虫"
    AMMONITE = "菊石"
    PTEROSAUR = "翼龙"
    # 亡灵类（概率权重低）
    SKELETON = "骷髅"
    GHOST = "幽灵"
    ZOMBIE = "僵尸"
    GHOUL = "食尸鬼"
    LICH = "巫妖"
    VAMPIRE = "吸血鬼"
    REVENANT = "还魂尸"
    # 神兽类（概率权重低）
    TRUE_DRAGON = "真龙"
    PHOENIX = "凤凰"
    QILIN = "麒麟"
    XUANWU = "玄武"
    WHITE_TIGER = "白虎"
    VERMILION_BIRD = "朱雀"
    AZURE_DRAGON = "青龙"
    NINE_TAILED_FOX = "九尾狐"
    TAOTIE = "饕餮"
    # 外星生物（概率权重低）
    XENOMORPH = "异形"
    PREDATOR = "铁血战士"
    ET = "E.T."
    MARTIAN = "火星人"
    SILICON_LIFE = "硅基生命体"
    ENERGY_BEING = "能量体"


# 物种 → 大类的映射表
SPECIES_TO_CATEGORY = {
    # 草食性动物
    Species.RABBIT: SpeciesCategory.HERBIVORE,
    Species.DEER: SpeciesCategory.HERBIVORE,
    Species.SHEEP: SpeciesCategory.HERBIVORE,
    Species.HORSE: SpeciesCategory.HERBIVORE,
    Species.COW: SpeciesCategory.HERBIVORE,
    Species.ELEPHANT: SpeciesCategory.HERBIVORE,
    Species.GIRAFFE: SpeciesCategory.HERBIVORE,
    Species.HIPPO: SpeciesCategory.HERBIVORE,
    Species.SLOTH: SpeciesCategory.HERBIVORE,
    Species.KOALA: SpeciesCategory.HERBIVORE,
    # 肉食性动物
    Species.TIGER: SpeciesCategory.CARNIVORE,
    Species.LION: SpeciesCategory.CARNIVORE,
    Species.WOLF: SpeciesCategory.CARNIVORE,
    Species.LEOPARD: SpeciesCategory.CARNIVORE,
    Species.EAGLE: SpeciesCategory.CARNIVORE,
    Species.CROCODILE: SpeciesCategory.CARNIVORE,
    Species.HYENA: SpeciesCategory.CARNIVORE,
    Species.OTTER: SpeciesCategory.CARNIVORE,
    Species.SHARK: SpeciesCategory.CARNIVORE,
    Species.SNAKE: SpeciesCategory.CARNIVORE,
    # 杂食性动物
    Species.BEAR: SpeciesCategory.OMNIVORE,
    Species.PIG: SpeciesCategory.OMNIVORE,
    Species.FOX: SpeciesCategory.OMNIVORE,
    Species.RACCOON: SpeciesCategory.OMNIVORE,
    Species.MOUSE: SpeciesCategory.OMNIVORE,
    Species.GORILLA: SpeciesCategory.OMNIVORE,
    Species.CROW: SpeciesCategory.OMNIVORE,
    Species.WILDCAT: SpeciesCategory.OMNIVORE,
    Species.HEDGEHOG: SpeciesCategory.OMNIVORE,
    Species.BADGER: SpeciesCategory.OMNIVORE,
    # 无脊椎动物
    Species.CENTIPEDE: SpeciesCategory.INVERTEBRATE,
    Species.SCORPION: SpeciesCategory.INVERTEBRATE,
    Species.SPIDER: SpeciesCategory.INVERTEBRATE,
    Species.MANTIS: SpeciesCategory.INVERTEBRATE,
    Species.BEETLE: SpeciesCategory.INVERTEBRATE,
    Species.ANT: SpeciesCategory.INVERTEBRATE,
    Species.BEE: SpeciesCategory.INVERTEBRATE,
    Species.DRAGONFLY: SpeciesCategory.INVERTEBRATE,
    Species.JELLYFISH: SpeciesCategory.INVERTEBRATE,
    Species.OCTOPUS: SpeciesCategory.INVERTEBRATE,
    Species.DUNG_BEETLE: SpeciesCategory.INVERTEBRATE,
    Species.EARTHWORM: SpeciesCategory.INVERTEBRATE,
    # 两栖类动物
    Species.FROG: SpeciesCategory.AMPHIBIAN,
    Species.TOAD: SpeciesCategory.AMPHIBIAN,
    Species.NEWT: SpeciesCategory.AMPHIBIAN,
    Species.GIANT_SALAMANDER: SpeciesCategory.AMPHIBIAN,
    Species.TREE_FROG: SpeciesCategory.AMPHIBIAN,
    Species.POISON_DART_FROG: SpeciesCategory.AMPHIBIAN,
    Species.RAIN_FROG: SpeciesCategory.AMPHIBIAN,
    Species.MUD_PUPPY: SpeciesCategory.AMPHIBIAN,
    # 水生动物
    Species.GRASS_CARP: SpeciesCategory.AQUATIC,
    Species.CARP: SpeciesCategory.AQUATIC,
    Species.TUNA: SpeciesCategory.AQUATIC,
    Species.WHALE: SpeciesCategory.AQUATIC,
    Species.DOLPHIN: SpeciesCategory.AQUATIC,
    Species.LOBSTER: SpeciesCategory.AQUATIC,
    Species.CRAB: SpeciesCategory.AQUATIC,
    Species.CLAM: SpeciesCategory.AQUATIC,
    Species.SEA_TURTLE: SpeciesCategory.AQUATIC,
    # 植物类生物
    Species.OAK: SpeciesCategory.PLANT,
    Species.BAMBOO: SpeciesCategory.PLANT,
    Species.ROSE: SpeciesCategory.PLANT,
    Species.VINE: SpeciesCategory.PLANT,
    Species.CACTUS: SpeciesCategory.PLANT,
    Species.MUSHROOM: SpeciesCategory.PLANT,
    Species.KELP: SpeciesCategory.PLANT,
    Species.REED: SpeciesCategory.PLANT,
    Species.PITCHER_PLANT: SpeciesCategory.PLANT,
    Species.MIMOSA: SpeciesCategory.PLANT,
    Species.VENUS_FLYTRAP: SpeciesCategory.PLANT,
    Species.GINKGO: SpeciesCategory.PLANT,
    # 真菌类生物
    Species.SHIITAKE: SpeciesCategory.FUNGI,
    Species.REISHI: SpeciesCategory.FUNGI,
    Species.WOOD_EAR: SpeciesCategory.FUNGI,
    Species.SNOW_FUNGUS: SpeciesCategory.FUNGI,
    Species.CORDYCEPS: SpeciesCategory.FUNGI,
    Species.FLY_AGARIC: SpeciesCategory.FUNGI,
    Species.PUFFBALL: SpeciesCategory.FUNGI,
    # 细菌类生物
    Species.E_COLI: SpeciesCategory.BACTERIA,
    Species.LACTOBACILLUS: SpeciesCategory.BACTERIA,
    Species.CYANOBACTERIA: SpeciesCategory.BACTERIA,
    Species.BACTERIOPHAGE: SpeciesCategory.BACTERIA,
    Species.YEAST: SpeciesCategory.BACTERIA,
    # 远古类生物
    Species.DINOSAUR: SpeciesCategory.ANCIENT,
    Species.MAMMOTH: SpeciesCategory.ANCIENT,
    Species.SABERTOOTH: SpeciesCategory.ANCIENT,
    Species.TRILOBITE: SpeciesCategory.ANCIENT,
    Species.AMMONITE: SpeciesCategory.ANCIENT,
    Species.PTEROSAUR: SpeciesCategory.ANCIENT,
    # 亡灵类
    Species.SKELETON: SpeciesCategory.UNDEAD,
    Species.GHOST: SpeciesCategory.UNDEAD,
    Species.ZOMBIE: SpeciesCategory.UNDEAD,
    Species.GHOUL: SpeciesCategory.UNDEAD,
    Species.LICH: SpeciesCategory.UNDEAD,
    Species.VAMPIRE: SpeciesCategory.UNDEAD,
    Species.REVENANT: SpeciesCategory.UNDEAD,
    # 神兽类
    Species.TRUE_DRAGON: SpeciesCategory.MYTHICAL,
    Species.PHOENIX: SpeciesCategory.MYTHICAL,
    Species.QILIN: SpeciesCategory.MYTHICAL,
    Species.XUANWU: SpeciesCategory.MYTHICAL,
    Species.WHITE_TIGER: SpeciesCategory.MYTHICAL,
    Species.VERMILION_BIRD: SpeciesCategory.MYTHICAL,
    Species.AZURE_DRAGON: SpeciesCategory.MYTHICAL,
    Species.NINE_TAILED_FOX: SpeciesCategory.MYTHICAL,
    Species.TAOTIE: SpeciesCategory.MYTHICAL,
    # 外星生物
    Species.XENOMORPH: SpeciesCategory.ALIEN,
    Species.PREDATOR: SpeciesCategory.ALIEN,
    Species.ET: SpeciesCategory.ALIEN,
    Species.MARTIAN: SpeciesCategory.ALIEN,
    Species.SILICON_LIFE: SpeciesCategory.ALIEN,
    Species.ENERGY_BEING: SpeciesCategory.ALIEN,
}

# 物种适配地形表（用大类映射）
# 物种适配地形表（用新大类映射）
SPECIES_TERRAIN = {
    SpeciesCategory.HERBIVORE: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.5,
        Terrain.SWAMP: 0.5, Terrain.DESERT: 0.3, Terrain.TUNDRA: 0.3,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.1, Terrain.SEWAGE: 0.1,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.CARNIVORE: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.8,
        Terrain.SWAMP: 0.5, Terrain.DESERT: 0.3, Terrain.TUNDRA: 0.4,
        Terrain.FRESHWATER: 0.3, Terrain.SALTWATER: 0.1, Terrain.SEWAGE: 0.1,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.OMNIVORE: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.6,
        Terrain.SWAMP: 0.6, Terrain.DESERT: 0.3, Terrain.TUNDRA: 0.3,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.1, Terrain.SEWAGE: 0.1,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.INVERTEBRATE: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.5,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 0.5, Terrain.TUNDRA: 0.1,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.3, Terrain.SEWAGE: 0.5,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.AMPHIBIAN: {
        Terrain.PLAINS: 0.5, Terrain.FOREST: 0.8, Terrain.MOUNTAIN: 0.3,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 0.0, Terrain.TUNDRA: 0.1,
        Terrain.FRESHWATER: 1.0, Terrain.SALTWATER: 0.1, Terrain.SEWAGE: 0.3,
        Terrain.SHALLOW: 1.0,
    },
    SpeciesCategory.AQUATIC: {
        Terrain.PLAINS: 0.0, Terrain.FOREST: 0.0, Terrain.MOUNTAIN: 0.0,
        Terrain.SWAMP: 0.5, Terrain.DESERT: 0.0, Terrain.TUNDRA: 0.0,
        Terrain.FRESHWATER: 1.0, Terrain.SALTWATER: 1.0, Terrain.SEWAGE: 0.3,
        Terrain.SHALLOW: 0.8,
    },
    SpeciesCategory.PLANT: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.5,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 0.1, Terrain.TUNDRA: 0.1,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.1, Terrain.SEWAGE: 0.1,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.FUNGI: {
        Terrain.PLAINS: 0.5, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.5,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 0.0, Terrain.TUNDRA: 0.0,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.3, Terrain.SEWAGE: 0.8,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.BACTERIA: {
        Terrain.PLAINS: 0.8, Terrain.FOREST: 0.8, Terrain.MOUNTAIN: 0.5,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 0.5, Terrain.TUNDRA: 0.3,
        Terrain.FRESHWATER: 1.0, Terrain.SALTWATER: 0.8, Terrain.SEWAGE: 1.0,
        Terrain.SHALLOW: 0.8,
    },
    SpeciesCategory.ANCIENT: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 0.8,
        Terrain.SWAMP: 0.8, Terrain.DESERT: 0.5, Terrain.TUNDRA: 0.5,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.3, Terrain.SEWAGE: 0.5,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.UNDEAD: {
        Terrain.PLAINS: 0.8, Terrain.FOREST: 0.8, Terrain.MOUNTAIN: 0.7,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 0.8, Terrain.TUNDRA: 0.8,
        Terrain.FRESHWATER: 0.3, Terrain.SALTWATER: 0.3, Terrain.SEWAGE: 1.0,
        Terrain.SHALLOW: 0.5,
    },
    SpeciesCategory.MYTHICAL: {
        Terrain.PLAINS: 1.0, Terrain.FOREST: 1.0, Terrain.MOUNTAIN: 1.0,
        Terrain.SWAMP: 1.0, Terrain.DESERT: 1.0, Terrain.TUNDRA: 1.0,
        Terrain.FRESHWATER: 1.0, Terrain.SALTWATER: 1.0, Terrain.SEWAGE: 0.8,
        Terrain.SHALLOW: 1.0,
    },
    SpeciesCategory.ALIEN: {
        Terrain.PLAINS: 0.8, Terrain.FOREST: 0.8, Terrain.MOUNTAIN: 0.8,
        Terrain.SWAMP: 0.5, Terrain.DESERT: 1.0, Terrain.TUNDRA: 0.8,
        Terrain.FRESHWATER: 0.5, Terrain.SALTWATER: 0.5, Terrain.SEWAGE: 0.5,
        Terrain.SHALLOW: 0.5,
    },
}

# ---------- 天气对各大类物种的影响系数 ----------
# 系数含义：
#   >1.0  增益（消耗减慢）
#   1.0   无影响
#   0.5~0.9  轻度负面
#   <0.5  严重负面
WEATHER_EFFECTS = {
    "晴天": {
        "草食性动物": 1.0, "肉食性动物": 1.0, "杂食性动物": 1.0,
        "无脊椎动物": 1.1, "两栖类动物": 1.0, "水生动物": 1.0,
        "植物类生物": 1.2, "真菌类生物": 1.0, "细菌类生物": 1.0,
        "远古类生物": 1.0, "亡灵类": 0.8, "神兽类": 1.0, "外星生物": 1.0,
    },
    "酷暑": {
        "草食性动物": 0.7, "肉食性动物": 0.6, "杂食性动物": 0.7,
        "无脊椎动物": 1.1, "两栖类动物": 0.5, "水生动物": 0.6,
        "植物类生物": 0.5, "真菌类生物": 0.7, "细菌类生物": 1.2,
        "远古类生物": 0.6, "亡灵类": 0.5, "神兽类": 0.9, "外星生物": 0.8,
    },
    "寒潮": {
        "草食性动物": 0.5, "肉食性动物": 0.7, "杂食性动物": 0.5,
        "无脊椎动物": 0.3, "两栖类动物": 0.2, "水生动物": 0.5,
        "植物类生物": 0.4, "真菌类生物": 0.3, "细菌类生物": 0.4,
        "远古类生物": 0.5, "亡灵类": 0.9, "神兽类": 1.1, "外星生物": 0.6,
    },
    "暴雨": {
        "草食性动物": 0.7, "肉食性动物": 0.9, "杂食性动物": 0.7,
        "无脊椎动物": 0.4, "两栖类动物": 1.2, "水生动物": 1.2,
        "植物类生物": 0.9, "真菌类生物": 1.3, "细菌类生物": 1.2,
        "远古类生物": 0.8, "亡灵类": 0.6, "神兽类": 0.9, "外星生物": 0.7,
    },
    "大雾": {
        "草食性动物": 0.7, "肉食性动物": 0.9, "杂食性动物": 0.7,
        "无脊椎动物": 0.9, "两栖类动物": 1.0, "水生动物": 1.0,
        "植物类生物": 1.0, "真菌类生物": 1.0, "细菌类生物": 1.0,
        "远古类生物": 0.9, "亡灵类": 1.3, "神兽类": 1.0, "外星生物": 0.9,
    },
    "狂风": {
        "草食性动物": 0.5, "肉食性动物": 0.8, "杂食性动物": 0.5,
        "无脊椎动物": 0.3, "两栖类动物": 0.6, "水生动物": 0.9,
        "植物类生物": 0.6, "真菌类生物": 0.5, "细菌类生物": 0.6,
        "远古类生物": 0.7, "亡灵类": 0.8, "神兽类": 0.9, "外星生物": 0.8,
    },
    "梅雨": {
        "草食性动物": 0.7, "肉食性动物": 0.8, "杂食性动物": 0.7,
        "无脊椎动物": 0.6, "两栖类动物": 1.1, "水生动物": 1.1,
        "植物类生物": 0.7, "真菌类生物": 1.4, "细菌类生物": 1.3,
        "远古类生物": 0.7, "亡灵类": 0.9, "神兽类": 0.8, "外星生物": 0.7,
    },
}

# ---------- 地图系统 ----------

class MapType(str, Enum):
    """地图类型"""
    SPAWN = "新手初生区"
    TRAINING = "日常练级区"
    CITY = "都市人文区"
    INSTANCE = "单人秘境"
    ULTIMATE = "终极特殊地图"


class MapRegion(str, Enum):
    """具体地图"""
    # 新手初生区
    SUBURBAN_MEADOW = "城郊青草地"
    OLD_TOWN_ALLEY = "老城区巷弄"
    SUBURBAN_FOREST = "近郊小树林"
    # 日常练级区
    MAPLE_FOREST = "漫山枫林"
    CLOUD_VALLEY = "云雾山谷"
    REED_LAKE = "湖滨芦苇荡"
    GOBIDESERT = "荒寂戈壁滩"
    SNOW_RIDGE = "寒色雪岭"
    # 都市人文区（禁止战斗）
    CITY_STREET = "都市商业街"
    MOUNTAIN_TEMPLE = "山间古寺遗址"
    SEA_BRIDGE = "跨海长桥"
    # 单人秘境
    ILLUSION_FOREST = "幻境心林"
    TIME_VALLEY = "时光溪谷"
    SHIPWRECK = "沉船深海遗迹"
    # 终极特殊地图
    GATE_PORTAL = "众生之门玄关"
    CLOUD_ISLANDS = "云端孤岛群"


# 地图→类型 映射
MAP_TO_TYPE = {
    MapRegion.SUBURBAN_MEADOW: MapType.SPAWN,
    MapRegion.OLD_TOWN_ALLEY: MapType.SPAWN,
    MapRegion.SUBURBAN_FOREST: MapType.SPAWN,
    MapRegion.MAPLE_FOREST: MapType.TRAINING,
    MapRegion.CLOUD_VALLEY: MapType.TRAINING,
    MapRegion.REED_LAKE: MapType.TRAINING,
    MapRegion.GOBIDESERT: MapType.TRAINING,
    MapRegion.SNOW_RIDGE: MapType.TRAINING,
    MapRegion.CITY_STREET: MapType.CITY,
    MapRegion.MOUNTAIN_TEMPLE: MapType.CITY,
    MapRegion.SEA_BRIDGE: MapType.CITY,
    MapRegion.ILLUSION_FOREST: MapType.INSTANCE,
    MapRegion.TIME_VALLEY: MapType.INSTANCE,
    MapRegion.SHIPWRECK: MapType.INSTANCE,
    MapRegion.GATE_PORTAL: MapType.ULTIMATE,
    MapRegion.CLOUD_ISLANDS: MapType.ULTIMATE,
}

# 地图→适配地形 映射（用于环境消耗计算）
MAP_TO_TERRAIN = {
    MapRegion.SUBURBAN_MEADOW: Terrain.PLAINS,
    MapRegion.OLD_TOWN_ALLEY: Terrain.PLAINS,
    MapRegion.SUBURBAN_FOREST: Terrain.FOREST,
    MapRegion.MAPLE_FOREST: Terrain.FOREST,
    MapRegion.CLOUD_VALLEY: Terrain.MOUNTAIN,
    MapRegion.REED_LAKE: Terrain.SHALLOW,
    MapRegion.GOBIDESERT: Terrain.DESERT,
    MapRegion.SNOW_RIDGE: Terrain.TUNDRA,
    MapRegion.CITY_STREET: Terrain.PLAINS,
    MapRegion.MOUNTAIN_TEMPLE: Terrain.MOUNTAIN,
    MapRegion.SEA_BRIDGE: Terrain.SALTWATER,
    MapRegion.ILLUSION_FOREST: Terrain.FOREST,
    MapRegion.TIME_VALLEY: Terrain.MOUNTAIN,
    MapRegion.SHIPWRECK: Terrain.SALTWATER,
    MapRegion.GATE_PORTAL: Terrain.MOUNTAIN,
    MapRegion.CLOUD_ISLANDS: Terrain.PLAINS,
}

# 都市区（禁止战斗，违者踢出+冷却）
CITY_MAPS = {MapRegion.CITY_STREET, MapRegion.MOUNTAIN_TEMPLE, MapRegion.SEA_BRIDGE}

# 新手区列表
SPAWN_MAPS = [MapRegion.SUBURBAN_MEADOW, MapRegion.OLD_TOWN_ALLEY, MapRegion.SUBURBAN_FOREST]

# 非新手区（低概率出生地）
NON_SPAWN_MAPS = [
    m for m in MapRegion
    if m not in SPAWN_MAPS and MAP_TO_TYPE[m] != MapType.INSTANCE
]

# 各新手区的地图叙事描述
SPAWN_DESCRIPTIONS = {
    MapRegion.SUBURBAN_MEADOW: "城郊青草地——普通草坪、小河流淌、林荫小道蜿蜒其间。长椅静立路旁，路灯温柔地亮着，都市郊外安静祥和。温顺小灵物在草丛间出没，这是萌新落脚的好地方。",
    MapRegion.OLD_TOWN_ALLEY: "老城区巷弄——矮旧的居民楼鳞次栉比，窄巷子四通八达。小卖部的招牌嘎吱作响，老街道上弥漫着人间烟火的气息。人类和普通妖精在这里安静地开始旅程。",
    MapRegion.SUBURBAN_FOREST: "近郊小树林——小片树林郁郁葱葱，野花坡上星星点点地开着不知名的花。石径蜿蜒深入，氛围治愈。低阶灵草随处可见，适合新手独自练手。",
}

# 非新手区的叙事描述（小概率出生时用）
NON_SPAWN_DESCRIPTIONS = {
    MapRegion.MAPLE_FOREST: "漫山枫林——满山红枫如火焰燃烧，山间小溪淙淙流过青石崖台。这里是木系、风系修炼的福地，但对你这样的新手来说，独居的灵妖们似乎不太友好...",
    MapRegion.CLOUD_VALLEY: "云雾山谷——常年薄雾缭绕，山泉瀑布从高处倾泻。隐世小山洞散发着神秘的气息。你感到自己来得太早了，这里更适合独自闭关的修行者。",
    MapRegion.REED_LAKE: "湖滨芦苇荡——大湖泊烟波浩渺，芦苇丛随风摇曳。浅滩睡莲静静绽放，水下隐约可见灵材。但水域深处传来的气息让你这个新来者有些不安。",
    MapRegion.GOBIDESERT: "荒寂戈壁滩——黄沙漫天，风蚀怪石孤零零地矗立。零星枯木诉说着此地的严酷。干燥空旷，人迹罕至，一个新手在这里生存将格外艰难。",
    MapRegion.SNOW_RIDGE: "寒色雪岭——常年飘雪，松林银装素裹。结冰的湖面倒映着灰色的天空。冰系生灵的专属地，对于不适应寒冷的你来说，每一步都是考验。",
    MapRegion.CITY_STREET: "都市商业街——现代商场林立，街道店铺灯火通明。广场花坛旁有公交站台。这里是纯安全交易区，你运气不错，虽然偏离了新手区，但至少这里不能打架...",
    MapRegion.MOUNTAIN_TEMPLE: "山间古寺遗址——废弃古寺静卧在石阶尽头，古柏苍翠。幽静庭院里落叶无声。佛系修行的好地方，你在这里可以安静地思考怎么活下去。",
    MapRegion.SEA_BRIDGE: "跨海长桥——海上大桥伸向远方，海风栈道上可以俯瞰汹涌的波涛。夜景路灯连成一线。纯风景打卡地，但一个新手在这里连练级的地方都找不到...",
    MapRegion.GATE_PORTAL: "众生之门玄关——巨大的石门矗立在前，星雾浮空缭绕，空灵如神殿。这是终极试炼的入口！你咽了咽口水，以你现在的实力，最好远远看着就好。",
    MapRegion.CLOUD_ISLANDS: "云端孤岛群——零散的浮空小岛悬在云海之中，云间栈道若隐若现。悬空石台上风声呼啸。高阶修士独自历练的地方，你感到自己渺小得像一粒尘埃。",
}

# ---------- 道具系统 ----------

class ItemRarity(str, Enum):
    COMMON = "普通"
    UNCOMMON = "精良"
    RARE = "稀有"
    EPIC = "史诗"
    LEGENDARY = "传说"
    JOKE = "彩蛋"


class ItemCategory(str, Enum):
    CONSUMABLE = "生存消耗品"
    MATERIAL = "基础材料"
    MEDICINE = "疗伤物资"
    TALISMAN = "抗性护符"
    TRAP = "陷阱道具"
    TREASURE = "稀有造物"
    JOKE_ITEM = "梗道具"


class Item(str, Enum):
    # 生存消耗品
    WILD_FRUIT = "野果"
    CLEAN_WATER = "净水"
    RAW_MEAT = "生肉"
    DRIED_FISH = "鱼干"
    HONEY = "野蜂蜜"
    BREAD = "干粮"
    # 基础材料
    WOOD = "木材"
    STONE = "石块"
    FLINT = "燧石"
    VINE_ROPE = "藤绳"
    ANIMAL_HIDE = "兽皮"
    BONE = "骨头"
    IRON_ORE = "铁矿石"
    FISHING_ROD = "简易钓竿"
    # 疗伤物资
    HERB_BANDAGE = "草药绷带"
    ANTIDOTE_HERB = "解毒草"
    HEALING_SALVE = "治疗药膏"
    BLOODSTOP_POWDER = "止血散"
    # 抗性护符
    COLD_RESIST_TALISMAN = "御寒符"
    HEAT_RESIST_TALISMAN = "避暑符"
    WATER_BREATHING_TALISMAN = "避水符"
    POISON_RESIST_TALISMAN = "抗毒符"
    # 陷阱道具
    SNARE_TRAP = "捕兽夹"
    PIT_TRAP = "陷坑"
    NET_TRAP = "捕网"
    POISON_BAIT = "毒饵"
    # 稀有造物
    MYSTERIOUS_SCROLL = "神秘古卷"
    SPIRIT_STONE = "灵石"
    PHOENIX_FEATHER = "凤凰羽毛"
    BROKEN_KEY = "断钥"
    # 梗道具
    GOLDEN_AXE = "金斧头"
    SILVER_AXE = "银斧头"
    IRON_AXE = "铁斧头"
    USELESS_BOX = "无用之盒"
    SOCKS = "另一只袜子"
    EXPIRED_COUPON = "过期优惠券"
    # 武器
    RUSTY_KNIFE = "生锈的铁刀"
    SHARP_SPEAR = "尖刺长矛"
    HUNTING_BOW = "猎弓"
    STONE_AXE = "石斧"


# 道具详细信息
ITEM_INFO = {
    Item.WILD_FRUIT: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.CONSUMABLE, "描述": "路边采摘的野果，勉强能果腹。", "效果": {"饱腹值": 10}},
    Item.CLEAN_WATER: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.CONSUMABLE, "描述": "清澈的水源，生命之源。", "效果": {"生命机能": 5, "体力耐力": 5}},
    Item.RAW_MEAT: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.CONSUMABLE, "描述": "新鲜的肉块，需要烤熟才好吃。", "效果": {"饱腹值": 25}},
    Item.DRIED_FISH: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.CONSUMABLE, "描述": "风干的鱼，耐储存。", "效果": {"饱腹值": 15}},
    Item.HONEY: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.CONSUMABLE, "描述": "金黄的野蜂蜜，甜美的能量来源。", "效果": {"饱腹值": 20, "体力耐力": 10}},
    Item.BREAD: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.CONSUMABLE, "描述": "一块干粮，朴实但管饱。", "效果": {"饱腹值": 30}},
    Item.WOOD: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MATERIAL, "描述": "普通的木材，可以用来搭建营地。", "效果": {}},
    Item.STONE: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MATERIAL, "描述": "坚硬的石头，建材和武器的基础。", "效果": {}},
    Item.FLINT: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.MATERIAL, "描述": "能打出火星的石头，生火必备。", "效果": {}},
    Item.VINE_ROPE: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MATERIAL, "描述": "坚韧的藤蔓搓成的绳索。", "效果": {}},
    Item.ANIMAL_HIDE: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MATERIAL, "描述": "动物的皮毛，保暖和制作的基础材料。", "效果": {}},
    Item.BONE: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MATERIAL, "描述": "坚硬的骨头，可加工成工具。", "效果": {}},
    Item.IRON_ORE: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.MATERIAL, "描述": "含铁的矿石，冶炼后能打造铁器。", "效果": {}},
    Item.HERB_BANDAGE: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MEDICINE, "描述": "用草药捣碎做成的简易绷带。", "效果": {"皮肉撕裂": -20}},
    Item.ANTIDOTE_HERB: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.MEDICINE, "描述": "能解大部分常见毒的草药。", "效果": {"中毒": -30}},
    Item.HEALING_SALVE: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.MEDICINE, "描述": "稀有的治疗药膏，能加速伤口愈合。", "效果": {"生命机能": 30, "骨折": -15}},
    Item.BLOODSTOP_POWDER: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.MEDICINE, "描述": "撒在伤口上能迅速止血的粉末。", "效果": {"失血": -25}},
    Item.COLD_RESIST_TALISMAN: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.TALISMAN, "描述": "散发微弱热量的护符，抵御严寒。", "效果": {"冻伤": -20}},
    Item.HEAT_RESIST_TALISMAN: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.TALISMAN, "描述": "散发清凉气息的护符，抵御酷暑。", "效果": {"灼伤": -20}},
    Item.WATER_BREATHING_TALISMAN: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.TALISMAN, "描述": "佩戴后能在水下自由呼吸。", "效果": {"窒息": -30}},
    Item.POISON_RESIST_TALISMAN: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.TALISMAN, "描述": "能中和部分毒素的护符。", "效果": {"中毒": -20}},
    Item.SNARE_TRAP: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.TRAP, "描述": "踩中就会被夹住的陷阱。", "效果": {}},
    Item.PIT_TRAP: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.TRAP, "描述": "挖一个坑，盖上树枝和土。", "效果": {}},
    Item.NET_TRAP: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.TRAP, "描述": "从天而降的网，困住猎物。", "效果": {}},
    Item.POISON_BAIT: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.TRAP, "描述": "涂了毒药的食物诱饵。", "效果": {}},
    Item.MYSTERIOUS_SCROLL: {"稀有度": ItemRarity.EPIC, "分类": ItemCategory.TREASURE, "描述": "记载着古老秘法的卷轴，散发着微光。", "效果": {}},
    Item.SPIRIT_STONE: {"稀有度": ItemRarity.EPIC, "分类": ItemCategory.TREASURE, "描述": "蕴含灵力的石头，修行者梦寐以求。", "效果": {}},
    Item.PHOENIX_FEATHER: {"稀有度": ItemRarity.LEGENDARY, "分类": ItemCategory.TREASURE, "描述": "凤凰的羽毛，传说能让人浴火重生。", "效果": {}},
    Item.BROKEN_KEY: {"稀有度": ItemRarity.LEGENDARY, "分类": ItemCategory.TREASURE, "描述": "半截断裂的钥匙，似乎连接着某个巨大的秘密...", "效果": {}},
    Item.GOLDEN_AXE: {"稀有度": ItemRarity.JOKE, "分类": ItemCategory.JOKE_ITEM, "描述": "一把金光闪闪的斧头，散发着诚实的光芒。", "效果": {}},
    Item.SILVER_AXE: {"稀有度": ItemRarity.JOKE, "分类": ItemCategory.JOKE_ITEM, "描述": "一把银光闪闪的斧头，比金的差一点但也还行。", "效果": {}},
    Item.IRON_AXE: {"稀有度": ItemRarity.JOKE, "分类": ItemCategory.JOKE_ITEM, "描述": "一把普普通通的铁斧头，就是它了。", "效果": {}},
    Item.USELESS_BOX: {"稀有度": ItemRarity.JOKE, "分类": ItemCategory.JOKE_ITEM, "描述": "一个盒子，打开后什么也没有。但盒子里写着：'惊喜！'", "效果": {}},
    Item.EXPIRED_COUPON: {"稀有度": ItemRarity.JOKE, "分类": ItemCategory.JOKE_ITEM, "描述": "一张已经过期的优惠券，上面写着'众生之门开业大酬宾，满100减5'。", "效果": {}},
    Item.RUSTY_KNIFE: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.MATERIAL, "描述": "一把生锈的铁刀，+5伤害。", "效果": {"damage_bonus": 5}},
    Item.SHARP_SPEAR: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.TRAP, "描述": "削尖的长矛，+10伤害。", "效果": {"damage_bonus": 10}},
    Item.HUNTING_BOW: {"稀有度": ItemRarity.RARE, "分类": ItemCategory.TRAP, "描述": "一把猎弓，+15伤害。", "效果": {"damage_bonus": 15}},
    Item.STONE_AXE: {"稀有度": ItemRarity.UNCOMMON, "分类": ItemCategory.MATERIAL, "描述": "沉重的石斧，+12伤害。", "效果": {"damage_bonus": 12}},
    Item.FISHING_ROD: {"稀有度": ItemRarity.COMMON, "分类": ItemCategory.TRAP, "描述": "一根简陋但能用的钓竿，可以在水域钓鱼。", "效果": {}},
}

# 地图→可探索获得的道具池
MAP_LOOT_TABLE = {
    "城郊青草地": [(Item.WILD_FRUIT, 0.4), (Item.CLEAN_WATER, 0.3), (Item.HERB_BANDAGE, 0.2), (Item.SOCKS, 0.05), (Item.EXPIRED_COUPON, 0.05)],
    "老城区巷弄": [(Item.BREAD, 0.3), (Item.CLEAN_WATER, 0.3), (Item.WOOD, 0.25), (Item.EXPIRED_COUPON, 0.1), (Item.USELESS_BOX, 0.05)],
    "近郊小树林": [(Item.WOOD, 0.35), (Item.WILD_FRUIT, 0.3), (Item.VINE_ROPE, 0.2), (Item.HERB_BANDAGE, 0.1), (Item.HONEY, 0.05)],
    "漫山枫林": [(Item.WOOD, 0.3), (Item.VINE_ROPE, 0.25), (Item.HERB_BANDAGE, 0.2), (Item.MYSTERIOUS_SCROLL, 0.05), (Item.SPIRIT_STONE, 0.02)],
    "云雾山谷": [(Item.STONE, 0.3), (Item.IRON_ORE, 0.25), (Item.SPIRIT_STONE, 0.1), (Item.MYSTERIOUS_SCROLL, 0.08), (Item.PHOENIX_FEATHER, 0.01)],
    "湖滨芦苇荡": [(Item.DRIED_FISH, 0.3), (Item.CLEAN_WATER, 0.3), (Item.VINE_ROPE, 0.2), (Item.WATER_BREATHING_TALISMAN, 0.05), (Item.GOLDEN_AXE, 0.02)],
    "荒寂戈壁滩": [(Item.FLINT, 0.3), (Item.STONE, 0.3), (Item.IRON_ORE, 0.2), (Item.HEAT_RESIST_TALISMAN, 0.05), (Item.BROKEN_KEY, 0.02)],
    "寒色雪岭": [(Item.STONE, 0.3), (Item.COLD_RESIST_TALISMAN, 0.2), (Item.IRON_ORE, 0.15), (Item.PHOENIX_FEATHER, 0.03), (Item.MYSTERIOUS_SCROLL, 0.05)],
    "都市商业街": [(Item.BREAD, 0.35), (Item.EXPIRED_COUPON, 0.25), (Item.USELESS_BOX, 0.15), (Item.SOCKS, 0.1), (Item.SPIRIT_STONE, 0.02)],
    "山间古寺遗址": [(Item.SPIRIT_STONE, 0.2), (Item.MYSTERIOUS_SCROLL, 0.15), (Item.HEALING_SALVE, 0.15), (Item.PHOENIX_FEATHER, 0.05), (Item.BROKEN_KEY, 0.03)],
    "跨海长桥": [(Item.DRIED_FISH, 0.3), (Item.WATER_BREATHING_TALISMAN, 0.15), (Item.CLEAN_WATER, 0.2), (Item.SILVER_AXE, 0.05), (Item.SOCKS, 0.1)],
    "幻境心林": [(Item.SPIRIT_STONE, 0.3), (Item.MYSTERIOUS_SCROLL, 0.25), (Item.PHOENIX_FEATHER, 0.1), (Item.BROKEN_KEY, 0.05)],
    "时光溪谷": [(Item.SPIRIT_STONE, 0.35), (Item.MYSTERIOUS_SCROLL, 0.3), (Item.PHOENIX_FEATHER, 0.15), (Item.BROKEN_KEY, 0.08)],
    "沉船深海遗迹": [(Item.WATER_BREATHING_TALISMAN, 0.25), (Item.PHOENIX_FEATHER, 0.2), (Item.BROKEN_KEY, 0.15), (Item.GOLDEN_AXE, 0.05)],
    "众生之门玄关": [(Item.BROKEN_KEY, 0.4), (Item.PHOENIX_FEATHER, 0.3), (Item.MYSTERIOUS_SCROLL, 0.2), (Item.SPIRIT_STONE, 0.1)],
    "云端孤岛群": [(Item.PHOENIX_FEATHER, 0.35), (Item.BROKEN_KEY, 0.25), (Item.SPIRIT_STONE, 0.2), (Item.MYSTERIOUS_SCROLL, 0.2)],
}

# 钓鱼可获得的道具池
FISHING_LOOT_TABLE = [
    (Item.DRIED_FISH, 0.35),
    (Item.CLEAN_WATER, 0.2),
    (Item.RAW_MEAT, 0.15),
    (Item.RAW_MEAT, 0.1, "你钓上了一只小河蟹！它还活着，张牙舞爪的。不过太小了，只能当零嘴。"),
    (Item.USELESS_BOX, 0.05, "鱼线沉重，你满怀期待地拉上来——一个盒子。打开后什么也没有，但盒子里写着：'惊喜！'"),
    (Item.SOCKS, 0.05, "一只湿漉漉的袜子被钓了上来，它孤独地滴着水。"),
    (Item.GOLDEN_AXE, 0.02, "鱼钩卡住了什么重物，你用力一拽——一把金光闪闪的斧头破水而出！"),
    (Item.BROKEN_KEY, 0.01, "在鱼线尽头，你发现了一把锈迹斑斑的半截钥匙，它似乎不属于这个世界..."),
]

# 击杀不同大类生物可能掉落的道具
KILL_LOOT_TABLE = {
    "草食性动物": [(Item.RAW_MEAT, 0.6), (Item.ANIMAL_HIDE, 0.4), (Item.BONE, 0.3)],
    "肉食性动物": [(Item.RAW_MEAT, 0.5), (Item.ANIMAL_HIDE, 0.5), (Item.BONE, 0.4)],
    "杂食性动物": [(Item.RAW_MEAT, 0.5), (Item.ANIMAL_HIDE, 0.3), (Item.BONE, 0.3), (Item.WILD_FRUIT, 0.2)],
    "无脊椎动物": [(Item.BONE, 0.2), (Item.ANTIDOTE_HERB, 0.4), (Item.POISON_BAIT, 0.1)],
    "两栖类动物": [(Item.RAW_MEAT, 0.3), (Item.ANTIDOTE_HERB, 0.3), (Item.CLEAN_WATER, 0.2)],
    "水生动物": [(Item.RAW_MEAT, 0.5), (Item.DRIED_FISH, 0.4), (Item.BONE, 0.2)],
    "植物类生物": [(Item.WOOD, 0.5), (Item.HERB_BANDAGE, 0.4), (Item.WILD_FRUIT, 0.3), (Item.VINE_ROPE, 0.3)],
    "真菌类生物": [(Item.ANTIDOTE_HERB, 0.4), (Item.HEALING_SALVE, 0.1), (Item.BLOODSTOP_POWDER, 0.2)],
    "细菌类生物": [(Item.ANTIDOTE_HERB, 0.3), (Item.POISON_BAIT, 0.2)],
    "远古类生物": [(Item.RAW_MEAT, 0.3), (Item.BONE, 0.6), (Item.ANIMAL_HIDE, 0.5), (Item.MYSTERIOUS_SCROLL, 0.05)],
    "亡灵类": [(Item.BONE, 0.7), (Item.MYSTERIOUS_SCROLL, 0.1), (Item.BROKEN_KEY, 0.02)],
    "神兽类": [(Item.PHOENIX_FEATHER, 0.3), (Item.SPIRIT_STONE, 0.4), (Item.MYSTERIOUS_SCROLL, 0.2), (Item.BROKEN_KEY, 0.05)],
    "外星生物": [(Item.MYSTERIOUS_SCROLL, 0.3), (Item.SPIRIT_STONE, 0.2), (Item.BROKEN_KEY, 0.1), (Item.USELESS_BOX, 0.2)],
}


# ---------- 随机彩蛋事件系统 ----------

class EventType(str, Enum):
    TREASURE_CHEST = "宝箱事件"
    FISHING = "钓鱼事件"
    FAIRY = "仙女事件"
    WANDERING_MERCHANT = "迷路商人"
    METEOR = "天降陨石"
    WEIRD_SOUND = "奇怪声响"
    SUDDEN_RAINBOW = "雨后彩虹"
    TALKING_ANIMAL = "会说话的动物"


RANDOM_EVENTS = {
    "仙女问斧": {
        "触发条件": {"地形": ["淡水水域", "浅水水域", "湖滨芦苇荡"]},
        "概率": 0.05,
        "叙事": [
            "水面突然泛起金色涟漪，一个透明的身影从水中缓缓升起。\n那是一位周身笼罩着柔和光芒的仙女。\n她微微一笑，手中托着三把斧头：一把金的，一把银的，一把铁的。\n\n『诚实的孩子，你掉的是这把金斧头，还是这把银斧头，还是这把铁斧头呢？』\n\n她温柔地注视着你，等待你的回答...",
        ],
        "选项": [
            {"选择": "金斧头", "结果": "仙女摇了摇头：『你不诚实。』然后消失在水中，什么也没留下。", "获得": [], "精神变化": -5},
            {"选择": "银斧头", "结果": "仙女叹了口气：『还是不对呢。』水波荡漾，她渐渐消失了。", "获得": [], "精神变化": -3},
            {"选择": "铁斧头", "结果": "仙女开心地笑了：『你真是个诚实的人！作为奖励——三把斧头都送给你吧。』\n她把金、银、铁三把斧头都递给了你，然后化作光点消散在空气中。", "获得": [Item.GOLDEN_AXE, Item.SILVER_AXE, Item.IRON_AXE], "精神变化": 15},
        ],
    },
    "迷路商人": {
        "触发条件": {},
        "概率": 0.08,
        "叙事": [
            "你遇到了一位背着大包袱、满头大汗的商人。\n『哎呀呀，我迷路了...作为你帮我指路的答谢，送你点东西吧！』\n他热心地拿出一件物品塞到你手里，然后匆匆走了。",
        ],
        "随机奖励": [(Item.BREAD, 0.3), (Item.HEALING_SALVE, 0.2), (Item.CLEAN_WATER, 0.25), (Item.EXPIRED_COUPON, 0.15), (Item.SPIRIT_STONE, 0.05)],
    },
    "天降陨石": {
        "触发条件": {"地形": ["平原", "沙漠", "冻土", "山地"]},
        "概率": 0.03,
        "叙事": [
            "轰——！\n一声巨响，一颗陨石拖着火焰尾巴砸在你前方的地面上！\n坑里冒着热气，你小心地靠近，发现陨石中嵌着一小块发光的矿石...",
        ],
        "固定奖励": [{"道具": Item.IRON_ORE, "数量": 1}, {"道具": Item.SPIRIT_STONE, "数量": 1, "概率": 0.5}],
    },
    "宝箱降世": {
        "触发条件": {},
        "概率": 0.06,
        "叙事": [
            "草丛中反射出一道微弱的光芒。\n你拨开枝叶，发现了一个陈旧的宝箱。虽然布满灰尘，但锁扣似乎已经腐朽...",
            "一棵大树的树洞里，你隐约看到了一个箱子的轮廓。\n小心翼翼地伸手去够——还真是一个宝箱！",
            "水流冲来一只锈迹斑斑的铁箱，卡在了你身边的石缝里。\n打开之后里面竟然还有东西...",
        ],
        "随机奖励": [(Item.MYSTERIOUS_SCROLL, 0.1), (Item.SPIRIT_STONE, 0.15), (Item.HEALING_SALVE, 0.2), (Item.BLOODSTOP_POWDER, 0.2), (Item.FLINT, 0.15), (Item.USELESS_BOX, 0.1), (Item.GOLDEN_AXE, 0.02)],
    },
    "奇怪声响": {
        "触发条件": {},
        "概率": 0.1,
        "叙事": [
            "窸窸窣窣...\n旁边的草丛里传来奇怪的声音。你警惕地靠近，却只发现一只飞快逃窜的小东西——地上留下了几颗野果。",
            "远处传来像是叹息又像是风声的响动。\n你四处张望，什么也没看到，但脚下不知何时多了一块漂亮的石头。",
        ],
        "固定奖励": [{"道具": Item.WILD_FRUIT, "数量": 2, "概率": 0.6}, {"道具": Item.STONE, "数量": 1, "概率": 0.4}],
    },
    "雨后彩虹": {
        "触发条件": {"天气": ["暴雨", "梅雨"]},
        "概率": 0.15,
        "叙事": [
            "雨渐渐停了，天边出现了一道绚丽的彩虹。\n你望着那七彩的光桥，心中涌起一股莫名的感动。这景色，真美啊。",
        ],
        "精神加成": (10, 20),
    },
    "会说话的动物": {
        "触发条件": {},
        "概率": 0.02,
        "叙事": [
            "『喂——等一下！』\n你愣了一下，回头看向声音的来源。\n一只看起来很普通的动物正抬头看着你，嘴里吐出清晰的人言：\n『别那么惊讶，众生之门里什么都有可能发生，不是吗？祝你幸运！』\n说完，它转身钻进了树丛，留下你在原地风中凌乱。",
        ],
        "精神变化": 8,
        "随机奖励": [(Item.MYSTERIOUS_SCROLL, 0.3), (Item.SPIRIT_STONE, 0.3), (Item.BROKEN_KEY, 0.1), (Item.EXPIRED_COUPON, 0.3)],
    },
    # ===== 15个通用新彩蛋 =====
    "流浪小猫蹭身": {
        "触发条件": {"地图": ["城郊青草地", "老城区巷弄", "近郊小树林"]},
        "概率": 0.07,
        "叙事": [
            "一只脏兮兮却眼神明亮的流浪小猫不知从哪冒了出来。\n它看了你一眼，然后毫不客气地蹭了蹭你的身体，发出呼噜呼噜的声音。\n你的心一下子软了。",
        ],
        "精神加成": (8, 12),
        "随机奖励": [(Item.BREAD, 0.5)],
    },
    "捡到半张藏宝图": {
        "触发条件": {"地图": ["漫山枫林", "云雾山谷", "幻境心林"]},
        "概率": 0.04,
        "叙事": [
            "树根下露出一角泛黄的纸张。你小心地抽出来——是半张藏宝图！\n虽然不完整，但标注的位置隐约指向某个秘境深处...",
        ],
        "固定奖励": [{"道具": Item.MYSTERIOUS_SCROLL, "数量": 1, "概率": 1.0}],
    },
    "林间风铃自鸣": {
        "触发条件": {"地图": ["山间古寺遗址", "近郊小树林"], "天气": ["晴天"]},
        "概率": 0.09,
        "叙事": [
            "微风拂过，不知从哪传来风铃清脆的声响。\n明明没有铃铛，那声音却像在安抚你的心灵。你感到一阵莫名的安宁。",
        ],
        "精神加成": (10, 15),
    },
    "过期幸运彩票": {
        "触发条件": {"地图": ["老城区巷弄", "都市商业街"]},
        "概率": 0.06,
        "叙事": [
            "地上有一张刮开的彩票——'恭喜您获得大奖！'\n你心跳加速地翻到背面：'兑换截止日期：三天前'。",
        ],
        "固定奖励": [{"道具": Item.EXPIRED_COUPON, "数量": 1, "概率": 1.0}],
    },
    "月下白兔引路": {
        "触发条件": {"地图": ["城郊青草地", "漫山枫林"]},
        "概率": 0.03,
        "叙事": [
            "月光下，一只雪白的兔在前方停下脚步，回头看了你一眼。\n它似乎有意带路——你跟随它的身影，发现了一处隐蔽的物资点。",
            "白兔在月下跳跃前行，穿过草丛和小径。你跟着它走了一阵，眼前豁然开朗——一个小物资堆出现在面前。",
        ],
        "随机奖励": [(Item.WOOD, 0.5), (Item.STONE, 0.5), (Item.WILD_FRUIT, 0.4), (Item.VINE_ROPE, 0.3)],
    },
    "尘封旧日记": {
        "触发条件": {"地图": ["山间古寺遗址", "荒寂戈壁滩", "幻境心林"]},
        "概率": 0.05,
        "叙事": [
            "一本泛黄的日记本半埋在土中。扉页上写着：'致后来者——愿你在众生之门中找到自己的路。'\n你翻开残页，里面记载着一段古老的生存智慧。",
        ],
        "精神加成": (12, 18),
    },
    "雾中引路萤火": {
        "触发条件": {"天气": ["大雾"], "地图": ["近郊小树林", "湖滨芦苇荡"]},
        "概率": 0.12,
        "叙事": [
            "浓雾中，几点幽绿的萤火突然亮起。它们在你前方盘旋，仿佛在为你引路。\n你跟着萤火穿行，原本昏暗的视野变得清晰了一些。",
        ],
        "精神加成": (10, 22),
    },
    "自动售卖机漏电": {
        "触发条件": {"地图": ["都市商业街", "老城区巷弄"]},
        "概率": 0.05,
        "叙事": [
            "路边一台老旧的自动售卖机滋滋作响，屏幕乱码闪烁。\n然后——咣当一声，出货口滚出了一件商品！看来短路也有短路的好处。",
        ],
        "随机奖励": [(Item.CLEAN_WATER, 0.3), (Item.BREAD, 0.3), (Item.HEALING_SALVE, 0.1)],
    },
    "捡到另一只袜子": {
        "触发条件": {"地图": ["老城区巷弄", "城郊青草地"]},
        "概率": 0.08,
        "叙事": [
            "你捡起一只袜子——等等，这只和之前那只好像...能凑成一对！\n虽然不知道另一只为什么也会在这里，但成双的袜子让人莫名安心。",
        ],
        "固定奖励": [{"道具": Item.SOCKS, "数量": 1, "概率": 1.0}],
    },
    "古树低语落叶": {
        "触发条件": {"地图": ["近郊小树林", "漫山枫林"]},
        "概率": 0.06,
        "叙事": [
            "一棵参天古树下，落叶突然无风自动，围绕着你轻轻盘旋。\n你仿佛听到了古老的低语——那是树木在分享大地的记忆。",
        ],
        "精神加成": (10, 16),
        "随机奖励": [(Item.WILD_FRUIT, 0.3)],
    },
    "迷路的纸飞机": {
        "触发条件": {"地图": ["城郊青草地", "云端孤岛群"]},
        "概率": 0.1,
        "叙事": [
            "一架纸飞机晃晃悠悠地从天而降，落在你脚边。\n机翼上歪歪扭扭地写着：'如果你捡到，请帮我再飞一次！'",
        ],
        "精神加成": (3, 8),
        "随机奖励": [(Item.WOOD, 0.3)],
    },
    "夜半星轨显形": {
        "触发条件": {"天气": ["晴天"], "地图": ["山地", "云端孤岛群"]},
        "概率": 0.02,
        "叙事": [
            "深夜的天空格外清澈，星辰排列成不可思议的轨迹。\n你仰望着这片星空，感到自己虽渺小，却也与这天地万物相连。",
        ],
        "精神加成": (20, 25),
        "固定奖励": [{"道具": Item.SPIRIT_STONE, "数量": 1, "概率": 0.3}],
    },
    "蜂巢意外坠落": {
        "触发条件": {"地图": ["近郊小树林", "漫山枫林"]},
        "概率": 0.04,
        "叙事": [
            "头顶传来嗡嗡声——一个野蜂巢从树上掉了下来！\n幸运的是蜜蜂已经弃巢而去，留下的只有满满的金色蜂蜜。",
        ],
        "固定奖励": [{"道具": Item.HONEY, "数量": 1, "概率": 1.0}],
    },
    "无人野餐遗留": {
        "触发条件": {"地图": ["湖滨芦苇荡", "近郊小树林"]},
        "概率": 0.07,
        "叙事": [
            "一棵树下铺着一张野餐垫，上面放着还没打开的食物。\n四周空无一人，仿佛主人只是去散步了就再也没回来。",
        ],
        "固定奖励": [{"道具": Item.BREAD, "数量": 1, "概率": 1.0}, {"道具": Item.WILD_FRUIT, "数量": 2, "概率": 1.0},
                     {"道具": Item.CLEAN_WATER, "数量": 1, "概率": 0.8}],
    },
    "镜面水影幻景": {
        "触发条件": {"天气": ["晴天"], "地图": ["湖滨芦苇荡", "沉船深海遗迹"]},
        "概率": 0.05,
        "叙事": [
            "水面平静如镜，你俯身看去——倒影中竟然不是你自己，而是一片奇异的景象。\n那是另一个世界的映照，让你心神沉醉。",
        ],
        "精神加成": (15, 20),
    },
    # ===== 10个罗小黑主题彩蛋 =====
    "小黑同款黑毛团子": {
        "触发条件": {"地图": ["近郊小树林", "漫山枫林", "城郊青草地"], "天气": ["晴天"]},
        "概率": 0.06,
        "叙事": [
            "草丛里有一团软软的黑毛团子。你小心翼翼地碰了碰——毛茸茸的，让人想起某只黑色小猫。\n握着这团毛球，你的心情变得轻盈起来。",
        ],
        "精神加成": (10, 15),
    },
    "无限的随缘路过": {
        "触发条件": {"地图": ["山地", "山间古寺遗址", "跨海长桥"]},
        "概率": 0.03,
        "叙事": [
            "一袭白衣的身影从远处飘然路过，步伐从容，似在云游。\n他看了你一眼，微微颔首，留下了一缕清气便消失在山道尽头。",
        ],
        "固定奖励": [{"道具": Item.SPIRIT_STONE, "数量": 1, "概率": 1.0},
                     {"道具": Item.MYSTERIOUS_SCROLL, "数量": 1, "概率": 0.7}],
    },
    "老君的无聊棋局": {
        "触发条件": {"地图": ["山间古寺遗址"]},
        "概率": 0.04,
        "叙事": [
            "古寺庭院中，石桌上摆着一副残局。棋子已经落满了灰。\n你坐下来研究了许久，虽然没看懂棋路，但心境莫名地平静了下来。",
        ],
        "精神加成": (15, 20),
        "随机奖励": [(Item.EXPIRED_COUPON, 0.5)],
    },
    "比丢迷路探头": {
        "触发条件": {"地图": ["近郊小树林", "漫山枫林"]},
        "概率": 0.07,
        "叙事": [
            "灌木丛里探出一颗呆萌的小脑袋，好奇地打量着你。\n小家伙似乎迷路了，但丝毫不怕生。你忍不住和它分享了食物。",
        ],
        "固定奖励": [{"道具": Item.WILD_FRUIT, "数量": 3, "概率": 1.0}],
    },
    "阿根的冰系凉意": {
        "触发条件": {"地图": ["寒色雪岭", "荒寂戈壁滩"]},
        "概率": 0.05,
        "叙事": [
            "燥热之中，一股清凉的气息忽然包裹了你。\n仿佛有人在你周身布下了一层薄冰结界——寒意正好，不伤分毫。",
        ],
        "精神加成": (5, 10),
    },
    "妖灵会馆残牌": {
        "触发条件": {"地图": ["都市商业街", "老城区巷弄"]},
        "概率": 0.05,
        "叙事": [
            "不起眼的墙角躺着一块残破的木牌，上面刻着模糊的字迹——'...妖灵会馆...三楼左转...'\n这似乎是某个神秘组织的地址残片。",
        ],
        "精神加成": (12, 18),
    },
    "皇受傲娇蹭肩": {
        "触发条件": {"地图": ["城郊青草地", "近郊小树林"]},
        "概率": 0.08,
        "叙事": [
            "一道黑影无声地落在你肩上——一只高冷的黑猫正用尾巴尖扫你的耳朵。\n它面无表情，但身体却靠得很近。你明白了，它只是不好意思说喜欢你。",
        ],
        "精神加成": (8, 12),
    },
    "风息的落叶低语": {
        "触发条件": {"地图": ["近郊小树林", "漫山枫林", "云雾山谷"]},
        "概率": 0.02,
        "叙事": [
            "夜深了，落叶忽然聚在一起，发出类似人语的低吟。\n你侧耳倾听——那是风息带过树叶的沙沙声，却似乎讲述着一段古老的故事。",
        ],
        "精神加成": (20, 25),
        "随机奖励": [(Item.WOOD, 0.3)],
    },
    "府先生慵懒晒太阳": {
        "触发条件": {"地图": ["城郊青草地"]},
        "概率": 0.09,
        "叙事": [
            "草地上躺着一只体型壮硕的大猫，肚皮朝天，正在懒洋洋地晒太阳。\n它瞥了你一眼，打了个呵欠，挪了挪位置——给你留出了一块日晒最好的地方。",
        ],
        "精神加成": (10, 20),
    },
    "众生之门碎片现世": {
        "触发条件": {"地图": ["云端孤岛群", "众生之门玄关", "幻境心林", "时光溪谷"]},
        "概率": 0.02,
        "叙事": [
            "虚空中浮现出一枚微小的碎片，散发着柔和的光芒。\n那是众生之门的残片——触碰它的一瞬间，你感到整个世界的脉络在脑海中展开。",
        ],
        "固定奖励": [{"道具": Item.BROKEN_KEY, "数量": 1, "概率": 1.0}],
    },
    # ===== 6个嫦娥主题彩蛋 =====
    "桂树落桂飘香": {
        "触发条件": {"地图": ["近郊小树林", "漫山枫林", "云雾山谷"]},
        "概率": 0.08,
        "叙事": [
            "一阵幽香飘来，金黄的桂花从枝头簌簌落下。\n你伸手接了几朵，香气沁人心脾，让你忘却了疲惫。",
        ],
        "精神加成": (10, 15),
    },
    "玉兔草丛捣药": {
        "触发条件": {"地图": ["城郊青草地", "近郊小树林"]},
        "概率": 0.07,
        "叙事": [
            "草丛中传来笃笃的声音，一只小白兔正用小杵臼捣着什么。\n它看到你也不怕，反而推了一小团药膏到你面前。",
        ],
        "固定奖励": [{"道具": Item.HEALING_SALVE, "数量": 1, "概率": 1.0}],
    },
    "月下广寒虚影": {
        "触发条件": {"天气": ["晴天"], "地图": ["山地", "云端孤岛群"]},
        "概率": 0.03,
        "叙事": [
            "天边浮现出一座宫殿的淡淡虚影，琼楼玉宇，如梦似幻。\n那是传说中的广寒宫吗？你仰望着这片幻景，心中涌起无限遐思。",
        ],
        "精神加成": (18, 22),
        "固定奖励": [{"道具": Item.SPIRIT_STONE, "数量": 1, "概率": 0.3}],
    },
    "遗失月宫仙帕": {
        "触发条件": {"地图": ["湖滨芦苇荡"]},
        "概率": 0.05,
        "叙事": [
            "一条轻如蝉翼的丝帕从夜空飘落，上面绣着桂树玉兔的图案。\n你轻轻拾起，一股清凉的气息从掌心蔓延全身。",
        ],
        "精神加成": (8, 12),
    },
    "月圆玉兔静坐": {
        "触发条件": {"地图": ["城郊青草地", "湖滨芦苇荡", "漫山枫林"]},
        "概率": 0.06,
        "叙事": [
            "一轮圆月挂在当空，一只玉兔安静地坐在月光下，仿佛在等待着什么。\n你轻轻靠近，它推了一个小包裹到你脚边，里面是新鲜的野果。",
        ],
        "固定奖励": [{"道具": Item.WILD_FRUIT, "数量": 3, "概率": 1.0}],
        "精神加成": (8, 12),
    },
    "桂酒残坛留香": {
        "触发条件": {"地图": ["山间古寺遗址"]},
        "概率": 0.04,
        "叙事": [
            "古寺角落放着一坛尘封的桂酒，坛口微开，酒香四溢。\n你浅浅一尝——入口清甜，暖意从喉间流向四肢百骸。",
        ],
        "精神加成": (10, 15),
    },
}

# ---------- 营地建造系统 ----------

class BuildingType(str, Enum):
    CAMP = "简易营地"
    FENCE = "防护围栏"
    GREENHOUSE = "恒温种植区"
    AQUARIUM = "隔离水缸"
    FLOWERPOT = "隔离花盆"
    STORAGE = "储物箱"
    CAMPFIRE = "篝火"
    RAIN_COLLECTOR = "集雨器"


class Building(str, Enum):
    # 简易营地（核心建筑）
    SIMPLE_CAMP = "简易营地"
    REINFORCED_CAMP = "加固营地"
    # 防护设施
    WOODEN_FENCE = "木栅栏"
    STONE_WALL = "石墙"
    THORN_BARRIER = "荆棘屏障"
    # 种植区
    SMALL_GREENHOUSE = "小型温室"
    HERB_GARDEN = "草药圃"
    MUSHROOM_LOG = "菌菇木"
    # 水域隔离
    FRESHWATER_TANK = "淡水缸"
    SALTWATER_TANK = "海水缸"
    SEWAGE_TANK = "污水缸"
    # 花盆
    CLAY_POT = "陶土花盆"
    HANGING_PLANTER = "悬挂花盆"
    WATER_PLANT_BASIN = "水生植物盆"
    # 储物
    WOODEN_CHEST = "木箱"
    STONE_VAULT = "石柜"
    # 其他设施
    SMALL_CAMPFIRE = "小篝火"
    RAIN_BARREL = "集雨桶"


# 建筑配方：{成品: {材料: 数量}}
BUILDING_RECIPES = {
    Building.SIMPLE_CAMP: {Item.WOOD: 5, Item.VINE_ROPE: 2, Item.STONE: 3},
    Building.REINFORCED_CAMP: {Item.WOOD: 10, Item.STONE: 8, Item.IRON_ORE: 3, Item.VINE_ROPE: 4},
    Building.WOODEN_FENCE: {Item.WOOD: 3, Item.VINE_ROPE: 1},
    Building.STONE_WALL: {Item.STONE: 6, Item.IRON_ORE: 1},
    Building.THORN_BARRIER: {Item.VINE_ROPE: 4, Item.POISON_BAIT: 1},
    Building.SMALL_GREENHOUSE: {Item.WOOD: 4, Item.STONE: 2, Item.VINE_ROPE: 2},
    Building.HERB_GARDEN: {Item.WOOD: 2, Item.HERB_BANDAGE: 1, Item.STONE: 1},
    Building.MUSHROOM_LOG: {Item.WOOD: 3, Item.WILD_FRUIT: 1},
    Building.FRESHWATER_TANK: {Item.STONE: 4, Item.CLEAN_WATER: 2},
    Building.SALTWATER_TANK: {Item.STONE: 4, Item.CLEAN_WATER: 2},
    Building.SEWAGE_TANK: {Item.STONE: 4, Item.CLEAN_WATER: 2},
    Building.CLAY_POT: {Item.STONE: 2, Item.WOOD: 1},
    Building.HANGING_PLANTER: {Item.WOOD: 2, Item.VINE_ROPE: 1},
    Building.WATER_PLANT_BASIN: {Item.STONE: 3, Item.CLEAN_WATER: 1},
    Building.WOODEN_CHEST: {Item.WOOD: 4, Item.IRON_ORE: 1},
    Building.STONE_VAULT: {Item.STONE: 8, Item.IRON_ORE: 2},
    Building.SMALL_CAMPFIRE: {Item.WOOD: 2, Item.FLINT: 1},
    Building.RAIN_BARREL: {Item.WOOD: 3, Item.STONE: 2},
}

# 建筑效果描述
BUILDING_EFFECTS = {
    Building.SIMPLE_CAMP: "一个简陋但能遮风挡雨的营地，提供基本的安全感。",
    Building.REINFORCED_CAMP: "加固后的坚固营地，能抵御恶劣天气和野兽侵袭。",
    Building.WOODEN_FENCE: "一道木栅栏，挡住了大部分小型生物。",
    Building.STONE_WALL: "坚固的石墙，连猛兽都要三思。",
    Building.THORN_BARRIER: "布满荆棘的屏障，触碰者会受伤。",
    Building.SMALL_GREENHOUSE: "小型温室，里面的植物不受外面天气影响。",
    Building.HERB_GARDEN: "一小块草药圃，可以种植常见的疗伤草药。",
    Building.MUSHROOM_LOG: "一根接种了菌种的木头，能长出菌菇。",
    Building.FRESHWATER_TANK: "一个淡水缸，淡水生物可以在里面安全存活。",
    Building.SALTWATER_TANK: "一个模拟海水环境的缸，海水生物有了安身之所。",
    Building.SEWAGE_TANK: "用来养污水生物的隔离缸，不会污染其他水源。",
    Building.CLAY_POT: "一个普通的陶土花盆，能种小型植物。",
    Building.HANGING_PLANTER: "悬挂式的花盆，不占地面空间。",
    Building.WATER_PLANT_BASIN: "种水生植物的小型水盆。",
    Building.WOODEN_CHEST: "一个木箱，可以多放些东西。",
    Building.STONE_VAULT: "坚固的石柜，贵重物品放在里面比较安心。",
    Building.SMALL_CAMPFIRE: "一个小篝火，提供温暖和光亮的不二之选。",
    Building.RAIN_BARREL: "下雨的时候可以收集淡水，旱季的救命设施。",
}

# ---------- 六大灵系天赋效果 ----------
TALENT_EFFECTS = {
    "生灵系": {
        "name": "生灵系",
        "desc": "与生灵共鸣，生命恢复速度+30%，对植物类生物有亲和力",
        "vital_regen_bonus": 0.3,       # 生命自然恢复+30%
        "plant_affinity": True,          # 植物亲和
        "env_decay_reduction": 0.2,      # 环境消耗减少20%
    },
    "御灵系": {
        "name": "御灵系",
        "desc": "御使灵力的战斗天赋，战斗伤害+15%，可主动释放威压",
        "damage_bonus": 0.15,            # 战斗伤害+15%
        "intimidation": True,            # 威压：战斗开始时降低对手战力
    },
    "造物系": {
        "name": "造物系",
        "desc": "巧手造物的天赋，建造材料消耗-20%，可制作专属道具",
        "build_cost_reduction": 0.2,     # 建造材料-20%
        "craft_bonus": True,             # 可制作专属道具
    },
    "空间系": {
        "name": "空间系",
        "desc": "感知空间的天赋，无视地形减速，闪避率+10%",
        "ignore_terrain_slow": True,     # 无视地形减速
        "dodge_bonus": 0.1,             # 闪避率+10%
        "terrain_adapt_min": 0.3,       # 地形适配最低值提升到0.3
    },
    "心灵系": {
        "name": "心灵系",
        "desc": "洞察心灵的天赋，精神值消耗-30%，可感知附近红名玩家",
        "sanity_decay_reduction": 0.3,  # 精神消耗-30%
        "sense_red_name": True,          # 感知红名
    },
    "锁御系": {
        "name": "锁御系",
        "desc": "封锁与防御的天赋，防御力+20%，受伤时自动减伤10%",
        "defense_bonus": 0.2,           # 防御+20%
        "auto_damage_reduction": 0.1,   # 自动减伤10%
    },
}

# ---------- 物种大类特殊机制 ----------
CATEGORY_TRAITS = {
    "远古类生物": {
        "desc": "远古血脉，基础四维更高，抗性拉满，但经验获取-30%",
        "vital_bonus": 30,       # 四维上限+30
        "exp_penalty": 0.3,      # 经验获取-30%
        "env_resist": 0.4,       # 环境抗性+40%
    },
    "亡灵类": {
        "desc": "亡者之躯，不怕冻伤，精神值特殊机制，但怕阳光",
        "immune_frostbite": True, # 免疫冻伤
        "sanity_decay_bonus": 0.5, # 精神消耗+50%
        "sunlight_penalty": True,  # 白天阳光额外消耗
    },
    "神兽类": {
        "desc": "天生高天赋，极稀有，本能极强，全属性加成",
        "vital_bonus": 50,
        "damage_bonus": 0.25,
        "all_terrain_adapt": 0.5, # 全地形最低适配0.5
    },
    "外星生物": {
        "desc": "异星来客，无视部分环境规则，水土不忌，特殊感官",
        "ignore_weather": 0.5,    # 天气影响减半
        "terrain_adapt_bonus": 0.3, # 全地形适配+0.3
        "special_sense": True,
    },
    "细菌类生物": {
        "desc": "微小但顽强，环境抗性极高，四维消耗极低",
        "env_decay_reduction": 0.6, # 环境消耗-60%
        "tiny_size": True,          # 难以被命中
    },
}

# ---------- 生物被动本能系统 ----------
SPECIES_INNATES = {
    # ===== 无脊椎动物 =====
    "蜈蚣": {"innate": "毒素", "desc": "攻击时附带毒素，造成额外中毒损伤", "effect": {"poison_on_hit": 5}},
    "蝎": {"innate": "毒素", "desc": "尾部毒刺，攻击附带中毒效果", "effect": {"poison_on_hit": 8}},
    "蜘蛛": {"innate": "织网", "desc": "可在所在地形布置陷阱，限制目标行动", "effect": {"trap_bonus": True}},
    "水母": {"innate": "毒素", "desc": "触手带剧毒，被攻击时反伤中毒", "effect": {"poison_on_hit": 10, "poison_reflect": 5}},
    "章鱼": {"innate": "拟态", "desc": "可改变体色融入环境，闪避率+15%", "effect": {"dodge_bonus": 0.15}},
    "蜜蜂": {"innate": "毒素", "desc": "螫针攻击附带毒素", "effect": {"poison_on_hit": 3}},
    "蚂蚁": {"innate": "巨力", "desc": "可搬运超过自身体重的物体，建造材料-1", "effect": {"build_bonus": 1}},
    "甲虫": {"innate": "甲壳", "desc": "坚硬外壳提供额外防御，减伤15%", "effect": {"defense_bonus": 0.15}},
    "蜻蜓": {"innate": "高速", "desc": "飞行速度快，闪避率+20%", "effect": {"dodge_bonus": 0.2}},
    "螳螂": {"innate": "利爪", "desc": "前肢如刀，攻击伤害+10%", "effect": {"damage_bonus": 0.1}},
    "屎壳郎": {"innate": "坚韧", "desc": "推粪球练就惊人耐力，体力消耗-20%", "effect": {"stamina_decay_reduction": 0.2}},
    "蚯蚓": {"innate": "再生", "desc": "被斩断后可再生，生命自然恢复+50%", "effect": {"regen_bonus": 0.5}},

    # ===== 两栖类 =====
    "蛙": {"innate": "跳跃", "desc": "强健后腿，脱离战斗时必定成功", "effect": {"escape_bonus": True}},
    "蟾蜍": {"innate": "毒素", "desc": "皮肤分泌毒液，被攻击时反伤中毒", "effect": {"poison_reflect": 8}},
    "箭毒蛙": {"innate": "剧毒", "desc": "体表剧毒，攻击和被攻击都附带高额毒素", "effect": {"poison_on_hit": 15, "poison_reflect": 10}},
    "树蛙": {"innate": "伪装", "desc": "体色与树叶无异，闪避率+15%", "effect": {"dodge_bonus": 0.15}},

    # ===== 水生动物 =====
    "鲨鱼": {"innate": "嗜血", "desc": "闻到血腥味后攻击力+25%", "effect": {"bloodlust_bonus": 0.25}},
    "章鱼": {"innate": "拟态", "desc": "已在无脊椎动物中定义", "effect": {}},
    "电鳗": {"innate": "电击", "desc": "释放电流麻痹目标，攻击附带眩晕效果", "effect": {"stun_on_hit": True}},
    "海龟": {"innate": "甲壳", "desc": "坚硬龟壳，防御+25%", "effect": {"defense_bonus": 0.25}},
    "河蟹": {"innate": "甲壳", "desc": "坚硬外壳，防御+15%", "effect": {"defense_bonus": 0.15}},
    "龙虾": {"innate": "甲壳", "desc": "坚硬外壳，防御+15%", "effect": {"defense_bonus": 0.15}},

    # ===== 植物类 =====
    "仙人掌": {"innate": "储水", "desc": "体内储水，饱腹值消耗-30%", "effect": {"satiety_decay_reduction": 0.3}},
    "藤蔓": {"innate": "缠绕", "desc": "藤蔓缠绕目标，攻击附带束缚效果", "effect": {"bind_on_hit": True}},
    "猪笼草": {"innate": "诱捕", "desc": "分泌蜜液诱捕猎物，陷阱成功率+30%", "effect": {"trap_bonus": 0.3}},
    "捕蝇草": {"innate": "速攻", "desc": "瞬间闭合叶片，攻击速度极快，先手率+20%", "effect": {"initiative_bonus": 0.2}},
    "含羞草": {"innate": "感知", "desc": "对环境变化极度敏感，能提前感知危险", "effect": {"danger_sense": True}},
    "菌菇": {"innate": "孢子", "desc": "释放孢子，轻微中毒+精神干扰", "effect": {"spore_cloud": True}},

    # ===== 真菌类 =====
    "毒蝇伞": {"innate": "致幻", "desc": "释放致幻孢子，目标精神值下降", "effect": {"sanity_damage_on_hit": 5}},
    "冬虫夏草": {"innate": "寄生", "desc": "可寄生在目标身上缓慢吸取生命", "effect": {"life_drain": 2}},

    # ===== 肉食性动物 =====
    "虎": {"innate": "威压", "desc": "百兽之王的威压，战斗开始时降低目标战力", "effect": {"intimidation": True}},
    "狮": {"innate": "领袖", "desc": "狮群领袖气质，战斗时自身战力+5%", "effect": {"damage_bonus": 0.05}},
    "狼": {"innate": "追猎", "desc": "追踪猎物时体力消耗-25%，追击伤害+10%", "effect": {"pursuit_bonus": 0.1}},
    "鹰": {"innate": "锐眼", "desc": "高空俯瞰，总能先手攻击", "effect": {"initiative_bonus": 0.3}},
    "鳄鱼": {"innate": "潜伏", "desc": "水中潜伏时首次攻击伤害翻倍", "effect": {"ambush_bonus": 1.0}},
    "蛇": {"innate": "毒素", "desc": "毒牙攻击附带毒素", "effect": {"poison_on_hit": 6}},
    "豹": {"innate": "疾速", "desc": "陆地最快的速度，闪避+25%", "effect": {"dodge_bonus": 0.25}},
    "鬣狗": {"innate": "坚韧", "desc": "极强生存力，生命消耗-20%", "effect": {"vitality_decay_reduction": 0.2}},

    # ===== 草食性动物 =====
    "兔": {"innate": "警觉", "desc": "天生警觉，逃跑成功率+30%", "effect": {"escape_bonus": 0.3}},
    "鹿": {"innate": "疾速", "desc": "奔跑速度快，逃跑成功率+20%", "effect": {"escape_bonus": 0.2}},
    "马": {"innate": "耐力", "desc": "持久奔跑，体力消耗-30%", "effect": {"stamina_decay_reduction": 0.3}},
    "象": {"innate": "厚皮", "desc": "厚重皮肤，防御+20%，免疫小伤口", "effect": {"defense_bonus": 0.2}},
    "树懒": {"innate": "节能", "desc": "新陈代谢极慢，所有消耗-40%", "effect": {"all_decay_reduction": 0.4}},
    "考拉": {"innate": "毒素", "desc": "长期吃桉树叶，体内带微弱毒性", "effect": {"poison_reflect": 3}},

    # ===== 杂食性动物 =====
    "熊": {"innate": "狂暴", "desc": "生命低于30%时攻击力+40%", "effect": {"berserk_bonus": 0.4}},
    "猪": {"innate": "坚韧", "desc": "皮糙肉厚，减伤10%", "effect": {"defense_bonus": 0.1}},
    "狐": {"innate": "狡黠", "desc": "交易时更易获得有利交换", "effect": {"trade_bonus": True}},
    "鼠": {"innate": "隐匿", "desc": "体型小巧，闪避+20%", "effect": {"dodge_bonus": 0.2}},
    "猩猩": {"innate": "智慧", "desc": "使用道具效果+20%", "effect": {"item_bonus": 0.2}},
    "浣熊": {"innate": "灵巧", "desc": "前爪灵活，建造速度+25%", "effect": {"build_speed": 0.25}},
    "刺猬": {"innate": "尖刺", "desc": "浑身尖刺，被攻击时反伤", "effect": {"damage_reflect": 5}},

    # ===== 亡灵类 =====
    "骷髅": {"innate": "不死", "desc": "免疫中毒、窒息、冻伤", "effect": {"immune_poison": True, "immune_asphyxia": True, "immune_frostbite": True}},
    "幽灵": {"innate": "虚无", "desc": "物理攻击减免50%，但精神攻击翻倍", "effect": {"physical_resist": 0.5, "sanity_weakness": True}},
    "僵尸": {"innate": "腐烂", "desc": "攻击附带腐毒，造成持续伤害", "effect": {"rot_on_hit": 3}},
    "吸血鬼": {"innate": "吸血", "desc": "攻击时吸取目标生命值恢复自身", "effect": {"life_steal": 0.3}},
    "巫妖": {"innate": "奥术", "desc": "精神值消耗减半，可感知附近所有生物", "effect": {"sanity_decay_reduction": 0.5, "detect_life": True}},

    # ===== 神兽类 =====
    "真龙": {"innate": "龙威", "desc": "万物臣服，战斗开始时目标战力-20%", "effect": {"intimidation": 0.2}},
    "凤凰": {"innate": "涅槃", "desc": "死亡后可立刻重新降世，无冷却", "effect": {"rebirth": True}},
    "玄武": {"innate": "神甲", "desc": "防御+40%，免疫暴击", "effect": {"defense_bonus": 0.4}},
    "白虎": {"innate": "杀伐", "desc": "攻击力+30%，击杀后精神回复", "effect": {"damage_bonus": 0.3, "kill_sanity_restore": 10}},
    "九尾狐": {"innate": "魅惑", "desc": "战斗中有概率使目标放弃攻击", "effect": {"charm_chance": 0.15}},

    # ===== 外星生物 =====
    "异形": {"innate": "酸血", "desc": "被攻击时喷溅酸血，反伤15点伤害", "effect": {"acid_blood": 15}},
    "硅基生命体": {"innate": "结晶", "desc": "硅基皮肤，物理伤害减免30%", "effect": {"physical_resist": 0.3}},
    "能量体": {"innate": "无实", "desc": "物理攻击完全免疫，但环境消耗翻倍", "effect": {"physical_immune": True, "env_decay_double": True}},
}

# ---------- 专精加点系统 ----------
# 每5级获得1点专精点
SPECIALIZATION_PER_LEVELS = 5

# 六大专精树
SPECIALIZATIONS = {
    "气候抗性": {
        "desc": "提升对恶劣天气的耐受能力，每级减少天气影响10%",
        "max_level": 5,
        "effect_per_level": {"weather_reduction": 0.1},
    },
    "水域适应": {
        "desc": "提升跨水域生存能力，每级增加水域地形适配0.15",
        "max_level": 5,
        "effect_per_level": {"water_adapt_bonus": 0.15},
    },
    "体质强化": {
        "desc": "提升肉身强度，每级增加四维上限5点",
        "max_level": 5,
        "effect_per_level": {"vital_bonus": 5},
    },
    "生态适应": {
        "desc": "提升全地形适应能力，每级增加全地形适配0.08",
        "max_level": 5,
        "effect_per_level": {"terrain_adapt_bonus": 0.08},
    },
    "生存博弈": {
        "desc": "提升战斗技巧，每级增加战斗伤害3%",
        "max_level": 5,
        "effect_per_level": {"combat_bonus": 0.03},
    },
    "野外捕猎": {
        "desc": "提升捕猎效率，每级增加击杀经验获取10%",
        "max_level": 5,
        "effect_per_level": {"exp_bonus": 0.1},
    },
}

# ---------- 种田植物生态 ----------
PLANT_GROWTH = {
    "生长阶段": ["种子", "发芽", "幼苗", "成熟", "开花", "结果", "枯萎"],
    "阶段时长": {  # 每阶段所需Tick数
        "种子": 5,
        "发芽": 8,
        "幼苗": 12,
        "成熟": 15,
        "开花": 10,
        "结果": 8,
        "枯萎": 20,
    },
    "天气加成": {
        "晴天": {"生长速度": 1.2, "描述": "阳光充沛，光合作用旺盛"},
        "暴雨": {"生长速度": 0.7, "描述": "雨水过多，根系呼吸困难"},
        "梅雨": {"生长速度": 0.8, "描述": "持续潮湿，有烂根风险"},
        "酷暑": {"生长速度": 0.5, "描述": "烈日暴晒，水分蒸发过快"},
        "寒潮": {"生长速度": 0.3, "描述": "寒冷刺骨，生长几乎停滞"},
        "大雾": {"生长速度": 0.9, "描述": "光照不足，生长缓慢"},
        "狂风": {"生长速度": 0.6, "描述": "强风吹袭，枝叶受损"},
    },
    "建筑加成": {
        "小型温室": {"生长速度": 1.5, "免疫恶劣天气": True, "描述": "温室内四季如春"},
        "草药圃": {"生长速度": 1.3, "描述": "精心打理的小药圃"},
        "菌菇木": {"生长速度": 1.4, "描述": "菌丝在木头上蔓延"},
    },
    "产出": {
        "橡树": {"结果阶段产出": "木材", "产出量": 3},
        "竹": {"结果阶段产出": "木材", "产出量": 2},
        "蔷薇": {"开花阶段产出": "野蜂蜜", "产出量": 1},
        "仙人掌": {"成熟阶段产出": "净水", "产出量": 2},
        "猪笼草": {"成熟阶段产出": "毒饵", "产出量": 1},
        "捕蝇草": {"成熟阶段产出": "毒饵", "产出量": 1},
        "银杏": {"结果阶段产出": "野果", "产出量": 4},
        "香菇": {"成熟阶段产出": "野果", "产出量": 2},
        "灵芝": {"成熟阶段产出": "治疗药膏", "产出量": 1},
        "毒蝇伞": {"成熟阶段产出": "毒饵", "产出量": 2},
    },
    "环境要求": {
        "仙人掌": {"最低温度": "酷暑", "最高湿度": "干燥"},
        "蘑菇": {"最低湿度": "潮湿", "最高光照": "阴暗"},
        "芦苇": {"必须地形": "浅水水域"},
        "海带": {"必须地形": "海水水域"},
    },
}

# 每张地图的商店配置（只有部分地图有商店）
MAP_SHOPS = {
    # ===== 新手区 =====
    "城郊青草地": {
        "商店列表": [
            {
                "商店名": "路边摊",
                "描述": "一张简陋的桌子，摆着新手最需要的物资。",
                "商品": [
                    {"名称": "野果", "价格": "石块x1"},
                    {"名称": "木材", "价格": "野果x1"},
                    {"名称": "石块", "价格": "木材x1"},
                    {"名称": "净水", "价格": "野果x2"},
                ],
            },
            {
                "商店名": "老猎人地摊",
                "描述": "一位沉默的老猎人，出售狩猎用具。",
                "商品": [
                    {"名称": "藤绳", "价格": "木材x2"},
                    {"名称": "捕兽夹", "价格": "铁矿石x2"},
                    {"名称": "兽皮", "价格": "木材x3"},
                ],
            },
        ],
    },
    "老城区巷弄": {
        "商店列表": [
            {
                "商店名": "巷口杂货铺",
                "描述": "老城区角落里的小店，什么都卖一点。",
                "商品": [
                    {"名称": "干粮", "价格": "石块x3"},
                    {"名称": "净水", "价格": "木材x2"},
                    {"名称": "燧石", "价格": "野果x3"},
                    {"名称": "生锈的铁刀", "价格": "铁矿石x2"},
                    {"名称": "草药绷带", "价格": "野果x4"},
                    {"名称": "过期优惠券", "价格": "野果x1"},
                    {"名称": "简易钓竿", "价格": "木材x3"},
                ],
            },
            {
                "商店名": "老药铺",
                "描述": "柜台后是一排排药柜，老药师在研磨药粉。",
                "商品": [
                    {"名称": "草药绷带", "价格": "野果x2"},
                    {"名称": "解毒草", "价格": "野果x4"},
                    {"名称": "止血散", "价格": "净水x3"},
                    {"名称": "治疗药膏", "价格": "野蜂蜜x2"},
                ],
            },
        ],
    },
    "近郊小树林": {
        "商店列表": [
            {
                "商店名": "林间小铺",
                "描述": "藏在树林里的小木屋，专卖林间采集品。",
                "商品": [
                    {"名称": "木材", "价格": "石块x2"},
                    {"名称": "藤绳", "价格": "木材x2"},
                    {"名称": "野蜂蜜", "价格": "木材x4"},
                    {"名称": "草药绷带", "价格": "野果x3"},
                ],
            },
        ],
    },
    # ===== 日常练级区 =====
    "漫山枫林": {
        "商店列表": [
            {
                "商店名": "枫林客栈",
                "描述": "漫山红叶间的小客栈，供旅人歇脚补给。",
                "商品": [
                    {"名称": "干粮", "价格": "木材x3"},
                    {"名称": "净水", "价格": "野果x2"},
                    {"名称": "草药绷带", "价格": "兽皮x2"},
                ],
            },
        ],
    },
    "云雾山谷": {
        "商店列表": [
            {
                "商店名": "谷底小栈",
                "描述": "浓雾深处的小栈，专卖修行用品。",
                "商品": [
                    {"名称": "灵石", "价格": "铁矿石x3"},
                    {"名称": "神秘古卷", "价格": "灵石x2"},
                    {"名称": "铁矿石", "价格": "石块x5"},
                ],
            },
            {
                "商店名": "符咒摊",
                "描述": "一位云游道士摆的小摊，画符为生。",
                "商品": [
                    {"名称": "御寒符", "价格": "灵石x1"},
                    {"名称": "避暑符", "价格": "灵石x1"},
                    {"名称": "抗毒符", "价格": "灵石x2"},
                ],
            },
        ],
    },
    "湖滨芦苇荡": {
        "商店列表": [
            {
                "商店名": "湖畔鱼市",
                "描述": "芦苇荡边的鱼市，专卖水产。",
                "商品": [
                    {"名称": "鱼干", "价格": "野果x2"},
                    {"名称": "净水", "价格": "石块x1"},
                    {"名称": "藤绳", "价格": "鱼干x1"},
                    {"名称": "简易钓竿", "价格": "木材x3"},
                ],
            },
        ],
    },
    # ===== 都市区 =====
    "都市商业街": {
        "商店列表": [
            {
                "商店名": "都市大药房",
                "描述": "现代化的药房，药品齐全。",
                "商品": [
                    {"名称": "草药绷带", "价格": "野果x1"},
                    {"名称": "解毒草", "价格": "野果x2"},
                    {"名称": "治疗药膏", "价格": "净水x3"},
                    {"名称": "止血散", "价格": "兽皮x2"},
                ],
            },
            {
                "商店名": "五金店",
                "描述": "专卖工具和建材。",
                "商品": [
                    {"名称": "燧石", "价格": "石块x2"},
                    {"名称": "铁矿石", "价格": "石块x4"},
                    {"名称": "捕兽夹", "价格": "铁矿石x1"},
                    {"名称": "石斧", "价格": "铁矿石x3"},
                ],
            },
            {
                "商店名": "便利店",
                "描述": "24小时营业，旅行者的补给站。",
                "商品": [
                    {"名称": "干粮", "价格": "石块x2"},
                    {"名称": "净水", "价格": "木材x1"},
                    {"名称": "野果", "价格": "石块x1"},
                ],
            },
        ],
    },
    "山间古寺遗址": {
        "商店列表": [
            {
                "商店名": "灵器铺",
                "描述": "幽静的铺子里陈列着闪闪发光的灵器。",
                "商品": [
                    {"名称": "御寒符", "价格": "灵石x2"},
                    {"名称": "避暑符", "价格": "灵石x2"},
                    {"名称": "避水符", "价格": "灵石x3"},
                    {"名称": "抗毒符", "价格": "灵石x3"},
                    {"名称": "灵石", "价格": "神秘古卷x1"},
                ],
            },
        ],
    },
}

# ---------- 地图连接系统 ----------
# 每张地图可前往的相邻地图
MAP_CONNECTIONS = {
    "城郊青草地": ["近郊小树林", "老城区巷弄", "都市商业街"],
    "老城区巷弄": ["城郊青草地", "都市商业街", "近郊小树林"],
    "近郊小树林": ["城郊青草地", "老城区巷弄", "漫山枫林", "湖滨芦苇荡"],
    "漫山枫林": ["近郊小树林", "云雾山谷", "湖滨芦苇荡"],
    "云雾山谷": ["漫山枫林", "山间古寺遗址", "荒寂戈壁滩"],
    "湖滨芦苇荡": ["近郊小树林", "漫山枫林", "跨海长桥"],
    "荒寂戈壁滩": ["云雾山谷", "寒色雪岭"],
    "寒色雪岭": ["荒寂戈壁滩", "云端孤岛群"],
    "都市商业街": ["城郊青草地", "老城区巷弄", "跨海长桥"],
    "山间古寺遗址": ["云雾山谷", "幻境心林"],
    "跨海长桥": ["都市商业街", "湖滨芦苇荡", "沉船深海遗迹"],
    "幻境心林": ["山间古寺遗址", "时光溪谷"],
    "时光溪谷": ["幻境心林"],
    "沉船深海遗迹": ["跨海长桥"],
    "云端孤岛群": ["寒色雪岭", "众生之门玄关"],
    "众生之门玄关": ["云端孤岛群"],
}

# 可营业的物种（商店NPC身份）
STALL_ELIGIBLE_SPECIES = [
    "人类", "狐", "浣熊", "猩猩", "乌鸦",  # 杂食动物（聪明）
    "兔", "鹿", "羊", "马", "牛", "树懒", "考拉",  # 草食动物（温顺）
]

# ---------- 地图迷雾系统 ----------
# 每张地图的坐标网格（简化：每张地图视为一个节点）
# 地图连接关系已在 MAP_CONNECTIONS 定义
# 探索过的地图集合存储在玩家数据中
