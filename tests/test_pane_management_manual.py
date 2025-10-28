#!/usr/bin/env python3
"""Manual test script for pane management functionality.

This script verifies the pane management features work correctly.
Run this script and interact with the app to test:

1. Press 'm' on different panes to maximize/restore them
2. Press 'n' on different panes to minimize/restore them
3. Press Ctrl+Up/Down to cycle through all pane sizes
4. Press ESC to open the pane management menu
5. Verify the keyboard shortcuts work as expected

Press 'q' to quit when done testing.
"""

from llm_manager.gui.main_window import run_app


if __name__ == "__main__":
    print("Starting LLM Manager with pane management features...")
    print("\nTest the following:")
    print("1. Focus a pane (1-5) and press 'm' to maximize it")
    print("2. Press 'm' again to restore")
    print("3. Press 'n' to minimize a pane")
    print("4. Press 'n' again to restore")
    print("5. Press Ctrl+Up to cycle: Min→Norm→2x→3x→Max→Min")
    print("6. Press Ctrl+Down to cycle: Max→3x→2x→Norm→Min→Max")
    print("\n=== Menu System ===")
    print("7. Press ESC to open the pane management menu")
    print("8. Navigate with Up/Down arrows")
    print("9. Select a pane to focus it")
    print("10. Use 'Hide Selected Pane' action to hide highlighted pane")
    print("11. Use 'Unhide Selected Pane' action to unhide highlighted pane")
    print("12. Use 'Show All Panes' to restore all hidden panes")
    print("\n13. Press '?' to see all keyboard shortcuts")
    print("\nPress 'q' to quit when done testing.\n")

    run_app()
