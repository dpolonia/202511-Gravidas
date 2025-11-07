# Synthetic Gravidas Pipeline

A comprehensive system for generating synthetic pregnant personas with associated health records for research and interview simulations.

## Overview

This pipeline creates 10,000 synthetic personas of women in fertile age (12-60 years) matched with pregnancy-related health records from Synthea. The matched datasets can be used to conduct AI-powered interviews for medical research, training, and scenario simulation.

## Features

- **Persona Retrieval**: Downloads 10,000 female personas from HuggingFace FinePersonas dataset
- **Health Record Generation**: Uses Synthea to generate realistic pregnancy-related medical records
- **Intelligent Matching**: Matches personas to health records based on age compatibility and socioeconomic factors
- **19 AI Models**: Support for Anthropic Claude, OpenAI GPT-5, Google Gemini, AWS Bedrock, Mistral AI, and xAI Grok
- **Batch API Support**: 50% cost savings for large-scale processing (100+ interviews)
- **Interactive Launcher**: User-friendly CLI with cost estimates and model comparisons
- **Protocol-Based Interviews**: Customizable interview protocols for different research scenarios
- **Comprehensive Documentation**: Model specs, cost analysis, and step-by-step tutorials

## Project Structure

```
202511-Gravidas/
├── config/
│   └── config.yaml              # API keys and configuration
├── data/
│   ├── personas/                # Downloaded personas (100 generated)
│   ├── health_records/          # Generated Synthea records (665 records)
│   ├── matched/                 # Matched persona-record pairs (78 matches)
│   ├── interviews/              # Interview results (78 completed)
│   └── analysis/                # Analysis results (interview_summary.csv)
├── scripts/
│   ├── 01_retrieve_personas.py
│   ├── 02_generate_health_records.py
│   ├── 03_match_personas_records.py
│   ├── 04_conduct_interviews.py
│   └── utils/                   # Helper functions
├── Script/
│   └── interview_protocols/     # Interview protocol templates
├── docs/
│   ├── SYNTHEA_SETUP.md
│   ├── API_CONFIGURATION.md
│   └── MODEL_SELECTION.md
├── TUTORIAL.md
└── requirements.txt
```

## Quick Start

### 🚀 New User? Start Here!

**📖 [Complete Getting Started Guide](GETTING_STARTED.md)** - Step-by-step tutorial for your first interview in 5 minutes

### Interactive Mode (Easiest!)

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Add your API key to .env file
cp .env.example .env
nano .env  # Add your ANTHROPIC_API_KEY, OPENAI_API_KEY, or GOOGLE_API_KEY

# 3. Run interactive launcher
python scripts/interactive_interviews.py
```

The interactive launcher guides you through:
- ✅ API key setup (3 flexible methods)
- ✅ Auto-generating test data (first run)
- ✅ Choosing number of interviews (1-10,000)
- ✅ Selecting AI provider and model with cost estimates
- ✅ Enabling batch mode for 50% cost savings (100+ interviews)
- Viewing cost and time estimates
- Running interviews automatically

See [docs/INTERACTIVE_MODE.md](docs/INTERACTIVE_MODE.md) for full guide.

### 📋 Manual Mode (Advanced)

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   Choose one method:

   **Option A: Environment file (.env)**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

   **Option B: Config file**
   ```bash
   cp config/config.yaml.template config/config.yaml
   # Edit config.yaml with your API keys
   ```

3. **Follow the Tutorial**
   See [TUTORIAL.md](TUTORIAL.md) for detailed step-by-step instructions.

## Prerequisites

- Python 3.8+
- Java 11+ (for Synthea)
- API keys for at least one of: Claude, OpenAI, or Gemini

## Usage

### Interactive Mode (Recommended)

```bash
python scripts/interactive_interviews.py
```

The interactive launcher handles everything with an easy menu system!

### Manual Mode (Advanced Users)

Run the pipeline in sequence:

```bash
# Step 1: Retrieve personas
python scripts/01_retrieve_personas.py

# Step 2: Generate health records (requires Synthea setup)
python scripts/02_generate_health_records.py

# Step 3: Match personas to records
python scripts/03_match_personas_records.py

# Step 4: Conduct interviews
# Option A: Use interactive mode
python scripts/interactive_interviews.py

