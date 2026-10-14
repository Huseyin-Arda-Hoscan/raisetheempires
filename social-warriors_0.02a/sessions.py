import json
import os
import copy
import uuid
import random
from version import version_code, migrate_loaded_save
from engine import timestamp_now
from constants import Quests
from bundle import VILLAGES_DIR, QUESTS_DIR, SAVES_DIR

__villages = {}
__quests = {}
__saves = {}

__initial_village_path = os.path.join(VILLAGES_DIR, 'initial.json')
__initial_village = json.load(open(__initial_village_path, 'r', encoding='utf-8'))

def is_valid_village(save=None):
    if not isinstance(save, dict):
        return False
    if 'playerInfo' not in save or 'maps' not in save:
        return False
    if not isinstance(save['maps'], list) or len(save['maps']) == 0:
        return False
    if not isinstance(save.get('playerInfo'), dict):
        return False
    if not isinstance(save['maps'][0], dict):
        return False
    if 'privateState' not in save or not isinstance(save.get('privateState'), dict):
        save['privateState'] = {}
    return True

def load_saves():
    global __saves
    if not os.path.exists(SAVES_DIR):
        try:
            os.makedirs(SAVES_DIR, exist_ok=True)
        except Exception:
            pass

    if os.path.exists(SAVES_DIR) and os.path.isdir(SAVES_DIR):
        for file in os.listdir(SAVES_DIR):
            if not file.endswith('.json'):
                continue
            try:
                with open(os.path.join(SAVES_DIR, file), 'r', encoding='utf-8') as f:
                    save = json.load(f)
                if is_valid_village(save):
                    USERID = str(save['playerInfo'].get('pid', file.split('.')[0]))
                    if USERID not in __saves:
                        __saves[USERID] = save
                        migrate_loaded_save(save)
            except Exception as e:
                print(f"Error loading local save {file}: {e}")

    # 2. Veritabanindan (Supabase / Postgres / SQLite) kayitlari yukle
    try:
        from database import db_load_all_villages
        db_villages = db_load_all_villages()
        for vid, save in db_villages.items():
            if is_valid_village(save):
                vid_str = str(vid)
                if vid_str not in __saves:
                    __saves[vid_str] = save
                    print(f" * Loaded DB SAVE: {vid_str}")
    except Exception as e:
        print(f" * DB Save Load Note: {e}")

def load_static_villages():
    global __villages
    __villages = {}
    if not os.path.exists(VILLAGES_DIR):
        return
    for file in os.listdir(VILLAGES_DIR):
        if file == 'initial.json' or not file.endswith('.json'):
            continue
        print(f" * Loading STATIC NEIGHBOUR: village at {file}... ", end='')
        try:
            with open(os.path.join(VILLAGES_DIR, file), 'r', encoding='utf-8') as f:
                village = json.load(f)
        except Exception:
            print('Error loading static village')
            continue
        if not is_valid_village(village):
            print('Invalid neighbour')
            continue
        USERID = str(village['playerInfo']['pid'])
        print('STATIC USERID:', USERID)
        __villages[USERID] = village

def load_quests():
    global __quests
    __quests = {}
    if not os.path.exists(QUESTS_DIR):
        return
    for file in os.listdir(QUESTS_DIR):
        if not file.endswith('.json'):
            continue
        try:
            with open(os.path.join(QUESTS_DIR, file), 'r', encoding='utf-8') as f:
                village = json.load(f)
        except Exception:
            continue
        if not is_valid_village(village):
            print('Invalid Quest')
            continue
        QUESTID = str(village['playerInfo']['pid'])
        assert file.split('.')[0] == QUESTID
        quest_name = Quests.QUEST[QUESTID] if QUESTID in Quests.QUEST else '?'
        print(f' * Loading QUEST: {quest_name} ({QUESTID})')
        __quests[QUESTID] = village

def new_village():
    USERID = str(uuid.uuid4())
    assert USERID not in all_userid()
    village = copy.deepcopy(__initial_village)
    village['version'] = None
    village['playerInfo']['pid'] = USERID
    village['maps'][0]['timestamp'] = timestamp_now()
    village['privateState']['timeStampDartsReset'] = 0
    migrate_loaded_save(village)
    __saves[USERID] = village
    save_session(USERID)
    print('Done.')
    return USERID

