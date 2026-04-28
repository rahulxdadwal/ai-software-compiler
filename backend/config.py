"""Application configuration loaded from environment variables."""

from pydantic_settings import BaseSettings
from typing import Optional
import os
from dotenv import load_dotenv

# Load .env from project root
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env"))


class Settings(BaseSettings):
    """Application settings with env-var overrides."""

    openai_api_key: Optional[str] = None
    mock_mode: bool = True
    openai_model: str = "gpt-4o"
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    llm_temperature: float = 0.1
    max_repair_cycles: int = 3

    class Config:
        env_file = ".env"
        extra = "ignore"

    @property
    def use_mock(self) -> bool:
        """Use mock mode if explicitly set or if no API key is provided."""
        return self.mock_mode or not self.openai_api_key


settings = Settings()
