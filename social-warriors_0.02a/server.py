import os
import sys
import json
import urllib
import io

print(' [+] Loading Social Wars Server...')
from flask import Flask, render_template, send_from_directory, request, redirect, session, jsonify, flash, url_for
from werkzeug.security import generate_password_hash, check_password_hash

from bundle import ASSETS_DIR, STUB_DIR, TEMPLATES_DIR, BASE_DIR
from get_game_config import get_game_config
from get_player_info import get_player_info, get_neighbor_info
from sessions import (
    load_saves, load_static_villages, load_quests,
    all_saves_userid, all_saves_info, save_info,
    new_village, create_user_village, fb_friends_str, neighbors, session as get_village_session
)
from command import command
from engine import timestamp_now
from version import version_name
from constants import Quests
from database import (
    init_db, create_user, verify_user,
    get_user_by_id, get_user_by_email,
    update_password, update_username, get_all_users
)

# Initialize database
init_db()

print(' [+] Loading game data...')
load_saves()
load_static_villages()
load_quests()

app = Flask(__name__, template_folder=TEMPLATES_DIR)
app.secret_key = os.environ.get('SECRET_KEY', 'social_wars_super_secret_key_2026')

__STATIC_ROOT = '/static/socialwars'
__DYNAMIC_ROOT = '/dynamic/menvswomen/srvsexwars'

def get_server_base_url():
    """Returns absolute base URL, detecting Render.com or custom domain dynamically."""
    proto = request.headers.get('X-Forwarded-Proto', request.scheme)
    return f"{proto}://{request.host}"

# --- AUTH & WEB PAGES ---

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect('/profile')
    return redirect('/login')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect('/profile')
        
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        
        user = verify_user(email, password)
        if user:
            session['user_id'] = user['id']
            session['email'] = user['email']
            session['username'] = user['username']
            session['USERID'] = user['village_id']
            session['is_admin'] = user.get('is_admin', 0)
            session['GAMEVERSION'] = 'Basesec_1.5.4.swf'
            return redirect('/play.html')
        else:
            error = 'Geçersiz kullanıcı adı/e-posta veya şifre!'
            
    return render_template('login.html', error=error, version=version_name)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session:
        return redirect('/profile')
        
    error = None
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not email or not username or not password:
            error = 'Lütfen tüm alanları doldurun!'
        elif len(password) < 4:
            error = 'Şifre en az 4 karakter olmalıdır!'
        elif password != confirm_password:
            error = 'Şifreler uyuşmuyor!'
        elif get_user_by_email(email):
            error = 'Bu e-posta adresi zaten kayıtlı!'
        else:
            # Yeni oyuncuya özel imparatorluk olustur
            village_id = create_user_village(empire_name=username)
            user = create_user(email, username, password, village_id)
            if user:
                session['user_id'] = user['id']
                session['email'] = user['email']
                session['username'] = user['username']
                session['USERID'] = user['village_id']
                session['is_admin'] = user.get('is_admin', 0)
                session['GAMEVERSION'] = 'Basesec_1.5.4.swf'
                return redirect('/play.html')
            else:
                error = 'Hesap oluşturulurken bir hata oluştu!'
                
    return render_template('register.html', error=error, version=version_name)

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect('/login')
        
    user = get_user_by_id(session['user_id'])
    if not user:
        session.clear()
        return redirect('/login')
        
    msg = None
    msg_type = 'success'
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'change_password':
            old_pass = request.form.get('old_password', '')
            new_pass = request.form.get('new_password', '')
            confirm_pass = request.form.get('confirm_new_password', '')
            
            if not check_password_hash(user['password_hash'], old_pass):
                msg = 'Mevcut şifreniz hatalı!'
                msg_type = 'danger'
            elif len(new_pass) < 4:
                msg = 'Yeni şifre en az 4 karakter olmalıdır!'
                msg_type = 'danger'
            elif new_pass != confirm_pass:
                msg = 'Yeni şifreler uyuşmuyor!'
                msg_type = 'danger'
            else:
                update_password(user['id'], new_pass)
                msg = 'Şifreniz başarıyla güncellendi!'
                msg_type = 'success'
                
        elif action == 'update_profile':
            new_name = request.form.get('username', '').strip()
            if new_name:
                update_username(user['id'], new_name)
                session['username'] = new_name
                # Koy ismini de guncelle
                vill = get_village_session(user['village_id'])
                if vill:
                    vill['playerInfo']['name'] = new_name
                user = get_user_by_id(user['id'])
                msg = 'Profil adı güncellendi!'
                msg_type = 'success'

    info = save_info(user['village_id']) or {
        'userid': user['village_id'],
        'name': user['username'],
        'xp': 0,
        'level': 1,
        'cash': 0,
        'coins': 0
    }
    
    all_players = get_all_users()
    
    return render_template('profile.html', user=user, info=info, all_players=all_players, msg=msg, msg_type=msg_type, version=version_name)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if 'user_id' not in session:
        return redirect('/login')
    user = get_user_by_id(session['user_id'])
    if not user or not user.get('is_admin'):
        return redirect('/profile')
        
    msg = None
    msg_type = 'success'
    
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'modify_player':
            vid = request.form.get('village_id')
            cash = request.form.get('cash') or None
            gold = request.form.get('gold') or None
            level = request.form.get('level') or None
            wood = request.form.get('wood') or None
            steel = request.form.get('steel') or None
            oil = request.form.get('oil') or None
            item_id = request.form.get('item_id')
            
            from sessions import modify_player_resources, add_item_to_player_store
            modify_player_resources(vid, cash=cash, gold=gold, wood=wood, steel=steel, oil=oil, level=level)
            if item_id:
                add_item_to_player_store(vid, item_id, 1)
            msg = 'Oyuncunun kaynakları, seviyesi ve hediyeleri başarıyla güncellendi!'
            msg_type = 'success'
            
        elif action == 'server_event':
            e_cash = int(request.form.get('event_cash') or 0)
            e_gold = int(request.form.get('event_gold') or 0)
            e_wood = int(request.form.get('event_wood') or 0)
            e_steel = int(request.form.get('event_steel') or 0)
            
            from sessions import gift_all_players
            c = gift_all_players(cash=e_cash, gold=e_gold, wood=e_wood, steel=e_steel)
            msg = f'Sunucu Etkinliği Başlatıldı! {c} oyuncuya hediyeler dağıtıldı!'
            msg_type = 'success'

    all_users = get_all_users()
    players_data = []
    for u in all_users:
        u_info = save_info(u['village_id']) or {
            'level': 1, 'xp': 0, 'cash': 0, 'coins': 0
        }
        players_data.append({
            'id': u['id'],
            'username': u['username'],
            'email': u['email'],
            'is_admin': u.get('is_admin', 0),
            'village_id': u['village_id'],
            'info': u_info
        })
        
    return render_template('admin.html', players_data=players_data, msg=msg, msg_type=msg_type, version=version_name)

