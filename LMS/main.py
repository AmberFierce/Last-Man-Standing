import os
from threading import Thread

import uvicorn
import discord
from discord.ext import commands
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from models import init_db, get_leaderboard

# FastAPI setup
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Init DB
init_db()

@app.get("/")
async def leaderboard(request: Request):
    leaderboard_data = get_leaderboard()
    return templates.TemplateResponse("leaderboard.html", {"request": request, "players": leaderboard_data})

# Discord bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")
    try:
        # Replace with your actual server (guild) ID
        synced = await bot.tree.sync(guild=discord.Object(id=1117171688531042474))
        print(f"Synced {len(synced)} slash commands to your guild.")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

@bot.event
async def setup_hook():
    await bot.load_extension("pick")
   
# Run bot in background thread
def start_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    Thread(target=start_bot).start()
    uvicorn.run(app, host="0.0.0.0", port=8000)

