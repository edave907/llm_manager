"""Pane widget for LLM Manager."""

import subprocess
import tempfile
from pathlib import Path
from textual.app import ComposeResult
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static, Label, TextArea
from textual.reactive import reactive
from rich.text import Text


class EditablePane(Container, can_focus=True):
    """A pane that displays content and can be edited with nvim."""

    DEFAULT_CSS = """
    EditablePane {
        border: solid $primary;
        height: 1fr;
        margin: 1;
    }

    EditablePane:focus {
        border: heavy $accent;
    }

    EditablePane.pane-focused {
        border: heavy $accent;
    }

    EditablePane .pane-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 0 1;
    }

    EditablePane:focus .pane-title {
        background: $accent;
        color: $text;
    }

    EditablePane.pane-focused .pane-title {
        background: $accent;
        color: $text;
    }

    EditablePane .pane-content {
        height: 1fr;
    }

    EditablePane TextArea {
        height: 1fr;
        margin: 0 1;
    }

    EditablePane .pane-footer {
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 0 1;
    }
    """

    @property
    def content(self) -> str:
        """Get the current content from the TextArea."""
        try:
            content_widget = self.query_one(f"#{self.id}-content", TextArea)
            return content_widget.text
        except Exception:
            # If TextArea not yet mounted, return empty string
            return ""

    @content.setter
    def content(self, value: str) -> None:
        """Set the content in the TextArea."""
        try:
            content_widget = self.query_one(f"#{self.id}-content", TextArea)
            content_widget.load_text(value)
        except Exception:
            # If TextArea not yet mounted, ignore
            pass

    def __init__(
        self,
        title: str,
        storage_path: Path,
        editor: str = "nvim",
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialize the pane.

        Args:
            title: Display title for the pane
            storage_path: Path where pane content is persisted
            editor: Editor command to use (default: nvim)
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.title_text = title
        self.storage_path = storage_path
        self.editor = editor
        self.is_docked = True

    def compose(self) -> ComposeResult:
        """Compose the pane widget."""
        yield Label(self.title_text, classes="pane-title")
        yield TextArea("", id=f"{self.id}-content", classes="pane-content")
        yield Label(
            "Type to edit | 'e' for nvim | Ctrl+S to save",
            classes="pane-footer"
        )

    def on_mount(self) -> None:
        """Load content when pane is mounted."""
        self.load_content()

    def on_focus(self) -> None:
        """Handle focus event."""
        self.add_class("pane-focused")

    def on_blur(self) -> None:
        """Handle blur event."""
        self.remove_class("pane-focused")

    def load_content(self) -> None:
        """Load content from storage."""
        try:
            if self.storage_path.exists():
                content_text = self.storage_path.read_text(encoding="utf-8")
            else:
                content_text = ""

            content_widget = self.query_one(f"#{self.id}-content", TextArea)
            content_widget.load_text(content_text)
        except Exception as e:
            content_widget = self.query_one(f"#{self.id}-content", TextArea)
            content_widget.load_text(f"Error loading content: {e}")

    def save_content(self) -> bool:
        """Save content to storage.

        Returns:
            True if successful, False otherwise
        """
        try:
            content_widget = self.query_one(f"#{self.id}-content", TextArea)
            current_content = content_widget.text

            self.storage_path.parent.mkdir(parents=True, exist_ok=True)
            self.storage_path.write_text(current_content, encoding="utf-8")
            return True
        except Exception as e:
            self.app.notify(f"Error saving: {e}", severity="error")
            return False

    def edit_with_nvim(self) -> None:
        """Open content in nvim for editing."""
        # Get current content from TextArea
        content_widget = self.query_one(f"#{self.id}-content", TextArea)
        current_content = content_widget.text

        # Create a temporary file with current content
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".txt",
            delete=False,
            encoding="utf-8"
        ) as tmp_file:
            tmp_file.write(current_content)
            tmp_path = tmp_file.name

        try:
            # Suspend the Textual app
            with self.app.suspend():
                # Open nvim with the temporary file
                result = subprocess.run([self.editor, tmp_path])

                if result.returncode == 0:
                    # Read back the edited content
                    with open(tmp_path, "r", encoding="utf-8") as f:
                        new_content = f.read()

                    # Update content if changed
                    if new_content != current_content:
                        content_widget.load_text(new_content)
                        self.save_content()
                        self.app.notify(f"{self.title_text} updated", severity="information")
                else:
                    self.app.notify("Editor exited with error", severity="warning")
        except Exception as e:
            self.app.notify(f"Error opening editor: {e}", severity="error")
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)

    def toggle_dock(self) -> None:
        """Toggle the docked state of the pane."""
        self.is_docked = not self.is_docked
        # For now, just notify - actual docking/undocking will be implemented later
        state = "docked" if self.is_docked else "undocked"
        self.app.notify(f"{self.title_text} {state}", severity="information")
