"""
Base provider interface for AI models.

This module defines the abstract base class that all AI provider
implementations must inherit from. This enables:
- Consistent interface across different providers
- Easy addition of new providers
- Provider-agnostic interview conductor code
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)


class AIProvider(ABC):
    """
    Abstract base class for AI providers.

    All provider implementations (Claude, OpenAI, Gemini, etc.) must
    inherit from this class and implement the generate_response method.

    Attributes:
        config: Provider configuration dictionary
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the provider with configuration.

        Args:
            config: Configuration dictionary with provider-specific settings
        """
        self.config = config
        logger.debug(f"Initialized {self.__class__.__name__} with config: {list(config.keys())}")

    @abstractmethod
    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """
        Generate AI response given conversation history.

        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
                     Roles can be: 'system', 'user', 'assistant'

        Returns:
            Generated response text

        Raises:
            NotImplementedError: If subclass doesn't implement this method
            Exception: For API errors or other failures

        Example:
            >>> messages = [
            ...     {'role': 'system', 'content': 'You are a helpful assistant'},
            ...     {'role': 'user', 'content': 'Hello!'}
            ... ]
            >>> response = provider.generate_response(messages)
        """
        raise NotImplementedError(f"{self.__class__.__name__} must implement generate_response()")

    def __repr__(self) -> str:
        """String representation of the provider."""
        return f"{self.__class__.__name__}(config_keys={list(self.config.keys())})"


__all__ = ['AIProvider']
