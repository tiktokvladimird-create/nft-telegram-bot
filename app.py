import random
import sqlite3
from datetime import date
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

DB = Path("nft_bot.sqlite3")
app = FastAPI(title="NFT Telegram Mini App API")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Демонстрационные призы. Сумма весов = 100.
PRIZES = [
    {"id": "common", "name": "NFT: Pixel Bloom", "rarity": "Обычный", "weight": 65,
     "image": "https://placehold.co/640x640/17152b/ffffff?text=Pixel+Bloom"},
    {"id": "rare", "name": "NFT: Neon Fox", "rarity": "Редкий", "weight": 25,
     "image": "https://placehold.co/640x640/25204a/ffffff?text=Neon+Fox"},
    {"id": "epic", "name": "NFT: Cosmic Tiger", "rarity": "Эпический", "weight": 9,
     "image": "https://placehold.co/640x640/3a1e54/ffffff?text=Cosmic+Tiger"},
    {"id": "legendary", "name": "NFT: Golden Comet", "rarity": "Легендарный", "weight": 1,
     "image": "https://placehold.co/640x640/60451b/ffffff?text=Golden+Comet"},
]

def connect():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    with connect() as con:
        con.execute("CREATE TABLE IF NOT EXISTS users (user_id TEXT PRIMARY KEY, username TEXT, created_at TEXT NOT NULL)")
        con.execute("CREATE TABLE IF NOT EXISTS draws (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id TEXT NOT NULL, prize_id TEXT NOT NULL, draw_date TEXT NOT NULL, created_at TEXT NOT NULL, UNIQUE(user_id, draw_date))")

init_db()

@app.get("/")
def index():
    return FileResponse("static/index.html")

class UserIn(BaseModel):
    user_id: str
    username: str = "Игрок"

@app.post("/api/register")
def register(payload: UserIn):
    # DEMO ONLY: в production обязательно валидируйте Telegram WebApp initData.
    with connect() as con:
        con.execute(
            "INSERT INTO users(user_id, username, created_at) VALUES(?,?,?) "
            "ON CONFLICT(user_id) DO UPDATE SET username=excluded.username",
            (payload.user_id, payload.username, date.today().isoformat())
        )
    return {"ok": True, "username": payload.username}

@app.get("/api/prizes")
def prizes():
    total = sum(p["weight"] for p in PRIZES)
    return {"prizes": [{**p, "chance": round(p["weight"] / total * 100, 2)} for p in PRIZES]}

class DrawIn(BaseModel):
    user_id: str

@app.post("/api/draw")
def draw(payload: DrawIn):
    # Бесплатная ежедневная попытка. Не является покупкой шанса.
    today = date.today().isoformat()
    with connect() as con:
        old = con.execute("SELECT prize_id FROM draws WHERE user_id=? AND draw_date=?",
                          (payload.user_id, today)).fetchone()
        if old:
            raise HTTPException(status_code=409, detail="Сегодняшняя попытка уже использована")
        prize = random.choices(PRIZES, weights=[p["weight"] for p in PRIZES], k=1)[0]
        con.execute("INSERT INTO draws(user_id, prize_id, draw_date, created_at) VALUES(?,?,?,?)",
                    (payload.user_id, prize["id"], today, today))
    return {"ok": True, "prize": prize, "message": "Результат сохранён. NFT пока демонстрационный."}
