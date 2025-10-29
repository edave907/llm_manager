"""Confirmation dialog for LLM Manager."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Horizontal
from textual.widgets import Label, Button


class ConfirmationScreen(ModalScreen[bool]):
    """Modal screen for Y/N confirmation."""

    DEFAULT_CSS = """
    ConfirmationScreen {
        align: center middle;
    }

    #confirm-dialog {
        width: 60;
        height: auto;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }

    #confirm-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    #confirm-message {
        padding: 1 2;
        margin-bottom: 1;
    }

    #confirm-buttons {
        height: auto;
        align: center middle;
        margin-top: 1;
    }

    #confirm-buttons Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("y", "confirm_yes", "Yes"),
        ("n", "confirm_no", "No"),
        ("escape", "confirm_no", "Cancel"),
    ]

    def __init__(self, message: str, title: str = "Confirm", name=None, id=None, classes=None):
        """Initialize the confirmation screen.

        Args:
            message: The confirmation message to display
            title: The dialog title
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.message = message
        self.title = title

    def compose(self) -> ComposeResult:
        """Compose the confirmation dialog."""
        with Container(id="confirm-dialog"):
            yield Label(self.title, id="confirm-title")
            yield Label(self.message, id="confirm-message")

            with Horizontal(id="confirm-buttons"):
                yield Button("Yes (Y)", variant="success", id="yes-button")
                yield Button("No (N)", variant="error", id="no-button")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "yes-button":
            self.dismiss(True)
        else:
            self.dismiss(False)

    def action_confirm_yes(self) -> None:
        """Confirm with Yes."""
        self.dismiss(True)

    def action_confirm_no(self) -> None:
        """Confirm with No."""
        self.dismiss(False)
