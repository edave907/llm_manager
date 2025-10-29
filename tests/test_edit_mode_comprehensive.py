"""Comprehensive tests for edit mode entry via keyboard and mouse."""

import pytest
from textual.widgets import TextArea
from llm_manager.gui.pane import EditablePane
from pathlib import Path
import tempfile


@pytest.fixture
def temp_file():
    """Create a temporary file for pane storage."""
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
        f.write("Initial content")
        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


@pytest.mark.asyncio
async def test_edit_mode_keyboard_entry(temp_file):
    """Test entering edit mode with 'i' key and exiting with ESC."""
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield EditablePane(
                title="Test Pane",
                storage_path=temp_file,
                id="test-pane"
            )

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the pane
        pane = app.query_one(EditablePane)

        # Initially should be in command mode
        assert pane.edit_mode is False, "Should start in command mode"

        # Focus the pane
        pane.focus()
        await pilot.pause()

        # Press 'i' to enter edit mode
        await pilot.press("i")
        await pilot.pause()

        # Should now be in edit mode
        assert pane.edit_mode is True, "Should be in edit mode after pressing 'i'"

        # Get the TextArea and verify it has focus
        text_area = pane.query_one(TextArea)
        assert text_area.has_focus, "TextArea should have focus in edit mode"

        # Press ESC to exit edit mode
        await pilot.press("escape")
        await pilot.pause()

        # Should be back in command mode
        assert pane.edit_mode is False, "Should be in command mode after pressing ESC"

        # Pane should have focus again
        assert pane.has_focus, "Pane should have focus after exiting edit mode"


@pytest.mark.asyncio
async def test_edit_mode_mouse_entry(temp_file):
    """Test entering edit mode with direct TextArea focus (simulates mouse click) and exiting with ESC."""
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield EditablePane(
                title="Test Pane",
                storage_path=temp_file,
                id="test-pane"
            )

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the pane and text area
        pane = app.query_one(EditablePane)
        text_area = pane.query_one(TextArea)

        # Initially should be in command mode
        assert pane.edit_mode is False, "Should start in command mode"

        # Simulate mouse click by directly focusing the TextArea
        text_area.focus()
        await pilot.pause()

        # The on_focus handler should have set edit_mode to True
        assert pane.edit_mode is True, "Should be in edit mode after focusing TextArea (simulated mouse click)"

        # TextArea should have focus
        assert text_area.has_focus, "TextArea should have focus"

        # Press ESC to exit edit mode
        await pilot.press("escape")
        await pilot.pause()

        # Should be back in command mode
        assert pane.edit_mode is False, "Should be in command mode after pressing ESC"

        # Pane should have focus again
        assert pane.has_focus, "Pane should have focus after exiting edit mode"


@pytest.mark.asyncio
async def test_edit_mode_footer_updates(temp_file):
    """Test that footer updates correctly when entering/exiting edit mode."""
    from textual.app import App, ComposeResult
    from textual.widgets import Label

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield EditablePane(
                title="Test Pane",
                storage_path=temp_file,
                id="test-pane"
            )

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the pane and footer
        pane = app.query_one(EditablePane)
        footer = pane.query_one("#test-pane-footer", Label)

        # Initially should show command mode footer
        initial_text = str(footer.render())
        assert "i: Edit mode" in initial_text, "Footer should show command mode options"

        # Enter edit mode with 'i'
        pane.focus()
        await pilot.pause()
        await pilot.press("i")
        await pilot.pause()

        # Footer should show edit mode
        edit_text = str(footer.render())
        assert "-- EDIT MODE --" in edit_text, "Footer should show edit mode indicator"

        # Exit edit mode with ESC
        await pilot.press("escape")
        await pilot.pause()

        # Footer should show command mode again
        command_text = str(footer.render())
        assert "i: Edit mode" in command_text, "Footer should show command mode options again"


@pytest.mark.asyncio
async def test_edit_mode_typing_and_exit(temp_file):
    """Test typing in edit mode and exiting."""
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield EditablePane(
                title="Test Pane",
                storage_path=temp_file,
                id="test-pane"
            )

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the pane and text area
        pane = app.query_one(EditablePane)
        text_area = pane.query_one(TextArea)

        # Enter edit mode via keyboard
        pane.focus()
        await pilot.pause()
        await pilot.press("i")
        await pilot.pause()

        # Type some text
        await pilot.press("h", "e", "l", "l", "o")
        await pilot.pause()

        # Content should be updated
        assert "hello" in text_area.text, "Text should be typed in edit mode"

        # Exit edit mode
        await pilot.press("escape")
        await pilot.pause()

        # Should be in command mode
        assert pane.edit_mode is False, "Should be in command mode"


@pytest.mark.asyncio
async def test_edit_mode_mouse_then_keyboard_cycle(temp_file):
    """Test cycling between command and edit mode using both methods."""
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            yield EditablePane(
                title="Test Pane",
                storage_path=temp_file,
                id="test-pane"
            )

    app = TestApp()
    async with app.run_test() as pilot:
        # Get the pane and text area
        pane = app.query_one(EditablePane)
        text_area = pane.query_one(TextArea)

        # Start in command mode
        assert pane.edit_mode is False

        # Enter via mouse (direct focus)
        text_area.focus()
        await pilot.pause()
        assert pane.edit_mode is True, "Should enter edit mode via mouse"

        # Exit with ESC
        await pilot.press("escape")
        await pilot.pause()
        assert pane.edit_mode is False, "Should exit edit mode"

        # Enter via keyboard
        await pilot.press("i")
        await pilot.pause()
        assert pane.edit_mode is True, "Should enter edit mode via keyboard"

        # Exit with ESC
        await pilot.press("escape")
        await pilot.pause()
        assert pane.edit_mode is False, "Should exit edit mode"

        # Enter via mouse again
        text_area.focus()
        await pilot.pause()
        assert pane.edit_mode is True, "Should enter edit mode via mouse again"

        # Exit with ESC
        await pilot.press("escape")
        await pilot.pause()
        assert pane.edit_mode is False, "Should exit edit mode"


@pytest.mark.asyncio
async def test_edit_mode_no_auto_exit_on_blur(temp_file):
    """Test that edit mode does NOT automatically exit when pane loses focus."""
    from textual.app import App, ComposeResult

    class TestApp(App):
        def compose(self) -> ComposeResult:
            # Create two panes
            yield EditablePane(
                title="Pane 1",
                storage_path=temp_file,
                id="pane1"
            )
            yield EditablePane(
                title="Pane 2",
                storage_path=temp_file,
                id="pane2"
            )

    app = TestApp()
    async with app.run_test() as pilot:
        # Get both panes
        pane1 = app.query_one("#pane1", EditablePane)
        pane2 = app.query_one("#pane2", EditablePane)

        # Enter edit mode in pane1
        pane1.focus()
        await pilot.pause()
        await pilot.press("i")
        await pilot.pause()

        assert pane1.edit_mode is True, "Pane1 should be in edit mode"

        # Focus pane2 (pane1 loses focus)
        pane2.focus()
        await pilot.pause()

        # Pane1 should STILL be in edit mode (edit_mode flag should remain True)
        # even though it lost focus
        assert pane1.edit_mode is True, "Pane1 should remain in edit mode after losing focus"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
