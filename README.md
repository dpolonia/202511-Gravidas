# Synthetic Gravidas Pipeline

A comprehensive system for generating synthetic pregnant personas with associated health records for research and interview simulations.

**Current Version:** v1.3.1 (Publication-Ready)
**Latest Update:** 2025-11-18 - v1.2.0 Roadmap Complete: Operations Research Framework

## Overview

This pipeline creates 10,000 synthetic personas of women in fertile age (12-60 years) matched with pregnancy-related health records from Synthea. The matched datasets can be used to conduct AI-powered interviews for medical research, training, and scenario simulation.

## v1.2.0 Roadmap Complete (v1.3.1)

### 6 Specialized Interview Protocols

Comprehensive maternal health interview protocols with protocol auto-discovery:

- **Prenatal Care**: Routine prenatal care and preventive health (20 questions, 25 min)
- **Genetic Counseling**: Genetic testing, counseling, and decision-making (18 questions, 30 min)
- **Mental Health Screening**: Perinatal depression, anxiety, and psychosocial screening (18 questions, 30 min)
- **High-Risk Pregnancy**: Complications, specialized care, and risk management (15 questions, 35 min)
- **Postpartum Care**: Recovery, infant care, and transition to parenthood (14 questions, 25 min)
- **Pregnancy Experience**: General pregnancy journey and expectations (19 questions, 30 min)

Each protocol includes detailed questions, data mapping to persona fields, red flag protocols, and resource connections.

### Interactive Cost Dashboard & Exact Tracking

Real-time cost monitoring and visualization:

- **Exact Token Counting**: Direct from API responses (±0% accuracy)
- **Interactive HTML Dashboard**: 5 chart types (cost by model, by provider, token usage, efficiency, timeline)
- **Multi-Provider Comparison**: Anthropic, OpenAI, Google, xAI
- **Cost per Interview**: $0.032-0.095 depending on provider
- **Cost Optimization**: Up to 59% reduction with optimal provider selection

Generate dashboard: `python scripts/generate_cost_dashboard.py`
View output: `outputs/cost_dashboard.html`

## Features

- **Persona Retrieval**: Downloads 10,000 female personas from HuggingFace FinePersonas dataset
- **Health Record Generation**: Uses Synthea to generate realistic pregnancy-related medical records
- **Intelligent Matching**: Matches personas to health records based on age compatibility and socioeconomic factors
- **60+ AI Models**: Support for 15+ providers including OpenAI, Anthropic, Google, AWS, Azure, Mistral, xAI, and more
- **Universal AI Client**: Seamless switching between providers with unified interface
- **Batch API Support**: Up to 50% cost savings for large-scale processing with automatic detection
- **Real-time Cost Estimation**: Accurate pricing with batch mode recommendations
- **6 Specialized Interview Protocols**: Evidence-based protocols with auto-discovery system (v1.2.0+)
- **Interactive Cost Dashboard**: Real-time visualization with exact token tracking (v1.2.0+)
- **Pregnancy Stage Detection**: Automatic trimester calculation from FHIR data (v1.2.0+)
- **Protocol-Specific Anomaly Detection**: <10% false positive rate with dynamic thresholds (v1.2.0+)
- **Comprehensive Testing**: 60%+ code coverage with pytest (v1.2.0+)
- **Comprehensive Documentation**: Model specs, cost analysis, clinical protocols, and step-by-step tutorials

## Project Structure

