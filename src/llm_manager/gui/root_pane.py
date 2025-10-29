"""Root pane that contains all child panes in a hierarchical container structure."""

from textual.app import ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import Static, Label
from rich.text import Text


class RootPane(Container, can_focus=True):
    """Root container pane that manages all child panes in a true hierarchy.

    This pane acts as the parent container for all other panes in the application.
    It provides a visual tree display and root-level operations that affect all children.
    """

    DEFAULT_CSS = """
    RootPane {
        height: 1fr;
        border: solid $primary;
    }

    RootPane:focus {
        border: heavy $accent;
    }

    #root-header {
        background: $primary;
        color: $text;
        text-align: center;
        height: 3;
        padding: 1;
    }

    #root-content {
        height: 1fr;
    }
    """

    def __init__(self, child_panes_layout=None, name=None, id=None, classes=None):
        """Initialize the root pane container.

        Args:
            child_panes_layout: Callable that yields the child panes layout
            name: Widget name
            id: Widget ID
            classes: CSS classes
        """
        super().__init__(name=name, id=id, classes=classes)
        self.child_panes_layout = child_panes_layout
        self.child_panes = []  # Will store references to child panes

    def compose(self) -> ComposeResult:
        """Compose the root pane with header and content area.

        The content area contains all child panes in their layout structure.
        """
        header = Vertical(id="root-header")
        header.can_focus = False
        with header:
            yield Label("🌳 Root Pane - Master Control")

        content = Container(id="root-content")
        content.can_focus = False
        with content:
            # Yield child panes using the layout function if provided
            if self.child_panes_layout:
                yield from self.child_panes_layout()

    def hide_all_children(self) -> None:
        """Hide all child panes."""
        for pane in self.child_panes:
            pane.styles.display = "none"

    def show_all_children(self) -> None:
        """Show all child panes."""
        for pane in self.child_panes:
            pane.styles.display = "block"

    def reset_layout(self) -> None:
        """Reset all child panes to their default state."""
        for pane in self.child_panes:
            pane.styles.display = "block"
            pane.remove_class("pane-minimized")

        # Reset row heights
        rows = self.query(".pane-row")
        for row in rows:
            row.styles.height = "1fr"
            row.remove_class("row-hidden")
