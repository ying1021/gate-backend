import random
import uuid

from fastapi import FastAPI

from app.core.config import Species, Terrain
from app.models.player import Player, Talent
from app.services.game_service import simulate_tick_with_narrative

app = FastAPI(title="众生之门")
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
from app.database import init_db


@app.on_event("startup")
def startup():
    init_db()


@app.get("/")
async def root():
    return {"message": "众生之门已开启"}


@app.post("/player/create")
async def create_player():
    """创建一个新玩家，随机物种和天赋"""
    from app.database import save_player as db_save
    
    chosen_species = random.choice(list(Species))
    chosen_talent = random.choice(list(Talent))
    
    player = Player(
        id=str(uuid.uuid4())[:8],
        species=chosen_species,
        talent=chosen_talent,
    )
    
    # 初始化生命值和其他基础属性
    if not player.vital:
        player.vital = {
            '体力耐力': 100,
            '饱腹值': 100,
            '精神状态': 100
        }
    if not player.inventory:
        player.inventory = []
    if not player.current_map:
        player.current_map = "城郊青草地"
    
    # 保存到数据库
    db_save(player)
    
    return {
        "msg": "生灵降世",
        "success": True,
        "player": player.model_dump(by_alias=True)
    }



@app.post("/game/tick")
async def tick(
    player_id: str = "test",
    species_str: str = "草鱼",
    terrain_str: str = "淡水水域",
    weather_str: str = "晴天"
):
    """模拟一个时间 Tick"""
    species = Species(species_str)
    terrain = Terrain(terrain_str)
    player = Player(id=player_id, species=species)
    result = simulate_tick_with_narrative(player, terrain, weather_str)
    return result


@app.post("/game/kill")
async def kill(
    killer_level: int = 1,
    target_level: int = 1,
    player_id: str = "test",
    species_str: str = "虎"
):
    """模拟击杀"""
    from app.services.game_service import calculate_exp_gain, add_exp
    exp_gain = calculate_exp_gain(killer_level, target_level)
    player = Player(id=player_id, species=Species(species_str), level=killer_level)
    result = add_exp(player, exp_gain)
    result["击杀经验基础值"] = round(exp_gain, 2)
    result["玩家最终状态"] = player.model_dump(by_alias=True)
    return result


@app.post("/game/battle")
async def battle(
    attacker_species: str = "虎",
    defender_species: str = "兔",
    attacker_level: int = 3,
    defender_level: int = 1,
    terrain_str: str = "森林",
    attacker_action: str = "撕咬",
    defender_action: str = "冲撞",
):
    """模拟战斗回合"""
    from app.services.game_service import execute_battle
    attacker = Player(id="attacker", species=Species(attacker_species), level=attacker_level)
    defender = Player(id="defender", species=Species(defender_species), level=defender_level)
    result = await execute_battle(attacker, defender, terrain_str, attacker_action, defender_action)
    return result


from app.services.game_service import (
    go_offline, go_online, handle_death,
    create_new_life, check_death_cooldown,
    explore_map, go_fishing, resolve_fairy_choice,
    trigger_random_event, get_kill_loot,
    add_to_inventory, remove_from_inventory, view_inventory, use_item,
    list_trade, browse_trades, accept_trade,
    can_build, build, view_settlement, dismantle,
    get_shops_for_map, buy_item,
    move_to_map, get_available_moves,
    open_stall, close_stall,
    check_red_name, commit_suicide,
    explore_map_node, get_visible_maps,
    check_city_rules, get_city_ambience,
    enter_instance, instance_tick, exit_instance,
    tick_plant_growth, get_plant_growth_stage, harvest_plant,
)
from app.core.config import Building


@app.post("/player/online")
async def player_online(player_id: str = "test"):
    """玩家上线"""
    result = go_online(player_id)
    return result


@app.post("/player/offline")
async def player_offline(player_id: str = "test"):
    """离线保命"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.vital.vitality = 15
    player.vital.stamina = 20
    player.injury.skin_laceration = 60
    player.injury.blood_loss = 40
    result = go_offline(player)
    db_save(player)
    return result


@app.post("/player/death")
async def player_death(player_id: str = "test", killer_id: str = "unknown"):
    """玩家死亡"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.vital.vitality = 0
    result = handle_death(player, killer_id)
    return result


