from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    MONGO_URI: str
    DB_NAME: str
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: float = 60
    REFRESH_TOKEN_EXPIRE_DAYS: float = 7
    ORIGIN_URL: str

    class Config:
        env_file = ".env"

settings = Settings()