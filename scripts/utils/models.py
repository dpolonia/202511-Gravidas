"""
Centralized model registry for all AI providers.

This module serves as the single source of truth for:
- Model pricing (input/output, batch rates)
- Model capabilities (context windows, max tokens, features)
- Model performance (tokens/sec, quality ratings)
- Model metadata (names, descriptions, recommendations)

Usage:
    from utils.models import get_model_info, estimate_cost, MODELS_REGISTRY

    # Get full model information
    model_info = get_model_info('anthropic', 'claude-sonnet-4-5-20250929')

    # Calculate cost
    cost = estimate_cost('anthropic', 'claude-sonnet-4-5-20250929',
                        input_tokens=1000, output_tokens=500)

    # Check if batch API available
    if model_info['batch_available']:
        batch_cost = estimate_cost('anthropic', 'claude-sonnet-4-5-20250929',
                                  input_tokens=1000, output_tokens=500,
                                  use_batch=True)
"""

from typing import Dict, Any, Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)

# Centralized model registry
# All costs are per 1 million tokens (per 1M)
MODELS_REGISTRY = {
    'anthropic': {
        'name': 'Anthropic (Claude)',
        'models': {
            'claude-sonnet-4-5-20250929': {
                'name': 'Claude Sonnet 4.5',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'tokens_per_second': 80,
                'quality': 'Excellent',
                'context_window': 200000,
                'max_output': 64000,
                'extended_thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Smartest model for complex agents and coding (Recommended)',
                'recommended': True
            },
            'claude-haiku-4-5': {
                'name': 'Claude Haiku 4.5',
                'cost_input': 1.0,
                'cost_output': 5.0,
                'batch_available': True,
                'batch_input': 0.5,
                'batch_output': 2.5,
                'tokens_per_second': 120,
                'quality': 'Very Good',
                'context_window': 200000,
                'max_output': 64000,
                'extended_thinking': True,
                'knowledge_cutoff': 'Feb 2025',
                'description': 'Fastest model with near-frontier intelligence'
            },
            'claude-opus-4-1': {
                'name': 'Claude Opus 4.1',
                'cost_input': 15.0,
                'cost_output': 75.0,
                'batch_available': True,
                'batch_input': 7.5,
                'batch_output': 37.5,
                'tokens_per_second': 50,
                'quality': 'Excellent',
                'context_window': 200000,
                'max_output': 32000,
                'extended_thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Exceptional model for specialized reasoning tasks'
            },
            # Legacy models for backward compatibility
            'claude-3-haiku-20240307': {
                'name': 'Claude 3 Haiku',
                'cost_input': 0.25,
                'cost_output': 1.25,
                'batch_available': False,
                'tokens_per_second': 100,
                'quality': 'Good',
                'context_window': 200000,
                'max_output': 4096,
                'extended_thinking': False,
                'knowledge_cutoff': 'Aug 2023',
                'description': 'Legacy model for testing (deprecated)'
            },
            'claude-4.5-sonnet': {
                'name': 'Claude 4.5 Sonnet',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'tokens_per_second': 80,
                'quality': 'Excellent',
                'context_window': 200000,
                'max_output': 64000,
                'extended_thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Alias for claude-sonnet-4-5-20250929'
            }
        }
    },
    'openai': {
        'name': 'OpenAI (GPT)',
        'models': {
            'gpt-5': {
                'name': 'GPT-5',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'cached_input': 0.13,
                'tokens_per_second': 70,
                'quality': 'Excellent',
                'context_window': 400000,
                'max_output': 128000,
                'knowledge_cutoff': 'Sep 2024',
                'features': ['streaming', 'function_calling', 'structured_outputs', 'image_input'],
                'description': 'Best model for coding and agentic tasks across domains (Recommended)',
                'recommended': True
            },
            'gpt-5-pro': {
                'name': 'GPT-5 Pro',
                'cost_input': 15.0,
                'cost_output': 120.0,
                'batch_available': True,
                'batch_input': 7.5,
                'batch_output': 60.0,
                'tokens_per_second': 50,
                'quality': 'Exceptional',
                'context_window': 400000,
                'max_output': 272000,
                'knowledge_cutoff': 'Sep 2024',
                'features': ['streaming', 'function_calling', 'structured_outputs', 'image_input'],
                'description': 'Smarter and more precise responses for complex reasoning'
            },
            'gpt-5-chatgpt': {
                'name': 'GPT-5 (ChatGPT)',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'cached_input': 0.13,
                'tokens_per_second': 70,
                'quality': 'Excellent',
                'context_window': 128000,
                'max_output': 16384,
                'knowledge_cutoff': 'Sep 2024',
                'features': ['streaming', 'function_calling', 'structured_outputs', 'image_input'],
                'description': 'GPT-5 optimized for chat, 128K context'
            },
            'gpt-5-mini': {
                'name': 'GPT-5 Mini',
                'cost_input': 0.25,
                'cost_output': 2.0,
                'batch_available': True,
                'batch_input': 0.125,
                'batch_output': 1.0,
                'tokens_per_second': 90,
                'quality': 'Very Good',
                'context_window': 128000,
                'max_output': 16384,
                'knowledge_cutoff': 'Sep 2024',
                'description': 'Fast and cost-effective for high-volume tasks'
            }
        }
    },
    'google': {
        'name': 'Google (Gemini)',
        'models': {
            'gemini-2.5-pro': {
                'name': 'Gemini 2.5 Pro',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'tokens_per_second': 75,
                'quality': 'Excellent',
                'context_window': 1048576,
                'max_output': 65536,
                'thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'State-of-the-art thinking model for complex reasoning (Recommended)',
                'recommended': True
            },
            'gemini-2.5-flash': {
                'name': 'Gemini 2.5 Flash',
                'cost_input': 0.15,
                'cost_output': 1.25,
                'batch_available': True,
                'batch_input': 0.075,
                'batch_output': 0.625,
                'tokens_per_second': 110,
                'quality': 'Very Good',
                'context_window': 1048576,
                'max_output': 65536,
                'thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Best price-performance, large-scale processing'
            },
            'gemini-2.5-flash-lite': {
                'name': 'Gemini 2.5 Flash-Lite',
                'cost_input': 0.10,
                'cost_output': 0.40,
                'batch_available': True,
                'batch_input': 0.05,
                'batch_output': 0.20,
                'tokens_per_second': 130,
                'quality': 'Good',
                'context_window': 1048576,
                'max_output': 65536,
                'thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Fastest, optimized for cost-efficiency and high throughput'
            },
            'gemini-2.0-flash': {
                'name': 'Gemini 2.0 Flash',
                'cost_input': 0.05,
                'cost_output': 0.20,
                'batch_available': True,
                'batch_input': 0.025,
                'batch_output': 0.10,
                'tokens_per_second': 145,
                'quality': 'Good',
                'context_window': 1048576,
                'max_output': 8192,
                'thinking': False,
                'knowledge_cutoff': 'Aug 2024',
                'description': 'Second generation workhorse, 1M context window'
            },
            # Aliases for backward compatibility
            'gemini-2.5-pro-thinking': {
                'name': 'Gemini 2.5 Pro (Thinking)',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'tokens_per_second': 75,
                'quality': 'Excellent',
                'context_window': 1048576,
                'max_output': 65536,
                'thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Alias for gemini-2.5-pro with thinking enabled'
            },
            'gemini-2.5-flash-thinking': {
                'name': 'Gemini 2.5 Flash (Thinking)',
                'cost_input': 0.15,
                'cost_output': 0.60,
                'batch_available': True,
                'batch_input': 0.075,
                'batch_output': 0.30,
                'tokens_per_second': 110,
                'quality': 'Very Good',
                'context_window': 1048576,
                'max_output': 65536,
                'thinking': True,
                'knowledge_cutoff': 'Jan 2025',
                'description': 'Alias for gemini-2.5-flash with thinking enabled'
            }
        }
    },
    'aws': {
        'name': 'AWS Bedrock',
        'models': {
            'bedrock-claude-sonnet-4-5': {
                'name': 'Claude 4.5 Sonnet (Bedrock)',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'tokens_per_second': 80,
                'quality': 'Excellent',
                'description': 'Claude via AWS, enterprise integration'
            },
            'bedrock-llama-3-2-90b': {
                'name': 'Llama 3.2 90B (Bedrock)',
                'cost_input': 2.0,
                'cost_output': 2.0,
                'batch_available': True,
                'batch_input': 1.0,
                'batch_output': 1.0,
                'tokens_per_second': 85,
                'quality': 'Very Good',
                'description': 'Open source, AWS hosted'
            },
            'bedrock-titan-express': {
                'name': 'Amazon Titan Text Express',
                'cost_input': 0.8,
                'cost_output': 1.6,
                'batch_available': True,
                'batch_input': 0.4,
                'batch_output': 0.8,
                'tokens_per_second': 95,
                'quality': 'Good',
                'description': 'Amazon native, cost effective'
            }
        }
    },
    'mistral': {
        'name': 'Mistral AI',
        'models': {
            'mistral-large-2': {
                'name': 'Mistral Large 2',
                'cost_input': 3.0,
                'cost_output': 9.0,
                'batch_available': False,
                'tokens_per_second': 70,
                'quality': 'Excellent',
                'description': 'Advanced reasoning, European AI'
            },
            'codestral': {
                'name': 'Codestral',
                'cost_input': 1.0,
                'cost_output': 3.0,
                'batch_available': False,
                'tokens_per_second': 90,
                'quality': 'Very Good',
                'description': 'Code generation specialist'
            },
            'ministral-8b': {
                'name': 'Ministral 8B',
                'cost_input': 0.1,
                'cost_output': 0.1,
                'batch_available': False,
                'tokens_per_second': 130,
                'quality': 'Good',
                'description': 'Fast, edge deployment'
            }
        }
    },
    'xai': {
        'name': 'xAI (Grok)',
        'models': {
            'grok-4': {
                'name': 'Grok 4',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': False,
                'tokens_per_second': 60,
                'quality': 'Excellent',
                'description': 'Advanced reasoning, real-time knowledge'
            },
            'grok-4-fast': {
                'name': 'Grok 4 Fast (Reasoning)',
                'cost_input': 0.2,
                'cost_output': 0.5,
                'batch_available': False,
                'tokens_per_second': 100,
                'quality': 'Very Good',
                'description': 'Fast reasoning mode'
            },
            'grok-3-mini': {
                'name': 'Grok 3 Mini',
                'cost_input': 0.3,
                'cost_output': 0.5,
                'batch_available': False,
                'tokens_per_second': 90,
                'quality': 'Good',
                'description': 'Fast, capable, good value'
            }
        }
    }
}

