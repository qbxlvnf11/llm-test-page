from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field
from typing import List, Dict
from pathlib import Path

from .utils import load_models_from_file, load_pricing_from_file

class DBSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    CLOUD_SQL_INSTANCE: str

    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    DB_API_DRIVER: str
    DB_DRIVER: str

    DB_PROMPT_TABLE: str

db_settings = DBSettings()