def create_user_village(empire_name='Commander'):
    USERID = new_village()
    vill = session(USERID)
    if vill:
        vill['playerInfo']['name'] = str(empire_name)
        # Baslangic kaynaklari (Egitim gorevinde depo doldu hatasi vermemesi icin limit dahilinde)
        vill['playerInfo']['cash'] = 500
        vill['maps'][0]['gold'] = 1000
        vill['maps'][0]['wood'] = 200
        vill['maps'][0]['steel'] = 200
        vill['maps'][0]['oil'] = 200
        save_session(USERID)
    return USERID

def all_saves_userid():
    """Returns a list of the USERID of every saved village."""
    return list(__saves.keys())

def all_userid():
    """Returns a list of the USERID of every village."""
    return list(__villages.keys()) + list(__saves.keys()) + list(__quests.keys())

def save_info(USERID=None):
    if not USERID:
        return None
    USERID = str(USERID)
    save = __saves.get(USERID) or session(USERID)
    if not save:
        return None
    default_map = save.get('playerInfo', {}).get('default_map', 0)
    empire_name = str(save.get('playerInfo', {}).get('name', 'Empire'))
    maps = save.get('maps', [{}])
    target_map = maps[default_map] if default_map < len(maps) else maps[0]
    xp = target_map.get('xp', 0)
    level = target_map.get('level', 1)
    cash = save.get('playerInfo', {}).get('cash', 0)
    coins = target_map.get('gold', 0)
    return {
        'userid': USERID,
        'name': empire_name,
        'xp': xp,
        'level': level,
        'cash': cash,
        'coins': coins
    }

def all_saves_info():
    saves_info = []
    for userid in list(__saves.keys()):
        info = save_info(userid)
        if info:
            saves_info.append(info)
    return saves_info

def session(USERID=None):
    if not USERID:
        return None
    USERID = str(USERID)
    if USERID in __saves:
        return __saves[USERID]
        
    # 1. Diskten yuklemeyi dene
    for fname in [f"{USERID}.save.json", f"{USERID}.json"]:
        save_file = os.path.join(SAVES_DIR, fname)
        if os.path.exists(save_file):
            try:
                with open(save_file, 'r', encoding='utf-8') as f:
                    s = json.load(f)
                    if is_valid_village(s):
                        __saves[USERID] = s
                        return s
            except Exception:
                pass

    # 2. Veritabanindan (Supabase / Postgres) yuklemeyi dene
    try:
        from database import db_load_village
        db_s = db_load_village(USERID)
        if db_s and is_valid_village(db_s):
            __saves[USERID] = db_s
            return db_s
    except Exception as e:
        print(f"Error loading village from DB for {USERID}: {e}")
                
    # 3. Yoksa yeni koy olustur (ASLA None donup oyunu cokertme)
    try:
        village = copy.deepcopy(__initial_village)
        village['version'] = None
        village['playerInfo']['pid'] = USERID
        village['playerInfo']['name'] = 'Commander'
        village['playerInfo']['cash'] = 500
        village['maps'][0]['gold'] = 1000
        village['maps'][0]['wood'] = 200
        village['maps'][0]['steel'] = 200
        village['maps'][0]['oil'] = 200
        village['maps'][0]['timestamp'] = timestamp_now()
        village['privateState']['timeStampDartsReset'] = 0
        migrate_loaded_save(village)
        __saves[USERID] = village
        save_session(USERID)
        return village
    except Exception as e:
        print(f"Error fallback village for {USERID}: {e}")
        return None

def neighbor_session(USERID=None):
    assert isinstance(USERID, str)
    if USERID in __saves:
        return __saves[USERID]
    if USERID in __quests:
        return __quests[USERID]
    if USERID in __villages:
        return __villages[USERID]
    return None

def fb_friends_str(USERID=None):
    friends = []
    for key in __villages:
        vill = __villages[key]
        pid = str(vill['playerInfo']['pid'])
        if pid in ('100000030', '100000031'):
            continue
        friends.append({
            'uid': pid,
            'pic_square': vill['playerInfo'].get('pic', 'avatars/nerroth.png')
        })
    for key in __saves:
        vill = __saves[key]
        pid = str(vill['playerInfo']['pid'])
        if pid == str(USERID):
            continue
        friends.append({
            'uid': pid,
            'pic_square': vill['playerInfo'].get('pic', 'avatars/avatar_basic.png')
        })
    return friends

