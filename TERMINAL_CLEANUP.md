# Terminal Cleanup for LLM Manager

## Problem

The LLM Manager TUI application uses Textual, which enables various terminal modes including:
- Mouse tracking (for mouse interaction)
- Alternate screen buffer
- Cursor visibility changes
- Other terminal state modifications

If the application exits unexpectedly or is interrupted, these terminal modes may not be properly disabled, causing issues like:
- Mouse clicks appearing as escape sequences/characters
- Missing or invisible cursor
- Strange terminal behavior

## Solution

We've implemented multiple layers of protection:

### 1. Automatic Cleanup in Test Scripts

**test_tui.exp**: Now includes cleanup functions that automatically reset terminal state
```bash
./tests/test_tui.exp
```

**run_all_tests.sh**: Includes trap handlers to ensure cleanup even if tests fail
```bash
./tests/run_all_tests.sh
```

### 2. Manual Cleanup Script

If your terminal gets stuck, run:
```bash
./tests/cleanup_terminal.sh
```

This script:
- Disables all mouse tracking modes
- Shows the cursor
- Resets colors and formatting
- Restores sane terminal settings

### 3. Quick Manual Fix

You can also run these commands directly:

**Fastest fix:**
```bash
reset
```

**If reset fails (terminal device error), use this combination:**
```bash
# Disable mouse tracking
printf '\033[?1000l\033[?1003l\033[?1015l\033[?1006l'

# Clear screen and reset cursor
clear
# or if clear doesn't work:
printf '\033[2J\033[H'

# Restore sane terminal settings
stty sane
```

**Or manually reset terminal modes:**
```bash
printf '\033[?1000l\033[?1003l\033[?1015l\033[?1006l\033[?25h'
```

**Or restore terminal settings:**
```bash
stty sane
```

**Or simply close and reopen your terminal.**

## Escape Sequences Explained

The cleanup commands disable these terminal features:

- `\033[?1000l` - Disable X11 mouse tracking
- `\033[?1003l` - Disable all mouse motion tracking
- `\033[?1015l` - Disable urxvt mouse mode
- `\033[?1006l` - Disable SGR extended mouse mode
- `\033[?25h` - Show cursor
- `\033[0m` - Reset colors/formatting
- `\033[2J` - Clear entire screen
- `\033[H` - Move cursor to home position (top-left)
- `\033c` - Full terminal reset (alternative to `reset` command)

## Prevention

To prevent terminal state issues:

1. Always quit the application properly with 'q' key
2. Use the test scripts which include automatic cleanup
3. If developing, ensure proper cleanup in exit handlers

## Testing

The test suite now includes automatic cleanup:
```bash
# Run all tests with automatic cleanup
./tests/run_all_tests.sh

# TUI test with cleanup
./tests/test_tui.exp
```

Both scripts will reset terminal state even if tests fail or are interrupted.
