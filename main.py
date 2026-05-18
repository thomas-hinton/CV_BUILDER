from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

# Routers
from python.routers.auth import router as auth_router
from python.routers.cv import router as cv_router
from python.routers.profiles import router as profiles_router

app = FastAPI()
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/js", StaticFiles(directory="js"), name="js")

app.include_router(auth_router)
app.include_router(profiles_router)
app.include_router(cv_router)

BASE_DIR = Path(__file__).resolve().parent


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")


@app.get("/admin")
def admin():
    return FileResponse(BASE_DIR / "admin.html")
