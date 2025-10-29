# LLM Manager - Pane Navigation & Key Bindings Documentation

## Hierarchical Pane Structure

```
Application (LLMManagerApp)
├── Header
├── Root Pane (RootPane) [ID: root-pane]
│   └── Content Container [ID: root-content]
│       ├── Row 1 (Horizontal) [class: pane-row]
│       │   ├── User Prompt (EditablePane) [ID: user-prompt-pane]
│       │   └── System Prompt (EditablePane) [ID: system-prompt-pane]
│       ├── Row 2 (Horizontal) [class: pane-row]
│       │   ├── Context (EditablePane) [ID: context-pane]
│       │   └── LLM Selection (LLMSelectionPane) [ID: llm-selection-pane]
│       └── Row 3 (Vertical) [class: pane-row]
│           └── Response (ResponsePane) [ID: response-pane]
└── Footer
```

### Pane Order for Sequential Navigation
1. Root Pane (index 0)
2. User Prompt (index 1)
3. System Prompt (index 2)
4. Context (index 3)
5. LLM Selection (index 4)
6. Response (index 5)

---

## Navigation Methods

### 1. Direct Numeric Keys (BINDINGS lines 86-91)
Direct jump to specific panes using number keys:

| Key | Target Pane      | Action Method               | Line |
|-----|------------------|-----------------------------|------|
| `6` | Root Pane        | `action_focus_root()`       | 86   |
| `1` | User Prompt      | `action_focus_user_prompt()` | 87   |
| `2` | System Prompt    | `action_focus_system_prompt()` | 88   |
| `3` | Context          | `action_focus_context()`    | 89   |
| `4` | LLM Selection    | `action_focus_llm_selection()` | 90   |
| `5` | Response         | `action_focus_response()`   | 91   |

**Implementation:** Each action method (lines 222-244) directly calls `.focus()` on the target pane.

### 2. Sequential Navigation (BINDINGS lines 92-93)
Cycle through panes in order:

| Key         | Direction | Action Method          | Line |
|-------------|-----------|------------------------|------|
| `Tab`       | Forward   | `action_focus_next()`  | 92   |
| `Shift+Tab` | Backward  | `action_focus_previous()` | 93   |

**Implementation:**
- `action_focus_next()` (lines 288-296): Finds current pane index, increments with wraparound
- `action_focus_previous()` (lines 298-306): Finds current pane index, decrements with wraparound
- Both use `_find_current_pane_index()` (lines 267-286) which walks up the widget tree from focused widget

**Algorithm:**
1. Get focused widget
2. Walk up parent chain to find which pane contains it
3. Move to next/previous in `_get_pane_list()` order
4. Wrap around at ends (modulo operation)

### 3. Menu-Based Navigation (BINDING line 85)
Open pane management menu:

| Key  | Action Method           | Line |
|------|-------------------------|------|
| `ESC` | `action_show_pane_menu()` | 85   |

**Implementation:** Opens `PaneMenuScreen` modal (line 562-564)

---

## Key Bindings by Category

### Application-Level Controls (lines 83-84)
| Key | Action              | Method              | Show in Footer | Line |
|-----|---------------------|---------------------|----------------|------|
| `?` | Show Help Screen    | `action_show_help()` | Yes            | 83   |
| `q` | Quit Application    | `action_quit()`     | Yes            | 84   |

### Pane Editing (lines 94-96)
| Key      | Action                  | Method                     | Show in Footer | Line |
|----------|-------------------------|----------------------------|----------------|------|
| `e`      | Edit in nvim            | `action_edit_focused()`    | Yes            | 94   |
| `Ctrl+S` | Save current pane       | `action_save_focused()`    | Yes            | 95   |
| `p`      | Open Prompt Manager     | `action_open_prompt_manager()` | Yes        | 96   |

**Edit Mode (within panes):**
- `i`: Enter edit mode (handled by EditablePane, pane.py:211)
- `ESC`: Exit edit mode (handled by EditablePane, pane.py:216)
- Text editing available while in edit mode

### Pane Layout Management (lines 102-108)
| Key        | Action                | Method                     | Show in Footer | Line |
|------------|-----------------------|----------------------------|----------------|------|
| `m`        | Toggle Maximize       | `action_toggle_maximize()` | Yes            | 102  |
| `n`        | Toggle Minimize       | `action_toggle_minimize()` | Yes            | 103  |
| `Ctrl+↑`   | Increase Height       | `action_increase_height()` | No             | 104  |
| `Ctrl+↓`   | Decrease Height       | `action_decrease_height()` | No             | 105  |
| `Ctrl+H`   | Hide All Children     | `action_hide_all_children()` | No           | 106  |
| `Ctrl+Shift+H` | Show All Children | `action_show_all_children()` | No           | 107  |
| `Ctrl+R`   | Reset Layout          | `action_reset_layout()`    | No             | 108  |

