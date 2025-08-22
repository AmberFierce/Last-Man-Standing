from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import init_db, get_leaderboard

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

init_db()

@app.get("/")
async def leaderboard(request: Request):
    leaderboard_data = get_leaderboard()
    return templates.TemplateResponse("leaderboard.html", {"request": request, "players": leaderboard_data})

