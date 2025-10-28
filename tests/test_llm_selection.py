"""Tests for LLM selection and client."""

import pytest
from pathlib import Path
from unittest.mock import patch

from llm_manager.core.models import get_model_config, AVAILABLE_MODELS
from llm_manager.core.settings import Settings


class TestModelConfiguration:
    """Test model configuration."""

    def test_all_models_loadable(self):
        """Test that all models can be loaded."""
        for model_name in AVAILABLE_MODELS:
            config = get_model_config(model_name)
            assert config is not None
            assert config.name == model_name
            assert config.context_window > 0
            assert config.max_output_tokens > 0

    def test_openai_models(self):
        """Test OpenAI model configurations."""
        gpt4o = get_model_config("openai:gpt-4o")
        assert gpt4o is not None
        assert gpt4o.provider == "openai"
        assert gpt4o.display_name == "GPT-4o"
        assert gpt4o.context_window == 128000

    def test_anthropic_models(self):
        """Test Anthropic model configurations."""
        claude = get_model_config("anthropic:claude-3-5-sonnet-latest")
        assert claude is not None
        assert claude.provider == "anthropic"
        assert claude.display_name == "Claude 3.5 Sonnet"
        assert claude.context_window == 200000


class TestSettings:
    """Test settings with LLM configuration."""

    def test_default_model_setting(self):
        """Test that default model is set."""
        settings = Settings()
        assert settings.DEFAULT_MODEL == "openai:gpt-4o-mini"

    def test_selected_model_file_creation(self, tmp_path):
        """Test that selected model file is created."""
        with patch.object(Path, 'home', return_value=tmp_path):
            settings = Settings()
            settings.DATA_DIR = tmp_path / "data"
            settings.SELECTED_MODEL_FILE = settings.DATA_DIR / "selected_model.txt"

            settings.ensure_files()

            assert settings.SELECTED_MODEL_FILE.exists()
            content = settings.SELECTED_MODEL_FILE.read_text()
            assert content == settings.DEFAULT_MODEL


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
