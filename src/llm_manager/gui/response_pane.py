"""Response pane widget for displaying LLM responses."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Static, Label
from textual.reactive import reactive
from rich.text import Text

from ..core.settings import settings


class ResponsePane(Container, can_focus=True):
    """Pane for displaying LLM responses."""

    DEFAULT_CSS = """
    ResponsePane {
        border: solid $primary;
        height: 1fr;
        margin: 1;
    }

    ResponsePane:focus {
        border: heavy $accent;
    }

    ResponsePane.pane-focused {
        border: heavy $accent;
    }

    ResponsePane .pane-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 0 1;
    }

    ResponsePane:focus .pane-title {
        background: $accent;
        color: $text;
    }

    ResponsePane.pane-focused .pane-title {
        background: $accent;
        color: $text;
    }

    ResponsePane .response-content {
        padding: 1 2;
        height: 1fr;
        overflow-y: auto;
    }

    ResponsePane .pane-footer {
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 0 1;
    }

    ResponsePane .status-bar {
        background: $accent;
        color: $text;
        padding: 0 2;
        height: 1;
    }
    """

    response_text = reactive("")
    status = reactive("Ready")
    streaming_enabled = reactive(True)

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialize the response pane.

        Args:
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.streaming_enabled = settings.ENABLE_STREAMING

    def compose(self) -> ComposeResult:
        """Compose the pane widget."""
        title_text = "Response"
        if self.streaming_enabled:
            title_text += " (Streaming ON)"
        else:
            title_text += " (Streaming OFF)"

        yield Label(title_text, classes="pane-title", id="response-title")
        yield Static(self.status, classes="status-bar", id="status-bar")

        with ScrollableContainer(classes="response-content"):
            yield Static("", id="response-display")

        footer_text = "Press 's' to toggle streaming | 'c' to clear"
        yield Label(footer_text, classes="pane-footer")

    def on_focus(self) -> None:
        """Handle focus event."""
        self.add_class("pane-focused")

    def on_blur(self) -> None:
        """Handle blur event."""
        self.remove_class("pane-focused")

    def set_status(self, status: str) -> None:
        """Update the status bar.

        Args:
            status: Status message to display
        """
        self.status = status
        status_bar = self.query_one("#status-bar", Static)
        status_bar.update(status)

    def clear_response(self) -> None:
        """Clear the response display."""
        self.response_text = ""
        response_display = self.query_one("#response-display", Static)
        response_display.update("")
        self.set_status("Cleared")

    def set_response(self, text: str) -> None:
        """Set the complete response text.

        Args:
            text: The response text to display
        """
        self.response_text = text
        response_display = self.query_one("#response-display", Static)
        response_display.update(Text(text))

    def append_response_chunk(self, chunk: str) -> None:
        """Append a chunk of streaming response.

        Args:
            chunk: Text chunk to append
        """
        self.response_text += chunk
        response_display = self.query_one("#response-display", Static)
        response_display.update(Text(self.response_text))

        # Auto-scroll to bottom
        container = self.query_one(ScrollableContainer)
        container.scroll_end(animate=False)

    def toggle_streaming(self) -> None:
        """Toggle streaming mode."""
        self.streaming_enabled = not self.streaming_enabled
        settings.ENABLE_STREAMING = self.streaming_enabled

        # Update title
        title = self.query_one("#response-title", Label)
        if self.streaming_enabled:
            title.update("Response (Streaming ON)")
        else:
            title.update("Response (Streaming OFF)")

        mode = "ON" if self.streaming_enabled else "OFF"
        self.app.notify(f"Streaming: {mode}", severity="information")

    def show_error(self, error: str) -> None:
        """Display an error message.

        Args:
            error: Error message to display
        """
        self.response_text = ""
        response_display = self.query_one("#response-display", Static)
        error_text = Text(f"Error: {error}", style="bold red")
        response_display.update(error_text)
        self.set_status("Error")

    def get_response_text(self) -> str:
        """Get the current response text.

        Returns:
            The current response text
        """
        return self.response_text
