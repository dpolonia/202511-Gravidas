"""
Shared pytest fixtures and configuration for all tests.
"""

import pytest
import json
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Any


@pytest.fixture
def sample_config() -> Dict[str, Any]:
    """Sample configuration for testing."""
    return {
        'active_provider': 'anthropic',
        'active_model': 'claude-3-haiku-20240307',
        'api_keys': {
            'anthropic': {
                'api_key': 'test-key',
                'default_model': 'claude-3-haiku-20240307',
                'max_tokens': 4096,
                'temperature': 0.7
            }
        },
        'retry': {
            'max_retries': 3,
            'initial_delay': 1.0,
            'max_delay': 60.0,
            'exponential_base': 2.0,
            'strategy': 'exponential'
        }
    }


@pytest.fixture
def sample_persona() -> Dict[str, Any]:
    """Sample persona for testing."""
    return {
        'id': 'persona_001',
        'age': 28,
        'education': 'college',
        'occupation': 'teacher',
        'marital_status': 'married',
        'income_level': 'middle',
        'location': 'urban',
        'description': 'A 28-year-old married teacher living in an urban area.',
        'pregnancy_week': 20,
        'previous_pregnancies': 0,
        'health_concerns': ['gestational diabetes risk']
    }


@pytest.fixture
def sample_health_record() -> Dict[str, Any]:
    """Sample health record for testing."""
    return {
        'id': 'record_001',
        'patient_age': 28,
        'gestational_age_weeks': 20,
        'gravida': 1,
        'para': 0,
        'conditions': ['gestational_diabetes'],
        'medications': ['prenatal_vitamins'],
        'allergies': [],
        'blood_type': 'O+',
        'bmi': 24.5,
        'blood_pressure': '120/80'
    }


@pytest.fixture
def sample_personas() -> List[Dict[str, Any]]:
    """Multiple sample personas for testing."""
    return [
        {
            'id': 'persona_001',
            'age': 28,
            'education': 'college',
            'pregnancy_week': 20
        },
        {
            'id': 'persona_002',
            'age': 32,
            'education': 'graduate',
            'pregnancy_week': 15
        },
        {
            'id': 'persona_003',
            'age': 25,
            'education': 'high_school',
            'pregnancy_week': 30
        }
    ]


@pytest.fixture
def sample_health_records() -> List[Dict[str, Any]]:
    """Multiple sample health records for testing."""
    return [
        {
            'id': 'record_001',
            'patient_age': 28,
            'gestational_age_weeks': 20
        },
        {
            'id': 'record_002',
            'patient_age': 31,
            'gestational_age_weeks': 16
        },
        {
            'id': 'record_003',
            'patient_age': 26,
            'gestational_age_weeks': 29
        }
    ]


@pytest.fixture
def temp_config_file(sample_config, tmp_path) -> Path:
    """Create a temporary config file for testing."""
    import yaml

    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(sample_config, f)

    return config_file


@pytest.fixture
def temp_personas_file(sample_personas, tmp_path) -> Path:
    """Create a temporary personas JSON file for testing."""
    personas_file = tmp_path / "personas.json"
    with open(personas_file, 'w') as f:
        json.dump(sample_personas, f, indent=2)

    return personas_file


@pytest.fixture
def temp_records_file(sample_health_records, tmp_path) -> Path:
    """Create a temporary health records JSON file for testing."""
    records_file = tmp_path / "health_records.json"
    with open(records_file, 'w') as f:
        json.dump(sample_health_records, f, indent=2)

    return records_file


@pytest.fixture
def sample_matched_pair(sample_persona, sample_health_record) -> Dict[str, Any]:
    """Sample matched persona-record pair for testing."""
    return {
        'persona': sample_persona,
        'health_record': sample_health_record,
        'compatibility_score': 0.92,
        'match_details': {
            'age_score': 1.0,
            'pregnancy_stage_score': 1.0,
            'condition_alignment': 0.85
        }
    }


@pytest.fixture
def empty_file(tmp_path) -> Path:
    """Create an empty file for testing edge cases."""
    empty = tmp_path / "empty.json"
    empty.touch()
    return empty


@pytest.fixture
def invalid_json_file(tmp_path) -> Path:
    """Create a file with invalid JSON for testing error handling."""
    invalid = tmp_path / "invalid.json"
    invalid.write_text("{ this is not valid json }")
    return invalid


@pytest.fixture
def mock_api_response() -> Dict[str, Any]:
    """Mock API response for testing interview logic."""
    return {
        'id': 'msg_123',
        'content': [
            {
                'type': 'text',
                'text': 'Thank you for sharing. How have you been feeling lately?'
            }
        ],
        'model': 'claude-3-haiku-20240307',
        'role': 'assistant'
    }


# ========== FHIR and Semantic Tree Fixtures (v1.2.0) ==========

