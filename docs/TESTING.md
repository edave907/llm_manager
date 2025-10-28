# LLM Manager - Testing Documentation

## Test Suite Overview

The LLM Manager project includes a comprehensive test suite covering unit tests, integration tests, and functional tests.

## Test Structure

```
tests/
├── test_persistence.py          # Unit tests for persistence layer
├── test_settings.py              # Unit tests for settings module
├── test_integration.py           # Integration tests
├── test_persistence_manual.py   # Manual persistence verification
├── test_tui.exp                  # Expect script for TUI testing
├── test_nvim_integration.exp    # Expect script for nvim (manual)
└── run_all_tests.sh             # Comprehensive test runner
```

## Running Tests

### Quick Start

Run all tests with a single command:

```bash
./tests/run_all_tests.sh
```

### Individual Test Suites

#### Unit Tests - Persistence

Tests the core persistence layer (PaneStorage and PaneManager):

```bash
python -m pytest tests/test_persistence.py -v
```

**Coverage:**
- File creation and initialization
- Read/write operations
- Multiline content
- Unicode handling
- Content clearing
- Pane independence

#### Unit Tests - Settings

Tests configuration management:

```bash
python -m pytest tests/test_settings.py -v
```

**Coverage:**
- Default settings
- Directory creation
- File initialization
- Content preservation
- Custom editor configuration

#### Integration Tests

Tests interaction between components:

```bash
python -m pytest tests/test_integration.py -v
```

**Coverage:**
- Full workflow (settings → persistence → read/write)
- Empty panes on first run
- Content updates
- Persistence across restarts

#### Manual Persistence Test

Verifies actual file I/O in the real data directory:

```bash
python tests/test_persistence_manual.py
```

**What it tests:**
- Creates files in `~/.llm_manager/data/`
- Writes test content
- Simulates app restart
- Verifies persistence
- Updates and re-verifies

#### TUI Functional Test

Automated TUI testing with expect:

```bash
./tests/test_tui.exp
```

**What it tests:**
- Application startup
- Pane display (User Prompt, System Prompt, Context)
- Footer with keyboard shortcuts
- Pane navigation (keys 1, 2, 3)
- Quit functionality (key q)

## Test Results Summary

### Latest Test Run (2025-10-27)

```
==========================================
Test Summary
==========================================
Total tests:  5
Passed tests: 5
Failed tests: 0
==========================================
✓ All tests passed!
```

### Detailed Results

1. **Persistence Unit Tests**: ✅ 8/8 passed
   - All core persistence functionality working correctly
   - Unicode and multiline content handled properly

2. **Settings Unit Tests**: ✅ 5/5 passed
   - Configuration management working correctly
   - File and directory creation successful

3. **Integration Tests**: ✅ 3/3 passed
   - Components integrate correctly
   - End-to-end workflows function as expected

4. **Manual Persistence Test**: ✅ Passed
   - Real file I/O verified
   - Persistence across sessions confirmed

5. **TUI Functional Test**: ✅ Passed
   - Application starts correctly
   - All panes display properly
   - Navigation works as expected
   - Quit functionality works

## Manual Testing

### nvim Integration

The nvim integration requires interactive testing as it involves terminal suspension and editor control. To test manually:

1. Start the application:
   ```bash
   llm-manager
   ```

2. Press `1` to focus User Prompt pane

3. Press `e` to edit in nvim

4. Make changes in nvim and save (`:wq`)

5. Verify changes appear in the pane

6. Restart application and verify persistence

### Visual Testing Checklist

- [ ] Application launches without errors
- [ ] All three panes are visible
- [ ] Pane borders and titles display correctly
- [ ] Footer shows all keyboard shortcuts
- [ ] Pressing 1/2/3 focuses correct pane
- [ ] Focus indicator is visible
- [ ] Pressing 'e' opens nvim
- [ ] Changes in nvim appear in pane
- [ ] Content persists across restarts
- [ ] Pressing 'q' quits cleanly

## Continuous Testing

### Before Committing

Always run the full test suite before committing:

```bash
./tests/run_all_tests.sh
```

### Adding New Tests

When adding new functionality:

1. Add unit tests to appropriate test file
2. Add integration tests if multiple components interact
3. Update expect scripts if TUI behavior changes
4. Run full test suite to ensure no regressions

## Known Limitations

### nvim Expect Test

The nvim integration test (`test_nvim_integration.exp`) cannot fully run in an automated environment because:
- `app.suspend()` requires real terminal control
- Expect already controls the terminal
- nvim needs direct terminal access

**Solution**: nvim integration must be tested manually (see above)

## Test Data

### Persistence Test Data Location

Tests create actual files in:
```
~/.llm_manager/data/
├── user_prompt.txt
├── system_prompt.txt
└── context.txt
```

**Cleanup**: Test data is left in place for inspection. Delete manually if needed:
```bash
rm -rf ~/.llm_manager/data/
```

## Troubleshooting

### Tests Fail with "No module named llm_manager"

Ensure the package is installed:
```bash
pip install -e .
```

### Expect Tests Fail

Ensure expect is installed:
```bash
# Ubuntu/Debian
sudo apt install expect

# Check version
expect -v
```

### Permission Errors

Ensure you have write access to `~/.llm_manager/`:
```bash
ls -la ~/.llm_manager/
```

## Coverage

Current test coverage focuses on:
- ✅ Core persistence layer (100%)
- ✅ Settings and configuration (100%)
- ✅ Component integration (100%)
- ✅ TUI startup and navigation (100%)
- ⚠️ nvim integration (manual testing required)
- ⏳ Docking/undocking (not yet implemented)
- ⏳ LLM API integration (future)

## Future Testing

Planned test additions:
1. Full docking/undocking tests (when implemented)
2. LLM API integration tests (when added)
3. Response pane tests (future feature)
4. Performance/stress tests
5. Cross-platform tests (Windows, macOS)
