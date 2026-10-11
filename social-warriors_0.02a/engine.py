# Source Generated with Decompyle++
# File: engine.pyc (Python 3.9)

import time
import json
from get_game_config import get_attribute_from_item_id

def timestamp_now():
    return int(time.time())


def map_add_item(map, index, item, x, y, orientation = None, timestamp = None, attr = None, store = (0, None, None, None, 1), player = {
    'map': dict,
    'index': int,
    'item': int,
    'x': int,
    'y': int,
    'orientation': int,
    'timestamp': int,
    'attr': dict,
    'store': list,
    'player': int }):
    if not attr:
        attr = { }
    if not store:
        store = []
    if not timestamp:
        timestamp = timestamp_now()
    if player == 1:
        properties = get_attribute_from_item_id(item, 'properties')
        if properties:
            properties = json.loads(properties)
            if 'friend_assistable' in properties and int(properties['friend_assistable']) > 0:
                attr['si'] = []
        click_to_build = get_attribute_from_item_id(item, 'clicks_to_build')
        if click_to_build and int(click_to_build) > 0:
            attr['nc'] = 0
    map['items'][str(index)] = [
        item,
        x,
        y,
        timestamp,
        orientation,
        store,
        attr,
        player]


def map_add_item_from_item(map = None, index = None, item = None):
    map['items'][str(index)] = item


def map_get_item(map = None, index = None):
    itemstr = str(index)
    if itemstr not in map['items']:
        return None
    return map['items'][itemstr]


def map_pop_item(map = None, index = None):
    itemstr = str(index)
    if itemstr not in map['items']:
        return None
    return map['items'].pop(itemstr)


def map_delete_item(map = None, index = None):
    itemstr = str(index)
    if itemstr not in map['items']:
        return None
    del map['items'][str(itemstr)]


def push_unit(unit = None, building = None):
    building[5].append(unit)
    building[3] = timestamp_now()


def pop_unit(building = None, item_id = None):
    index = None
    count = 0
    for item in building[5]:
        if item[0] == item_id:
            index = count
            break
        count += 1
    if index is not None:
        return building[5].pop(index)
    return None


def add_store_item(map = None, item = None, quantity = None):
    itemstr = str(item)
    if itemstr not in map['store']:
        map['store'][itemstr] = quantity
    else:
        map['store'][itemstr] += quantity


def remove_store_item(map = None, item = None, quantity = None):
    itemstr = str(item)
    if itemstr in map['store']:
        new_quantity = map['store'][itemstr] - quantity
        if new_quantity <= 0:
            del map['store'][itemstr]
        else:
            map['store'][itemstr] = new_quantity


def bought_unit_add(save = None, item = None):
    boughtUnits = save['privateState']['boughtUnits']
    if item not in boughtUnits:
        boughtUnits.append(item)


def unit_collection_complete(save = None, collection = None):
    unitCollectionsCompleted = save['privateState']['unitCollectionsCompleted']
    if collection not in unitCollectionsCompleted:
        unitCollectionsCompleted.append(collection)


def set_goals(privateState = None, goal = None, progress = None):
    goals = privateState['goals']
    while goal >= len(goals):
        goals.append(None)
    goals[goal] = progress


def inventory_set(privateState = None, item = None, quantity = None):
    itemstr = str(item)
    if quantity > 0:
        privateState['inventoryItems'][itemstr] = quantity
    else:
        del privateState['inventoryItems'][itemstr]


def inventory_add(privateState = None, item = None, quantity = None):
    itemstr = str(item)
    if itemstr not in privateState['inventoryItems']:
        privateState['inventoryItems'][itemstr] = quantity
    else:
        privateState['inventoryItems'][itemstr] += quantity


def inventory_remove(privateState = None, item = None, quantity = None):
    itemstr = str(item)
    if itemstr in privateState['inventoryItems']:
        new_quantity = privateState['inventoryItems'][itemstr] - quantity
        if new_quantity <= 0:
            del privateState['inventoryItems'][itemstr]
        else:
            privateState['inventoryItems'][itemstr] = new_quantity


