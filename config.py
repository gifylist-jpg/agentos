import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH, override=True)


def env_bool(name: str, default: str = "false") -> bool:
    return os.getenv(name, default).strip().lower() in ["1", "true", "yes", "on"]


class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")

    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    DOUBAO_API_KEY = os.getenv("DOUBAO_API_KEY", "")
    DOUBAO_BASE_URL = os.getenv("DOUBAO_BASE_URL", "")

    ENABLE_GPT = env_bool("ENABLE_GPT", "false")
    ENABLE_DEEPSEEK = env_bool("ENABLE_DEEPSEEK", "true")
    ENABLE_CLAUDE = env_bool("ENABLE_CLAUDE", "false")
    ENABLE_DOUBAO = env_bool("ENABLE_DOUBAO", "false")
