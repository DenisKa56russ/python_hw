from pydantic_settings import BaseSettings, SettingsConfigDict

from latte_gallery.accounts.schemas import AccountCreateSchema

import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME: str = "Latte Gallery"
    BASE_URL: str = "localhost"
    PORT: int = 8000
    DEBUG: bool = True if os.getenv("DEBUG") == "True" else False

    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./latte_gallery.db")

    SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_THIS_SECRET")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_SECONDS: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 3600))


settings = Settings()
class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(secrets_dir="/run/secrets")

    db_url: str
    initial_accounts: list[AccountCreateSchema]
