# API Configuration Guide

Complete guide to obtaining and configuring API keys for Claude, OpenAI, and Gemini.

## Overview

The Synthetic Gravidas Pipeline supports three AI providers for conducting interviews:
- **Anthropic Claude** (recommended)
- **OpenAI GPT**
- **Google Gemini**

You only need to configure **one** provider to use the pipeline, but you can configure all three to compare results.

---

## Anthropic Claude

### Getting an API Key

1. **Create Account**
   - Go to: https://console.anthropic.com
   - Sign up for an Anthropic account
   - Verify your email

2. **Generate API Key**
   - Log in to the console
   - Navigate to "API Keys"
   - Click "Create Key"
   - Give it a name (e.g., "Gravidas Pipeline")
   - Copy the key (starts with `sk-ant-`)

3. **Add Credits**
   - Claude API requires prepaid credits
   - Navigate to "Billing" in the console
   - Add credit (minimum $5)
   - Recommended: $20-50 for 10,000 interviews

### Configuration

Edit `config/config.yaml`:

```yaml
api_keys:
  claude:
    api_key: "sk-ant-xxxxxxxxxxxxx"  # Your actual key
    default_model: "claude-3-5-sonnet-20241022"
    max_tokens: 4096
    temperature: 0.7
```

### Model Options

- `claude-3-5-sonnet-20241022` (recommended) - Best balance of quality and cost
- `claude-3-opus-20240229` - Highest quality, most expensive
- `claude-3-haiku-20240307` - Fastest, cheapest

### Pricing (as of 2025)

**Claude 3.5 Sonnet:**
- Input: $3 per million tokens
- Output: $15 per million tokens
- Estimated cost for 10,000 interviews: ~$200-400

**Cost Estimation:**
- Average interview: 3,000 input tokens + 2,000 output tokens
- Cost per interview: ~$0.02-0.04
- 10,000 interviews: $200-400

---

## OpenAI

### Getting an API Key

1. **Create Account**
   - Go to: https://platform.openai.com
   - Sign up or log in
   - Complete verification

2. **Generate API Key**
   - Navigate to "API Keys" section
   - Click "Create new secret key"
   - Give it a name
   - Copy the key (starts with `sk-`)

3. **Add Payment Method**
   - Go to "Billing"
   - Add payment method
   - Set spending limits (optional)

### Configuration

Edit `config/config.yaml`:

```yaml
api_keys:
  openai:
    api_key: "sk-xxxxxxxxxxxxx"  # Your actual key
    default_model: "gpt-4"
    max_tokens: 4096
    temperature: 0.7
```

### Model Options

- `gpt-4-turbo` - Latest GPT-4, good balance
- `gpt-4` - Original GPT-4, reliable
- `gpt-3.5-turbo` - Cheaper, faster, lower quality

### Pricing (as of 2025)

**GPT-4 Turbo:**
- Input: $10 per million tokens
- Output: $30 per million tokens
- Estimated cost for 10,000 interviews: ~$500-800

**GPT-3.5 Turbo:**
- Input: $0.50 per million tokens
- Output: $1.50 per million tokens
- Estimated cost for 10,000 interviews: ~$25-50

---

## Google Gemini

### Getting an API Key

1. **Create Google Cloud Account**
   - Go to: https://makersuite.google.com/app/apikey
   - Sign in with Google account
   - Accept terms of service

2. **Create API Key**
   - Click "Create API Key"
   - Select or create a project
   - Copy the key

3. **Enable Billing (Optional)**
   - Gemini has free tier
   - For production, enable billing in Google Cloud Console

### Configuration

Edit `config/config.yaml`:

```yaml
api_keys:
  gemini:
    api_key: "xxxxxxxxxxxxx"  # Your actual key
    default_model: "gemini-1.5-pro"
    max_tokens: 4096
    temperature: 0.7
```

### Model Options

- `gemini-1.5-pro` - Best quality
- `gemini-1.5-flash` - Faster, cheaper
- `gemini-1.0-pro` - Original version

### Pricing (as of 2025)

**Gemini 1.5 Pro:**
- Free tier: 50 requests per day
- Input: $7 per million tokens (above free tier)
- Output: $21 per million tokens
- Estimated cost for 10,000 interviews: ~$300-500

**Free Tier:**
- 50 requests per day = ~1,500 per month
- Good for testing and small-scale projects

---

## Configuration File Setup

### Step 1: Copy Template

```bash
cd /home/user/202511-Gravidas
cp config/config.yaml.template config/config.yaml
```

### Step 2: Edit Configuration

```bash
nano config/config.yaml
```

### Step 3: Add Your Keys

Replace placeholders with actual keys:

