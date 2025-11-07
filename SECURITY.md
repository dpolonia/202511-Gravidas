# Security Guide for Synthetic Gravidas Pipeline

## 🔒 API Key Security

This project has been updated to enforce secure API key management practices. **Never commit API keys to version control.**

---

## Quick Start - Secure Setup

### 1. Copy Environment Template

```bash
cp .env.example .env
```

### 2. Edit .env with Your API Keys

Open `.env` in your text editor and add your real API keys:

```bash
# .env file (this file is gitignored)
ANTHROPIC_API_KEY=sk-ant-api03-your-real-key-here
OPENAI_API_KEY=sk-proj-your-real-key-here
GOOGLE_API_KEY=AIzaSy-your-real-key-here
```

### 3. Run Your Scripts

The scripts will automatically load keys from environment variables:

```bash
python scripts/04_conduct_interviews.py --count 10
```

---

## ✅ What's Safe

- ✅ Storing API keys in `.env` file (gitignored)
- ✅ Setting API keys as environment variables
- ✅ Using placeholders in `config/config.yaml`
- ✅ Loading keys via `get_api_key()` function

## ❌ What's NOT Safe

- ❌ Putting real API keys in `config/config.yaml`
- ❌ Committing `.env` file to git
- ❌ Sharing API keys in code, documentation, or screenshots
- ❌ Using `--no-verify` to bypass pre-commit hooks

---

## API Key Loading Methods

### Method 1: Environment File (.env) - **RECOMMENDED**

1. Copy `.env.example` to `.env`
2. Edit `.env` with your real keys
3. The `python-dotenv` package loads these automatically

```bash
cp .env.example .env
# Edit .env with your keys
python scripts/04_conduct_interviews.py
```

### Method 2: Direct Environment Variables

#### Linux/macOS:
```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
export OPENAI_API_KEY='sk-proj-your-key-here'
export GOOGLE_API_KEY='AIza-your-key-here'
```

#### Windows CMD:
```cmd
set ANTHROPIC_API_KEY=sk-ant-your-key-here
set OPENAI_API_KEY=sk-proj-your-key-here
set GOOGLE_API_KEY=AIza-your-key-here
```

#### Windows PowerShell:
```powershell
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
$env:OPENAI_API_KEY='sk-proj-your-key-here'
$env:GOOGLE_API_KEY='AIza-your-key-here'
```

---

## How API Keys Are Loaded

The pipeline uses a **secure loading function** that:

1. ✅ Checks environment variables first (ALWAYS)
2. ❌ Rejects placeholder values
3. ❌ Provides clear error messages with setup instructions
4. ✅ Never logs or prints API keys

### Example Usage in Code:

```python
from utils.common_loaders import get_api_key

# Load API key securely
api_key = get_api_key('anthropic')  # Loads from ANTHROPIC_API_KEY env var
```

---

## Pre-Commit Hook Protection

A **pre-commit hook** automatically scans for API keys before allowing commits.

### What It Detects:

- `sk-ant-*` - Anthropic Claude API keys
- `sk-proj-*` - OpenAI project API keys
- `AIza*` - Google API keys
- `xai-*` - xAI API keys
- Other common patterns

### If Hook Detects Keys:

```
❌ BLOCKED: Potential API key found in: config/config.yaml
   Pattern matched: sk-ant-[a-zA-Z0-9_-]{95,}

🚨 COMMIT BLOCKED: API keys or secrets detected!

How to fix this:
  1. Remove API keys from the staged files
  2. Use environment variables instead
  3. In config/config.yaml, use placeholders only
```

### Bypass Hook (NOT RECOMMENDED):

```bash
git commit --no-verify  # ⚠️  Only use if you're sure there are no secrets
```

---

## Configuration File Security

### config/config.yaml - Use Placeholders Only

The `config/config.yaml` file should **NEVER** contain real API keys:

```yaml
api_keys:
  anthropic:
    # ⚠️ SECURITY: DO NOT put real API keys here!
    # Set ANTHROPIC_API_KEY in your .env file
    api_key: "sk-ant-PLACEHOLDER-USE-ENVIRONMENT-VARIABLE-ANTHROPIC_API_KEY"

  openai:
    api_key: "sk-proj-PLACEHOLDER-USE-ENVIRONMENT-VARIABLE-OPENAI_API_KEY"

  google:
    api_key: "AIza-PLACEHOLDER-USE-ENVIRONMENT-VARIABLE-GOOGLE_API_KEY"
```

---

## .gitignore Protection

The following files are automatically ignored by git:

```gitignore
# API Keys and Credentials
config/config.yaml
.env
.env.local
*.key
*_secret*
credentials.json
```

