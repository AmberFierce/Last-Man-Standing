import discord
from discord import app_commands
from discord.ext import commands
from utils import get_current_gameweek, is_pick_locked
import psycopg2
import os

# List of valid Premier League teams
PL_TEAMS = [
    "Arsenal",
    "Aston Villa",
    "AFC Bournemouth",
    "Brentford",
    "Brighton & Hove Albion",
    "Burnley",
    "Chelsea",
    "Crystal Palace",
    "Everton",
    "Fulham",
    "Leeds United",
    "Liverpool",
    "Manchester City",
    "Manchester United",
    "Newcastle United",
    "Nottingham Forest",
    "Sunderland",
    "Tottenham Hotspur",
    "West Ham United",
    "Wolverhampton Wanderers"
]

DATABASE_URL = os.getenv("DATABASE_URL")

class Pick(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = discord.Object(id=1117171688531042474)  # Replace with your actual guild ID

    @app_commands.command(name="pick", description="Submit your team pick for this gameweek.")
    @app_commands.describe(team="The team you want to pick")
    async def pick(self, interaction: discord.Interaction, team: str):
        user_id = interaction.user.id
        gameweek = get_current_gameweek()

        if is_pick_locked():
            await interaction.response.send_message("Picks are locked for the current gameweek.", ephemeral=True)
            return

        try:
            conn = psycopg2.connect(DATABASE_URL)
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO picks (user_id, gameweek, team)
                VALUES (%s, %s, %s)
                ON CONFLICT (user_id, gameweek)
                DO UPDATE SET team = EXCLUDED.team;
            """, (user_id, gameweek, team))

            conn.commit()
            cur.close()
            conn.close()

            await interaction.response.send_message(f"✅ Your pick for Gameweek {gameweek} is **{team}**!", ephemeral=True)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error submitting your pick: {e}", ephemeral=True)

    @pick.autocomplete("team")
    async def team_autocomplete(self, interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=team, value=team)
            for team in PL_TEAMS if current.lower() in team.lower()
        ]

# ✅ Ensure this is at the top level of the file, not indented
async def setup(bot):
    cog = Pick(bot)
    await bot.add_cog(cog)
    bot.tree.add_command(cog.pick, guild=cog.guild)

