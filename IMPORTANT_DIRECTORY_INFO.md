# ⚠️ IMPORTANT: Directory Structure

## Two Different Directories

### 1. `/home/dpolonia/202511-Gravidas`
**Sync utilities ONLY** - Just `sync.sh` and docs for synchronization

```
/home/dpolonia/202511-Gravidas/
├── sync.sh          (synchronization utility)
└── docs/
    ├── SYNCHRONIZATION_README.md
    └── GIT_SYNC_INSTRUCTIONS.md
```

❌ This is **NOT** the project directory - don't run commands here

---

### 2. `/home/user/202511-Gravidas` ⭐ **USE THIS ONE**
**ACTUAL PROJECT** - All scripts, code, configuration, and git repository

```
/home/user/202511-Gravidas/          ← RUN COMMANDS FROM HERE
├── scripts/                         ← Python scripts are here
│   ├── 04_conduct_interviews.py
│   ├── analyze_interviews.py
│   ├── 01b_generate_personas.py
│   └── ...
├── config/
│   └── workflow_config.yaml
├── run_pipeline.py                  ← Main orchestrator
├── MODEL_NAMES_REFERENCE.md         ← My documentation
├── PIPELINE_EXECUTION_GUIDE.md      ← My documentation
├── GROK_INTEGRATION_SUMMARY.md      ← My documentation
└── .git/                            ← Git repository
```

✅ This is the **CORRECT** directory - all project files are here

---

## How to Use

### Step 1: Navigate to Project Directory

```bash
cd /home/user/202511-Gravidas
pwd  # Should show: /home/user/202511-Gravidas
```

### Step 2: Run Commands

```bash
# All commands should be run from /home/user/202511-Gravidas

# Run interviews
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-opus-4-1 \
  --count 10

# Or use pipeline
python run_pipeline.py --preset quick_test

# Or analyze interviews
python scripts/analyze_interviews.py --json
```

### Step 3: View My Recent Documentation

```bash
# Quick model reference
cat MODEL_NAMES_REFERENCE.md

# Full execution guide
cat PIPELINE_EXECUTION_GUIDE.md

# Grok setup guide
cat docs/GROK_SETUP_GUIDE.md
```

---

## Summary of My Commits

All changes I made are in `/home/user/202511-Gravidas`:

✅ Added Grok (xAI) provider to `config/workflow_config.yaml`
✅ Created `docs/GROK_SETUP_GUIDE.md` (350+ lines)
✅ Created `PIPELINE_EXECUTION_GUIDE.md` (400+ lines)
✅ Created `MODEL_NAMES_REFERENCE.md` (200+ lines)
✅ Created `GROK_INTEGRATION_SUMMARY.md` (350+ lines)
✅ All commits pushed to git branch

---

## What to Do Now

1. **Navigate to correct directory**:
   ```bash
   cd /home/user/202511-Gravidas
   ```

2. **Run interviews with correct model name**:
   ```bash
   python scripts/04_conduct_interviews.py \
     --provider anthropic \
     --model claude-opus-4-1 \
     --count 1
   ```

3. **Check my documentation**:
   ```bash
   cat MODEL_NAMES_REFERENCE.md
   ```

---

## Available Models (Verified)

These model names work in this project:

**Anthropic (Claude)**
- `claude-opus-4-1` - Most capable
- `claude-sonnet-4-5-20250929` - **RECOMMENDED**
- `claude-haiku-4-5` - Fastest

**xAI (Grok)** - Need API key
- `grok-4` - Premium
- `grok-4-fast` - **RECOMMENDED**
- `grok-3` - Budget

**OpenAI (GPT)**
- `gpt-5`
- `gpt-4-1`
- `gpt-5-pro`

**Google (Gemini)**
- `gemini-2.5-pro`
- `gemini-2.5-flash`
- `gemini-2.5-flash-lite`

---

## Quick Test

After navigating to `/home/user/202511-Gravidas`:

```bash
# Test 1: Check Python environment
python -c "print('Python works!')"

# Test 2: Check if scripts exist
ls -la scripts/04_conduct_interviews.py

# Test 3: View available models
grep "claude-\|grok-\|gpt-\|gemini-" run_pipeline.py | grep "'" | head -15

# Test 4: Check git status
git status
git log --oneline -5
```

---

**Status**: All my work is in `/home/user/202511-Gravidas` and committed to git
**Next**: Navigate to that directory and run interviews!
