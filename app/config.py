from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv
import os

BASE_DIR = Path(__file__).resolve().parent.parent

load_dotenv(BASE_DIR / ".env")


@dataclass
class Settings:
    openai_api_key: str | None = os.getenv("OPENAI_API_KEY")
    llm_provider: str = os.getenv("LLM_PROVIDER", "openai")  # openai | yandex | mock
    bot_token: str | None = os.getenv("BOT_TOKEN")

    data_dir: Path = BASE_DIR / "data"
    raw_faq_path: Path = BASE_DIR / "data" / "raw_faq.json"
    faiss_dir: Path = BASE_DIR / "data" / "faiss"


settings = Settings()