**Note:** `config/config.yaml` is gitignored to prevent accidental commits. However, you should still use placeholders in it.

---

## Troubleshooting

### Error: "API key not found in environment variables"

**Cause:** The required environment variable is not set.

**Solution:**
```bash
# 1. Create .env file
cp .env.example .env

# 2. Edit .env and add your key
# ANTHROPIC_API_KEY=sk-ant-your-real-key-here

# 3. Verify it's loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY')[:20])"
```

### Error: "contains a placeholder value"

**Cause:** Environment variable is set to a placeholder, not a real key.

**Solution:**
```bash
# Make sure your .env contains real keys, not placeholders
cat .env | grep ANTHROPIC_API_KEY
# Should show: ANTHROPIC_API_KEY=sk-ant-real-key...
# NOT: ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

### Pre-commit hook blocks valid code

**Cause:** Hook detected a pattern that looks like an API key.

**Solution:**
```bash
# 1. Review the file carefully
git diff --cached filename

# 2. If it's a false positive, you can:
#    - Use a different string pattern
#    - Add the file to EXCLUDE_FILES in .git/hooks/pre-commit
#    - As a last resort: git commit --no-verify
```

---

## Security Best Practices

### ✅ DO:

1. **Store API keys in `.env` file**
   - Easy to manage
   - Automatically gitignored
   - Loaded by python-dotenv

2. **Use environment variables**
   - Most secure method
   - Works in CI/CD
   - No files to manage

3. **Rotate keys regularly**
   - Generate new keys periodically
   - Revoke old keys
   - Update `.env` file

4. **Use different keys per environment**
   - Development: `.env.development`
   - Production: `.env.production`
   - Testing: `.env.test`

5. **Set permissions on .env**
   ```bash
   chmod 600 .env  # Only you can read/write
   ```

### ❌ DON'T:

1. **Never commit API keys**
   - Not in config files
   - Not in documentation
   - Not in code comments

2. **Don't share .env files**
   - Send keys via secure channel
   - Use secret management tools
   - Never email or Slack API keys

3. **Don't hardcode keys**
   ```python
   # ❌ BAD
   api_key = "sk-ant-hardcoded-key"

   # ✅ GOOD
   api_key = get_api_key('anthropic')
   ```

4. **Don't bypass security hooks**
   - Pre-commit hooks protect you
   - Only bypass if absolutely certain
   - Review changes carefully first

---

## Checking for Leaked Keys

### Audit Git History

```bash
# Search for Anthropic keys
git log -p | grep -i "sk-ant-"

# Search for OpenAI keys
git log -p | grep -i "sk-proj-"

# Search for Google keys
git log -p | grep -i "AIza"
```

### If You Find Leaked Keys:

1. **Immediately revoke the key**
   - Anthropic: https://console.anthropic.com
   - OpenAI: https://platform.openai.com/api-keys
   - Google: https://console.cloud.google.com/apis/credentials

2. **Generate new key**

3. **Update .env file**

4. **Consider using git-filter-repo to remove from history:**
   ```bash
   # ⚠️  WARNING: This rewrites git history
   pip install git-filter-repo
   git-filter-repo --invert-paths --path config/config.yaml
   ```

---

## Additional Security Tools

### git-secrets

Prevent committing secrets to git:

```bash
# Install
brew install git-secrets  # macOS
apt-get install git-secrets  # Ubuntu

# Setup in repo
git secrets --install
git secrets --register-aws
git secrets --add 'sk-ant-[a-zA-Z0-9_-]{95,}'
git secrets --add 'sk-proj-[a-zA-Z0-9_-]{100,}'
```

### detect-secrets

Scan for secrets in codebase:

```bash
pip install detect-secrets

# Scan
detect-secrets scan

# Audit findings
detect-secrets audit .secrets.baseline
```

---

## Getting Help

If you have security questions or concerns:

1. Check this SECURITY.md file
2. Review .env.example for configuration
3. Check the error messages (they include setup instructions)
4. Open an issue (without including any actual keys!)

---

## Summary Checklist

- [ ] Copied .env.example to .env
- [ ] Added real API keys to .env
- [ ] Verified .env is in .gitignore
- [ ] config/config.yaml contains only placeholders
- [ ] Pre-commit hook is installed (`.git/hooks/pre-commit`)
- [ ] Tested loading keys: `python scripts/04_conduct_interviews.py --help`
- [ ] Never commit real API keys
- [ ] Set .env file permissions: `chmod 600 .env`

---

**🔒 Remember: API keys are like passwords. Treat them with the same level of security!**
