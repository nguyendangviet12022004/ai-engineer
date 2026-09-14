"""Application settings loaded from .env and environment variables."""
from __future__ import annotations

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
    """Central place for all configuration — never hardcode these values."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")
    app_name: str = "expconfig"
    api_key: SecretStr
    max_epochs: int = 100
    debug: bool = False


if __name__ == "__main__":
    # mypy sees AppSettings() as missing the required `api_key` argument,
    # because it cannot know pydantic-settings fills it in from .env/env
    # vars at runtime. This is a known, deliberate mismatch — not a real
    # bug — so we silence exactly this error code with a clear reason.
    settings = AppSettings()  # type: ignore[call-arg]
    print(settings.app_name, settings.max_epochs, settings.debug)
    print(settings.api_key)                     # masked in repr
    print(settings.api_key.get_secret_value())   # real value, on purpose
