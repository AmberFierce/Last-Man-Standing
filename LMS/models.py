import sqlite3
from datetime import date

DB_PATH = "lms.db"

def init_db():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            discord_id TEXT UNIQUE,
            name TEXT,
            paid BOOLEAN DEFAULT 0,
            status TEXT DEFAULT 'In',
            round_wins INTEGER DEFAULT 0
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS picks (
            id INTEGER PRIMARY KEY,
            player_id INTEGER,
            gameweek INTEGER,
            team TEXT,
            FOREIGN KEY(player_id) REFERENCES players(id)
        )""")
        cur.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY,
            gameweek INTEGER,
            team TEXT,
            result TEXT
        )""")
        conn.commit()

def get_leaderboard():
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("""
            SELECT name, status, round_wins FROM players
            ORDER BY status DESC, round_wins DESC, name ASC
        """)
        return cur.fetchall()