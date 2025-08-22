import os
import requests
from datetime import datetime, timezone

API_URL = "https://v3.football.api-sports.io"
API_KEY = os.getenv("API_KEY")
HEADERS = {
    "x-apisports-key": API_KEY
}

LEAGUE_ID = 39  # Premier League
SEASON = 2025


def get_current_gameweek():
    """
    Fetch the current active gameweek (round) based on the first upcoming fixture
    """
    response = requests.get(
        f"{API_URL}/fixtures",
        headers=HEADERS,
        params={
            "league": LEAGUE_ID,
            "season": SEASON,
            "next": 10  # Get next 10 fixtures to be safe
        }
    )

    if response.status_code != 200:
        raise Exception("Failed to fetch fixtures from API-Football")

    fixtures = response.json().get("response", [])
    for fixture in fixtures:
        fixture_time = datetime.fromisoformat(fixture["fixture"]["date"].replace("Z", "+00:00"))
        if fixture_time > datetime.now(timezone.utc):
            round_str = fixture["league"]["round"]  # Example: "Regular Season - 3"
            gw = int(round_str.split(" - ")[-1])
            return gw

    raise Exception("Could not determine upcoming gameweek")


def is_pick_locked():
    """
    Determines if the current time is past the start of the first fixture of the next gameweek
    """
    current_gw = get_current_gameweek()

    response = requests.get(
        f"{API_URL}/fixtures",
        headers=HEADERS,
        params={
            "league": LEAGUE_ID,
            "season": SEASON,
            "round": f"Regular Season - {current_gw}"
        }
    )

    if response.status_code != 200:
        raise Exception("Failed to fetch fixtures for current round")

    fixtures = response.json().get("response", [])
    fixture_times = [
        datetime.fromisoformat(f["fixture"]["date"].replace("Z", "+00:00"))
        for f in fixtures
    ]

    if not fixture_times:
        return False  # no fixtures means no lock required

    first_kickoff = min(fixture_times)
    return datetime.now(timezone.utc) >= first_kickoff

