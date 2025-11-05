# API Key Setup - Three Easy Methods

Choose the method that works best for you!

---

## Method 1: Interactive Mode (Easiest!)

**No file editing required - just run and enter keys when prompted**

```bash
python scripts/interactive_interviews.py
```

1. The launcher starts
2. Select: "1. Add/Update API key manually"
3. Choose your provider (Anthropic, OpenAI, Google, xAI)
4. Paste your API key
5. Done! Start interviewing

**Pros:**
- No file editing
- Keys stored in memory only
- Immediate feedback
- Can add multiple providers interactively

**Cons:**
- Keys not saved between sessions
- Need to re-enter each time

---

## Method 2: Environment File (Recommended!)

**Best for development - keeps keys separate from code**

### Setup:

```bash
# 1. Copy the example file
cp .env.example .env

# 2. Edit with your API keys
nano .env
```

### Edit .env:

```bash
# Anthropic (Claude)
ANTHROPIC_API_KEY=sk-ant-api03-YOUR-ACTUAL-KEY-HERE

# OpenAI (GPT)
OPENAI_API_KEY=sk-proj-YOUR-ACTUAL-KEY-HERE

# Google (Gemini)
GOOGLE_API_KEY=AIzaSyYOUR-ACTUAL-KEY-HERE

# xAI (Grok) - Optional
XAI_API_KEY=xai-YOUR-ACTUAL-KEY-HERE
```

### Run:

```bash
python scripts/interactive_interviews.py
# Or
python scripts/04_conduct_interviews.py --provider anthropic --model claude-4.5-sonnet --count 10
```

**Pros:**
- Keys automatically loaded
- Git-ignored (secure)
- Standard practice
- Easy to manage multiple keys

**Cons:**
- Requires file editing
- One extra setup step

---

## Method 3: Config File

**Best for production - integrated with all settings**

### Setup:

```bash
# 1. Copy the template
cp config/config.yaml.template config/config.yaml

# 2. Edit with your API keys
nano config/config.yaml
```

### Edit config/config.yaml:

```yaml
api_keys:
  anthropic:
    api_key: "sk-ant-api03-YOUR-ACTUAL-KEY-HERE"
    max_tokens: 4096
    temperature: 0.7

  openai:
    api_key: "sk-proj-YOUR-ACTUAL-KEY-HERE"
    max_tokens: 4096
    temperature: 0.7

  google:
    api_key: "AIzaSyYOUR-ACTUAL-KEY-HERE"
    max_tokens: 4096
    temperature: 0.7
```

### Run:

```bash
python scripts/interactive_interviews.py
# Or
python scripts/04_conduct_interviews.py --count 10
```

**Pros:**
- All settings in one place
- Model configuration included
- Advanced options available

**Cons:**
- More complex file
- Risk of committing keys if not careful

---

## Comparison Table

| Method | Setup Time | Best For | Security | Flexibility |
|--------|------------|----------|----------|-------------|
| **Interactive** | 1 minute | Quick tests | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **.env file** | 2 minutes | Development | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ |
| **config.yaml** | 3 minutes | Production | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |

---

## Getting API Keys

### Anthropic (Claude)

1. Go to: https://console.anthropic.com
2. Sign up or log in
3. Navigate to "API Keys"
4. Click "Create Key"
5. Copy the key (starts with `sk-ant-`)

### OpenAI (GPT)

1. Go to: https://platform.openai.com/api-keys
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-proj-` or `sk-`)

### Google (Gemini)

1. Go to: https://makersuite.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key (starts with `AIza`)

### xAI (Grok)

1. Go to: https://console.x.ai
2. Sign up or log in
3. Navigate to API keys
4. Create new key
5. Copy the key

---

## Security Best Practices

### ✅ DO:

- Use `.env` file for local development
- Add `config/config.yaml` to `.gitignore` (already done)
- Rotate keys every 3-6 months
- Use different keys for testing and production
- Set spending limits in provider dashboards

### ❌ DON'T:

- Commit API keys to Git
- Share keys in public channels
- Use the same key across multiple projects
- Hard-code keys in scripts
- Leave keys in screenshots or documentation

---

## Troubleshooting

### "No API keys available"

**Problem**: No keys configured

**Solution**: Use any of the three methods above to add at least one key

### "Invalid API key"

**Problem**: Key is wrong or expired

**Solution**:
1. Check for typos (no extra spaces, complete key)
2. Verify key is active in provider dashboard
3. Regenerate key if needed

### Keys not loading from .env

**Problem**: `.env` file not found or not loaded

**Solution**:
```bash
# Check file exists
ls -la .env

# Check file contents
cat .env

# Make sure file is in project root directory
```

### Keys not loading from config.yaml

**Problem**: YAML syntax error or wrong location

**Solution**:
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/config.yaml'))"

# Check file location
ls -la config/config.yaml
```

---

## Recommendation

**For most users**: Use **Method 2 (.env file)**

It's the best balance of:
- Easy setup
- Good security
- Standard practice
- Automatic loading

Just run:
```bash
cp .env.example .env
nano .env  # Add your keys
python scripts/interactive_interviews.py
```

Done! 🎉
