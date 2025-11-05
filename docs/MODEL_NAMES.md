# AI Model Names Guide

## Important: Using Actual API Model Identifiers

The model names in `config/config.yaml` and `scripts/interactive_interviews.py` need to match the **exact model identifiers** used by each provider's API.

---

## Anthropic Claude Models (2025)

### ✅ Current Models (Working)

| Display Name | **API Model ID** | Cost (per 1M tokens) | Context |
|--------------|------------------|----------------------|---------|
| Claude Sonnet 4.5 | `claude-sonnet-4-5-20250929` | $3.00 / $15.00 | 200K |
| Claude Haiku 4.5 | `claude-haiku-4-5` | $1.00 / $5.00 | 200K |
| Claude 3.5 Sonnet | `claude-3-5-sonnet-20241022` | $3.00 / $15.00 | 200K |
| Claude 3.5 Haiku | `claude-3-5-haiku-20241022` | $1.00 / $5.00 | 200K |

**Official Documentation**: https://docs.anthropic.com/en/docs/about-claude/models

---

## OpenAI Models (2025)

### ✅ Current Models (Working)

As of January 2025, these are the most common OpenAI models:

| Display Name | **API Model ID** | Cost (per 1M tokens) | Context |
|--------------|------------------|----------------------|---------|
| GPT-4o | `gpt-4o` | $2.50 / $10.00 | 128K |
| GPT-4o mini | `gpt-4o-mini` | $0.15 / $0.60 | 128K |
| GPT-4 Turbo | `gpt-4-turbo` | $10.00 / $30.00 | 128K |
| GPT-4 | `gpt-4` | $30.00 / $60.00 | 8K |
| GPT-3.5 Turbo | `gpt-3.5-turbo` | $0.50 / $1.50 | 16K |

**Note**: GPT-5 models mentioned in config are **fictional/placeholder** names. Use GPT-4o for best current performance.

**Official Documentation**: https://platform.openai.com/docs/models

---

## Google Gemini Models (2025)

### ✅ Current Models (Working)

| Display Name | **API Model ID** | Cost (per 1M tokens) | Context |
|--------------|------------------|----------------------|---------|
| Gemini 1.5 Pro | `gemini-1.5-pro` | $1.25 / $5.00 | 2M |
| Gemini 1.5 Flash | `gemini-1.5-flash` | $0.075 / $0.30 | 1M |
| Gemini 1.0 Pro | `gemini-1.0-pro` | $0.50 / $1.50 | 32K |

**Note**: Gemini 2.x models mentioned in config are **not yet released**. Use Gemini 1.5 Pro for best performance.

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
