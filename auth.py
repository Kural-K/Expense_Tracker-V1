"""
auth.py — SQLite-based auth for WalletWatch
Handles: user registration, login, password hashing, session management
"""

import sqlite3
import hashlib
import os
import re

DB_PATH = "walletwatch.db"

# ── DB Setup ──────────────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            username  TEXT UNIQUE NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            created   TEXT DEFAULT (datetime('now'))
        )
    """)
    conn.commit()
    conn.close()

# ── Helpers ───────────────────────────────────────────────────────────────────
def hash_password(password: str) -> str:
    """SHA-256 hash with a salt."""
    salt = "walletwatch_salt_2024"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def is_valid_email(email: str) -> bool:
    return bool(re.match(r"^[\w\.-]+@[\w\.-]+\.\w{2,}$", email))

def is_strong_password(password: str) -> tuple[bool, str]:
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    return True, ""

# ── User ops ──────────────────────────────────────────────────────────────────
def register_user(username: str, email: str, password: str) -> tuple[bool, str]:
    init_db()
    username = username.strip().lower()
    email    = email.strip().lower()

    if not username or len(username) < 3:
        return False, "Username must be at least 3 characters."
    if not is_valid_email(email):
        return False, "Invalid email address."
    ok, msg = is_strong_password(password)
    if not ok:
        return False, msg

    try:
        conn = sqlite3.connect(DB_PATH)
        c    = conn.cursor()
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hash_password(password)))
        conn.commit()
        conn.close()
        return True, "Account created successfully!"
    except sqlite3.IntegrityError as e:
        if "username" in str(e):
            return False, "Username already taken."
        if "email" in str(e):
            return False, "Email already registered."
        return False, "Registration failed."

def login_user(username: str, password: str) -> tuple[bool, str, dict]:
    init_db()
    username = username.strip().lower()
    conn = sqlite3.connect(DB_PATH)
    c    = conn.cursor()
    c.execute("SELECT id, username, email FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    row = c.fetchone()
    conn.close()
    if row:
        return True, "Login successful!", {"id": row[0], "username": row[1], "email": row[2]}
    return False, "Invalid username or password.", {}

def get_user_data_paths(user_id: int) -> dict:
    """Returns per-user file paths so data is isolated per account."""
    base = f"data/user_{user_id}"
    os.makedirs(base, exist_ok=True)
    return {
        "csv":       f"{base}/expenses.csv",
        "budgets":   f"{base}/budgets.json",
        "income":    f"{base}/income.json",
        "recurring": f"{base}/recurring.json",
    }