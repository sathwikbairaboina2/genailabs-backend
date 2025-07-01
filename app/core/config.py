from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    CELERY_BROKER_URL: str = "redis://127.0.0.1:6379/0"
    CELERY_BACKEND_URL: str = "redis://127.0.0.1:6379/0"

    MONGO_URI: str = (
        "mongodb://admin:password@mongodb:27017/genailabs_db?authSource=admin"
    )
    MONGO_DB_NAME: str = "genailabs_db"
    QDRANT_HOST: str = "http://127.0.0.1:6333"

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="allow"
    )


settings = Settings()
#  "mongodb://admin:password@mongodb:27017/genailabs_db?authSource=admin"
