"""Model configuration for LLM Manager."""

from dataclasses import dataclass
from typing import Dict
import os


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

    @property
    def safe_input_budget(self) -> int:
        """Calculate safe input budget (70% of context - max_output)."""
        return max(1000, int(self.context_window * 0.7) - self.max_output_tokens)

    @property
    def aggressive_input_budget(self) -> int:
        """Calculate aggressive input budget (85% of context - max_output)."""
        return max(2000, int(self.context_window * 0.85) - self.max_output_tokens)

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
    # Ollama Models (local)
    "ollama:llama3.2": ModelConfig(
        name="ollama:llama3.2",
        display_name="Llama 3.2",
        provider="ollama",
        context_window=128000,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "ollama:qwen2.5": ModelConfig(
        name="ollama:qwen2.5",
        display_name="Qwen 2.5",
        provider="ollama",
        context_window=32768,
        max_output_tokens=2048,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "ollama:mistral": ModelConfig(
        name="ollama:mistral",
        display_name="Mistral",
        provider="ollama",
        context_window=32768,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "ollama:codellama": ModelConfig(
        name="ollama:codellama",
        display_name="Code Llama",
        provider="ollama",
        context_window=16384,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    # OpenAI-Compatible Models (vLLM, llama.cpp, etc.)
    "openai_compatible:default": ModelConfig(
        name="openai_compatible:default",
        display_name="Custom Server (Default)",
        provider="openai_compatible",
        context_window=8192,
        max_output_tokens=2048,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "openai_compatible:llama-3-8b": ModelConfig(
        name="openai_compatible:llama-3-8b",
        display_name="Llama 3 8B (vLLM)",
        provider="openai_compatible",
        context_window=8192,
        max_output_tokens=2048,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "openai_compatible:mistral-7b": ModelConfig(
        name="openai_compatible:mistral-7b",
        display_name="Mistral 7B (vLLM)",
        provider="openai_compatible",
        context_window=32768,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
    ),
    "openai_compatible:qwen2.5-32b": ModelConfig(
        name="openai_compatible:qwen2.5-32b",
        display_name="Qwen 2.5 32B (vLLM)",
        provider="openai_compatible",
        context_window=32768,
        max_output_tokens=4096,
        input_cost_per_1k=0.0,
        output_cost_per_1k=0.0,
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
    "ollama": [
        "ollama:llama3.2",
        "ollama:qwen2.5",
        "ollama:mistral",
        "ollama:codellama",
    ],
    "openai_compatible": [
        "openai_compatible:default",
        "openai_compatible:llama-3-8b",
        "openai_compatible:mistral-7b",
        "openai_compatible:qwen2.5-32b",
    ],
}


def _apply_env_overrides(model_name: str, config: ModelConfig) -> ModelConfig:
    """Apply environment variable overrides to model configuration.

    Supports overrides like:
      MODEL_CONTEXT_GPT_4O=200000
      MODEL_MAX_TOKENS_GPT_4O=8192

    Args:
        model_name: The model identifier (e.g., "openai:gpt-4o")
        config: The base model configuration

    Returns:
        Updated ModelConfig with environment overrides applied
    """
    # Extract just the model name part (remove provider prefix)
    base_name = model_name.split(":", 1)[1] if ":" in model_name else model_name

    # Convert to uppercase and replace special chars with underscores
    env_key = base_name.upper().replace("-", "_").replace(".", "_")

    # Check for context window override
    context_env = os.getenv(f"MODEL_CONTEXT_{env_key}")
    if context_env:
        try:
            config.context_window = int(context_env)
            print(f"[ENV OVERRIDE] {model_name} context_window: {config.context_window}")
        except ValueError:
            pass

    # Check for max tokens override
    max_tokens_env = os.getenv(f"MODEL_MAX_TOKENS_{env_key}")
    if max_tokens_env:
        try:
            config.max_output_tokens = int(max_tokens_env)
            print(f"[ENV OVERRIDE] {model_name} max_output_tokens: {config.max_output_tokens}")
        except ValueError:
            pass

    return config


def get_model_config(model_name: str) -> ModelConfig:
    """Get configuration for a specific model with environment overrides applied.

    Args:
        model_name: The model identifier (e.g., "openai:gpt-4o")

    Returns:
        ModelConfig with environment overrides applied, or None if not found
    """
    config = AVAILABLE_MODELS.get(model_name)
    if config:
        # Apply environment overrides
        config = _apply_env_overrides(model_name, config)
    return config


def get_models_by_provider(provider: str) -> list[str]:
    """Get list of model names for a specific provider."""
    return MODELS_BY_PROVIDER.get(provider, [])


def get_input_budget(config: ModelConfig, aggressive: bool = False) -> int:
    """Get input budget for a model with optional global override.

    Calculates how many tokens can be used for input while leaving room
    for the model's output. Supports global INPUT_BUDGET_TOKENS override.

    Args:
        config: The model configuration
        aggressive: If True, use aggressive budget (85%), else safe budget (70%)

    Returns:
        Input budget in tokens
    """
    budget = config.aggressive_input_budget if aggressive else config.safe_input_budget

    # Check for global override
    env_budget = os.getenv("INPUT_BUDGET_TOKENS")
    if env_budget:
        try:
            return min(budget, int(env_budget))
        except ValueError:
            pass

    return budget


def get_output_budget(config: ModelConfig) -> int:
    """Get output budget for a model with optional global override.

    Returns a conservative output budget (600 tokens) or the global
    MAX_OUTPUT_TOKENS override if set.

    Args:
        config: The model configuration

    Returns:
        Output budget in tokens
    """
    env_output = os.getenv("MAX_OUTPUT_TOKENS")
    if env_output:
        try:
            return min(config.max_output_tokens, int(env_output))
        except ValueError:
            pass

    return min(600, config.max_output_tokens)


def format_model_info(config: ModelConfig) -> str:
    """Format detailed model information including budgets.

    Args:
        config: The model configuration

    Returns:
        Formatted string with model details
    """
    lines = [
        f"Model: {config.display_name}",
        f"Provider: {config.provider}",
        f"Context: {config.context_window:,} tokens",
        f"Max output: {config.max_output_tokens:,} tokens",
        f"Safe input budget: {config.safe_input_budget:,} tokens",
        f"Aggressive input budget: {config.aggressive_input_budget:,} tokens",
    ]

    if config.input_cost_per_1k > 0:
        lines.append(
            f"Cost (per 1K): input ${config.input_cost_per_1k:.3f} / "
            f"output ${config.output_cost_per_1k:.3f}"
        )

    return "\n".join(lines)
