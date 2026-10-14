# Source Generated with Decompyle++
# File: get_player_info.pyc (Python 3.9)

from sessions import session, neighbors, neighbor_session
from engine import timestamp_now, reset_stuff

def get_player_info(USERID):
    ts_now = timestamp_now()
    p_session = session(USERID)
    if not p_session:
        return {'result': 'error', 'error': 'session_not_found'}
    p_session['playerInfo']['last_logged_in'] = ts_now
    reset_stuff(p_session)
    player_info = {
        'result': 'ok',
        'processed_errors': 0,
        'timestamp': ts_now,
        'playerInfo': p_session['playerInfo'],
        'map': p_session['maps'][0],
        'privateState': p_session['privateState'],
        'neighbors': neighbors(USERID) }
    return player_info


def get_neighbor_info(userid, map_number):
    userid = str(userid) if userid is not None else '0'
    _session = neighbor_session(userid)
    if not _session and userid in ('0', 'Neutral'):
        _session = neighbor_session('Neutral')
    if not _session:
        print(f'USERID {userid} not found, checking fallback.')
        _session = neighbor_session('Neutral')
    if not _session or 'maps' not in _session:
        print(f'USERID {userid} could not be loaded.')
        return {'result': 'error', 'error': 'not_found'}
        
    _map_number = 0 if not map_number else int(map_number)
    if _map_number >= len(_session['maps']):
        _map_number = 0
        
    neighbor_info = {
        'result': 'ok',
        'processed_errors': 0,
        'timestamp': timestamp_now(),
        'playerInfo': _session['playerInfo'],
        'map': _session['maps'][_map_number],
        'privateState': _session.get('privateState', {})
    }
    return neighbor_info