### LLM Operations (lines 97-101)
| Key      | Action                    | Method                       | Show in Footer | Line |
|----------|---------------------------|------------------------------|----------------|------|
| `Ctrl+J` | Send to LLM               | `action_send_to_llm()`       | Yes (priority) | 97   |
| `s`      | Toggle Streaming Mode     | `action_toggle_streaming()`  | No             | 98   |
| `c`      | Clear Response            | `action_clear_response()`    | No             | 99   |
| `Ctrl+E` | Export Conversation       | `action_export_conversation()` | No           | 100  |
| `Ctrl+I` | Import Conversation       | `action_import_conversation()` | No           | 101  |

---

## Pane Management Menu System

### Menu Access
**Trigger:** Press `ESC` → Opens `PaneMenuScreen` (menu.py)

### Menu Structure (menu.py lines 83-131)

```
Pane Management Menu
├── [Pane Hierarchy Section]
│   ├── 🌳 Root (selectable)
│   ├──   ├─ User Prompt (status indicator)
│   ├──   ├─ System Prompt (status indicator)
│   ├──   ├─ Context (status indicator)
│   ├──   ├─ LLM Selection (status indicator)
│   └──   └─ Response (status indicator)
├── [Pane Actions Section]
│   ├── 📋 Select/Focus Pane
│   ├── 🔒 Hide Selected Pane
│   └── 👁 Unhide Selected Pane
└── [Root Actions Section]
    ├── 🌳 Hide All Children
    ├── 🌳 Show All Children
    └── 🌳 Reset Layout
```

### Status Indicators (menu.py lines 94-108)
- `🔒 Hidden` - Pane display is "none" (dim style)
- `📌 Maximized` - Pane is maximized (bold green)
- `📉 Minimized` - Pane is in minimized state (yellow)
- `👁 Visible` - Pane is visible and normal (white)

### Menu Actions (menu.py lines 135-161)

#### Individual Pane Selection (lines 143-146)
- Selecting a pane: If visible → focuses it and closes menu
- Selecting a pane: If hidden → unhides it and shows notification

#### Pane Actions (lines 147-152)
- **Select/Focus:** Close menu (return to focused pane)
- **Hide:** Hide the currently highlighted pane
- **Unhide:** Unhide the currently highlighted pane

#### Root Actions (lines 153-161)
- **Hide All Children:** `root_pane.hide_all_children()` - Sets display="none" on all child panes
- **Show All Children:** `root_pane.show_all_children()` - Sets display="block" on all child panes
- **Reset Layout:** `root_pane.reset_layout()` - Restores all default states

---

## Focus Management System

### Focus Determination
**Algorithm:** `_find_current_pane_index()` (main_window.py lines 267-286)

1. Get currently focused widget via `self.focused`
2. Walk up parent chain using `widget.parent`
3. At each level, check if widget matches any pane in `_get_pane_list()`
4. Return index when match found
5. Default to index 0 (Root) if not found

**Example Traversal:**
```
TextArea (focused)
  → EditablePane (pane-content)
    → EditablePane (user-prompt-pane) ← Match found! Return index 1
      → Horizontal (pane-row)
        → Container (root-content)
          → RootPane
```

### Focus Methods by Pane Type

#### EditablePane (User, System, Context) - pane.py
- **Command Mode** (default): Pane has focus, TextArea does not
  - Press `i`: Enter edit mode
  - Key bindings: `e` (nvim), `Ctrl+S` (save), `1-6` (nav), etc.

- **Edit Mode**: TextArea has focus
  - Press `ESC`: Exit to command mode
  - Text editing keys active
  - Most app key bindings suppressed

#### LLMSelectionPane - llm_pane.py
- Focus: Entire pane container
- Arrow keys: Navigate model list
- Enter: Select model

#### ResponsePane - response_pane.py
- Focus: Read-only pane
- Key bindings: `s` (streaming), `c` (clear), etc.

#### RootPane - root_pane.py
- Focus: Master container
- Key bindings: All root-level operations
- Child panes visible/accessible within

---

## Pane States (PaneState Enum - main_window.py lines 25-29)

