"""LLM client for communicating with language models."""

from typing import Optional, Generator
import anthropic
import openai

from .models import ModelConfig, get_model_config
from .settings import settings


class LLMClient:
    """Client for interacting with LLM APIs."""

    def __init__(self):
        """Initialize the LLM client."""
        self.current_model: Optional[str] = None
        self.model_config: Optional[ModelConfig] = None
        self._openai_client: Optional[openai.OpenAI] = None
        self._anthropic_client: Optional[anthropic.Anthropic] = None

    def set_model(self, model_name: str) -> bool:
        """Set the current model.

        Args:
            model_name: Full model identifier (e.g., "openai:gpt-4o")

        Returns:
            True if model was set successfully, False otherwise
        """
        config = get_model_config(model_name)
        if not config:
            return False

        self.current_model = model_name
        self.model_config = config

        # Initialize appropriate client
        if config.provider == "openai":
            if not settings.OPENAI_API_KEY:
                return False
            self._openai_client = openai.OpenAI(
                api_key=settings.OPENAI_API_KEY,
                base_url=settings.OPENAI_BASE_URL,
            )
        elif config.provider == "anthropic":
            if not settings.ANTHROPIC_API_KEY:
                return False
            self._anthropic_client = anthropic.Anthropic(
                api_key=settings.ANTHROPIC_API_KEY
            )

        return True

    def send_message(
        self,
        user_prompt: str,
        system_prompt: str = "",
        context: str = "",
        max_tokens: Optional[int] = None,
    ) -> str:
        """Send a message to the current LLM.

        Args:
            user_prompt: The user's prompt
            system_prompt: Optional system prompt
            context: Optional context information
            max_tokens: Maximum tokens to generate (uses model default if not specified)

        Returns:
            The LLM's response text

        Raises:
            ValueError: If no model is set or API key is missing
            Exception: If the API call fails
        """
        if not self.current_model or not self.model_config:
            raise ValueError("No model selected. Please select a model first.")

        # Construct the full prompt
        full_prompt = user_prompt
        if context:
            full_prompt = f"Context:\n{context}\n\n{user_prompt}"

        # Use model's max output tokens if not specified
        if max_tokens is None:
            max_tokens = min(4096, self.model_config.max_output_tokens)

        # Route to appropriate provider
        if self.model_config.provider == "openai":
            return self._send_openai_message(full_prompt, system_prompt, max_tokens)
        elif self.model_config.provider == "anthropic":
            return self._send_anthropic_message(full_prompt, system_prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.model_config.provider}")

    def _send_openai_message(
        self, user_prompt: str, system_prompt: str, max_tokens: int
    ) -> str:
        """Send message to OpenAI API."""
        if not self._openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        # Extract actual model name (remove provider prefix)
        model_name = self.current_model.split(":", 1)[1] if ":" in self.current_model else self.current_model

        response = self._openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
        )

        return response.choices[0].message.content

    def _send_anthropic_message(
        self, user_prompt: str, system_prompt: str, max_tokens: int
    ) -> str:
        """Send message to Anthropic API."""
        if not self._anthropic_client:
            raise ValueError("Anthropic client not initialized. Check API key.")

        # Extract actual model name (remove provider prefix)
        model_name = self.current_model.split(":", 1)[1] if ":" in self.current_model else self.current_model

        kwargs = {
            "model": model_name,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        response = self._anthropic_client.messages.create(**kwargs)

        return response.content[0].text

    def stream_message(
        self,
        user_prompt: str,
        system_prompt: str = "",
        context: str = "",
        max_tokens: Optional[int] = None,
    ) -> Generator[str, None, None]:
        """Stream a message from the current LLM.

        Args:
            user_prompt: The user's prompt
            system_prompt: Optional system prompt
            context: Optional context information
            max_tokens: Maximum tokens to generate

        Yields:
            Text chunks as they are received from the API

        Raises:
            ValueError: If no model is set or API key is missing
            Exception: If the API call fails
        """
        if not self.current_model or not self.model_config:
            raise ValueError("No model selected. Please select a model first.")

        # Construct the full prompt
        full_prompt = user_prompt
        if context:
            full_prompt = f"Context:\n{context}\n\n{user_prompt}"

        # Use model's max output tokens if not specified
        if max_tokens is None:
            max_tokens = min(4096, self.model_config.max_output_tokens)

        # Route to appropriate provider
        if self.model_config.provider == "openai":
            yield from self._stream_openai_message(full_prompt, system_prompt, max_tokens)
        elif self.model_config.provider == "anthropic":
            yield from self._stream_anthropic_message(full_prompt, system_prompt, max_tokens)
        else:
            raise ValueError(f"Unsupported provider: {self.model_config.provider}")

    def _stream_openai_message(
        self, user_prompt: str, system_prompt: str, max_tokens: int
    ) -> Generator[str, None, None]:
        """Stream message from OpenAI API."""
        if not self._openai_client:
            raise ValueError("OpenAI client not initialized. Check API key.")

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        # Extract actual model name (remove provider prefix)
        model_name = self.current_model.split(":", 1)[1] if ":" in self.current_model else self.current_model

        stream = self._openai_client.chat.completions.create(
            model=model_name,
            messages=messages,
            max_tokens=max_tokens,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _stream_anthropic_message(
        self, user_prompt: str, system_prompt: str, max_tokens: int
    ) -> Generator[str, None, None]:
        """Stream message from Anthropic API."""
        if not self._anthropic_client:
            raise ValueError("Anthropic client not initialized. Check API key.")

        # Extract actual model name (remove provider prefix)
        model_name = self.current_model.split(":", 1)[1] if ":" in self.current_model else self.current_model

        kwargs = {
            "model": model_name,
            "max_tokens": max_tokens,
            "messages": [{"role": "user", "content": user_prompt}],
        }

        if system_prompt:
            kwargs["system"] = system_prompt

        with self._anthropic_client.messages.stream(**kwargs) as stream:
            for text in stream.text_stream:
                yield text

    def get_current_model_info(self) -> str:
        """Get information about the current model."""
        if not self.model_config:
            return "No model selected"

        info = f"{self.model_config.display_name}\n"
        info += f"Provider: {self.model_config.provider}\n"
        info += f"Context: {self.model_config.context_window:,} tokens\n"
        info += f"Max output: {self.model_config.max_output_tokens:,} tokens"

        if self.model_config.input_cost_per_1k > 0:
            info += f"\nCost: ${self.model_config.input_cost_per_1k:.3f}/${self.model_config.output_cost_per_1k:.3f} per 1K"

        return info
