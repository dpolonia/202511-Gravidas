#!/usr/bin/env python3
"""
Enhanced AI Models Database (2025) - Comprehensive Provider Support

This module contains the complete database of AI models from the AImodels.csv file,
organized by provider with API key requirements and connection details.

Supports 15+ providers with 60+ models for maximum flexibility.
"""

from typing import Dict, Any, List
import os

# Enhanced model database based on AImodels.csv
ENHANCED_MODELS_DATABASE = {
    'openai': {
        'name': 'OpenAI',
        'api_key_env': 'OPENAI_API_KEY',
        'base_url': 'https://api.openai.com/v1',
        'models': {
            'gpt-5': {
                'name': 'GPT-5',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'context_window': 1000000,
                'max_output': 128000,
                'quality': 'Excellent',
                'description': 'Latest flagship model with advanced reasoning',
                'recommended': True
            },
            'gpt-5-mini': {
                'name': 'GPT-5 mini',
                'cost_input': 0.25,
                'cost_output': 2.0,
                'batch_available': True,
                'batch_input': 0.125,
                'batch_output': 1.0,
                'context_window': 128000,
                'max_output': 16384,
                'quality': 'Very Good',
                'description': 'Fast and cost-effective GPT-5 variant'
            },
            'gpt-5-nano': {
                'name': 'GPT-5 nano',
                'cost_input': 0.05,
                'cost_output': 0.40,
                'batch_available': True,
                'batch_input': 0.025,
                'batch_output': 0.20,
                'context_window': 32000,
                'max_output': 8192,
                'quality': 'Good',
                'description': 'Ultra-fast model for simple tasks'
            },
            'gpt-4-1': {
                'name': 'GPT-4.1',
                'cost_input': 2.0,
                'cost_output': 8.0,
                'batch_available': True,
                'batch_input': 1.0,
                'batch_output': 4.0,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Excellent',
                'description': 'Enhanced GPT-4 with improved performance'
            },
            'gpt-4o': {
                'name': 'GPT-4o (Vision)',
                'cost_input': 2.5,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 1.25,
                'batch_output': 5.0,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Excellent',
                'features': ['vision', 'multimodal'],
                'description': 'Multimodal GPT-4 with vision capabilities'
            },
            'gpt-4o-mini': {
                'name': 'GPT-4o mini',
                'cost_input': 0.15,
                'cost_output': 0.60,
                'batch_available': True,
                'batch_input': 0.075,
                'batch_output': 0.30,
                'context_window': 128000,
                'max_output': 16384,
                'quality': 'Very Good',
                'features': ['vision', 'multimodal'],
                'description': 'Compact multimodal model'
            }
        }
    },
    
    'anthropic': {
        'name': 'Anthropic (Claude)',
        'api_key_env': 'ANTHROPIC_API_KEY',
        'base_url': 'https://api.anthropic.com',
        'models': {
            'claude-opus-4-1': {
                'name': 'Claude 4.1 Opus',
                'cost_input': 15.0,
                'cost_output': 75.0,
                'batch_available': True,
                'batch_input': 7.5,
                'batch_output': 37.5,
                'context_window': 200000,
                'max_output': 32000,
                'quality': 'Exceptional',
                'description': 'Flagship model for complex reasoning',
                'recommended': True
            },
            'claude-sonnet-4-5': {
                'name': 'Claude 4.5 Sonnet',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'context_window': 200000,
                'max_output': 64000,
                'quality': 'Excellent',
                'description': 'Balanced performance and cost',
                'recommended': True
            },
            'claude-sonnet-4-5-20250929': {
                'name': 'Claude Sonnet 4.5 (2025-09-29)',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'context_window': 200000,
                'max_output': 64000,
                'quality': 'Excellent',
                'description': 'Claude Sonnet 4.5 versioned release',
                'recommended': True
            },
            'claude-haiku-4-5': {
                'name': 'Claude 4.5 Haiku',
                'cost_input': 1.0,
                'cost_output': 5.0,
                'batch_available': True,
                'batch_input': 0.5,
                'batch_output': 2.5,
                'context_window': 200000,
                'max_output': 32000,
                'quality': 'Very Good',
                'description': 'Fast and economical'
            }
        }
    },
    
    'google': {
        'name': 'Google (Vertex AI)',
        'api_key_env': 'GOOGLE_API_KEY',
        'base_url': 'https://generativelanguage.googleapis.com/v1',
        'models': {
            'gemini-2.5-pro': {
                'name': 'Gemini 2.5 Pro (≤200k)',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'context_window': 200000,
                'max_output': 65536,
                'quality': 'Excellent',
                'description': 'Pro model for standard context',
                'recommended': True
            },
            'gemini-2.5-pro-long': {
                'name': 'Gemini 2.5 Pro (>200k)',
                'cost_input': 2.5,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.25,
                'batch_output': 7.5,
                'context_window': 1000000,
                'max_output': 65536,
                'quality': 'Excellent',
                'description': 'Pro model for long context'
            },
            'gemini-2.5-flash': {
                'name': 'Gemini 2.5 Flash',
                'cost_input': 0.15,
                'cost_output': 1.25,
                'batch_available': True,
                'batch_input': 0.075,
                'batch_output': 0.625,
                'context_window': 1000000,
                'max_output': 65536,
                'quality': 'Very Good',
                'description': 'Fast and cost-effective'
            }
        }
    },
    
    'aws': {
        'name': 'AWS Bedrock',
        'api_key_env': 'AWS_ACCESS_KEY_ID',
        'additional_env': ['AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION'],
        'base_url': 'https://bedrock-runtime.{region}.amazonaws.com',
        'models': {
            'bedrock-claude-sonnet-4-5': {
                'name': 'Claude 4.5 Sonnet (Bedrock)',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'context_window': 200000,
                'max_output': 64000,
                'quality': 'Excellent',
                'description': 'Claude via AWS Bedrock'
            },
            'bedrock-llama-3.2-90b': {
                'name': 'Llama 3.2 90B (Bedrock)',
                'cost_input': 2.0,
                'cost_output': 2.0,
                'batch_available': True,
                'batch_input': 1.0,
                'batch_output': 1.0,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Open source via AWS'
            },
            'bedrock-titan-express': {
                'name': 'Amazon Titan Text Express',
                'cost_input': 0.8,
                'cost_output': 1.6,
                'batch_available': True,
                'batch_input': 0.4,
                'batch_output': 0.8,
                'context_window': 32000,
                'max_output': 8192,
                'quality': 'Good',
                'description': 'Amazon native model'
            }
        }
    },
    
    'azure': {
        'name': 'Microsoft Azure AI',
        'api_key_env': 'AZURE_OPENAI_KEY',
        'additional_env': ['AZURE_OPENAI_ENDPOINT'],
        'base_url': 'https://{endpoint}.openai.azure.com',
        'models': {
            'azure-gpt-5': {
                'name': 'GPT-5 (Azure)',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 5.0,
                'context_window': 1000000,
                'max_output': 128000,
                'quality': 'Excellent',
                'description': 'GPT-5 via Azure OpenAI'
            },
            'azure-gpt-4-1': {
                'name': 'GPT-4.1 (Azure)',
                'cost_input': 2.0,
                'cost_output': 8.0,
                'batch_available': True,
                'batch_input': 1.0,
                'batch_output': 4.0,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Excellent',
                'description': 'GPT-4.1 via Azure OpenAI'
            },
            'azure-gpt-4o': {
                'name': 'GPT-4o (Azure)',
                'cost_input': 2.5,
                'cost_output': 10.0,
                'batch_available': True,
                'batch_input': 1.25,
                'batch_output': 5.0,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Excellent',
                'features': ['vision', 'multimodal'],
                'description': 'GPT-4o via Azure OpenAI'
            }
        }
    },
    
    'azure-foundry': {
        'name': 'Azure AI Foundry (MaaS)',
        'api_key_env': 'AZURE_AI_FOUNDRY_KEY',
        'additional_env': ['AZURE_AI_FOUNDRY_ENDPOINT'],
        'base_url': 'https://{endpoint}.inference.ml.azure.com',
        'models': {
            'llama-4-maverick-17b': {
                'name': 'Llama 4 Maverick 17B',
                'cost_input': 0.25,
                'cost_output': 1.0,
                'batch_available': True,
                'batch_input': 0.125,
                'batch_output': 0.5,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Meta Llama via Azure MaaS'
            },
            'llama-3.3-70b': {
                'name': 'Llama 3.3 70B',
                'cost_input': 0.71,
                'cost_output': 0.71,
                'batch_available': True,
                'batch_input': 0.355,
                'batch_output': 0.355,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Meta Llama 3.3 via Azure'
            },
            'azure-grok-4': {
                'name': 'Grok 4 (Azure)',
                'cost_input': 5.5,
                'cost_output': 27.5,
                'batch_available': True,
                'batch_input': 2.75,
                'batch_output': 13.75,
                'context_window': 2000000,
                'max_output': 65536,
                'quality': 'Excellent',
                'description': 'xAI Grok via Azure MaaS'
            },
            'azure-grok-3': {
                'name': 'Grok 3 (Azure)',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': True,
                'batch_input': 1.5,
                'batch_output': 7.5,
                'context_window': 1000000,
                'max_output': 32768,
                'quality': 'Excellent',
                'description': 'xAI Grok 3 via Azure MaaS'
            },
            'azure-grok-3-mini': {
                'name': 'Grok 3 Mini (Azure)',
                'cost_input': 0.25,
                'cost_output': 1.27,
                'batch_available': True,
                'batch_input': 0.125,
                'batch_output': 0.635,
                'context_window': 128000,
                'max_output': 16384,
                'quality': 'Good',
                'description': 'Grok 3 Mini via Azure MaaS'
            },
            'deepseek-v3': {
                'name': 'DeepSeek V3 (Azure)',
                'cost_input': 1.14,
                'cost_output': 4.56,
                'batch_available': True,
                'batch_input': 0.57,
                'batch_output': 2.28,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Very Good',
                'description': 'DeepSeek V3 via Azure MaaS'
            },
            'deepseek-r1': {
                'name': 'DeepSeek R1 (Azure)',
                'cost_input': 1.35,
                'cost_output': 5.40,
                'batch_available': True,
                'batch_input': 0.675,
                'batch_output': 2.70,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Very Good',
                'description': 'DeepSeek R1 via Azure MaaS'
            }
        }
    },
    
    'mistral': {
        'name': 'Mistral AI',
        'api_key_env': 'MISTRAL_API_KEY',
        'base_url': 'https://api.mistral.ai/v1',
        'models': {
            'mistral-large-2': {
                'name': 'Mistral Large 2',
                'cost_input': 2.0,
                'cost_output': 6.0,
                'batch_available': False,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Excellent',
                'description': 'Advanced reasoning model'
            },
            'mistral-small-3.2': {
                'name': 'Mistral Small 3.2',
                'cost_input': 0.2,
                'cost_output': 0.6,
                'batch_available': False,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Good',
                'description': 'Fast and economical'
            },
            'ministral-8b': {
                'name': 'Ministral 8B',
                'cost_input': 0.1,
                'cost_output': 0.1,
                'batch_available': False,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Good',
                'description': 'Ultra-fast edge model'
            }
        }
    },
    
    'xai': {
        'name': 'xAI (Direct)',
        'api_key_env': 'XAI_API_KEY',
        'base_url': 'https://api.x.ai/v1',
        'models': {
            'grok-4': {
                'name': 'Grok 4',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'batch_available': False,
                'context_window': 2000000,
                'max_output': 65536,
                'quality': 'Excellent',
                'description': 'Advanced reasoning with real-time knowledge'
            },
            'grok-4-fast': {
                'name': 'Grok 4 Fast (Reasoning)',
                'cost_input': 0.2,
                'cost_output': 0.5,
                'batch_available': False,
                'context_window': 2000000,
                'max_output': 32768,
                'quality': 'Very Good',
                'description': 'Fast reasoning mode'
            },
            'grok-3-mini': {
                'name': 'Grok 3 Mini',
                'cost_input': 0.3,
                'cost_output': 0.5,
                'batch_available': False,
                'context_window': 128000,
                'max_output': 16384,
                'quality': 'Good',
                'description': 'Compact reasoning model'
            }
        }
    },
    
    'deepseek': {
        'name': 'DeepSeek (Direct)',
        'api_key_env': 'DEEPSEEK_API_KEY',
        'base_url': 'https://api.deepseek.com/v1',
        'models': {
            'deepseek-v3.2-exp': {
                'name': 'DeepSeek-V3.2-Exp',
                'cost_input': 0.28,
                'cost_output': 0.42,
                'batch_available': False,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Very Good',
                'description': 'Experimental reasoning model'
            }
        }
    },
    
    'together': {
        'name': 'Together AI',
        'api_key_env': 'TOGETHER_API_KEY',
        'base_url': 'https://api.together.xyz/v1',
        'models': {
            'llama-3.1-405b': {
                'name': 'Llama 3.1 405B Instruct',
                'cost_input': 3.5,
                'cost_output': 3.5,
                'batch_available': True,
                'batch_input': 1.75,
                'batch_output': 1.75,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Excellent',
                'description': 'Large open source model'
            },
            'llama-4-maverick': {
                'name': 'Llama 4 Maverick',
                'cost_input': 0.27,
                'cost_output': 0.85,
                'batch_available': True,
                'batch_input': 0.135,
                'batch_output': 0.425,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Latest Meta Llama'
            },
            'qwen3-coder-480b': {
                'name': 'Qwen3-Coder 480B',
                'cost_input': 2.0,
                'cost_output': 2.0,
                'batch_available': True,
                'batch_input': 1.0,
                'batch_output': 1.0,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Excellent',
                'description': 'Code generation specialist'
            },
            'deepseek-v3': {
                'name': 'DeepSeek-V3',
                'cost_input': 1.25,
                'cost_output': 1.25,
                'batch_available': True,
                'batch_input': 0.625,
                'batch_output': 0.625,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Very Good',
                'description': 'Advanced reasoning via Together'
            }
        }
    },
    
    'fireworks': {
        'name': 'Fireworks AI',
        'api_key_env': 'FIREWORKS_API_KEY',
        'base_url': 'https://api.fireworks.ai/inference/v1',
        'models': {
            'llama-3.1-405b': {
                'name': 'Llama 3.1 405B',
                'cost_input': 3.0,
                'cost_output': 3.0,
                'batch_available': True,
                'batch_input': 1.8,  # 40% discount
                'batch_output': 1.8,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Excellent',
                'description': 'Large model via Fireworks'
            },
            'llama-4-maverick': {
                'name': 'Llama 4 Maverick',
                'cost_input': 0.22,
                'cost_output': 0.88,
                'batch_available': True,
                'batch_input': 0.132,  # 40% discount
                'batch_output': 0.528,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Latest Llama via Fireworks'
            },
            'qwen3-coder-480b': {
                'name': 'Qwen3 Coder 480B',
                'cost_input': 0.45,
                'cost_output': 1.8,
                'batch_available': True,
                'batch_input': 0.27,  # 40% discount
                'batch_output': 1.08,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Excellent',
                'description': 'Code specialist via Fireworks'
            },
            'deepseek-v3': {
                'name': 'DeepSeek V3 family',
                'cost_input': 0.9,
                'cost_output': 0.9,
                'batch_available': True,
                'batch_input': 0.54,  # 40% discount
                'batch_output': 0.54,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Very Good',
                'description': 'DeepSeek via Fireworks'
            }
        }
    },
    
    'groq': {
        'name': 'Groq',
        'api_key_env': 'GROQ_API_KEY',
        'base_url': 'https://api.groq.com/openai/v1',
        'models': {
            'llama-3.3-70b': {
                'name': 'Llama 3.3 70B',
                'cost_input': 0.59,
                'cost_output': 0.79,
                'batch_available': True,
                'batch_input': 0.295,  # 50% discount
                'batch_output': 0.395,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Fast inference via Groq'
            },
            'llama-3.1-8b': {
                'name': 'Llama 3.1 8B',
                'cost_input': 0.05,
                'cost_output': 0.08,
                'batch_available': True,
                'batch_input': 0.025,  # 50% discount
                'batch_output': 0.04,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Good',
                'description': 'Ultra-fast small model'
            },
            'qwen-3-32b': {
                'name': 'Qwen 3 32B',
                'cost_input': 0.29,
                'cost_output': 0.59,
                'batch_available': True,
                'batch_input': 0.145,  # 50% discount
                'batch_output': 0.295,
                'context_window': 32768,
                'max_output': 8192,
                'quality': 'Very Good',
                'description': 'Balanced model via Groq'
            }
        }
    },
    
    'cohere': {
        'name': 'Cohere',
        'api_key_env': 'COHERE_API_KEY',
        'base_url': 'https://api.cohere.ai/v1',
        'models': {
            'command-r-plus': {
                'name': 'Command R+',
                'cost_input': 2.5,
                'cost_output': 10.0,
                'batch_available': False,
                'context_window': 128000,
                'max_output': 32768,
                'quality': 'Excellent',
                'description': 'Advanced RAG-optimized model'
            },
            'rerank-3.5': {
                'name': 'Rerank 3.5',
                'cost_per_1k_searches': 2.0,
                'batch_available': True,
                'quality': 'Excellent',
                'description': 'Document reranking (per 1k searches)',
                'model_type': 'rerank'
            },
            'embed-4': {
                'name': 'Embed 4',
                'cost_input': 0.12,
                'cost_output': 0.12,
                'batch_available': True,
                'quality': 'Excellent',
                'description': 'Text embeddings',
                'model_type': 'embedding'
            }
        }
    },
    
    'perplexity': {
        'name': 'Perplexity AI',
        'api_key_env': 'PERPLEXITY_API_KEY',
        'base_url': 'https://api.perplexity.ai',
        'models': {
            'sonar-deep-research': {
                'name': 'Sonar Deep Research',
                'cost_per_request': 0.41,
                'batch_available': False,
                'quality': 'Excellent',
                'description': 'Deep research queries',
                'model_type': 'research'
            },
            'sonar-reasoning-pro': {
                'name': 'Sonar Reasoning Pro',
                'cost_input': 2.0,
                'cost_output': 8.0,
                'batch_available': False,
                'context_window': 32768,
                'max_output': 16384,
                'quality': 'Excellent',
                'description': 'Advanced reasoning with search'
            }
        }
    }
}

