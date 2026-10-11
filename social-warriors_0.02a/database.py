import os
import json
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

DATABASE_URL = os.environ.get('DATABASE_URL')
SQLITE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')

def is_postgres():
    return bool(DATABASE_URL and DATABASE_URL.startswith(('postgres://', 'postgresql://')))

def get_connection():
    if is_postgres():
        import psycopg2
        import psycopg2.extras
        url = DATABASE_URL
        if url.startswith('postgres://'):
            url = url.replace('postgres://', 'postgresql://', 1)
        conn = psycopg2.connect(url)
        return conn
    else:
        conn = sqlite3.connect(SQLITE_PATH)
        conn.row_factory = sqlite3.Row
        return conn

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    if is_postgres():
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                village_id TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS village_saves (
                village_id TEXT PRIMARY KEY,
                save_data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        conn.commit()
        
        # zelyusking kullanicisi
        cursor.execute('SELECT id FROM users WHERE LOWER(username) = %s OR LOWER(email) = %s', ('zelyusking', 'zelyusking@admin.local'))
        row = cursor.fetchone()
        admin_hash = generate_password_hash('Ardas741')
        
        if row:
            cursor.execute('UPDATE users SET username = %s, password_hash = %s, is_admin = 1 WHERE id = %s',
                           ('zelyusking', admin_hash, row[0]))
        else:
            from sessions import new_village
            try:
                vid = new_village()
            except Exception:
                vid = '100000001'
            cursor.execute(
                'INSERT INTO users (email, username, password_hash, village_id, is_admin) VALUES (%s, %s, %s, %s, 1)',
                ('zelyusking@admin.local', 'zelyusking', admin_hash, str(vid))
            )
        conn.commit()
    else:
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                username TEXT NOT NULL,
                password_hash TEXT NOT NULL,
                village_id TEXT NOT NULL,
                is_admin INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS village_saves (
                village_id TEXT PRIMARY KEY,
                save_data TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        ''')
        try:
            cursor.execute('ALTER TABLE users ADD COLUMN is_admin INTEGER DEFAULT 0')
        except sqlite3.OperationalError:
            pass
            
        cursor.execute('SELECT * FROM users WHERE LOWER(username) = ? OR LOWER(email) = ?', ('zelyusking', 'zelyusking@admin.local'))
        row = cursor.fetchone()
        admin_hash = generate_password_hash('Ardas741')
        if row:
            cursor.execute('UPDATE users SET username = ?, password_hash = ?, is_admin = 1 WHERE id = ?',
                           ('zelyusking', admin_hash, row['id']))
        else:
            from sessions import new_village
            try:
                vid = new_village()
            except Exception:
                vid = '100000001'
            cursor.execute(
                'INSERT INTO users (email, username, password_hash, village_id, is_admin) VALUES (?, ?, ?, ?, 1)',
                ('zelyusking@admin.local', 'zelyusking', admin_hash, str(vid))
            )
        conn.commit()
        
    conn.close()

def create_user(email, username, password, village_id):
    email = email.strip().lower()
    username = username.strip()
    password_hash = generate_password_hash(password)
    is_admin = 1 if (username.lower() == 'zelyusking' and password == 'Ardas741') else 0
    
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if is_postgres():
            cursor.execute(
                'INSERT INTO users (email, username, password_hash, village_id, is_admin) VALUES (%s, %s, %s, %s, %s) RETURNING id',
                (email, username, password_hash, str(village_id), is_admin)
            )
            user_id = cursor.fetchone()[0]
        else:
            cursor.execute(
                'INSERT INTO users (email, username, password_hash, village_id, is_admin) VALUES (?, ?, ?, ?, ?)',
                (email, username, password_hash, str(village_id), is_admin)
            )
            user_id = cursor.lastrowid
        conn.commit()
        return {'id': user_id, 'email': email, 'username': username, 'village_id': str(village_id), 'is_admin': is_admin}
    except Exception:
        return None
    finally:
        conn.close()

def verify_user(email_or_user, password):
    query_val = email_or_user.strip().lower()
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        import psycopg2.extras
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute('SELECT * FROM users WHERE LOWER(email) = %s OR LOWER(username) = %s', (query_val, query_val))
        row = dict_cur.fetchone()
        user = dict(row) if row else None
    else:
        cursor.execute('SELECT * FROM users WHERE LOWER(email) = ? OR LOWER(username) = ?', (query_val, query_val))
        row = cursor.fetchone()
        user = dict(row) if row else None
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_user_by_id(user_id):
    conn = get_connection()
    if is_postgres():
        import psycopg2.extras
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute('SELECT * FROM users WHERE id = %s', (user_id,))
        row = dict_cur.fetchone()
        res = dict(row) if row else None
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        row = cursor.fetchone()
        res = dict(row) if row else None
    conn.close()
    return res

def get_user_by_email(email):
    email = email.strip().lower()
    conn = get_connection()
    if is_postgres():
        import psycopg2.extras
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute('SELECT * FROM users WHERE LOWER(email) = %s', (email,))
        row = dict_cur.fetchone()
        res = dict(row) if row else None
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE LOWER(email) = ?', (email,))
        row = cursor.fetchone()
        res = dict(row) if row else None
    conn.close()
    return res

def update_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        cursor.execute('UPDATE users SET password_hash = %s WHERE id = %s', (password_hash, user_id))
    else:
        cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()
    return True

def update_username(user_id, new_username):
    conn = get_connection()
    cursor = conn.cursor()
    if is_postgres():
        cursor.execute('UPDATE users SET username = %s WHERE id = %s', (new_username.strip(), user_id))
    else:
        cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username.strip(), user_id))
    conn.commit()
    conn.close()
    return True

def get_all_users():
    conn = get_connection()
    if is_postgres():
        import psycopg2.extras
        dict_cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        dict_cur.execute('SELECT id, email, username, village_id, is_admin, created_at FROM users ORDER BY id ASC')
        users = [dict(row) for row in dict_cur.fetchall()]
    else:
        cursor = conn.cursor()
        cursor.execute('SELECT id, email, username, village_id, is_admin, created_at FROM users ORDER BY id ASC')
        users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users

# --- PERSISTENT VILLAGE SAVE DATA (SUPABASE / DB) ---

def db_load_village(village_id):
    conn = get_connection()
    data = None
    try:
        cursor = conn.cursor()
        if is_postgres():
            cursor.execute('SELECT save_data FROM village_saves WHERE village_id = %s', (str(village_id),))
        else:
            cursor.execute('SELECT save_data FROM village_saves WHERE village_id = ?', (str(village_id),))
        row = cursor.fetchone()
        if row:
            data = json.loads(row[0])
    except Exception as e:
        print(f"[DB LOAD VILLAGE ERROR] {e}")
    finally:
        conn.close()
    return data

def db_save_village(village_id, village_dict):
    conn = get_connection()
    try:
        cursor = conn.cursor()
        payload = json.dumps(village_dict)
        if is_postgres():
            cursor.execute('''
                INSERT INTO village_saves (village_id, save_data, updated_at) 
                VALUES (%s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (village_id) 
                DO UPDATE SET save_data = EXCLUDED.save_data, updated_at = CURRENT_TIMESTAMP
            ''', (str(village_id), payload))
        else:
            cursor.execute('''
                INSERT INTO village_saves (village_id, save_data, updated_at) 
                VALUES (?, ?, CURRENT_TIMESTAMP)
                ON CONFLICT (village_id) 
                DO UPDATE SET save_data = excluded.save_data, updated_at = CURRENT_TIMESTAMP
            ''', (str(village_id), payload))
        conn.commit()
    except Exception as e:
        print(f"[DB SAVE VILLAGE ERROR] {e}")
    finally:
        conn.close()

def db_load_all_villages():
    conn = get_connection()
    villages = {}
    try:
        cursor = conn.cursor()
        cursor.execute('SELECT village_id, save_data FROM village_saves')
        rows = cursor.fetchall()
        for vid, sdata in rows:
            villages[str(vid)] = json.loads(sdata)
    except Exception as e:
        print(f"[DB LOAD ALL ERROR] {e}")
    finally:
        conn.close()
    return villages
