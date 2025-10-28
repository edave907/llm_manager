"""Menu system for LLM Manager."""

from textual.app import ComposeResult
from textual.binding import Binding
from textual.containers import Container, Vertical
from textual.screen import ModalScreen
from textual.widgets import Static, OptionList, Label
from textual.widgets.option_list import Option
from rich.text import Text


class PaneMenuScreen(ModalScreen):
    """Modal screen for pane management menu."""

    DEFAULT_CSS = """
    PaneMenuScreen {
        align: center middle;
    }

    #menu-dialog {
        width: 60;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }

    #menu-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    #menu-options {
        height: auto;
        max-height: 20;
        border: solid $surface;
        margin: 1 0;
    }

    #menu-status {
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 1;
        margin-top: 1;
    }

    .menu-section-header {
        text-style: bold;
        color: $accent;
    }
    """

    BINDINGS = [
        ("escape", "dismiss", "Close"),
        ("q", "dismiss", "Close"),
    ]

    def __init__(self, app_ref, name=None, id=None, classes=None):
        """Initialize the menu screen.

        Args:
            app_ref: Reference to the main application
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.app_ref = app_ref

    def compose(self) -> ComposeResult:
        """Compose the menu screen."""
        with Container(id="menu-dialog"):
            yield Label("Pane Management Menu", id="menu-title")

            # Build menu options
            options = []

            # List all panes section
            options.append(Option(Text("═══ All Panes ═══", style="bold cyan"), disabled=True))

            for pane, name in self.app_ref._get_pane_list():
                pane_id = pane.id if hasattr(pane, 'id') else str(id(pane))
                is_hidden = pane.styles.display == "none"

                # Show status indicator
                if is_hidden:
                    status = "🔒 Hidden"
                    style = "dim"
                elif self.app_ref.maximized_pane == pane:
                    status = "📌 Maximized"
                    style = "bold green"
                elif self.app_ref.pane_states.get(pane) == self.app_ref.PaneState.MINIMIZED:
                    status = "📉 Minimized"
                    style = "yellow"
                else:
                    status = "👁 Visible"
                    style = "white"

                label = Text(f"{name:20} {status}", style=style)
                options.append(Option(label, id=f"pane_{pane_id}"))

            # Separator
            options.append(Option(Text("─────────────────────", style="dim"), disabled=True))

            # Actions section
            options.append(Option(Text("═══ Actions ═══", style="bold magenta"), disabled=True))
            options.append(Option("📋 Select/Focus Pane", id="action_select"))
            options.append(Option("🔒 Hide Selected Pane", id="action_hide"))
            options.append(Option("👁 Unhide Selected Pane", id="action_unhide"))
            options.append(Option("🔄 Show All Panes", id="action_show_all"))

            yield OptionList(*options, id="menu-options")
            yield Label("↑/↓ Navigate | Enter Select | ESC/Q Close", id="menu-status")

    def on_option_list_option_selected(self, event):
        """Handle menu option selection."""
        option_id = event.option.id

        if not option_id:
            return

        if option_id.startswith("pane_"):
            # Extract pane ID and find the pane
            pane = self._find_pane_by_id(option_id)
            if pane:
                self._handle_pane_selection(pane)
        elif option_id == "action_select":
            self.dismiss()
        elif option_id == "action_hide":
            self._hide_highlighted_pane()
        elif option_id == "action_unhide":
            self._unhide_highlighted_pane()
        elif option_id == "action_show_all":
            self._show_all_panes()

    def _find_pane_by_id(self, option_id):
        """Find pane by option ID."""
        for pane, _ in self.app_ref._get_pane_list():
            pane_id = pane.id if hasattr(pane, 'id') else str(id(pane))
            if f"pane_{pane_id}" == option_id:
                return pane
        return None

    def _handle_pane_selection(self, pane):
        """Handle pane selection from menu."""
        # Toggle hide/unhide for the selected pane
        is_hidden = pane.styles.display == "none"

        if is_hidden:
            # Unhide
            pane.styles.display = "block"
            self.app_ref.notify(f"Unhidden: {self.app_ref._get_pane_name(pane)}", severity="information")
        else:
            # Focus the pane
            pane.focus()
            self.dismiss()

    def _hide_highlighted_pane(self):
        """Hide the currently highlighted pane in the list."""
        option_list = self.query_one("#menu-options", OptionList)
        highlighted_option = option_list.get_option_at_index(option_list.highlighted)

        if highlighted_option and highlighted_option.id and highlighted_option.id.startswith("pane_"):
            pane = self._find_pane_by_id(highlighted_option.id)
            if pane and pane.styles.display != "none":
                pane.styles.display = "none"
                # Refresh the menu
                self.dismiss()
                self.app_ref.action_show_pane_menu()
            elif pane and pane.styles.display == "none":
                self.app_ref.notify("Pane is already hidden", severity="warning")

    def _unhide_highlighted_pane(self):
        """Unhide the currently highlighted pane in the list."""
        option_list = self.query_one("#menu-options", OptionList)
        highlighted_option = option_list.get_option_at_index(option_list.highlighted)

        if highlighted_option and highlighted_option.id and highlighted_option.id.startswith("pane_"):
            pane = self._find_pane_by_id(highlighted_option.id)
            if pane and pane.styles.display == "none":
                pane.styles.display = "block"
                # Refresh the menu
                self.dismiss()
                self.app_ref.action_show_pane_menu()
            elif pane and pane.styles.display != "none":
                self.app_ref.notify("Pane is already visible", severity="warning")

    def _show_all_panes(self):
        """Show all hidden panes."""
        for pane, _ in self.app_ref._get_pane_list():
            pane.styles.display = "block"
        self.dismiss()

    def action_dismiss(self):
        """Dismiss the menu screen."""
        self.dismiss()