```yaml
api_keys:
  claude:
    api_key: "sk-ant-api03-xxxxxxxxxxxxx"  # <- Your actual Claude key
  openai:
    api_key: "sk-proj-xxxxxxxxxxxxx"        # <- Your actual OpenAI key
  gemini:
    api_key: "AIzaSyxxxxxxxxxxxxx"          # <- Your actual Gemini key
```

**Important:** Only configure the providers you plan to use.

### Step 4: Verify Configuration

Test your configuration:

```bash
python scripts/04_conduct_interviews.py \
  --model claude \
  --count 1 \
  --protocol Script/interview_protocols/pregnancy_experience.json
```

---

## Security Best Practices

### 1. Never Commit API Keys

Add `config/config.yaml` to `.gitignore`:

```bash
echo "config/config.yaml" >> .gitignore
```

### 2. Use Environment Variables (Alternative)

Instead of storing keys in config file:

```bash
export CLAUDE_API_KEY="sk-ant-xxxxxxxxxxxxx"
export OPENAI_API_KEY="sk-xxxxxxxxxxxxx"
export GEMINI_API_KEY="xxxxxxxxxxxxx"
```

### 3. Restrict Key Permissions

- Claude: Set spending limits in console
- OpenAI: Set usage limits in settings
- Gemini: Enable API restrictions in Google Cloud

### 4. Rotate Keys Regularly

- Regenerate keys every 3-6 months
- Delete old keys from console
- Update configuration

### 5. Monitor Usage

- Check billing dashboards regularly
- Set up usage alerts
- Review API logs for unusual activity

---

## Cost Optimization

### 1. Start Small

Test with 10-50 interviews before running full 10,000:

```bash
python scripts/04_conduct_interviews.py --count 10
```

### 2. Use Cheaper Models for Testing

For development and testing:
- Claude: Use `claude-3-haiku-20240307`
- OpenAI: Use `gpt-3.5-turbo`
- Gemini: Use free tier

### 3. Batch Processing

Process interviews in batches to monitor costs:

```bash
# Run 1000 at a time
for i in {0..9}; do
  python scripts/04_conduct_interviews.py \
    --count 1000 \
    --start-index $((i * 1000))
  sleep 60  # Pause between batches
done
```

### 4. Reduce Token Usage

Edit `config/config.yaml`:

```yaml
interview:
  max_turns: 10  # Reduce from 20
```

### 5. Compare Providers

Run small test batches with each provider:

```bash
# Test with each provider
python scripts/04_conduct_interviews.py --model claude --count 5
python scripts/04_conduct_interviews.py --model openai --count 5
python scripts/04_conduct_interviews.py --model gemini --count 5
```

Then choose the best value for your needs.

---

## Troubleshooting

### Error: "Invalid API key"

**Cause:** Key is incorrect or not properly formatted

**Solutions:**
1. Double-check key in config file
2. Ensure no extra spaces or newlines
3. Verify key is active in provider console
4. Regenerate key if necessary

### Error: "Rate limit exceeded"

**Cause:** Too many requests too quickly

**Solutions:**
1. Reduce `batch_size` in config
2. Add delays between interviews
3. Upgrade API plan
4. Spread interviews over longer time period

### Error: "Insufficient credits"

**Cause:** No funds in account (Claude, OpenAI)

**Solutions:**
1. Add credits/payment method
2. Check billing dashboard
3. Verify payment method is valid

### Error: "Model not found"

**Cause:** Model name is incorrect or not available

**Solutions:**
1. Check model name in config
2. Verify model availability in docs
3. Use default recommended model

---

## HuggingFace Token (Optional)

For accessing private datasets or increased rate limits:

### Getting a Token

1. Go to: https://huggingface.co
2. Sign up or log in
3. Go to Settings → Access Tokens
4. Create new token
5. Copy token

### Configuration

Add to `config/config.yaml`:

```yaml
huggingface:
  token: "hf_xxxxxxxxxxxxx"  # Your token
  dataset: "argilla/FinePersonas-v0.1"
```

**Note:** HuggingFace token is optional for FinePersonas dataset as it's public.

---

## API Key Verification Script

Create a test script to verify all keys:

```bash
python scripts/utils/verify_api_keys.py
```

This will test each configured provider and report status.

---

## Support and Resources

### Anthropic Claude
- Documentation: https://docs.anthropic.com
- API Reference: https://docs.anthropic.com/claude/reference
- Support: support@anthropic.com

### OpenAI
- Documentation: https://platform.openai.com/docs
- API Reference: https://platform.openai.com/docs/api-reference
- Community: https://community.openai.com

### Google Gemini
- Documentation: https://ai.google.dev/docs
- API Reference: https://ai.google.dev/api
- Support: Google Cloud Support

---

## Next Steps

After configuring your API keys:

1. Test with a single interview
2. Run 10 interviews to verify
3. Review costs in provider dashboard
4. Scale up to full 10,000 interviews

See [TUTORIAL.md](../TUTORIAL.md) for complete usage guide.
