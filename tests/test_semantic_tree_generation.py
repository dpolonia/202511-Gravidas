"""
Unit tests for semantic tree generation from FHIR data.

Phase 1, Task 1.4.3 - v1.2.0 Implementation

Tests cover:
- FHIR bundle parsing
- Semantic tree generation
- Vitals extraction
- Edge case handling
- Null safety
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.fhir_semantic_extractor import (
    build_semantic_tree_from_fhir,
    extract_vitals_from_observations,
    extract_pregnancy_profile,
    calculate_comorbidity_index
)
from scripts.utils.semantic_tree import HealthRecordSemanticTree, PregnancyProfile


class TestFHIRParsing:
    """Test FHIR bundle parsing."""

    def test_parse_valid_fhir_bundle(self, sample_fhir_bundle):
        """Test parsing a valid FHIR bundle."""
        patient_id = 'patient-123'
        age = 29

        # Should not raise any exceptions
        semantic_tree = build_semantic_tree_from_fhir(sample_fhir_bundle, patient_id, age)

        # Verify tree was created
        assert isinstance(semantic_tree, HealthRecordSemanticTree)
        assert semantic_tree.patient_id == patient_id
        assert semantic_tree.age == age

    def test_parse_minimal_fhir_bundle(self, minimal_fhir_bundle):
        """Test parsing a minimal FHIR bundle with only patient."""
        patient_id = 'patient-minimal'
        age = 32

        semantic_tree = build_semantic_tree_from_fhir(minimal_fhir_bundle, patient_id, age)

        assert isinstance(semantic_tree, HealthRecordSemanticTree)
        assert semantic_tree.patient_id == patient_id
        # Should have empty or minimal data structures
        assert len(semantic_tree.conditions) >= 0

    def test_parse_edge_case_bundle(self, edge_case_fhir_bundle):
        """Test parsing FHIR bundle with None values and edge cases."""
        patient_id = 'patient-edge'
        age = 34

        # Should handle None values gracefully
        semantic_tree = build_semantic_tree_from_fhir(edge_case_fhir_bundle, patient_id, age)

        assert isinstance(semantic_tree, HealthRecordSemanticTree)
        # Should not crash despite None values

    def test_empty_bundle(self):
        """Test handling of empty FHIR bundle."""
        empty_bundle = {
            'resourceType': 'Bundle',
            'type': 'collection',
            'entry': []
        }

        patient_id = 'patient-empty'
        age = 25

        # Should handle gracefully
        semantic_tree = build_semantic_tree_from_fhir(empty_bundle, patient_id, age)
        assert isinstance(semantic_tree, HealthRecordSemanticTree)


class TestVitalsExtraction:
    """Test vital signs extraction from observations."""

    def test_extract_basic_vitals(self, sample_observations):
        """Test extracting basic vital signs."""
        vitals = extract_vitals_from_observations(sample_observations)

        # Check expected vitals are extracted
        assert vitals['blood_pressure_systolic'] == 120
        assert vitals['blood_pressure_diastolic'] == 80
        assert vitals['maternal_weight_kg'] == 65.5
        assert vitals['maternal_height_cm'] == 165

    def test_extract_from_empty_observations(self):
        """Test vitals extraction with no observations."""
        vitals = extract_vitals_from_observations([])

        # All vitals should be None
        assert vitals['gestational_age_weeks'] is None
        assert vitals['blood_pressure_systolic'] is None
        assert vitals['blood_pressure_diastolic'] is None
        assert vitals['fetal_heart_rate'] is None
        assert vitals['maternal_weight_kg'] is None

    def test_extract_partial_vitals(self):
        """Test vitals extraction with only some observations."""
        partial_obs = [
            {
                'code': '8480-6',
                'value': 125,
                'effective_date': '2024-03-15'
            }
        ]

        vitals = extract_vitals_from_observations(partial_obs)

        # Only BP should be extracted
        assert vitals['blood_pressure_systolic'] == 125
        assert vitals['blood_pressure_diastolic'] is None

    def test_weight_gain_calculation(self):
        """Test weight gain calculation from multiple weight measurements."""
        weight_obs = [
            {
                'code': '29463-7',
                'value': 60.0,
                'effective_date': '2024-01-01'
            },
            {
                'code': '29463-7',
                'value': 65.0,
                'effective_date': '2024-03-01'
            },
            {
                'code': '29463-7',
                'value': 70.0,
                'effective_date': '2024-06-01'
            }
        ]

        vitals = extract_vitals_from_observations(weight_obs)

        # Should calculate weight gain from first to last
        assert vitals['maternal_weight_kg'] == 70.0  # Latest weight
        assert vitals['weight_gain_kg'] == 10.0  # 70 - 60

    def test_null_value_handling(self):
        """Test handling of null observation values."""
        null_obs = [
            {
                'code': '8480-6',
                'value': None,  # Null value
                'effective_date': '2024-03-15'
            },
            {
                'code': '8462-4',
                'value': 'invalid',  # Invalid type
                'effective_date': '2024-03-15'
            }
        ]

        vitals = extract_vitals_from_observations(null_obs)

        # Should handle gracefully, no values extracted
        assert vitals['blood_pressure_systolic'] is None
        assert vitals['blood_pressure_diastolic'] is None


class TestPregnancyProfile:
    """Test pregnancy profile extraction."""

    def test_extract_pregnancy_profile_basic(self):
        """Test basic pregnancy profile extraction."""
        conditions = [
            {'code': '72892002', 'display': 'Normal pregnancy'}
        ]
        encounters = [
            {'type': 'prenatal visit'}
        ]
        observations = [
            {'code': '8480-6', 'value': 120, 'effective_date': '2024-03-15'}
        ]
        age = 28
        comorbidity_index = 0.2

        profile = extract_pregnancy_profile(
            conditions, encounters, observations, age, comorbidity_index
        )

        assert isinstance(profile, PregnancyProfile)
        assert profile.has_pregnancy_codes is True
        assert profile.risk_level >= 1
        assert profile.blood_pressure_systolic == 120

    def test_extract_profile_no_pregnancy(self):
        """Test profile extraction without pregnancy codes."""
        conditions = [
            {'code': '12345', 'display': 'Some other condition'}
        ]
        encounters = []
        observations = []
        age = 25
        comorbidity_index = 0.1

        profile = extract_pregnancy_profile(
            conditions, encounters, observations, age, comorbidity_index
        )

        assert profile.has_pregnancy_codes is False
        assert profile.pregnancy_stage is None

    def test_high_risk_pregnancy_profile(self):
        """Test profile with high-risk indicators."""
        conditions = [
            {'code': '47200007', 'display': 'High risk pregnancy'},
            {'code': '73211009', 'display': 'Diabetes'}
        ]
        encounters = []
        observations = []
        age = 42  # Advanced maternal age
        comorbidity_index = 0.8

        profile = extract_pregnancy_profile(
            conditions, encounters, observations, age, comorbidity_index
        )

        # Should have elevated risk level
        assert profile.risk_level >= 3


class TestComorbidityIndex:
    """Test comorbidity index calculation."""

    def test_no_conditions(self):
        """Test comorbidity index with no conditions."""
        index = calculate_comorbidity_index([])
        assert index == 0.0

    def test_single_chronic_condition(self):
        """Test with a single chronic condition."""
        conditions = [
            {'code': '73211009', 'display': 'Diabetes'}
        ]
        index = calculate_comorbidity_index(conditions)
        assert index > 0.0

    def test_multiple_conditions(self):
        """Test with multiple conditions."""
        conditions = [
            {'code': '73211009', 'display': 'Diabetes'},
            {'code': '38341003', 'display': 'Hypertension'},
            {'code': '195662009', 'display': 'Acute condition'}
        ]
        index = calculate_comorbidity_index(conditions)
        assert 0.0 < index <= 1.0


class TestSemanticTreeStructure:
    """Test semantic tree data structure."""

    def test_semantic_tree_has_required_fields(self, sample_fhir_bundle):
        """Test that semantic tree has all required fields."""
        patient_id = 'patient-123'
        age = 29

        tree = build_semantic_tree_from_fhir(sample_fhir_bundle, patient_id, age)

        # Check required fields exist
        assert hasattr(tree, 'patient_id')
        assert hasattr(tree, 'age')
        assert hasattr(tree, 'conditions')
        assert hasattr(tree, 'medications')
        assert hasattr(tree, 'healthcare_utilization')
        assert hasattr(tree, 'pregnancy_profile')
        assert hasattr(tree, 'comorbidity_index')

    def test_pregnancy_profile_structure(self, sample_fhir_bundle):
        """Test pregnancy profile has all required fields."""
        patient_id = 'patient-123'
        age = 29

        tree = build_semantic_tree_from_fhir(sample_fhir_bundle, patient_id, age)
        profile = tree.pregnancy_profile

        # Check pregnancy profile fields
        assert hasattr(profile, 'has_pregnancy_codes')
        assert hasattr(profile, 'pregnancy_stage')
        assert hasattr(profile, 'risk_level')
        assert hasattr(profile, 'gestational_age_weeks')
        assert hasattr(profile, 'blood_pressure_systolic')
        assert hasattr(profile, 'blood_pressure_diastolic')
        assert hasattr(profile, 'maternal_weight_kg')


class TestNullSafety:
    """Test null safety and error handling."""

    def test_missing_resource_fields(self):
        """Test handling of missing resource fields."""
        bundle = {
            'resourceType': 'Bundle',
            'entry': [
                {
                    'resource': {
                        'resourceType': 'Condition'
                        # Missing 'code' field
                    }
                }
            ]
        }

        # Should not crash
        tree = build_semantic_tree_from_fhir(bundle, 'patient-test', 30)
        assert isinstance(tree, HealthRecordSemanticTree)

    def test_none_values_in_coding(self):
        """Test handling of None values in coding arrays."""
        bundle = {
            'resourceType': 'Bundle',
            'entry': [
                {
                    'resource': {
                        'resourceType': 'Condition',
                        'code': {
                            'coding': [
                                {
                                    'code': None,
                                    'display': None
                                }
                            ]
                        }
                    }
                }
            ]
        }

        # Should handle None values gracefully
        tree = build_semantic_tree_from_fhir(bundle, 'patient-test', 30)
        assert isinstance(tree, HealthRecordSemanticTree)


class TestIntegrationWithRealData:
    """Integration tests with real FHIR files."""

    def test_real_fhir_file(self, real_fhir_file_path):
        """Test semantic tree generation with real FHIR file."""
        if real_fhir_file_path is None:
            pytest.skip("No real FHIR files available")

        import json

        with open(real_fhir_file_path, 'r') as f:
            fhir_data = json.load(f)

        patient_id = real_fhir_file_path.stem
        age = 30

        # Should successfully build semantic tree from real data
        tree = build_semantic_tree_from_fhir(fhir_data, patient_id, age)

        assert isinstance(tree, HealthRecordSemanticTree)
        assert tree.patient_id == patient_id

    def test_all_fhir_files_parseable(self):
        """Test that all FHIR files can be parsed without errors."""
        import json

        fhir_dir = Path('synthea/output/fhir')
        if not fhir_dir.exists():
            pytest.skip("FHIR directory not found")

        fhir_files = list(fhir_dir.glob('*.json'))[:10]  # Test first 10
        fhir_files = [f for f in fhir_files if 'hospitalInformation' not in f.name and 'practitionerInformation' not in f.name]

        success_count = 0
        for fhir_file in fhir_files:
            try:
                with open(fhir_file, 'r') as f:
                    fhir_data = json.load(f)

                tree = build_semantic_tree_from_fhir(fhir_data, fhir_file.stem, 30)
                assert isinstance(tree, HealthRecordSemanticTree)
                success_count += 1
            except Exception as e:
                pytest.fail(f"Failed to parse {fhir_file.name}: {e}")

        assert success_count == len(fhir_files)
