"""Configuration settings for LLM Manager."""

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