@app.post("/player/suicide")
async def suicide(player_id: str = "test", level: int = 3):
    """玩家自杀"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = commit_suicide(player)
    return result


@app.post("/player/new_life")
async def new_life():
    """创建新生命"""
    result = create_new_life()
    return result


@app.get("/player/death_cooldown")
async def death_cooldown(player_id: str = "test"):
    """查询死亡冷却"""
    remaining = check_death_cooldown(player_id)
    if remaining is None:
        return {"msg": "可以重新降世", "需要等待": False}
    return {"msg": f"冷却中，剩余 {remaining} 秒", "需要等待": True, "剩余秒数": remaining}


@app.get("/player/red_name")
async def player_red_name(player_id: str = "test"):
    """查看红名状态"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    if not hasattr(player, 'same_category_kills'):
        player.same_category_kills = 10
        player.red_name = False
        player.penance_ticks = 0
    result = check_red_name(player)
    return result


@app.post("/game/explore")
async def explore(player_id: str = "test", map_region: str = "城郊青草地"):
    """地图探索"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = explore_map(player, map_region)
    db_save(player)
    return result


@app.post("/game/fishing")
async def fishing(player_id: str = "test", map_region: str = "湖滨芦苇荡"):
    """钓鱼"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = go_fishing(player, map_region)
    db_save(player)
    return result


@app.post("/game/fairy_choice")
async def fairy_choice(player_id: str = "test", choice: str = "铁斧头"):
    """仙女问斧"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = resolve_fairy_choice(player, choice)
    db_save(player)
    return result


@app.post("/game/random_event")
async def random_event(
    player_id: str = "test",
    terrain_str: str = "森林",
    weather_str: str = "晴天",
    map_region: str = "漫山枫林",
):
    """触发随机事件"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = trigger_random_event(player, terrain_str, weather_str, map_region)
    db_save(player)
    return result


@app.post("/game/kill_loot")
async def kill_loot(target_category: str = "草食性动物"):
    """查看击杀掉落"""
    result = get_kill_loot(target_category)
    return {"击杀目标大类": target_category, "掉落道具": result}


@app.post("/inventory/add")
async def inventory_add(player_id: str = "test", item_name: str = "野果", quantity: int = 1):
    """添加道具"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = add_to_inventory(player, item_name, quantity)
    db_save(player)
    result["背包总览"] = view_inventory(player)
    return result


@app.post("/inventory/remove")
async def inventory_remove(player_id: str = "test", item_name: str = "野果", quantity: int = 1):
    """移除道具"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    add_to_inventory(player, item_name, 3)
    result = remove_from_inventory(player, item_name, quantity)
    db_save(player)
    result["背包总览"] = view_inventory(player)
    return result


@app.get("/inventory/view")
async def inventory_view(player_id: str = "test"):
    """查看背包"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
        add_to_inventory(player, "野果", 2)
        add_to_inventory(player, "草药绷带", 1)
    result = view_inventory(player)
    return result


@app.post("/inventory/use")
async def inventory_use(
    player_id: str = "test",
    item_name: str = "草药绷带",
):
    """使用道具"""
    from app.database import load_player as db_load, save_player as db_save
    from app.services.game_service import use_item

    player = db_load(player_id)
    if not player:
        return {"msg": f"玩家 {player_id} 不存在", "成功": False}

    # 确认背包有道具
    if item_name not in player.inventory or player.inventory[item_name] <= 0:
        return {"msg": f"你没有{item_name}", "成功": False}

    result = use_item(player, item_name)
    result["使用后状态"] = player.model_dump(by_alias=True)
    db_save(player)
    return result


@app.post("/trade/list")
async def trade_list(
    player_id: str = "seller1", offer_item: str = "兽皮", offer_qty: int = 3,
    want_item: str = "草药绷带", want_qty: int = 2,
):
    """挂交易单"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    add_to_inventory(player, offer_item, offer_qty + 2)
    result = list_trade(player, offer_item, offer_qty, want_item, want_qty)
    result["背包"] = view_inventory(player)
    return result


@app.get("/trade/browse")
async def trade_browse():
    """浏览交易板"""
    result = browse_trades()
    return result


@app.post("/trade/accept")
async def trade_accept(buyer_id: str = "buyer1", trade_id: str = "trade_0001"):
    """接受交易"""
    from app.database import load_player as db_load, save_player as db_save
    buyer = db_load(buyer_id)
    if not buyer:
        buyer = Player(id=buyer_id, species=Species.TIGER)
    add_to_inventory(buyer, "草药绷带", 5)
    result = accept_trade(buyer, trade_id)
    result["背包"] = view_inventory(buyer)
    return result


