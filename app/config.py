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
    denue_token: str = ""
    alcaldias: str = "09003,09007"
    demo_mode: bool = False
    # v2 §5: primero en mapa, panel, bot y selectores
    alcaldias_prioridad: str = "09003,09007"
    # v2 §2: negocio local = comercio al por menor (46) o servicios de consumo (72, 81), con estos estratos DENUE
    negocio_local_estratos: str = "0 a 5 personas,6 a 10 personas"
    negocio_local_scian: str = "46,72,81"
    # v2 §4.3: prioridad = peso_edad (si edad en rango) + peso_estudiante (si estudia); solo ordena, no excluye
    repartidor_edad_minima: int = 18
    prioridad_edad_min: int = 18
    prioridad_edad_max: int = 30
    prioridad_peso_edad: int = 1
    prioridad_peso_estudiante: int = 1

    @property
    def alcaldias_list(self) -> list[str]:
        return [a.strip() for a in self.alcaldias.split(",") if a.strip()]

    @property
    def alcaldias_prioridad_list(self) -> list[str]:
        return [a.strip() for a in self.alcaldias_prioridad.split(",") if a.strip()]


settings = Settings()

DATA_DIR = ROOT / "data"
PROCESSED_DIR = DATA_DIR / "processed"
LIVE_DIR = DATA_DIR / "live"
DEMO_DIR = DATA_DIR / "demo"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
