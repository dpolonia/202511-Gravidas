# Semantic Tree Structure and Implementation Guide

## Overview

The Semantic Tree system provides a hierarchical, multi-dimensional representation of person attributes (personas and health records) that enables sophisticated, healthcare-aware matching for the Gravidas pipeline.

**Key Innovation:** Rather than matching on simple demographics alone, semantic trees capture the rich complexity of health, behavioral, and psychosocial factors, resulting in clinically meaningful persona-record pairs.

---

## Architecture

### Two-Tree System

The implementation consists of two complementary semantic tree types:

1. **PersonaSemanticTree** - Synthetic personas with rich healthcare attributes
2. **HealthRecordSemanticTree** - Clinical profiles extracted from FHIR medical records

### Hierarchical Structure

#### PersonaSemanticTree (5 Branches)

```
PersonaSemanticTree
├── Demographics (25% matching weight)
│   ├── age
│   ├── gender
│   ├── location_type (urban/suburban/rural)
│   ├── ethnicity
│   └── language_primary
│
├── Socioeconomic (15% matching weight)
│   ├── education_level
│   ├── income_bracket
│   ├── occupation_category
│   ├── employment_status
│   └── insurance_status
│
├── HealthProfile (35% matching weight) ⭐ PRIMARY MATCHING FACTOR
│   ├── health_consciousness (1-5 scale)
│   ├── healthcare_access (1-5 scale)
│   ├── pregnancy_readiness (1-5 scale)
│   ├── reported_health_conditions (list)
│   ├── medication_history (list)
│   ├── allergies (list)
│   ├── surgery_history (list)
│   ├── reproductive_history
│   └── family_medical_history (list)
│
├── Behavioral (15% matching weight)
│   ├── physical_activity_level (1-5 scale)
│   ├── nutrition_awareness (1-5 scale)
│   ├── smoking_status (never/former/current)
│   ├── alcohol_consumption (never/occasional/moderate/heavy)
│   ├── substance_use (none/minimal/moderate/significant)
│   └── sleep_quality (1-5 scale)
│
└── Psychosocial (10% matching weight)
    ├── mental_health_status (1-5 scale)
    ├── stress_level (1-5 scale)
    ├── social_support (1-5 scale)
    ├── marital_status
    ├── relationship_stability (1-5 scale)
    ├── financial_stress (1-5 scale)
    └── family_planning_attitudes
```

#### HealthRecordSemanticTree (FHIR-Derived)

```
HealthRecordSemanticTree
├── Patient Demographics
│   ├── patient_id
│   └── age
│
├── Clinical Conditions
│   ├── conditions[] (SNOMED-mapped)
│   ├── condition_categories (by type)
│   ├── chronic_disease_count
│   ├── acute_condition_count
│   └── comorbidity_index (0.0-1.0)
│
├── Medication Profile
│   ├── medication_categories
│   ├── pregnancy_safety (safe/caution/contraindicated)
│   ├── chronic_vs_acute
│   └── medication_count
│
├── Healthcare Utilization
│   ├── visit_frequency
│   ├── primary_care_engagement (1-5)
│   ├── specialist_utilization (1-5)
│   ├── preventive_care_visits
│   ├── emergency_visits
│   ├── inpatient_stays
│   └── estimated_healthcare_access (1-5)
│
├── Pregnancy Profile
│   ├── has_pregnancy_codes
│   ├── pregnancy_stage
│   ├── complication_indicators
│   ├── obstetric_history_indicators
│   ├── prenatal_care_indicators
│   └── risk_level (1-5)
│
└── Health Status
    └── overall_health_status (excellent/good/fair/poor/complex)
```

---

## Component Details

### Scale-Based Attributes (1-5)

Most semantic attributes use a standardized 1-5 scale:

| Scale | Meaning | Example |
|-------|---------|---------|
| 1 | Very Low / Very Poor | Sedentary (activity), High stress, Poor health |
| 2 | Low / Poor | Limited exercise, High stress levels |
| 3 | Moderate / Fair | Occasional exercise, Moderate stress |
| 4 | High / Good | Regular exercise, Low stress |
| 5 | Very High / Excellent | Very active, Very low stress |

### Health Consciousness (1-5)

Measures engagement with personal health:

- **1 (Very Low)**: No exercise, poor diet, no healthcare provider
- **2 (Low)**: Sedentary, limited attention to health
- **3 (Moderate)**: Occasional exercise, some health awareness
- **4 (High)**: Regular exercise, healthy lifestyle choices
- **5 (Very High)**: Fitness focused, nutritionist consultation, preventive care

### Healthcare Access (1-5)

Measures availability and use of medical services:

- **1 (Very Limited)**: Uninsured, cannot afford care, no regular provider
- **2 (Limited)**: Underinsured, occasional visits
- **3 (Moderate)**: Some insurance, community clinic access
- **4 (Good)**: Primary care provider, decent coverage
- **5 (Excellent)**: Private physician, specialist access, preventive visits