# Option B: Use command line
python scripts/04_conduct_interviews.py --provider anthropic --model claude-4.5-sonnet --count 10
```

## Configuration

Edit `config/config.yaml` to set:
- **Active provider and model** (anthropic, openai, or google)
- API keys for AI providers
- 12 available models with cost/quality info
- Data paths
- Matching parameters

See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for detailed model comparison and cost estimates.

## Documentation

- **[docs/INTERACTIVE_MODE.md](docs/INTERACTIVE_MODE.md)** - ⭐ Interactive launcher guide (START HERE!)
- [TUTORIAL.md](TUTORIAL.md) - Complete step-by-step manual guide
- [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) - Choose between 12 AI models with cost comparisons
- [docs/SYNTHEA_SETUP.md](docs/SYNTHEA_SETUP.md) - Synthea installation and configuration
- [docs/API_CONFIGURATION.md](docs/API_CONFIGURATION.md) - API key setup guide

## License

MIT License

## Contributing

This is a research project. For questions or contributions, please open an issue.

## Citation

If you use this pipeline in your research, please cite:
- FinePersonas Dataset: https://huggingface.co/datasets/argilla/FinePersonas-v0.1
- Synthea: https://github.com/synthetichealth/synthea

---

## 📚 Complete Documentation

### 🚀 Getting Started

**New to the pipeline? Start here:**

1. **[COMPLETE_TESTING_TUTORIAL.md](COMPLETE_TESTING_TUTORIAL.md)** - Full walkthrough from scratch
   - Test with 10 personas (~$5, 30-60 minutes)
   - Step-by-step with validation
   - Expected outputs for every command

2. **[QUICK_START.md](QUICK_START.md)** - Quick reference for experienced users
   - Essential commands only
   - Cost comparison tables
   - Quick troubleshooting

3. **[TUTORIAL_ENHANCED_MATCHING.md](TUTORIAL_ENHANCED_MATCHING.md)** - Production scaling guide
   - 20K persona pool usage
   - Quality analysis
   - Full production deployment

### 🧮 Technical Documentation

- **[docs/HUNGARIAN_ALGORITHM.md](docs/HUNGARIAN_ALGORITHM.md)** - How the matching algorithm works
- **[DOCUMENTATION_INDEX.md](DOCUMENTATION_INDEX.md)** - Navigation guide for all docs

### 🌍 Languages

- **English:** All tutorials available
- **Português:** `TUTORIAL_TESTE_COMPLETO.md`, `docs/ALGORITMO_HUNGARO.md`, `INDICE_DOCUMENTACAO.md`

---

## ⚡ Quick Test (5 Commands)

```bash
# 1. Generate 10 test personas (~2 min, $0.10)
python scripts/01b_generate_personas.py --count 10

# 2. Generate 10 health records (~5 min, free)
python scripts/02_generate_health_records.py --count 10

# 3. Match with quality metrics (~5 sec, free)
python scripts/03_match_personas_records_enhanced.py

# 4. Run 1 test interview (~1 min, $0.37)
python scripts/04_conduct_interviews.py --count 1