# Average tokens per interview (for cost estimation)
AVG_INPUT_TOKENS_PER_INTERVIEW = 3000
AVG_OUTPUT_TOKENS_PER_INTERVIEW = 5000


def get_model_info(provider: str, model_id: str) -> Optional[Dict[str, Any]]:
    """
    Get full model information from registry.

    Args:
        provider: Provider name (e.g., 'anthropic', 'openai', 'google')
        model_id: Model identifier (e.g., 'claude-sonnet-4-5-20250929')

    Returns:
        Dictionary with model info, or None if not found

    Example:
        >>> model = get_model_info('anthropic', 'claude-sonnet-4-5-20250929')
        >>> print(f"Cost: ${model['cost_input']}/1M input tokens")
    """
    provider = provider.lower()

    if provider not in MODELS_REGISTRY:
        logger.warning(f"Provider '{provider}' not found in model registry")
        return None

    models = MODELS_REGISTRY[provider].get('models', {})
    if model_id not in models:
        logger.warning(f"Model '{model_id}' not found for provider '{provider}'")
        return None

    return models[model_id]


def estimate_cost(provider: str, model_id: str,
                 input_tokens: int, output_tokens: int,
                 use_batch: bool = False) -> Optional[float]:
    """
    Calculate cost for given token counts.

    Args:
        provider: Provider name
        model_id: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens
        use_batch: Whether to use batch API pricing (50% discount)

    Returns:
        Total cost in dollars, or None if model not found

    Example:
        >>> cost = estimate_cost('anthropic', 'claude-sonnet-4-5-20250929',
        ...                     input_tokens=3000, output_tokens=5000)
        >>> print(f"Cost: ${cost:.4f}")
    """
    model_info = get_model_info(provider, model_id)
    if not model_info:
        return None

    # Use batch pricing if available and requested
    if use_batch and model_info.get('batch_available', False):
        input_cost_per_1m = model_info.get('batch_input', model_info['cost_input'])
        output_cost_per_1m = model_info.get('batch_output', model_info['cost_output'])
    else:
        input_cost_per_1m = model_info['cost_input']
        output_cost_per_1m = model_info['cost_output']

    # Calculate cost (prices are per 1M tokens)
    input_cost = (input_tokens / 1_000_000) * input_cost_per_1m
    output_cost = (output_tokens / 1_000_000) * output_cost_per_1m

    return input_cost + output_cost