### Pregnancy Readiness (1-5)

Assesses pregnancy planning and preparation:

- **1 (Not Ready)**: Does not want children
- **2 (Uncertain)**: Hasn't decided about pregnancy
- **3 (Neutral)**: Open to pregnancy if timing is right
- **4 (Planning)**: Plans to have children soon
- **5 (Actively Trying)**: Actively trying to conceive

### Comorbidity Index (0.0-1.0)

Quantifies disease burden:

- **0.0-0.2**: Minimal disease burden, excellent health
- **0.2-0.4**: Mild disease burden
- **0.4-0.6**: Moderate disease burden
- **0.6-0.8**: Significant disease burden
- **0.8-1.0**: Severe disease burden, multiple comorbidities

---

## Semantic Matching Process

### Step 1: Load Data with Trees

```python
# Personas with semantic trees
personas = load_personas('data/personas/personas.json')
# Each persona contains:
# {
#   "id": 123,
#   "name": "Maria",
#   "age": 32,
#   "semantic_tree": {
#     "demographics": {...},
#     "socioeconomic": {...},
#     "health_profile": {...},
#     "behavioral": {...},
#     "psychosocial": {...}
#   }
# }

# Records with semantic trees
records = load_health_records('data/health_records/health_records.json')
```

### Step 2: Component Scoring

The matching algorithm calculates 5 component scores:

1. **Demographics Similarity** (25%)
   - Age difference with tolerance
   - Location type compatibility

2. **Socioeconomic Alignment** (15%)
   - Healthcare access expectations vs. actual utilization
   - Employment status compatibility

3. **Health Profile Alignment** (35%) ⭐ PRIMARY
   - Health consciousness ↔ medical engagement
   - Pregnancy readiness ↔ pregnancy risk level
   - Condition expectations ↔ actual diagnoses

4. **Behavioral Alignment** (15%)
   - Physical activity ↔ health status
   - Smoking status ↔ disease burden
   - Nutrition awareness ↔ health indicators

5. **Psychosocial Alignment** (10%)
   - Mental health status ↔ risk profile
   - Social support ↔ healthcare engagement
   - Family planning attitudes ↔ pregnancy presence

### Step 3: Blended Scoring

Final match score combines:
- **Demographic Score**: 40% (baseline demographics)
- **Semantic Score**: 60% (rich healthcare attributes)

```
Blended_Score = (0.40 × Demographic) + (0.60 × Semantic)
```

### Step 4: Optimal Assignment

Hungarian Algorithm selects N-to-M best matches from large persona pools.

### Step 5: Alignment Reporting

For each match, generate explainable report:

```json
{
  "persona_id": 123,
  "record_id": "patient_456",
  "total_semantic_score": 0.82,
  "match_quality": "good",
  "component_scores": {
    "demographics": 0.88,
    "socioeconomic": 0.79,
    "health_profile": 0.85,
    "behavioral": 0.76,
    "psychosocial": 0.81
  },
  "key_insights": [
    "Excellent pregnancy readiness and risk level alignment",
    "Strong health consciousness and medical engagement alignment",
    "Lifestyle factors (smoking, activity) well-aligned"
  ],
  "strengths": ["health_profile", "demographics"],
  "weaknesses": ["behavioral"]
}
```

---

## Usage Examples

### Example 1: Generate Personas with Semantic Trees

```bash
python scripts/01b_generate_personas.py --count 100 --output data/personas
```

Output: `data/personas/personas.json` with semantic trees for each persona

### Example 2: Extract Health Records with Semantic Trees

```bash
python scripts/02_generate_health_records.py --count 100
```

Output: `data/health_records/health_records.json` with semantic trees extracted from FHIR

### Example 3: Run Semantic Matching

```bash
# Default: 60% semantic + 40% demographic
python scripts/03_match_personas_records_enhanced.py

# Semantic-only matching
python scripts/03_match_personas_records_enhanced.py --semantic-only

# Custom semantic weight
python scripts/03_match_personas_records_enhanced.py --semantic-weight 0.7
```

### Example 4: Validate Semantic Trees

```bash
python scripts/test_semantic_implementation.py \
  --personas data/personas/personas.json \
  --records data/health_records/health_records.json \
  --output data/validation
```

Output: Validation reports with quality metrics

---

## Key Features

### 1. Healthcare-Aware Matching

Semantic trees capture:
- Health consciousness vs. healthcare engagement
- Pregnancy readiness vs. clinical risk
- Behavioral consistency with health status
- Psychosocial factors affecting outcomes

### 2. Explainability

Each match includes:
- Component-level scores
- Strength/weakness analysis
- Clinical insights
- Clear rationale for match decision

