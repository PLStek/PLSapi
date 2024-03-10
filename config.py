from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    youtube_api_key: str
    token_secret: str
    discord_client_id: str
    discord_client_secret: str
    storage_path: str

    class Config:
        env_file = ".env"


settings = Settings()
