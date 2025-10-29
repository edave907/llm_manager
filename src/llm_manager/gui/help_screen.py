"""Help screen for LLM Manager."""

from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical, VerticalScroll
from textual.widgets import Static, Label
from rich.text import Text


class HelpScreen(ModalScreen):
    """Modal screen displaying help information and keybindings."""

    DEFAULT_CSS = """
    HelpScreen {
        align: center middle;
    }

    #help-dialog {
        width: 80;
        height: auto;
        max-height: 90%;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }

    #help-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    #help-content {
        height: auto;
        max-height: 30;
        padding: 1 2;
    }

    .help-section {
        margin-bottom: 1;
    }

    .help-section-title {
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .help-item {
        margin-left: 2;
    }

    #help-footer {
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 1;
        margin-top: 1;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("?", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def compose(self) -> ComposeResult:
        """Compose the help screen."""
        with Container(id="help-dialog"):
            yield Label("LLM Manager - Help", id="help-title")

            with VerticalScroll(id="help-content"):
                # Navigation section
                yield Static(self._create_section(
                    "Navigation",
                    [
                        ("Tab", "Focus next pane"),
                        ("Shift+Tab", "Focus previous pane"),
                    ]
                ), classes="help-section")

                # Editing section
                yield Static(self._create_section(
                    "Editing",
                    [
                        ("i", "Enter edit mode in prompt panes"),
                        ("ESC", "Exit edit mode to command mode"),
                        ("c", "Clear pane content (command mode only)"),
                        ("Ctrl+S", "Save current pane to disk"),
                        ("e", "Open current pane in external editor (nvim)"),
                        ("Ctrl+A", "Select all text"),
                        ("Ctrl+C/V", "Copy/Paste"),
                        ("Ctrl+Z/Y", "Undo/Redo"),
                    ]
                ), classes="help-section")

                # LLM Operations section
                yield Static(self._create_section(
                    "LLM Operations",
                    [
                        ("Ctrl+J", "Send prompts to LLM"),
                        ("↑/↓", "Navigate LLM models (when in LLM pane)"),
                        ("Enter", "Select LLM model (when in LLM pane)"),
                    ]
                ), classes="help-section")

                # Response section
                yield Static(self._create_section(
                    "Response",
                    [
                        ("s", "Toggle streaming mode on/off"),
                        ("c", "Clear response pane"),
                    ]
                ), classes="help-section")

                # Pane Management section
                yield Static(self._create_section(
                    "Pane Management",
                    [
                        ("m", "Toggle maximize/restore focused pane"),
                        ("n", "Toggle minimize/restore focused pane"),
                        ("Ctrl+↑", "Increase pane size (Min→Norm→2x→3x→Max)"),
                        ("Ctrl+↓", "Decrease pane size (Max→3x→2x→Norm→Min)"),
                    ]
                ), classes="help-section")

                # Conversation section
                yield Static(self._create_section(
                    "Conversation History",
                    [
                        ("Ctrl+E", "Export conversation to JSON file"),
                        ("Ctrl+I", "Import conversation (feature in development)"),
                    ]
                ), classes="help-section")

                # General section
                yield Static(self._create_section(
                    "General",
                    [
                        ("ESC", "Open pane management menu"),
                        ("?", "Show/hide this help screen"),
                        ("q", "Quit application"),
                    ]
                ), classes="help-section")

            yield Label("Press ESC, ?, or Q to close this help", id="help-footer")

    def _create_section(self, title: str, items: list[tuple[str, str]]) -> Text:
        """Create a help section with title and items.

        Args:
            title: Section title
            items: List of (keybinding, description) tuples

        Returns:
            Rich Text object with formatted section
        """
        text = Text()
        text.append(f"{title}\n", style="bold cyan")

        for key, description in items:
            text.append(f"  {key:15}", style="yellow")
            text.append(f" - {description}\n")

        return text

    def action_dismiss(self) -> None:
        """Dismiss the help screen."""
        self.dismiss()
