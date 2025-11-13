# Grok (xAI) Integration Setup & Usage Guide

## Quick Start

**If you have a Grok API key:**

```bash
# Set the API key
export XAI_API_KEY="your-grok-api-key-here"

# Run interviews with Grok
cd /home/user/202511-Gravidas
python scripts/04_conduct_interviews.py --provider xai --model grok-4-fast --count 10

# Or use the pipeline with Grok
python run_pipeline.py --provider xai --preset quick_test
```

---

## Getting a Grok API Key

### Step 1: Create xAI Account

1. Go to: **https://console.x.ai**
2. Click "Sign Up" or "Sign In"
3. Complete the registration (accepts email or X/Twitter account)

### Step 2: Create API Key

1. Navigate to **API Keys** section
2. Click **"Create New Key"**
3. Give it a name like "Gravidas Pipeline"
4. Copy the key (save it safely!)

### Step 3: Set in Environment

**Option A: Quick (Session Only)**
```bash
export XAI_API_KEY="xai-your-actual-key-here"
```

**Option B: Permanent (.env file)**
```bash
# Edit your .env file
nano .env

# Add or update this line:
XAI_API_KEY=xai-your-actual-key-here

# Save (Ctrl+X, Y, Enter in nano)
```

**Option C: Config File**
```bash
# Edit config/workflow_config.yaml
nano config/workflow_config.yaml

# Update the xai section:
xai:
  model: "grok-4-fast"
  api_key: "xai-your-actual-key-here"  # Replace with your actual key
  max_tokens: 4096
  temperature: 0.7
```

---

## Available Grok Models

### Recommended: **grok-4-fast** ⭐

Best combination of speed and cost for most use cases.

**Cost**: $0.2 input / $0.5 output per 1M tokens
**Speed**: 100 tokens/second
**Context**: 2M tokens
**Use case**: Most interviews and batch processing

```bash
python scripts/04_conduct_interviews.py --provider xai --model grok-4-fast --count 10
```

**Estimated cost for 10 interviews**: ~$0.34

---

### Premium: **grok-4**

Most capable, real-time knowledge access, best quality.

**Cost**: $3.0 input / $15.0 output per 1M tokens
**Speed**: 60 tokens/second
**Context**: 2M tokens
**Use case**: Complex clinical reasoning, maximum accuracy

```bash
python scripts/04_conduct_interviews.py --provider xai --model grok-4 --count 10
```

**Estimated cost for 10 interviews**: ~$5.04

---

### Budget: **grok-3**

Earlier version, good balance of cost and capability.

**Cost**: $0.5 input / $1.0 output per 1M tokens
**Speed**: 80 tokens/second
**Context**: 1M tokens
**Use case**: Large-scale testing on budget

```bash
python scripts/04_conduct_interviews.py --provider xai --model grok-3 --count 10
```

**Estimated cost for 10 interviews**: ~$0.68

---

## Running Interviews with Grok

### Method 1: Direct Script Execution

```bash
cd /home/user/202511-Gravidas

# Single interview
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --count 1

# Batch of 10 interviews
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --count 10

# Using a specific protocol
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --protocol Script/interview_protocols/prenatal_care.json \
  --count 5
```

### Method 2: Using Workflow Pipeline

```bash
cd /home/user/202511-Gravidas

# Edit config to use Grok
nano config/workflow_config.yaml

# Change the active_provider line:
ai_provider:
  active_provider: "xai"

# Run the pipeline
python run_pipeline.py --preset quick_test
```

### Method 3: Interactive Mode

```bash
cd /home/user/202511-Gravidas
python scripts/interactive_interviews.py

# When prompted:
# 1. Select "Add/Update API key manually"
# 2. Choose "xAI (Grok)"
# 3. Paste your API key
# 4. Select provider: xai
# 5. Choose model: grok-4-fast
# 6. Start interviewing!
```

---

## Complete Pipeline Execution with Grok

### Step 1: Generate Personas
```bash
cd /home/user/202511-Gravidas
python scripts/01b_generate_personas.py --count 10 --output data/personas
```

### Step 2: Generate Health Records
```bash
python scripts/02_generate_health_records.py --count 10 --output data/health_records
```

### Step 3: Match Personas to Records
```bash
python scripts/03_match_personas_records_enhanced.py
```

### Step 4: Conduct Interviews with Grok
```bash
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --matched_file data/matched_persona_records.json \
  --count 10
```

### Step 5: Analyze Results
```bash
python scripts/analyze_interviews.py --json --export-json outputs/analysis.json
```

---

## Configuration Reference

### Basic Workflow Config (workflow_config.yaml)

