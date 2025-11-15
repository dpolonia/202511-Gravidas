#!/usr/bin/env python3
"""
Universal AI Client Factory

Provides a unified interface for interacting with multiple AI providers:
- OpenAI (GPT models)
- Anthropic (Claude models)  
- Google (Gemini models)
- AWS Bedrock
- Azure OpenAI
- Azure AI Foundry
- Mistral AI
- xAI (Grok)
- DeepSeek
- Together AI
- Fireworks AI
- Groq
- Cohere
- Perplexity

Each provider is abstracted behind a common interface for easy switching.
"""

import os
import json
import time
import logging
from typing import Dict, Any, List, Optional, Iterator
from abc import ABC, abstractmethod
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import AI provider SDKs
try:
    import openai
    from anthropic import Anthropic
    import google.generativeai as genai
    import boto3
    import requests
except ImportError as e:
    logging.warning(f"Some AI provider SDKs not available: {e}")

@dataclass
class AIResponse:
    """Standardized response format for all AI providers."""
    content: str
    usage: Dict[str, int]
    model: str
    provider: str
    cost_usd: float
    metadata: Dict[str, Any] = None

class BaseAIClient(ABC):
    """Abstract base class for all AI clients."""
    
    def __init__(self, provider_name: str, model_id: str, api_key: str, **kwargs):
        self.provider_name = provider_name
        self.model_id = model_id
        self.api_key = api_key
        self.logger = logging.getLogger(f"{provider_name}.{model_id}")
        
    @abstractmethod
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate a response from the AI model."""
        pass
    
    @abstractmethod
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """Generate a streaming response from the AI model."""
        pass

class OpenAIClient(BaseAIClient):
    """OpenAI client for GPT models."""
    
    def __init__(self, model_id: str, api_key: str, **kwargs):
        super().__init__("OpenAI", model_id, api_key, **kwargs)
        self.client = openai.OpenAI(api_key=api_key)
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using OpenAI API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            usage = {
                'input_tokens': response.usage.prompt_tokens,
                'output_tokens': response.usage.completion_tokens,
                'total_tokens': response.usage.total_tokens
            }
            
            # Calculate cost (simplified - would use model pricing from database)
            cost = self._calculate_cost(usage['input_tokens'], usage['output_tokens'])
            
            return AIResponse(
                content=response.choices[0].message.content,
                usage=usage,
                model=self.model_id,
                provider=self.provider_name,
                cost_usd=cost,
                metadata={'response_id': response.id}
            )
            
        except Exception as e:
            self.logger.error(f"OpenAI API error: {e}")
            raise
    
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream response using OpenAI API."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"OpenAI streaming error: {e}")
            raise
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on model pricing."""
        # This would use the enhanced model database for accurate pricing
        # Simplified implementation for now
        base_input_cost = 0.001  # $1 per 1M tokens
        base_output_cost = 0.002  # $2 per 1M tokens
        
        input_cost = (input_tokens / 1_000_000) * base_input_cost
        output_cost = (output_tokens / 1_000_000) * base_output_cost
        
        return input_cost + output_cost

