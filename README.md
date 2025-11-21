# GRAVIDAS - Synthetic Maternal Health Interview Research Platform

[![Version](https://img.shields.io/badge/version-v2.1.0-blue.svg)](https://github.com/dpolonia/202511-Gravidas)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

A comprehensive end-to-end platform for generating synthetic pregnant personas, conducting AI-powered interviews, analyzing results with 11 NLP algorithms, generating academic reports, and selecting target journals for publication.

## Key Features

- **8-Stage Automated Workflow** - From persona generation to journal-formatted paper
- **11 NLP Analysis Algorithms** - Medical NER, emotion detection, sentiment analysis, and more
- **18 Q1/Q2 Journals Database** - With suitability index and automatic recommendation
- **Multi-Provider LLM Support** - Anthropic, OpenAI, Google AI
- **FHIR-Compliant Health Records** - Generated via Synthea
- **Semantic Persona-Record Matching** - Hungarian algorithm with quality metrics
- **Automatic Archiving** - Timestamped runs with comprehensive summaries

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure API keys
cp .env.example .env
# Edit .env with your ANTHROPIC_API_KEY or OPENAI_API_KEY

# 3. Run the complete workflow
python run_complete_workflow.py

# Or use interactive mode
python run_interactive_workflow.py
```

## Workflow Stages

| Stage | Script | Description |
|-------|--------|-------------|
| 1 | `01b_generate_personas.py` | Generate synthetic pregnant women personas |
| 2 | `02_generate_health_records.py` | Create FHIR-compliant medical records |
| 3 | `03_match_personas_records_enhanced.py` | Semantic matching with Hungarian algorithm |
| 4 | `04_conduct_interviews.py` | AI-powered interview simulation |
| 5 | `analyze_interviews.py` | Extract insights and detect anomalies |
| 6 | `test_semantic_implementation.py` | Quality validation checks |
| 7 | `06_generate_academic_report.py` | LLM-based systematic report generation |
| 8 | `07_journal_selector.py` | Journal recommendation with suitability index |

## NLP Analysis Suite

The platform includes 11 state-of-the-art NLP algorithms for comprehensive interview analysis:

| Module | Description | Key Features |
|--------|-------------|--------------|
| **Medical NER** | Entity recognition | Conditions, symptoms, medications, procedures |
| **Multi-Emotion** | 8 discrete emotions | Joy, fear, anger, sadness, trust, anticipation |
| **Topic Modeling** | Theme discovery | BERTopic or Gensim LDA |
| **BERT Sentiment** | Context-aware sentiment | Per-speaker profiling, trajectory tracking |
| **QA Patterns** | Question analysis | Type classification, empathy detection |
| **Readability** | Linguistic complexity | Flesch, SMOG, health literacy assessment |
| **Mental Health** | Screening tools | PHQ-9, GAD-7, risk stratification |
| **Semantic Similarity** | Content clustering | Sentence-BERT, thematic grouping |
| **Empathy Detection** | Communication quality | 7 positive, 4 negative indicators |
| **Narrative Arc** | Story progression | Turning points, emotional journey |
| **Risk Extraction** | Clinical risks | 30+ factors, automated recommendations |

## Journal Selection System

### Suitability Index (0-100 scale)

| Component | Points | Description |
|-----------|--------|-------------|
| Scope Match | 30 | Alignment with research themes |
| Methodology Fit | 20 | Match with journal focus |
| Impact & Prestige | 20 | IF + Quartile ranking |
| Accessibility | 15 | Open access, APC affordability |
| Management Focus | 10 | ASJC area bonus |
| Review Time | 5 | Turnaround speed |

### Journal Database (Q1/Q2 Only)

18 journals including:
- BMC Pregnancy and Childbirth (Q1, IF: 3.2, OA)
- Health Care Management Science (Q1, IF: 2.5)
- BMC Health Services Research (Q1, IF: 2.7, OA)
- Health Policy and Planning (Q1, IF: 3.2)
- Midwifery (Q1, IF: 2.8)
- And 13 more...

### Example Output

```
JOURNAL RECOMMENDATIONS - SUITABILITY ANALYSIS
============================================================================
 # Journal Name                          ISSN        Q   IF   OA     APC  Suit. Grade
 1 BMC Pregnancy and Childbirth         1471-2393  Q1  3.2  Yes  $2,890    66 B (Goo)
 2 Health Care Management Science       1386-9620  Q1  2.5   No  $3,290    66 B (Goo)
 3 Reproductive Health                  1742-4755  Q1  3.1  Yes  $2,790    64 C (Mod)
...
```

## Archive Structure

Each workflow run is automatically archived:

```
archive/
├── run_YYYYMMDD_HHMMSS/
│   ├── data/
│   │   ├── personas/
│   │   ├── health_records/
│   │   ├── matched/
│   │   ├── interviews/
│   │   ├── analysis/
│   │   └── validation/
│   ├── outputs/
│   │   ├── academic_report.md
│   │   └── formatted_paper.md
│   ├── logs/
│   ├── config/
│   └── RUN_SUMMARY.md
└── run_history.json
```

## Configuration

### Workflow Options

```bash
python run_complete_workflow.py --help

Options:
  --personas N       Number of personas to generate (default: 100)
  --records N        Number of health records (default: 100)
  --interviews N     Number of interviews (default: 10)
  --provider NAME    LLM provider: anthropic, openai (default: anthropic)
  --model NAME       Specific model to use
  --quick-test       Quick test with minimal data
  --list-runs        Show previous workflow runs
  --cleanup-runs N   Keep only last N runs
```

### Journal Selector Options

```bash
python scripts/07_journal_selector.py --help

Options:
  --report PATH      Path to academic report
  --objective TEXT   Publication objective (e.g., "healthcare management")
  --prefer-oa        Prefer open access journals
  --max-apc N        Maximum APC in USD
  --auto-select      Automatically select top recommendation
  --fetch-scopus     Enrich with Scopus API data
```

## Cost Estimates

| Scale | Personas | Interviews | Est. Cost | Time |
|-------|----------|------------|-----------|------|
| Test | 10 | 10 | ~$5 | 30 min |
| Small | 100 | 50 | ~$25 | 2 hrs |
| Medium | 500 | 100 | ~$50 | 5 hrs |
| Large | 1000 | 500 | ~$200 | 12 hrs |

*Costs based on Claude Sonnet 4.5. OpenAI gpt-4o-mini is ~60% cheaper.*

## Documentation

| Guide | Description |
|-------|-------------|
| [QUICK_START_WORKFLOW.md](QUICK_START_WORKFLOW.md) | Getting started guide |
| [INTERACTIVE_LAUNCHER_GUIDE.md](INTERACTIVE_LAUNCHER_GUIDE.md) | Interactive workflow execution |
| [WORKFLOW_CUSTOMIZATION_GUIDE.md](WORKFLOW_CUSTOMIZATION_GUIDE.md) | Advanced customization |
| [NLP_ANALYSIS_CAPABILITIES.md](NLP_ANALYSIS_CAPABILITIES.md) | NLP modules documentation |
| [docs/PROVIDERS_AND_MODELS.md](docs/PROVIDERS_AND_MODELS.md) | LLM provider configuration |

## Requirements

- Python 3.8+
- Java 11+ (for Synthea health record generation)
- API key for Anthropic or OpenAI

### Python Dependencies

```bash
pip install -r requirements.txt
```

Key packages: anthropic, openai, scipy, pandas, nltk, transformers (optional)

## Project Structure

```
202511-Gravidas/
├── run_complete_workflow.py      # Main workflow runner
├── run_interactive_workflow.py   # Interactive TUI launcher
├── scripts/
│   ├── 01b_generate_personas.py
│   ├── 02_generate_health_records.py
│   ├── 03_match_personas_records_enhanced.py
│   ├── 04_conduct_interviews.py
│   ├── analyze_interviews.py
│   ├── 06_generate_academic_report.py
│   ├── 07_journal_selector.py
│   ├── nlp_modules/              # 11 NLP analysis algorithms
│   └── utils/
│       ├── archive_manager.py
│       ├── fhir_semantic_extractor.py
│       └── retry_logic.py
├── config/
│   └── workflow_config.yaml
├── data/                         # Working data directory
├── archive/                      # Timestamped run archives
├── outputs/                      # Generated reports and papers
└── synthea/                      # Synthea installation
```

## Ethical Use

**IMPORTANT: This system generates 100% synthetic (artificial) data.**

### Appropriate Uses
- Algorithm development and testing
- Educational and training purposes
- Operations research and methodology development
- System prototyping and proof-of-concept

### Inappropriate Uses
- Clinical decision-making
- Presenting as real patient data
- Insurance or financial decisions
- Diagnosing or treating real patients

## Citation

If you use GRAVIDAS in your research, please cite:

```bibtex
@software{gravidas2025,
  author = {Polônia, D.},
  title = {GRAVIDAS: Synthetic Maternal Health Interview Research Platform},
  version = {2.1.0},
  year = {2025},
  url = {https://github.com/dpolonia/202511-Gravidas}
}
```

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Issues and pull requests welcome! Please open an issue for questions or suggestions.

---

**Version:** 2.1.0 | **Last Updated:** 2025-11-21 | **Status:** Production Ready
