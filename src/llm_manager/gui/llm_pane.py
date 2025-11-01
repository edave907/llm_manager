"""LLM selection pane widget for LLM Manager."""

from textual.app import ComposeResult
from textual.containers import Container, Vertical
from textual.widgets import Static, Label, OptionList
from textual.widgets.option_list import Option
from textual.binding import Binding
from textual import events, work
from rich.text import Text

from ..core.models import AVAILABLE_MODELS, MODELS_BY_PROVIDER, get_model_config
from ..core.settings import settings
from .confirmation_screen import ConfirmationScreen


class LLMSelectionPane(Container, can_focus=True):
    """Pane for selecting and viewing LLM information."""

    BINDINGS = [
        Binding("escape", "exit_select_mode", "Exit Select Mode", show=False),
    ]

    DEFAULT_CSS = """
    LLMSelectionPane {
        border: solid $primary;
        height: 1fr;
        margin: 1;
    }

    LLMSelectionPane:focus {
        border: heavy $accent;
    }

    LLMSelectionPane.pane-focused {
        border: heavy $accent;
    }

    LLMSelectionPane .pane-title {
        background: $primary;
        color: $text;
        text-align: center;
        padding: 0 1;
    }

    LLMSelectionPane:focus .pane-title {
        background: $accent;
        color: $text;
    }

    LLMSelectionPane.pane-focused .pane-title {
        background: $accent;
        color: $text;
    }

    LLMSelectionPane .model-list {
        height: 1fr;
        border: solid $surface;
        margin: 1 2;
    }

    LLMSelectionPane .model-info {
        background: $surface;
        color: $text;
        padding: 1 2;
        height: auto;
        min-height: 6;
    }

    LLMSelectionPane .pane-footer {
        background: $surface;
        color: $text-muted;
        text-align: center;
        padding: 0 1;
    }

    LLMSelectionPane .feedback-box {
        background: $surface;
        color: $accent;
        text-align: center;
        padding: 0 1;
        height: 1;
    }
    """

    def __init__(
        self,
        name: str | None = None,
        id: str | None = None,
        classes: str | None = None,
    ):
        """Initialize the LLM selection pane.

        Args:
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.selected_model: str | None = None
        self.select_mode: bool = False  # Track if in model select mode
        self.staged_model: str | None = None  # Track temporary selection
        self._load_selected_model()

    def compose(self) -> ComposeResult:
        """Compose the pane widget."""
        yield Label("LLM Selection", classes="pane-title")

        with Vertical():
            # Build model options
            options = []

            # OpenAI models
            options.append(Option(Text("OpenAI Models", style="bold cyan"), disabled=True))
            for model_name in MODELS_BY_PROVIDER.get("openai", []):
                config = get_model_config(model_name)
                if config:
                    options.append(Option(config.display_name, id=model_name))

            # Separator
            options.append(Option(Text("---", style="dim"), disabled=True))

            # Anthropic models
            options.append(Option(Text("Anthropic Models", style="bold magenta"), disabled=True))
            for model_name in MODELS_BY_PROVIDER.get("anthropic", []):
                config = get_model_config(model_name)
                if config:
                    options.append(Option(config.display_name, id=model_name))

            # Separator
            options.append(Option(Text("---", style="dim"), disabled=True))

            # Ollama models (local)
            options.append(Option(Text("Ollama Models (Local)", style="bold green"), disabled=True))
            for model_name in MODELS_BY_PROVIDER.get("ollama", []):
                config = get_model_config(model_name)
                if config:
                    options.append(Option(config.display_name, id=model_name))

            yield OptionList(*options, classes="model-list", id="model-option-list")
            yield Static("", classes="model-info", id="model-info-display")

        yield Static("", classes="feedback-box", id="feedback-box")
        yield Label(
            "Press Enter to select | Up/Down to navigate",
            classes="pane-footer"
        )

    def on_mount(self) -> None:
        """Handle mount event."""
        # Highlight the selected model if one exists
        if self.selected_model:
            option_list = self.query_one("#model-option-list", OptionList)
            # Find and highlight the selected model
            for idx, option in enumerate(option_list._options):
                if hasattr(option, 'id') and option.id == self.selected_model:
                    option_list.highlighted = idx
                    break
            self._update_model_info(self.selected_model)

    def on_focus(self) -> None:
        """Handle focus event."""
        self.add_class("pane-focused")

    def on_blur(self) -> None:
        """Handle blur event."""
        self.remove_class("pane-focused")

    def on_key(self, event: events.Key) -> None:
        """Handle key events."""
        if not self.select_mode and event.key == "enter":
            # Enter select mode
            self.enter_select_mode()
            event.prevent_default()
            event.stop()
        elif self.select_mode:
            if event.key == "enter":
                # Stage the currently highlighted model
                self.stage_current_selection()
                event.prevent_default()
                event.stop()
            elif event.key in ("up", "down"):
                # Let OptionList handle navigation
                pass

    def on_click(self, event: events.Click) -> None:
        """Handle mouse click - enter select mode."""
        if not self.select_mode and self.has_focus:
            self.enter_select_mode()

    def on_option_list_option_highlighted(self, event: OptionList.OptionHighlighted) -> None:
        """Handle model option highlighted."""
        if event.option.id:
            self._update_model_info(event.option.id)

    def on_option_list_option_selected(self, event: OptionList.OptionSelected) -> None:
        """Handle model selection - only when NOT in select mode."""
        # When in select mode, we handle Enter key separately
        if not self.select_mode and event.option.id:
            self.selected_model = event.option.id
            self._save_selected_model()
            self._update_model_info(event.option.id)
            self.app.notify(f"Selected: {event.option.prompt}", severity="information")

    def _update_model_info(self, model_name: str) -> None:
        """Update the model info display.

        Args:
            model_name: The model identifier
        """
        config = get_model_config(model_name)
        if not config:
            return

        info_display = self.query_one("#model-info-display", Static)

        info_text = Text()
        info_text.append(f"{config.display_name}\n", style="bold")
        info_text.append(f"Provider: {config.provider.capitalize()}\n")
        info_text.append(f"Context: {config.context_window:,} tokens\n")
        info_text.append(f"Max output: {config.max_output_tokens:,} tokens\n")

        if config.input_cost_per_1k > 0:
            info_text.append(
                f"Cost: ${config.input_cost_per_1k:.3f}/${config.output_cost_per_1k:.3f} per 1K\n",
                style="yellow"
            )

        if self.selected_model == model_name:
            info_text.append("\n", style="")
            info_text.append("✓ Currently Selected", style="bold green")

        info_display.update(info_text)

    def _load_selected_model(self) -> None:
        """Load the previously selected model from file."""
        try:
            if settings.SELECTED_MODEL_FILE.exists():
                self.selected_model = settings.SELECTED_MODEL_FILE.read_text().strip()
        except Exception:
            self.selected_model = settings.DEFAULT_MODEL

    def _save_selected_model(self) -> None:
        """Save the selected model to file."""
        try:
            settings.SELECTED_MODEL_FILE.parent.mkdir(parents=True, exist_ok=True)
            settings.SELECTED_MODEL_FILE.write_text(self.selected_model, encoding="utf-8")
        except Exception as e:
            self.app.notify(f"Failed to save model selection: {e}", severity="error")

    def enter_select_mode(self) -> None:
        """Enter model select mode."""
        self.select_mode = True
        self.staged_model = None
        # Focus the OptionList so arrow keys work
        option_list = self.query_one("#model-option-list", OptionList)
        option_list.focus()
        self._update_feedback_box()

    def stage_current_selection(self) -> None:
        """Stage the currently highlighted model."""
        option_list = self.query_one("#model-option-list", OptionList)
        highlighted_option = option_list.get_option_at_index(option_list.highlighted)
        if highlighted_option and highlighted_option.id:
            self.staged_model = highlighted_option.id
            self._update_feedback_box()

    def action_exit_select_mode(self) -> None:
        """Exit select mode with confirmation if model changed."""
        if not self.select_mode:
            return

        # Check if staged model differs from selected model
        if self.staged_model and self.staged_model != self.selected_model:
            # Show confirmation in a worker
            self._confirm_and_exit()
        else:
            # No change, just exit
            self.select_mode = False
            self.staged_model = None
            self._update_feedback_box()
            self.focus()

    @work(exclusive=True)
    async def _confirm_and_exit(self) -> None:
        """Show confirmation dialog and handle result (runs in worker)."""
        config = get_model_config(self.staged_model)
        model_display = config.display_name if config else self.staged_model

        result = await self.app.push_screen_wait(
            ConfirmationScreen(
                message=f"Save model selection: {model_display}?",
                title="Confirm Model Selection"
            )
        )

        if result:
            # Save the staged model
            self.selected_model = self.staged_model
            self._save_selected_model()
            self._update_model_info(self.selected_model)
            self.app.notify(f"Selected: {model_display}", severity="information")

        # Exit select mode
        self.select_mode = False
        self.staged_model = None
        self._update_feedback_box()
        self.focus()

    def _update_feedback_box(self) -> None:
        """Update the feedback box display."""
        feedback_box = self.query_one("#feedback-box", Static)

        if self.select_mode and self.staged_model:
            config = get_model_config(self.staged_model)
            model_display = config.display_name if config else self.staged_model
            feedback_box.update(f"Staged: {model_display}")
        else:
            feedback_box.update("")

    def get_selected_model(self) -> str | None:
        """Get the currently selected model."""
        return self.selected_model
