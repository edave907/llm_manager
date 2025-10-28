"""Manual test for persistence - actually writes to ~/.llm_manager/data."""

from pathlib import Path
from llm_manager.core.settings import settings
from llm_manager.core.persistence import PaneManager


def test_actual_persistence():
    """Test actual file persistence in the real data directory."""
    print("Testing actual file persistence...")

    # Ensure directories exist
    settings.ensure_files()

    # Verify files exist
    print(f"✓ User prompt file: {settings.USER_PROMPT_FILE}")
    print(f"✓ System prompt file: {settings.SYSTEM_PROMPT_FILE}")
    print(f"✓ Context file: {settings.CONTEXT_FILE}")

    assert settings.USER_PROMPT_FILE.exists()
    assert settings.SYSTEM_PROMPT_FILE.exists()
    assert settings.CONTEXT_FILE.exists()

    # Create manager
    manager = PaneManager(
        settings.USER_PROMPT_FILE,
        settings.SYSTEM_PROMPT_FILE,
        settings.CONTEXT_FILE
    )

    # Write test content
    test_user = "Test user prompt: What is Python?"
    test_system = "Test system prompt: You are a helpful assistant."
    test_context = "Test context: Python programming"

    print("\nWriting test content...")
    manager.user_prompt.write(test_user)
    manager.system_prompt.write(test_system)
    manager.context.write(test_context)

    # Read back immediately
    print("Reading back content immediately...")
    assert manager.user_prompt.read() == test_user
    assert manager.system_prompt.read() == test_system
    assert manager.context.read() == test_context
    print("✓ Immediate read successful")

    # Create new manager (simulating app restart)
    print("\nSimulating app restart with new manager...")
    manager2 = PaneManager(
        settings.USER_PROMPT_FILE,
        settings.SYSTEM_PROMPT_FILE,
        settings.CONTEXT_FILE
    )

    # Verify content persists
    assert manager2.user_prompt.read() == test_user
    assert manager2.system_prompt.read() == test_system
    assert manager2.context.read() == test_context
    print("✓ Content persisted across manager instances")

    # Verify file contents directly
    print("\nVerifying file contents directly...")
    assert settings.USER_PROMPT_FILE.read_text() == test_user
    assert settings.SYSTEM_PROMPT_FILE.read_text() == test_system
    assert settings.CONTEXT_FILE.read_text() == test_context
    print("✓ File contents verified directly")

    # Update content
    print("\nUpdating content...")
    updated_user = "Updated: How do I write a function in Python?"
    manager2.user_prompt.write(updated_user)

    # Verify update
    assert manager2.user_prompt.read() == updated_user
    assert settings.USER_PROMPT_FILE.read_text() == updated_user
    print("✓ Content update successful")

    # Clean up test data (optional - comment out to inspect files)
    print("\nTest data remains in:")
    print(f"  {settings.DATA_DIR}")
    print("You can manually inspect or delete these files.")

    print("\n" + "=" * 50)
    print("✓ All persistence tests passed!")
    print("=" * 50)


if __name__ == "__main__":
    test_actual_persistence()
