import sqlite3
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel
import os

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'licenses.db')

class Order(BaseModel):
    order_id: str
    discord_id: str
    zen_serial: str
    product: str
    tier: str  # trial, standard, plus
    purchased_at: datetime
    expires_at: Optional[datetime] = None
    status: str = "active"  # active, expired, revoked

class Redemption(BaseModel):
    redemption_id: str
    order_id: str
    challenge_code: str
    key_issued: str
    issued_at: datetime
    ip_address: str

class Ban(BaseModel):
    ban_id: str
    target_type: str  # serial, discord_id
    target_value: str
    reason: str
    banned_at: datetime

class Script(BaseModel):
    script_id: str
    name: str
    description: str
    gpc_template: str
    price: float

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS orders (
            order_id TEXT PRIMARY KEY,
            discord_id TEXT NOT NULL,
            zen_serial TEXT NOT NULL,
            product TEXT NOT NULL,
            tier TEXT NOT NULL,
            purchased_at TIMESTAMP NOT NULL,
            expires_at TIMESTAMP,
            status TEXT DEFAULT 'active'
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS redemptions (
            redemption_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            challenge_code TEXT NOT NULL,
            key_issued TEXT NOT NULL,
            issued_at TIMESTAMP NOT NULL,
            ip_address TEXT,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS bans (
            ban_id TEXT PRIMARY KEY,
            target_type TEXT NOT NULL,
            target_value TEXT NOT NULL,
            reason TEXT NOT NULL,
            banned_at TIMESTAMP NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS scripts (
            script_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            gpc_template TEXT NOT NULL,
            price REAL DEFAULT 0.0
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS licenses (
            license_id TEXT PRIMARY KEY,
            order_id TEXT NOT NULL,
            seed_data TEXT NOT NULL,
            exported_at TIMESTAMP NOT NULL,
            FOREIGN KEY (order_id) REFERENCES orders(order_id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS rate_limits (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            target_type TEXT NOT NULL,
            target_value TEXT NOT NULL,
            request_time TIMESTAMP NOT NULL
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            discord_id TEXT PRIMARY KEY,
            username TEXT,
            zen_serial TEXT UNIQUE,
            connected_at TIMESTAMP NOT NULL,
            last_login TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()

def check_rate_limit(target_type: str, target_value: str, max_requests: int = 5, window_seconds: int = 300) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM rate_limits 
        WHERE target_type = ? AND target_value = ? 
        AND request_time > datetime('now', ? || ' seconds')
    ''', (target_type, target_value, f'-{window_seconds}'))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count < max_requests

def log_rate_limit(target_type: str, target_value: str):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO rate_limits (target_type, target_value, request_time)
        VALUES (?, ?, datetime('now'))
    ''', (target_type, target_value))
    
    conn.commit()
    conn.close()

def is_banned(target_type: str, target_value: str) -> Optional[str]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT reason FROM bans 
        WHERE target_type = ? AND target_value = ?
    ''', (target_type, target_value))
    
    result = cursor.fetchone()
    conn.close()
    return result['reason'] if result else None

def get_order_by_serial_and_discord(zen_serial: str, discord_id: str) -> Optional[dict]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM orders 
        WHERE zen_serial = ? AND discord_id = ? AND status = 'active'
    ''', (zen_serial, discord_id))
    
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def create_order(order: Order):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO orders (order_id, discord_id, zen_serial, product, tier, purchased_at, expires_at, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (order.order_id, order.discord_id, order.zen_serial, order.product, 
          order.tier, order.purchased_at, order.expires_at, order.status))
    
    conn.commit()
    conn.close()

def create_redemption(redemption: Redemption):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO redemptions (redemption_id, order_id, challenge_code, key_issued, issued_at, ip_address)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (redemption.redemption_id, redemption.order_id, redemption.challenge_code,
          redemption.key_issued, redemption.issued_at, redemption.ip_address))
    
    conn.commit()
    conn.close()

def create_ban(ban: Ban):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO bans (ban_id, target_type, target_value, reason, banned_at)
        VALUES (?, ?, ?, ?, ?)
    ''', (ban.ban_id, ban.target_type, ban.target_value, ban.reason, ban.banned_at))
    
    conn.commit()
    conn.close()

def get_scripts() -> List[dict]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM scripts')
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def create_script(script: Script):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO scripts (script_id, name, description, gpc_template, price)
        VALUES (?, ?, ?, ?, ?)
    ''', (script.script_id, script.name, script.description, script.gpc_template, script.price))
    
    conn.commit()
    conn.close()

def has_trial_been_used(zen_serial: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT COUNT(*) FROM orders 
        WHERE zen_serial = ? AND tier = 'trial'
    ''', (zen_serial,))
    
    count = cursor.fetchone()[0]
    conn.close()
    return count > 0

def create_license(license_id: str, order_id: str, seed_data: str):
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO licenses (license_id, order_id, seed_data, exported_at)
        VALUES (?, ?, ?, datetime('now'))
    ''', (license_id, order_id, seed_data))
    
    conn.commit()
    conn.close()

def get_order_by_id(order_id: str) -> Optional[dict]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM orders WHERE order_id = ?', (order_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def get_redemptions_by_order(order_id: str) -> List[dict]:
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM redemptions WHERE order_id = ?', (order_id,))
    results = cursor.fetchall()
    conn.close()
    return [dict(r) for r in results]

def get_user_by_discord(discord_id: str) -> Optional[dict]:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE discord_id = ?', (discord_id,))
    result = cursor.fetchone()
    conn.close()
    return dict(result) if result else None

def create_or_update_user(discord_id: str, username: str, zen_serial: str = None):
    conn = get_db()
    cursor = conn.cursor()
    existing = get_user_by_discord(discord_id)
    if existing:
        cursor.execute('''
            UPDATE users SET last_login = datetime('now'), username = ?
            WHERE discord_id = ?
        ''', (username, discord_id))
        if zen_serial and not existing.get('zen_serial'):
            cursor.execute('UPDATE users SET zen_serial = ? WHERE discord_id = ?', (zen_serial, discord_id))
    else:
        cursor.execute('''
            INSERT INTO users (discord_id, username, zen_serial, connected_at, last_login)
            VALUES (?, ?, ?, datetime('now'), datetime('now'))
        ''', (discord_id, username, zen_serial))
    conn.commit()
    conn.close()

def bind_zen_serial(discord_id: str, zen_serial: str) -> bool:
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT zen_serial FROM users WHERE discord_id = ?', (discord_id,))
    result = cursor.fetchone()
    if result and result['zen_serial']:
        conn.close()
        return False
    cursor.execute('UPDATE users SET zen_serial = ? WHERE discord_id = ?', (zen_serial, discord_id))
    conn.commit()
    conn.close()
    return True
