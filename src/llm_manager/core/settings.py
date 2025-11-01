"""Configuration settings for LLM Manager.

Environment Variable Overrides:
-------------------------------
Per-Model Overrides:
  MODEL_CONTEXT_<MODEL_NAME>=<tokens>    - Override context window
  MODEL_MAX_TOKENS_<MODEL_NAME>=<tokens> - Override max output tokens

  Example:
    MODEL_CONTEXT_GPT_4O=200000
    MODEL_MAX_TOKENS_GPT_4O=8192
    MODEL_CONTEXT_LLAMA3_2=131072

Global Overrides:
  INPUT_BUDGET_TOKENS=<tokens>  - Cap input budget globally
  MAX_OUTPUT_TOKENS=<tokens>    - Cap output budget globally

  Example:
    INPUT_BUDGET_TOKENS=80000
    MAX_OUTPUT_TOKENS=1024
"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


# Project root directory
PROJECT_ROOT = Path(__file__).resolve().parents[3]


class Settings(BaseSettings):
    """Application settings with environment variable support."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application paths
    DATA_DIR: Path = Path.home() / ".llm_manager" / "data"
    RUNTIME_DIR: Path = Path.home() / ".llm_manager" / "runtime"
    PROMPTS_DIR: Path = Path.home() / ".llm_manager" / "prompts"

    # Pane content persistence files
    USER_PROMPT_FILE: Path = DATA_DIR / "user_prompt.txt"
    SYSTEM_PROMPT_FILE: Path = DATA_DIR / "system_prompt.txt"
    CONTEXT_FILE: Path = DATA_DIR / "context.txt"
    SELECTED_MODEL_FILE: Path = DATA_DIR / "selected_model.txt"

    # Application configuration
    EDITOR: str = "nvim"
    DEBUG: bool = False

    # LLM API Configuration
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = "https://api.openai.com/v1"
    ANTHROPIC_API_KEY: str = ""
    OLLAMA_BASE_URL: str = "http://localhost:11434"

    # OpenAI-compatible servers (vLLM, llama.cpp, etc.)
    OPENAI_COMPATIBLE_BASE_URL: str = "http://localhost:8000/v1"
    OPENAI_COMPATIBLE_API_KEY: str = ""  # Optional, depends on server

    # Default model
    DEFAULT_MODEL: str = "openai:gpt-4o-mini"

    # Streaming toggle
    ENABLE_STREAMING: bool = True

    # Conversation history
    CONVERSATION_HISTORY_FILE: Path = DATA_DIR / "conversation_history.json"
    MAX_HISTORY_ITEMS: int = 100

    def ensure_dirs(self) -> None:
        """Ensure all required directories exist."""
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
        self.PROMPTS_DIR.mkdir(parents=True, exist_ok=True)

    def ensure_files(self) -> None:
        """Ensure all pane files exist with default content."""
        self.ensure_dirs()

        # Create files with default content if they don't exist
        if not self.USER_PROMPT_FILE.exists():
            self.USER_PROMPT_FILE.write_text("", encoding="utf-8")

        if not self.SYSTEM_PROMPT_FILE.exists():
            self.SYSTEM_PROMPT_FILE.write_text("", encoding="utf-8")

        if not self.CONTEXT_FILE.exists():
            self.CONTEXT_FILE.write_text("", encoding="utf-8")

        if not self.SELECTED_MODEL_FILE.exists():
            self.SELECTED_MODEL_FILE.write_text(self.DEFAULT_MODEL, encoding="utf-8")


# Global settings instance
settings = Settings()
