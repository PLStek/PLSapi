from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    youtube_api_key: str
    secret_key: str
    algorithm: str

    class Config:
        env_file = ".env"


settings = Settings()