@pytest.fixture
def sample_fhir_bundle() -> Dict[str, Any]:
    """Sample FHIR bundle for testing semantic tree generation."""
    return {
        'resourceType': 'Bundle',
        'type': 'collection',
        'entry': [
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'patient-123',
                    'birthDate': '1995-01-15',
                    'gender': 'female'
                }
            },
            {
                'resource': {
                    'resourceType': 'Condition',
                    'code': {
                        'coding': [
                            {
                                'system': 'http://snomed.info/sct',
                                'code': '72892002',
                                'display': 'Normal pregnancy'
                            }
                        ]
                    },
                    'onsetDateTime': '2024-01-01'
                }
            },
            {
                'resource': {
                    'resourceType': 'MedicationRequest',
                    'medicationCodeableConcept': {
                        'coding': [
                            {
                                'system': 'http://www.nlm.nih.gov/research/umls/rxnorm',
                                'code': '4077',
                                'display': 'Prenatal vitamins'
                            }
                        ]
                    }
                }
            },
            {
                'resource': {
                    'resourceType': 'Encounter',
                    'type': [
                        {
                            'text': 'Prenatal visit'
                        }
                    ],
                    'period': {
                        'start': '2024-03-15'
                    }
                }
            },
            {
                'resource': {
                    'resourceType': 'Observation',
                    'code': {
                        'coding': [
                            {
                                'system': 'http://loinc.org',
                                'code': '8480-6',
                                'display': 'Systolic blood pressure'
                            }
                        ]
                    },
                    'valueQuantity': {
                        'value': 120,
                        'unit': 'mmHg'
                    },
                    'effectiveDateTime': '2024-03-15'
                }
            },
            {
                'resource': {
                    'resourceType': 'Observation',
                    'code': {
                        'coding': [
                            {
                                'system': 'http://loinc.org',
                                'code': '29463-7',
                                'display': 'Body Weight'
                            }
                        ]
                    },
                    'valueQuantity': {
                        'value': 65.5,
                        'unit': 'kg'
                    },
                    'effectiveDateTime': '2024-03-15'
                }
            }
        ]
    }


@pytest.fixture
def sample_persona_with_semantic_tree() -> Dict[str, Any]:
    """Sample persona with semantic tree structure."""
    return {
        'id': 'persona_test_001',
        'name': 'Test Emily',
        'age': 28,
        'education': 'college',
        'occupation': 'teacher',
        'semantic_tree': {
            'age': 28,
            'education_level': 'college',
            'occupation_category': 'education',
            'desired_conditions': ['pregnancy', 'gestational_diabetes'],
            'desired_medications': ['prenatal_vitamins'],
            'pregnancy_stage': 'second_trimester',
            'risk_factors': ['gestational_diabetes_risk'],
            'lifestyle_factors': ['active', 'healthy_diet']
        }
    }


@pytest.fixture
def sample_observations() -> List[Dict[str, Any]]:
    """Sample observation data for testing vitals extraction."""
    return [
        {
            'code': '8480-6',
            'display': 'Systolic blood pressure',
            'value': 120,
            'unit': 'mmHg',
            'effective_date': '2024-03-15',
            'parent_code': None
        },
        {
            'code': '8462-4',
            'display': 'Diastolic blood pressure',
            'value': 80,
            'unit': 'mmHg',
            'effective_date': '2024-03-15',
            'parent_code': None
        },
        {
            'code': '29463-7',
            'display': 'Body Weight',
            'value': 65.5,
            'unit': 'kg',
            'effective_date': '2024-03-15',
            'parent_code': None
        },
        {
            'code': '8302-2',
            'display': 'Body Height',
            'value': 165,
            'unit': 'cm',
            'effective_date': '2024-01-01',
            'parent_code': None
        }
    ]


@pytest.fixture
def edge_case_fhir_bundle() -> Dict[str, Any]:
    """FHIR bundle with edge cases for testing robustness."""
    return {
        'resourceType': 'Bundle',
        'type': 'collection',
        'entry': [
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'patient-edge',
                    'birthDate': '1990-06-15'
                }
            },
            {
                'resource': {
                    'resourceType': 'Condition',
                    'code': {
                        'coding': [
                            {
                                'system': 'http://snomed.info/sct',
                                'code': '123456',
                                'display': None  # Edge case: None display
                            }
                        ]
                    }
                }
            },
            {
                'resource': {
                    'resourceType': 'Observation',
                    'code': {
                        'coding': [
                            {
                                'system': 'http://loinc.org',
                                'code': '8480-6',
                                'display': 'Systolic blood pressure'
                            }
                        ]
                    },
                    'valueQuantity': None,  # Edge case: missing value
                    'effectiveDateTime': '2024-03-15'
                }
            }
        ]
    }


@pytest.fixture
def minimal_fhir_bundle() -> Dict[str, Any]:
    """Minimal valid FHIR bundle for testing."""
    return {
        'resourceType': 'Bundle',
        'type': 'collection',
        'entry': [
            {
                'resource': {
                    'resourceType': 'Patient',
                    'id': 'patient-minimal',
                    'birthDate': '1992-03-20'
                }
            }
        ]
    }


@pytest.fixture
def real_fhir_file_path() -> Path:
    """Path to a real FHIR file for integration testing."""
    fhir_dir = Path('synthea/output/fhir')
    if fhir_dir.exists():
        fhir_files = list(fhir_dir.glob('*.json'))
        # Filter out metadata files
        fhir_files = [f for f in fhir_files if 'hospitalInformation' not in f.name and 'practitionerInformation' not in f.name]
        if fhir_files:
            return fhir_files[0]
    return None


@pytest.fixture
def real_personas_file_path() -> Path:
    """Path to the real personas file for integration testing."""
    personas_file = Path('data/personas/personas.json')
    if personas_file.exists():
        return personas_file
    return None
