# Gravidas System Architecture - v1.2.1

**Project:** Gravidas - Persona-to-Health-Record Matching System
**Phase:** Phase 3, Task 3.1 - Architecture Documentation
**Version:** 1.2.1
**Date:** 2025-11-16
**Status:** ✅ COMPLETE

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Pipeline Stages](#pipeline-stages)
4. [Data Flow](#data-flow)
5. [Module Structure](#module-structure)
6. [Key Components](#key-components)
7. [Data Models](#data-models)
8. [Integration Points](#integration-points)
9. [Technology Stack](#technology-stack)
10. [Performance Characteristics](#performance-characteristics)

---

## System Overview

Gravidas is a **synthetic healthcare interview generation system** that creates realistic maternal health personas, matches them with synthetic FHIR health records, and conducts AI-powered clinical interviews for research, training, and algorithm development.

### Core Capabilities

1. **Persona Generation**: AI-powered creation of realistic pregnant patient personas
2. **Health Record Generation**: Synthea-based FHIR R4 compliant health records
3. **Semantic Matching**: Intelligent persona-to-record assignment using Hungarian Algorithm
4. **Interview Orchestration**: Protocol-based clinical interviews with multiple LLM providers
5. **Data Analysis**: Comprehensive clinical and cost analytics

### Design Principles

- **Modularity**: Each pipeline stage is independent and can run standalone
- **Reproducibility**: Fixed seeds and version control ensure consistent results
- **Scalability**: Designed to handle 10-10,000+ interviews
- **Cost Optimization**: Multi-provider support with batch processing capabilities
- **Clinical Accuracy**: Evidence-based protocols (ACOG/ADA 2025)

---

## Architecture Diagram

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         GRAVIDAS SYSTEM                              │
│                    Synthetic Interview Pipeline                      │
└─────────────────────────────────────────────────────────────────────┘

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   STAGE 1    │      │   STAGE 2    │      │   STAGE 3    │
│   Persona    │─────▶│   Health     │─────▶│   Semantic   │
│  Generation  │      │   Records    │      │   Matching   │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                      │
       │ personas.json       │ FHIR bundles         │ matched_pairs.json
       ▼                     ▼                      ▼

┌──────────────┐      ┌──────────────┐      ┌──────────────┐
│   STAGE 4    │      │   STAGE 5    │      │   STAGE 6    │
│  Interview   │─────▶│   Analysis   │─────▶│ Validation   │
│  Execution   │      │  & Export    │      │  & Quality   │
└──────────────┘      └──────────────┘      └──────────────┘
       │                     │                      │
       │ interview_logs      │ CSV/JSON             │ reports
       ▼                     ▼                      ▼
```

### Detailed Data Flow

```
┌────────────────────────────────────────────────────────────────────────┐
│                         INPUT LAYER                                     │
├────────────────────────────────────────────────────────────────────────┤
│  • Configuration (YAML)                                                │
│  • API Keys (.env)                                                     │
│  • Interview Protocols (JSON)                                          │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      GENERATION LAYER                                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐         ┌──────────────────┐                   │
│  │ Persona Generator│         │ Synthea Generator│                    │
│  │  (LLM-powered)   │         │  (FHIR R4)       │                    │
│  └────────┬─────────┘         └────────┬─────────┘                    │
│           │                            │                               │
│           │ Semantic Tree             │ Observations                  │
│           │ Demographics              │ Conditions                    │
│           │ Socioeconomic             │ Medications                   │
│           ▼                            ▼                               │
│   data/personas/              synthea/output/fhir/                    │
│   personas.json               [patient_id].json                       │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      PROCESSING LAYER                                   │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │            FHIR Semantic Extractor                            │    │
│  │  • Parse FHIR bundles                                         │    │
│  │  • Extract vital signs (BP, weight, height, BMI)             │    │
│  │  • Build semantic tree from health record                     │    │
│  └────────────────────────┬──────────────────────────────────────┘    │
│                           │                                            │
│                           ▼                                            │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │            Semantic Matcher (Hungarian Algorithm)             │    │
│  │  • Calculate similarity scores (5 factors)                    │    │
│  │  • Optimal assignment                                         │    │
│  │  • Quality validation                                         │    │
│  └────────────────────────┬──────────────────────────────────────┘    │
│                           │                                            │
│                           ▼                                            │
│                  data/matched/                                         │
│                  matched_pairs.json                                    │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      INTERVIEW LAYER                                    │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────┐    ┌──────────────────┐   ┌─────────────────┐  │
│  │ Protocol Selector│───▶│ Interview Engine │──▶│ LLM Provider    │  │
│  │  (5 protocols)   │    │  (Orchestrator)  │   │ (Multi-provider)│  │
│  └──────────────────┘    └──────────────────┘   └─────────────────┘  │
│           │                       │                      │             │
│           │                       │                      │             │
│           ▼                       ▼                      ▼             │
│  PROTO_001-005          Conversation Flow      Claude/GPT/Gemini     │
│                         Question-Answer                               │
│                         Red Flag Detection                            │
│                         Data Mapping                                  │
│                                                                         │
│                           │                                            │
│                           ▼                                            │
│                  data/interviews/                                      │
│                  [interview_id].json                                   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                      ANALYSIS LAYER                                     │
├────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐    │
│  │            Interview Analyzer                                 │    │
│  │  • Extract clinical data                                      │    │
│  │  • Calculate engagement metrics                               │    │
│  │  • Cost analysis                                              │    │
│  │  • Anomaly detection (threshold: 0.7000)                     │    │
│  └────────────────────────┬──────────────────────────────────────┘    │
│                           │                                            │
│                           ▼                                            │
│                  data/analysis/                                        │
│                  interview_summary.csv                                 │
│                  cost_report.json                                      │
│                  anomaly_report.json                                   │
│                                                                         │
└────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                         OUTPUT LAYER                                    │
├────────────────────────────────────────────────────────────────────────┤
│  • Structured CSV (41 columns)                                        │
│  • JSON exports (comprehensive data)                                   │
│  • Validation reports                                                  │
│  • Cost analytics                                                      │
│  • Quality metrics                                                     │
└────────────────────────────────────────────────────────────────────────┘
```

---

## Pipeline Stages

### Stage 1: Persona Generation

**Script:** `scripts/01b_generate_personas.py`

**Purpose:** Generate synthetic pregnant patient personas with comprehensive demographic, socioeconomic, and clinical attributes.

**Inputs:**
- Configuration (persona count, seed)
- LLM API credentials
- Demographic templates

**Outputs:**
- `data/personas/personas.json`

**Process:**
1. Initialize LLM client (default: Claude Haiku 4.5)
2. Generate persona demographics using AI
3. Create semantic tree structure:
   - Demographics (age, gender, location)
   - Socioeconomic (education, income, insurance)
   - Health profile (consciousness, access, readiness)
   - Behavioral (activity, smoking, alcohol)
   - Psychosocial (mental health, stress, support)
   - Pregnancy intentions (gravida, para, planning)
4. Validate completeness
5. Export to JSON

**Key Functions:**
- `generate_persona(count, seed)` - Main generation loop
- `create_semantic_tree(persona_data)` - Build semantic structure
- `validate_persona(persona)` - Quality checks

**Performance:**
- Speed: ~30 seconds for 10 personas
- Cost: ~$0.01 per persona (Claude Haiku)

---

### Stage 2: Health Record Generation

**Script:** `scripts/02_generate_health_records.py`

**Purpose:** Generate synthetic FHIR R4-compliant health records using Synthea.

**Inputs:**
- Configuration (record count, seed)
- Synthea installation path
- Population parameters

**Outputs:**
- `synthea/output/fhir/[patient_id].json` (FHIR bundles)

**Process:**
1. Configure Synthea parameters:
   - Population: Female, fertile age (12-60)
   - Modules: pregnancy, contraceptives, sexual_activity
   - Seed: Fixed for reproducibility
2. Execute Synthea Java process
3. Parse FHIR R4 bundles
4. Validate structure
5. Extract patient demographics

**Key Functions:**
- `run_synthea(count, seed)` - Execute Synthea
- `parse_fhir_bundle(file_path)` - Load FHIR data
- `validate_fhir_structure(bundle)` - Schema validation

**Performance:**
- Speed: ~30-60 seconds for 10 records
- Cost: Free (local generation)

---

### Stage 3: Semantic Matching

**Script:** `scripts/03_match_personas_records_enhanced.py`

**Purpose:** Match personas to health records using semantic similarity and optimal assignment.

**Inputs:**
- `data/personas/personas.json`
- `synthea/output/fhir/*.json`
- Matching configuration

**Outputs:**
- `data/matched/matched_pairs.json`
- `logs/matching_report.json`

**Process:**
1. **FHIR Semantic Extraction** (`scripts/utils/fhir_semantic_extractor.py`):
   - Parse Patient resource (demographics)
   - Parse Observation resources (vitals: BP, weight, height, BMI, gestational age, fetal heart rate)
   - Parse Condition resources (diagnoses)
   - Parse Medication resources
   - Build semantic tree from health record

2. **Similarity Calculation** (`scripts/utils/semantic_tree.py`):
   - Age compatibility (40% weight)
   - Education level (20% weight)
   - Income bracket (15% weight)
   - Marital status (15% weight)
   - Occupation category (10% weight)
   - Calculate weighted similarity score (0-1)

3. **Optimal Assignment** (`scripts/utils/semantic_matcher.py`):
   - Build cost matrix (1 - similarity)
   - Apply Hungarian Algorithm
   - Generate optimal 1:1 matches
   - Quality classification (Excellent ≥0.9, Good ≥0.7, Fair ≥0.5)

4. **Validation**:
   - Verify all personas matched
   - Check similarity distribution
   - Generate quality report

**Key Functions:**
- `build_semantic_tree_from_fhir(bundle, patient_id, age)` - FHIR to semantic tree
- `calculate_semantic_tree_similarity(persona_tree, record_tree)` - Similarity scoring
- `hungarian_matching(personas, records, similarity_matrix)` - Optimal assignment

**Performance:**
- Speed: ~5 seconds for 100 persona-record pairs
- Success Rate: 100% (all personas matched)
- Quality: Average similarity score ~0.75-0.85

---

### Stage 4: Interview Execution

**Script:** `scripts/04_conduct_interviews.py`

**Purpose:** Conduct AI-powered clinical interviews using evidence-based protocols.

**Inputs:**
- `data/matched/matched_pairs.json`
- `data/interview_protocols.json`
- LLM API credentials
- Interview configuration

**Outputs:**
- `data/interviews/[interview_id].json`
- `logs/interview_[timestamp].log`

**Process:**
1. **Protocol Selection**:
   - Load matched persona-record pair
   - Analyze risk factors (age, conditions, access barriers)
   - Select appropriate protocol (PROTO_001 through PROTO_005)

2. **Interview Orchestration**:
   - Initialize LLM client (multi-provider support via `universal_ai_client.py`)
   - Load protocol sections and questions
   - Build conversation context
   - Execute interview loop:
     a. Present question from protocol
     b. Generate patient response via LLM
     c. Apply follow-up prompts if needed
     d. Check for red flags
     e. Map responses to persona data fields
     f. Continue to next question

3. **Data Capture**:
   - Full conversation transcript
   - Response metadata (tokens, cost, timing)
   - Red flags identified
   - Resources provided
   - Data field updates

**Key Functions:**
- `select_protocol(persona)` - Protocol selection logic
- `conduct_interview(persona, record, protocol, llm_client)` - Main interview loop
- `check_red_flags(question, response)` - Safety monitoring
- `map_response_to_fields(response, data_mapping)` - Data extraction

**Performance:**
- Speed: 2-3 minutes per interview
- Cost: $0.08 per interview (Claude Sonnet 4.5)
- Token Usage: ~10,000 tokens average

**Supported LLM Providers:**
- Anthropic (Claude Haiku, Sonnet, Opus)
- OpenAI (GPT-4, GPT-5)
- Google (Gemini 2.5 Pro, Flash)
- Together AI (Llama models)
- Groq (Ultra-fast inference)
- AWS Bedrock, Azure OpenAI, Mistral, xAI, Cohere, Perplexity

---

### Stage 5: Analysis & Export

**Script:** `scripts/analyze_interviews.py`

**Purpose:** Comprehensive analysis and structured export of interview data.

**Inputs:**
- `data/interviews/*.json`
- `data/matched/matched_pairs.json`

**Outputs:**
- `data/analysis/interview_summary.csv` (41 columns)
- `data/analysis/cost_report.json`
- `data/analysis/anomaly_report.json`

**Process:**
1. **Data Extraction**:
   - Demographics from persona
   - Clinical data from responses
   - Conversation metrics (turns, words, engagement)
   - Cost data (tokens, pricing)

2. **Topic Analysis**:
   - Identify 26 standardized topics covered
   - Pregnancy planning, prenatal care, nutrition
   - Mental health, support systems, birth planning
   - Financial concerns, work impact, healthcare access

3. **Anomaly Detection**:
   - Calculate semantic similarity score
   - Apply calibrated threshold (0.7000)
   - Classify anomalies (Critical <0.5, Warning 0.5-0.7, Acceptable 0.7-0.8, High Quality ≥0.8)
   - Generate alerts for low-quality matches

4. **Cost Analysis**:
   - Token usage by stage
   - Per-interview costs
   - Provider comparison
   - Budget projections

5. **Export**:
   - Structured CSV with 41 standardized columns
   - JSON exports for programmatic access
   - Validation reports

**Key Functions:**
- `extract_clinical_data(interview)` - Parse medical information
- `calculate_engagement_metrics(interview)` - Conversation quality
- `detect_anomalies(similarity_score, threshold)` - Quality control
- `export_to_csv(interviews, output_path)` - Structured export

**Performance:**
- Speed: ~10 seconds for 100 interviews
- Completeness: 100% (all interviews analyzed)

---

### Stage 6: Validation & Quality Control

**Scripts:**
- `scripts/debug_semantic_trees.py`
- `scripts/validate_semantic_matching.py`
- `scripts/validate_threshold_edge_cases.py`
- `scripts/test_semantic_implementation.py`

**Purpose:** Automated testing and quality validation.

**Capabilities:**

1. **Semantic Tree Validation**:
   - Test FHIR parsing success rate (target: 100%)
   - Verify null safety
   - Validate data completeness

2. **Matching Validation**:
   - Test similarity calculations
   - Verify match quality distribution
   - Validate assignment optimality

3. **Threshold Validation**:
   - Test edge cases near threshold (0.7000)
   - Verify false positive/negative rates (target: 0%)
   - Validate alert levels

4. **Integration Testing**:
   - End-to-end workflow tests
   - Performance benchmarks
   - Error handling

**Test Coverage:** 100+ automated tests

---

## Data Flow

### Data Transformations

```
1. AI Generation → Persona JSON
   ├─ LLM prompt engineering
   ├─ Structured data extraction
   └─ Semantic tree construction

2. Synthea → FHIR R4 Bundle
   ├─ Population simulation
   ├─ Clinical event generation
   └─ Standard-compliant formatting

3. FHIR Bundle → Semantic Tree
   ├─ Resource parsing (Patient, Observation, Condition, Medication)
   ├─ Vital signs extraction
   └─ Semantic structure alignment

4. Persona + Record → Similarity Score
   ├─ Multi-factor comparison
   ├─ Weighted scoring
   └─ Normalization (0-1 scale)

5. Similarity Matrix → Optimal Matches
   ├─ Hungarian algorithm
   ├─ 1:1 assignment
   └─ Quality classification

6. Matched Pair + Protocol → Interview
   ├─ Risk stratification
   ├─ Protocol selection
   ├─ LLM-powered conversation
   └─ Response capture

7. Interview → Structured Analytics
   ├─ Clinical data extraction
   ├─ Metric calculation
   ├─ Anomaly detection
   └─ CSV/JSON export
```

### Data Persistence

| Stage | Format | Location | Size (10 samples) |
|-------|--------|----------|-------------------|
| Personas | JSON | `data/personas/personas.json` | ~50 KB |
| Health Records | FHIR JSON | `synthea/output/fhir/*.json` | ~2 MB |
| Matched Pairs | JSON | `data/matched/matched_pairs.json` | ~100 KB |
| Interviews | JSON | `data/interviews/*.json` | ~500 KB |
| Analysis | CSV | `data/analysis/interview_summary.csv` | ~50 KB |
| Logs | Text | `logs/*.log` | ~100 KB |

---

## Module Structure

```
202511-Gravidas/
│
├── scripts/                          # Main pipeline scripts
│   ├── 01b_generate_personas.py      # Stage 1: Persona generation
│   ├── 02_generate_health_records.py # Stage 2: Synthea execution
│   ├── 03_match_personas_records_enhanced.py # Stage 3: Matching
│   ├── 04_conduct_interviews.py      # Stage 4: Interviews
│   ├── analyze_interviews.py         # Stage 5: Analysis
│   ├── run_workflow.py               # Orchestrator
│   ├── interactive_interviews.py     # Interactive UI
│   │
│   └── utils/                        # Shared utilities
│       ├── fhir_semantic_extractor.py # FHIR parsing
│       ├── semantic_tree.py          # Semantic structures
│       ├── semantic_matcher.py       # Matching logic
│       ├── common_loaders.py         # Data loading
│       ├── validators.py             # Validation functions
│       ├── exceptions.py             # Custom exceptions
│       └── retry_logic.py            # Resilience
│
├── data/                             # Data storage
│   ├── personas/                     # Generated personas
│   ├── matched/                      # Match results
│   ├── interviews/                   # Interview logs
│   ├── analysis/                     # Analytics outputs
│   └── interview_protocols.json      # Clinical protocols
│
├── tests/                            # Automated tests
│   ├── test_semantic_tree_generation.py
│   ├── test_semantic_similarity.py
│   ├── test_anomaly_detection.py
│   └── test_integration_semantic_matching.py
│
├── config/                           # Configuration
│   ├── config.yaml                   # Main config
│   └── workflow_config.yaml          # Workflow settings
│
├── logs/                             # Log files
│   ├── workflow.log                  # Pipeline logs
│   ├── interview_*.log               # Interview logs
│   └── *_report.json                 # Validation reports
│
└── docs/                             # Documentation
    ├── ARCHITECTURE.md               # This file
    ├── API_REFERENCE.md              # API docs
    ├── COST_BUDGET_ANALYSIS.md       # Cost analysis
    ├── INTERVIEW_PROTOCOL_USAGE_GUIDE.md # Protocol guide
    └── ETHICAL_USE.md                # Ethics guidelines
```

---

## Key Components

### 1. Universal AI Client (`universal_ai_client.py`)

**Purpose:** Unified interface for multiple LLM providers

**Supported Providers:**
- Anthropic Claude (Haiku, Sonnet, Opus)
- OpenAI (GPT-4, GPT-5)
- Google (Gemini 2.5 Pro, Flash)
- AWS Bedrock
- Azure OpenAI
- Together AI
- Groq
- Mistral
- xAI
- Cohere
- Perplexity

**Key Features:**
- Automatic provider detection
- Unified message format
- Cost tracking
- Batch API support (50% discount)
- Retry logic with exponential backoff
- Token counting

**API:**
```python
class UniversalAIClient:
    def __init__(self, provider: str, model: str, api_key: str)
    def send_message(self, messages: List[Dict], max_tokens: int) -> Dict
    def get_cost(self, input_tokens: int, output_tokens: int) -> float
```

---

### 2. FHIR Semantic Extractor (`fhir_semantic_extractor.py`)

**Purpose:** Extract semantic data from FHIR bundles

**Capabilities:**
- Parse FHIR R4 bundles
- Extract Patient demographics
- Parse Observation resources (vitals)
- Extract Conditions (diagnoses)
- Extract Medications
- Build semantic tree structure

**Vitals Extracted:**
- Blood pressure (systolic/diastolic)
- Maternal weight
- Maternal height
- Maternal BMI
- Weight gain
- Gestational age
- Fetal heart rate

**Success Rate:** 100% (Phase 1 improvement from 16.7%)

**API:**
```python
def build_semantic_tree_from_fhir(
    fhir_bundle: Dict,
    patient_id: str,
    age: int
) -> SemanticTree
```

---

### 3. Semantic Matcher (`semantic_matcher.py`)

**Purpose:** Optimal persona-to-record assignment

**Algorithm:** Hungarian Algorithm (optimal assignment in O(n³))

**Similarity Factors:**
- Age compatibility (40% weight)
- Education level (20% weight)
- Income bracket (15% weight)
- Marital status (15% weight)
- Occupation (10% weight)

**Quality Thresholds:**
- Excellent: ≥0.9
- Good: ≥0.7
- Fair: ≥0.5
- Poor: <0.5

**API:**
```python
def calculate_semantic_tree_similarity(
    persona_tree: SemanticTree,
    record_tree: SemanticTree
) -> Tuple[float, Dict[str, float]]

def hungarian_matching(
    personas: List[Dict],
    records: List[Dict],
    similarity_matrix: np.ndarray
) -> List[Tuple[int, int, float]]
```

---

### 4. Interview Orchestrator (`04_conduct_interviews.py`)

**Purpose:** Conduct protocol-based clinical interviews

**Features:**
- Protocol selection (5 protocols)
- Multi-provider LLM support
- Red flag detection
- Data mapping
- Resource provision
- Cost tracking

**Protocols:**
1. PROTO_001: First-Time Mothers (45 min)
2. PROTO_002: Experienced Mothers (35 min)
3. PROTO_003: High-Risk Pregnancy (50 min)
4. PROTO_004: Low SES/Access Barriers (50 min)
5. PROTO_005: Routine Prenatal Care (30 min)

**API:**
```python
def select_protocol(persona: Dict) -> Dict
def conduct_interview(
    persona: Dict,
    record: Dict,
    protocol: Dict,
    llm_client: UniversalAIClient
) -> Dict
```

---

## Data Models

### Persona Structure

```python
{
    "id": str,                    # Unique identifier
    "name": str,                  # Full name
    "age": int,                   # Age in years
    "semantic_tree": {
        "demographics": {
            "age": int,
            "gender": str,
            "race_ethnicity": str,
            "location_type": str  # urban/suburban/rural
        },
        "socioeconomic": {
            "education_level": str,  # high_school/bachelor/master/phd
            "income_bracket": str,   # low/middle/high
            "insurance_status": str, # insured/underinsured/uninsured
            "occupation": str
        },
        "health_profile": {
            "health_consciousness": int,  # 1-5 scale
            "healthcare_access": int,     # 1-5 scale
            "pregnancy_readiness": int,   # 1-5 scale
            "chronic_conditions": List[str]
        },
        "behavioral": {
            "physical_activity_level": int,  # 1-5 scale
            "smoking_status": str,           # never/former/current
            "alcohol_consumption": str,      # none/light/moderate/heavy
            "substance_use": bool
        },
        "psychosocial": {
            "mental_health_status": int,  # 1-5 scale
            "stress_level": int,          # 1-5 scale
            "social_support": int,        # 1-5 scale
            "relationship_status": str
        },
        "pregnancy_intentions": {
            "gravida": int,              # Number of pregnancies
            "para": int,                 # Number of births
            "preconception_care": bool,
            "pregnancy_planning": str    # planned/unplanned/ambivalent
        }
    }
}
```

### FHIR Bundle Structure (Simplified)

```python
{
    "resourceType": "Bundle",
    "type": "collection",
    "entry": [
        {
            "resource": {
                "resourceType": "Patient",
                "id": str,
                "gender": str,
                "birthDate": str,
                "address": [...],
                "name": [...]
            }
        },
        {
            "resource": {
                "resourceType": "Observation",
                "code": {"coding": [{"code": str, "display": str}]},
                "valueQuantity": {"value": float, "unit": str},
                "effectiveDateTime": str
            }
        },
        {
            "resource": {
                "resourceType": "Condition",
                "code": {"coding": [{"code": str, "display": str}]},
                "onsetDateTime": str
            }
        }
    ]
}
```

### Interview Structure

```python
{
    "interview_id": str,
    "persona_id": str,
    "record_id": str,
    "protocol_id": str,
    "timestamp": str,
    "conversation": [
        {
            "turn": int,
            "role": str,          # "interviewer" or "patient"
            "content": str,
            "tokens": int,
            "timestamp": str
        }
    ],
    "responses": {
        "Q1.1": str,
        "Q1.2": str,
        ...
    },
    "red_flags": [
        {
            "question_id": str,
            "severity": str,      # "critical" or "warning"
            "action": str,
            "response": str
        }
    ],
    "data_updates": {
        "behavioral.smoking_status": str,
        ...
    },
    "resources_provided": List[str],
    "metadata": {
        "total_tokens": int,
        "input_tokens": int,
        "output_tokens": int,
        "cost_usd": float,
        "duration_seconds": float,
        "llm_provider": str,
        "llm_model": str
    }
}
```

---

## Integration Points

### External Systems

1. **LLM APIs**
   - Anthropic Claude API
   - OpenAI API
   - Google Gemini API
   - AWS Bedrock
   - Azure OpenAI
   - Together AI, Groq, Mistral, xAI, Cohere, Perplexity

2. **Synthea**
   - Java-based synthetic patient generator
   - Local execution via subprocess
   - FHIR R4 output

3. **File System**
   - JSON for structured data
   - CSV for tabular exports
   - YAML for configuration
   - Text logs for debugging

### Internal Interfaces

1. **Pipeline Orchestrator** (`run_workflow.py`)
   - Coordinates all pipeline stages
   - Manages configuration
   - Handles errors and retries

2. **Data Loaders** (`utils/common_loaders.py`)
   - Standardized data loading
   - Validation on load
   - Error handling

3. **Validators** (`utils/validators.py`)
   - Schema validation
   - Data quality checks
   - Completeness verification

---

## Technology Stack

### Core Technologies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Language** | Python | 3.8+ | Primary implementation |
| **LLM Integration** | Anthropic SDK | Latest | Claude API |
| **LLM Integration** | OpenAI SDK | Latest | GPT API |
| **LLM Integration** | Google GenAI | Latest | Gemini API |
| **Health Records** | Synthea | 3.x | FHIR generation |
| **Testing** | pytest | Latest | Automated testing |
| **Data** | pandas | Latest | Analysis and export |
| **Optimization** | scipy | Latest | Hungarian algorithm |
| **Configuration** | PyYAML | Latest | Config management |
| **Logging** | Python logging | Built-in | Diagnostics |

### Python Dependencies

```
anthropic>=0.25.0
openai>=1.0.0
google-generativeai>=0.5.0
scipy>=1.10.0
pandas>=2.0.0
pyyaml>=6.0
pytest>=7.0.0
python-dotenv>=1.0.0
```

### Infrastructure Requirements

- **Compute**: 2-4 CPU cores
- **Memory**: 4-8 GB RAM
- **Storage**: 10-50 GB (depending on scale)
- **Network**: Stable internet for API calls
- **Java Runtime**: JRE 11+ for Synthea

---

## Performance Characteristics

### Throughput

| Operation | Time | Throughput |
|-----------|------|------------|
| Generate 10 personas | 30 sec | 20 personas/min |
| Generate 10 health records | 60 sec | 10 records/min |
| Match 100 pairs | 5 sec | 1,200 matches/min |
| Conduct 1 interview | 150 sec | 0.4 interviews/min |
| Analyze 100 interviews | 10 sec | 600 analyses/min |

### Scalability

| Scale | Personas | Records | Interviews | Time | Cost (Sonnet 4.5) |
|-------|----------|---------|------------|------|-------------------|
| **Pilot** | 10 | 10 | 10 | ~30 min | $4 |
| **Small** | 100 | 100 | 100 | ~3 hours | $40 |
| **Medium** | 1,000 | 1,000 | 1,000 | ~30 hours | $400 |
| **Large** | 10,000 | 10,000 | 10,000 | ~12 days | $4,000 |

### Optimization Strategies

1. **Batch Processing**: Use LLM Batch APIs for 50% cost savings
2. **Prompt Caching**: Cache protocol contexts for 50% input token savings
3. **Parallel Execution**: Run independent stages concurrently
4. **Model Selection**: Use appropriate model tier for each task (Haiku for simple, Sonnet for complex)
5. **Token Optimization**: Minimize prompt verbosity, use efficient data structures

### Bottlenecks

1. **LLM API Rate Limits**: Primary bottleneck for interviews
   - Mitigation: Use multiple providers, batch processing
2. **Synthea Generation**: CPU-bound health record creation
   - Mitigation: Parallel Synthea instances, pre-generation
3. **Disk I/O**: Large FHIR files
   - Mitigation: SSD storage, streaming parsers

---

## Error Handling

### Retry Logic

- **API Failures**: Exponential backoff (3 retries)
- **Network Issues**: Automatic retry with timeout
- **Rate Limiting**: Queue and delay
- **Transient Errors**: Retry with fresh connection

### Validation Checks

1. **Input Validation**: Schema checks before processing
2. **Output Validation**: Completeness verification
3. **Data Quality**: Null checks, range validation
4. **Semantic Validation**: Consistency across pipeline

### Logging

- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL
- **Destinations**: Console + file (`logs/workflow.log`)
- **Format**: Timestamp, level, message, context
- **Rotation**: Daily rotation, 30-day retention

---

## Security & Privacy

### Data Protection

- **Synthetic Only**: No real patient data
- **Local Storage**: All data stored locally
- **API Keys**: Environment variables, never committed
- **Access Control**: File system permissions

### API Security

- **Key Management**: `.env` file (gitignored)
- **HTTPS Only**: All API calls encrypted
- **Token Refresh**: Automatic credential rotation
- **Rate Limiting**: Respect provider limits

---

## Monitoring & Observability

### Metrics Tracked

1. **Performance Metrics**
   - Pipeline execution time
   - Per-stage duration
   - Throughput (items/min)

2. **Quality Metrics**
   - FHIR parsing success rate (target: 100%)
   - Match quality distribution
   - Interview completion rate (target: ≥95%)
   - Anomaly detection accuracy

3. **Cost Metrics**
   - Token usage (input/output)
   - Cost per interview
   - Provider comparison
   - Budget tracking

### Health Checks

- **API Connectivity**: Test before pipeline execution
- **Data Availability**: Verify input files exist
- **Disk Space**: Check sufficient storage
- **Configuration Validity**: Validate YAML/JSON

---

## Future Architecture Enhancements

### Planned Improvements

1. **Distributed Processing**: Multi-node execution for large-scale generation
2. **Real-time Analytics**: Dashboard for live monitoring
3. **API Service**: REST API for interview execution
4. **Database Backend**: PostgreSQL for structured storage
5. **Kubernetes Deployment**: Container orchestration
6. **Message Queue**: RabbitMQ/Kafka for async processing

---

## Conclusion

The Gravidas architecture is designed for:

✅ **Modularity**: Independent, reusable components
✅ **Scalability**: 10 to 10,000+ interviews
✅ **Reproducibility**: Fixed seeds, version control
✅ **Cost-Effectiveness**: Multi-provider support, optimization
✅ **Clinical Accuracy**: Evidence-based protocols
✅ **Quality**: Comprehensive testing and validation

The system successfully generates synthetic maternal health interviews at scale, providing realistic training data for research, algorithm development, and healthcare education.

---

**Document Prepared By:** Claude Code
**Date:** 2025-11-16
**Version:** 1.2.1
**Status:** Task 3.1 COMPLETE ✅