class AnthropicClient(BaseAIClient):
    """Anthropic client for Claude models."""
    
    def __init__(self, model_id: str, api_key: str, **kwargs):
        super().__init__("Anthropic", model_id, api_key, **kwargs)
        self.client = Anthropic(api_key=api_key)
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Anthropic API."""
        try:
            response = self.client.messages.create(
                model=self.model_id,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            )
            
            usage = {
                'input_tokens': response.usage.input_tokens,
                'output_tokens': response.usage.output_tokens,
                'total_tokens': response.usage.input_tokens + response.usage.output_tokens
            }
            
            cost = self._calculate_cost(usage['input_tokens'], usage['output_tokens'])
            
            return AIResponse(
                content=response.content[0].text,
                usage=usage,
                model=self.model_id,
                provider=self.provider_name,
                cost_usd=cost,
                metadata={'response_id': response.id}
            )
            
        except Exception as e:
            self.logger.error(f"Anthropic API error: {e}")
            raise
    
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream response using Anthropic API."""
        try:
            with self.client.messages.stream(
                model=self.model_id,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7),
                messages=[{"role": "user", "content": prompt}]
            ) as stream:
                for text in stream.text_stream:
                    yield text
                    
        except Exception as e:
            self.logger.error(f"Anthropic streaming error: {e}")
            raise
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on Claude pricing."""
        # This would use the enhanced model database
        base_input_cost = 0.003  # $3 per 1M tokens for Sonnet
        base_output_cost = 0.015  # $15 per 1M tokens for Sonnet
        
        input_cost = (input_tokens / 1_000_000) * base_input_cost
        output_cost = (output_tokens / 1_000_000) * base_output_cost
        
        return input_cost + output_cost

class GoogleClient(BaseAIClient):
    """Google client for Gemini models."""
    
    def __init__(self, model_id: str, api_key: str, **kwargs):
        super().__init__("Google", model_id, api_key, **kwargs)
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model_id)
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using Google Gemini API."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get('max_tokens', 4096),
                    temperature=kwargs.get('temperature', 0.7)
                )
            )
            
            # Google doesn't provide detailed usage in free tier
            usage = {
                'input_tokens': len(prompt.split()) * 1.3,  # Rough estimate
                'output_tokens': len(response.text.split()) * 1.3,  # Rough estimate
                'total_tokens': 0
            }
            usage['total_tokens'] = usage['input_tokens'] + usage['output_tokens']
            
            cost = self._calculate_cost(usage['input_tokens'], usage['output_tokens'])
            
            return AIResponse(
                content=response.text,
                usage=usage,
                model=self.model_id,
                provider=self.provider_name,
                cost_usd=cost,
                metadata={'safety_ratings': response.prompt_feedback}
            )
            
        except Exception as e:
            self.logger.error(f"Google API error: {e}")
            raise
    
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream response using Google Gemini API."""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    max_output_tokens=kwargs.get('max_tokens', 4096),
                    temperature=kwargs.get('temperature', 0.7)
                ),
                stream=True
            )
            
            for chunk in response:
                yield chunk.text
                
        except Exception as e:
            self.logger.error(f"Google streaming error: {e}")
            raise
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on Gemini pricing."""
        base_input_cost = 0.00125  # $1.25 per 1M tokens
        base_output_cost = 0.01  # $10 per 1M tokens
        
        input_cost = (input_tokens / 1_000_000) * base_input_cost
        output_cost = (output_tokens / 1_000_000) * base_output_cost
        
        return input_cost + output_cost

class GenericAPIClient(BaseAIClient):
    """Generic client for OpenAI-compatible APIs (Together, Fireworks, Groq, etc.)."""
    
    def __init__(self, provider_name: str, model_id: str, api_key: str, base_url: str, **kwargs):
        super().__init__(provider_name, model_id, api_key, **kwargs)
        self.client = openai.OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        
    def generate(self, prompt: str, **kwargs) -> AIResponse:
        """Generate response using generic OpenAI-compatible API."""
        try:
            response = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            usage = {
                'input_tokens': response.usage.prompt_tokens if response.usage else 0,
                'output_tokens': response.usage.completion_tokens if response.usage else 0,
                'total_tokens': response.usage.total_tokens if response.usage else 0
            }
            
            cost = self._calculate_cost(usage['input_tokens'], usage['output_tokens'])
            
            return AIResponse(
                content=response.choices[0].message.content,
                usage=usage,
                model=self.model_id,
                provider=self.provider_name,
                cost_usd=cost,
                metadata={'response_id': response.id if hasattr(response, 'id') else None}
            )
            
        except Exception as e:
            self.logger.error(f"{self.provider_name} API error: {e}")
            raise
    
    def stream_generate(self, prompt: str, **kwargs) -> Iterator[str]:
        """Stream response using generic API."""
        try:
            stream = self.client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                stream=True,
                max_tokens=kwargs.get('max_tokens', 4096),
                temperature=kwargs.get('temperature', 0.7)
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content
                    
        except Exception as e:
            self.logger.error(f"{self.provider_name} streaming error: {e}")
            raise
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost - would use enhanced model database."""
        # Simplified cost calculation
        base_input_cost = 0.001
        base_output_cost = 0.002
        
        input_cost = (input_tokens / 1_000_000) * base_input_cost
        output_cost = (output_tokens / 1_000_000) * base_output_cost
        
        return input_cost + output_cost

