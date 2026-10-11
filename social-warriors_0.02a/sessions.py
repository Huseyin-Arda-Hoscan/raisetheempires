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
    if 'playerInfo' not in save or 'maps' not in save or 'privateState' not in save:
        return False
    for m in save['maps']:
        if 'oil' not in m or 'steel' not in m:
            return False
        if 'stone' in m or 'food' in m:
            return False
        if 'items' not in m:
            return False
        if type(m['items']) != dict:
            return False
    return True

def load_saves():
    global __saves
    __saves = {}
    if not os.path.exists(SAVES_DIR):
        try:
            print(f"Creating '{SAVES_DIR}' folder...")
            os.mkdir(SAVES_DIR)
        except Exception:
            print(f"Could not create '{SAVES_DIR}' folder.")
            exit(1)
    if not os.path.isdir(SAVES_DIR):
        print(f"'{SAVES_DIR}' is not a folder... Move the file somewhere else.")
        exit(1)

    for file in os.listdir(SAVES_DIR):
        if not file.endswith('.json'):
            continue
        print(f" * Loading SAVE: village at {file}... ", end='')
        try:
            with open(os.path.join(SAVES_DIR, file), 'r', encoding='utf-8') as f:
                save = json.load(f)
        except json.decoder.JSONDecodeError:
            print('Corrupted JSON.')
            continue
        if not is_valid_village(save):
            print('Invalid Save')
            continue
        USERID = str(save['playerInfo']['pid'])
        print('PLAYER USERID:', USERID)
        __saves[USERID] = save
        modified = migrate_loaded_save(save)
        if modified:
            save_session(USERID)

    # 2. Veritabanindan (Supabase / Postgres / SQLite) kayitlari yukle
    try:
        from database import db_load_all_villages
        db_villages = db_load_all_villages()
        for vid, save in db_villages.items():
            if is_valid_village(save):
                __saves[str(vid)] = save
                print(f" * Loaded DB SAVE: {vid}")
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
        # Baslangic kaynaklari (arkadaslarla oynamayi hizlandirmak icin makul baslangic)
        vill['playerInfo']['cash'] = 500
        vill['maps'][0]['gold'] = 50000
        vill['maps'][0]['wood'] = 50000
        vill['maps'][0]['steel'] = 25000
        vill['maps'][0]['oil'] = 25000
        save_session(USERID)
    return USERID

def all_saves_userid():
    """Returns a list of the USERID of every saved village."""
    return list(__saves.keys())

def all_userid():
    """Returns a list of the USERID of every village."""
    return list(__villages.keys()) + list(__saves.keys()) + list(__quests.keys())

def save_info(USERID=None):
    if USERID not in __saves:
        return None
    save = __saves[USERID]
    default_map = save['playerInfo'].get('default_map', 0)
    empire_name = str(save['playerInfo'].get('name', 'Empire'))
    xp = save['maps'][default_map].get('xp', 0)
    level = save['maps'][default_map].get('level', 1)
    cash = save['playerInfo'].get('cash', 0)
    coins = save['maps'][default_map].get('gold', 0)
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
    for userid in __saves:
        info = save_info(userid)
        if info:
            saves_info.append(info)
    return saves_info

def session(USERID=None):
    if not USERID or not isinstance(USERID, str):
        return None
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
    except Exception:
        pass
                
    # 3. Yoksa yeni koy olustur (ASLA None donup oyunu cokertme)
    try:
        village = copy.deepcopy(__initial_village)
        village['version'] = None
        village['playerInfo']['pid'] = USERID
        village['playerInfo']['name'] = 'Commander'
        village['playerInfo']['cash'] = 500
        village['maps'][0]['gold'] = 50000
        village['maps'][0]['wood'] = 50000
        village['maps'][0]['steel'] = 25000
        village['maps'][0]['oil'] = 25000
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
    file = f'{USERID}.save.json'
    print(f" * Saving village at {file}... ", end='')
    village = session(USERID)
    if not village:
        print('Not found!')
        return
    save_path = os.path.join(SAVES_DIR, file)
    with open(save_path, 'w', encoding='utf-8') as f:
        json.dump(village, f, indent=4)
        
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