def neighbors(USERID=None):
    neighs = []
    for key in __villages:
        vill = __villages[key]
        pid = str(vill['playerInfo']['pid'])
        if pid in ('100000030', '100000031'):
            continue
        neigh = copy.deepcopy(vill['playerInfo'])
        neigh['xp'] = vill['maps'][0].get('xp', 0)
        neigh['level'] = vill['maps'][0].get('level', 1)
        neigh['gold'] = vill['maps'][0].get('gold', 0)
        neigh['wood'] = vill['maps'][0].get('wood', 0)
        neigh['oil'] = vill['maps'][0].get('oil', 0)
        neigh['steel'] = vill['maps'][0].get('steel', 0)
        neighs.append(neigh)
    for key in __saves:
        vill = __saves[key]
        pid = str(vill['playerInfo']['pid'])
        if pid == str(USERID):
            continue
        neigh = copy.deepcopy(vill['playerInfo'])
        neigh['xp'] = vill['maps'][0].get('xp', 0)
        neigh['level'] = vill['maps'][0].get('level', 1)
        neigh['gold'] = vill['maps'][0].get('gold', 0)
        neigh['wood'] = vill['maps'][0].get('wood', 0)
        neigh['oil'] = vill['maps'][0].get('oil', 0)
        neigh['steel'] = vill['maps'][0].get('steel', 0)
        neighs.append(neigh)
    return neighs

def save_session(USERID=None):
    if not USERID:
        return
    USERID = str(USERID)
    file = f'{USERID}.save.json'
    print(f" * Saving village {USERID}... ", end='')
    village = __saves.get(USERID) or session(USERID)
    if not village:
        print('Not found!')
        return
    try:
        if not os.path.exists(SAVES_DIR):
            os.makedirs(SAVES_DIR, exist_ok=True)
        save_path = os.path.join(SAVES_DIR, file)
        with open(save_path, 'w', encoding='utf-8') as f:
            json.dump(village, f, indent=4)
    except Exception as e:
        print(f" * Disk Save Note: {e}")
        
    # Supabase / DB'ye de kalici olarak yaz
    try:
        from database import db_save_village
        db_save_village(USERID, village)
    except Exception as e:
        print(f" * DB Save Note: {e}")
        
    print('Done.')

def modify_player_resources(village_id, cash=None, gold=None, wood=None, steel=None, oil=None, level=None, xp=None):
    vill = session(str(village_id))
    if not vill:
        return False
    if cash is not None:
        vill['playerInfo']['cash'] = int(cash)
    if gold is not None:
        vill['maps'][0]['gold'] = int(gold)
    if wood is not None:
        vill['maps'][0]['wood'] = int(wood)
    if steel is not None:
        vill['maps'][0]['steel'] = int(steel)
    if oil is not None:
        vill['maps'][0]['oil'] = int(oil)
    if level is not None:
        vill['maps'][0]['level'] = int(level)
    if xp is not None:
        vill['maps'][0]['xp'] = int(xp)
    save_session(str(village_id))
    return True

def gift_all_players(cash=0, gold=0, wood=0, steel=0, oil=0):
    count = 0
    for uid in __saves:
        vill = __saves[uid]
        if cash:
            vill['playerInfo']['cash'] = vill['playerInfo'].get('cash', 0) + int(cash)
        if gold:
            vill['maps'][0]['gold'] = vill['maps'][0].get('gold', 0) + int(gold)
        if wood:
            vill['maps'][0]['wood'] = vill['maps'][0].get('wood', 0) + int(wood)
        if steel:
            vill['maps'][0]['steel'] = vill['maps'][0].get('steel', 0) + int(steel)
        if oil:
            vill['maps'][0]['oil'] = vill['maps'][0].get('oil', 0) + int(oil)
        save_session(uid)
        count += 1
    return count

def add_item_to_player_store(village_id, item_id, quantity=1):
    vill = session(str(village_id))
    if not vill:
        return False
    from engine import add_store_item, bought_unit_add
    item_id = int(item_id)
    quantity = int(quantity)
    add_store_item(vill['maps'][0], item_id, quantity)
    bought_unit_add(vill, item_id)
    save_session(str(village_id))
    return True

