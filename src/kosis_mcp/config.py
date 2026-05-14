from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    api_key: str | None = None
    base_url: str = "https://kosis.kr/openapi"
    timeout_seconds: float = 30.0


def load_settings() -> Settings:
    timeout_raw = os.getenv("KOSIS_TIMEOUT", "30")
    try:
        timeout_seconds = float(timeout_raw)
    except ValueError:
        timeout_seconds = 30.0

    return Settings(
        api_key=os.getenv("KOSIS_API_KEY"),
        base_url=os.getenv("KOSIS_BASE_URL", "https://kosis.kr/openapi").rstrip("/"),
        timeout_seconds=timeout_seconds,
    )

