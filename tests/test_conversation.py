"""Tests for conversation history functionality."""

import json
import tempfile
from pathlib import Path
from datetime import datetime
import pytest

from llm_manager.core.conversation import ConversationHistory, ConversationTurn


class TestConversationTurn:
    """Test ConversationTurn dataclass."""

    def test_create_turn(self):
        """Test creating a conversation turn."""
        turn = ConversationTurn(
            timestamp="2024-01-01T12:00:00",
            model="openai:gpt-4o",
            user_prompt="Hello",
            system_prompt="You are helpful",
            context="Some context",
            response="Hi there!"
        )

        assert turn.timestamp == "2024-01-01T12:00:00"
        assert turn.model == "openai:gpt-4o"
        assert turn.user_prompt == "Hello"
        assert turn.response == "Hi there!"

    def test_to_dict(self):
        """Test converting turn to dictionary."""
        turn = ConversationTurn(
            timestamp="2024-01-01T12:00:00",
            model="openai:gpt-4o",
            user_prompt="Hello",
            system_prompt="",
            context="",
            response="Hi!"
        )

        turn_dict = turn.to_dict()
        assert isinstance(turn_dict, dict)
        assert turn_dict["model"] == "openai:gpt-4o"
        assert turn_dict["user_prompt"] == "Hello"

    def test_from_dict(self):
        """Test creating turn from dictionary."""
        data = {
            "timestamp": "2024-01-01T12:00:00",
            "model": "openai:gpt-4o",
            "user_prompt": "Hello",
            "system_prompt": "",
            "context": "",
            "response": "Hi!"
        }

        turn = ConversationTurn.from_dict(data)
        assert turn.model == "openai:gpt-4o"
        assert turn.user_prompt == "Hello"


class TestConversationHistory:
    """Test ConversationHistory class."""

    def test_initialize_with_temp_file(self):
        """Test initializing history with a temporary file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            assert history.history_file == history_file
            assert history.turns == []

    def test_add_turn(self):
        """Test adding a conversation turn."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            history.add_turn(
                model="openai:gpt-4o",
                user_prompt="Test prompt",
                response="Test response",
                system_prompt="System",
                context="Context"
            )

            assert len(history.turns) == 1
            assert history.turns[0].model == "openai:gpt-4o"
            assert history.turns[0].user_prompt == "Test prompt"
            assert history.turns[0].response == "Test response"

    def test_add_turn_persists(self):
        """Test that added turns are persisted to file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            history.add_turn(
                model="openai:gpt-4o",
                user_prompt="Test",
                response="Response"
            )

            # Verify file was created
            assert history_file.exists()

            # Load and verify contents
            with open(history_file, "r") as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["model"] == "openai:gpt-4o"

    def test_get_recent_turns(self):
        """Test getting recent conversation turns."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            # Add multiple turns
            for i in range(5):
                history.add_turn(
                    model="openai:gpt-4o",
                    user_prompt=f"Prompt {i}",
                    response=f"Response {i}"
                )

            recent = history.get_recent_turns(count=3)
            assert len(recent) == 3
            assert recent[0].user_prompt == "Prompt 2"
            assert recent[2].user_prompt == "Prompt 4"

    def test_clear_history(self):
        """Test clearing conversation history."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            history.add_turn(
                model="openai:gpt-4o",
                user_prompt="Test",
                response="Response"
            )

            assert len(history.turns) == 1

            history.clear_history()
            assert len(history.turns) == 0

    def test_export_json(self):
        """Test exporting history to JSON."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            export_file = Path(tmpdir) / "export.json"
            history = ConversationHistory(history_file=history_file)

            history.add_turn(
                model="openai:gpt-4o",
                user_prompt="Test",
                response="Response"
            )

            success = history.export_to_file(export_file, format="json")
            assert success
            assert export_file.exists()

            # Verify exported contents
            with open(export_file, "r") as f:
                data = json.load(f)

            assert len(data) == 1
            assert data[0]["user_prompt"] == "Test"

    def test_export_text(self):
        """Test exporting history to text."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            export_file = Path(tmpdir) / "export.txt"
            history = ConversationHistory(history_file=history_file)

            history.add_turn(
                model="openai:gpt-4o",
                user_prompt="Test prompt",
                response="Test response",
                system_prompt="System prompt",
                context="Context"
            )

            success = history.export_to_file(export_file, format="txt")
            assert success
            assert export_file.exists()

            # Verify text contents
            content = export_file.read_text()
            assert "Test prompt" in content
            assert "Test response" in content
            assert "System prompt" in content
            assert "Context" in content

    def test_import_from_file(self):
        """Test importing history from JSON file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create export file
            export_file = Path(tmpdir) / "export.json"
            export_data = [
                {
                    "timestamp": "2024-01-01T12:00:00",
                    "model": "openai:gpt-4o",
                    "user_prompt": "Imported prompt",
                    "system_prompt": "",
                    "context": "",
                    "response": "Imported response"
                }
            ]

            with open(export_file, "w") as f:
                json.dump(export_data, f)

            # Import into new history
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            success = history.import_from_file(export_file)
            assert success
            assert len(history.turns) == 1
            assert history.turns[0].user_prompt == "Imported prompt"

    def test_max_history_items(self):
        """Test that history respects max items limit."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"
            history = ConversationHistory(history_file=history_file)

            # Mock the max history items
            from llm_manager.core import settings
            original_max = settings.settings.MAX_HISTORY_ITEMS
            settings.settings.MAX_HISTORY_ITEMS = 5

            try:
                # Add more turns than the limit
                for i in range(10):
                    history.add_turn(
                        model="openai:gpt-4o",
                        user_prompt=f"Prompt {i}",
                        response=f"Response {i}"
                    )

                # Should only keep last 5
                assert len(history.turns) <= 5
                assert history.turns[0].user_prompt == "Prompt 5"
                assert history.turns[-1].user_prompt == "Prompt 9"
            finally:
                settings.settings.MAX_HISTORY_ITEMS = original_max

    def test_load_existing_history(self):
        """Test loading existing history from file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            history_file = Path(tmpdir) / "history.json"

            # Create existing history
            existing_data = [
                {
                    "timestamp": "2024-01-01T12:00:00",
                    "model": "openai:gpt-4o",
                    "user_prompt": "Existing",
                    "system_prompt": "",
                    "context": "",
                    "response": "Response"
                }
            ]

            with open(history_file, "w") as f:
                json.dump(existing_data, f)

            # Load history
            history = ConversationHistory(history_file=history_file)

            assert len(history.turns) == 1
            assert history.turns[0].user_prompt == "Existing"
