"""Conversation history management."""

import json
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from .settings import settings


@dataclass
class ConversationTurn:
    """A single turn in a conversation."""

    timestamp: str
    model: str
    user_prompt: str
    system_prompt: str
    context: str
    response: str

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "ConversationTurn":
        """Create from dictionary."""
        return cls(**data)


class ConversationHistory:
    """Manages conversation history."""

    def __init__(self, history_file: Optional[Path] = None):
        """Initialize conversation history.

        Args:
            history_file: Path to history file (uses default if not specified)
        """
        self.history_file = history_file or settings.CONVERSATION_HISTORY_FILE
        self.turns: List[ConversationTurn] = []
        self._load_history()

    def add_turn(
        self,
        model: str,
        user_prompt: str,
        response: str,
        system_prompt: str = "",
        context: str = "",
    ) -> None:
        """Add a conversation turn to history.

        Args:
            model: The model used
            user_prompt: The user's prompt
            response: The model's response
            system_prompt: Optional system prompt
            context: Optional context
        """
        turn = ConversationTurn(
            timestamp=datetime.now().isoformat(),
            model=model,
            user_prompt=user_prompt,
            system_prompt=system_prompt,
            context=context,
            response=response,
        )
        self.turns.append(turn)

        # Trim to max items
        if len(self.turns) > settings.MAX_HISTORY_ITEMS:
            self.turns = self.turns[-settings.MAX_HISTORY_ITEMS:]

        self._save_history()

    def get_recent_turns(self, count: int = 10) -> List[ConversationTurn]:
        """Get the most recent conversation turns.

        Args:
            count: Number of recent turns to get

        Returns:
            List of recent conversation turns
        """
        return self.turns[-count:]

    def clear_history(self) -> None:
        """Clear all conversation history."""
        self.turns = []
        self._save_history()

    def export_to_file(self, filepath: Path, format: str = "json") -> bool:
        """Export conversation history to a file.

        Args:
            filepath: Path to export file
            format: Export format ("json" or "txt")

        Returns:
            True if successful, False otherwise
        """
        try:
            if format == "json":
                self._export_json(filepath)
            elif format == "txt":
                self._export_text(filepath)
            else:
                return False
            return True
        except Exception as e:
            print(f"Error exporting history: {e}")
            return False

    def import_from_file(self, filepath: Path) -> bool:
        """Import conversation history from a JSON file.

        Args:
            filepath: Path to import file

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)

            imported_turns = [ConversationTurn.from_dict(turn) for turn in data]
            self.turns.extend(imported_turns)

            # Trim to max items
            if len(self.turns) > settings.MAX_HISTORY_ITEMS:
                self.turns = self.turns[-settings.MAX_HISTORY_ITEMS:]

            self._save_history()
            return True
        except Exception as e:
            print(f"Error importing history: {e}")
            return False

    def _load_history(self) -> None:
        """Load history from file."""
        if not self.history_file.exists():
            return

        try:
            with open(self.history_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            self.turns = [ConversationTurn.from_dict(turn) for turn in data]
        except Exception as e:
            print(f"Error loading history: {e}")
            self.turns = []

    def _save_history(self) -> None:
        """Save history to file."""
        try:
            self.history_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.history_file, "w", encoding="utf-8") as f:
                data = [turn.to_dict() for turn in self.turns]
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving history: {e}")

    def _export_json(self, filepath: Path) -> None:
        """Export as JSON."""
        with open(filepath, "w", encoding="utf-8") as f:
            data = [turn.to_dict() for turn in self.turns]
            json.dump(data, f, indent=2, ensure_ascii=False)

    def _export_text(self, filepath: Path) -> None:
        """Export as plain text."""
        with open(filepath, "w", encoding="utf-8") as f:
            for i, turn in enumerate(self.turns, 1):
                f.write(f"=" * 80 + "\n")
                f.write(f"Conversation {i}\n")
                f.write(f"Timestamp: {turn.timestamp}\n")
                f.write(f"Model: {turn.model}\n")
                f.write(f"=" * 80 + "\n\n")

                if turn.system_prompt:
                    f.write(f"System Prompt:\n{turn.system_prompt}\n\n")

                if turn.context:
                    f.write(f"Context:\n{turn.context}\n\n")

                f.write(f"User:\n{turn.user_prompt}\n\n")
                f.write(f"Assistant:\n{turn.response}\n\n")
