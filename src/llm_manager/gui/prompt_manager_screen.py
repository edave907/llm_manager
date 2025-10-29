"""Prompt file manager screen for loading and saving prompts."""

from pathlib import Path
from textual.app import ComposeResult
from textual.screen import ModalScreen
from textual.containers import Container, Vertical
from textual.widgets import Label, OptionList, Input, Button
from textual.widgets.option_list import Option
from rich.text import Text

from ..core.settings import settings


class PromptManagerScreen(ModalScreen[dict]):
    """Modal screen for managing prompt files (load/save)."""

    DEFAULT_CSS = """
    PromptManagerScreen {
        align: center middle;
    }

    #prompt-manager-dialog {
        width: 70;
        height: auto;
        max-height: 80%;
        background: $surface;
        border: heavy $primary;
        padding: 1 2;
    }

    #prompt-manager-title,
    #list-title,
    #load-title,
    #save-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 1;
        margin-bottom: 1;
    }

    #prompt-manager-options,
    #list-options,
    #load-options {
        height: auto;
        max-height: 25;
        border: solid $surface;
        margin: 1 0;
    }

    #prompt-manager-status,
    #list-status,
    #load-status,
    #save-status {
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 1;
        margin-top: 1;
    }

    .input-container {
        height: auto;
        padding: 1;
        margin: 1 0;
    }

    .input-label {
        margin-bottom: 1;
    }

    Input {
        margin-bottom: 1;
    }

    #button-container,
    #save-button-container {
        height: auto;
        align: center middle;
    }

    #button-container Button,
    #save-button-container Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        ("escape", "dismiss_cancel", "Cancel"),
        ("q", "dismiss_cancel", "Cancel"),
    ]

    def __init__(self, pane_name: str, current_content: str, name=None, id=None, classes=None):
        """Initialize the prompt manager screen.

        Args:
            pane_name: Name of the pane (User Prompt, System Prompt, Context)
            current_content: Current content of the pane
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.pane_name = pane_name
        self.current_content = current_content
        self.mode = "menu"  # menu, load, save, load_mode_select
        self.prompts_dir = settings.PROMPTS_DIR
        self.selected_filename = None  # Store selected file for load mode selection

    def compose(self) -> ComposeResult:
        """Compose the prompt manager screen."""
        with Container(id="prompt-manager-dialog"):
            yield Label(f"{self.pane_name} - Prompt Manager", id="prompt-manager-title")
            yield from self._compose_menu()

    def _compose_menu(self) -> ComposeResult:
        """Compose the main menu."""
        options = []
        options.append(Option(Text("═══ Prompt Manager ═══", style="bold cyan"), disabled=True))
        options.append(Option("📂 List Prompts", id="action_list"))
        options.append(Option("📥 Load Prompt", id="action_load"))
        options.append(Option("💾 Save Prompt", id="action_save"))
        options.append(Option(Text("─────────────────────", style="dim"), disabled=True))
        options.append(Option("❌ Cancel", id="action_cancel"))

        yield OptionList(*options, id="prompt-manager-options")
        yield Label("↑/↓ Navigate | Enter Select | ESC/Q Cancel", id="prompt-manager-status")

    def on_option_list_option_selected(self, event) -> None:
        """Handle menu option selection."""
        option_id = event.option.id

        if not option_id:
            return

        if option_id == "action_list":
            self._show_prompt_list()
        elif option_id == "action_load":
            self._show_load_screen()
        elif option_id == "action_save":
            self._show_save_screen()
        elif option_id == "action_cancel":
            self.dismiss({"action": "cancel"})

    def _show_prompt_list(self) -> None:
        """Show list of available prompt files."""
        # Get all .txt files from prompts directory
        prompt_files = sorted(self.prompts_dir.glob("*.txt"))

        # Remove existing widgets properly
        container = self.query_one("#prompt-manager-dialog", Container)
        for child in list(container.children):
            child.remove()

        container.mount(Label(f"{self.pane_name} - Available Prompts", id="list-title"))

        options = []
        options.append(Option(Text("═══ Available Prompts ═══", style="bold cyan"), disabled=True))

        if prompt_files:
            for prompt_file in prompt_files:
                file_size = prompt_file.stat().st_size
                # Read first 15 characters for preview
                preview = ""
                try:
                    content = prompt_file.read_text(encoding="utf-8")
                    # Get first 15 chars, replace newlines/tabs with spaces
                    preview = content[:15].replace('\n', ' ').replace('\t', ' ').replace('\r', ' ')
                    if len(content) > 15:
                        preview += "..."
                except Exception:
                    preview = "[unreadable]"

                label = f"📄 {prompt_file.name:30} | {preview:18} ({file_size} bytes)"
                options.append(Option(label, id=f"file_{prompt_file.name}"))
        else:
            options.append(Option(Text("No prompts found", style="dim italic"), disabled=True))

        options.append(Option(Text("─────────────────────", style="dim"), disabled=True))
        options.append(Option("⬅ Back to Menu", id="action_back"))

        container.mount(OptionList(*options, id="list-options"))
        container.mount(Label("↑/↓ Navigate | Enter Select to Load | ESC Cancel", id="list-status"))

        self.mode = "list"

        # Focus the option list for keyboard navigation
        self.query_one("#list-options", OptionList).focus()

    def _show_load_screen(self) -> None:
        """Show screen for loading a prompt."""
        # Get all .txt files from prompts directory
        prompt_files = sorted(self.prompts_dir.glob("*.txt"))

        # Remove existing widgets properly
        container = self.query_one("#prompt-manager-dialog", Container)
        for child in list(container.children):
            child.remove()

        container.mount(Label(f"{self.pane_name} - Load Prompt", id="load-title"))

        options = []
        options.append(Option(Text("═══ Select Prompt to Load ═══", style="bold cyan"), disabled=True))

        if prompt_files:
            for prompt_file in prompt_files:
                file_size = prompt_file.stat().st_size
                label = f"📥 {prompt_file.name:40} ({file_size} bytes)"
                options.append(Option(label, id=f"load_{prompt_file.name}"))
        else:
            options.append(Option(Text("No prompts found", style="dim italic"), disabled=True))

        options.append(Option(Text("─────────────────────", style="dim"), disabled=True))
        options.append(Option("⬅ Back to Menu", id="action_back"))

        container.mount(OptionList(*options, id="load-options"))
        container.mount(Label("↑/↓ Navigate | Enter Load | ESC Cancel", id="load-status"))

        self.mode = "load"

        # Focus the option list for keyboard navigation
        self.query_one("#load-options", OptionList).focus()

    def _show_save_screen(self) -> None:
        """Show screen for saving a prompt."""
        # Remove existing widgets properly
        container = self.query_one("#prompt-manager-dialog", Container)
        for child in list(container.children):
            child.remove()

        container.mount(Label(f"{self.pane_name} - Save Prompt", id="save-title"))

        # Create and mount input container first
        input_container = Vertical(classes="input-container")
        container.mount(input_container)

        # Now mount children to the input container
        input_container.mount(Label("Enter filename (without .txt extension):", classes="input-label"))
        input_container.mount(Input(placeholder="my_prompt", id="save-filename-input"))

        # Create and mount button container
        button_container = Container(id="save-button-container")
        input_container.mount(button_container)

        # Now mount buttons to the button container
        button_container.mount(Button("💾 Save", variant="success", id="save-button"))
        button_container.mount(Button("❌ Cancel", variant="error", id="save-cancel-button"))

        container.mount(Label("Enter filename and click Save | ESC Cancel", id="save-status"))

        self.mode = "save"
        # Focus the input
        self.query_one("#save-filename-input", Input).focus()

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Handle button press."""
        if event.button.id == "save-button":
            self._save_prompt()
        elif event.button.id == "save-cancel-button":
            self.dismiss({"action": "cancel"})

    def _save_prompt(self) -> None:
        """Save the current prompt to a file."""
        filename_input = self.query_one("#save-filename-input", Input)
        filename = filename_input.value.strip()

        if not filename:
            # Show error - need filename
            return

        # Add .txt extension if not present
        if not filename.endswith(".txt"):
            filename = f"{filename}.txt"

        # Save to prompts directory
        file_path = self.prompts_dir / filename

        # Return the save action
        self.dismiss({
            "action": "save",
            "filename": filename,
            "path": str(file_path)
        })

    def _load_prompt(self, filename: str) -> None:
        """Show insertion mode selection for loading a prompt."""
        file_path = self.prompts_dir / filename

        if not file_path.exists():
            return

        # Store the selected filename and show insertion mode selection
        self.selected_filename = filename
        self._show_load_mode_selection(filename)

    def _show_load_mode_selection(self, filename: str) -> None:
        """Show insertion mode options for loading a prompt."""
        # Remove existing widgets
        container = self.query_one("#prompt-manager-dialog", Container)
        for child in list(container.children):
            child.remove()

        container.mount(Label(f"{self.pane_name} - Load: {filename}", id="load-mode-title"))

        options = []
        options.append(Option(Text("═══ Choose Insertion Mode ═══", style="bold cyan"), disabled=True))
        options.append(Option("🔄 [R] Replace current contents", id="mode_replace"))
        options.append(Option("➕ [A] Append to current contents", id="mode_append"))
        options.append(Option("📌 [I] Insert at cursor position", id="mode_insert"))
        options.append(Option(Text("─────────────────────", style="dim"), disabled=True))
        options.append(Option("⬅ Back", id="action_back"))

        container.mount(OptionList(*options, id="load-mode-options"))
        container.mount(Label("R: Replace | A: Append | I: Insert | ESC: Cancel", id="load-mode-status"))

        self.mode = "load_mode_select"

        # Focus the option list
        self.query_one("#load-mode-options", OptionList).focus()

    def _show_menu(self) -> None:
        """Show the main menu."""
        container = self.query_one("#prompt-manager-dialog", Container)
        for child in list(container.children):
            child.remove()

        container.mount(Label(f"{self.pane_name} - Prompt Manager", id="prompt-manager-title"))
        for widget in self._compose_menu():
            container.mount(widget)

        self.mode = "menu"

        # Focus the option list for keyboard navigation
        self.query_one("#prompt-manager-options", OptionList).focus()

    def on_mount(self) -> None:
        """Handle mount event."""
        # Ensure prompts directory exists
        self.prompts_dir.mkdir(parents=True, exist_ok=True)

        # Focus the initial menu options list
        self.query_one("#prompt-manager-options", OptionList).focus()

    def action_dismiss_cancel(self) -> None:
        """Dismiss with cancel action."""
        self.dismiss({"action": "cancel"})

    def on_key(self, event) -> None:
        """Handle keyboard shortcuts."""
        # Single key shortcuts for load mode selection
        if self.mode == "load_mode_select":
            if event.key in ("r", "R"):
                # Replace mode
                file_path = self.prompts_dir / self.selected_filename
                self.dismiss({
                    "action": "load",
                    "mode": "replace",
                    "filename": self.selected_filename,
                    "path": str(file_path)
                })
                event.prevent_default()
                event.stop()
            elif event.key in ("a", "A"):
                # Append mode
                file_path = self.prompts_dir / self.selected_filename
                self.dismiss({
                    "action": "load",
                    "mode": "append",
                    "filename": self.selected_filename,
                    "path": str(file_path)
                })
                event.prevent_default()
                event.stop()
            elif event.key in ("i", "I"):
                # Insert mode
                file_path = self.prompts_dir / self.selected_filename
                self.dismiss({
                    "action": "load",
                    "mode": "insert",
                    "filename": self.selected_filename,
                    "path": str(file_path)
                })
                event.prevent_default()
                event.stop()

    def on_option_list_option_selected(self, event) -> None:
        """Handle option selection based on current mode."""
        option_id = event.option.id

        if not option_id:
            return

        if option_id == "action_back":
            self._show_menu()
        elif option_id == "action_cancel":
            self.dismiss({"action": "cancel"})
        elif self.mode == "menu":
            if option_id == "action_list":
                self._show_prompt_list()
            elif option_id == "action_load":
                self._show_load_screen()
            elif option_id == "action_save":
                self._show_save_screen()
        elif self.mode == "list":
            # Load the selected file
            if option_id.startswith("file_"):
                filename = option_id[5:]  # Remove "file_" prefix
                self._load_prompt(filename)
        elif self.mode == "load":
            # Load the selected file
            if option_id.startswith("load_"):
                filename = option_id[5:]  # Remove "load_" prefix
                self._load_prompt(filename)
        elif self.mode == "load_mode_select":
            # Handle insertion mode selection
            if option_id.startswith("mode_"):
                mode = option_id[5:]  # Remove "mode_" prefix (replace, append, insert)
                file_path = self.prompts_dir / self.selected_filename
                self.dismiss({
                    "action": "load",
                    "mode": mode,
                    "filename": self.selected_filename,
                    "path": str(file_path)
                })
