# LLM Manager

A text-based GUI application for managing and interacting with Large Language Models, built with Textual.

## Features

- **Text-Based UI**: Modern terminal interface using Textual framework
- **Five Panes**:
  - User Prompt: For entering user prompts to send to LLMs
  - System Prompt: For defining system-level prompts/instructions
  - Context: For managing context sent to LLMs
  - LLM Selection: For selecting and configuring language models
  - Response: For displaying LLM responses with streaming support
- **In-Place Editing**: Edit text directly in the TUI with multi-line TextArea widgets
- **Visual Focus Indicators**: Highlighted borders and title bars show which pane is active
- **Pane Management**: Maximize, minimize, resize, hide/unhide panes to customize your workspace
- **Menu System**: Hierarchical dropdown menu for pane management (ESC key)
- **Multiple LLM Support**:
  - OpenAI (GPT-4o, GPT-4o Mini, GPT-4 Turbo, GPT-3.5 Turbo)
  - Anthropic (Claude 3.5 Sonnet, Claude 3 Opus, Claude 3 Haiku)
- **LLM Communication**:
  - Send prompts to selected LLM with Enter key
  - Streaming and non-streaming response modes
  - Toggle streaming on/off with 's' key
- **Conversation History**:
  - Automatic conversation tracking and persistence
  - Export conversations to JSON or text format
  - Import previous conversations
- **Dual Editing Modes**:
  - In-place editing with full text editing capabilities (undo/redo, copy/paste, selection)
  - External editor support (nvim) for complex editing tasks
- **Persistent Storage**: All pane contents, model selection, and conversation history automatically saved
- **Keyboard Shortcuts**: Quick navigation, editing, and comprehensive help system

## Installation

```bash
pip install -e .
```

## Usage

Run the application:

```bash
llm-manager
# or
python -m llm_manager
```

### Keyboard Shortcuts

#### Navigation
- `1` - Focus User Prompt pane
- `2` - Focus System Prompt pane
- `3` - Focus Context pane
- `4` - Focus LLM Selection pane
- `5` - Focus Response pane
- `Tab` - Focus next pane (cycles through all panes)
- `Shift+Tab` - Focus previous pane (reverse cycle)
- `Up/Down` - Navigate models (in LLM Selection pane)

#### Editing
- **Type** - Edit text directly in the focused pane
- `Ctrl+S` - Save current pane to disk
- `e` - Open focused pane in external editor (nvim)
- `Ctrl+A` - Select all text
- `Ctrl+C/V` - Copy/Paste
- `Ctrl+Z/Y` - Undo/Redo

#### LLM Communication
- `Enter` - Send prompts to LLM / Select model (context-dependent)
- `s` - Toggle streaming mode on/off
- `c` - Clear response pane

#### Pane Management
- `m` - Toggle maximize/restore focused pane
- `n` - Toggle minimize/restore focused pane
- `Ctrl+Up` - Increase pane size (cycles: Minimized → Normal → 2x → 3x → Maximized → Minimized)
- `Ctrl+Down` - Decrease pane size (cycles: Maximized → 3x → 2x → Normal → Minimized → Maximized)

#### History & Data
- `Ctrl+E` - Export conversation history to JSON file
- `Ctrl+I` - Import conversation history (placeholder)

#### Application
- `ESC` - Open pane management menu (list, select, hide/unhide panes)
- `?` - Show help menu with all keyboard shortcuts
- `q` - Quit application

### Storage Location

Pane contents and configuration are automatically saved to:
- `~/.llm_manager/data/user_prompt.txt`
- `~/.llm_manager/data/system_prompt.txt`
- `~/.llm_manager/data/context.txt`
- `~/.llm_manager/data/selected_model.txt`
- `~/.llm_manager/data/conversation_history.json`

Exported conversations are saved to your home directory with timestamps:
- `~/llm_conversation_YYYYMMDD_HHMMSS.json`

### Configuration

Create a `.env` file in the project root to configure the application:

```bash
# Editor to use (default: nvim)
EDITOR=nvim

# Debug mode
DEBUG=false

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1

# Anthropic Configuration
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Default model (optional)
DEFAULT_MODEL=openai:gpt-4o-mini

# Streaming toggle (optional, default: true)
ENABLE_STREAMING=true

# Conversation history settings (optional)
MAX_HISTORY_ITEMS=100
```

**Note**: You need to set at least one API key to use the LLM features.

## Troubleshooting

### Terminal Issues After Running the Application

If your terminal is behaving strangely (mouse clicks showing as characters, cursor missing, etc.) after running the application, the TUI may have left the terminal in an altered state.

**Quick Fix:**
```bash
./tests/cleanup_terminal.sh
```

**Or manually run:**
```bash
printf '\033[?1000l\033[?1003l\033[?1015l\033[?1006l\033[?25h'
```

**Or simply:**
```bash
reset
```

**Or close and reopen your terminal.**

This can happen if the application exits unexpectedly or tests are interrupted. The test suite now includes automatic cleanup, but this utility is available if needed.

## Development

### Setup
1. Clone the repository
2. Install dependencies: `pip install -e .[dev]`
3. Run tests: `./tests/run_all_tests.sh` (includes automatic terminal cleanup)

### Testing
- **All tests**: `./tests/run_all_tests.sh`
- **Unit tests only**: `pytest tests/ -v`
- **TUI test**: `./tests/test_tui.exp`
- **Live API tests**: `python tests/test_live_api.py` (requires API keys)

## License

TBD
