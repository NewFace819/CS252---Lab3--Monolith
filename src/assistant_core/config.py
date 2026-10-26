"""Read settings from the environment and validate them.

Owner: Thông (issue #2). Uses the team's agreed Settings fields and signature.
"""

import math
import os
from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseModel, Field, ValidationError

from assistant_core.errors import ConfigError


class Settings(BaseModel):
    data_dir: Path = Path("data")
    llm_provider: str = "stub"
    llm_api_key: str | None = Field(default=None, repr=False)  # never printed
    credit_rate_vnd: int = 450_000
    retake_multiplier: float = 1.5
    max_credits: int = 30
    log_level: str = "INFO"


def load_settings(env_file: str | None = ".env") -> Settings:
    """Build Settings from env vars (and ``env_file`` if given).

    Raises ConfigError if LLM_PROVIDER != "stub" and LLM_API_KEY is missing.
    """
    if env_file:
        load_dotenv(env_file, override=False)
    try:
        settings = Settings(
            data_dir=Path(os.getenv("ASSISTANT_DATA_DIR", "data")),
            llm_provider=os.getenv("LLM_PROVIDER", "stub").strip(),
            llm_api_key=os.getenv("LLM_API_KEY", "").strip() or None,
            credit_rate_vnd=int(os.getenv("CREDIT_RATE_VND", "450000")),
            retake_multiplier=float(os.getenv("RETAKE_MULTIPLIER", "1.5")),
            max_credits=int(os.getenv("MAX_CREDITS", "30")),
            log_level=os.getenv("LOG_LEVEL", "INFO").strip().upper(),
        )
    except (ValueError, ValidationError):
        # Do not expose environment values or Pydantic's input dump in errors.
        raise ConfigError("Invalid configuration: check the numeric environment variables.") from None
    if not settings.llm_provider:
        raise ConfigError("LLM_PROVIDER must not be empty.")
    if settings.llm_provider != "stub" and not settings.llm_api_key:
        raise ConfigError("LLM_API_KEY is required when LLM_PROVIDER is not stub.")
    if settings.credit_rate_vnd <= 0 or settings.max_credits <= 0:
        raise ConfigError("CREDIT_RATE_VND and MAX_CREDITS must be positive integers.")
    if not math.isfinite(settings.retake_multiplier) or settings.retake_multiplier <= 0:
        raise ConfigError("RETAKE_MULTIPLIER must be finite and positive.")
    if settings.log_level not in {"DEBUG", "INFO", "WARNING", "WARN", "ERROR", "CRITICAL", "FATAL", "NOTSET"}:
        raise ConfigError("LOG_LEVEL must name a standard Python logging level.")
    return settings
