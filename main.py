from fastapi import FastAPI
from pydantic import BaseModel


class Config(BaseModel):
    rt_url: str
    yt_url: str | None = None


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.post("/config")
async def video_config(config: Config):
    return config


@app.get("/downloadVideo")
async def download_video():
    return "This is the video"
