# AI Model Names Guide

## Important: Using Actual API Model Identifiers

The model names in `config/config.yaml` and `scripts/interactive_interviews.py` need to match the **exact model identifiers** used by each provider's API.

---

## Anthropic Claude Models (2025)

### ✅ Current Models (Working)

| Display Name | **API Model ID** | Cost (per 1M tokens) | Context | Max Output | Features |
|--------------|------------------|----------------------|---------|------------|----------|
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | $3.00 / $15.00 | 200K | 64K | Extended Thinking, Priority Tier |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 / $5.00 | 200K | 64K | Extended Thinking, Fastest |
| Claude Opus 4.1 | `claude-opus-4-1` | $15.00 / $75.00 | 200K | 32K | Extended Thinking, Specialized Reasoning |

**Model Descriptions:**
- **Claude Sonnet 4.5**: Smartest model for complex agents and coding. Fast latency. Knowledge cutoff: Jan 2025.
- **Claude Haiku 4.5**: Fastest model with near-frontier intelligence. Knowledge cutoff: Feb 2025.
- **Claude Opus 4.1**: Exceptional model for specialized reasoning tasks. Moderate latency. Knowledge cutoff: Jan 2025.

**All Models Support:**
- ✅ Extended Thinking mode
- ✅ Priority Tier access
- ✅ Batch API (50% discount)
- ✅ 200K token context window (1M tokens beta for Sonnet 4.5)

**Official Documentation**: https://docs.anthropic.com/en/docs/about-claude/models

---

## OpenAI Models (2025)

### ✅ Current Models (Working)

| Display Name | **API Model ID** | Cost (per 1M tokens) | Context | Max Output | Features |
|--------------|------------------|----------------------|---------|------------|----------|
| GPT-5 | `gpt-5` | $1.25 / $10.00 | 400K | 128K | Batch API, Cached Input, Image Input |
| GPT-5 Pro | `gpt-5-pro` | $15.00 / $120.00 | 400K | 272K | Batch API, Image Input |
| GPT-5 (ChatGPT) | `gpt-5-chatgpt` | $1.25 / $10.00 | 128K | 16K | Batch API, Cached Input, Image Input |

**Model Descriptions:**
- **GPT-5**: Best model for coding and agentic tasks across domains. Cached input: $0.13/1M tokens. Knowledge cutoff: Sep 2024.
- **GPT-5 Pro**: Smarter and more precise responses for complex reasoning. Maximum output: 272K tokens. Knowledge cutoff: Sep 2024.
- **GPT-5 (ChatGPT)**: GPT-5 optimized for chat with 128K context window. Cached input: $0.13/1M tokens. Knowledge cutoff: Sep 2024.

**All Models Support:**
- ✅ Batch API (50% discount)
- ✅ Streaming responses
- ✅ Function calling
- ✅ Structured outputs
- ✅ Distillation

**Batch Pricing:**
- GPT-5: $0.625 / $5.00 per 1M tokens
- GPT-5 Pro: $7.50 / $60.00 per 1M tokens
- GPT-5 (ChatGPT): $0.625 / $5.00 per 1M tokens

**Official Documentation**: https://platform.openai.com/docs/models

---

## Google Gemini Models (2025)

### ✅ Current Models (Working)

| Display Name | **API Model ID** | Cost (per 1M tokens) | Context | Max Output | Features |
|--------------|------------------|----------------------|---------|------------|----------|
| Gemini 2.5 Pro | `gemini-2.5-pro` | $1.25 / $10.00 | 1M | 65K | Thinking, Batch API |
| Gemini 2.5 Flash | `gemini-2.5-flash` | $0.15 / $1.25 | 1M | 65K | Thinking, Batch API |
| Gemini 2.5 Flash-Lite | `gemini-2.5-flash-lite` | $0.10 / $0.40 | 1M | 65K | Thinking, Batch API |
| Gemini 2.0 Flash | `gemini-2.0-flash` | $0.05 / $0.20 | 1M | 8K | Batch API |

