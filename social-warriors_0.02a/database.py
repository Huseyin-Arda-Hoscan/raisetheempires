import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'users.db')

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            username TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            village_id TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def create_user(email, username, password, village_id):
    email = email.strip().lower()
    username = username.strip()
    password_hash = generate_password_hash(password)
    
    conn = get_db()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO users (email, username, password_hash, village_id) VALUES (?, ?, ?, ?)',
            (email, username, password_hash, str(village_id))
        )
        conn.commit()
        user_id = cursor.lastrowid
        return {'id': user_id, 'email': email, 'username': username, 'village_id': str(village_id)}
    except sqlite3.IntegrityError:
        return None
    finally:
        conn.close()

def verify_user(email, password):
    email = email.strip().lower()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user['password_hash'], password):
        return dict(user)
    return None

def get_user_by_id(user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_email(email):
    email = email.strip().lower()
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def get_user_by_village_id(village_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE village_id = ?', (str(village_id),))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def update_password(user_id, new_password):
    password_hash = generate_password_hash(new_password)
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET password_hash = ? WHERE id = ?', (password_hash, user_id))
    conn.commit()
    conn.close()
    return True

def update_username(user_id, new_username):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET username = ? WHERE id = ?', (new_username.strip(), user_id))
    conn.commit()
    conn.close()
    return True

def get_all_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT id, email, username, village_id, created_at FROM users ORDER BY id ASC')
    users = [dict(row) for row in cursor.fetchall()]
    conn.close()
    return users