# Provider authentication requirements
PROVIDER_AUTH_REQUIREMENTS = {
    'openai': {
        'required_env': ['OPENAI_API_KEY'],
        'setup_instructions': 'Get API key from https://platform.openai.com/api-keys'
    },
    'anthropic': {
        'required_env': ['ANTHROPIC_API_KEY'],
        'setup_instructions': 'Get API key from https://console.anthropic.com'
    },
    'google': {
        'required_env': ['GOOGLE_API_KEY'],
        'setup_instructions': 'Get API key from https://makersuite.google.com/app/apikey'
    },
    'aws': {
        'required_env': ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_DEFAULT_REGION'],
        'setup_instructions': 'Configure AWS credentials via AWS CLI or environment variables'
    },
    'azure': {
        'required_env': ['AZURE_OPENAI_KEY', 'AZURE_OPENAI_ENDPOINT'],
        'setup_instructions': 'Get credentials from Azure OpenAI Service in Azure Portal'
    },
    'azure-foundry': {
        'required_env': ['AZURE_AI_FOUNDRY_KEY', 'AZURE_AI_FOUNDRY_ENDPOINT'],
        'setup_instructions': 'Get credentials from Azure AI Foundry'
    },
    'mistral': {
        'required_env': ['MISTRAL_API_KEY'],
        'setup_instructions': 'Get API key from https://console.mistral.ai'
    },
    'xai': {
        'required_env': ['XAI_API_KEY'],
        'setup_instructions': 'Get API key from https://x.ai/api'
    },
    'deepseek': {
        'required_env': ['DEEPSEEK_API_KEY'],
        'setup_instructions': 'Get API key from https://platform.deepseek.com'
    },
    'together': {
        'required_env': ['TOGETHER_API_KEY'],
        'setup_instructions': 'Get API key from https://api.together.xyz/settings/api-keys'
    },
    'fireworks': {
        'required_env': ['FIREWORKS_API_KEY'],
        'setup_instructions': 'Get API key from https://app.fireworks.ai/account/api-keys'
    },
    'groq': {
        'required_env': ['GROQ_API_KEY'],
        'setup_instructions': 'Get API key from https://console.groq.com/keys'
    },
    'cohere': {
        'required_env': ['COHERE_API_KEY'],
        'setup_instructions': 'Get API key from https://dashboard.cohere.ai/api-keys'
    },
    'perplexity': {
        'required_env': ['PERPLEXITY_API_KEY'],
        'setup_instructions': 'Get API key from https://www.perplexity.ai/settings/api'
    }
}

