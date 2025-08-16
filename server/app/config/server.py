from contextlib import asynccontextmanager

from app.api import api_router
from app.config import close_redis, init_redis
from fastapi import APIRouter, FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles


async def lifespan(app: FastAPI):
    await init_redis()
    yield
    await close_redis()


app = FastAPI(lifespan=lifespan)

router = APIRouter()

app.include_router(api_router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
def root():
    return {
        "app": "FocusTube",
        "app_description": "FocusTube is an app designed to help you watch a YouTube video without any distractions",
        "author": {
            "name": "Drona Raj Gyawali",
            "email": "dronarajgyawali@gmail.com",
            "x": "https://x.com/dornaoffical",
            "github": "https://github.com/drona-gyawali",
            "linkdein": "https://www.linkedin.com/in/dorna-gyawali",
        },
        "message": "Please visit and explore our APIs at /docs",
    }


@app.get("/favicon.ico")
def favicon():
    return FileResponse("app/static/favicon.ico")
