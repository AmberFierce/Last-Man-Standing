import discord
from discord.ext import commands
import sqlite3
import os
from dotenv import load_dotenv

DB_PATH = "lms.db"
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"Bot is ready. Logged in as {bot.user}.")

@bot.command()
async def pick(ctx, *, team):
    user_id = str(ctx.author.id)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id, paid FROM players WHERE discord_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            await ctx.send("❌ You're not registered to play. Contact the admin.")
            return
        pid, paid = row
        if not paid:
            await ctx.send("❌ You're not marked as paid. Contact the admin.")
            return
        cur.execute("INSERT OR REPLACE INTO picks (player_id, gameweek, team) VALUES (?, ?, ?)", (pid, 1, team.title()))
        conn.commit()
    await ctx.send(f"✅ Pick saved: {team.title()}.")

@bot.command()
async def leaderboard(ctx):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT name, status FROM players ORDER BY status DESC, name ASC")
        rows = cur.fetchall()
    msg = "\n".join([f"{'🟢' if s == 'In' else '🔴'} {n}" for n, s in rows])
    await ctx.send(f"**Leaderboard**\n{msg}")

@bot.command()
async def status(ctx):
    user_id = str(ctx.author.id)
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE discord_id = ?", (user_id,))
        row = cur.fetchone()
        if not row:
            await ctx.send("❌ You're not in the game.")
            return
        pid = row[0]
        cur.execute("SELECT team FROM picks WHERE player_id = ? AND gameweek = ?", (pid, 1))
        pick_row = cur.fetchone()
        team = pick_row[0] if pick_row else "None"
    await ctx.send(f"📋 Your pick this week: **{team}**")

@bot.command()
async def markpaid(ctx, member: discord.Member):
    admin_id = str(ctx.author.id)
    if not admin_id:
        return
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("UPDATE players SET paid = 1 WHERE discord_id = ?", (str(member.id),))
        conn.commit()
    await ctx.send(f"✅ {member.display_name} marked as paid.")

@bot.command()
async def setpick(ctx, member: discord.Member, *, team):
    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT id FROM players WHERE discord_id = ?", (str(member.id),))
        row = cur.fetchone()
        if not row:
            await ctx.send("❌ Player not registered.")
            return
        pid = row[0]
        cur.execute("INSERT OR REPLACE INTO picks (player_id, gameweek, team) VALUES (?, ?, ?)", (pid, 1, team.title()))
        conn.commit()
    await ctx.send(f"✅ {member.display_name}'s pick set to {team.title()}.")
	
@bot.command()
async def help(ctx):
    msg = (
        "**Last Man Standing Bot Commands**\n\n"
        "🎯 `!pick <team>` – Submit your team for the current gameweek\n"
        "📋 `!status` – See your current pick\n"
        "📊 `!leaderboard` – View the leaderboard\n"
        "📝 `!join <name>` – (coming soon) Register to play\n"
        "💰 `!markpaid @user` – (admin) Mark a user as paid\n"
        "🛠️ `!setpick @user <team>` – (admin) Set a pick for a player\n"
    )
    await ctx.send(msg)

if __name__ == "__main__":
    bot.run(TOKEN)