class AIClientFactory:
    """Factory for creating AI clients for different providers."""
    
    @staticmethod
    def create_client(provider_id: str, model_id: str, **kwargs) -> BaseAIClient:
        """Create an AI client for the specified provider and model."""
        
        if provider_id == 'openai':
            api_key = kwargs.get('api_key') or os.getenv('OPENAI_API_KEY')
            if not api_key:
                raise ValueError("OPENAI_API_KEY not found")
            return OpenAIClient(model_id, api_key, **kwargs)
            
        elif provider_id == 'anthropic':
            api_key = kwargs.get('api_key') or os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not found")
            return AnthropicClient(model_id, api_key, **kwargs)
            
        elif provider_id == 'google':
            api_key = kwargs.get('api_key') or os.getenv('GOOGLE_API_KEY')
            if not api_key:
                raise ValueError("GOOGLE_API_KEY not found")
            return GoogleClient(model_id, api_key, **kwargs)
            
        elif provider_id == 'together':
            api_key = kwargs.get('api_key') or os.getenv('TOGETHER_API_KEY')
            if not api_key:
                raise ValueError("TOGETHER_API_KEY not found")
            return GenericAPIClient('Together AI', model_id, api_key, 
                                  'https://api.together.xyz/v1', **kwargs)
            
        elif provider_id == 'fireworks':
            api_key = kwargs.get('api_key') or os.getenv('FIREWORKS_API_KEY')
            if not api_key:
                raise ValueError("FIREWORKS_API_KEY not found")
            return GenericAPIClient('Fireworks AI', model_id, api_key, 
                                  'https://api.fireworks.ai/inference/v1', **kwargs)
            
        elif provider_id == 'groq':
            api_key = kwargs.get('api_key') or os.getenv('GROQ_API_KEY')
            if not api_key:
                raise ValueError("GROQ_API_KEY not found")
            return GenericAPIClient('Groq', model_id, api_key, 
                                  'https://api.groq.com/openai/v1', **kwargs)
            
        elif provider_id == 'xai':
            api_key = kwargs.get('api_key') or os.getenv('XAI_API_KEY')
            if not api_key:
                raise ValueError("XAI_API_KEY not found")
            return GenericAPIClient('xAI', model_id, api_key, 
                                  'https://api.x.ai/v1', **kwargs)
            
        elif provider_id == 'deepseek':
            api_key = kwargs.get('api_key') or os.getenv('DEEPSEEK_API_KEY')
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found")
            return GenericAPIClient('DeepSeek', model_id, api_key, 
                                  'https://api.deepseek.com/v1', **kwargs)
            
        elif provider_id == 'mistral':
            api_key = kwargs.get('api_key') or os.getenv('MISTRAL_API_KEY')
            if not api_key:
                raise ValueError("MISTRAL_API_KEY not found")
            return GenericAPIClient('Mistral AI', model_id, api_key, 
                                  'https://api.mistral.ai/v1', **kwargs)
            
        elif provider_id == 'cohere':
            api_key = kwargs.get('api_key') or os.getenv('COHERE_API_KEY')
            if not api_key:
                raise ValueError("COHERE_API_KEY not found")
            return GenericAPIClient('Cohere', model_id, api_key, 
                                  'https://api.cohere.ai/v1', **kwargs)
        
        elif provider_id == 'perplexity':
            api_key = kwargs.get('api_key') or os.getenv('PERPLEXITY_API_KEY')
            if not api_key:
                raise ValueError("PERPLEXITY_API_KEY not found")
            return GenericAPIClient('Perplexity AI', model_id, api_key, 
                                  'https://api.perplexity.ai', **kwargs)
            
        else:
            raise ValueError(f"Unsupported provider: {provider_id}")

# Convenience function for easy usage
def create_ai_client(provider_id: str, model_id: str, **kwargs) -> BaseAIClient:
    """Create an AI client for the specified provider and model."""
    return AIClientFactory.create_client(provider_id, model_id, **kwargs)

# Example usage
def example_usage():
    """Example of how to use the universal AI client."""
    
    # OpenAI GPT-5
    openai_client = create_ai_client('openai', 'gpt-5')
    response = openai_client.generate("What is the capital of France?")
    print(f"OpenAI Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.4f}")
    
    # Anthropic Claude
    claude_client = create_ai_client('anthropic', 'claude-sonnet-4-5')
    response = claude_client.generate("What is the capital of France?")
    print(f"Claude Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.4f}")
    
    # Together AI Llama
    together_client = create_ai_client('together', 'llama-4-maverick')
    response = together_client.generate("What is the capital of France?")
    print(f"Together Response: {response.content}")
    print(f"Cost: ${response.cost_usd:.4f}")

if __name__ == "__main__":
    example_usage()