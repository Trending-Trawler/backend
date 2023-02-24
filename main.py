from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello"}


@app.get("/threadURL")
async def reddit_thread_url(rt_url: str):
    return rt_url

@app.get("/videoURL")
async def video_url(yt_url: str):
    return yt_url


@app.get("/downloadVideo")
async def download_video():
    return "This is the video"