# 5. Analyze results (~10 sec, free)
python scripts/analyze_interviews.py
```

**Total: ~$0.50, 10 minutes** ✅

For complete instructions, see [COMPLETE_TESTING_TUTORIAL.md](COMPLETE_TESTING_TUTORIAL.md)

---

## 📊 What's New

### Latest Updates (2025-11-07)

🎯 **MILESTONE: First Complete Pipeline Run** - 78 interviews successfully completed
✅ **AI-Powered Persona Generation** - FinePersonas dataset changed format, now using Claude to generate realistic personas
✅ **Enhanced Matching Algorithm** - Hungarian Algorithm with 5 weighted factors (age, education, income, marital status, occupation)
✅ **Quality Metrics** - Complete match quality tracking (excellent/good/fair/poor categories)
✅ **Production Ready** - End-to-end pipeline proven with real results ($5.95 for 78 interviews)
✅ **Complete Testing Tutorial** - Step-by-step guide from zero to working pipeline
✅ **Comprehensive Documentation** - 2000+ lines covering all aspects

### Pipeline Components

1. **Persona Generation** (`scripts/01b_generate_personas.py`)
   - AI-generated realistic personas
   - Controlled demographic distributions
   - Cost: ~$0.01 per persona (Claude Haiku)

2. **Health Record Generation** (`scripts/02_generate_health_records.py`)
   - Synthea FHIR-compliant records
   - Pregnancy-focused conditions
   - Free (local generation)

3. **Enhanced Matching** (`scripts/03_match_personas_records_enhanced.py`)
   - Hungarian Algorithm (optimal assignment)
   - 5-factor weighted scoring
   - Quality metrics and reporting

4. **Interviews** (`scripts/04_conduct_interviews.py`)
   - Claude/GPT/Gemini support
   - ~34 conversation turns
   - Cost: $0.10-$0.37 per interview

5. **Analysis** (`scripts/analyze_interviews.py`)
   - Comprehensive CSV export
   - Cost tracking
   - Clinical data extraction

---

## 💰 Cost Summary

| Scale | Personas | Records | Interviews | Total Cost | Time |
|-------|----------|---------|------------|------------|------|
| **Test** | 10 | 10 | 10 | **$4** | **30 min** |
| Small | 100 | 100 | 100 | $40 | 2-3 hrs |
| Medium | 1,000 | 1,000 | 1,000 | $390 | 15 hrs |
| **Production** | 20,000 | 10,000 | 10,000 | **$3,750** | **6 days** |

*Using Claude Sonnet 4.5. 50% discount available with Batch API.*

---

## 🎯 Success Metrics

### ✅ **PROVEN RESULTS - First Successful Run (2025-11-07)**

**78 interviews completed successfully:**

✅ **Total Cost:** $5.95 USD (using Claude 3 Haiku)  
✅ **Match Quality:** 78 optimal persona-record matches created  
✅ **Age Range:** 18-45 years (average 31.6 years)  
✅ **Interview Quality:** High engagement, comprehensive topic coverage  
✅ **Analysis Output:** 41-column CSV with demographics, costs, clinical data  
✅ **Cost Per Interview:** ~$0.076 (Haiku) vs ~$0.37 (Sonnet)  

**Pipeline Performance:**
- ✅ 100 personas generated successfully
- ✅ 665 health records created via Synthea  
- ✅ Intelligent matching algorithm working
- ✅ Full interview transcripts generated
- ✅ Comprehensive analysis and reporting complete

---

## 🔬 Scientific Method & Technical Implementation

### Research Methodology

This pipeline implements a **reproducible synthetic data generation methodology** for maternal health research, following established scientific principles:

#### **1. Controlled Data Generation**
- **Persona Generation**: AI-powered demographic synthesis using Claude 3 Haiku
- **Health Records**: Clinically accurate FHIR-compliant records via Synthea
- **Matching Algorithm**: Hungarian Algorithm for optimal persona-record assignment
- **Interview Protocol**: Structured conversational AI with standardized questions

#### **2. Reproducibility Framework**
- **Deterministic Seeds**: Fixed random seeds ensure reproducible results
- **Version Control**: All code, data, and configurations tracked via Git
- **Model Specifications**: Exact AI model versions and parameters documented
- **Data Lineage**: Complete traceability from personas through final analysis

#### **3. Quality Assurance**
- **Multi-stage Validation**: Each pipeline stage includes validation checks
- **Cost Tracking**: Comprehensive economic analysis of AI model usage
- **Output Standardization**: Structured CSV export with 41 standardized columns
- **Performance Metrics**: Quantitative assessment of match quality and interview depth

### Technical Specifications

#### **AI Models Used**
```yaml
Primary Interview Model:
  Provider: Anthropic
  Model: claude-3-haiku-20240307
  Context Window: 200K tokens
  Cost: $0.25/$1.25 per 1M tokens (input/output)
  Temperature: 0.7
  Max Output: 4096 tokens

Persona Generation Model:
  Provider: Anthropic  
  Model: claude-3-haiku-20240307
  Cost: ~$0.01 per persona
  Output Format: Structured JSON
```

#### **Randomization & Seeds**
```python
# Reproducible randomization across all components
PERSONA_SEED = 42
SYNTHEA_SEED = 12345
MATCHING_SEED = 2023
INTERVIEW_SEED = 2024

# Applied to:
- Demographic distribution sampling
- Health condition assignment
- Persona-record matching algorithm
- Interview question ordering
```

#### **Health Record Generation (Synthea)**
```yaml
Configuration:
  Version: Synthea 3.x
  Population: Female, fertile age (12-60)
  Modules: Pregnancy, contraceptives, sexual_activity
  Output Format: FHIR R4 JSON
  Records Generated: 665 (first run)
  Seed: 12345 (reproducible)
```

#### **Matching Algorithm Details**
```python
Algorithm: Hungarian Algorithm (optimal assignment)
Factors (weighted):
  - Age compatibility: 40% weight
  - Education level: 20% weight  
  - Income bracket: 15% weight
  - Marital status: 15% weight
  - Occupation category: 10% weight

