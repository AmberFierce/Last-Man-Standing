import asyncio
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from models import init_db, get_leaderboard

# Run FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/")
async def leaderboard(request: Request):
    leaderboard_data = get_leaderboard()
    return templates.TemplateResponse("leaderboard.html", {"request": request, "players": leaderboard_data})

# Discord bot
import discord
from discord.ext import commands
import os

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"{bot.user.name} is online!")

# Include your bot commands here...

# Function to run both FastAPI and the bot
async def run_all():
    import uvicorn
    bot_task = asyncio.create_task(bot.start(os.getenv("DISCORD_TOKEN")))
    api_task = asyncio.create_task(uvicorn.run(app, host="0.0.0.0", port=8000))
    await asyncio.gather(bot_task, api_task)

if __name__ == "__main__":
    asyncio.run(run_all())
