# Source Generated with Decompyle++
# File: command.pyc (Python 3.9)

import json
from sessions import session, save_session
from get_game_config import get_name_from_item_id, get_attribute_from_item_id, get_attribute_from_goal_id, get_xp_from_level, get_weekly_reward_length, get_inventory_item_name, get_collection_name, get_collection_prize, get_premium_days
from constants import Constant
from engine import timestamp_now, apply_resources, map_add_item, map_add_item_from_item, map_get_item, map_pop_item, map_delete_item, push_unit, pop_unit, add_store_item, remove_store_item, bought_unit_add, unit_collection_complete, set_goals, inventory_set, inventory_add, inventory_remove, add_click, activate_item_click, buy_si_help, finish_si, push_dead_unit, resurrect_hero, push_queue_unit, pop_queue_unit, map_lose_item, push_queue_unit2
from math import ceil

def command(USERID, data):
    first_number = data.get('first_number')
    publishActions = data.get('publishActions')
    timestamp = data.get('ts')
    tries = data.get('tries')
    accessToken = data.get('accessToken')
    commands = data.get('commands', [])
    for i, comm in enumerate(commands):
        try:
            map_id = comm[0]
            cmd = comm[1]
            args = comm[2]
            resources_changed = comm[3]
            do_command(USERID, map_id, cmd, args, resources_changed)
        except Exception as e:
            print(f"[COMMAND ERROR in {comm[1] if len(comm)>1 else 'unknown'}]: {e}")
    save_session(USERID)


