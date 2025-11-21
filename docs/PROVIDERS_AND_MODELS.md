# AI Providers & Models - Gravidas System

**Last Updated:** November 18, 2025  
**Status:** All 4 configured providers tested and working ✓

---

## Currently Configured & Active Providers

### ✓ Anthropic (Claude) - **ACTIVE**
**Provider ID:** `anthropic`  
**Status:** ✓ Configured & Tested  
**API Endpoint:** https://api.anthropic.com

| Model ID | Model Name | Cost (Input/Output per 1M tokens) | Batch API |
|----------|------------|-----------------------------------|-----------|
| `claude-sonnet-4-5-20250929` ⭐ | Claude Sonnet 4.5 (2025-09-29) | $3.00 / $15.00 | ✓ |
| `claude-haiku-4-5` | Claude 4.5 Haiku | $1.00 / $5.00 | ✓ |
| `claude-opus-4-1` | Claude 4.1 Opus | $15.00 / $75.00 | ✓ |
| `claude-sonnet-4-5` | Claude 4.5 Sonnet | $3.00 / $15.00 | ✓ |

**Workflow Settings:**
- Model: `claude-sonnet-4-5-20250929`
- Max Tokens: 4096
- Temperature: 0.7
- Rate Limit: 50 requests/min
- **Recommended:** Best balance of quality and cost

---

### ✓ OpenAI (GPT)
**Provider ID:** `openai`  
**Status:** ✓ Configured & Tested  
**API Endpoint:** https://api.openai.com/v1

| Model ID | Model Name | Cost (Input/Output per 1M tokens) | Batch API |
|----------|------------|-----------------------------------|-----------|
| `gpt-4o-mini` ⭐ | GPT-4o mini | $0.15 / $0.60 | ✓ |
| `gpt-4o` | GPT-4o (Vision) | $2.50 / $10.00 | ✓ |
| `gpt-4-1` | GPT-4.1 | $2.00 / $8.00 | ✓ |
| `gpt-5` | GPT-5 | $1.25 / $10.00 | ✓ |
| `gpt-5-mini` | GPT-5 mini | $0.25 / $2.00 | ✓ |
| `gpt-5-nano` | GPT-5 nano | $0.05 / $0.40 | ✓ |

**Workflow Settings:**
- Model: `gpt-4o-mini`
- Max Tokens: 4096
- Temperature: 0.7
- Rate Limit: 30 requests/min
- **Recommended:** High quality, good performance

---

### ✓ Google (Gemini)
**Provider ID:** `google`  
**Status:** ✓ Configured & Tested  
**API Endpoint:** https://generativelanguage.googleapis.com/v1

| Model ID | Model Name | Cost (Input/Output per 1M tokens) | Batch API |
|----------|------------|-----------------------------------|-----------|
| `gemini-2.5-flash` ⭐ | Gemini 2.5 Flash | $0.15 / $1.25 | ✓ |
| `gemini-2.5-pro` | Gemini 2.5 Pro (≤200k) | $1.25 / $10.00 | ✓ |
| `gemini-2.5-pro-long` | Gemini 2.5 Pro (>200k) | $2.50 / $15.00 | ✓ |

**Workflow Settings:**
- Model: `gemini-2.5-flash`
- Max Tokens: 4096
- Temperature: 0.7
- Rate Limit: 30 requests/min
- **Recommended:** Best value, very fast

---

### ✓ xAI (Grok)
**Provider ID:** `xai`  
**Status:** ✓ Configured & Tested  
**API Endpoint:** https://api.x.ai/v1

| Model ID | Model Name | Cost (Input/Output per 1M tokens) | Batch API |
|----------|------------|-----------------------------------|-----------|
| `grok-4-fast` ⭐ | Grok 4 Fast (Reasoning) | $0.20 / $0.50 | ✗ |
| `grok-4` | Grok 4 | $3.00 / $15.00 | ✗ |
| `grok-3-mini` | Grok 3 Mini | $0.30 / $0.50 | ✗ |

**Workflow Settings:**
- Model: `grok-4-fast`
- Max Tokens: 4096
- Temperature: 0.7
- Rate Limit: 20 requests/min
- **Recommended:** Fastest, best value for money

---

## Additional Providers Available (Not Configured)

The system supports 14 total providers with 49 models. The following providers are available but not currently configured:

| Provider | Models Available | Configuration Required |
|----------|-----------------|------------------------|
| AWS Bedrock | 3 | AWS credentials + region |
| Microsoft Azure AI | 3 | Azure API key + endpoint |
| Azure AI Foundry (MaaS) | 7 | Azure subscription |
| Cohere | 3 | Cohere API key |
| DeepSeek (Direct) | 1 | DeepSeek API key |
| Fireworks AI | 4 | Fireworks API key |
| Groq | 3 | Groq API key |
| Mistral AI | 3 | Mistral API key |
| Perplexity AI | 2 | Perplexity API key |
| Together AI | 4 | Together API key |

---

## How to Switch Providers

### Command Line:
```bash
# Use Anthropic (default)
python scripts/run_workflow.py --provider anthropic

# Use OpenAI
python scripts/run_workflow.py --provider openai

# Use Google Gemini
python scripts/run_workflow.py --provider google

# Use xAI Grok
python scripts/run_workflow.py --provider xai
```

### Configuration File:
Edit `config/workflow_config.yaml` and change the `active_provider` setting:

```yaml
ai_provider:
  active_provider: "anthropic"  # Change to: openai, google, or xai
```

---

## Cost Comparison (Per 1M Tokens)

**Most Economical for Input:**
1. GPT-5 nano: $0.05
2. Gemini 2.5 Flash: $0.15
3. GPT-4o mini: $0.15

**Most Economical for Output:**
1. GPT-5 nano: $0.40
2. Grok 4 Fast: $0.50
3. Grok 3 Mini: $0.50

**Best Overall Value:**
- **grok-4-fast**: $0.20 / $0.50 (cheapest reasoning model)
- **gemini-2.5-flash**: $0.15 / $1.25 (fast, efficient)
- **gpt-4o-mini**: $0.15 / $0.60 (excellent quality/cost ratio)

---

## System Status

✓ All 4 providers configured  
✓ All 4 providers tested successfully  
✓ Multi-provider mode enabled  
✓ Model names validated  
✓ API keys verified  

**Total Available:**
- 14 providers
- 49 models
- 4 active and ready to use
