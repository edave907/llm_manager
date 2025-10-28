# LLM Manager - Project Requirements & Implementation Plan

## Project Overview
A text-based GUI application for managing and interacting with Large Language Models, built with Textual TUI framework.

## Requirements

### 1. Text-Based Window Manager
- Implement using Textual framework
- Support for panes with docking/undocking functionality
- Works with tmux for terminal management

### 2. Initial Panes
The application includes five main panes:
- **User Prompt Pane**: For entering user prompts to send to LLMs
- **System Prompt Pane**: For defining system-level prompts/instructions
- **Context Pane**: For managing context that will be sent to LLMs
- **LLM Selection Pane**: For browsing and selecting language models
- **Response Pane**: For displaying LLM responses with streaming support

### 3. Editor Integration
- Each pane content is editable via nvim editor
- Seamless integration between TUI and nvim

### 4. Persistence
- All pane contents persist between sessions
- Content automatically saved and restored

## Implementation Status

### Phase 1: Project Setup & Exploration ✅ COMPLETED
1. ✅ Explored the generic_agent project for patterns (settings, persistence)
2. ✅ Updated pyproject.toml with Textual, pydantic, pydantic-settings
3. ✅ Set up basic project configuration

### Phase 2: Core TUI Framework ✅ COMPLETED
4. ✅ Created Textual-based main window with pane layout
5. ✅ Implemented three panes as Textual widgets (EditablePane)
6. ✅ Set up window manager with horizontal/vertical layout

### Phase 3: Editor Integration ✅ COMPLETED
7. ✅ Added nvim integration for editing pane content
8. ✅ Implemented seamless transitions using app.suspend()

### Phase 4: Persistence Layer ✅ COMPLETED
9. ✅ Implemented file-based persistence in `~/.llm_manager/data/`
10. ✅ Added auto-save on edit and auto-restore on load
11. ✅ Created PaneStorage and PaneManager classes

### Phase 5: Advanced Features ✅ COMPLETED
12. ⚠️ Basic docking/undocking stub (notification only)
13. ⏳ TODO: Full docking/undocking with layout changes
14. ✅ Keyboard shortcuts implemented (1, 2, 3, 4, 5, e, Enter, s, c, Ctrl+E, Ctrl+I, q)

## Architecture

### File Structure
```
src/llm_manager/
├── __init__.py
├── __main__.py          # Entry point for python -m
├── main.py              # Main entry point
├── core/
│   ├── settings.py      # Configuration with pydantic-settings
│   ├── persistence.py   # PaneStorage and PaneManager
│   ├── models.py        # Model configuration and registry
│   ├── llm_client.py    # LLM API integration (OpenAI, Anthropic)
│   └── conversation.py  # Conversation history management
├── gui/
│   ├── pane.py          # EditablePane widget
│   ├── llm_pane.py      # LLM selection widget
│   ├── response_pane.py # Response display widget
│   └── main_window.py   # LLMManagerApp (main Textual app)
└── utils/
    └── __init__.py
```

### Key Components

1. **Settings** (core/settings.py):
   - Uses pydantic-settings for configuration
   - Supports .env file overrides
   - Manages paths for data storage

2. **Persistence** (core/persistence.py):
   - PaneStorage: Individual pane file I/O
   - PaneManager: Manages all pane storages

3. **EditablePane** (gui/pane.py):
   - Custom Textual widget
   - nvim integration via subprocess
   - Auto-save on edit

4. **LLMManagerApp** (gui/main_window.py):
   - Main Textual application
   - Layout management
   - Keyboard shortcuts

## Reference Projects
- **generic_agent**: Located at ../generic_agent - reference for patterns and implementation details

## Usage

Run the application:
```bash
llm-manager
# or
python -m llm_manager
```

Keyboard shortcuts:
- `1`, `2`, `3`, `4`, `5` - Focus panes (User Prompt, System Prompt, Context, LLM Selection, Response)
- `e` - Edit in nvim
- `Enter` - Send prompt to LLM / Select model
- `s` - Toggle streaming mode
- `c` - Clear response
- `Ctrl+E` - Export conversation
- `Ctrl+I` - Import conversation
- `d` - Dock/undock (stub)
- `q` - Quit

## LLM Integration ✅ COMPLETED

### Phase 6: LLM Selection and Communication
- ✅ Model configuration module
- ✅ LLM client for OpenAI and Anthropic
- ✅ LLM selection pane with model browser
- ✅ API key configuration in settings
- ✅ Model persistence across sessions
- ✅ Support for 7+ models (GPT-4o, Claude 3.5, etc.)

### Phase 7: LLM Communication & Response Handling ✅ COMPLETED
- ✅ Send prompts to LLM with Enter key
- ✅ Response pane for displaying LLM output
- ✅ Streaming responses with real-time display
- ✅ Toggle streaming mode on/off
- ✅ Clear response functionality
- ✅ Status bar showing current state
- ✅ Error handling and display

### Phase 8: Conversation History ✅ COMPLETED
- ✅ Automatic conversation tracking
- ✅ Persist conversation history to JSON
- ✅ Export conversations to JSON/text format
- ✅ Import conversations from JSON
- ✅ Configurable history size limit
- ✅ Timestamped conversation turns

### Available Models

**OpenAI:**
- GPT-4o
- GPT-4o Mini
- GPT-4 Turbo
- GPT-3.5 Turbo

**Anthropic:**
- Claude 3.5 Sonnet
- Claude 3 Opus
- Claude 3 Haiku

## Future Enhancements

1. **Full Docking/Undocking**: Implement actual layout changes for undocked panes
2. **Themes**: Support for custom color themes
3. **Pane Resizing**: Allow users to resize panes dynamically
4. **Token Counting**: Display token counts for prompts
5. **Multi-turn Conversations**: Support for back-and-forth conversation threads
6. **Response Formatting**: Better markdown/code rendering in response pane
7. **Search History**: Search through conversation history
8. **Model Comparison**: Send same prompt to multiple models and compare responses

## Notes
- Last updated: 2025-10-27
- Status: Core functionality, LLM integration, streaming responses, and conversation history complete
- All test suites passing (35 unit/integration tests + TUI functional test)
- Next priority: Enhanced features (themes, token counting, response formatting)