def get_available_providers() -> Dict[str, bool]:
    """Check which providers have configured API keys."""
    available = {}
    
    for provider_id, auth_info in PROVIDER_AUTH_REQUIREMENTS.items():
        required_env = auth_info['required_env']
        has_all_keys = all(os.getenv(key) for key in required_env)
        available[provider_id] = has_all_keys
        
    return available

def get_provider_models(provider_id: str) -> Dict[str, Any]:
    """Get all models for a specific provider."""
    return ENHANCED_MODELS_DATABASE.get(provider_id, {}).get('models', {})

def get_model_info(provider_id: str, model_id: str) -> Dict[str, Any]:
    """Get detailed information for a specific model."""
    provider_models = get_provider_models(provider_id)
    return provider_models.get(model_id, {})

def calculate_cost(model_info: Dict[str, Any], input_tokens: int, output_tokens: int, use_batch: bool = False) -> float:
    """Calculate cost for a given model and token usage."""
    if 'model_type' in model_info:
        # Special pricing models (rerank, embedding, research)
        if model_info['model_type'] == 'rerank':
            # Assume 1 search per 1000 input tokens
            searches = max(1, input_tokens // 1000)
            return searches * model_info.get('cost_per_1k_searches', 0) / 1000
        elif model_info['model_type'] == 'research':
            return model_info.get('cost_per_request', 0)
        elif model_info['model_type'] == 'embedding':
            total_tokens = input_tokens + output_tokens
            return (total_tokens / 1_000_000) * model_info.get('cost_input', 0)
    
    # Standard token-based pricing
    if use_batch and model_info.get('batch_available', False):
        input_cost_per_million = model_info.get('batch_input', model_info.get('cost_input', 0))
        output_cost_per_million = model_info.get('batch_output', model_info.get('cost_output', 0))
    else:
        input_cost_per_million = model_info.get('cost_input', 0)
        output_cost_per_million = model_info.get('cost_output', 0)
    
    input_cost = (input_tokens / 1_000_000) * input_cost_per_million
    output_cost = (output_tokens / 1_000_000) * output_cost_per_million
    
    return input_cost + output_cost

def get_recommended_models() -> List[Dict[str, Any]]:
    """Get list of recommended models across all providers."""
    recommended = []
    
    for provider_id, provider_data in ENHANCED_MODELS_DATABASE.items():
        for model_id, model_info in provider_data['models'].items():
            if model_info.get('recommended', False):
                recommended.append({
                    'provider_id': provider_id,
                    'provider_name': provider_data['name'],
                    'model_id': model_id,
                    'model_info': model_info
                })
    
    return recommended