def get_all_providers() -> List[str]:
    """
    Get list of all available providers.

    Returns:
        List of provider names

    Example:
        >>> providers = get_all_providers()
        >>> print(providers)
        ['anthropic', 'openai', 'google', 'aws', 'mistral', 'xai']
    """
    return list(MODELS_REGISTRY.keys())


def get_provider_models(provider: str) -> List[str]:
    """
    Get list of all models for a provider.

    Args:
        provider: Provider name

    Returns:
        List of model IDs for that provider

    Example:
        >>> models = get_provider_models('anthropic')
        >>> print(models)
        ['claude-sonnet-4-5-20250929', 'claude-haiku-4-5', 'claude-opus-4-1']
    """
    provider = provider.lower()
    if provider not in MODELS_REGISTRY:
        return []

    return list(MODELS_REGISTRY[provider].get('models', {}).keys())


def get_recommended_models() -> List[Tuple[str, str, Dict[str, Any]]]:
    """
    Get list of recommended models across all providers.

    Returns:
        List of (provider, model_id, model_info) tuples for recommended models

    Example:
        >>> for provider, model_id, info in get_recommended_models():
        ...     print(f"{provider}: {info['name']} - {info['description']}")
    """
    recommended = []

    for provider, provider_data in MODELS_REGISTRY.items():
        for model_id, model_info in provider_data.get('models', {}).items():
            if model_info.get('recommended', False):
                recommended.append((provider, model_id, model_info))

    return recommended


