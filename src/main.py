import uvicorn

from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import Response, FileResponse

from screenshots import create_screenshots
from tts import tts
from validators import validate_thread, validate_voice, validate_video


app = FastAPI()


@app.get("/thread")
async def reddit_thread_url(thread_url: str = Depends(validate_thread)):
    response = Response(
        await create_screenshots(thread_url),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=thread_comments.zip"},
    )
    response.set_cookie(key="c_thread_url", value=thread_url)
    return response


@app.get("/preview/video")
async def video_preview():
    return True


@app.get("/preview/voice")
async def voice_preview(
    voice_id: str = Depends(validate_voice),
    text: str = "Trending Trawler Text to Speech",
):
    response = Response(
        tts(voice_id, text),
        media_type="audio/mpeg",
        headers={"Content-Disposition": "attachment; filename=voice.mp3"},
    )
    response.set_cookie(key="c_voice_id", value=voice_id)
    return response


@app.post("/video")
async def video_upload(video: UploadFile, response: Response):
    response.set_cookie(key="c_video_id", value=video.filename)
    return True


@app.get("/video")
async def download_video(
    thread_url: str = Depends(validate_thread),
    voice_id: str = Depends(validate_voice),
    video_id: str = Depends(validate_video),
):
    response = FileResponse("final_video.mp4")
    response.set_cookie(key="c_voice_id", value=voice_id)
    response.set_cookie(key="c_thread_url", value=thread_url)
    response.set_cookie(key="c_video_id", value=video_id)

    print("Voice ID:", voice_id, "  Thread URL:", thread_url, "  Video ID:", video_id)
    return response


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, proxy_headers=True, reload=True)