@app.post("/settlement/can_build")
async def settlement_can_build(player_id: str = "test", building_str: str = "简易营地"):
    """检查是否可建造"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    building = Building(building_str)
    result = can_build(player, building)
    return result


@app.post("/settlement/build")
async def settlement_build(player_id: str = "test", building_str: str = "简易营地"):
    """建造建筑"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    building = Building(building_str)
    result = build(player, building)
    db_save(player)
    result["背包"] = view_inventory(player)
    return result


@app.get("/settlement/view")
async def settlement_view(player_id: str = "test"):
    """查看营地"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = view_settlement(player)
    return result


@app.post("/settlement/dismantle")
async def settlement_dismantle(player_id: str = "test", building_str: str = "木栅栏"):
    """拆除建筑"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = dismantle(player, building_str)
    db_save(player)
    result["背包"] = view_inventory(player)
    return result


@app.get("/shop/info")
async def shop_info(map_region: str = "都市商业街"):
    """查看商店"""
    result = get_shops_for_map(map_region)
    return result


@app.post("/shop/buy")
async def shop_buy(
    player_id: str = "test", map_region: str = "城郊青草地",
    shop_name: str = "", item_name: str = "野果",
):
    """购买商品"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = buy_item(player, map_region, shop_name, item_name)
    db_save(player)
    return result


@app.post("/map/move")
async def map_move(player_id: str = "test", target_map: str = "近郊小树林"):
    """移动到目标地图"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = move_to_map(player, target_map)
    if result.get("成功"):
        db_save(player)
    return result


@app.get("/map/moves")
async def map_moves(player_id: str = "test", map_region: str = "城郊青草地"):
    """查看可前往的地图"""
    result = get_available_moves(player_id, map_region)
    return result


@app.get("/map/explore")
async def explore_map_endpoint(player_id: str = "test", map_region: str = "城郊青草地"):
    """探索地图节点"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = map_region
    result = explore_map_node(player, map_region)
    db_save(player)
    return result


@app.get("/map/visible")
async def visible_maps(player_id: str = "test", map_region: str = "城郊青草地"):
    """查看可见地图"""
    from app.database import load_player as db_load
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = map_region
    result = get_visible_maps(player, map_region)
    return result


@app.post("/stall/open")
async def stall_open(player_id: str = "test"):
    """开启营业"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = "城郊青草地"
    add_to_inventory(player, "野果", 3)
    add_to_inventory(player, "木材", 5)
    items = [{"名称": "野果", "数量": 2, "价格": "石块x1"}, {"名称": "木材", "数量": 3, "价格": "野果x1"}]
    result = open_stall(player, items)
    return result


@app.post("/stall/close")
async def stall_close(player_id: str = "test"):
    """关闭营业"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = "城郊青草地"
    result = close_stall(player)
    return result


@app.post("/city/check")
async def city_check(player_id: str = "test", action: str = "撕咬", map_region: str = "都市商业街"):
    """测试都市区规则"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = map_region
    result = check_city_rules(player, action, map_region)
    if result["违规"]:
        result["传送后位置"] = player.current_map
    result["氛围"] = get_city_ambience(map_region)
    return result


@app.post("/instance/enter")
async def instance_enter(player_id: str = "test", map_name: str = "幻境心林"):
    """进入秘境"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = enter_instance(player, map_name)
    db_save(player)
    return result


@app.post("/instance/tick")
async def instance_tick_test(player_id: str = "test", map_name: str = "幻境心林"):
    """秘境Tick"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = map_name
    player.instance_ticks = 5
    result = instance_tick(player, map_name)
    db_save(player)
    return result


@app.post("/instance/exit")
async def instance_exit(player_id: str = "test"):
    """离开秘境"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.current_map = "幻境心林"
    result = exit_instance(player)
    db_save(player)
    return result


@app.post("/plant/growth")
async def plant_growth(player_id: str = "test", weather_str: str = "晴天", has_greenhouse: bool = False):
    """植物生长Tick"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    result = tick_plant_growth(player, weather_str, has_greenhouse)
    db_save(player)
    result["生长详情"] = get_plant_growth_stage(player)
    return result


@app.post("/plant/harvest")
async def plant_harvest(player_id: str = "test"):
    """收获植物"""
    from app.database import load_player as db_load, save_player as db_save
    player = db_load(player_id)
    if not player:
        player = Player(id=player_id, species=Species.TIGER)
    player.plant_growth = {"阶段": "成熟", "进度": 10, "总Tick": 30, "已收获": False}
    result = harvest_plant(player)
    db_save(player)
    result["背包"] = player.inventory
    return result
