# Synthetic Gravidas Pipeline

A comprehensive system for generating synthetic pregnant personas with associated health records for research and interview simulations.

## Overview

This pipeline creates 10,000 synthetic personas of women in fertile age (12-60 years) matched with pregnancy-related health records from Synthea. The matched datasets can be used to conduct AI-powered interviews for medical research, training, and scenario simulation.

## Features

- **Persona Retrieval**: Downloads 10,000 female personas from HuggingFace FinePersonas dataset
- **Health Record Generation**: Uses Synthea to generate realistic pregnancy-related medical records
- **Intelligent Matching**: Matches personas to health records based on age compatibility and socioeconomic factors
- **Multi-AI Support**: Choose from 12 different AI models across Claude, OpenAI, and Gemini
- **Flexible Model Selection**: Easy configuration with cost/quality comparisons for each model
- **Protocol-Based Interviews**: Customizable interview protocols for different research scenarios

## Project Structure

```
202511-Gravidas/
├── config/
│   └── config.yaml              # API keys and configuration
├── data/
│   ├── personas/                # Downloaded personas
│   ├── health_records/          # Generated Synthea records
│   ├── matched/                 # Matched persona-record pairs
│   └── interviews/              # Interview results
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

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure API Keys**
   Copy and edit the config file:
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

Run the pipeline in sequence:

```bash
# Step 1: Retrieve personas
python scripts/01_retrieve_personas.py

# Step 2: Generate health records (requires Synthea setup)
python scripts/02_generate_health_records.py

# Step 3: Match personas to records
python scripts/03_match_personas_records.py

# Step 4: Conduct interviews (uses active_provider and active_model from config.yaml)
python scripts/04_conduct_interviews.py --count 10

# Or specify provider and model explicitly
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

- [TUTORIAL.md](TUTORIAL.md) - Complete step-by-step guide
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
