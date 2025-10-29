"""Main window for the LLM Manager application."""

import asyncio
from pathlib import Path
from datetime import datetime
from enum import Enum
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
from .menu import PaneMenuScreen
from .root_pane import RootPane
from .prompt_manager_screen import PromptManagerScreen


class PaneState(Enum):
    """Pane visibility states."""
    NORMAL = "normal"
    MAXIMIZED = "maximized"
    MINIMIZED = "minimized"


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

    .pane-minimized {
        height: 3;
        max-height: 3;
    }

    .pane-minimized TextArea {
        display: none;
    }

    .pane-minimized .pane-footer {
        display: none;
    }

    .pane-minimized .response-content {
        display: none;
    }

    .pane-minimized .status-bar {
        display: none;
    }

    .pane-minimized .model-list {
        display: none;
    }

    .pane-minimized .model-info {
        display: none;
    }

    .row-hidden {
        display: none;
    }
    """

    BINDINGS = [
        Binding("?", "show_help", "Help", show=True),
        Binding("q", "quit", "Quit", show=True),
        Binding("escape", "show_pane_menu", "Menu", show=True),
        Binding("tab", "focus_next", "Next Pane", show=True, priority=True),
        Binding("shift+tab", "focus_previous", "Prev Pane", show=True, priority=True),
        Binding("e", "edit_focused", "Edit", show=True),
        Binding("ctrl+s", "save_focused", "Save", show=True),
        Binding("p", "open_prompt_manager", "Prompt Mgr", show=True),
        Binding("ctrl+j", "send_to_llm", "Send", show=True, priority=True),
        Binding("s", "toggle_streaming", "Stream Toggle", show=False),
        Binding("c", "clear_response", "Clear", show=False),
        Binding("ctrl+e", "export_conversation", "Export", show=False),
        Binding("ctrl+i", "import_conversation", "Import", show=False),
        Binding("m", "toggle_maximize", "Maximize", show=True),
        Binding("n", "toggle_minimize", "Minimize", show=True),
        Binding("ctrl+up", "increase_height", "Height+", show=False),
        Binding("ctrl+down", "decrease_height", "Height-", show=False),
        Binding("ctrl+h", "hide_all_children", "Hide All", show=False),
        Binding("ctrl+shift+h", "show_all_children", "Show All", show=False),
        Binding("ctrl+r", "reset_layout", "Reset Layout", show=False),
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

        # Track pane states
        self.pane_states = {}
        self.maximized_pane = None
        self.PaneState = PaneState  # Make PaneState accessible to menu

        # Create child panes first
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

        # Create root pane (will contain all other panes)
        self.root_pane = RootPane(
            child_panes_layout=self._compose_child_panes,
            id="root-pane"
        )

    def _compose_child_panes(self) -> ComposeResult:
        """Compose the layout of child panes within the root pane."""
        # First row: User Prompt and System Prompt side by side
        row1 = Horizontal(classes="pane-row")
        row1.can_focus = False
        with row1:
            yield self.user_prompt_pane
            yield self.system_prompt_pane

        # Second row: Context and LLM Selection side by side
        row2 = Horizontal(classes="pane-row")
        row2.can_focus = False
        with row2:
            yield self.context_pane
            yield self.llm_selection_pane

        # Third row: Response pane (full width)
        row3 = Vertical(classes="pane-row")
        row3.can_focus = False
        with row3:
            yield self.response_pane

    def compose(self) -> ComposeResult:
        """Compose the application layout with hierarchical root pane structure."""
        yield Header()

        # Mount the root pane which contains all other panes
        yield self.root_pane

        yield Footer()

    def on_mount(self) -> None:
        """Handle mount event."""
        # Store child pane references in root pane
        self.root_pane.child_panes = [
            self.user_prompt_pane,
            self.system_prompt_pane,
            self.context_pane,
            self.llm_selection_pane,
            self.response_pane,
        ]

        # Initialize pane states
        for pane, _ in self._get_pane_list():
            self.pane_states[pane] = PaneState.NORMAL

        # Focus root pane by default to show hierarchy
        self.root_pane.focus()

        # Load selected model
        selected_model = self.llm_selection_pane.get_selected_model()
        if selected_model:
            success = self.llm_client.set_model(selected_model)
            if success:
                self.notify(f"Model loaded: {selected_model}", severity="information")
            else:
                self.notify("Failed to load model. Check API keys.", severity="warning")

    def action_focus_root(self) -> None:
        """Focus the root pane."""
        self.root_pane.focus()

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
        """Get the ordered list of all panes including root."""
        return [
            (self.root_pane, "Root"),
            (self.user_prompt_pane, "User Prompt"),
            (self.system_prompt_pane, "System Prompt"),
            (self.context_pane, "Context"),
            (self.llm_selection_pane, "LLM Selection"),
            (self.response_pane, "Response"),
        ]

    def _get_child_panes(self):
        """Get only the child panes (excluding root)."""
        return [
            (self.user_prompt_pane, "User Prompt"),
            (self.system_prompt_pane, "System Prompt"),
            (self.context_pane, "Context"),
            (self.llm_selection_pane, "LLM Selection"),
            (self.response_pane, "Response"),
        ]

    def _find_current_pane_index(self, panes):
        """Find the index of the currently focused pane.

        Walks up the widget tree from the focused widget to find which
        top-level pane contains it.
        """
        focused = self.focused
        if not focused:
            return 0  # Default to first pane if nothing focused

        # Walk up from focused widget to find which pane it belongs to
        current = focused
        while current is not None:
            # Check if this widget is one of our panes
            for i, (pane, _) in enumerate(panes):
                if current is pane:
                    return i
            current = current.parent

        return 0  # Default to first pane if not found

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

    def action_open_prompt_manager(self) -> None:
        """Open prompt manager for the currently focused pane."""
        focused = self.focused
        current = focused

        # Find which pane is focused
        pane_name = None
        target_pane = None

        while current is not None:
            if current is self.user_prompt_pane:
                pane_name = "User Prompt"
                target_pane = self.user_prompt_pane
                break
            elif current is self.system_prompt_pane:
                pane_name = "System Prompt"
                target_pane = self.system_prompt_pane
                break
            elif current is self.context_pane:
                pane_name = "Context"
                target_pane = self.context_pane
                break
            current = current.parent

        if not pane_name or not target_pane:
            self.notify("Prompt manager only works for User Prompt, System Prompt, and Context panes", severity="warning")
            return

        # Open the prompt manager screen
        self.push_screen(
            PromptManagerScreen(
                pane_name=pane_name,
                current_content=target_pane.content
            ),
            lambda result: self._handle_prompt_manager_result(result, target_pane)
        )

    def _handle_prompt_manager_result(self, result: dict, target_pane) -> None:
        """Handle the result from the prompt manager.

        Args:
            result: Dictionary with action and data
            target_pane: The pane to update
        """
        if not result or result.get("action") == "cancel":
            return

        action = result.get("action")

        if action == "load":
            # Load prompt from file
            file_path = Path(result.get("path"))
            if file_path.exists():
                new_content = file_path.read_text(encoding="utf-8")
                mode = result.get("mode", "replace")  # Default to replace if no mode specified

                if mode == "replace":
                    # Replace entire content
                    target_pane.content = new_content
                    self.notify(f"Loaded (replaced): {result.get('filename')}", severity="information")
                elif mode == "append":
                    # Append to existing content
                    current_content = target_pane.content
                    target_pane.content = current_content + new_content
                    self.notify(f"Loaded (appended): {result.get('filename')}", severity="information")
                elif mode == "insert":
                    # Insert at cursor position
                    # Get the TextArea widget to access cursor position
                    try:
                        text_area = target_pane.query_one(f"#{target_pane.id}-content")
                        cursor = text_area.cursor_location
                        current_text = text_area.text

                        # Calculate position from cursor location (row, column)
                        lines = current_text.split('\n')
                        position = sum(len(line) + 1 for line in lines[:cursor[0]]) + cursor[1]

                        # Insert at cursor position
                        new_text = current_text[:position] + new_content + current_text[position:]
                        target_pane.content = new_text
                        self.notify(f"Loaded (inserted): {result.get('filename')}", severity="information")
                    except Exception:
                        # Fallback to append if cursor position not available
                        current_content = target_pane.content
                        target_pane.content = current_content + new_content
                        self.notify(f"Loaded (appended): {result.get('filename')}", severity="information")
            else:
                self.notify("File not found", severity="error")

        elif action == "save":
            # Save current prompt to file
            file_path = Path(result.get("path"))
            file_path.write_text(target_pane.content, encoding="utf-8")
            self.notify(f"Saved: {result.get('filename')}", severity="information")

    def action_show_help(self) -> None:
        """Show the help screen."""
        self.push_screen(HelpScreen())

    def action_show_pane_menu(self) -> None:
        """Show the pane management menu."""
        self.push_screen(PaneMenuScreen(self))

    def _get_focused_pane(self):
        """Get the currently focused pane."""
        focused = self.focused
        current = focused

        while current is not None:
            if current in [pane for pane, _ in self._get_pane_list()]:
                return current
            current = current.parent

        return None

    def _get_pane_row(self, pane):
        """Get the row container for a given pane."""
        # Root pane contains all rows, so it doesn't have a specific row
        if pane == self.root_pane:
            return None
        # Map child panes to their row indices
        elif pane in [self.user_prompt_pane, self.system_prompt_pane]:
            return 0
        elif pane in [self.context_pane, self.llm_selection_pane]:
            return 1
        elif pane == self.response_pane:
            return 2
        return None

    def action_toggle_maximize(self) -> None:
        """Toggle maximize state for the currently focused pane."""
        pane = self._get_focused_pane()
        if not pane:
            return

        # If this pane is maximized, restore it
        if self.maximized_pane == pane:
            self._restore_all_panes()
            self.maximized_pane = None
        # If another pane is maximized, switch to this one
        elif self.maximized_pane is not None:
            self._restore_all_panes()
            self._maximize_pane(pane)
            self.maximized_pane = pane
        # If no pane is maximized, maximize this one
        else:
            self._maximize_pane(pane)
            self.maximized_pane = pane

    def action_toggle_minimize(self) -> None:
        """Toggle minimize state for the currently focused pane."""
        pane = self._get_focused_pane()
        if not pane:
            return

        # Can't minimize if pane is maximized
        if self.maximized_pane == pane:
            return

        # Initialize state if not present
        if pane not in self.pane_states:
            self.pane_states[pane] = PaneState.NORMAL

        current_state = self.pane_states.get(pane, PaneState.NORMAL)

        if current_state == PaneState.MINIMIZED:
            # Restore from minimized
            pane.remove_class("pane-minimized")
            self.pane_states[pane] = PaneState.NORMAL
        else:
            # Minimize
            pane.add_class("pane-minimized")
            self.pane_states[pane] = PaneState.MINIMIZED

    def _maximize_pane(self, pane):
        """Maximize a specific pane."""
        containers = self.query(".pane-row")
        target_row_idx = self._get_pane_row(pane)

        # Can't maximize panes that aren't in a row (like root pane)
        if target_row_idx is None:
            return

        # Hide all rows except the one containing the target pane
        for idx, container in enumerate(containers):
            if idx != target_row_idx:
                container.add_class("row-hidden")

        # In the target row, hide other panes
        pane_row = containers[target_row_idx]
        for child in pane_row.children:
            if child != pane and hasattr(child, 'add_class'):
                child.add_class("row-hidden")

        self.pane_states[pane] = PaneState.MAXIMIZED

    def _restore_all_panes(self):
        """Restore all panes to normal state."""
        containers = self.query(".pane-row")
        for container in containers:
            container.remove_class("row-hidden")

        for pane, _ in self._get_pane_list():
            pane.remove_class("row-hidden")
            if self.pane_states.get(pane) != PaneState.MINIMIZED:
                self.pane_states[pane] = PaneState.NORMAL

    def _get_pane_name(self, pane):
        """Get the display name of a pane."""
        for p, name in self._get_pane_list():
            if p == pane:
                return name
        return "Unknown"

    def action_increase_height(self) -> None:
        """Increase height/state of the focused pane.

        Cycles: Minimized → Normal (1fr) → 2fr → 3fr → Maximized → Minimized
        """
        pane = self._get_focused_pane()
        if not pane:
            return

        # Initialize state if not present
        if pane not in self.pane_states:
            self.pane_states[pane] = PaneState.NORMAL

        # Check current state
        if self.maximized_pane == pane:
            # Maximized → Minimized
            self._restore_all_panes()
            self.maximized_pane = None
            pane.add_class("pane-minimized")
            self.pane_states[pane] = PaneState.MINIMIZED
        elif self.pane_states[pane] == PaneState.MINIMIZED:
            # Minimized → Normal (1fr)
            pane.remove_class("pane-minimized")
            self.pane_states[pane] = PaneState.NORMAL
            row_idx = self._get_pane_row(pane)
            if row_idx is not None:
                containers = self.query(".pane-row")
                if row_idx < len(containers):
                    containers[row_idx].styles.height = "1fr"
        else:
            # Normal state - check row height
            row_idx = self._get_pane_row(pane)
            if row_idx is not None:
                containers = self.query(".pane-row")
                if row_idx < len(containers):
                    container = containers[row_idx]
                    current_height = getattr(container.styles, 'height', None)

                    if current_height is None or str(current_height) == "1fr":
                        # 1fr → 2fr
                        container.styles.height = "2fr"
                    elif str(current_height) == "2fr":
                        # 2fr → 3fr
                        container.styles.height = "3fr"
                    else:
                        # 3fr → Maximized
                        self._maximize_pane(pane)
                        self.maximized_pane = pane

    def action_decrease_height(self) -> None:
        """Decrease height/state of the focused pane.

        Cycles: Maximized → 3fr → 2fr → Normal (1fr) → Minimized → Maximized
        """
        pane = self._get_focused_pane()
        if not pane:
            return

        # Initialize state if not present
        if pane not in self.pane_states:
            self.pane_states[pane] = PaneState.NORMAL

        # Check current state
        if self.maximized_pane == pane:
            # Maximized → 3fr
            self._restore_all_panes()
            self.maximized_pane = None
            row_idx = self._get_pane_row(pane)
            if row_idx is not None:
                containers = self.query(".pane-row")
                if row_idx < len(containers):
                    containers[row_idx].styles.height = "3fr"
        elif self.pane_states[pane] == PaneState.MINIMIZED:
            # Minimized → Maximized
            pane.remove_class("pane-minimized")
            self.pane_states[pane] = PaneState.NORMAL
            self._maximize_pane(pane)
            self.maximized_pane = pane
        else:
            # Normal state - check row height
            row_idx = self._get_pane_row(pane)
            if row_idx is not None:
                containers = self.query(".pane-row")
                if row_idx < len(containers):
                    container = containers[row_idx]
                    current_height = getattr(container.styles, 'height', None)

                    if str(current_height) == "3fr":
                        # 3fr → 2fr
                        container.styles.height = "2fr"
                    elif str(current_height) == "2fr":
                        # 2fr → 1fr
                        container.styles.height = "1fr"
                    else:
                        # 1fr → Minimized
                        pane.add_class("pane-minimized")
                        self.pane_states[pane] = PaneState.MINIMIZED

    def action_hide_all_children(self) -> None:
        """Hide all child panes (root-level operation)."""
        self.root_pane.hide_all_children()

    def action_show_all_children(self) -> None:
        """Show all child panes (root-level operation)."""
        self.root_pane.show_all_children()

    def action_reset_layout(self) -> None:
        """Reset layout to defaults (root-level operation)."""
        # Restore from maximized state if any
        if self.maximized_pane is not None:
            self._restore_all_panes()
            self.maximized_pane = None

        # Reset all pane states via root pane
        self.root_pane.reset_layout()

        # Reset pane state tracking
        for pane, _ in self._get_pane_list():
            if pane in self.pane_states:
                self.pane_states[pane] = PaneState.NORMAL


def run_app() -> None:
    """Run the LLM Manager application."""
    app = LLMManagerApp()
    app.run()