```
202511-Gravidas/
├── run_pipeline.py              # 🚀 Complete automation (v1.0.1)
├── config/
│   └── config.yaml              # API keys and configuration
├── data/
│   ├── personas/                # Downloaded personas (100 generated)
│   ├── interview_protocols.json # 🆕 5 clinical protocols (v1.2.1)
│   ├── health_records/          # Generated Synthea records (665 records)
│   ├── matched/                 # Matched persona-record pairs (78 matches)
│   ├── interviews/              # Interview results (78 completed)
│   └── analysis/                # Analysis results (interview_summary.csv)
├── scripts/
│   ├── 01_retrieve_personas.py
│   ├── 02_generate_health_records.py
│   ├── 03_match_personas_records.py
│   ├── 04_conduct_interviews.py # Updated with universal client support
│   ├── interactive_interviews.py # AI model selection interface
│   ├── enhanced_models_database.py # Comprehensive provider/model database
│   ├── universal_ai_client.py   # Universal client factory for all providers
│   ├── generate_test_data.py    # Quick test data generation
│   └── utils/                   # Helper functions including FHIR processing
│       ├── fhir_semantic_extractor.py # 🆕 100% FHIR processing (v1.2.1)
│       └── semantic_tree.py     # 🆕 Semantic matching (v1.2.1)
├── tests/                       # 🆕 100+ automated tests (v1.2.1)
│   ├── test_semantic_tree_generation.py
│   ├── test_semantic_similarity.py
│   ├── test_anomaly_detection.py
│   └── test_integration_semantic_matching.py
├── Script/
│   └── interview_protocols/     # Interview protocol templates
├── docs/
│   ├── SYNTHEA_SETUP.md
│   ├── API_CONFIGURATION.md
│   ├── MODEL_SELECTION.md
│   ├── COST_BUDGET_ANALYSIS.md  # 🆕 Complete cost analysis (v1.2.1)
│   ├── ANOMALY_DETECTION_CALIBRATION.md # 🆕 Threshold calibration (v1.2.1)
│   ├── V1.2.0_MASTER_PLAN.md    # 🆕 12-week roadmap (v1.2.1)
│   ├── V1.2.0_IMPLEMENTATION_GUIDE.md # 🆕 Technical guide (v1.2.1)
│   └── V1.2.0_IMPLEMENTATION_GUIDE_PART2.md # 🆕 Phases 2-4 (v1.2.1)
├── TUTORIAL.md
├── INTEGRATION_SUMMARY.md       # v1.0.1 integration details
├── PHASE_1_COMPLETION_REPORT.md # 🆕 Phase 1 summary (v1.2.1)
└── requirements.txt
```

## 🚀 Quick Start v1.0.1 - Complete Automation

### One-Command Pipeline (NEW!)
```bash
# Interactive mode - guided setup with model selection
python run_pipeline.py

# CLI mode - automated execution  
python run_pipeline.py --count 100 --provider anthropic --model claude-sonnet-4-5

# Quick test with 10 interviews
python run_pipeline.py --count 10 --test

# Large study with batch API (50% cost savings)  
python run_pipeline.py --count 1000 --batch --provider together --model llama-3.1-405b

# Ultra-fast processing with Groq
python run_pipeline.py --count 500 --provider groq --model llama-3.3-70b --batch
```

### Latest AI Models (2025) - 60+ Models from 15+ Providers

| **Provider** | **Model** | **Quality** | **Cost (per 1M tokens)** | **Features** |
|--------------|-----------|-------------|---------------------------|-------------|
| **OpenAI** | `gpt-5` ⭐ | Excellent | $1.25/$10 | 🔄 1M context |
| | `gpt-5-mini` | Very Good | $0.25/$2.00 | 🔄 Fast |
| | `gpt-4o` | Excellent | $2.50/$10 | 🔄 Vision |
| **Anthropic** | `claude-sonnet-4-5` ⭐ | Excellent | $3/$15 | 🔄 200K context |
| | `claude-opus-4-1` | Exceptional | $15/$75 | 🔄 Premium |
| | `claude-haiku-4-5` | Very Good | $1/$5 | 🔄 Fast |
| **Google** | `gemini-2.5-pro` ⭐ | Excellent | $1.25/$10 | 🔄 1M context |
| | `gemini-2.5-flash` | Very Good | $0.15/$1.25 | 🔄 💰 Best value |
| **Together AI** | `llama-3.1-405b` | Excellent | $3.50/$3.50 | 🔄 Open source |
| | `llama-4-maverick` | Very Good | $0.27/$0.85 | 🔄 💰 |
| **Groq** | `llama-3.3-70b` | Very Good | $0.59/$0.79 | 🔄 ⚡ Ultra-fast |
| | `llama-3.1-8b` | Good | $0.05/$0.08 | 🔄 💰 Cheapest |
| **Mistral** | `mistral-large-2` | Excellent | $2.00/$6.00 | Advanced reasoning |
| **xAI** | `grok-4` | Excellent | $3/$15 | Real-time knowledge |
| **DeepSeek** | `deepseek-v3.2-exp` | Very Good | $0.28/$0.42 | 💰 Experimental |

