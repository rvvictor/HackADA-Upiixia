"""The only place with model IDs and keys. Values come from the env file; nobody hard-codes them elsewhere."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = ROOT / ("." + "env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    openai_api_key: str = ""
    openai_model: str = "gpt-5.6-terra"
    openai_fallback_model: str = "gpt-5-mini"
    openai_transcribe_model: str = "gpt-transcribe"
    mapbox_token: str = ""
    telegram_bot_token: str = ""
    alcaldias: str = "09003,09007"
    demo_mode: bool = False

    @property
    def alcaldias_list(self) -> list[str]:
        return [a.strip() for a in self.alcaldias.split(",") if a.strip()]


settings = Settings()

DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
LIVE_DIR = DATA_DIR / "live"
DEMO_DIR = DATA_DIR / "demo"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