@app.route('/play.html')
def play():
    if 'USERID' not in session or 'user_id' not in session:
        return redirect('/login')
        
    USERID = session['USERID']
    GAMEVERSION = session.get('GAMEVERSION', 'Basesec_1.5.4.swf')
    
    user_save = save_info(USERID)
    if not user_save:
        load_saves()
        user_save = save_info(USERID)
        
    if not user_save:
        # Save bulunamazsa yeni oluştur
        USERID = create_user_village(session.get('username', 'Commander'))
        session['USERID'] = USERID
        user_save = save_info(USERID)
        
    base_url = get_server_base_url()
    
    return render_template(
        'play.html',
        save_info=user_save,
        serverTime=timestamp_now(),
        friendsInfo=fb_friends_str(USERID),
        version=version_name,
        GAMEVERSION=GAMEVERSION,
        BASE_URL=base_url
    )

# --- STATIC CONTENT ROUTES ---

@app.route('/crossdomain.xml')
def crossdomain():
    return send_from_directory(STUB_DIR, 'crossdomain.xml')

@app.route('/img/<path:path>')
def images(path):
    return send_from_directory(os.path.join(TEMPLATES_DIR, 'img'), path)

@app.route('/avatars/<path:path>')
def avatars(path):
    return send_from_directory(os.path.join(TEMPLATES_DIR, 'avatars'), path)

@app.route('/css/<path:path>')
def css(path):
    return send_from_directory(os.path.join(TEMPLATES_DIR, 'css'), path)

@app.route(__STATIC_ROOT + '/<path:path>')
def static_assets_loader(path):
    return send_from_directory(ASSETS_DIR, path)

# --- GAME API ROUTES ---

@app.route(__DYNAMIC_ROOT + '/track_game_status.php', methods=['POST'])
def track_game_status_response():
    status = request.values.get('status')
    user_id = request.values.get('user_id')
    print(f'[STATUS] USERID {user_id}: {status}')
    return ('', 200)

@app.route(__DYNAMIC_ROOT + '/get_game_config.php', methods=['GET', 'POST'])
def get_game_config_response():
    USERID = request.values.get('USERID')
    print(f'[CONFIG] USERID {USERID}.')
    return jsonify(get_game_config())

@app.route(__DYNAMIC_ROOT + '/get_player_info.php', methods=['POST'])
def get_player_info_response():
    USERID = request.values.get('USERID')
    user = request.values.get('user')
    map_idx = int(request.values.get('map', 0)) if 'map' in request.values else None
    
    if user is None:
        print(f'[PLAYER INFO] USERID {USERID}.')
        return jsonify(get_player_info(USERID))
        
    if user in ('100000030', '100000031'):
        print(f'[VISIT] USERID {USERID} visiting General Mike ({user}).')
        return jsonify(get_neighbor_info('100000030', map_idx))
        
    if user.startswith('100000'):
        q_name = Quests.QUEST.get(user, '?')
        print(f'[QUEST] USERID {USERID} loading {q_name} ({user}).')
        return jsonify(get_neighbor_info(user, map_idx))
        
    print(f'[VISIT] USERID {USERID} visiting user: {user}.')
    return jsonify(get_neighbor_info(user, map_idx))

@app.route(__DYNAMIC_ROOT + '/sync_error_track.php', methods=['POST'])
def sync_error_track_response():
    return ('', 200)

@app.route('/null')
def flash_sync_error_response():
    sp_ref_cat = request.values.get('sp_ref_cat', '')
    print(f'[FLASH SYNC ERROR] {sp_ref_cat}')
    return redirect('/play.html')

@app.route(__DYNAMIC_ROOT + '/command.php', methods=['POST'])
def command_response():
    USERID = request.values.get('USERID')
    data_str = request.values.get('data', '')
    
    if len(data_str) > 64 and data_str[64] == ';':
        data_payload = data_str[65:]
        try:
            data = json.loads(data_payload)
            command(USERID, data)
        except Exception as e:
            print(f'[COMMAND ERROR] {e}')
            
    return jsonify({'result': 'success'}), 200

@app.route(__DYNAMIC_ROOT + '/alliance/', methods=['POST'])
def alliance():
    return jsonify({}), 200

# --- RUN APPLICATION ---

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5055))
    host = '0.0.0.0'
    print(f' [+] Server running on http://{host}:{port}')
    app.run(host=host, port=port, debug=False)