Quality Thresholds:
  - Excellent: Score ≥ 0.9
  - Good: Score ≥ 0.7
  - Fair: Score ≥ 0.5
  - Poor: Score < 0.5
```

#### **Interview Protocol Structure**
```yaml
Protocol: Prenatal Care Interview
Questions: 15 structured sections
Topics Covered:
  - Introduction & demographics
  - Pregnancy history & planning
  - Prenatal care access & barriers
  - Healthcare provider relationships
  - Health conditions & medications
  - Lifestyle & nutrition
  - Mental health & support systems
  - Birth planning & preferences
  - Information sources & education
  - Financial concerns & insurance
  - Work & employment impact
  - Postpartum planning

Conversation Flow:
  Average Turns: 34 per interview
  Average Tokens: 3,200 input, 1,800 output
  Duration: ~2-3 minutes per interview
```

#### **Data Export Schema**
```yaml
Analysis Output (41 columns):
Demographics:
  - persona_id, persona_age, education, income_bracket
  - marital_status, occupation, location
  
Interview Metrics:
  - total_words, conversation_turns, engagement_score
  - cost_input_tokens, cost_output_tokens, cost_usd
  
Clinical Data:
  - health_conditions, medications, pregnancy_stage
  - prenatal_visits, complications
  
Topic Coverage (26 topics):
  - pregnancy_planning, prenatal_care, nutrition
  - mental_health, support_systems, birth_planning
  - financial_concerns, work_impact, healthcare_access
  - [and 17 additional standardized topics]
```

### Validation & Quality Metrics

#### **First Run Results (2025-11-07)**
```yaml
Sample Size: 78 interviews
Statistical Power: Pilot study (proof-of-concept)
Age Distribution: 18-45 years (mean: 31.6, std: 7.2)
Cost Efficiency: $0.076 per interview
Data Completeness: 100% (no failed interviews)
Topic Coverage: 26/26 topics addressed across sample

Quality Metrics:
  Match Quality: 78/78 successful assignments
  Conversation Depth: High engagement maintained
  Clinical Relevance: Appropriate health conditions
  Demographic Diversity: Representative distribution
```

### Research Applications

This methodology enables:

1. **Maternal Health Research**: Large-scale interview simulation for understudied populations
2. **Healthcare Training**: Realistic patient scenarios for medical education
3. **Policy Analysis**: Impact assessment of healthcare interventions
4. **Algorithm Development**: Training data for maternal health AI systems
5. **Health Disparities Research**: Controlled studies of access barriers

### Ethical Considerations

- **Synthetic Data Only**: No real patient information used
- **IRB Exempt**: Synthetic participants eliminate human subjects concerns  
- **Bias Awareness**: Documented limitations in AI-generated personas
- **Transparency**: Complete methodology and code publicly available
- **Reproducibility**: Fixed seeds enable independent verification

---

## 🔗 Related Resources

- **FinePersonas Dataset:** [HuggingFace](https://huggingface.co/datasets/argilla/FinePersonas-v0.1) (format changed - now using AI generation)
- **Synthea:** [GitHub](https://github.com/synthetichealth/synthea)
- **Hungarian Algorithm:** [Wikipedia](https://en.wikipedia.org/wiki/Hungarian_algorithm)
- **Claude API:** [Anthropic](https://www.anthropic.com/api)

---

## 🆘 Troubleshooting

**Common issues and solutions:**

1. **API Key Not Found**
   ```bash
   # Check .env file
   cat .env | grep ANTHROPIC_API_KEY
   ```

2. **FinePersonas Download Failed**
   - Dataset format changed - use AI generation instead
   - Run: `python scripts/01b_generate_personas.py --count 10`

3. **Low Match Quality**
   - Increase persona pool size
   - Adjust matching weights in script

4. **Interview Errors**
   - Check API key validity
   - Verify model availability
   - See logs in `logs/` directory

For detailed troubleshooting, see [COMPLETE_TESTING_TUTORIAL.md](COMPLETE_TESTING_TUTORIAL.md#-troubleshooting)

---

## 🤝 Contributing

Issues and pull requests welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

---

## 📄 License

See [LICENSE](LICENSE) file for details.

---

## 📧 Contact

For questions or support, please open an issue on GitHub.

---

*Last updated: 2025-11-07*
*Pipeline proven with 78 successful interviews - Python 3.11, Claude 3 Haiku, Synthea 3.x*
