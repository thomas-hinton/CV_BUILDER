# My app
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pathlib import Path
from fastapi.staticfiles import StaticFiles

# Personal modules
from python.database.db_add_user import addUserIntoDatabaseByName
from python.database.db_get_user import getUserFromDatabaseByName


app = FastAPI()
app.mount("/css", StaticFiles(directory="css"), name="css")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/js", StaticFiles(directory="js"), name="js")


BASE_DIR = Path(__file__).resolve().parent


@app.get("/")
def home():
    return FileResponse(BASE_DIR / "index.html")

@app.get("/admin")
def admin():
    return FileResponse(BASE_DIR / "admin.html")

@app.post("/modify_name")
def modify_name(name: str):
    print(f"Modifying name to {name}")
    return(addUserIntoDatabaseByName(name))

@app.get("/get_user_by_name")
def get_user_by_name(name: str):
    print(f"Getting user by name {name}")
    return(getUserFromDatabaseByName(name))

