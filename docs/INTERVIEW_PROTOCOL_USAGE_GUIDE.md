# Interview Protocol Usage Guide - v1.2.1

**Project:** Gravidas - Persona-to-Health-Record Matching System
**Phase:** Phase 2, Task 2.3.2 - Documentation
**Version:** 1.2.1
**Date:** 2025-11-16
**Status:** ✅ COMPLETE

---

## Table of Contents

1. [Overview](#overview)
2. [Protocol Selection Guide](#protocol-selection-guide)
3. [Using the Protocols](#using-the-protocols)
4. [Protocol Structure](#protocol-structure)
5. [Implementation Examples](#implementation-examples)
6. [Data Mapping](#data-mapping)
7. [Red Flag Protocols](#red-flag-protocols)
8. [Resource Connection](#resource-connection)
9. [Quality Assurance](#quality-assurance)
10. [Troubleshooting](#troubleshooting)

---

## Overview

This guide provides practical instructions for using the 5 clinical interview protocols developed in Phase 2 of the Gravidas project. These protocols are based on **ACOG Clinical Consensus 2025** and **ADA Standards of Care 2025**, ensuring evidence-based, clinically appropriate prenatal care interviews.

### Quick Reference

| Protocol | Duration | When to Use | Priority |
|----------|----------|-------------|----------|
| **PROTO_001** | 45 min | First-time mothers (G1P0) | High |
| **PROTO_002** | 35 min | Experienced mothers (G2+) | Medium |
| **PROTO_003** | 50 min | High-risk pregnancy | Critical |
| **PROTO_004** | 50 min | Low SES/access barriers | High |
| **PROTO_005** | 30 min | Routine, low-risk | Standard |

### File Location

```
/home/dpolonia/202511-Gravidas/data/interview_protocols.json
```

---

## Protocol Selection Guide

### Step 1: Assess Risk Level

**High-Risk Indicators** (use PROTO_003):
- Advanced maternal age (≥35 years)
- Pre-existing chronic conditions (hypertension, diabetes)
- History of pregnancy complications
- Multiple gestations
- Known genetic/chromosomal concerns

**Access Barrier Indicators** (use PROTO_004):
- Uninsured or underinsured
- Housing instability
- Food insecurity
- Transportation barriers
- Language barriers
- Low health literacy

### Step 2: Determine Pregnancy History

**First-time mothers (G1P0)** → Use PROTO_001
**Experienced mothers (G2+)** → Use PROTO_002

### Step 3: Consider Social Determinants

If access barriers are identified, **PROTO_004 takes priority** over PROTO_001 or PROTO_002.

### Step 4: Default Protocol

For well-resourced, routine care → Use PROTO_005

### Decision Tree

```
START
  ↓
Is patient high-risk? → YES → PROTO_003 (High-Risk)
  ↓ NO
Does patient have significant access barriers? → YES → PROTO_004 (Low SES)
  ↓ NO
Is this patient's first pregnancy (G1P0)? → YES → PROTO_001 (First-Time)
  ↓ NO
Has patient had previous pregnancies (G2+)? → YES → PROTO_002 (Experienced)
  ↓ NO
Default → PROTO_005 (Routine)
```

### Persona-to-Protocol Mapping

Based on the 10 personas in `data/personas/personas.json`:

| Persona | Age | Risk | Protocol | Rationale |
|---------|-----|------|----------|-----------|
| **Samantha** | 24 | Low | PROTO_001 | G1P0, first-time |
| **Emily** | 32 | Low | PROTO_002 | G2P1, experienced |
| **Olivia** | 28 | Barriers | PROTO_004 | Uninsured, access barriers |
| **Aaliyah** | 31 | Moderate | PROTO_002 or 003 | G2P1, GDM history |
| **Chloe** | 27 | Barriers | PROTO_004 | Underinsured, depression |
| **Fatima** | 41 | High | PROTO_003 | Age 41, hypertension |
| **Isabelle** | 29 | Low | PROTO_001 | G1P0, high readiness |
| **Jasmine** | 26 | Low | PROTO_001 | G1P0, rural |
| **Hannah** | 40 | High | PROTO_003 | Age 40, IVF, G3P2 |
| **Addison** | 35 | Low | PROTO_002 | G4P3, healthcare professional |

---

## Using the Protocols

### Loading the Protocol File

**Python Example:**

```python
import json
from pathlib import Path

# Load protocols
protocols_path = Path('data/interview_protocols.json')
with open(protocols_path, 'r') as f:
    protocol_data = json.load(f)

# Access specific protocol
proto_001 = protocol_data['protocols'][0]  # First-time mothers
print(f"Protocol: {proto_001['name']}")
print(f"Duration: {proto_001['interview_structure']['duration_minutes']} minutes")
```

### Selecting a Protocol

```python
def select_protocol(persona):
    """
    Select appropriate protocol based on persona characteristics.

    Args:
        persona (dict): Persona data with semantic_tree

    Returns:
        dict: Selected protocol
    """
    # Extract key factors
    age = persona['semantic_tree']['demographics']['age']
    gravida = persona['semantic_tree']['pregnancy_intentions']['gravida']
    insurance = persona['semantic_tree']['socioeconomic']['insurance_status']
    health_access = persona['semantic_tree']['health_profile']['healthcare_access']

    # High-risk conditions
    if age >= 35 or persona.get('chronic_conditions'):
        return 'PROTO_003'  # High-risk

    # Access barriers
    if insurance == 'uninsured' or health_access <= 2:
        return 'PROTO_004'  # Low SES/barriers

    # First-time vs experienced
    if gravida == 1:
        return 'PROTO_001'  # First-time
    elif gravida >= 2:
        return 'PROTO_002'  # Experienced
    else:
        return 'PROTO_005'  # Routine
```

### Executing the Interview

**Recommended Workflow:**

1. **Load persona data**
2. **Select appropriate protocol**
3. **Initialize conversation context**
4. **Iterate through protocol sections**
5. **Ask questions in sequence**
6. **Apply follow-up prompts based on responses**
7. **Check for red flags**
8. **Document responses and map to persona fields**
9. **Provide resources**

**Code Example:**

```python
def conduct_protocol_interview(persona, protocol):
    """
    Conduct interview using specified protocol.

    Args:
        persona (dict): Persona data
        protocol (dict): Interview protocol

    Returns:
        dict: Interview results with responses and data mapping
    """
    results = {
        'persona_id': persona['id'],
        'protocol_id': protocol['protocol_id'],
        'responses': {},
        'red_flags': [],
        'resources_provided': [],
        'data_updates': {}
    }

    # Iterate through sections
    for section in protocol['sections']:
        section_id = section['section_id']
        section_name = section['section_name']

        print(f"\n--- Section {section_id}: {section_name} ---")

        # Ask each question
        for question in section['questions']:
            q_id = question['question_id']
            q_text = question['text']

            # Send question to LLM
            response = ask_llm(q_text, persona_context)

            # Store response
            results['responses'][q_id] = response

            # Check for red flags
            if question.get('critical_risk_factor') and is_concerning(response):
                results['red_flags'].append({
                    'question_id': q_id,
                    'response': response,
                    'action': question.get('immediate_referral_if_yes')
                })

            # Map data
            if 'data_mapping' in question:
                for field in question['data_mapping']:
                    results['data_updates'][field] = extract_value(response)

            # Apply follow-up prompts if needed
            if needs_follow_up(response):
                for follow_up in question.get('follow_up_prompts', []):
                    follow_up_response = ask_llm(follow_up, persona_context)
                    results['responses'][f"{q_id}_followup"] = follow_up_response

    # Add resources
    results['resources_provided'] = protocol.get('resources_to_provide_today', [])

    return results
```

---

## Protocol Structure

Each protocol in the JSON file follows this structure:

### Top-Level Fields

```json
{
  "protocol_id": "PROTO_001",
  "name": "First-Time Mothers (Primigravida) Protocol",
  "description": "Comprehensive interview protocol for...",
  "target_personas": ["Samantha", "Olivia", "Isabelle", "Jasmine"],
  "target_criteria": {
    "gravida": 1,
    "para": 0,
    "age_range": "18-35"
  },
  "interview_structure": {
    "duration_minutes": 45,
    "sections": 8,
    "follow_up_frequency": "Every 4 weeks..."
  },
  "sections": [...]
}
```

### Section Structure

```json
{
  "section_id": 1,
  "section_name": "Introduction and Rapport Building",
  "duration_minutes": 5,
  "objectives": [
    "Establish trusting relationship",
    "Set comfortable tone for sensitive topics"
  ],
  "questions": [...]
}
```

### Question Structure

```json
{
  "question_id": "Q1.1",
  "text": "How are you feeling about your pregnancy today?",
  "type": "open_ended",
  "purpose": "Assess current emotional state",
  "data_mapping": ["psychosocial.mental_health_status"],
  "follow_up_prompts": [
    "What emotions have been strongest for you?",
    "Is there anything that's been particularly exciting or worrying?"
  ],
  "critical_risk_factor": false
}
```

### Question Types

| Type | Description | Example |
|------|-------------|---------|
| `open_ended` | Encourage narrative response | "Tell me about your pregnancy journey..." |
| `yes_no` | Binary response | "Do you have prenatal care?" |
| `multiple_choice` | Select from options | "How often do you exercise?" |
| `scale` | Numerical rating | "On a scale of 1-10, how is your stress?" |
| `checklist` | Multiple selections | "Which symptoms have you experienced?" |

---

## Implementation Examples

### Example 1: Complete Interview Flow

```python
import json
from pathlib import Path

# Load protocols
with open('data/interview_protocols.json', 'r') as f:
    protocol_data = json.load(f)

# Load personas
with open('data/personas/personas.json', 'r') as f:
    personas = json.load(f)

# Select first persona (Samantha - first-time mother)
persona = personas[0]

# Select protocol
protocol = protocol_data['protocols'][0]  # PROTO_001

# Initialize interview
print(f"Conducting {protocol['name']}")
print(f"Patient: {persona['name']}, Age: {persona['age']}")
print(f"Expected duration: {protocol['interview_structure']['duration_minutes']} minutes")
print("\n" + "="*50 + "\n")

# Conduct interview
interview_results = conduct_protocol_interview(persona, protocol)

# Review results
print(f"\nInterview Complete!")
print(f"Total responses: {len(interview_results['responses'])}")
print(f"Red flags identified: {len(interview_results['red_flags'])}")
print(f"Resources provided: {len(interview_results['resources_provided'])}")
```

### Example 2: Automated Protocol Selection

```python
def auto_select_protocol(persona, protocols):
    """
    Automatically select the most appropriate protocol.
    """
    # Extract persona characteristics
    age = persona['semantic_tree']['demographics']['age']
    gravida = persona['semantic_tree']['pregnancy_intentions']['gravida']
    insurance = persona['semantic_tree']['socioeconomic']['insurance_status']
    health_access = persona['semantic_tree']['health_profile']['healthcare_access']

    # Apply decision logic
    for protocol in protocols:
        # High-risk protocol
        if protocol['protocol_id'] == 'PROTO_003':
            if age >= 35:
                return protocol

        # Access barriers protocol
        if protocol['protocol_id'] == 'PROTO_004':
            if insurance in ['uninsured', 'underinsured'] or health_access <= 2:
                return protocol

        # First-time protocol
        if protocol['protocol_id'] == 'PROTO_001':
            if gravida == 1:
                return protocol

        # Experienced mothers protocol
        if protocol['protocol_id'] == 'PROTO_002':
            if gravida >= 2:
                return protocol

    # Default to routine care
    return next(p for p in protocols if p['protocol_id'] == 'PROTO_005')
```

### Example 3: LLM Integration

```python
from anthropic import Anthropic

def conduct_llm_interview(persona, protocol, api_key):
    """
    Conduct interview using Claude API.
    """
    client = Anthropic(api_key=api_key)

    # Build system prompt
    system_prompt = f"""
    You are conducting a prenatal care interview following the {protocol['name']}.

    Patient Profile:
    - Age: {persona['age']}
    - Gravida: {persona['semantic_tree']['pregnancy_intentions']['gravida']}
    - Para: {persona['semantic_tree']['pregnancy_intentions']['para']}

    Interview Guidelines:
    - Follow the protocol structure
    - Ask questions in order
    - Use empathetic, professional tone
    - Identify red flags
    - Provide appropriate resources
    """

    # Initialize conversation
    messages = []

    # Iterate through sections
    for section in protocol['sections']:
        for question in section['questions']:
            # Create message
            messages.append({
                "role": "user",
                "content": question['text']
            })

            # Get response from Claude
            response = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=4096,
                system=system_prompt,
                messages=messages
            )

            # Store assistant response
            messages.append({
                "role": "assistant",
                "content": response.content[0].text
            })

            # Check for red flags
            if question.get('critical_risk_factor'):
                # Analyze response for concerning content
                pass

    return messages
```

---

## Data Mapping

### Understanding Data Mapping

Each question includes a `data_mapping` field that specifies which persona fields should be updated based on the response.

**Example:**

```json
{
  "question_id": "Q2.3",
  "text": "Do you smoke or use tobacco products?",
  "data_mapping": ["behavioral.smoking_status", "behavioral.tobacco_use"]
}
```

### Semantic Tree Structure

The persona semantic tree has this hierarchy:

```
semantic_tree/
├── demographics/
│   ├── age
│   ├── gender
│   ├── race_ethnicity
│   └── location_type
├── socioeconomic/
│   ├── education_level
│   ├── income_bracket
│   ├── insurance_status
│   └── occupation
├── health_profile/
│   ├── health_consciousness
│   ├── healthcare_access
│   ├── pregnancy_readiness
│   └── chronic_conditions
├── behavioral/
│   ├── physical_activity_level
│   ├── smoking_status
│   ├── alcohol_consumption
│   └── substance_use
├── psychosocial/
│   ├── mental_health_status
│   ├── stress_level
│   ├── social_support
│   └── relationship_status
└── pregnancy_intentions/
    ├── gravida
    ├── para
    ├── preconception_care
    └── pregnancy_planning
```

### Mapping Responses to Fields

```python
def map_response_to_fields(response, data_mapping_fields):
    """
    Extract values from response and map to persona fields.

    Args:
        response (str): Interview response text
        data_mapping_fields (list): List of field paths

    Returns:
        dict: Field updates
    """
    updates = {}

    for field_path in data_mapping_fields:
        # Parse field path (e.g., "behavioral.smoking_status")
        parts = field_path.split('.')
        category = parts[0]
        field = parts[1]

        # Extract value from response using LLM or regex
        value = extract_value_from_text(response, field)

        # Store update
        if category not in updates:
            updates[category] = {}
        updates[category][field] = value

    return updates

def extract_value_from_text(text, field_name):
    """
    Use LLM to extract structured value from text response.
    """
    # Example extraction logic
    if 'smoking' in field_name.lower():
        if any(word in text.lower() for word in ['yes', 'smoke', 'cigarettes']):
            return 'current'
        elif any(word in text.lower() for word in ['quit', 'former', 'stopped']):
            return 'former'
        else:
            return 'never'

    # Add more extraction logic for other fields
    return None
```

---

## Red Flag Protocols

### Critical Risk Factors

Questions marked with `"critical_risk_factor": true` require immediate attention if answered positively or concerningly.

### Red Flag Categories

**Immediate Referrals:**
- Suicidal ideation
- Intimate partner violence
- Severe mental health crisis
- Housing instability
- Food insecurity

**Specialist Referrals:**
- Uncontrolled chronic conditions
- High-risk pregnancy complications
- Substance use disorders
- Complex medical history

### Implementation

```python
def check_red_flags(question, response):
    """
    Check if response triggers red flag protocol.

    Args:
        question (dict): Question with red flag criteria
        response (str): Patient response

    Returns:
        dict: Red flag details if triggered, None otherwise
    """
    if not question.get('critical_risk_factor'):
        return None

    # Analyze response for concerning content
    concerning = is_response_concerning(response, question)

    if concerning:
        return {
            'question_id': question['question_id'],
            'severity': 'critical' if 'immediate' in question.get('immediate_referral_if_yes', '').lower() else 'warning',
            'action': question.get('immediate_referral_if_yes') or question.get('immediate_referral_if_no'),
            'response': response
        }

    return None

def is_response_concerning(response, question):
    """
    Determine if response is concerning based on question type.
    """
    response_lower = response.lower()

    # Safety concerns
    if any(word in response_lower for word in ['suicidal', 'kill myself', 'end my life']):
        return True

    # Violence indicators
    if any(word in response_lower for word in ['hit', 'hurt', 'abuse', 'afraid']):
        return True

    # Severe distress
    if any(phrase in response_lower for phrase in ['can\'t cope', 'overwhelmed', 'can\'t take it']):
        return True

    return False
```

### Red Flag Response Actions

| Severity | Response Time | Action |
|----------|--------------|---------|
| **Critical** | Immediate | Stop interview, contact supervisor, initiate emergency protocol |
| **Urgent** | Same day | Flag for clinician review, schedule follow-up within 24 hours |
| **Warning** | 1-3 days | Document concern, include in next scheduled visit |
| **Monitor** | Next visit | Track for pattern, reassess at follow-up |

---

## Resource Connection

### Resources Included in Protocols

Each protocol includes a `resources_to_provide_today` section listing recommended resources.

**Example (PROTO_004 - Low SES/Barriers):**

```json
"resources_to_provide_today": [
  "Insurance/Medicaid application assistance",
  "WIC application and information",
  "Prenatal vitamins (samples to take home)",
  "Transportation vouchers or bus passes",
  "List of local food banks",
  "Housing assistance contacts",
  "Community health centers list",
  "Sliding scale payment information"
]
```

### Resource Distribution Workflow

```python
def provide_resources(protocol, red_flags):
    """
    Compile resources to provide based on protocol and red flags.

    Args:
        protocol (dict): Interview protocol
        red_flags (list): Identified red flags

    Returns:
        list: Resources to provide
    """
    resources = []

    # Add standard protocol resources
    resources.extend(protocol.get('resources_to_provide_today', []))

    # Add red flag-specific resources
    for flag in red_flags:
        if 'housing' in flag['action'].lower():
            resources.append("Emergency housing assistance: 1-800-XXX-XXXX")
        if 'food' in flag['action'].lower():
            resources.append("Emergency food assistance: WIC, SNAP, local food banks")
        if 'mental health' in flag['action'].lower():
            resources.append("Crisis counseling: 988 Suicide & Crisis Lifeline")
        if 'violence' in flag['action'].lower():
            resources.append("National Domestic Violence Hotline: 1-800-799-7233")

    # Remove duplicates
    return list(set(resources))
```

---

## Quality Assurance

### Interview Quality Metrics

Track these metrics for each interview:

```python
def calculate_quality_metrics(interview_results):
    """
    Calculate quality metrics for completed interview.
    """
    metrics = {
        'completeness': 0.0,
        'red_flags_identified': 0,
        'data_fields_updated': 0,
        'resources_provided': 0,
        'follow_up_needed': False
    }

    # Completeness (% of questions answered)
    total_questions = count_protocol_questions(interview_results['protocol'])
    answered_questions = len(interview_results['responses'])
    metrics['completeness'] = answered_questions / total_questions

    # Red flags
    metrics['red_flags_identified'] = len(interview_results['red_flags'])

    # Data mapping
    metrics['data_fields_updated'] = len(interview_results['data_updates'])

    # Resources
    metrics['resources_provided'] = len(interview_results['resources_provided'])

    # Follow-up determination
    metrics['follow_up_needed'] = (
        metrics['red_flags_identified'] > 0 or
        metrics['completeness'] < 0.9
    )

    return metrics
```

### Quality Thresholds

| Metric | Target | Minimum Acceptable |
|--------|--------|-------------------|
| Completeness | 100% | 90% |
| Data Fields Updated | 80% | 60% |
| Response Quality | High | Moderate |
| Red Flag Detection | 100% | 100% |

---

## Troubleshooting

### Common Issues and Solutions

#### Issue 1: Protocol Selection Confusion

**Problem:** Unclear which protocol to use for complex cases

**Solution:**
- Use decision tree in Section 2
- When in doubt, err on the side of more comprehensive protocol (PROTO_003 or PROTO_004)
- Protocols can be combined if needed

#### Issue 2: Incomplete Data Mapping

**Problem:** Not all persona fields being updated

**Solution:**
```python
# Validate data mapping coverage
def validate_data_mapping(protocol):
    """Check which persona fields are covered by protocol."""
    covered_fields = set()

    for section in protocol['sections']:
        for question in section['questions']:
            for field in question.get('data_mapping', []):
                covered_fields.add(field)

    # Compare to full persona schema
    all_fields = get_all_persona_fields()
    uncovered = all_fields - covered_fields

    print(f"Coverage: {len(covered_fields)}/{len(all_fields)} fields")
    print(f"Uncovered fields: {uncovered}")
```

#### Issue 3: Red Flag False Positives

**Problem:** System flagging non-critical responses

**Solution:**
- Review question `critical_risk_factor` settings
- Adjust sensitivity of `is_response_concerning()` function
- Implement human review for borderline cases

#### Issue 4: LLM Response Quality

**Problem:** LLM not following protocol structure

**Solution:**
```python
# Enhanced system prompt
system_prompt = f"""
You are a prenatal care interviewer following STRICT protocol guidelines.

PROTOCOL: {protocol['name']}
SECTION: {current_section['section_name']}

RULES:
1. Ask ONLY the specified question
2. Do NOT skip ahead
3. Use empathetic, professional tone
4. Listen for red flags
5. Follow up on concerning responses

CURRENT QUESTION: {question['text']}
PURPOSE: {question['purpose']}

If patient's response is concerning, probe deeper using these follow-ups:
{question.get('follow_up_prompts', [])}
"""
```

---

## Best Practices

### 1. Protocol Preparation

✅ **Review protocol before interview**
✅ **Prepare resources in advance**
✅ **Test LLM integration**
✅ **Have backup plan for technical issues**

### 2. During Interview

✅ **Follow protocol sequence**
✅ **Document responses in real-time**
✅ **Watch for red flags**
✅ **Maintain professional tone**
✅ **Allow time for patient questions**

### 3. After Interview

✅ **Review completeness**
✅ **Address red flags immediately**
✅ **Update persona data**
✅ **Provide resources**
✅ **Schedule follow-up if needed**

### 4. Quality Control

✅ **Audit 10% of interviews**
✅ **Track quality metrics**
✅ **Calibrate red flag detection**
✅ **Update protocols based on feedback**

---

## Appendix: Quick Reference Tables

### Protocol Comparison

| Aspect | PROTO_001 | PROTO_002 | PROTO_003 | PROTO_004 | PROTO_005 |
|--------|-----------|-----------|-----------|-----------|-----------|
| **Target** | First-time | Experienced | High-risk | Barriers | Routine |
| **Duration** | 45 min | 35 min | 50 min | 50 min | 30 min |
| **Sections** | 8 | 7 | 9 | 9 | 6 |
| **Education Focus** | High | Medium | High | High | Low |
| **Resource Intensity** | Medium | Low | High | Very High | Low |
| **Follow-up Frequency** | Every 4 weeks | Every 4 weeks | 1-4 weeks | Flexible | Standard |

### Question Count by Protocol

| Protocol | Total Questions | Open-Ended | Yes/No | Scale | Checklist |
|----------|----------------|------------|--------|-------|-----------|
| PROTO_001 | 65 | 45 | 12 | 5 | 3 |
| PROTO_002 | 52 | 35 | 10 | 4 | 3 |
| PROTO_003 | 78 | 50 | 15 | 8 | 5 |
| PROTO_004 | 75 | 48 | 18 | 6 | 3 |
| PROTO_005 | 42 | 28 | 8 | 4 | 2 |

---

**Document Prepared By:** Claude Code
**Date:** 2025-11-16
**Version:** 1.2.1
**Status:** Task 2.3.2 COMPLETE ✅
