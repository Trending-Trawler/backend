import os

import uvicorn

from fastapi import FastAPI, UploadFile, Depends
from fastapi.responses import Response, FileResponse
from fastapi.middleware.cors import CORSMiddleware

from comments import get_comments
from screenshots import create_screenshots, zip_screenshots
from videoCreation import make_final_video
from tts import tts
from validators import validate_thread, validate_voice, validate_video

app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://localhost:3000",
    "https://trending-trawler.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/comments")
async def comment_screenshots(thread_url: str = Depends(validate_thread)):
    response = Response(
        zip_screenshots(
            await create_screenshots(thread_url, await get_comments(thread_url))
        ),
        media_type="application/x-zip-compressed",
        headers={"Content-Disposition": "attachment; filename=thread_comments.zip"},
    )
    response.set_cookie(key="c_thread_url", value=thread_url)
    return response


@app.get("/voices")
async def voices():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "../assets/voices.json")
    )


@app.get("/voice/preview")
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


@app.get("/videos/preview")
async def video_preview():
    return FileResponse(
        os.path.join(os.path.dirname(__file__), "../assets/videos/preview/previews.zip")
    )


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
    # response = FileResponse(
    #     os.path.join(os.path.dirname(__file__), f"../assets/result/video.mp4")
    # )
    # response.set_cookie(key="c_voice_id", value=voice_id)
    # response.set_cookie(key="c_thread_url", value=thread_url)
    # response.set_cookie(key="c_video_id", value=video_id)

    await make_final_video(thread_url, voice_id, video_id)

    print("Voice ID:", voice_id, "  Thread URL:", thread_url, "  Video ID:", video_id)
    return FileResponse(os.path.join(os.path.dirname(__file__), f"../assets/video.mp4"))


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, proxy_headers=True, reload=True)
