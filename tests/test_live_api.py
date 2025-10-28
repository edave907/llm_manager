"""Live API tests for OpenAI and Anthropic.

This test requires valid API keys in environment variables:
- OPENAI_API_KEY
- ANTHROPIC_API_KEY

Note: This test makes real API calls and may incur costs.
"""

import os
import pytest
from llm_manager.core.llm_client import LLMClient
from llm_manager.core.conversation import ConversationHistory
from pathlib import Path
import tempfile


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
def test_openai_non_streaming():
    """Test OpenAI API with non-streaming response."""
    print("\n🔵 Testing OpenAI (non-streaming)...")

    client = LLMClient()
    success = client.set_model("openai:gpt-4o-mini")
    assert success, "Failed to initialize OpenAI client"

    response = client.send_message(
        user_prompt="Say 'Hello from OpenAI' and nothing else.",
        system_prompt="You are a helpful assistant.",
        context=""
    )

    print(f"✅ OpenAI Response: {response}")
    assert len(response) > 0, "Response is empty"
    assert "openai" in response.lower() or "hello" in response.lower()


@pytest.mark.skipif(
    not os.environ.get("OPENAI_API_KEY"),
    reason="OPENAI_API_KEY not set"
)
def test_openai_streaming():
    """Test OpenAI API with streaming response."""
    print("\n🔵 Testing OpenAI (streaming)...")

    client = LLMClient()
    success = client.set_model("openai:gpt-4o-mini")
    assert success, "Failed to initialize OpenAI client"

    chunks = []
    for chunk in client.stream_message(
        user_prompt="Count from 1 to 3, one number per word.",
        system_prompt="You are a helpful assistant.",
        context=""
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)

    print()  # New line after streaming
    full_response = "".join(chunks)
    print(f"✅ OpenAI Streaming Response: {full_response}")
    assert len(chunks) > 1, "Should have received multiple chunks"
    assert len(full_response) > 0, "Response is empty"


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
def test_anthropic_non_streaming():
    """Test Anthropic API with non-streaming response."""
    print("\n🟣 Testing Anthropic (non-streaming)...")

    client = LLMClient()
    success = client.set_model("anthropic:claude-3-haiku-20240307")
    assert success, "Failed to initialize Anthropic client"

    response = client.send_message(
        user_prompt="Say 'Hello from Claude' and nothing else.",
        system_prompt="You are a helpful assistant.",
        context=""
    )

    print(f"✅ Anthropic Response: {response}")
    assert len(response) > 0, "Response is empty"
    assert "claude" in response.lower() or "hello" in response.lower()


@pytest.mark.skipif(
    not os.environ.get("ANTHROPIC_API_KEY"),
    reason="ANTHROPIC_API_KEY not set"
)
def test_anthropic_streaming():
    """Test Anthropic API with streaming response."""
    print("\n🟣 Testing Anthropic (streaming)...")

    client = LLMClient()
    success = client.set_model("anthropic:claude-3-haiku-20240307")
    assert success, "Failed to initialize Anthropic client"

    chunks = []
    for chunk in client.stream_message(
        user_prompt="Count from 1 to 3, one number per word.",
        system_prompt="You are a helpful assistant.",
        context=""
    ):
        chunks.append(chunk)
        print(chunk, end="", flush=True)

    print()  # New line after streaming
    full_response = "".join(chunks)
    print(f"✅ Anthropic Streaming Response: {full_response}")
    assert len(chunks) > 1, "Should have received multiple chunks"
    assert len(full_response) > 0, "Response is empty"


@pytest.mark.skipif(
    not (os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")),
    reason="No API keys set"
)
def test_conversation_history_integration():
    """Test conversation history with live API."""
    print("\n📝 Testing Conversation History...")

    with tempfile.TemporaryDirectory() as tmpdir:
        history_file = Path(tmpdir) / "test_history.json"
        history = ConversationHistory(history_file=history_file)

        client = LLMClient()

        # Use whichever API key is available
        if os.environ.get("OPENAI_API_KEY"):
            model = "openai:gpt-4o-mini"
        else:
            model = "anthropic:claude-3-haiku-20240307"

        client.set_model(model)

        user_prompt = "What is 2+2? Answer with just the number."
        response = client.send_message(user_prompt, "", "")

        # Save to history
        history.add_turn(
            model=model,
            user_prompt=user_prompt,
            response=response,
            system_prompt="",
            context=""
        )

        print(f"✅ Conversation saved to history")
        print(f"   User: {user_prompt}")
        print(f"   Assistant: {response}")

        # Verify history was saved
        assert len(history.turns) == 1
        assert history.turns[0].user_prompt == user_prompt
        assert history.turns[0].response == response

        # Test export
        export_file = Path(tmpdir) / "export.json"
        success = history.export_to_file(export_file, format="json")
        assert success
        assert export_file.exists()
        print(f"✅ Conversation exported successfully")


if __name__ == "__main__":
    print("=" * 60)
    print("LIVE API TESTS")
    print("=" * 60)
    print("\nNote: These tests make real API calls and may incur costs.")
    print()

    # Run tests manually
    try:
        test_openai_non_streaming()
    except Exception as e:
        print(f"❌ OpenAI non-streaming test failed: {e}")

    try:
        test_openai_streaming()
    except Exception as e:
        print(f"❌ OpenAI streaming test failed: {e}")

    try:
        test_anthropic_non_streaming()
    except Exception as e:
        print(f"❌ Anthropic non-streaming test failed: {e}")

    try:
        test_anthropic_streaming()
    except Exception as e:
        print(f"❌ Anthropic streaming test failed: {e}")

    try:
        test_conversation_history_integration()
    except Exception as e:
        print(f"❌ Conversation history test failed: {e}")

    print("\n" + "=" * 60)
    print("TESTS COMPLETE")
    print("=" * 60)
