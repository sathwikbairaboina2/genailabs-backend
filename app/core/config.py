from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_BACKEND_URL: str = "redis://127.0.0.1:6379/0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
