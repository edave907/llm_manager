"""Persistence layer for pane contents."""

from pathlib import Path
from typing import Optional


class PaneStorage:
    """Handles reading and writing pane content to persistent storage."""

    def __init__(self, file_path: Path):
        """Initialize pane storage with a file path.

        Args:
            file_path: Path to the file where pane content will be stored
        """
        self.file_path = file_path
        self._ensure_exists()

    def _ensure_exists(self) -> None:
        """Ensure the storage file exists."""
        if not self.file_path.exists():
            self.file_path.parent.mkdir(parents=True, exist_ok=True)
            self.file_path.write_text("", encoding="utf-8")

    def read(self) -> str:
        """Read content from storage.

        Returns:
            The stored content as a string
        """
        try:
            return self.file_path.read_text(encoding="utf-8")
        except Exception as e:
            # If read fails, return empty string and log error
            print(f"Error reading from {self.file_path}: {e}")
            return ""

    def write(self, content: str) -> bool:
        """Write content to storage.

        Args:
            content: The content to write

        Returns:
            True if successful, False otherwise
        """
        try:
            self.file_path.write_text(content, encoding="utf-8")
            return True
        except Exception as e:
            print(f"Error writing to {self.file_path}: {e}")
            return False

    def clear(self) -> bool:
        """Clear the stored content.

        Returns:
            True if successful, False otherwise
        """
        return self.write("")


class PaneManager:
    """Manages storage for all panes in the application."""

    def __init__(self, user_prompt_path: Path, system_prompt_path: Path, context_path: Path):
        """Initialize the pane manager.

        Args:
            user_prompt_path: Path to user prompt storage file
            system_prompt_path: Path to system prompt storage file
            context_path: Path to context storage file
        """
        self.user_prompt = PaneStorage(user_prompt_path)
        self.system_prompt = PaneStorage(system_prompt_path)
        self.context = PaneStorage(context_path)

    def get_pane(self, pane_name: str) -> Optional[PaneStorage]:
        """Get a pane storage by name.

        Args:
            pane_name: Name of the pane ('user_prompt', 'system_prompt', or 'context')

        Returns:
            The PaneStorage instance, or None if not found
        """
        panes = {
            "user_prompt": self.user_prompt,
            "system_prompt": self.system_prompt,
            "context": self.context,
        }
        return panes.get(pane_name)
