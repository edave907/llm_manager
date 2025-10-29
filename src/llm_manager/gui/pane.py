"""Pane widget for LLM Manager."""

import subprocess
import tempfile
from pathlib import Path
from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container
from textual.widget import Widget
from textual.widgets import Static, Label, TextArea
from textual.reactive import reactive
from textual import events
from rich.text import Text


class EditableTextArea(TextArea):
    """Custom TextArea that handles ESC key to exit edit mode."""

    def on_focus(self) -> None:
        """When TextArea gains focus (via mouse or otherwise), enter edit mode."""
        # Find parent EditablePane and ensure edit_mode is set
        parent = self.parent
        while parent is not None:
            if hasattr(parent, 'edit_mode') and hasattr(parent, 'enter_edit_mode'):
                if not parent.edit_mode:
                    # Set edit mode flag without calling focus again (avoid recursion)
                    parent.edit_mode = True
                    parent._update_footer()
                return
            parent = parent.parent
        # Call parent's on_focus
        super().on_focus()

    def _on_key(self, event: events.Key) -> None:
        """Handle key events, with ESC exiting edit mode."""
        if event.key == "escape":
            # Find parent with exit_edit_mode method and call it
            parent = self.parent
            while parent is not None:
                if hasattr(parent, 'exit_edit_mode') and hasattr(parent, 'edit_mode'):
                    # Always try to exit edit mode when ESC is pressed
                    parent.exit_edit_mode()
                    event.prevent_default()
                    event.stop()
                    return
                parent = parent.parent
            # If no parent found, just return
            return
        # For all other keys, call the parent TextArea's handler
        super()._on_key(event)


class EditablePane(Container, can_focus=True):
    """A pane that displays content and can be edited with nvim."""

    BINDINGS = [
        Binding("escape", "exit_edit_mode", "Exit Edit Mode", priority=True),
        Binding("c", "clear_content", "Clear", show=False),
    ]

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
        self.edit_mode = False  # Track edit vs command mode

    def compose(self) -> ComposeResult:
        """Compose the pane widget."""
        yield Label(self.title_text, classes="pane-title")
        text_area = EditableTextArea("", id=f"{self.id}-content", classes="pane-content")
        text_area.can_focus = True
        yield text_area
        yield Label(
            "i: Edit mode | e: nvim | c: clear | Ctrl+S: Save",
            classes="pane-footer",
            id=f"{self.id}-footer"
        )

    def on_mount(self) -> None:
        """Load content when pane is mounted."""
        self.load_content()
        # Start in command mode
        self.edit_mode = False
        self._update_footer()

    def on_focus(self) -> None:
        """Handle focus event."""
        self.add_class("pane-focused")
        # Ensure we stay in command mode when pane gets focus
        if not self.edit_mode:
            # Check if TextArea somehow got focus and unfocus it
            try:
                content_widget = self.query_one(f"#{self.id}-content", TextArea)
                if content_widget.has_focus:
                    # Call focus on self but use call_later to avoid recursion
                    self.app.call_later(lambda: self.focus() if not self.edit_mode else None)
            except Exception:
                pass

    def on_blur(self) -> None:
        """Handle blur event."""
        self.remove_class("pane-focused")
        # Don't automatically exit edit mode here - let user press ESC to exit
        # This avoids timing issues with focus changes

    def enter_edit_mode(self) -> None:
        """Enter edit mode - focus the TextArea for typing."""
        if not self.edit_mode:
            self.edit_mode = True
            try:
                content_widget = self.query_one(f"#{self.id}-content", TextArea)
                content_widget.focus()
                self._update_footer()
            except Exception:
                pass

    def exit_edit_mode(self) -> None:
        """Exit edit mode - return to command mode."""
        if self.edit_mode:
            self.edit_mode = False
            self.focus()
            self._update_footer()

    def _update_footer(self) -> None:
        """Update footer to show current mode."""
        try:
            footer = self.query_one(f"#{self.id}-footer", Label)
            if self.edit_mode:
                footer.update("-- EDIT MODE -- | ESC: Command mode | Ctrl+S: Save")
            else:
                footer.update("i: Edit mode | e: nvim | c: clear | Ctrl+S: Save")
        except Exception:
            pass

    def on_key(self, event) -> None:
        """Handle key events."""
        # In command mode, 'i' enters edit mode
        if not self.edit_mode and event.key == "i":
            self.enter_edit_mode()
            event.prevent_default()
            event.stop()
        # ESC in edit mode exits to command mode
        elif self.edit_mode and event.key == "escape":
            self.exit_edit_mode()
            event.prevent_default()
            event.stop()

    def action_exit_edit_mode(self) -> None:
        """Action to exit edit mode (bound to ESC key)."""
        if self.edit_mode:
            self.exit_edit_mode()

    def action_clear_content(self) -> None:
        """Action to clear pane content (bound to 'c' key)."""
        # Only allow clear in command mode
        if not self.edit_mode:
            self.clear_content()

    def clear_content(self) -> None:
        """Clear the content of the pane."""
        try:
            content_widget = self.query_one(f"#{self.id}-content", TextArea)
            content_widget.load_text("")
            self.save_content()
            self.app.notify(f"{self.title_text} cleared", severity="information")
        except Exception as e:
            self.app.notify(f"Error clearing content: {e}", severity="error")

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
