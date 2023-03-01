from fastapi import FastAPI
from fastapi.responses import Response, FileResponse
from config import settings
from screenshots import create_screenshots

app = FastAPI()


@app.get("/thread")
async def reddit_thread_url(url: str):
    return Response(
        await create_screenshots(url),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=thread_comments.zip"},
    )


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
async def download_video(
    voice_id, thread_url: str | None = None, video_id: int | None = None
):
    # respond with a video file
    print(thread_url, voice_id, video_id)
    return FileResponse("final_video.mp4")
