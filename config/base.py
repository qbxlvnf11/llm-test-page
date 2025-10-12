from pydantic_settings import BaseSettings, SettingsConfigDict

from pydantic import Field
from typing import List, Dict
from pathlib import Path

from .utils import load_models_from_file, load_pricing_from_file

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

    # GEMINI_API_KEY: str
    GOOGLE_APPLICATION_CREDENTIALS_PATH: str
    GEMINI_MODELS: List[str] = Field(default_factory=load_models_from_file)
    MODEL_PRICING: Dict[str, Dict[str, float]] = Field(default_factory=load_pricing_from_file)

settings = Settings()