def add_click(item = None):
    attr = item[6]
    if 'nc' not in attr:
        attr['nc'] = 1
    else:
        attr['nc'] += 1


def activate_item_click(item = None):
    attr = item[6]
    if 'nc' in attr:
        del attr['nc']


def buy_si_help(item = None):
    attr = item[6]
    if 'si' not in attr:
        attr['si'] = [0]
        return None
    attr['si'].append(0)


def finish_si(item = None):
    attr = item[6]
    if 'si' in attr:
        del attr['si']


def push_dead_unit(privateState = None, item = None):
    if item[7] != 1:
        return False
    properties = get_attribute_from_item_id(item[0], 'properties')
    if not properties:
        return False
    properties = json.loads(properties)
    if 'resurrectable' not in properties:
        return False
    if int(properties['resurrectable']) > 0:
        deadHeroes = privateState['deadHeroes']
        hero_id = str(item[0])
        if hero_id in deadHeroes:
            deadHeroes[hero_id] += 1
        else:
            deadHeroes[hero_id] = 1
        return True
    return False


def resurrect_hero(privateState = None, item = None):
    deadHeroes = privateState['deadHeroes']
    itemstr = str(item)
    if itemstr not in deadHeroes:
        return None
    num_heroes = deadHeroes[itemstr] - 1
    if num_heroes <= 0:
        del deadHeroes[itemstr]
    else:
        deadHeroes[itemstr] -= 1
    return None


def push_queue_unit(item = None):
    attr = item[6]
    if 'nu' in attr:
        attr['nu'] += 1
    else:
        attr['nu'] = 1
    attr['ts'] = timestamp_now()


def pop_queue_unit(item = None):
    attr = item[6]
    if 'nu' not in attr:
        return None
    nu = attr['nu'] - 1
    if nu > 0:
        attr['nu'] = nu
        attr['ts'] = timestamp_now()
    else:
        del attr['nu']
        if 'ts' in attr:
            del attr['ts']
        if 'ui' in attr:
            del attr['ui']


def push_queue_unit2(item = None, unit_id = None):
    attr = item[6]
    if 'nu' in attr:
        attr['nu'] += 1
    else:
        attr['nu'] = 1
    attr['ts'] = timestamp_now()
    attr['ui'] = unit_id


def map_lose_item(map = None, privateState = None, item = None, quantity = 1):
    qty = quantity
    map_items = map['items']
    while qty > 0:
        deleted = False
        for index in map_items:
            if map_items[index][0] == item and map_items[index][7]:
                _item = map_pop_item(map, index)
                push_dead_unit(privateState, _item)
                deleted = True
                break
        if not deleted:
            return None
        qty -= 1
    return None


def reset_stuff(save = None):
    now = timestamp_now()
    for map in save['maps']:
        last_trade = map['timestampLastTrade']
        if now // 86400 != last_trade // 86400:
            map['numTradesDone'] = 0
    privateState = save['privateState']
    if 'timeStampDartsReset' in privateState:
        last_darts_reset = privateState['timeStampDartsReset'] + 259200
        temp = now + 259200
        if temp // 604800 != last_darts_reset // 604800:
            privateState['timeStampDartsReset'] = 0


def apply_resources(save = None, map = None, resource = None):
    unknown = resource[0]
    xp = resource[1]
    gold = resource[2]
    wood = resource[3]
    oil = resource[4]
    steel = resource[5]
    cash = resource[6]
    mana = resource[7]
    map['xp'] = max(map['xp'] + xp, 0)
    map['gold'] = max(map['gold'] + gold, 0)
    map['wood'] = max(map['wood'] + wood, 0)
    map['oil'] = max(map['oil'] + oil, 0)
    map['steel'] = max(map['steel'] + steel, 0)
    save['playerInfo']['cash'] = max(save['playerInfo']['cash'] + cash, 0)
    save['privateState']['mana'] = max(save['privateState']['mana'] + mana, 0)

