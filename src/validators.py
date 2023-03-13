from typing import Union
from fastapi import HTTPException, Cookie
from tts import voices
from settings import settings


async def validate_thread(
    thread_url: Union[str, None] = None,
    c_thread_url: str = Cookie(default=settings.default_thread_url),
):
    if not thread_url:
        thread_url = c_thread_url
    if (
        not thread_url.startswith("https://www.reddit.com/r/")
        or "/comments/" not in thread_url
    ):
        raise HTTPException(status_code=400, detail="Invalid thread URL")
    return thread_url


async def validate_voice(
    voice_id: Union[str, None] = None,
    c_voice_id: str = Cookie(default=settings.default_voice_id),
):
    if not voice_id:
        voice_id = c_voice_id
    if voice_id not in voices:
        raise HTTPException(status_code=400, detail="Invalid voice ID")
    return voice_id


async def validate_video(
    video_id: Union[str, None] = None,
    c_video_id: str = Cookie(default=settings.default_video_id),
):
    if not video_id:
        video_id = c_video_id
    # TODO: Check if video exists in folder
    # if video_id not in videos:
    #     raise HTTPException(status_code=400, detail="Invalid video ID")
    return video_id