**Model Descriptions:**
- **Gemini 2.5 Pro**: State-of-the-art thinking model for complex reasoning in code, math, and STEM. Knowledge cutoff: Jan 2025.
- **Gemini 2.5 Flash**: Best price-performance model for large-scale processing and agentic use cases. Knowledge cutoff: Jan 2025.
- **Gemini 2.5 Flash-Lite**: Fastest flash model optimized for cost-efficiency and high throughput. Knowledge cutoff: Jan 2025.
- **Gemini 2.0 Flash**: Second generation workhorse model with 1M context window. Knowledge cutoff: Aug 2024.

**All 2.5 Models Support:**
- ✅ Thinking mode for complex reasoning
- ✅ Batch API (50% discount)
- ✅ 1,048,576 token context window
- ✅ Code execution
- ✅ Function calling
- ✅ Search grounding
- ✅ Structured outputs

**Official Documentation**: https://ai.google.dev/models/gemini

---

## How to Update Model Names

### Option 1: Update config.yaml

Edit `config/config.yaml`:

```yaml
# Change this:
active_model: "claude-4.5-sonnet"

# To this:
active_model: "claude-sonnet-4-5-20250929"
```

### Option 2: Use Command Line

Override the model when running interviews:

```bash
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 10
```

### Option 3: Update Interactive Launcher

Edit `scripts/interactive_interviews.py` and update the `MODELS_DATABASE` dictionary with correct API model IDs.

---

## Testing Model Names

To verify a model name works:

```bash
# Set your API key
export ANTHROPIC_API_KEY="your-key-here"

# Test with 1 interview
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 1
```

If you see:
- ✅ **"Initialized Claude provider"** → Model name is correct
- ❌ **"model: ... not found"** → Model name is incorrect

---

## Finding Current Model Names

### Anthropic Claude
```bash
# Check official docs
curl https://docs.anthropic.com/en/api/models
```

### OpenAI
```bash
# List available models (requires API key)
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer $OPENAI_API_KEY"
```

### Google Gemini
```bash
# Check official docs
curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GOOGLE_API_KEY"
```

---

## Common Issues

### Issue: "model: claude-4.5-sonnet not found"

**Problem**: Using display name instead of API identifier
**Solution**: Use `claude-sonnet-4-5-20250929` instead

### Issue: "GPT-5 model not found"

**Problem**: GPT-5 doesn't exist yet (as of January 2025)
**Solution**: Use `gpt-4o` or `gpt-4-turbo` instead

### Issue: "Gemini 2.5 not found"

**Problem**: Gemini 2.x isn't released yet
**Solution**: Use `gemini-1.5-pro` or `gemini-1.5-flash`

---

## Recommended Models (Actual API IDs)

### For Production (10,000 interviews)

| Provider | Model | API ID | Est. Cost |
|----------|-------|--------|-----------|
| Anthropic | Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | ~$390 |
| OpenAI | GPT-4o | `gpt-4o` | ~$625 |
| Google | Gemini 1.5 Pro | `gemini-1.5-pro` | ~$312 |

### For Testing (10 interviews)

| Provider | Model | API ID | Est. Cost |
|----------|-------|--------|-----------|
| Anthropic | Claude 3.5 Haiku | `claude-3-5-haiku-20241022` | ~$0.20 |
| OpenAI | GPT-4o mini | `gpt-4o-mini` | ~$0.15 |
| Google | Gemini 1.5 Flash | `gemini-1.5-flash` | ~$0.08 |

---

## Summary

**Key Points:**
1. ✅ Always use **exact API model IDs** from provider documentation
2. ❌ Don't use display names like "Claude 4.5 Sonnet" in code
3. 🔍 Model IDs often include version dates (e.g., `-20250929`)
4. 📝 Check provider docs regularly as models change
5. 🧪 Test with 1 interview before running 10,000

**Quick Fix Command:**
```bash
# Replace fictional model names with working ones
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 1
```
