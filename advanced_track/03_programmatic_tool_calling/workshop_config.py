"""Load the shared ScaDS configuration from the repository root."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

TRACK_DIR = Path(__file__).resolve().parent
REPOSITORY_ROOT = TRACK_DIR.parents[1]
ROOT_ENV_FILE = REPOSITORY_ROOT / ".env"


@dataclass(frozen=True)
class ScadsConfig:
    api_key: str
    base_url: str
    model: str


def load_scads_config(default_base_url: str, default_model: str) -> ScadsConfig:
    """Read the shared configuration from the repository root."""
    load_dotenv(ROOT_ENV_FILE)

    api_key = os.getenv("SCADS_API_KEY")
    if not api_key:
        raise SystemExit(f"SCADS_API_KEY fehlt. Lege {ROOT_ENV_FILE} anhand von .env.example an.")

    return ScadsConfig(
        api_key=api_key,
        base_url=os.getenv("SCADS_BASE_URL", default_base_url),
        model=os.getenv("SCADS_MODEL", default_model),
    )