### 3. Flexible Integration

Use semantic trees at any weight:
- **0% semantic** = Pure demographic matching (backward compatible)
- **60% semantic** = Balanced approach (default)
- **100% semantic** = Healthcare-focused matching

### 4. Data Quality Validation

Test framework verifies:
- Semantic tree completeness
- Value ranges and consistency
- Missing or invalid data
- Clinical data quality
- Demographic diversity

---

## Best Practices

### 1. Data Generation

- Always include healthcare dimensions in AI prompts
- Ensure diverse distribution of health attributes
- Validate persona descriptions for consistency
- Check for semantic tree completeness before matching

### 2. Health Record Processing

- Use Synthea for realistic FHIR generation
- Map SNOMED codes carefully
- Assess pregnancy safety of medications
- Classify risk levels consistently

### 3. Matching Strategy

- Start with balanced approach (60% semantic)
- Validate match quality reports
- Adjust weights based on research requirements
- Review weak matches for clinical relevance

### 4. Quality Assurance

- Run test suite before production matching
- Generate validation reports
- Check demographic diversity
- Analyze comorbidity distributions
- Review match rationales

---

## Troubleshooting

### Issue: Missing Semantic Trees in Personas

**Cause:** Generation failed or incomplete extraction

**Solution:**
```bash
# Check if personas.json has semantic_tree field
python -c "import json; d=json.load(open('data/personas/personas.json')); print('Tree found' if d[0].get('semantic_tree') else 'Tree missing')"

# Regenerate if missing
python scripts/01b_generate_personas.py --count 10 --output data/personas_test
```

### Issue: Low Semantic Scores

**Cause:** Mismatch between persona and record characteristics

**Solution:**
- Review demographic diversity
- Check health attribute distributions
- Adjust semantic weight
- Regenerate with better FHIR data

### Issue: Validation Failures

**Cause:** Incomplete or invalid semantic tree data

**Solution:**
```bash
# Run detailed validation
python scripts/test_semantic_implementation.py

# Check validation_report.json for specific issues
python -c "import json; r=json.load(open('data/validation/validation_report.json')); print(json.dumps(r['detailed_results']['personas']['issues_found'][:5], indent=2))"
```

---

## Performance Considerations

### Complexity

- **Matrix Computation**: O(P × R × C) where P=personas, R=records, C=components
- **Matching Algorithm**: O((P×R)³) for Hungarian Algorithm
- **Typical Runtime**:
  - 100 personas × 100 records: ~1-2 seconds
  - 1000 personas × 1000 records: ~30-60 seconds
  - 10000 personas × 10000 records: ~5-10 minutes

### Optimization

- Use semantic weight 1.0 for faster semantic-only matching
- Implement caching for repeated component calculations
- Consider batch processing for large datasets

---

## Extensions and Customization

### Adding New Semantic Dimensions

1. Define new node type in `semantic_tree.py`
2. Implement extraction in `01b_generate_personas.py` or `fhir_semantic_extractor.py`
3. Add component scoring function in `semantic_matcher.py`
4. Update weights in matching configuration

### Custom SNOMED Code Mappings

Edit `fhir_semantic_extractor.py`:
```python
SNOMED_FULL_MAP[code] = {
    'display': 'Display name',
    'category': 'category_type',
    'severity': 3,  # 1-5 scale
    'pregnancy_relevance': 4  # 1-5 scale
}
```

### Adjusting Component Weights

In configuration or command line:
```python
weights = {
    'age': 0.25,  # Increase age importance
    'education': 0.10,
    'income': 0.10,
    'marital_status': 0.10,
    'occupation': 0.10,
    'health_consciousness': 0.15,  # Add custom factors
    'pregnancy_readiness': 0.10
}
```

---

## References

### Related Files

- `scripts/utils/semantic_tree.py` - Core data structures
- `scripts/utils/semantic_matcher.py` - Matching algorithms
- `scripts/utils/fhir_semantic_extractor.py` - FHIR extraction
- `scripts/01b_generate_personas.py` - Persona generation with trees
- `scripts/02_generate_health_records.py` - Health record extraction
- `scripts/03_match_personas_records_enhanced.py` - Matching integration
- `scripts/test_semantic_implementation.py` - Testing framework

### Key References

- SNOMED CT Clinical Terminology: https://www.snomed.org/
- HL7 FHIR: https://www.hl7.org/fhir/
- Pregnancy Risk Assessment: Clinical guidelines
- Comorbidity Scoring: Charlson Index, Elixhauser

---

## Support

For issues or questions:
1. Check validation reports in `data/validation/`
2. Review test logs in `logs/test_semantic_implementation.log`
3. Examine sample matches in `data/matched/` output
4. Consult this guide's Troubleshooting section

---

**Last Updated:** 2025-11-12
**Version:** 1.0
**Status:** Production Ready
