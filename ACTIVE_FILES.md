# Gravidas Pipeline - Active Files Structure

**Last Updated:** 2025-11-14
**Archive:** `archive/run_20251114_165407/`

This document describes the current active file structure after cleanup and archiving.

---

## 📁 Directory Structure

```
202511-Gravidas/
├── config/                          # Configuration files
│   └── workflow_config.yaml         # Main workflow configuration
│
├── data/                            # Active data directories
│   ├── analysis/                    # Interview analysis results
│   ├── health_records/              # Generated health records (FHIR)
│   ├── interviews/                  # Conducted interviews
│   ├── matched/                     # Matched persona-record pairs
│   ├── personas/                    # Generated synthetic personas
│   └── validation/                  # Validation reports
│
├── scripts/                         # Active Python scripts
│   ├── __init__.py                  # Package initializer
│   ├── 01b_generate_personas.py    # Persona generation (main)
│   ├── 02_generate_health_records.py # Health record extraction
│   ├── 03_match_personas_records_enhanced.py # Enhanced matching
│   ├── 04_conduct_interviews.py    # Interview conductor
│   ├── analyze_interviews.py       # Interview analysis
│   ├── test_semantic_implementation.py # Validation tests
│   ├── run_workflow.py              # Workflow orchestrator
│   ├── interactive_interviews.py   # Interactive interview mode
│   ├── enhanced_models_database.py # AI models database
│   ├── universal_ai_client.py      # Universal AI client
│   └── utils/                       # Utility modules
│       ├── __init__.py
│       ├── common_loaders.py
│       ├── semantic_matcher.py
│       └── semantic_tree.py
│
├── logs/                            # Execution logs
├── outputs/                         # Workflow reports
├── synthea/                         # Synthea FHIR generator
├── archive/                         # Historical archives
│   └── run_20251114_165407/        # Latest archive
│
└── docs/                            # Documentation (optional)

```

---

## 🔧 Active Scripts

### Core Pipeline Scripts

| Script | Purpose | Stage |
|--------|---------|-------|
| `01b_generate_personas.py` | Generate synthetic personas with semantic attributes | 1 |
| `02_generate_health_records.py` | Extract health profiles from Synthea FHIR data | 2 |
| `03_match_personas_records_enhanced.py` | Match personas to records using semantic + demographic scoring | 3 |
| `04_conduct_interviews.py` | Conduct AI-powered interviews | 4 |
| `analyze_interviews.py` | Analyze interview transcripts (NLP, cost, clinical) | 5 |
| `test_semantic_implementation.py` | Validate semantic trees and data quality | 6 |

### Workflow Management

| Script | Purpose |
|--------|---------|
| `run_workflow.py` | Main workflow orchestrator - executes pipeline stages |
| `interactive_interviews.py` | Interactive interview mode for testing |

### Support Modules

| Module | Purpose |
|--------|---------|
| `enhanced_models_database.py` | AI model database (15+ providers, 60+ models) |
| `universal_ai_client.py` | Universal AI client factory (Anthropic, OpenAI, Google, etc.) |
| `utils/common_loaders.py` | Common data loading utilities |
| `utils/semantic_matcher.py` | Semantic tree matching algorithms |
| `utils/semantic_tree.py` | Semantic tree data structures |

---

## 📄 Essential Documentation

| File | Description |
|------|-------------|
| `README.md` | Main project documentation |
| `GETTING_STARTED.md` | Quick start guide |
| `QUICK_START.md` | Fast setup instructions |
| `API_KEY_SETUP.md` | API key configuration guide |
| `PIPELINE_EXECUTION_GUIDE.md` | Detailed pipeline execution instructions |
| `MODEL_NAMES_REFERENCE.md` | AI model reference guide |
| `INTEGRATION_SUMMARY.md` | Integration overview |
| `DOCUMENTATION_INDEX.md` | Documentation index |
| `CHANGELOG.md` | Version history |
| `VERSION` | Current version number |
| `ACTIVE_FILES.md` | This file - current structure reference |

---

## 🗂️ Archived Content

All deprecated scripts, old data, and historical documentation have been moved to:

