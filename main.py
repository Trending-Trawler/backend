from fastapi import FastAPI
from fastapi.responses import FileResponse

import context

app = FastAPI()


@app.get("/thread")
async def reddit_thread_url(rt_url: str):
    # should return images of reddit_thread_comments
    context.thread_url = rt_url
    return True


@app.get("/preview/video")
async def video_preview():
    # should return images of reddit_thread_comments
    return True


@app.get("/preview/voice")
async def voice_preview():
    return True


@app.post("/video")
async def video_upload():
    return True


@app.get("/video")
async def download_video(voice_id, thread_url: str | None = None, video_id: int | None = None):
    # respond with a video file
    print(context.thread_url, voice_id, video_id)
    return FileResponse("final_video.mp4")