```yaml
ai_provider:
  active_provider: "xai"

  providers:
    xai:
      model: "grok-4-fast"
      api_key: "${XAI_API_KEY}"
      max_tokens: 4096
      temperature: 0.7
      requests_per_minute: 20
```

### CLI Overrides

```bash
# Provider via CLI
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast

# Model selection
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4        # Use grok-4 instead of default

# Interview count
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --count 100           # Generate 100 interviews
```

---

## Cost Estimation

### Per Interview (Average)

Using **grok-4-fast** (recommended):
- Input: ~3,200 tokens × $0.2 / 1M = $0.00064
- Output: ~1,800 tokens × $0.5 / 1M = $0.0009
- **Total per interview: ~$0.0015 ($0.0034 with overhead)**

### Batch Costs

| Count | grok-4-fast | grok-3 | grok-4 |
|-------|------------|--------|---------|
| 10 | $0.34 | $0.68 | $5.04 |
| 100 | $3.40 | $6.80 | $50.40 |
| 1,000 | $34.00 | $68.00 | $504.00 |
| 10,000 | $340.00 | $680.00 | $5,040.00 |

---

## Troubleshooting

### "XAI API key not configured"

**Problem**: Getting error about missing XAI_API_KEY

**Solution**:
```bash
# Check if key is set
echo $XAI_API_KEY

# If empty, set it
export XAI_API_KEY="xai-your-key-here"

# Or add to .env file
echo "XAI_API_KEY=xai-your-key-here" >> .env
source .env
```

### "Model not found"

**Problem**: "Model grok-4-fast not found for provider xai"

**Solution**:
```bash
# Make sure you're using correct model name
# Valid models: grok-4, grok-4-fast, grok-3

# Check your command
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast    # Correct
  # NOT: grok-4-fast-lite or grok-fast
```

### "Rate limit exceeded"

**Problem**: Too many API calls too quickly

**Solution**:
```bash
# Reduce batch size
python scripts/04_conduct_interviews.py \
  --provider xai \
  --model grok-4-fast \
  --count 5              # Smaller batches

# Or adjust rate limiting in config
# workflow_config.yaml:
xai:
  requests_per_minute: 10  # Reduce from 20
```

### "API key invalid"

**Problem**: Authentication failure

**Solution**:
```bash
# Verify key format
# Grok keys typically start with "xai-"
echo $XAI_API_KEY

# Check for typos (no extra spaces)
# Regenerate key if needed from console.x.ai

# Test with simpler request first
python -c "import openai; openai.api_key='YOUR_KEY'; print('Key loaded')"
```

---

## Comparison: All AI Providers

| Provider | Model | Cost/1M | Speed | Context | Best For |
|----------|-------|---------|-------|---------|----------|
| **Anthropic** | Claude Sonnet 4.5 | $3/$15 | Fast | 200K | Consistent quality |
| **OpenAI** | GPT-5 | $7.50/$30 | Very fast | 128K | High volume |
| **Google** | Gemini 2.5 Flash | $0.075/$0.3 | Very fast | 1M | Budget option |
| **xAI** | Grok-4-Fast | $0.2/$0.5 | Fast | 2M | **Best value** |
| **xAI** | Grok-4 | $3/$15 | Medium | 2M | Premium quality |

---

## Real-Time Knowledge & Benefits

**Grok's Unique Advantages:**

1. **Real-time Knowledge**: Access to current information (not date-limited)
2. **Large Context**: 2M token context window (8x larger than Claude)
3. **Cost-Effective**: $0.2/$0.5 for fast model (10-15x cheaper than GPT-5)
4. **Fast**: 100 tokens/second throughput
5. **Developer-Friendly**: OpenAI-compatible API

---

## Next Steps

1. **Get your API key** from https://console.x.ai
2. **Set the environment variable**:
   ```bash
   export XAI_API_KEY="your-key-here"
   ```
3. **Run a test interview**:
   ```bash
   cd /home/user/202511-Gravidas
   python scripts/04_conduct_interviews.py \
     --provider xai \
     --model grok-4-fast \
     --count 1
   ```
4. **Monitor your usage** at https://console.x.ai
5. **Scale up** once you verify everything works

---

## Additional Resources

- [xAI Console](https://console.x.ai)
- [Grok Documentation](https://docs.x.ai)
- [API Reference](https://docs.x.ai/api)
- [Model Specs](https://docs.x.ai/models)

---

**Last Updated**: 2025-11-12
**Status**: Ready for Production
**All 4 AI Providers Now Supported**: ✅ Anthropic ✅ OpenAI ✅ Google ✅ xAI
