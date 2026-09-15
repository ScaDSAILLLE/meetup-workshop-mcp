"""Lädt die gemeinsamen ScaDS-Einstellungen aus der Root-``.env``.

Das Laden erfolgt erst beim ersten echten API-Aufruf. Offline-Tests und reine
Modulimporte lesen deshalb keine Zugangsdaten.
"""

from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

REPOSITORY_ROOT = Path(__file__).resolve().parents[3]
ENV_FILE = REPOSITORY_ROOT / ".env"

# Fallback, falls die ``.env`` fehlt oder unvollständig ist. Das Frontend muss
# auch dann ein brauchbares Zeitbudget bekommen.
DEFAULT_FRONTEND_REQUEST_TIMEOUT = 300


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
    # Lesetimeout je LLM-Aufruf. Reasoning-Modelle brauchen auf dem Cluster
    # regelmäßig deutlich über eine Minute pro Antwort.
    scadsai_request_timeout: int = 300
    # Zeitbudget des Browsers für einen kompletten Vergleichslauf, also alle
    # sequenziellen LLM-Aufrufe zusammen. Muss deutlich über
    # ``scadsai_request_timeout`` liegen.
    frontend_request_timeout: int = DEFAULT_FRONTEND_REQUEST_TIMEOUT


@lru_cache
def get_settings() -> Settings:
    """Lädt und validiert die Root-Konfiguration genau einmal."""
    return Settings()
