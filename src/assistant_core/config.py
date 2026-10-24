"""Read settings from the environment and validate them.

Owner: Thông (see issue). Contract below is fixed; replace the stub body.
"""

from pathlib import Path

from pydantic import BaseModel, Field


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
    raise NotImplementedError("config.load_settings — owned by Thông")
