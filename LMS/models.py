import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    return psycopg2.connect(DATABASE_URL, sslmode="require")

def init_db():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS players (
                    id SERIAL PRIMARY KEY,
                    discord_id TEXT UNIQUE,
                    name TEXT,
                    paid BOOLEAN DEFAULT FALSE,
                    status TEXT DEFAULT 'In',
                    round_wins INTEGER DEFAULT 0
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS picks (
                    id SERIAL PRIMARY KEY,
                    player_id INTEGER REFERENCES players(id),
                    gameweek INTEGER,
                    team TEXT
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS results (
                    id SERIAL PRIMARY KEY,
                    gameweek INTEGER,
                    team TEXT,
                    result TEXT
                )
            """)
        conn.commit()

def get_leaderboard():
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT name, status, round_wins FROM players
                ORDER BY status DESC, round_wins DESC, name ASC
            """)
            return cur.fetchall()
