# LLM Manager - Quick Start Guide

## Installation

1. Navigate to the project directory:
```bash
cd /home/david/projects/ai/llm_manager
```

2. Install the package in development mode:
```bash
pip install -e .
```

## Running the Application

Launch the application using either command:

```bash
llm-manager
```

or

```bash
python -m llm_manager
```

## First Steps

When the application starts, you'll see three panes:

```
┌─────────────────────────────────────────────────────────────┐
│                      LLM Manager                            │
├────────────────────────┬────────────────────────────────────┤
│   User Prompt          │   System Prompt                    │
│                        │                                    │
│   (empty)              │   (empty)                          │
│                        │                                    │
│                        │                                    │
├────────────────────────┴────────────────────────────────────┤
│   Context                                                   │
│                                                             │
│   (empty)                                                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Basic Workflow

1. **Focus a pane**: Press `1`, `2`, or `3` to focus a pane
   - `1` - User Prompt
   - `2` - System Prompt
   - `3` - Context

2. **Edit content**: Press `e` to open the focused pane in nvim
   - Edit your content in nvim
   - Save and quit (`:wq`) to return to the TUI
   - Changes are automatically persisted

3. **Navigate between panes**: Use number keys to switch focus

4. **Quit**: Press `q` to exit the application

## Example Use Case

### Setting up a conversation with an LLM

1. Press `2` to focus System Prompt
2. Press `e` to edit
3. In nvim, type your system prompt:
   ```
   You are a helpful AI assistant specialized in Python programming.
   ```
4. Save and quit (`:wq`)

5. Press `3` to focus Context
6. Press `e` to edit
7. Add any context information:
   ```
   Working on a Django project with Python 3.10
   ```
8. Save and quit (`:wq`)

9. Press `1` to focus User Prompt
10. Press `e` to edit
11. Type your question:
    ```
    How do I create a custom Django middleware?
    ```
12. Save and quit (`:wq`)

All your content is now saved in `~/.llm_manager/data/` and will persist between sessions!

## Keyboard Reference

| Key | Action |
|-----|--------|
| `1` | Focus User Prompt pane |
| `2` | Focus System Prompt pane |
| `3` | Focus Context pane |
| `e` | Edit focused pane in nvim |
| `d` | Toggle dock/undock (placeholder) |
| `q` | Quit application |

## Storage Location

Your pane contents are stored in:
- `~/.llm_manager/data/user_prompt.txt`
- `~/.llm_manager/data/system_prompt.txt`
- `~/.llm_manager/data/context.txt`

You can also edit these files directly with any text editor!

## Tips

1. **Use tmux**: The application works great in tmux for session management
2. **vim keybindings**: All nvim shortcuts and plugins work when editing panes
3. **Persistent**: Your edits are automatically saved - no need to manually save
4. **Backup**: The files are plain text, so you can version control them with git

## Troubleshooting

### "nvim: command not found"

If you don't have nvim installed, you can:

1. Install nvim:
   ```bash
   # Ubuntu/Debian
   sudo apt install neovim

   # MacOS
   brew install neovim
   ```

2. Or change the editor in `.env`:
   ```bash
   EDITOR=vim  # or nano, emacs, etc.
   ```

### Application won't start

Make sure you've installed the dependencies:
```bash
pip install -e .
```

## Next Steps

- Integrate with LLM APIs (coming soon)
- Add response pane for LLM outputs
- Implement full docking/undocking functionality
- Add conversation history tracking

For more details, see the [Project Requirements](PROJECT_REQUIREMENTS.md).
