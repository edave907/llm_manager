"""Model configuration for LLM Manager."""

from dataclasses import dataclass
from typing import Dict


@dataclass
class ModelConfig:
    """Configuration for a specific LLM model."""

    name: str
    display_name: str
    provider: str
    context_window: int
    max_output_tokens: int
    input_cost_per_1k: float = 0.0
    output_cost_per_1k: float = 0.0
    supports_streaming: bool = True

    def __str__(self) -> str:
        """String representation for display."""
        cost_info = ""
        if self.input_cost_per_1k > 0:
            cost_info = f" (${self.input_cost_per_1k:.3f}/${ self.output_cost_per_1k:.3f} per 1K)"
        return f"{self.display_name}{cost_info}"


# Available models configuration
AVAILABLE_MODELS: Dict[str, ModelConfig] = {
    # OpenAI Models
    "openai:gpt-4o": ModelConfig(
        name="openai:gpt-4o",
        display_name="GPT-4o",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        input_cost_per_1k=5.0,
        output_cost_per_1k=15.0,
    ),
    "openai:gpt-4o-mini": ModelConfig(
        name="openai:gpt-4o-mini",
        display_name="GPT-4o Mini",
        provider="openai",
        context_window=128000,
        max_output_tokens=16384,
        input_cost_per_1k=0.15,
        output_cost_per_1k=0.6,
    ),
    "openai:gpt-4-turbo": ModelConfig(
        name="openai:gpt-4-turbo",
        display_name="GPT-4 Turbo",
        provider="openai",
        context_window=128000,
        max_output_tokens=4096,
        input_cost_per_1k=10.0,
        output_cost_per_1k=30.0,
    ),
    "openai:gpt-3.5-turbo": ModelConfig(
        name="openai:gpt-3.5-turbo",
        display_name="GPT-3.5 Turbo",
        provider="openai",
        context_window=16385,
        max_output_tokens=4096,
        input_cost_per_1k=0.5,
        output_cost_per_1k=1.5,
    ),
    # Anthropic Models
    "anthropic:claude-3-5-sonnet-latest": ModelConfig(
        name="anthropic:claude-3-5-sonnet-latest",
        display_name="Claude 3.5 Sonnet",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=8192,
        input_cost_per_1k=3.0,
        output_cost_per_1k=15.0,
    ),
    "anthropic:claude-3-opus-20240229": ModelConfig(
        name="anthropic:claude-3-opus-20240229",
        display_name="Claude 3 Opus",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        input_cost_per_1k=15.0,
        output_cost_per_1k=75.0,
    ),
    "anthropic:claude-3-haiku-20240307": ModelConfig(
        name="anthropic:claude-3-haiku-20240307",
        display_name="Claude 3 Haiku",
        provider="anthropic",
        context_window=200000,
        max_output_tokens=4096,
        input_cost_per_1k=0.25,
        output_cost_per_1k=1.25,
    ),
}

# Group models by provider for organized display
MODELS_BY_PROVIDER = {
    "openai": [
        "openai:gpt-4o",
        "openai:gpt-4o-mini",
        "openai:gpt-4-turbo",
        "openai:gpt-3.5-turbo",
    ],
    "anthropic": [
        "anthropic:claude-3-5-sonnet-latest",
        "anthropic:claude-3-opus-20240229",
        "anthropic:claude-3-haiku-20240307",
    ],
}


def get_model_config(model_name: str) -> ModelConfig:
    """Get configuration for a specific model."""
    return AVAILABLE_MODELS.get(model_name)


def get_models_by_provider(provider: str) -> list[str]:
    """Get list of model names for a specific provider."""
    return MODELS_BY_PROVIDER.get(provider, [])
