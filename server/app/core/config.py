import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from pydantic_settings import BaseSettings


def _load_agent_config() -> dict:
    config_path = Path(__file__).resolve().parents[2] / "agent_config.json"
    if not config_path.exists():
        return {}

    try:
        return json.loads(config_path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def _build_database_url_from_agent_config() -> str | None:
    database = _load_agent_config().get("database", {})
    host = str(database.get("host", "")).strip()
    port = database.get("port")
    user = str(database.get("user", "")).strip()
    password = database.get("password", "")
    database_name = str(database.get("database", "")).strip()

    if not all([host, port, user, database_name]):
        return None

    encoded_password = quote_plus(str(password))
    return (
        f"mysql+pymysql://{quote_plus(user)}:{encoded_password}"
        f"@{host}:{port}/{database_name}?charset=utf8mb4"
    )


class Settings(BaseSettings):
    DATABASE_URL: str = _build_database_url_from_agent_config() or "sqlite:///./app.db"
    SECRET_KEY: str = os.getenv("SECRET_KEY", "local-dev-secret-key")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440")
    )

    def __init__(self, **values):
        super().__init__(**values)
        database_url = _build_database_url_from_agent_config()
        if database_url:
            self.DATABASE_URL = database_url

    class Config:
        env_file = ".env"


settings = Settings()