### State Definitions
```python
class PaneState(Enum):
    NORMAL = "normal"      # Default: 1fr height, visible
    MAXIMIZED = "maximized" # Full screen, others hidden
    MINIMIZED = "minimized" # 3-line height, content hidden
```

### State Tracking
- **Storage:** `self.pane_states` dictionary (line 124)
- **Maximized Tracking:** `self.maximized_pane` (line 125)
- **Initialized:** On mount for each pane (lines 206-208)

### State Transitions

#### Maximize/Minimize Toggle (lines 592-636)

**Maximize (`m` key):**
```
Normal → Maximized: Hide other rows, hide siblings in same row
Maximized → Normal: Restore all panes
```

**Minimize (`n` key):**
```
Normal → Minimized: Add "pane-minimized" class
Minimized → Normal: Remove "pane-minimized" class
```

#### Height Cycling (lines 677-773)

**Increase Height (`Ctrl+↑`):**
```
Minimized → Normal (1fr) → 2fr → 3fr → Maximized → [wraps to] Minimized
```

**Decrease Height (`Ctrl+↓`):**
```
Maximized → 3fr → 2fr → Normal (1fr) → Minimized → [wraps to] Maximized
```

**Implementation:**
- Height applied to parent row container (`.pane-row`)
- Uses Textual's fraction-based height (`1fr`, `2fr`, `3fr`)
- Maximized hides other rows entirely

---

## Pane Row Organization (main_window.py lines 578-590)

### Row Index Mapping
**Method:** `_get_pane_row(pane)` returns row index or None

| Pane(s)                        | Row Index | Container Type |
|--------------------------------|-----------|----------------|
| User Prompt, System Prompt    | 0         | Horizontal     |
| Context, LLM Selection         | 1         | Horizontal     |
| Response                       | 2         | Vertical       |
| Root Pane                      | None      | (contains rows) |

### Row Visibility Control
- CSS class: `.row-hidden` (CSS line 77-79)
- Applied during maximize operations
- Affects entire row container and all children

---

## Context-Aware Action Handlers

### Edit-Related Actions (lines 308-350)
These actions walk up the widget tree to find which pane is focused:

**Edit with nvim (`e` key):** `action_edit_focused()`
```python
Walk tree → Find EditablePane → Call edit_with_nvim()
```

**Save (`Ctrl+S`):** `action_save_focused()`
```python
Walk tree → Find EditablePane → Call save_content()
```

**Algorithm (lines 313-326):**
1. Start with `focused` widget
2. Walk up parents with `current = current.parent`
3. Check if `current is self.user_prompt_pane` (or system/context)
4. Call appropriate method when match found
5. Show warning if no editable pane found

### Prompt Manager (`p` key) - lines 463-498
**Similar tree walking:**
1. Identify which pane is focused (User/System/Context only)
2. Get current content from pane
3. Open `PromptManagerScreen` modal with pane context
4. Handle result with `_handle_prompt_manager_result()`

**Supported Panes:** User Prompt, System Prompt, Context
**Unsupported:** LLM Selection, Response, Root

---

## Prompt Manager Integration

### Load Modes (prompt_manager_screen.py lines 296-384)
When loading a prompt file:

| Mode      | Behavior                                   | Key Shortcut |
|-----------|--------------------------------------------|--------------|
| Replace   | Replace entire pane content                | `R`          |
| Append    | Add to end of current content              | `A`          |
| Insert    | Insert at current cursor position          | `I`          |

**Cursor Position Calculation (lines 531-548):**
```python
cursor = text_area.cursor_location  # (row, column)
lines = current_text.split('\n')
position = sum(len(line) + 1 for line in lines[:cursor[0]]) + cursor[1]
new_text = current_text[:position] + new_content + current_text[position:]
```

### Save Operation (lines 552-556)
- Saves current pane content to selected file
- File stored in `settings.PROMPTS_DIR`
- Auto-adds `.txt` extension if missing

---

## Layout Reset Operations

### Individual Pane Reset
**Via Root Pane:** `root_pane.reset_layout()` (root_pane.py lines 79-89)
```python
for pane in child_panes:
    pane.styles.display = "block"
    pane.remove_class("pane-minimized")

for row in rows:
    row.styles.height = "1fr"
    row.remove_class("row-hidden")
```

### Application-Level Reset
**Action:** `action_reset_layout()` (main_window.py lines 783-796)
```python
1. Restore from maximized state if any
2. Call root_pane.reset_layout()
3. Reset all pane states to NORMAL in self.pane_states
```

