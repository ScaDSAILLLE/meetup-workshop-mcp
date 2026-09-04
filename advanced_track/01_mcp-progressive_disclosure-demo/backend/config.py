"""Lädt die drei gemeinsamen ScaDS-Einstellungen aus der Root-``.env``.

Das Laden erfolgt erst beim ersten echten API-Aufruf. Offline-Tests und reine
Modulimporte lesen deshalb keine Zugangsdaten.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPOSITORY_ROOT / ".env"


class Settings(BaseSettings):
    """Typisierte Konfiguration des OpenAI-kompatiblen Endpoints."""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    scads_api_key: str
    scads_base_url: str
    scads_model: str


@lru_cache
def get_settings() -> Settings:
    """Lädt und validiert die Root-Konfiguration genau einmal."""
    return Settings()
