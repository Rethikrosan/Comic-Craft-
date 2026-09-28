from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    app_name: str = "ComicCraft"
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True

    gemini_api_key: str = ""
    gemini_flash_model: str = "gemini-2.5-flash"
    gemini_pro_model: str = "gemini-2.5-pro"

    image_backend: str = "hf"
    hf_api_key: str = ""
    hf_image_model: str = "stabilityai/stable-diffusion-xl-base-1.0"
    hf_provider: str = "hf-inference"

    panels: int = 5
    image_width: int = 768
    image_height: int = 768
    image_steps: int = 25

    output_dir: Path = BASE_DIR / "static" / "panels"
    export_dir: Path = BASE_DIR / "static" / "exports"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.export_dir.mkdir(parents=True, exist_ok=True)
    return settings
