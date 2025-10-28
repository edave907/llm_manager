#!/bin/bash
# Terminal cleanup script for LLM Manager
# Run this if your terminal gets stuck after TUI tests

echo "Resetting terminal state..."

# Disable mouse tracking modes
printf '\033[?1000l'  # Disable X11 mouse tracking
printf '\033[?1003l'  # Disable all mouse tracking
printf '\033[?1015l'  # Disable urxvt mouse mode
printf '\033[?1006l'  # Disable SGR mouse mode

# Show cursor (in case it's hidden)
printf '\033[?25h'

# Reset alternate screen (in case stuck in it)
printf '\033[?1049l'

# Reset colors and formatting
printf '\033[0m'

# Try to restore sane terminal settings
stty sane 2>/dev/null || true

echo "Terminal state reset complete!"
echo ""
echo "If your terminal is still behaving strangely, try:"
echo "  1. Close and reopen your terminal window"
echo "  2. Run: reset"
echo "  3. Run: stty sane"
