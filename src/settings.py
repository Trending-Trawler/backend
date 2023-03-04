import os
from functools import lru_cache
from pydantic import BaseSettings, SecretStr, Field


class Settings(BaseSettings):
    reddit_client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    reddit_client_secret: SecretStr = Field(..., env="REDDIT_CLIENT_SECRET")

    tiktok_session_id: str = Field(..., env="TIKTOK_SESSION_ID")

    default_voice_id: str = Field("random", env="DEFAULT_VOICE_ID")
    default_thread_url: str = Field(
        "https://www.reddit.com/r/AskReddit/comments/ablzuq/people_who_havent_pooped_in_2019_yet_why_are_you/",
        env="DEFAULT_THREAD_URL",
    )
    default_video_id: str = Field("default.mp4", env="DEFAULT_VIDEO_ID")

    class Config:
        env_file = os.path.join(os.path.dirname(__file__), "../.env")
        env_file_encoding = "utf-8"


# lru_cache() is used to cache the result of the function
# so that the .env file is only read once from disk
@lru_cache()
def createSettings():
    return Settings()


settings = createSettings()
