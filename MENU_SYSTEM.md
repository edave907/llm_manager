# Menu System Documentation

## Overview

The LLM Manager now includes a hierarchical dropdown menu system for managing panes. Press **ESC** to open the menu.

## Menu Features

### Opening the Menu
- **Keyboard Shortcut**: `ESC`
- Opens a modal dialog with pane management options
- Shows real-time status of all panes

### Menu Structure

#### 1. All Panes Section
Lists all 5 panes with their current status:

- **User Prompt**
- **System Prompt**
- **Context**
- **LLM Selection**
- **Response**

Each pane shows one of these status indicators:
- `👁 Visible` - Pane is currently visible
- `📌 Maximized` - Pane is maximized (fills screen)
- `📉 Minimized` - Pane is minimized (title bar only)
- `🔒 Hidden` - Pane is completely hidden

#### 2. Actions Section
Available actions:
- **📋 Select/Focus Pane** - Focus the highlighted pane
- **🔒 Hide Selected Pane** - Hide the currently highlighted pane
- **👁 Unhide Selected Pane** - Show the currently highlighted pane
- **🔄 Show All Panes** - Restore all hidden panes

## Usage

### Navigating the Menu
1. Press `ESC` to open the menu
2. Use `↑` / `↓` arrow keys to navigate
3. Press `Enter` to select an option
4. Press `ESC` or `Q` to close the menu

### Selecting a Pane
1. Navigate to a pane in the "All Panes" section
2. Press `Enter` to:
   - **If hidden**: Unhide the pane
   - **If visible**: Focus the pane and close menu

### Hiding a Pane
1. Navigate to the pane you want to hide
2. Navigate down to "🔒 Hide Selected Pane"
3. Press `Enter`
4. The pane will be hidden and menu will refresh

### Unhiding a Pane
1. Navigate to a hidden pane (marked with 🔒)
2. Navigate down to "👁 Unhide Selected Pane"
3. Press `Enter`
4. The pane will become visible and menu will refresh

### Show All Panes
1. Navigate to "🔄 Show All Panes"
2. Press `Enter`
3. All hidden panes will become visible
4. Menu will close

## Integration with Other Features

The menu system works seamlessly with:
- **Maximize** (`m` key) - Status shown in menu
- **Minimize** (`n` key) - Status shown in menu
- **Resize** (`Ctrl+↑`/`Ctrl+↓`) - Works on visible panes
- **Focus shortcuts** (keys `1-5`) - Works on visible panes

## Implementation Details

### Files Created
- `src/llm_manager/gui/menu.py` - Menu screen component

### Files Modified
- `src/llm_manager/gui/main_window.py` - Added menu action and ESC binding
- `src/llm_manager/gui/help_screen.py` - Added menu documentation
- `README.md` - Updated with menu features

### Tests
- `tests/test_menu.py` - Unit tests for menu functionality
- All existing tests pass: **44 passed, 2 skipped**

## Technical Notes

- Menu uses Textual's `ModalScreen` for overlay display
- Pane visibility controlled via `styles.display` property
- Menu auto-refreshes after hide/unhide operations
- PaneState enum accessible to menu for status display