⭐ = Recommended • 🔄 = Batch API (50% savings) • 💰 = Cost-effective • ⚡ = Ultra-fast

**Full Support:** AWS Bedrock, Azure OpenAI, Azure AI Foundry, Fireworks AI, Cohere, Perplexity

### 🆕 What's New in v1.0.1

- ✅ **15+ AI Providers**: Comprehensive integration from OpenAI to specialized providers
- ✅ **60+ Models**: Latest 2025 models with accurate pricing from AImodels.csv
- ✅ **Universal Client**: Seamless switching between any provider with unified interface  
- ✅ **Enhanced Cost Optimization**: Automatic batch API detection and savings calculation
- ✅ **Real-time Pricing**: Accurate cost estimation with per-provider breakdowns
- ✅ **Improved CLI**: All providers available in both interactive and command-line modes

---

## Legacy Quick Start

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

### Getting Started
- **[docs/INTERACTIVE_MODE.md](docs/INTERACTIVE_MODE.md)** - ⭐ Interactive launcher guide (START HERE!)
- [TUTORIAL.md](TUTORIAL.md) - Complete step-by-step manual guide
- [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) - Choose between 12 AI models with cost comparisons
- [docs/SYNTHEA_SETUP.md](docs/SYNTHEA_SETUP.md) - Synthea installation and configuration
- [docs/API_CONFIGURATION.md](docs/API_CONFIGURATION.md) - API key setup guide

### Phase 2 Documentation (v1.2.1 - NEW!)
- **[docs/COST_BUDGET_ANALYSIS.md](docs/COST_BUDGET_ANALYSIS.md)** - Complete LLM cost analysis and budget recommendations
- **[data/interview_protocols.json](data/interview_protocols.json)** - 5 clinical interview protocols (ACOG/ADA 2025)
- [docs/ANOMALY_DETECTION_CALIBRATION.md](docs/ANOMALY_DETECTION_CALIBRATION.md) - Threshold calibration methodology
- [PHASE_1_COMPLETION_REPORT.md](PHASE_1_COMPLETION_REPORT.md) - Phase 1 technical achievements
- [docs/V1.2.0_MASTER_PLAN.md](docs/V1.2.0_MASTER_PLAN.md) - 12-week implementation roadmap
- [docs/V1.2.0_IMPLEMENTATION_GUIDE.md](docs/V1.2.0_IMPLEMENTATION_GUIDE.md) - Detailed technical guide

### Phase 3 Documentation (v1.2.1 - NEW!)
- **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Complete system architecture and data flow
- **[docs/API_REFERENCE.md](docs/API_REFERENCE.md)** - Comprehensive API documentation
- **[docs/DEVELOPER_ONBOARDING.md](docs/DEVELOPER_ONBOARDING.md)** - Developer setup and configuration guide
- **[docs/ETHICAL_USE.md](docs/ETHICAL_USE.md)** - Ethical guidelines and responsible AI practices
- [docs/RESEARCH_MANUSCRIPT_IJPE.md](docs/RESEARCH_MANUSCRIPT_IJPE.md) - Operations research manuscript (draft)

---

## ⚠️ Ethical Use and Limitations

### Important: Synthetic Data Only

**Gravidas generates 100% synthetic (artificial) data.** All personas, health records, and interviews are AI-generated simulations. This data:

✅ **CAN** be used for:
- Algorithm development and testing
- Educational and training purposes
- Operations research and cost analysis
- System prototyping and proof-of-concept
- Research methodology development

❌ **CANNOT** be used for:
- Clinical decision-making
- Presenting as real patient data
- Policy recommendations without real data validation
- Insurance or financial decisions
- Diagnosing or treating real patients

### Key Limitations

