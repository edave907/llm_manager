"""Main window for the LLM Manager application."""

import asyncio
from pathlib import Path
from datetime import datetime
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Header, Footer
from textual.worker import Worker, WorkerState

from ..core.settings import settings
from ..core.llm_client import LLMClient
from ..core.conversation import ConversationHistory
from .pane import EditablePane
from .llm_pane import LLMSelectionPane
from .response_pane import ResponsePane
from .help_screen import HelpScreen


class LLMManagerApp(App):
    """Main LLM Manager TUI application."""

    CSS = """
    Screen {
        background: $surface;
    }

    #pane-container {
        height: 1fr;
    }

    .pane-row {
        height: 1fr;
    }
    """

    BINDINGS = [
        Binding("?", "show_help", "Help", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("1", "focus_user_prompt", "User Prompt", show=True),
        Binding("2", "focus_system_prompt", "System Prompt", show=True),
        Binding("3", "focus_context", "Context", show=True),
        Binding("4", "focus_llm_selection", "LLM Select", show=True),
        Binding("5", "focus_response", "Response", show=True),
        Binding("tab", "focus_next", "Next Pane", show=True),
        Binding("shift+tab", "focus_previous", "Prev Pane", show=True),
        Binding("e", "edit_focused", "Edit", show=True),
        Binding("ctrl+s", "save_focused", "Save", show=True),
        Binding("enter", "send_to_llm", "Send", show=True),
        Binding("s", "toggle_streaming", "Stream Toggle", show=False),
        Binding("c", "clear_response", "Clear", show=False),
        Binding("ctrl+e", "export_conversation", "Export", show=False),
        Binding("ctrl+i", "import_conversation", "Import", show=False),
    ]

    TITLE = "LLM Manager"
    SUB_TITLE = "Text-based LLM Interface"

    def __init__(self):
        """Initialize the application."""
        super().__init__()
        settings.ensure_files()

        # Create LLM client and conversation history
        self.llm_client = LLMClient()
        self.conversation_history = ConversationHistory()

        # Create panes
        self.user_prompt_pane = EditablePane(
            title="User Prompt",
            storage_path=settings.USER_PROMPT_FILE,
            editor=settings.EDITOR,
            id="user-prompt-pane"
        )

        self.system_prompt_pane = EditablePane(
            title="System Prompt",
            storage_path=settings.SYSTEM_PROMPT_FILE,
            editor=settings.EDITOR,
            id="system-prompt-pane"
        )

        self.context_pane = EditablePane(
            title="Context",
            storage_path=settings.CONTEXT_FILE,
            editor=settings.EDITOR,
            id="context-pane"
        )

        self.llm_selection_pane = LLMSelectionPane(
            id="llm-selection-pane"
        )

        self.response_pane = ResponsePane(
            id="response-pane"
        )

    def compose(self) -> ComposeResult:
        """Compose the application layout."""
        yield Header()

        with Container(id="pane-container"):
            # First row: User Prompt and System Prompt side by side
            with Horizontal(classes="pane-row"):
                yield self.user_prompt_pane
                yield self.system_prompt_pane

            # Second row: Context and LLM Selection side by side
            with Horizontal(classes="pane-row"):
                yield self.context_pane
                yield self.llm_selection_pane

            # Third row: Response pane (full width)
            with Vertical(classes="pane-row"):
                yield self.response_pane

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        # Focus user prompt by default
        self.user_prompt_pane.focus()

        # Load selected model
        selected_model = self.llm_selection_pane.get_selected_model()
        if selected_model:
            success = self.llm_client.set_model(selected_model)
            if success:
                self.notify(f"Model loaded: {selected_model}", severity="information")
            else:
                self.notify("Failed to load model. Check API keys.", severity="warning")

    def action_focus_user_prompt(self) -> None:
        """Focus the user prompt pane."""
        self.user_prompt_pane.focus()

    def action_focus_system_prompt(self) -> None:
        """Focus the system prompt pane."""
        self.system_prompt_pane.focus()

    def action_focus_context(self) -> None:
        """Focus the context pane."""
        self.context_pane.focus()

    def action_focus_llm_selection(self) -> None:
        """Focus the LLM selection pane."""
        self.llm_selection_pane.focus()

    def action_focus_response(self) -> None:
        """Focus the response pane."""
        self.response_pane.focus()

    def _get_pane_list(self):
        """Get the ordered list of panes."""
        return [
            (self.user_prompt_pane, "User Prompt"),
            (self.system_prompt_pane, "System Prompt"),
            (self.context_pane, "Context"),
            (self.llm_selection_pane, "LLM Selection"),
            (self.response_pane, "Response"),
        ]

    def _find_current_pane_index(self, panes):
        """Find the index of the currently focused pane."""
        focused = self.focused
        current_index = -1

        for i, (pane, _) in enumerate(panes):
            # Check if this pane or any of its children is focused
            current = focused
            while current is not None:
                if current is pane:
                    current_index = i
                    break
                current = current.parent
            if current_index >= 0:
                break

        return current_index

    def action_focus_next(self) -> None:
        """Focus the next pane in sequence."""
        panes = self._get_pane_list()
        current_index = self._find_current_pane_index(panes)

        # Move to next pane (wrap around to first if at the end)
        next_index = (current_index + 1) % len(panes)
        next_pane, next_name = panes[next_index]
        next_pane.focus()

    def action_focus_previous(self) -> None:
        """Focus the previous pane in sequence."""
        panes = self._get_pane_list()
        current_index = self._find_current_pane_index(panes)

        # Move to previous pane (wrap around to last if at the beginning)
        prev_index = (current_index - 1) % len(panes)
        prev_pane, prev_name = panes[prev_index]
        prev_pane.focus()

    def action_edit_focused(self) -> None:
        """Edit the currently focused pane in external editor."""
        focused = self.focused

        # Find which pane is focused by checking the widget's ancestry
        # We need to walk up the tree to find the EditablePane container
        current = focused
        while current is not None:
            if current is self.user_prompt_pane:
                self.user_prompt_pane.edit_with_nvim()
                return
            elif current is self.system_prompt_pane:
                self.system_prompt_pane.edit_with_nvim()
                return
            elif current is self.context_pane:
                self.context_pane.edit_with_nvim()
                return
            current = current.parent

        self.notify("No editable pane focused", severity="warning")

    def action_save_focused(self) -> None:
        """Save the currently focused pane."""
        focused = self.focused

        # Find which pane is focused
        current = focused
        while current is not None:
            if current is self.user_prompt_pane:
                if self.user_prompt_pane.save_content():
                    self.notify("User Prompt saved", severity="information")
                return
            elif current is self.system_prompt_pane:
                if self.system_prompt_pane.save_content():
                    self.notify("System Prompt saved", severity="information")
                return
            elif current is self.context_pane:
                if self.context_pane.save_content():
                    self.notify("Context saved", severity="information")
                return
            current = current.parent

        self.notify("No editable pane focused", severity="warning")

    def action_send_to_llm(self) -> None:
        """Send the current prompts to the LLM."""
        # Get selected model
        selected_model = self.llm_selection_pane.get_selected_model()
        if not selected_model:
            self.notify("Please select a model first (press 4)", severity="error")
            return

        # Set model if not already set
        if self.llm_client.current_model != selected_model:
            success = self.llm_client.set_model(selected_model)
            if not success:
                self.notify("Failed to initialize model. Check API keys.", severity="error")
                return

        # Get prompts
        user_prompt = self.user_prompt_pane.content
        system_prompt = self.system_prompt_pane.content
        context = self.context_pane.content

        if not user_prompt.strip():
            self.notify("User prompt is empty", severity="warning")
            return

        # Clear previous response
        self.response_pane.clear_response()

        # Send based on streaming setting
        if self.response_pane.streaming_enabled:
            self.run_worker(self._send_streaming(user_prompt, system_prompt, context))
        else:
            self.run_worker(self._send_non_streaming(user_prompt, system_prompt, context))

    async def _send_streaming(self, user_prompt: str, system_prompt: str, context: str) -> None:
        """Send message with streaming enabled."""
        self.response_pane.set_status("Streaming...")

        try:
            full_response = ""
            for chunk in self.llm_client.stream_message(user_prompt, system_prompt, context):
                full_response += chunk
                self.response_pane.append_response_chunk(chunk)
                await asyncio.sleep(0.01)  # Small delay for UI update

            self.response_pane.set_status("Complete")

            # Save to history
            self.conversation_history.add_turn(
                model=self.llm_client.current_model,
                user_prompt=user_prompt,
                response=full_response,
                system_prompt=system_prompt,
                context=context,
            )

            self.notify("Response received", severity="information")

        except Exception as e:
            self.response_pane.show_error(str(e))
            self.notify(f"Error: {str(e)}", severity="error")

    async def _send_non_streaming(self, user_prompt: str, system_prompt: str, context: str) -> None:
        """Send message without streaming."""
        self.response_pane.set_status("Waiting for response...")

        try:
            response = self.llm_client.send_message(user_prompt, system_prompt, context)
            self.response_pane.set_response(response)
            self.response_pane.set_status("Complete")

            # Save to history
            self.conversation_history.add_turn(
                model=self.llm_client.current_model,
                user_prompt=user_prompt,
                response=response,
                system_prompt=system_prompt,
                context=context,
            )

            self.notify("Response received", severity="information")

        except Exception as e:
            self.response_pane.show_error(str(e))
            self.notify(f"Error: {str(e)}", severity="error")

    def action_toggle_streaming(self) -> None:
        """Toggle streaming mode."""
        self.response_pane.toggle_streaming()

    def action_clear_response(self) -> None:
        """Clear the response pane."""
        self.response_pane.clear_response()
        self.notify("Response cleared", severity="information")

    def action_export_conversation(self) -> None:
        """Export conversation history."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = Path.home() / f"llm_conversation_{timestamp}.json"

        success = self.conversation_history.export_to_file(filepath, format="json")
        if success:
            self.notify(f"Exported to {filepath}", severity="information")
        else:
            self.notify("Export failed", severity="error")

    def action_import_conversation(self) -> None:
        """Import conversation history."""
        # For now, this is a placeholder
        # In a full implementation, you'd show a file picker
        self.notify("Import: Feature requires file picker", severity="information")

    def action_show_help(self) -> None:
        """Show the help screen."""
        self.push_screen(HelpScreen())


def run_app() -> None:
    """Run the LLM Manager application."""
    app = LLMManagerApp()
    app.run()
