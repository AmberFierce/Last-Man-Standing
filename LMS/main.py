import os
import asyncio
import uvicorn
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from discord.ext import commands
import discord
from threading import Thread
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

# Your bot commands go here
@bot.command()
async def ping(ctx):
    await ctx.send("Pong!")

# Run bot in background thread
def start_bot():
    bot.run(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    # Start the bot in a separate thread so it doesn't block FastAPI
    Thread(target=start_bot).start()

    # Run FastAPI app
    uvicorn.run(app, host="0.0.0.0", port=8000)
