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
    assert isinstance(USERID, str)
    if USERID in __saves:
        return __saves[USERID]
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
    print('Done.')
