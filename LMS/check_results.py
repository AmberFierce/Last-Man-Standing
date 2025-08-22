import sqlite3
import requests
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")
DB_PATH = "lms.db"
GAMEWEEK = 1  # Update this manually per week

response = requests.get(
    "https://api.football-data.org/v4/competitions/PL/matches",
    headers={"X-Auth-Token": API_KEY}
)
matches = response.json()["matches"]

team_results = {}
for match in matches:
    if match["matchday"] != GAMEWEEK:
        continue
    home = match["homeTeam"]["name"]
    away = match["awayTeam"]["name"]
    winner = match["score"]["winner"]
    if winner == "HOME_TEAM":
        team_results[home] = "Win"
        team_results[away] = "Lose"
    elif winner == "AWAY_TEAM":
        team_results[away] = "Win"
        team_results[home] = "Lose"
    else:
        team_results[home] = team_results[away] = "Draw"

with sqlite3.connect(DB_PATH) as conn:
    cur = conn.cursor()
    cur.execute("SELECT id, player_id, team FROM picks WHERE gameweek = ?", (GAMEWEEK,))
    for _, pid, team in cur.fetchall():
        result = team_results.get(team, "Unknown")
        if result != "Win":
            cur.execute("UPDATE players SET status = 'Out' WHERE id = ?", (pid,))
    conn.commit()