def format_cost_summary(provider: str, model_id: str,
                       input_tokens: int, output_tokens: int) -> str:
    """
    Format a human-readable cost summary.

    Args:
        provider: Provider name
        model_id: Model identifier
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Formatted string with cost breakdown

    Example:
        >>> summary = format_cost_summary('anthropic', 'claude-sonnet-4-5-20250929',
        ...                               3000, 5000)
        >>> print(summary)
    """
    model_info = get_model_info(provider, model_id)
    if not model_info:
        return f"Model {provider}/{model_id} not found"

    regular_cost = estimate_cost(provider, model_id, input_tokens, output_tokens, use_batch=False)

    result = [
        f"Model: {model_info['name']} ({provider})",
        f"Input tokens: {input_tokens:,} @ ${model_info['cost_input']}/1M",
        f"Output tokens: {output_tokens:,} @ ${model_info['cost_output']}/1M",
        f"Total cost: ${regular_cost:.4f}"
    ]

    # Add batch pricing if available
    if model_info.get('batch_available', False):
        batch_cost = estimate_cost(provider, model_id, input_tokens, output_tokens, use_batch=True)
        savings = regular_cost - batch_cost
        savings_pct = (savings / regular_cost) * 100
        result.append(f"Batch API cost: ${batch_cost:.4f} (save ${savings:.4f}, {savings_pct:.0f}%)")

    return "\n".join(result)


def validate_model_registry() -> Tuple[bool, List[str]]:
    """
    Validate model registry completeness and consistency.

    Returns:
        Tuple of (is_valid, list_of_errors)

    Example:
        >>> is_valid, errors = validate_model_registry()
        >>> if not is_valid:
        ...     for error in errors:
        ...         print(f"❌ {error}")
    """
    errors = []

    for provider, provider_data in MODELS_REGISTRY.items():
        # Check provider has name
        if 'name' not in provider_data:
            errors.append(f"Provider '{provider}' missing 'name' field")

        # Check provider has models
        if 'models' not in provider_data or not provider_data['models']:
            errors.append(f"Provider '{provider}' has no models defined")
            continue

        # Validate each model
        for model_id, model_info in provider_data['models'].items():
            required_fields = ['name', 'cost_input', 'cost_output', 'quality', 'description']
            for field in required_fields:
                if field not in model_info:
                    errors.append(f"Model '{provider}/{model_id}' missing required field '{field}'")

            # If batch available, must have batch pricing
            if model_info.get('batch_available', False):
                if 'batch_input' not in model_info or 'batch_output' not in model_info:
                    errors.append(f"Model '{provider}/{model_id}' has batch_available=True but missing batch pricing")

    return (len(errors) == 0, errors)


# Export public API
__all__ = [
    'MODELS_REGISTRY',
    'AVG_INPUT_TOKENS_PER_INTERVIEW',
    'AVG_OUTPUT_TOKENS_PER_INTERVIEW',
    'get_model_info',
    'estimate_cost',
    'get_all_providers',
    'get_provider_models',
    'get_recommended_models',
    'format_cost_summary',
    'validate_model_registry',
]