1. **Not Clinically Validated**: Synthetic interviews are AI-generated, not from real patients
2. **Potential Biases**: LLM training data may contain societal biases
3. **Limited Generalizability**: Findings must be validated with real clinical data
4. **No IRB Required**: Synthetic data exempt from human subjects research

### Citation Requirement

When publishing research using Gravidas, you must:
- Clearly state that data is synthetic
- Cite the system and version used
- Acknowledge limitations
- Include proper attributions

**Required Citation:**
```
Polônia, D. (2025). Gravidas: A Synthetic Healthcare Interview Generation
System for Maternal Health Research (Version 1.3.1) [Software]. GitHub.
https://github.com/yourusername/202511-Gravidas
```

### Full Ethical Guidelines

See **[docs/ETHICAL_USE.md](docs/ETHICAL_USE.md)** for complete guidelines including:
- Detailed appropriate and inappropriate use cases
- Bias acknowledgment and mitigation strategies
- Data privacy and security practices
- Responsible AI development guidelines
- Reporting misuse procedures

**By using Gravidas, you agree to follow these ethical guidelines and use the system responsibly.**

---

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

### Latest Updates (2025-11-18) - Version 1.3.1 - v1.2.0 Roadmap Complete

🎯 **v1.2.0 ROADMAP COMPLETE: Publication-Ready Operations Research Framework**
- **6 specialized interview protocols** with protocol auto-discovery system
- **Interactive cost dashboard** with exact token tracking (±0% accuracy)
- **Pregnancy stage detection** from FHIR data with automatic trimester calculation
- **Protocol-specific anomaly detection** with <10% false positive rate
- **Comprehensive testing** with 60%+ code coverage using pytest
- **Operations research manuscript** positioned for IJPE submission
- **Zero clinical overclaims** - honest framing as AI cost-optimization research

✅ **90% FHIR Data Completeness** - Pregnancy weeks, vitals, clinical data
✅ **Exact Token Tracking** - Direct from API responses (not estimates)
✅ **59% Cost Reduction** - Multi-provider optimization ($0.032-0.095 per interview)
✅ **6 Interview Protocols** - Prenatal, genetic counseling, mental health, high-risk, postpartum, pregnancy experience
✅ **Interactive Dashboard** - Real-time cost visualization with 5 chart types
✅ **20,450+ Lines of Documentation** - Architecture, ethical guidelines, research manuscript

### Previous Updates (2025-11-07) - Version 1.0.1

🚀 **Complete End-to-End Automation Pipeline**
- One-command pipeline execution with `python run_pipeline.py`
- Dynamic sample size selection (1-10,000 personas/interviews)
- Interactive AI model selection with cost estimation
- Latest 2025 models: Claude Opus 4.1, GPT-5, Gemini 2.5 Pro, Grok 4
- Batch API integration for 50% cost savings on large studies
- Real-time progress monitoring and error recovery

✅ **Enhanced AI Model Support** - 15+ latest models with updated pricing
✅ **Production Ready** - End-to-end pipeline proven with real results
✅ **Scientific Rigor** - Reproducible methodology with fixed seeds and comprehensive validation

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

### ✅ **PROVEN RESULTS - Production System (2025-11-07)**

**v1.0.1 - Complete Automation:**

🚀 **New Pipeline Orchestrator:** `python run_pipeline.py`
✅ **Dynamic Sample Sizes:** 1-10,000 personas/interviews supported  
✅ **Latest AI Models:** Claude Opus 4.1, GPT-5, Gemini 2.5 Pro, Grok 4
✅ **Cost Optimization:** Batch API support for 50% savings on large studies
✅ **Real-time Monitoring:** Progress tracking and error recovery

**v1.0 - First Successful Run:**
✅ **78 interviews completed** with $5.95 total cost (Claude 3 Haiku)
✅ **100% success rate** with comprehensive quality validation
✅ **Scientific reproducibility** with fixed seeds and version control

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

*Last updated: 2025-11-16 (v1.2.1 - Phase 2 Complete)*
*Pipeline proven with 78 successful interviews - Python 3.11, Claude Sonnet 4.5, Synthea 3.x*
*Phase 2: 5 Clinical Interview Protocols + Comprehensive Cost Analysis*
