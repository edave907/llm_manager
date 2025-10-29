"""Tests for menu system functionality."""

import pytest
from llm_manager.gui.main_window import LLMManagerApp
from llm_manager.gui.menu import PaneMenuScreen


class TestMenuSystem:
    """Test suite for menu system features."""

    @pytest.fixture
    def app(self):
        """Create an app instance for testing."""
        return LLMManagerApp()

    def test_app_has_menu_action(self, app):
        """Test that app has menu action method."""
        assert hasattr(app, 'action_show_pane_menu')
        assert callable(app.action_show_pane_menu)

    def test_pane_state_accessible_to_menu(self, app):
        """Test that PaneState is accessible to menu."""
        assert hasattr(app, 'PaneState')
        assert app.PaneState is not None

    def test_menu_screen_initialization(self, app):
        """Test menu screen can be initialized."""
        menu = PaneMenuScreen(app)
        assert menu.app_ref is app

    def test_all_panes_accessible(self, app):
        """Test that all panes can be accessed."""
        panes = app._get_pane_list()
        assert len(panes) == 6

        pane_names = [name for _, name in panes]
        assert "Root" in pane_names
        assert "User Prompt" in pane_names
        assert "System Prompt" in pane_names
        assert "Context" in pane_names
        assert "LLM Selection" in pane_names
        assert "Response" in pane_names

    def test_child_panes_accessible(self, app):
        """Test that child panes (excluding root) can be accessed."""
        child_panes = app._get_child_panes()
        assert len(child_panes) == 5

        pane_names = [name for _, name in child_panes]
        assert "User Prompt" in pane_names
        assert "System Prompt" in pane_names
        assert "Context" in pane_names
        assert "LLM Selection" in pane_names
        assert "Response" in pane_names

    def test_pane_has_display_style(self, app):
        """Test that panes have display style attribute."""
        for pane, _ in app._get_pane_list():
            # Panes should have a styles attribute
            assert hasattr(pane, 'styles')

    def test_root_pane_exists(self, app):
        """Test that root pane is created."""
        assert hasattr(app, 'root_pane')
        assert app.root_pane is not None
        assert app.root_pane.id == "root-pane"

    def test_root_pane_has_children(self, app):
        """Test that root pane tracks child panes."""
        assert hasattr(app.root_pane, 'child_panes')
        # Initially empty, set during on_mount
        assert isinstance(app.root_pane.child_panes, list)

    def test_root_level_operations_exist(self, app):
        """Test that root-level operation methods exist."""
        assert hasattr(app, 'action_hide_all_children')
        assert callable(app.action_hide_all_children)
        assert hasattr(app, 'action_show_all_children')
        assert callable(app.action_show_all_children)
        assert hasattr(app, 'action_reset_layout')
        assert callable(app.action_reset_layout)