### Hide/Show All Operations (lines 775-781)
- **Hide All:** `root_pane.hide_all_children()` → display="none" on all children
- **Show All:** `root_pane.show_all_children()` → display="block" on all children

---

## Key Binding Priorities

### Priority Flag (BINDINGS)
Bindings with `priority=True` are handled first:

| Key      | Action                  | Priority | Line |
|----------|-------------------------|----------|------|
| `Tab`    | Focus Next              | True     | 92   |
| `Shift+Tab` | Focus Previous       | True     | 93   |
| `Ctrl+J` | Send to LLM             | True     | 97   |

**Effect:** These keys are captured at app level before widgets can handle them.

### Conflict Resolution
**EditablePane ESC Binding** (pane.py line 42):
```python
Binding("escape", "exit_edit_mode", "Exit Edit Mode", priority=True)
```

**When ESC is pressed:**
1. If in edit mode in pane → Exit edit mode (pane.py)
2. If in command mode → Show pane menu (main_window.py)

**Handled by:** Event bubbling and `event.stop()` (pane.py line 219)

---

## CSS Classes for Pane States

### Pane-Level Classes (main_window.py lines 48-72)

| Class             | Effect                                      | Applied By          |
|-------------------|---------------------------------------------|---------------------|
| `.pane-minimized` | height:3, max-height:3, hide TextArea/footer | toggle_minimize()   |
| `.row-hidden`     | display:none (entire row or pane)           | maximize operations |
| `.pane-focused`   | Heavy accent border                         | on_focus()          |

### Per-Widget Hiding (lines 53-71)
When `.pane-minimized` applied:
- `TextArea` → display:none
- `.pane-footer` → display:none
- `.response-content` → display:none
- `.status-bar` → display:none
- `.model-list` → display:none
- `.model-info` → display:none

---

## Implementation Notes

### Pane List Methods

**`_get_pane_list()`** (lines 246-255)
- Returns ALL panes including Root
- Used for sequential navigation (Tab/Shift+Tab)
- Order: Root → User → System → Context → LLM → Response

**`_get_child_panes()`** (lines 257-265)
- Returns ONLY child panes (excludes Root)
- Used for operations on children only
- Order: User → System → Context → LLM → Response

### Maximization Logic (lines 637-668)

**Hide other rows:**
```python
for idx, container in enumerate(containers):
    if idx != target_row_idx:
        container.add_class("row-hidden")
```

**Hide siblings in same row:**
```python
pane_row = containers[target_row_idx]
for child in pane_row.children:
    if child != pane:
        child.add_class("row-hidden")
```

**Restore all:**
```python
for container in containers:
    container.remove_class("row-hidden")
for pane in all_panes:
    pane.remove_class("row-hidden")
```

---

## File References

| Component          | File Path                                    | Key Lines  |
|--------------------|----------------------------------------------|------------|
| Main Window        | `src/llm_manager/gui/main_window.py`        | Full file  |
| Root Pane          | `src/llm_manager/gui/root_pane.py`          | 1-90       |
| Editable Pane      | `src/llm_manager/gui/pane.py`               | 38-303     |
| LLM Selection Pane | `src/llm_manager/gui/llm_pane.py`           | -          |
| Response Pane      | `src/llm_manager/gui/response_pane.py`      | -          |
| Pane Menu          | `src/llm_manager/gui/menu.py`               | 12-218     |
| Help Screen        | `src/llm_manager/gui/help_screen.py`        | 10-174     |
| Prompt Manager     | `src/llm_manager/gui/prompt_manager_screen.py` | 14-425  |

---

## Summary

### Navigation Paradigm
LLM Manager uses a **hierarchical pane system** with:
- **Root pane** as master container
- **5 child panes** organized in 3 rows
- **Multiple navigation methods**: Direct keys (1-6), sequential (Tab), menu (ESC)
- **Modal editing** in text panes (vim-style i/ESC pattern)

### Key Design Principles
1. **Hierarchical Focus:** Widget tree walking for context-aware actions
2. **State Preservation:** Explicit tracking of pane states (normal/minimized/maximized)
3. **Flexible Layout:** Dynamic height adjustment (1fr/2fr/3fr) and maximize/minimize
4. **Root Operations:** Master container provides app-wide layout control
5. **Context Awareness:** Actions apply to focused pane via tree traversal

### User Experience
- **Discoverability:** Help screen (`?`), menu system (ESC)
- **Flexibility:** Multiple ways to navigate (keys, Tab, menu)
- **Power User:** Direct numeric keys, vim-like modal editing
- **Visual Feedback:** Status indicators in menu, focused pane highlighting
