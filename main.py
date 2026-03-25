# My app
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")


BASE_DIR = Path(__file__).resolve().parent


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/admin")
def admin():
    return FileResponse(BASE_DIR / "admin.html")