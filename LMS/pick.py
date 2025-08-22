import discord
from discord import app_commands
from discord.ext import commands
from utils import get_current_gameweek, is_pick_locked
import psycopg2
import os

PL_TEAMS = [
    "Arsenal", "Aston Villa", "Bournemouth", "Brentford", "Brighton & Hove Albion",
    "Burnley", "Chelsea", "Crystal Palace", "Everton", "Fulham", "Leeds United",
    "Liverpool", "Manchester City", "Manchester United", "Newcastle United",
    "Nottingham Forest", "Sunderland", "Tottenham Hotspur", "West Ham United",
    "Wolverhampton Wanderers"
]

DATABASE_URL = os.getenv("DATABASE_URL")

class Pick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="pick", description="Submit your team pick for this gameweek.")
    @app_commands.describe(team="The team you want to pick")
    async def pick(self, interaction: discord.Interaction, team: str):
        if is_pick_locked():
            await interaction.response.send_message("❌ Picks are locked. The gameweek has already started.", ephemeral=True)
            return

        current_gameweek = get_current_gameweek()
        user_id = str(interaction.user.id)
        name = interaction.user.display_name

        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM players WHERE discord_id = %s", (user_id,))
                result = cur.fetchone()

                if not result:
                    cur.execute(
                        "INSERT INTO players (discord_id, name) VALUES (%s, %s) RETURNING id",
                        (user_id, name)
                    )
                    player_id = cur.fetchone()[0]
                else:
                    player_id = result[0]

                # Check if already picked for this gameweek
                cur.execute("SELECT id FROM picks WHERE player_id = %s AND gameweek = %s", (player_id, current_gameweek))
                if cur.fetchone():
                    await interaction.response.send_message(f"⚠️ You've already picked for Gameweek {current_gameweek}.", ephemeral=True)
                    return

                # Save the pick
                cur.execute(
                    "INSERT INTO picks (player_id, gameweek, team) VALUES (%s, %s, %s)",
                    (player_id, current_gameweek, team)
                )
                conn.commit()

        await interaction.response.send_message(f"✅ Pick submitted for Gameweek {current_gameweek}: **{team}**", ephemeral=True)

    @pick.autocomplete("team")
    async def team_autocomplete(self, interaction: discord.Interaction, current: str):
        user_id = str(interaction.user.id)
        current_gameweek = get_current_gameweek()

        with psycopg2.connect(DATABASE_URL, sslmode="require") as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT id FROM players WHERE discord_id = %s", (user_id,))
                result = cur.fetchone()

                if not result:
                    return [app_commands.Choice(name=team, value=team) for team in PL_TEAMS if current.lower() in team.lower()]

                player_id = result[0]
                cur.execute("SELECT team FROM picks WHERE player_id = %s", (player_id,))
                picked_teams = [row[0] for row in cur.fetchall()]

                available_teams = [team for team in PL_TEAMS if team not in picked_teams]

        filtered = [team for team in available_teams if current.lower() in team.lower()]
        return [app_commands.Choice(name=team, value=team) for team in filtered[:25]]


async def setup(bot):
    await bot.add_cog(Pick(bot))
