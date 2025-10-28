"""Integration tests for LLM Manager."""

import tempfile
from pathlib import Path
import pytest
from unittest.mock import patch

from llm_manager.core.settings import Settings
from llm_manager.core.persistence import PaneStorage, PaneManager


class TestIntegration:
    """Integration tests combining multiple components."""

    def test_full_workflow(self, tmp_path):
        """Test complete workflow: settings -> persistence -> read/write."""
        # Setup custom settings
        with patch.object(Path, 'home', return_value=tmp_path):
            settings = Settings()
            settings.DATA_DIR = tmp_path / "data"
            settings.USER_PROMPT_FILE = settings.DATA_DIR / "user_prompt.txt"
            settings.SYSTEM_PROMPT_FILE = settings.DATA_DIR / "system_prompt.txt"
            settings.CONTEXT_FILE = settings.DATA_DIR / "context.txt"

            # Initialize directories and files
            settings.ensure_files()

            # Create pane manager
            manager = PaneManager(
                settings.USER_PROMPT_FILE,
                settings.SYSTEM_PROMPT_FILE,
                settings.CONTEXT_FILE
            )

            # Write content to panes
            manager.user_prompt.write("What is Python?")
            manager.system_prompt.write("You are a helpful assistant.")
            manager.context.write("Python programming language context")

            # Verify files exist and contain correct content
            assert settings.USER_PROMPT_FILE.exists()
            assert settings.SYSTEM_PROMPT_FILE.exists()
            assert settings.CONTEXT_FILE.exists()

            assert settings.USER_PROMPT_FILE.read_text() == "What is Python?"
            assert settings.SYSTEM_PROMPT_FILE.read_text() == "You are a helpful assistant."
            assert settings.CONTEXT_FILE.read_text() == "Python programming language context"

            # Create new manager instance (simulating app restart)
            manager2 = PaneManager(
                settings.USER_PROMPT_FILE,
                settings.SYSTEM_PROMPT_FILE,
                settings.CONTEXT_FILE
            )

            # Verify content persists
            assert manager2.user_prompt.read() == "What is Python?"
            assert manager2.system_prompt.read() == "You are a helpful assistant."
            assert manager2.context.read() == "Python programming language context"

    def test_empty_panes_on_first_run(self, tmp_path):
        """Test that panes are empty on first run."""
        with patch.object(Path, 'home', return_value=tmp_path):
            settings = Settings()
            settings.DATA_DIR = tmp_path / "data"
            settings.USER_PROMPT_FILE = settings.DATA_DIR / "user_prompt.txt"
            settings.SYSTEM_PROMPT_FILE = settings.DATA_DIR / "system_prompt.txt"
            settings.CONTEXT_FILE = settings.DATA_DIR / "context.txt"

            # Initialize
            settings.ensure_files()

            # Create manager
            manager = PaneManager(
                settings.USER_PROMPT_FILE,
                settings.SYSTEM_PROMPT_FILE,
                settings.CONTEXT_FILE
            )

            # All panes should be empty
            assert manager.user_prompt.read() == ""
            assert manager.system_prompt.read() == ""
            assert manager.context.read() == ""

    def test_update_existing_content(self, tmp_path):
        """Test updating existing content."""
        with patch.object(Path, 'home', return_value=tmp_path):
            settings = Settings()
            settings.DATA_DIR = tmp_path / "data"
            settings.USER_PROMPT_FILE = settings.DATA_DIR / "user_prompt.txt"
            settings.SYSTEM_PROMPT_FILE = settings.DATA_DIR / "system_prompt.txt"
            settings.CONTEXT_FILE = settings.DATA_DIR / "context.txt"

            settings.ensure_files()

            # Create manager and write initial content
            manager = PaneManager(
                settings.USER_PROMPT_FILE,
                settings.SYSTEM_PROMPT_FILE,
                settings.CONTEXT_FILE
            )
            manager.user_prompt.write("Initial content")

            # Update content
            manager.user_prompt.write("Updated content")

            # Verify update
            assert manager.user_prompt.read() == "Updated content"

            # Create new manager to verify persistence
            manager2 = PaneManager(
                settings.USER_PROMPT_FILE,
                settings.SYSTEM_PROMPT_FILE,
                settings.CONTEXT_FILE
            )
            assert manager2.user_prompt.read() == "Updated content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