```
archive/run_20251114_165407/
├── data/          # Old backups and experimental data
├── scripts/       # Deprecated scripts
├── docs/          # Old documentation and tutorials
├── logs/          # Historical logs
├── outputs/       # Old outputs
└── README.md      # Archive documentation
```

### Archived Scripts (No Longer Used)

- `01_retrieve_personas.py` - Replaced by `01b_generate_personas.py`
- `02b_generate_health_records_progressive.py` - Progressive variant (deprecated)
- `02c_generate_10k_progressive.py` - Large-scale variant (deprecated)
- `03_match_personas_100_progressive.py` - Progressive matching (deprecated)
- `03_match_personas_records.py` - Replaced by enhanced version
- `debug_finepersonas.py` - Debug utility (no longer needed)
- `debug_finepersonas_detailed.py` - Debug utility (no longer needed)
- `generate_test_data.py` - Test data generator (deprecated)
- `save_finepersonas_profiles.py` - Profile saver (deprecated)
- `test_workflow.py` - Old workflow testing (deprecated)
- `validate_pipeline_data.py` - Old validation (deprecated)
- `validate_workflow_setup.py` - Old validation (deprecated)

### Archived Data

- `backup_synthea_1k/` - Old Synthea backup
- `backup_synthea_run1/` - Old Synthea backup
- `batch_requests/` - Batch API experiments
- `batch_results/` - Batch API results
- `finepersonas_profiles/` - Old profile storage
- `hf_cache/` - HuggingFace cache
- `personas_additional/` - Experimental personas
- `personas_combined/` - Combined datasets
- `suspension_checkpoint/` - Old checkpoint system

### Archived Documentation

- `TUTORIAL.md` - Replaced by GETTING_STARTED.md
- `TUTORIAL_ENHANCED_MATCHING.md` - Outdated
- `TUTORIAL_TESTE_COMPLETO.md` - Outdated
- `INDICE_DOCUMENTACAO.md` - Outdated index
- `COMPLETE_TESTING_TUTORIAL.md` - Outdated
- `CLEAN_RUN_TUTORIAL.md` - Outdated
- `APPLY_IMPROVEMENTS.md` - Historical
- `BUNDLE_SUMMARY.txt` - Historical
- `RESTART_INSTRUCTIONS.md` - Historical
- `gravidas-improvements.bundle` - Historical patch

---

## 🚀 Running the Pipeline

### Quick Start

```bash
# Run complete pipeline with quick test preset
python scripts/run_workflow.py --preset quick_test

# Run complete pipeline with standard settings
python scripts/run_workflow.py --preset standard

# Run specific stages
python scripts/run_workflow.py --stages generate_personas,match_personas_records

# Run with custom settings
python scripts/run_workflow.py --personas 50 --model claude-sonnet-4-5
```

### Configuration

Main configuration file: `config/workflow_config.yaml`

Presets available:
- `quick_test` - 10 personas/records for testing
- `standard` - 100 personas/records for normal runs
- `production` - 1000 personas/records for production

---

## 📊 Data Flow

```
1. Personas Generation → data/personas/
2. Health Records → data/health_records/
3. Matching → data/matched/
4. Interviews → data/interviews/
5. Analysis → data/analysis/
6. Validation → data/validation/
```

---

## 🔍 Finding Files

### Active Data
All current data is in `data/` subdirectories

### Historical Data
Check `archive/run_20251114_165407/` for archived data

### Scripts
All active scripts are in `scripts/` (11 total)

### Configuration
`config/workflow_config.yaml` is the single source of truth

---

## ✅ Cleanup Summary

- **Scripts archived:** 12
- **Data directories archived:** 9
- **Documentation archived:** 10
- **Active scripts:** 11
- **Active data directories:** 6

**Archive timestamp:** 2025-11-14 16:54:07 UTC

---

## 📝 Notes

- Only actively used files remain in the main codebase
- All deprecated/experimental code is properly archived with documentation
- Archive includes README explaining what was moved and why
- Main codebase is now clean and production-ready
- All pipeline stages are fully functional and tested

---

**For questions about archived files, see:** `archive/run_20251114_165407/README.md`
