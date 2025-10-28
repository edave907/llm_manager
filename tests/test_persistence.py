"""Unit tests for persistence layer."""

import tempfile
from pathlib import Path
import pytest

from llm_manager.core.persistence import PaneStorage, PaneManager


class TestPaneStorage:
    """Test PaneStorage class."""

    def test_create_and_read(self, tmp_path):
        """Test creating and reading from storage."""
        test_file = tmp_path / "test.txt"
        storage = PaneStorage(test_file)

        # File should be created
        assert test_file.exists()

        # Should read empty content initially
        content = storage.read()
        assert content == ""

    def test_write_and_read(self, tmp_path):
        """Test writing and reading content."""
        test_file = tmp_path / "test.txt"
        storage = PaneStorage(test_file)

        # Write content
        test_content = "Hello, World!"
        result = storage.write(test_content)
        assert result is True

        # Read content back
        content = storage.read()
        assert content == test_content

    def test_write_multiline(self, tmp_path):
        """Test writing multiline content."""
        test_file = tmp_path / "test.txt"
        storage = PaneStorage(test_file)

        # Write multiline content
        test_content = """Line 1
Line 2
Line 3
with some special characters: !@#$%^&*()"""
        storage.write(test_content)

        # Read back
        content = storage.read()
        assert content == test_content

    def test_clear(self, tmp_path):
        """Test clearing content."""
        test_file = tmp_path / "test.txt"
        storage = PaneStorage(test_file)

        # Write and clear
        storage.write("Some content")
        result = storage.clear()
        assert result is True

        # Should be empty
        content = storage.read()
        assert content == ""

    def test_unicode_content(self, tmp_path):
        """Test handling unicode content."""
        test_file = tmp_path / "test.txt"
        storage = PaneStorage(test_file)

        # Write unicode content
        test_content = "Hello 世界! 🚀 Émoji test"
        storage.write(test_content)

        # Read back
        content = storage.read()
        assert content == test_content


class TestPaneManager:
    """Test PaneManager class."""

    def test_create_pane_manager(self, tmp_path):
        """Test creating a pane manager."""
        user_file = tmp_path / "user.txt"
        system_file = tmp_path / "system.txt"
        context_file = tmp_path / "context.txt"

        manager = PaneManager(user_file, system_file, context_file)

        # All panes should be accessible
        assert manager.user_prompt is not None
        assert manager.system_prompt is not None
        assert manager.context is not None

    def test_get_pane_by_name(self, tmp_path):
        """Test getting panes by name."""
        user_file = tmp_path / "user.txt"
        system_file = tmp_path / "system.txt"
        context_file = tmp_path / "context.txt"

        manager = PaneManager(user_file, system_file, context_file)

        # Get panes by name
        assert manager.get_pane("user_prompt") is manager.user_prompt
        assert manager.get_pane("system_prompt") is manager.system_prompt
        assert manager.get_pane("context") is manager.context
        assert manager.get_pane("invalid") is None

    def test_pane_independence(self, tmp_path):
        """Test that panes are independent."""
        user_file = tmp_path / "user.txt"
        system_file = tmp_path / "system.txt"
        context_file = tmp_path / "context.txt"

        manager = PaneManager(user_file, system_file, context_file)

        # Write different content to each pane
        manager.user_prompt.write("User content")
        manager.system_prompt.write("System content")
        manager.context.write("Context content")

        # Verify independence
        assert manager.user_prompt.read() == "User content"
        assert manager.system_prompt.read() == "System content"
        assert manager.context.read() == "Context content"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
