# My app
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

coffees = []

@app.get("/")
def home():
    return "Bienvenue !"

