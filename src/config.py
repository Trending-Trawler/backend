from functools import lru_cache
from pydantic import BaseSettings, SecretStr, Field


class Settings(BaseSettings):
    reddit_client_id: str = Field(..., env="REDDIT_CLIENT_ID")
    reddit_client_secret: SecretStr = Field(..., env="REDDIT_CLIENT_SECRET")

    tiktok_session_id: str = Field(..., env="TIKTOK_SESSION_ID")

    class Config:
        env_file = "../.env"
        env_file_encoding = "utf-8"


# lru_cache() is used to cache the result of the function
# so that the .env file is only read once from disk
@lru_cache()
def createSettings():
    return Settings()


settings = createSettings()
