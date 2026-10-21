import os
from pathlib import Path
from typing import Literal, Optional
from pydantic import BaseModel, Field

def load_env(env_path: Optional[str] = None):
    """Load environment variables from a .env file if it exists."""
    path = Path(env_path or ".env")
    if not path.exists():
        return
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip("'\"")
            if key and key not in os.environ:
                os.environ[key] = val

# Load default .env on module import
load_env()

class AppConfig(BaseModel):
    """Application configuration settings."""
    llm_provider: Literal["groq", "gemini", "mock"] = Field(
        default_factory=lambda: os.getenv("LLM_PROVIDER", "groq").lower()  # type: ignore
    )
    llm_model: Optional[str] = Field(
        default_factory=lambda: os.getenv("LLM_MODEL")
    )
    groq_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GROQ_API_KEY")
    )
    google_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("GOOGLE_API_KEY")
    )
    search_provider: Literal["duckduckgo", "mock"] = Field(
        default_factory=lambda: os.getenv("SEARCH_PROVIDER", "duckduckgo").lower()  # type: ignore
    )
    search_api_key: Optional[str] = Field(
        default_factory=lambda: os.getenv("SEARCH_API_KEY")
    )
    default_lookback_days: int = Field(
        default_factory=lambda: int(os.getenv("DEFAULT_LOOKBACK_DAYS", "90"))
    )
    request_timeout_seconds: int = Field(
        default_factory=lambda: int(os.getenv("REQUEST_TIMEOUT_SECONDS", "15"))
    )
    max_search_results: int = Field(
        default_factory=lambda: int(os.getenv("MAX_SEARCH_RESULTS", "5"))
    )
    cache_enabled: bool = Field(
        default_factory=lambda: os.getenv("CACHE_ENABLED", "true").lower() in ("true", "1", "yes")
    )
    output_dir: str = Field(
        default_factory=lambda: os.getenv("OUTPUT_DIR", "runs")
    )

    def get_resolved_model(self) -> str:
        """Resolve model name if not explicitly specified."""
        if self.llm_model:
            return self.llm_model
        if self.llm_provider == "groq":
            return "openai/gpt-oss-120b"
        elif self.llm_provider == "gemini":
            return "gemini-1.5-flash"
        return "mock-intelligence-v1"

# Global singleton config
config = AppConfig()
