# Gravidas Developer Onboarding Guide - v1.2.1

**Project:** Gravidas - Persona-to-Health-Record Matching System
**Phase:** Phase 3, Tasks 3.1.4 & 3.1.5 - Developer Onboarding
**Version:** 1.2.1
**Date:** 2025-11-16
**Status:** ✅ COMPLETE

---

## Welcome to Gravidas! 🎉

This guide will help you get up and running with the Gravidas system in **under 30 minutes**. Whether you're contributing code, running experiments, or extending the system, this document provides everything you need to know.

---

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start (5 Minutes)](#quick-start-5-minutes)
3. [Development Setup](#development-setup)
4. [Project Structure](#project-structure)
5. [Configuration Guide](#configuration-guide)
6. [Running the Pipeline](#running-the-pipeline)
7. [Testing](#testing)
8. [Common Development Tasks](#common-development-tasks)
9. [Troubleshooting](#troubleshooting)
10. [Contributing Guidelines](#contributing-guidelines)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Purpose |
|----------|----------------|---------|
| **Python** | 3.8+ | Core runtime |
| **pip** | 20.0+ | Package management |
| **Java** | 11+ (JRE) | Synthea health record generation |
| **git** | 2.0+ | Version control |

### Recommended Tools

- **VS Code** or **PyCharm** - IDE with Python support
- **Docker** (optional) - For containerized deployment
- **pytest** - Testing framework (installed via requirements.txt)

### API Keys

You'll need at least ONE of the following:

- **Anthropic API Key** (recommended) - [Get key](https://console.anthropic.com/)
- **OpenAI API Key** - [Get key](https://platform.openai.com/api-keys)
- **Google AI API Key** - [Get key](https://makersuite.google.com/app/apikey)

---

## Quick Start (5 Minutes)

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/202511-Gravidas.git
cd 202511-Gravidas
```

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt
```

### 3. Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API key
nano .env
```

Add to `.env`:
```bash
ANTHROPIC_API_KEY=sk-ant-your-key-here
# OR
OPENAI_API_KEY=sk-your-key-here
# OR
GOOGLE_API_KEY=your-key-here
```

### 4. Run Quick Test

```bash
# Generate 5 test personas (~30 seconds, ~$0.05)
python scripts/01b_generate_personas.py --count 5

# Success! You should see:
# ✅ Generated 5 personas
# 📁 Saved to: data/personas/personas.json
```

**Congratulations!** 🎉 You're ready to use Gravidas.

---

## Development Setup

### Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate
source venv/bin/activate  # Linux/Mac
# OR
venv\Scripts\activate  # Windows

# Verify activation
which python  # Should show venv/bin/python
```

### Install Development Dependencies

```bash
# Core dependencies
pip install -r requirements.txt

# Development tools (optional)
pip install black flake8 mypy pytest-cov ipython

# Verify installation
python -c "import anthropic, openai, scipy, pandas; print('✅ All packages installed')"
```

### Synthea Setup (For Health Records)

```bash
# Download Synthea (one-time setup)
cd ~
git clone https://github.com/synthetichealth/synthea.git
cd synthea

# Build Synthea
./gradlew build check test

# Verify installation
java -jar build/libs/synthea-with-dependencies.jar --help

# Return to Gravidas directory
cd /path/to/202511-Gravidas
```

**Update Synthea Path:**

Edit `config/workflow_config.yaml`:
```yaml
health_records:
  synthea_path: /home/yourusername/synthea  # Your path
```

### IDE Setup

#### VS Code

1. Install Python extension
2. Set interpreter to virtual environment:
   - `Cmd+Shift+P` → "Python: Select Interpreter"
   - Choose `./venv/bin/python`

3. Recommended settings (`.vscode/settings.json`):
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true
}
```

#### PyCharm

1. File → Settings → Project → Python Interpreter
2. Add interpreter → Virtualenv Environment → Existing
3. Select `venv/bin/python`

---

## Project Structure

```
202511-Gravidas/
│
├── scripts/                    # Main pipeline scripts
│   ├── 01b_generate_personas.py
│   ├── 02_generate_health_records.py
│   ├── 03_match_personas_records_enhanced.py
│   ├── 04_conduct_interviews.py
│   ├── analyze_interviews.py
│   ├── run_workflow.py         # Orchestrator
│   └── utils/                  # Shared modules
│       ├── fhir_semantic_extractor.py
│       ├── semantic_tree.py
│       ├── semantic_matcher.py
│       └── common_loaders.py
│
├── data/                       # Data storage (gitignored)
│   ├── personas/
│   ├── matched/
│   ├── interviews/
│   └── analysis/
│
├── tests/                      # Automated tests
│   ├── test_semantic_tree_generation.py
│   ├── test_semantic_similarity.py
│   └── test_integration_semantic_matching.py
│
├── docs/                       # Documentation
│   ├── ARCHITECTURE.md
│   ├── API_REFERENCE.md
│   ├── DEVELOPER_ONBOARDING.md  # This file
│   └── ETHICAL_USE.md
│
├── config/                     # Configuration files
│   ├── config.yaml
│   └── workflow_config.yaml
│
├── logs/                       # Log files (gitignored)
│
├── .env                        # Environment variables (gitignored)
├── .env.example                # Environment template
├── requirements.txt            # Python dependencies
├── README.md                   # Project overview
└── .gitignore
```

### Key Directories

| Directory | Purpose | Tracked by Git? |
|-----------|---------|----------------|
| `scripts/` | Pipeline code | ✅ Yes |
| `data/` | Generated data | ❌ No (too large) |
| `tests/` | Automated tests | ✅ Yes |
| `docs/` | Documentation | ✅ Yes |
| `config/` | Configuration | ✅ Yes (templates) |
| `logs/` | Debug logs | ❌ No |

---

## Configuration Guide

### Configuration Files

Gravidas uses three configuration methods:

1. **Environment Variables** (`.env`) - API keys, secrets
2. **YAML Configuration** (`config/workflow_config.yaml`) - Pipeline settings
3. **Python Constants** - Hardcoded defaults

### 1. Environment Variables (.env)

```bash
# .env file (NEVER commit this file!)

# LLM API Keys (choose at least one)
ANTHROPIC_API_KEY=sk-ant-your-key-here
OPENAI_API_KEY=sk-your-key-here
GOOGLE_API_KEY=your-key-here

# Optional: AWS Bedrock
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_DEFAULT_REGION=us-east-1

# Optional: Azure OpenAI
AZURE_OPENAI_API_KEY=your-azure-key
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/

# Optional: Other providers
TOGETHER_API_KEY=your-together-key
GROQ_API_KEY=your-groq-key
MISTRAL_API_KEY=your-mistral-key
```

**Security Note:** Never commit `.env` to git! Use `.env.example` as a template.

### 2. Workflow Configuration (workflow_config.yaml)

```yaml
# config/workflow_config.yaml

# Persona Generation Settings
personas:
  count: 100                    # Number of personas to generate
  seed: 42                      # Random seed for reproducibility
  llm_provider: anthropic       # anthropic, openai, google
  llm_model: claude-haiku-4-5   # Model identifier
  output_path: data/personas/personas.json

# Health Record Generation
health_records:
  count: 100                    # Number of FHIR records
  seed: 12345                   # Synthea random seed
  synthea_path: ./synthea       # Path to Synthea installation
  output_dir: synthea/output/fhir
  modules:                      # Synthea modules to enable
    - pregnancy
    - contraceptives
    - sexual_activity

# Semantic Matching Configuration
matching:
  algorithm: hungarian          # Matching algorithm
  min_similarity: 0.5           # Minimum acceptable similarity
  weights:                      # Factor weights (must sum to 1.0)
    age: 0.40                   # Age compatibility
    education: 0.20             # Education level
    income: 0.15                # Income bracket
    marital: 0.15               # Marital status
    occupation: 0.10            # Occupation category
  output_path: data/matched/matched_pairs.json

# Interview Settings
interviews:
  llm_provider: anthropic       # LLM provider for interviews
  llm_model: claude-sonnet-4-5  # Recommended: Sonnet for quality
  max_tokens: 4096              # Maximum response length
  temperature: 0.7              # Creativity (0-1)
  batch_mode: false             # Enable batch API (50% discount)
  anomaly_threshold: 0.7000     # Calibrated threshold
  protocols_path: data/interview_protocols.json
  output_dir: data/interviews

# Analysis Settings
analysis:
  output_path: data/analysis/interview_summary.csv
  include_cost_report: true
  include_anomaly_report: true

# Logging
logging:
  level: INFO                   # DEBUG, INFO, WARNING, ERROR
  file: logs/workflow.log
  console: true
```

### Configuration Parameters

#### Persona Generation

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | 100 | Number of personas to generate |
| `seed` | int | 42 | Random seed for reproducibility |
| `llm_provider` | str | "anthropic" | LLM provider (anthropic/openai/google) |
| `llm_model` | str | "claude-haiku-4-5" | Model identifier |

**Cost Estimates:**
- Claude Haiku: ~$0.01/persona
- Claude Sonnet: ~$0.03/persona
- GPT-4: ~$0.02/persona

#### Health Records

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `count` | int | 100 | Number of FHIR records |
| `seed` | int | 12345 | Synthea random seed |
| `synthea_path` | str | "./synthea" | Path to Synthea installation |

**Performance:** ~30-60 seconds for 10 records

#### Matching

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `algorithm` | str | "hungarian" | Matching algorithm |
| `min_similarity` | float | 0.5 | Minimum match quality |
| `weights.age` | float | 0.40 | Age importance (0-1) |
| `weights.education` | float | 0.20 | Education importance |
| `weights.income` | float | 0.15 | Income importance |
| `weights.marital` | float | 0.15 | Marital status importance |
| `weights.occupation` | float | 0.10 | Occupation importance |

**Note:** Weights must sum to 1.0

#### Interviews

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `llm_provider` | str | "anthropic" | LLM provider |
| `llm_model` | str | "claude-sonnet-4-5" | Model for interviews |
| `max_tokens` | int | 4096 | Maximum response length |
| `temperature` | float | 0.7 | Sampling temperature (0-1) |
| `batch_mode` | bool | false | Use batch API (async) |
| `anomaly_threshold` | float | 0.7000 | Quality threshold |

**Model Recommendations:**
- **Quality Priority:** Claude Sonnet 4.5 (~$0.08/interview)
- **Cost Priority:** Claude Haiku 4.5 (~$0.03/interview)
- **Speed Priority:** Groq Llama 3.3 70B (~$0.01/interview)

---

## Running the Pipeline

### Option 1: Complete Workflow (Recommended)

```bash
# Run entire pipeline with defaults
python scripts/run_workflow.py

# Custom configuration
python scripts/run_workflow.py --config config/workflow_config.yaml

# Quick test (10 samples)
python scripts/run_workflow.py --preset quick_test

# Specify sample size
python scripts/run_workflow.py --personas 50 --provider claude --model claude-sonnet-4-5
```

### Option 2: Individual Stages

#### Stage 1: Generate Personas

```bash
python scripts/01b_generate_personas.py --count 100 --seed 42

# Options:
#   --count: Number of personas (default: 100)
#   --seed: Random seed (default: 42)
#   --provider: LLM provider (default: anthropic)
#   --model: LLM model (default: claude-haiku-4-5)
#   --output: Output file (default: data/personas/personas.json)
```

#### Stage 2: Generate Health Records

```bash
python scripts/02_generate_health_records.py --count 100 --seed 12345

# Options:
#   --count: Number of records (default: 100)
#   --seed: Synthea seed (default: 12345)
#   --synthea-path: Path to Synthea (default: ./synthea)
```

#### Stage 3: Match Personas to Records

```bash
python scripts/03_match_personas_records_enhanced.py

# Uses default paths from config
# Outputs: data/matched/matched_pairs.json
```

#### Stage 4: Conduct Interviews

```bash
python scripts/04_conduct_interviews.py --count 10 --provider anthropic --model claude-sonnet-4-5

# Options:
#   --count: Number of interviews (default: all matched pairs)
#   --provider: LLM provider
#   --model: LLM model
#   --batch: Enable batch mode (50% discount)
```

#### Stage 5: Analyze Results

```bash
python scripts/analyze_interviews.py

# Outputs: data/analysis/interview_summary.csv
```

### Interactive Mode

```bash
python scripts/interactive_interviews.py

# Guided UI walks you through:
# 1. API key setup
# 2. Sample size selection
# 3. Model selection with cost estimates
# 4. Execution and monitoring
```

---

## Testing

### Run All Tests

```bash
# Run full test suite
pytest

# With coverage report
pytest --cov=scripts --cov-report=html

# Verbose output
pytest -v

# Specific test file
pytest tests/test_semantic_tree_generation.py
```

### Test Categories

#### Unit Tests

```bash
# Semantic tree tests
pytest tests/test_semantic_tree_generation.py

# Similarity calculation tests
pytest tests/test_semantic_similarity.py

# Anomaly detection tests
pytest tests/test_anomaly_detection.py
```

#### Integration Tests

```bash
# End-to-end workflow
pytest tests/test_integration_semantic_matching.py
```

### Writing Tests

Create new test file in `tests/`:

```python
# tests/test_my_feature.py

import pytest
from scripts.my_module import my_function

def test_my_function():
    """Test my_function with valid input."""
    result = my_function(input_data)
    assert result == expected_output

def test_my_function_edge_case():
    """Test my_function with edge case."""
    with pytest.raises(ValueError):
        my_function(invalid_input)
```

Run your test:
```bash
pytest tests/test_my_feature.py -v
```

---

## Common Development Tasks

### Task 1: Add a New Interview Question

1. **Edit protocol JSON:**

```json
// data/interview_protocols.json

{
  "question_id": "Q8.5",
  "text": "Have you discussed birth plans with your provider?",
  "type": "yes_no",
  "purpose": "Assess birth planning preparedness",
  "data_mapping": ["pregnancy_intentions.birth_plan_discussed"],
  "follow_up_prompts": [
    "What aspects of your birth plan have you discussed?",
    "Are there any concerns about your birth plan?"
  ]
}
```

2. **Test the updated protocol:**

```bash
python scripts/04_conduct_interviews.py --count 1
```

### Task 2: Add a New LLM Provider

1. **Update `universal_ai_client.py`:**

```python
# scripts/universal_ai_client.py

SUPPORTED_PROVIDERS = {
    # ... existing providers
    "new_provider": {
        "models": ["model-1", "model-2"],
        "pricing": {
            "model-1": {"input": 1.0, "output": 3.0}  # per 1M tokens
        }
    }
}

def _send_new_provider_message(self, messages, max_tokens):
    """Send message to new provider API."""
    # Implementation here
    pass
```

2. **Test the integration:**

```python
from scripts.universal_ai_client import UniversalAIClient

client = UniversalAIClient(
    provider="new_provider",
    model="model-1",
    api_key="your-key"
)

response = client.send_message([
    {"role": "user", "content": "Hello"}
])
print(response)
```

### Task 3: Modify Matching Weights

1. **Edit `config/workflow_config.yaml`:**

```yaml
matching:
  weights:
    age: 0.50           # Increased from 0.40
    education: 0.20
    income: 0.10        # Decreased from 0.15
    marital: 0.10       # Decreased from 0.15
    occupation: 0.10
```

2. **Re-run matching:**

```bash
python scripts/03_match_personas_records_enhanced.py

# Verify results
python -c "
import json
with open('data/matched/matched_pairs.json', 'r') as f:
    data = json.load(f)
print(f'Average similarity: {data[\"statistics\"][\"average_similarity\"]:.3f}')
"
```

### Task 4: Export Custom Analytics

Create new analysis script:

```python
# scripts/my_custom_analysis.py

import json
import pandas as pd
from pathlib import Path

def custom_analysis():
    """Custom analysis of interview data."""
    # Load interviews
    interviews = []
    for file in Path('data/interviews').glob('*.json'):
        with open(file, 'r') as f:
            interviews.append(json.load(f))

    # Custom processing
    results = []
    for interview in interviews:
        results.append({
            'interview_id': interview['interview_id'],
            'custom_metric': calculate_custom_metric(interview)
        })

    # Export
    df = pd.DataFrame(results)
    df.to_csv('data/analysis/custom_analysis.csv', index=False)
    print(f"✅ Exported {len(results)} custom analyses")

if __name__ == "__main__":
    custom_analysis()
```

---

## Troubleshooting

### Common Issues

#### 1. ModuleNotFoundError

**Error:** `ModuleNotFoundError: No module named 'anthropic'`

**Solution:**
```bash
# Ensure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt
```

#### 2. API Key Not Found

**Error:** `Error: ANTHROPIC_API_KEY not found`

**Solution:**
```bash
# Check .env file exists
ls -la .env

# Verify key is set
cat .env | grep ANTHROPIC_API_KEY

# If missing, add to .env:
echo "ANTHROPIC_API_KEY=sk-ant-your-key" >> .env
```

#### 3. FHIR Parsing Failures

**Error:** `FHIRParsingError: Failed to parse bundle`

**Solution:**
```bash
# Run debug script
python scripts/debug_semantic_trees.py

# Check logs
cat logs/semantic_tree_failures_report.json

# Verify FHIR files are valid
python -c "
import json
with open('synthea/output/fhir/patient_123.json', 'r') as f:
    data = json.load(f)
print(f'Resource type: {data.get(\"resourceType\")}')
"
```

#### 4. Synthea Not Found

**Error:** `FileNotFoundError: Synthea not found at ./synthea`

**Solution:**
```bash
# Update config with correct path
nano config/workflow_config.yaml

# Change:
health_records:
  synthea_path: /home/yourusername/synthea  # Your actual path
```

#### 5. Out of Memory

**Error:** `MemoryError: Unable to allocate array`

**Solution:**
```bash
# Reduce batch size
python scripts/04_conduct_interviews.py --count 10  # Instead of 100

# Or process in chunks
for i in {1..10}; do
  python scripts/04_conduct_interviews.py --count 10 --offset $((i*10))
done
```

### Getting Help

1. **Check Documentation:**
   - [ARCHITECTURE.md](ARCHITECTURE.md) - System design
   - [API_REFERENCE.md](API_REFERENCE.md) - Function signatures
   - [README.md](../README.md) - Project overview

2. **Search Issues:** [GitHub Issues](https://github.com/yourusername/202511-Gravidas/issues)

3. **Ask Questions:** Open a new issue with:
   - Error message
   - Steps to reproduce
   - System info (`python --version`, `pip list`)

---

## Contributing Guidelines

### Code Style

We follow [PEP 8](https://pep8.org/) with some modifications:

- **Line length:** 100 characters (not 79)
- **Imports:** Group into stdlib, third-party, local
- **Type hints:** Required for all functions
- **Docstrings:** Google style

**Format code:**
```bash
# Install black
pip install black

# Format file
black scripts/my_file.py

# Format all
black scripts/ tests/
```

### Pull Request Process

1. **Fork repository**
2. **Create feature branch:**
   ```bash
   git checkout -b feature/my-new-feature
   ```

3. **Make changes and commit:**
   ```bash
   git add .
   git commit -m "Add: My new feature description"
   ```

4. **Write tests:**
   ```bash
   pytest tests/test_my_feature.py
   ```

5. **Push to fork:**
   ```bash
   git push origin feature/my-new-feature
   ```

6. **Create Pull Request** on GitHub

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat: Add new interview protocol`
- `fix: Correct FHIR parsing null handling`
- `docs: Update API reference`
- `test: Add semantic similarity tests`
- `refactor: Simplify matching algorithm`

---

## Next Steps

Now that you're set up, explore these resources:

1. **[ARCHITECTURE.md](ARCHITECTURE.md)** - Understand system design
2. **[API_REFERENCE.md](API_REFERENCE.md)** - Function documentation
3. **[COST_BUDGET_ANALYSIS.md](COST_BUDGET_ANALYSIS.md)** - Cost optimization
4. **[ETHICAL_USE.md](ETHICAL_USE.md)** - Responsible AI guidelines

### Suggested Learning Path

**Week 1: Basics**
- Run quick test (5 personas)
- Explore generated data
- Read ARCHITECTURE.md

**Week 2: Experimentation**
- Modify matching weights
- Try different LLM models
- Analyze cost trade-offs

**Week 3: Development**
- Add custom analysis
- Write tests
- Contribute improvements

---

**Welcome to the team!** 🚀

If you have questions, don't hesitate to open an issue or reach out to the community.

---

**Document Prepared By:** Claude Code
**Date:** 2025-11-16
**Version:** 1.2.1
**Status:** Tasks 3.1.4 & 3.1.5 COMPLETE ✅
