"""Tests for pane management (maximize, minimize, resize) functionality."""

import pytest
from textual.widgets import TextArea

from llm_manager.gui.main_window import LLMManagerApp, PaneState


class TestPaneManagement:
    """Test suite for pane management features."""

    @pytest.fixture
    def app(self):
        """Create an app instance for testing."""
        return LLMManagerApp()

    def test_pane_states_initialized(self, app):
        """Test that pane states dictionary is initialized."""
        # States are initialized in on_mount, so we just verify the dict exists
        assert hasattr(app, 'pane_states')
        assert isinstance(app.pane_states, dict)
        assert hasattr(app, 'maximized_pane')
        assert app.maximized_pane is None

    @pytest.mark.skip(reason="Requires mounted app with DOM")
    def test_maximize_pane_tracking(self, app):
        """Test that maximized pane is tracked correctly."""
        assert app.maximized_pane is None

        # Simulate maximizing the user prompt pane
        app._maximize_pane(app.user_prompt_pane)
        assert app.pane_states[app.user_prompt_pane] == PaneState.MAXIMIZED

    @pytest.mark.skip(reason="Requires mounted app with DOM")
    def test_restore_all_panes(self, app):
        """Test that restore resets pane states correctly."""
        # Set a pane as maximized
        app._maximize_pane(app.user_prompt_pane)
        assert app.pane_states[app.user_prompt_pane] == PaneState.MAXIMIZED

        # Restore all panes
        app._restore_all_panes()
        assert app.pane_states[app.user_prompt_pane] == PaneState.NORMAL

    def test_get_pane_name(self, app):
        """Test getting pane display names."""
        assert app._get_pane_name(app.user_prompt_pane) == "User Prompt"
        assert app._get_pane_name(app.system_prompt_pane) == "System Prompt"
        assert app._get_pane_name(app.context_pane) == "Context"
        assert app._get_pane_name(app.llm_selection_pane) == "LLM Selection"
        assert app._get_pane_name(app.response_pane) == "Response"

    def test_get_pane_row(self, app):
        """Test getting pane row indices."""
        # Row 0: User Prompt and System Prompt
        assert app._get_pane_row(app.user_prompt_pane) == 0
        assert app._get_pane_row(app.system_prompt_pane) == 0

        # Row 1: Context and LLM Selection
        assert app._get_pane_row(app.context_pane) == 1
        assert app._get_pane_row(app.llm_selection_pane) == 1

        # Row 2: Response
        assert app._get_pane_row(app.response_pane) == 2

    def test_pane_list(self, app):
        """Test that _get_pane_list returns all panes in order."""
        panes = app._get_pane_list()
        assert len(panes) == 5

        pane_objects, pane_names = zip(*panes)

        assert app.user_prompt_pane in pane_objects
        assert app.system_prompt_pane in pane_objects
        assert app.context_pane in pane_objects
        assert app.llm_selection_pane in pane_objects
        assert app.response_pane in pane_objects

        assert "User Prompt" in pane_names
        assert "System Prompt" in pane_names
        assert "Context" in pane_names
        assert "LLM Selection" in pane_names
        assert "Response" in pane_names
