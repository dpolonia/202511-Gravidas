# Gravidas API Reference - v1.2.1

**Project:** Gravidas - Persona-to-Health-Record Matching System
**Phase:** Phase 3, Task 3.1.3 - API Documentation
**Version:** 1.2.1
**Date:** 2025-11-16
**Status:** ✅ COMPLETE

---

## Table of Contents

1. [Overview](#overview)
2. [Core Modules](#core-modules)
3. [Pipeline Scripts](#pipeline-scripts)
4. [Utility Modules](#utility-modules)
5. [Data Structures](#data-structures)
6. [Configuration](#configuration)
7. [Error Handling](#error-handling)

---

## Overview

This document provides comprehensive API documentation for the Gravidas system. All functions include type hints and docstrings following Google-style documentation standards.

### Import Conventions

```python
# Core utilities
from scripts.utils.semantic_tree import (
    PersonaSemanticTree,
    RecordSemanticTree,
    calculate_semantic_tree_similarity
)
from scripts.utils.fhir_semantic_extractor import build_semantic_tree_from_fhir
from scripts.utils.semantic_matcher import hungarian_matching

# Universal AI client
from scripts.universal_ai_client import UniversalAIClient

# Data loaders
from scripts.utils.common_loaders import load_personas, load_fhir_records
```

---

## Core Modules

### scripts.utils.semantic_tree

Semantic tree data structures and similarity calculations.

#### Classes

##### `PersonaSemanticTree`

Semantic representation of a persona with hierarchical attributes.

```python
@dataclass
class PersonaSemanticTree:
    demographics: DemographicsNode
    socioeconomic: SocioeconomicNode
    health_profile: HealthProfileNode
    behavioral: BehavioralNode
    psychosocial: PsychosocialNode
    pregnancy_intentions: PregnancyIntentionsNode

    def to_dict(self) -> Dict[str, Any]:
        """Convert semantic tree to dictionary."""

    def validate(self) -> bool:
        """Validate all nodes in the semantic tree."""
```

**Example:**
```python
persona_tree = PersonaSemanticTree(
    demographics=DemographicsNode(age=28, gender="female", location_type="urban"),
    socioeconomic=SocioeconomicNode(...),
    # ... other nodes
)
is_valid = persona_tree.validate()
dict_repr = persona_tree.to_dict()
```

##### `RecordSemanticTree`

Semantic representation of a health record extracted from FHIR data.

```python
@dataclass
class RecordSemanticTree:
    patient_demographics: PatientDemographicsNode
    clinical_profile: ClinicalProfileNode
    utilization: UtilizationNode
    risk_factors: RiskFactorsNode
    pregnancy_profile: PregnancyProfile

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""

    def validate(self) -> bool:
        """Validate all nodes."""
```

#### Functions

##### `calculate_semantic_tree_similarity()`

Calculate weighted similarity between persona and record semantic trees.

```python
def calculate_semantic_tree_similarity(
    persona_tree: PersonaSemanticTree,
    record_tree: RecordSemanticTree
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate semantic similarity score between persona and health record.

    Args:
        persona_tree: Persona semantic tree
        record_tree: Health record semantic tree

    Returns:
        Tuple of (overall_similarity, component_scores)
        - overall_similarity: Weighted average score (0-1)
        - component_scores: Individual factor scores

    Component Weights:
        - Age compatibility: 40%
        - Education level: 20%
        - Income bracket: 15%
        - Marital status: 15%
        - Occupation: 10%
    """
```

**Example:**
```python
similarity, components = calculate_semantic_tree_similarity(
    persona_tree,
    record_tree
)

print(f"Overall similarity: {similarity:.3f}")
print(f"Age compatibility: {components['age']:.3f}")
print(f"Education match: {components['education']:.3f}")
```

##### `persona_tree_from_dict()`

Construct PersonaSemanticTree from dictionary.

```python
def persona_tree_from_dict(data: Dict[str, Any]) -> PersonaSemanticTree:
    """
    Build PersonaSemanticTree from dictionary representation.

    Args:
        data: Dictionary with semantic tree structure

    Returns:
        PersonaSemanticTree instance

    Raises:
        ValueError: If required fields missing
        TypeError: If field types incorrect
    """
```

---

### scripts.utils.fhir_semantic_extractor

FHIR bundle parsing and semantic tree extraction.

#### Functions

##### `build_semantic_tree_from_fhir()`

Primary function to extract semantic tree from FHIR bundle.

```python
def build_semantic_tree_from_fhir(
    fhir_bundle: Dict[str, Any],
    patient_id: str,
    age: int
) -> RecordSemanticTree:
    """
    Build semantic tree from FHIR R4 bundle.

    Args:
        fhir_bundle: FHIR bundle dictionary
        patient_id: Patient identifier
        age: Patient age in years

    Returns:
        RecordSemanticTree with extracted data

    Process:
        1. Parse Patient resource (demographics)
        2. Extract Observations (vital signs)
        3. Extract Conditions (diagnoses)
        4. Extract Medications
        5. Build semantic tree structure

    Vitals Extracted:
        - Blood pressure (systolic/diastolic)
        - Maternal weight, height, BMI
        - Weight gain
        - Gestational age
        - Fetal heart rate
    """
```

**Example:**
```python
with open('synthea/output/fhir/patient_123.json', 'r') as f:
    fhir_bundle = json.load(f)

record_tree = build_semantic_tree_from_fhir(
    fhir_bundle=fhir_bundle,
    patient_id="patient_123",
    age=28
)

print(f"Patient age: {record_tree.patient_demographics.age}")
print(f"BP: {record_tree.pregnancy_profile.blood_pressure_systolic}/",
      f"{record_tree.pregnancy_profile.blood_pressure_diastolic}")
```

##### `extract_vitals_from_observations()`

Extract vital signs from FHIR Observation resources.

```python
def extract_vitals_from_observations(
    observations: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Extract pregnancy vital signs from FHIR Observations.

    Args:
        observations: List of FHIR Observation resources

    Returns:
        Dictionary with vital signs:
            - blood_pressure_systolic: float (mmHg)
            - blood_pressure_diastolic: float (mmHg)
            - maternal_weight: float (kg)
            - maternal_height: float (cm)
            - maternal_bmi: float
            - weight_gain: float (kg)
            - gestational_age: int (weeks)
            - fetal_heart_rate: int (bpm)

    LOINC Codes Mapped:
        - 8480-6: Systolic BP
        - 8462-4: Diastolic BP
        - 29463-7: Body Weight
        - 8302-2: Body Height
        - 39156-5: Body Mass Index
        - 18185-9: Gestational Age
        - 55283-6: Fetal Heart Rate
    """
```

---

### scripts.utils.semantic_matcher

Optimal persona-to-record matching using Hungarian Algorithm.

#### Functions

##### `hungarian_matching()`

Perform optimal assignment using Hungarian Algorithm.

```python
def hungarian_matching(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    similarity_matrix: np.ndarray
) -> List[Tuple[int, int, float]]:
    """
    Find optimal 1:1 matching between personas and health records.

    Args:
        personas: List of persona dictionaries
        records: List of health record dictionaries
        similarity_matrix: NxM similarity scores matrix

    Returns:
        List of (persona_idx, record_idx, similarity_score) tuples

    Algorithm:
        Hungarian Algorithm (Kuhn-Munkres) for optimal assignment
        Complexity: O(n³) where n = min(personas, records)

    Quality Thresholds:
        - Excellent: similarity ≥ 0.9
        - Good: similarity ≥ 0.7
        - Fair: similarity ≥ 0.5
        - Poor: similarity < 0.5
    """
```

**Example:**
```python
from scipy.optimize import linear_sum_assignment

# Calculate similarity matrix
n_personas = len(personas)
n_records = len(records)
sim_matrix = np.zeros((n_personas, n_records))

for i, persona in enumerate(personas):
    for j, record in enumerate(records):
        sim, _ = calculate_semantic_tree_similarity(
            persona_tree_from_dict(persona['semantic_tree']),
            record['semantic_tree']
        )
        sim_matrix[i, j] = sim

# Perform matching
matches = hungarian_matching(personas, records, sim_matrix)

for persona_idx, record_idx, score in matches:
    print(f"Persona {persona_idx} -> Record {record_idx}: {score:.3f}")
```

---

### scripts.universal_ai_client

Multi-provider LLM client with unified interface.

#### Class: `UniversalAIClient`

##### Constructor

```python
class UniversalAIClient:
    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        max_retries: int = 3,
        timeout: int = 120
    ):
        """
        Initialize universal LLM client.

        Args:
            provider: Provider name (anthropic, openai, google, etc.)
            model: Model identifier
            api_key: API authentication key
            max_retries: Maximum retry attempts for failed requests
            timeout: Request timeout in seconds

        Supported Providers:
            - anthropic: Claude Haiku, Sonnet, Opus
            - openai: GPT-4, GPT-5
            - google: Gemini 2.5 Pro, Flash
            - aws_bedrock: AWS Bedrock models
            - azure_openai: Azure OpenAI Service
            - together: Together AI (Llama models)
            - groq: Groq inference
            - mistral: Mistral AI
            - xai: xAI (Grok)
            - cohere: Cohere models
            - perplexity: Perplexity AI
        """
```

##### Methods

```python
def send_message(
    self,
    messages: List[Dict[str, str]],
    max_tokens: int = 4096,
    temperature: float = 0.7,
    system_prompt: Optional[str] = None
) -> Dict[str, Any]:
    """
    Send message to LLM and get response.

    Args:
        messages: List of message dicts with 'role' and 'content'
        max_tokens: Maximum tokens in response
        temperature: Sampling temperature (0-1)
        system_prompt: Optional system instruction

    Returns:
        Response dictionary:
            - content: Response text
            - usage: Token usage stats
            - cost: Cost in USD
            - model: Model used
            - provider: Provider used

    Message Format:
        [
            {"role": "user", "content": "Hello"},
            {"role": "assistant", "content": "Hi there!"},
            {"role": "user", "content": "How are you?"}
        ]
    """

def get_cost(
    self,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Calculate cost for token usage.

    Args:
        input_tokens: Number of input tokens
        output_tokens: Number of output tokens

    Returns:
        Cost in USD

    Pricing (as of Nov 2025):
        Claude Sonnet 4.5: $3/$15 per 1M tokens
        Claude Haiku 4.5: $1/$5 per 1M tokens
        GPT-4: $2.50/$10 per 1M tokens
        Gemini 2.5 Flash: $0.15/$1.25 per 1M tokens
    """

def enable_batch_mode(self) -> bool:
    """
    Enable batch API for 50% cost savings.

    Returns:
        True if batch mode supported and enabled

    Note:
        Batch mode is asynchronous and may take minutes to hours.
        Best for non-real-time analysis.
    """
```

**Example:**
```python
from scripts.universal_ai_client import UniversalAIClient

# Initialize client
client = UniversalAIClient(
    provider="anthropic",
    model="claude-sonnet-4-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# Send message
messages = [
    {"role": "user", "content": "What is prenatal care?"}
]

response = client.send_message(
    messages=messages,
    max_tokens=1000,
    temperature=0.7
)

print(response['content'])
print(f"Cost: ${response['cost']:.4f}")
print(f"Tokens: {response['usage']['total_tokens']}")
```

---

## Pipeline Scripts

### 01b_generate_personas.py

#### Function: `generate_personas()`

```python
def generate_personas(
    count: int,
    seed: int = 42,
    provider: str = "anthropic",
    model: str = "claude-haiku-4-5",
    output_path: str = "data/personas/personas.json"
) -> List[Dict[str, Any]]:
    """
    Generate synthetic personas using LLM.

    Args:
        count: Number of personas to generate
        seed: Random seed for reproducibility
        provider: LLM provider
        model: LLM model
        output_path: Output JSON file path

    Returns:
        List of persona dictionaries

    Persona Structure:
        - id: Unique identifier
        - name: Full name
        - age: Age in years
        - semantic_tree: Hierarchical attributes

    Cost:
        ~$0.01 per persona (Claude Haiku)
    """
```

### 02_generate_health_records.py

#### Function: `generate_health_records()`

```python
def generate_health_records(
    count: int,
    seed: int = 12345,
    synthea_path: str = "synthea",
    output_dir: str = "synthea/output/fhir"
) -> List[str]:
    """
    Generate FHIR health records using Synthea.

    Args:
        count: Number of records to generate
        seed: Random seed for Synthea
        synthea_path: Path to Synthea installation
        output_dir: Output directory for FHIR files

    Returns:
        List of generated FHIR file paths

    Configuration:
        - Population: Female, age 12-60
        - Modules: pregnancy, contraceptives, sexual_activity
        - Format: FHIR R4 JSON

    Performance:
        ~30-60 seconds for 10 records
    """
```

### 03_match_personas_records_enhanced.py

#### Function: `match_personas_to_records()`

```python
def match_personas_to_records(
    personas_path: str = "data/personas/personas.json",
    fhir_dir: str = "synthea/output/fhir",
    output_path: str = "data/matched/matched_pairs.json"
) -> Dict[str, Any]:
    """
    Match personas to health records using semantic similarity.

    Args:
        personas_path: Path to personas JSON file
        fhir_dir: Directory containing FHIR bundle files
        output_path: Output path for matches

    Returns:
        Matching results:
            - matches: List of (persona_id, record_id, score)
            - statistics: Quality metrics
            - quality_distribution: Score distribution

    Process:
        1. Load personas and FHIR records
        2. Build semantic trees for all records
        3. Calculate similarity matrix
        4. Apply Hungarian algorithm
        5. Export matched pairs

    Performance:
        ~5 seconds for 100 pairs
    """
```

### 04_conduct_interviews.py

#### Function: `conduct_interview()`

```python
def conduct_interview(
    persona: Dict[str, Any],
    health_record: Dict[str, Any],
    protocol: Dict[str, Any],
    llm_client: UniversalAIClient,
    output_dir: str = "data/interviews"
) -> Dict[str, Any]:
    """
    Conduct AI-powered clinical interview.

    Args:
        persona: Persona dictionary with semantic tree
        health_record: Health record with FHIR data
        protocol: Interview protocol (PROTO_001 through PROTO_005)
        llm_client: Initialized LLM client
        output_dir: Directory for interview logs

    Returns:
        Interview results:
            - interview_id: Unique identifier
            - conversation: Full transcript
            - responses: Question-answer mapping
            - red_flags: Safety concerns identified
            - data_updates: Extracted data
            - metadata: Cost, tokens, duration

    Protocol Selection:
        - PROTO_001: First-time mothers (G1P0)
        - PROTO_002: Experienced mothers (G2+)
        - PROTO_003: High-risk pregnancy
        - PROTO_004: Low SES/access barriers
        - PROTO_005: Routine prenatal care

    Cost:
        ~$0.08 per interview (Claude Sonnet 4.5)
    """
```

#### Function: `select_protocol()`

```python
def select_protocol(persona: Dict[str, Any]) -> Dict[str, Any]:
    """
    Select appropriate interview protocol based on persona characteristics.

    Args:
        persona: Persona dictionary with semantic tree

    Returns:
        Selected protocol dictionary

    Decision Logic:
        1. Check for high-risk factors (age ≥35, chronic conditions)
           → PROTO_003
        2. Check for access barriers (uninsured, low access)
           → PROTO_004
        3. Check gravida (first pregnancy)
           → PROTO_001
        4. Check gravida (experienced)
           → PROTO_002
        5. Default
           → PROTO_005
    """
```

### analyze_interviews.py

#### Function: `analyze_interviews()`

```python
def analyze_interviews(
    interviews_dir: str = "data/interviews",
    output_path: str = "data/analysis/interview_summary.csv",
    anomaly_threshold: float = 0.7000
) -> pd.DataFrame:
    """
    Analyze interviews and generate structured export.

    Args:
        interviews_dir: Directory containing interview JSON files
        output_path: Output CSV file path
        anomaly_threshold: Threshold for anomaly detection

    Returns:
        DataFrame with 41 standardized columns

    Analysis:
        - Demographics extraction
        - Clinical data parsing
        - Engagement metrics (turns, words, topics)
        - Cost analysis (tokens, pricing)
        - Anomaly detection
        - Topic coverage (26 topics)

    Output Columns:
        Demographics: persona_id, age, education, income, etc.
        Interview Metrics: total_words, conversation_turns, etc.
        Clinical Data: health_conditions, medications, etc.
        Topic Coverage: pregnancy_planning, prenatal_care, etc.
        Cost: input_tokens, output_tokens, cost_usd
    """
```

---

## Utility Modules

### scripts.utils.common_loaders

Data loading utilities with validation.

```python
def load_personas(file_path: str) -> List[Dict[str, Any]]:
    """Load and validate personas from JSON file."""

def load_fhir_records(fhir_dir: str) -> List[Dict[str, Any]]:
    """Load all FHIR bundles from directory."""

def load_matched_pairs(file_path: str) -> Dict[str, Any]:
    """Load matched persona-record pairs."""

def load_interview_protocols(file_path: str) -> Dict[str, Any]:
    """Load interview protocols from JSON."""
```

### scripts.utils.validators

Data validation functions.

```python
def validate_persona(persona: Dict[str, Any]) -> bool:
    """Validate persona structure and required fields."""

def validate_fhir_bundle(bundle: Dict[str, Any]) -> bool:
    """Validate FHIR R4 bundle structure."""

def validate_semantic_tree(tree: Dict[str, Any]) -> bool:
    """Validate semantic tree completeness."""

def validate_interview(interview: Dict[str, Any]) -> bool:
    """Validate interview results structure."""
```

### scripts.utils.exceptions

Custom exception classes.

```python
class PersonaValidationError(Exception):
    """Raised when persona validation fails."""

class FHIRParsingError(Exception):
    """Raised when FHIR bundle parsing fails."""

class MatchingError(Exception):
    """Raised when matching process fails."""

class InterviewError(Exception):
    """Raised when interview execution fails."""
```

---

## Data Structures

### Persona Dictionary

```python
{
    "id": str,                    # Unique identifier
    "name": str,                  # Full name
    "age": int,                   # Age in years
    "semantic_tree": {
        "demographics": {
            "age": int,
            "gender": str,
            "location_type": str,
            "ethnicity": Optional[str],
            "language_primary": str
        },
        "socioeconomic": {
            "education_level": str,
            "income_bracket": str,
            "occupation_category": str,
            "employment_status": str,
            "insurance_status": str
        },
        "health_profile": {
            "health_consciousness": int,  # 1-5
            "healthcare_access": int,     # 1-5
            "pregnancy_readiness": int,   # 1-5
            "chronic_conditions": List[str]
        },
        "behavioral": {
            "physical_activity_level": int,  # 1-5
            "smoking_status": str,           # never/former/current
            "alcohol_consumption": str,
            "substance_use": bool
        },
        "psychosocial": {
            "mental_health_status": int,  # 1-5
            "stress_level": int,          # 1-5
            "social_support": int,        # 1-5
            "relationship_status": str
        },
        "pregnancy_intentions": {
            "gravida": int,
            "para": int,
            "preconception_care": bool,
            "pregnancy_planning": str
        }
    }
}
```

### Interview Results

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
    "responses": Dict[str, str],  # question_id -> response
    "red_flags": List[Dict],
    "data_updates": Dict[str, Any],
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

## Configuration

### Workflow Configuration (YAML)

```yaml
# config/workflow_config.yaml

personas:
  count: 100
  seed: 42
  llm_provider: anthropic
  llm_model: claude-haiku-4-5

health_records:
  count: 100
  seed: 12345
  synthea_path: ./synthea

matching:
  algorithm: hungarian
  min_similarity: 0.5
  weights:
    age: 0.40
    education: 0.20
    income: 0.15
    marital: 0.15
    occupation: 0.10

interviews:
  llm_provider: anthropic
  llm_model: claude-sonnet-4-5
  max_tokens: 4096
  temperature: 0.7
  batch_mode: false
  anomaly_threshold: 0.7000

output:
  personas_path: data/personas/personas.json
  matched_path: data/matched/matched_pairs.json
  interviews_dir: data/interviews
  analysis_path: data/analysis/interview_summary.csv
```

### Environment Variables

```bash
# .env file

# LLM API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AI...

# Optional
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AZURE_OPENAI_API_KEY=...
AZURE_OPENAI_ENDPOINT=...
```

---

## Error Handling

### Exception Hierarchy

```
Exception
├── PersonaValidationError
├── FHIRParsingError
├── MatchingError
├── InterviewError
└── ConfigurationError
```

### Retry Logic

All LLM API calls use exponential backoff retry:

```python
@retry(
    exceptions=(APIError, NetworkError),
    max_attempts=3,
    delay=1.0,
    backoff=2.0
)
def api_call_with_retry():
    """API call with automatic retry."""
    pass
```

### Logging

```python
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/workflow.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Usage
logger.info("Processing started")
logger.warning("Low similarity score: 0.42")
logger.error("FHIR parsing failed", exc_info=True)
```

---

## Best Practices

### 1. Type Hints

Always use type hints for function signatures:

```python
from typing import List, Dict, Any, Optional, Tuple

def process_data(
    input_data: List[Dict[str, Any]],
    threshold: float = 0.7
) -> Tuple[List[Dict], int]:
    """Process data with type hints."""
    pass
```

### 2. Error Handling

Use try-except blocks and custom exceptions:

```python
try:
    result = build_semantic_tree_from_fhir(bundle, patient_id, age)
except FHIRParsingError as e:
    logger.error(f"FHIR parsing failed: {e}")
    raise
```

### 3. Validation

Always validate inputs:

```python
def process_persona(persona: Dict) -> None:
    if not validate_persona(persona):
        raise PersonaValidationError(f"Invalid persona: {persona['id']}")
    # ... process
```

### 4. Documentation

Include comprehensive docstrings:

```python
def calculate_score(a: float, b: float) -> float:
    """
    Calculate weighted score.

    Args:
        a: First value
        b: Second value

    Returns:
        Weighted average score

    Raises:
        ValueError: If inputs negative

    Example:
        >>> calculate_score(0.8, 0.6)
        0.7
    """
    if a < 0 or b < 0:
        raise ValueError("Inputs must be non-negative")
    return (a * 0.6 + b * 0.4)
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.2.1 | 2025-11-16 | Added Phase 2 protocols, cost analysis APIs |
| 1.2.0 | 2025-11-15 | Phase 1 improvements, semantic matching |
| 1.1.0 | 2025-11-07 | Multi-provider LLM support |
| 1.0.0 | 2025-11-01 | Initial release |

---

**Document Prepared By:** Claude Code
**Date:** 2025-11-16
**Version:** 1.2.1
**Status:** Task 3.1.3 COMPLETE ✅
