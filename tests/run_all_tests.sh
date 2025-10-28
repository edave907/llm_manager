#!/bin/bash
# Comprehensive test runner for LLM Manager

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$(dirname "$SCRIPT_DIR")"

# Cleanup function to reset terminal state
cleanup_terminal() {
    # Disable all mouse tracking modes
    printf '\033[?1000l\033[?1003l\033[?1015l\033[?1006l'
    # Show cursor (in case it's hidden)
    printf '\033[?25h'
    # Reset colors and formatting
    printf '\033[0m'
    # Try to restore sane terminal settings
    stty sane 2>/dev/null || true
}

# Trap cleanup on exit, interrupt, or termination
trap cleanup_terminal EXIT INT TERM

echo "=========================================="
echo "LLM Manager - Comprehensive Test Suite"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

run_test() {
    local test_name="$1"
    local test_command="$2"

    TOTAL_TESTS=$((TOTAL_TESTS + 1))

    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test: $test_name"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

    if eval "$test_command"; then
        echo -e "${GREEN}✓ PASSED${NC}: $test_name"
        PASSED_TESTS=$((PASSED_TESTS + 1))
    else
        echo -e "${RED}✗ FAILED${NC}: $test_name"
        FAILED_TESTS=$((FAILED_TESTS + 1))
    fi

    echo ""
}

echo "Starting test suite..."
echo ""

# Unit tests - Persistence
run_test "Persistence Unit Tests" "python -m pytest tests/test_persistence.py -v"

# Unit tests - Settings
run_test "Settings Unit Tests" "python -m pytest tests/test_settings.py -v"

# Integration tests
run_test "Integration Tests" "python -m pytest tests/test_integration.py -v"

# Manual persistence test
run_test "Manual Persistence Test" "python tests/test_persistence_manual.py"

# TUI functional test (expect)
run_test "TUI Functional Test" "./tests/test_tui.exp"

# Note about nvim test
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${YELLOW}Note: nvim Integration Test${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "The nvim integration test requires interactive terminal control"
echo "and cannot be fully automated with expect. To test nvim integration:"
echo "  1. Run: llm-manager"
echo "  2. Press '1' to focus User Prompt"
echo "  3. Press 'e' to edit in nvim"
echo "  4. Make changes and save (:wq)"
echo "  5. Verify changes appear in the pane"
echo ""

# Summary
echo "=========================================="
echo "Test Summary"
echo "=========================================="
echo -e "Total tests:  $TOTAL_TESTS"
echo -e "${GREEN}Passed tests: $PASSED_TESTS${NC}"
if [ $FAILED_TESTS -gt 0 ]; then
    echo -e "${RED}Failed tests: $FAILED_TESTS${NC}"
else
    echo -e "Failed tests: $FAILED_TESTS"
fi
echo "=========================================="

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Terminal state has been reset."
    exit 0
else
    echo -e "${RED}✗ Some tests failed${NC}"
    echo ""
    echo "Terminal state has been reset."
    exit 1
fi
