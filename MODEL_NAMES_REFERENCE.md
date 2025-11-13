# ⚡ Model Names Quick Reference

## The Issue: Model Names Must Be EXACT

Scripts use a **specific model database** with exact naming conventions.

### ❌ These WILL NOT WORK:
```
--model claude
--model claude-4.5-sonnet
--model gpt-5-pro
--model gemini-2-flash
--model grok-fast
```

### ✅ These WILL WORK:

---

## Anthropic (Claude)

| Use Case | Exact Model Name | Cost/Interview | Speed |
|----------|-----------------|-----------------|-------|
| BEST FOR MOST CASES | `claude-sonnet-4-5-20250929` | $0.034 | ⚡⚡⚡ |
| Complex Reasoning | `claude-opus-4-1` | $0.15 | ⚡⚡ |
| Fast & Budget | `claude-haiku-4-5` | $0.011 | ⚡⚡⚡⚡ |

**Example:**
```bash
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 10
```

---

## xAI (Grok) - ⭐ BEST VALUE

| Use Case | Exact Model Name | Cost/Interview | Speed |
|----------|-----------------|-----------------|-------|
| RECOMMENDED | `grok-4-fast` | $0.034 | ⚡⚡⚡⚡ |
| Premium Quality | `grok-4` | $0.504 | ⚡⚡⚡ |
| Budget Option | `grok-3` | $0.068 | ⚡⚡⚡ |

**Example:**
```bash
export XAI_API_KEY="your-key-here"
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --count 10
```

---

## OpenAI (GPT)

| Use Case | Exact Model Name | Cost/Interview | Speed |
|----------|-----------------|-----------------|-------|
| Standard | `gpt-5` | $0.25 | ⚡⚡⚡⚡ |

**Example:**
```bash
python scripts/04_conduct_interviews.py \
  --provider openai \
  --model gpt-5 \
  --count 10
```

---

## Google (Gemini)

| Use Case | Exact Model Name | Cost/Interview | Speed |
|----------|-----------------|-----------------|-------|
| CHEAPEST | `gemini-2.5-flash` | $0.002 | ⚡⚡⚡⚡⚡ |

**Example:**
```bash
python scripts/04_conduct_interviews.py \
  --provider google \
  --model gemini-2.5-flash \
  --count 10
```

---

## Complete Command Templates

### Claude Sonnet (Recommended Default)
```bash
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 10
```

### Grok-4-Fast (Best Value)
```bash
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --count 10
```

### Gemini Flash (Cheapest)
```bash
python scripts/04_conduct_interviews.py \
  --provider google \
  --model gemini-2.5-flash \
  --count 10
```

### Full Workflow Pipeline
```bash
python run_pipeline.py --preset quick_test
```

---

## How to Find Model Names

If you need to verify model names:

```bash
# View all models and their specs
grep -A 5 "'models':" run_pipeline.py | head -50

# Or check the database file
cat AImodels.csv | grep "claude\|gpt\|gemini\|grok"

# Or check documentation
cat docs/AI_MODELS_DATABASE.csv
```

---

## Cost Comparison (1000 Interviews)

| Provider | Model | 1000 Interviews | Speed |
|----------|-------|-----------------|-------|
| 🏆 Google | gemini-2.5-flash | $2.00 | Fastest |
| ✅ xAI | grok-4-fast | $34.00 | Very Fast |
| ✅ Anthropic | claude-sonnet-4-5-20250929 | $34.00 | Very Fast |
| ⚡ Anthropic | claude-haiku-4-5 | $11.00 | Fastest |
| 💎 Anthropic | claude-opus-4-1 | $150.00 | Fast |
| 🚀 xAI | grok-4 | $504.00 | Fast |

---

## Troubleshooting: Wrong Model Name

If you get error: `Model [X] not found for provider [Y]`

**Step 1: Check spelling**
- Look at your command
- Compare to table above
- Must match EXACTLY

**Step 2: Check format**
```
WRONG: claude-4.5-sonnet
RIGHT: claude-sonnet-4-5-20250929
        ↑ notice: 4-5 not 4.5, and version suffix
```

**Step 3: Verify provider matches model**
```
WRONG: --provider anthropic --model grok-4-fast
RIGHT: --provider xai --model grok-4-fast
```

**Step 4: Get current list**
```bash
python -c "
import run_pipeline
for provider, info in run_pipeline.PROVIDERS.items():
    print(f'{provider}:')
    for model in info['models'].keys():
        print(f'  - {model}')
"
```

---

## Remember

- **Copy-paste the exact model name** from the green checkmarks above
- **Match provider to model** (don't mix anthropic with grok)
- **If unsure, use**: `--provider anthropic --model claude-sonnet-4-5-20250929`

---

## Bookmark This!

Save this file location: `/home/user/202511-Gravidas/MODEL_NAMES_REFERENCE.md`

Use it whenever you run interviews:
```bash
cat /home/user/202511-Gravidas/MODEL_NAMES_REFERENCE.md
```

---

**Last Updated**: 2025-11-12
**Status**: Ready to Use
