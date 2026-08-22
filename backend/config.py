import os
from pathlib import Path
from pydantic import ConfigDict
from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    BASE_DIR: Path = BASE_PATH
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    DEBUG: bool = True
    
    DATABASE_URL: str = f"sqlite:///{BASE_PATH}/database/resume_screener.db"
    
    LLM_PROVIDER: str = "auto"
    GEMINI_API_KEY: str = ""
    GEMINI_MODEL: str = "gemini-1.5-flash"
    OPENAI_API_KEY: str = ""
    OPENAI_MODEL: str = "gpt-4o-mini"
    
    DEFAULT_SHORTLIST_THRESHOLD: float = 7.0
    MAX_UPLOAD_SIZE_MB: int = 10
    
    UPLOAD_DIR: Path = BASE_PATH / "uploads"
    DATA_DIR: Path = BASE_PATH / "data"
    DB_DIR: Path = BASE_PATH / "database"

    model_config = ConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()

# Ensure directories exist
settings.UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.DB_DIR.mkdir(parents=True, exist_ok=True)

