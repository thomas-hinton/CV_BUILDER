# My app
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path

app = FastAPI()

coffees = []

BASE_DIR = Path(__file__).resolve().parent

@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/admin")
def admin():
    return FileResponse(BASE_DIR / "admin.html")