def do_command(USERID, map_id, cmd, args, resources_changed):
    save = session(USERID)
    time_now = timestamp_now()
    map = save['maps'][map_id]
    print(' [+] COMMAND: ', cmd, '(', args, ') -> ', sep='', end='')
    apply_resources(save, map, resources_changed)
    if cmd == 'buy':
        item_index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        playerID = args[4]
        orientation = args[5] if len(args) > 5 else 0
        unknown = args[6] if len(args) > 6 else 0
        reason = args[7] if len(args) > 7 else ''
        if playerID == 1:
            bought_unit_add(save, item_id)
        map_add_item(map, item_index, item_id, x, y, orientation=orientation, player=playerID)
        print('Add', str(get_name_from_item_id(item_id)), 'at', f'({x},{y})')
        return None
    elif cmd == 'complete_tutorial':
        tutorial_step = args[0]
        print('Tutorial step', tutorial_step, 'reached.')
        save['playerInfo']['tutorial_step'] = tutorial_step
        if tutorial_step >= 12 or tutorial_step == 15 or tutorial_step >= 25:
            print('Tutorial COMPLETED!')
            save['playerInfo']['completed_tutorial'] = 1
        return None
    elif cmd == 'set_goals':
        goal_id = args[0]
        try:
            if isinstance(args[1], str):
                progress = json.loads(args[1])
            else:
                progress = args[1]
        except Exception:
            progress = args[1]
        set_goals(save['privateState'], goal_id, progress)
        print("Goal '", get_attribute_from_goal_id(goal_id, 'title'), "' progressed.", sep='')
    elif cmd == 'complete_goal':
        goal_id = args[0]
        print("Goal '", get_attribute_from_goal_id(goal_id, 'title'), "' completed.", sep='')
    elif cmd == 'level_up':
        new_level = args[0]
        map['level'] = new_level
        print('Level up! New level:', new_level)
    elif cmd == 'set_quest_var':
        key = args[0]
        value = args[1]
        if key == 'idSimpleChapter':
            print(f'''Ignored {key}''')
            return None
        questVars = map['currentQuestVars']
        if key == 'id':
            map['idCurrentMission'] = value
        if not map['currentQuestVars']:
            map['currentQuestVars'] = { }
        map['currentQuestVars'][key] = value
        print(f'''Set current quest {key} to \'{value}\'''')
    elif cmd == 'move':
        item_index = args[0]
        x = args[1]
        y = args[2]
        frame = args[3]
        string = args[4]
        item = map_get_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        item[1] = x
        item[2] = y
        print('Move', str(get_name_from_item_id(item[0])), 'to', f'''({x},{y})''')
    elif cmd == 'collect':
        item_index = args[0]
        item = map_get_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        item[3] = time_now
        print('Collect', str(get_name_from_item_id(item[0])))
    elif cmd == 'sell':
        item_index = args[0]
        reason = args[1]
        item = map_get_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        resurrectable = None
        if reason == 'KILL':
            resurrectable = push_dead_unit(save['privateState'], item)
        name = str(get_name_from_item_id(item[0]))
        map_delete_item(map, item_index)
        if resurrectable:
            print(f'''Remove {name} (Resurrectable). Reason: {reason}''')
        else:
            print(f'''Remove {name}. Reason: {reason}''')
    elif cmd == 'kill':
        item_index = args[0]
        reason = args[1]
        item = map_get_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        name = str(get_name_from_item_id(item[0]))
        map_delete_item(map, item_index)
        print(f'''Kill {name}. Reason: {reason}''')
    elif cmd == 'kill_iid':
        item_id = args[0]
        reason_str = args[1]
        print('Killed', str(get_name_from_item_id(item_id)))
    elif cmd == 'batch_remove':
        index_list = json.loads(args[0])
        for index in index_list:
            map_delete_item(map, index)
        print(f'''Removed {len(index_list)} items.''')
    elif cmd == 'orient':
        item_index = args[0]
        orientation = args[1]
        item = map_get_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        item[4] = int(orientation)
        print('Rotate', str(get_name_from_item_id(item[0])))
    elif cmd == 'expand':
        expansion = args[0]
        map['expansions'] += [
            int(expansion)]
        print('Unlocked Expansion', expansion)
    elif cmd == 'store_item':
        item_index = args[0]
        item = map_pop_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        item_id = item[0]
        name = str(get_name_from_item_id(item_id))
        add_store_item(map, item_id)
        print(f'''Store {name}.''')
    elif cmd == 'place_stored_item':
        item_index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        playerID = args[4]
        orientation = args[5]
        unknown_autoactivable_bool = args[6]
        unknown_imgIndex = args[7]
        name = str(get_name_from_item_id(item_id))
        remove_store_item(map, item_id)
        map_add_item(map, item_index, item_id, x, y, orientation=orientation, player=playerID)
        bought_unit_add(save, item_id)
        print(f'''Placed stored {name}.''')
    elif cmd == 'sell_stored_item':
        item_id = args[0]
        name = str(get_name_from_item_id(item_id))
        remove_store_item(map, item_id)
        print(f'''Sell stored {name}.''')
    elif cmd == 'store_add_items':
        item_id_list = args[0]
        for item_id in item_id_list:
            add_store_item(map, item_id)
            bought_unit_add(save, item_id)
        print('Add to store', ', '.join([str(get_name_from_item_id(i)) for i in item_id_list]))
    elif cmd == 'next_research_step':
        _type = args[0]
        save['privateState']['researchStepNumber'][_type] += 1
        save['privateState']['timeStampDoResearch'][_type] = time_now
        print('Research step for', [
            'Area 51',
            'Robotic Center'][_type])
    elif cmd == 'research_buy_step_cash':
        cash = args[0]
        _type = args[1]
        save['privateState']['timeStampDoResearch'][_type] = 0
        print('Buy research step for', [
            'Area 51',
            'Robotic Center'][_type])
    elif cmd == 'next_research_item':
        _type = args[0]
        save['privateState']['researchItemNumber'][_type] += 1
        save['privateState']['researchStepNumber'][_type] = 0
        save['privateState']['timeStampDoResearch'][_type] = 0
        print('Finished research for', [
            'Area 51',
            'Robotic Center'][_type])
    elif cmd == 'reset_research_item':
        _type = args[0]
        save['privateState']['researchItemNumber'][_type] = 0
        save['privateState']['researchStepNumber'][_type] = 0
        save['privateState']['timeStampDoResearch'][_type] = 0
        print('Reset research for', [
            'Area 51',
            'Robotic Center'][_type])
    elif cmd == 'flash_debug':
        cash = args[0]
        unknown = args[1]
        xp = args[2]
        gold = args[3]
        oil = args[4]
        steel = args[5]
        wood = args[6]
        playerInfo = save['playerInfo']
        playerInfo['cash'] = cash
        map['xp'] = xp
        map['gold'] = gold
        map['oil'] = oil
        map['steel'] = steel
        map['wood'] = wood
        print('Keep up with resources.')
    elif cmd == 'add_xp_unit':
        item_index = args[0]
        xp_gain = args[1]
        level = None
        if len(args) > 2:
            level = args[2]
        item = map_get_item(map, item_index)
        if not item:
            print('Error: item not found.')
            return None
        attr = item[6]
        if 'xp' not in attr:
            attr['xp'] = xp_gain
        else:
            attr['xp'] += xp_gain
        if level:
            print(f'''{get_name_from_item_id(item[0])} +{xp_gain}xp BOUGHT LEVEL UP -> {level}''')
        else:
            print(f'''{get_name_from_item_id(item[0])} +{xp_gain}xp''')
    elif cmd == 'weekly_reward':
        if len(args) > 4:
            item_index = args[0]
            item_id = args[1]
            x = args[2]
            y = args[3]
            playerID = args[4]
            map_add_item(map, item_index, item_id, x, y, player=playerID)
            bought_unit_add(save, item_id)
            print('Won', str(get_name_from_item_id(item_id)))
        else:
            print('Won resources')
        save['privateState']['timeStampMondayBonus'] = time_now
        save['privateState']['weeklyRewardIndex'] = (save['privateState']['weeklyRewardIndex'] + 1) % get_weekly_reward_length()
    elif cmd == 'push_unit':
        index_unit = args[0]
        index_building = args[1]
        unit = map_pop_item(map, index_unit)
        building = map_get_item(map, index_building)
        if not unit:
            print('Error: unit not found.')
            return None
        if not building:
            print('Error: building not found.')
            return None
        push_unit(unit, building)
        print('Pushed', str(get_name_from_item_id(unit[0])), 'to', str(get_name_from_item_id(building[0])))
    elif cmd == 'pop_unit':
        index_building = args[0]
        index_unit = args[1]
        item_id = args[2]
        x = args[3]
        y = args[4]
        playerID = args[5]
        unknown = args[6]
        building = map_get_item(map, index_building)
        if not building:
            print('Error: building not found.')
            return None
        unit = pop_unit(building, item_id)
        if not unit:
            print('Error: no units in building.')
            return None
        unit[0] = item_id
        unit[1] = x
        unit[2] = y
        unit[7] = playerID
        map_add_item_from_item(map, index_unit, unit)
        print('Popped', str(get_name_from_item_id(unit[0])), 'from', str(get_name_from_item_id(building[0])))
    elif cmd == 'activate':
        item_id = args[0]
        activate = args[1]
        item = map_get_item(map, item_id)
        if not item:
            print('Error: item not found.')
            return None
        if None > 0:
            item[3] = time_now
            item[6]['cp'] = args[1]
            print('Activated', str(get_name_from_item_id(item[0])), 'Set CP to', str(activate))
        else:
            item[3] = time_now
            item[6] = { }
            print('Deactivated', str(get_name_from_item_id(item[0])))
    elif cmd == 'collect_mission':
        next_mission = args[0]
        if next_mission > 99:
            next_mission = 1
        map['idCurrentMission'] = str(next_mission)
        map['timestampLastChapter'] = time_now
        map['currentQuestVars'] = { }
        print('Advanced to mission', str(next_mission))
    elif cmd == 'win_daily_bonus':
        item = args[0]
        next_id = args[1] + 1
        privateState = save['privateState']
        if next_id > 5:
            next_id = 1
        privateState['timestampLastBonus'] = time_now
        privateState['bonusNextId'] = next_id
        if item > 0:
            bought_unit_add(save, item)
            add_store_item(map, item)
            print('Put', str(get_name_from_item_id(item)), 'in storage')
        else:
            print('Rewarded resources')
    elif cmd == 'trade_resource':
        resource_type = args[0]
        sold = args[1]
        num_trades = map['numTradesDone'] + 1
        map['numTradesDone'] = min(20, num_trades)
        map['timestampLastTrade'] = time_now
        print(f'''Remaining trades: {20 - num_trades}''')
    elif cmd == 'buy_stored_item_cash':
        item_id = args[0]
        bought_unit_add(save, item_id)
        add_store_item(map, item_id)
        print('Bought', str(get_name_from_item_id(item_id)), 'from unit collection')
    elif cmd == 'unit_collections_completed':
        collection_id = args[0]
        unit_collection_complete(save, collection_id)
        print('Completed unit collection', str(collection_id))
    elif cmd == 'add_inventory_item':
        item = args[0]
        quantity = args[1]
        inventory_add(save['privateState'], item, quantity)
        name = get_inventory_item_name(item)
        print(f'''Added {quantity} {name} to inventory''')
    elif cmd == 'remove_inventory_item':
        item = args[0]
        quantity = args[1]
        inventory_remove(save['privateState'], item, quantity)
        name = get_inventory_item_name(item)
        print(f'''Removed {quantity} {name} from inventory''')
    elif cmd == 'complete_collection':
        collection_id = args[0]
        bought = args[1]
        privateState = save['privateState']
        prize = get_collection_prize(collection_id)
        for key in prize:
            add_store_item(map, int(key), prize[key])
        collection_name = get_collection_name(collection_id)
        if collection_id not in privateState['collections']:
            privateState['collections'].append(collection_id)
        if bought:
            print(f'''Bought {collection_name}''')
        else:
            print(f'''Completed {collection_name}''')
    elif cmd == 'add_click':
        index = args[0]
        item = map_get_item(map, index)
        if not item:
            print('Error: item not found.')
            return None
        add_click(item)
        print('Added click to', str(get_name_from_item_id(item[0])))
    elif cmd == 'activate_item_click':
        index = args[0]
        item = map_get_item(map, index)
        if not item:
            print('Error: item not found.')
            return None
        activate_item_click(item)
        print('Click to build finished for', str(get_name_from_item_id(item[0])))
    elif cmd == 'buy_si_help':
        index = args[0]
        item = map_get_item(map, index)
        if not item:
            print('Error: item not found.')
            return None
        buy_si_help(item)
        print('Bought SI help for', str(get_name_from_item_id(item[0])))
    elif cmd == 'finish_si':
        index = args[0]
        item = map_get_item(map, index)
        if not item:
            print('Error: item not found.')
            return None
        finish_si(item)
        print('Finished SI for', str(get_name_from_item_id(item[0])))
    elif cmd == 'darts_reset':
        seed = args[0]
        privateState = save['privateState']
        privateState['dartsRandomSeed'] = seed
        privateState['dartsBalloonsShot'] = []
        privateState['dartsHasFree'] = True
        privateState['dartsGotExtra'] = False
        privateState['timeStampDartsReset'] = time_now
        privateState['timeStampDartsNewFree'] = time_now
        print(f'''Reset Targets (SEED: {seed})''')
    elif cmd == 'darts_new_free':
        privateState = save['privateState']
        privateState['dartsHasFree'] = True
        privateState['timeStampDartsNewFree'] = time_now
        print('Given free Targets shot')
    elif cmd == 'darts_shoot_balloon':
        index = args[0]
        won_extra = args[1]
        privateState = save['privateState']
        targets = privateState['dartsBalloonsShot']
        if index not in targets:
            targets.append(index)
        privateState['dartsHasFree'] = False
        privateState['timeStampDartsNewFree'] = time_now
        if won_extra:
            privateState['dartsGotExtra'] = True
        if won_extra:
            print(f'''Shot Target {index} and won the game!''')
        else:
            print(f'''Shot Target {index}''')
    elif cmd == 'buy_premium_account':
        package_index = args[0]
        days = get_premium_days(package_index)
        privateState = save['privateState']
        ts_premium = privateState['timeStampEndPremium']
        if time_now >= ts_premium:
            privateState['timeStampEndPremium'] = time_now + days * 86400
            print(f'''Bought Premium Account for {days} day(s)''')
        else:
            privateState['timeStampEndPremium'] += days * 86400
            print(f'''Extended Premium Account for {days} day(s)''')
    elif cmd == 'resurrect_hero':
        index = args[0]
        item_id = args[1]
        x = args[2]
        y = args[3]
        used_syringe = args[4]
        resurrect_hero(save['privateState'], item_id)
        map_add_item(map, index, item_id, x, y)
        print('Resurrected', str(get_name_from_item_id(item_id)))
    elif cmd == 'set_resource_allies':
        resource = args[0]
        index = args[1]
        item = map_get_item(map, index)
        if item:
            item[3] = time_now
            finish_si(item)
        map['resourceAlliesMarket'] = resource
        print('Set Allies Market resource')
    elif cmd == 'buy_mana_new':
        print('Bought mana')
    elif cmd == 'buy_magic':
        magic_id = args[0]
        privateState = save['privateState']
        magics = privateState['magics']
        if str(magic_id) in magics:
            magics[str(magic_id)] += min(50, magics[str(magic_id)] + 1)
        else:
            magics[str(magic_id)] = 0
        print('Bought magic spell')
    elif cmd == 'use_magic':
        magic_id = args[0]
        privateState = save['privateState']
        magics = privateState['magics']
        if str(magic_id) in magics:
            magics[str(magic_id)] = min(50, magics[str(magic_id)] + 1)
        else:
            magics[str(magic_id)] = 0
        print('Used magic spell')
    elif cmd == 'push_queue_unit':
        index = args[0]
        item = map_get_item(map, index)
        if not item:
            print('Error: item not found.')
            return None
        push_queue_unit(item)
        print('Pushed unit.')
    elif cmd == 'push_queue_unit2':
        atom_fusion_index = args[0]
        unit_id = args[1]
        atom_fusion = map_get_item(map, atom_fusion_index)
        if not atom_fusion:
            print('Error: Atom Fusion not found.')
            return None
        push_queue_unit2(atom_fusion, unit_id)
        print('Pushed', get_name_from_item_id(unit_id), 'to Atom Fusion.')
    elif cmd == 'pop_queue_unit':
        index = args[0]
        item = map_get_item(map, index)
        if not item:
            print('Error: item not found.')
            return None
        pop_queue_unit(item)
        print('Popped unit.')
    elif cmd == 'buy_offer_pack':
        package_id = args[0]
        item_list = args[1]
        items = json.loads(item_list)
        for item in items:
            add_store_item(map, item)
        print('Bought Offer Pack')
    elif cmd == 'buy_powerups':
        powerup_index = args[0]
        print('Buy Atom Fusion PowerUP')
    elif cmd == 'soulmixer_speedup':
        atom_fusion_index = args[0]
        atom_fusion = map_get_item(map, atom_fusion_index)
        start = atom_fusion[6]['ts']
        now = timestamp_now()
        sm_training_time = int(get_attribute_from_item_id(atom_fusion[6]['ui'], 'sm_training_time'))
        remaining_time = sm_training_time - now - start
        cash_cost = ceil(remaining_time / 3600)
        atom_fusion[6]['ts'] = 0
        print(f'''Buy Atom Fusion Speedup for {get_name_from_item_id(atom_fusion[6]['ui'])}. Cost: {cash_cost} cash.''')
    elif cmd == 'admin_set_quest_rank':
        quest_index = args[0]
        difficulty = args[1]
        privateState = save['privateState']
        privateState['questsRank'][str(quest_index)] = difficulty
    elif cmd == 'end_quest':
        response = None
        try:
            if isinstance(args[0], dict):
                response = args[0]
            else:
                response = json.loads(args[0])
        except Exception:
            print('Error: Failed to parse end_quest command.')
            return None
        if not response:
            print('Error: Failed to parse end_quest command.')
            return None
        win = response.get('win')
        duration = response.get('duration', 0)
        units = response.get('units') or []
        _map = response.get('map', 0)
        difficulty = response.get('difficulty')
        if difficulty is not None:
            difficulty = max(1, min(3, difficulty))
        voluntary_end = response.get('voluntary_end', True)
        quest_id = response.get('quest_id')
        privateState = save['privateState']
        for unit in units:
            lost = max(0, unit[2] - unit[3])
            if lost > 0:
                item = unit[0]
                print(f'Lost {lost} {get_name_from_item_id(unit[0])}(s)')
                map_lose_item(map, privateState, unit[0], lost)
        if not quest_id:
            print('Error: No quest played.')
            return None
        if 'questTimes' not in map:
            map['questTimes'] = {}
        map['questTimes'][str(quest_id)] = None
        if win:
            print(f'Won quest {quest_id}')
        else:
            print(f'Failed quest {quest_id}')
        return None

    elif cmd == 'end_attack':
        response = None
        try:
            if isinstance(args[0], dict):
                response = args[0]
            else:
                response = json.loads(args[0])
        except Exception:
            print('Error: Failed to parse end_attack command.')
            return None
        if not response:
            print('Error: Failed to parse end_attack command.')
            return None
        voluntary_end = response.get('voluntary_end')
        victim = response.get('victim') or {}
        attacker = response.get('attacker') or {}
        resources = response.get('resources')
        honor = response.get('honor', 0)
        duration = response.get('duration', 0)
        townhall_gold = response.get('townhall_gold', 0)
        win = response.get('win', False)
        different_island = response.get('different_island', True)
        victim_units = response.get('victim_units') or []
        attacker_units = response.get('attacker_units') or []
        resources_victim = response.get('resources_victim')
        privateState = save['privateState']
        for unit in attacker_units:
            lost = max(0, unit[2] - unit[3])
            if lost > 0:
                item = unit[0]
                print(f'Lost {lost} {get_name_from_item_id(unit[0])}(s)')
                map_lose_item(map, privateState, unit[0], lost)
        if 'name' in victim:
            name = victim['name']
            if win:
                print(f'Won battle against {name}')
            else:
                print(f'Lost battle against {name}')
        elif win:
            print('Won battle')
        else:
            print('Lost battle')
        return None

    elif cmd == 'rt_open_graph_unit':
        item = args[0]
        privateState = save['privateState']
        if 'publishedOpenGraphUnit' not in privateState or not isinstance(privateState['publishedOpenGraphUnit'], list):
            privateState['publishedOpenGraphUnit'] = []
        if str(item) not in privateState['publishedOpenGraphUnit']:
            privateState['publishedOpenGraphUnit'].append(str(item))
        print(f'Open Unit Graph for {get_name_from_item_id(item)}')
        return None

    elif cmd == 'first_time_marketplace':
        privateState = save['privateState']
        privateState['marketPlaceFirstTime'] = True
        print('Seen Auction House')
        return None

    elif cmd == 'fast_forward':
        seconds = args[0]
        privateState = save['privateState']
        map['timestamp'] = max(0, map.get('timestamp', 0) - seconds)
        map['timestampLastChapter'] = max(0, map.get('timestampLastChapter', 0) - seconds)
        map['timestampLastTreasure'] = max(0, map.get('timestampLastTreasure', 0) - seconds)
        map['timestampLastTrade'] = max(0, map.get('timestampLastTrade', 0) - seconds)
        privateState['timestampLastBonus'] = max(0, privateState.get('timestampLastBonus', 0) - seconds)
        privateState['timestampLastAllianceBonus'] = max(0, privateState.get('timestampLastAllianceBonus', 0) - seconds)
        privateState['timeStampDartsNewFree'] = max(0, privateState.get('timeStampDartsNewFree', 0) - seconds)
        privateState['tsAttacksReset'] = max(0, privateState.get('tsAttacksReset', 0) - seconds)
        privateState['tsSpyingsReset'] = max(0, privateState.get('tsSpyingsReset', 0) - seconds)
        research_timers = privateState.get('timeStampDoResearch', [])
        for i in range(len(research_timers)):
            research_timers[i] = max(0, research_timers[i] - seconds)
        items = map.get('items', {})
        for index in items:
            data = items[index]
            data[3] = max(0, data[3] - seconds)
            if len(data) > 6 and data[6] and isinstance(data[6], dict) and 'ts' in data[6]:
                data[6]['ts'] = max(0, data[6]['ts'] - seconds)
        questTimes = map.get('questTimes', {})
        for key in questTimes:
            if questTimes[key] is not None:
                questTimes[key] = max(0, questTimes[key] - seconds)
        print(f'Fast forwarded {seconds} seconds')
        return None

    elif cmd == 'ping':
        print('Pong')
        return None

    elif cmd == 'set_variables':
        print('Set player resources')
        return None

    else:
        print(f"Unhandled command '{cmd}' -> args {args}")
        return None

