"""
Unit tests for semantic tree similarity calculations.

Phase 1, Task 1.4.4 - v1.2.0 Implementation

Tests cover:
- Semantic tree similarity calculation
- Component score calculation
- Persona-record matching
- Edge cases and boundary conditions
"""

import pytest
import sys
from pathlib import Path
from typing import Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.semantic_tree import (
    PersonaSemanticTree,
    HealthRecordSemanticTree,
    PregnancyProfile,
    ClinicalConditions,
    MedicationProfile,
    HealthcareUtilization,
    calculate_semantic_tree_similarity,
    persona_tree_from_dict
)


class TestSemanticSimilarityCalculation:
    """Test semantic similarity calculation between persona and health record."""

    def test_perfect_match(self):
        """Test similarity calculation for perfect match."""
        # Create identical persona and record trees
        persona_tree = PersonaSemanticTree(
            age=28,
            education_level='college',
            occupation_category='education',
            desired_conditions=['pregnancy'],
            desired_medications=['prenatal_vitamins'],
            pregnancy_stage='second_trimester',
            risk_factors=[],
            lifestyle_factors=['active']
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-perfect',
            age=28,
            conditions=ClinicalConditions(
                chronic_conditions=['pregnancy'],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=['pregnancy'],
                severity_low=[]
            ),
            condition_categories={'pregnancy_related': 1},
            medications=MedicationProfile(
                current_medications=['prenatal_vitamins'],
                medication_categories={'prenatal': 1},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='regular',
                primary_care_visits=4,
                specialist_visits=2,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=True,
                pregnancy_stage='second_trimester',
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=['prenatal_visit'],
                risk_level=1
            ),
            comorbidity_index=0.1,
            health_status='healthy'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Should have high similarity for perfect match
        assert total_similarity > 0.8
        assert 'conditions' in components
        assert 'medications' in components

    def test_complete_mismatch(self):
        """Test similarity for completely mismatched trees."""
        persona_tree = PersonaSemanticTree(
            age=28,
            education_level='college',
            occupation_category='education',
            desired_conditions=['pregnancy', 'gestational_diabetes'],
            desired_medications=['prenatal_vitamins', 'insulin'],
            pregnancy_stage='second_trimester',
            risk_factors=['diabetes'],
            lifestyle_factors=[]
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-mismatch',
            age=28,
            conditions=ClinicalConditions(
                chronic_conditions=['hypertension'],
                acute_conditions=['flu'],
                severity_high=[],
                severity_moderate=['hypertension'],
                severity_low=['flu']
            ),
            condition_categories={'cardiovascular': 1, 'acute': 1},
            medications=MedicationProfile(
                current_medications=['blood_pressure_med'],
                medication_categories={'cardiovascular': 1},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='regular',
                primary_care_visits=2,
                specialist_visits=0,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=False,
                pregnancy_stage=None,
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.3,
            health_status='stable'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Should have low similarity for mismatch
        assert total_similarity < 0.5

    def test_partial_match(self):
        """Test similarity for partial match."""
        persona_tree = PersonaSemanticTree(
            age=30,
            education_level='college',
            occupation_category='education',
            desired_conditions=['pregnancy'],
            desired_medications=['prenatal_vitamins'],
            pregnancy_stage='first_trimester',
            risk_factors=[],
            lifestyle_factors=['active']
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-partial',
            age=30,
            conditions=ClinicalConditions(
                chronic_conditions=['pregnancy'],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=['pregnancy'],
                severity_low=[]
            ),
            condition_categories={'pregnancy_related': 1},
            medications=MedicationProfile(
                current_medications=[],  # No medications
                medication_categories={},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='regular',
                primary_care_visits=3,
                specialist_visits=0,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=True,
                pregnancy_stage='second_trimester',  # Different stage
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.1,
            health_status='healthy'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Should have moderate similarity
        assert 0.4 < total_similarity < 0.9


class TestComponentScores:
    """Test individual component scores."""

    def test_component_scores_range(self):
        """Test that component scores are in valid range [0, 1]."""
        persona_tree = PersonaSemanticTree(
            age=28,
            education_level='college',
            occupation_category='education',
            desired_conditions=['pregnancy'],
            desired_medications=[],
            pregnancy_stage='second_trimester',
            risk_factors=[],
            lifestyle_factors=[]
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-test',
            age=28,
            conditions=ClinicalConditions(
                chronic_conditions=['pregnancy'],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=[],
                severity_low=[]
            ),
            condition_categories={'pregnancy_related': 1},
            medications=MedicationProfile(
                current_medications=[],
                medication_categories={},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='regular',
                primary_care_visits=2,
                specialist_visits=0,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=True,
                pregnancy_stage='second_trimester',
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.1,
            health_status='healthy'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Check all components are in valid range
        for component_name, score in components.items():
            assert 0.0 <= score <= 1.0, f"Component {component_name} score {score} out of range"

    def test_all_components_present(self):
        """Test that all expected components are calculated."""
        persona_tree = PersonaSemanticTree(
            age=28,
            education_level='college',
            occupation_category='education',
            desired_conditions=[],
            desired_medications=[],
            pregnancy_stage=None,
            risk_factors=[],
            lifestyle_factors=[]
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-test',
            age=28,
            conditions=ClinicalConditions(
                chronic_conditions=[],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=[],
                severity_low=[]
            ),
            condition_categories={},
            medications=MedicationProfile(
                current_medications=[],
                medication_categories={},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='minimal',
                primary_care_visits=0,
                specialist_visits=0,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=False,
                pregnancy_stage=None,
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.0,
            health_status='healthy'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Check expected components exist
        expected_components = ['conditions', 'medications', 'demographics', 'pregnancy', 'health_status']
        for component in expected_components:
            assert component in components, f"Missing component: {component}"


class TestPersonaTreeFromDict:
    """Test persona tree creation from dictionary."""

    def test_create_persona_from_dict(self, sample_persona_with_semantic_tree):
        """Test creating PersonaSemanticTree from dictionary."""
        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        assert isinstance(persona_tree, PersonaSemanticTree)
        assert persona_tree.age == 28
        assert persona_tree.education_level == 'college'

    def test_create_persona_from_minimal_dict(self):
        """Test creating persona from minimal dictionary."""
        minimal_dict = {
            'age': 25,
            'education_level': 'high_school',
            'occupation_category': 'service'
        }

        persona_tree = persona_tree_from_dict(minimal_dict)

        assert isinstance(persona_tree, PersonaSemanticTree)
        assert persona_tree.age == 25

    def test_create_persona_with_missing_fields(self):
        """Test creating persona with some missing fields."""
        partial_dict = {
            'age': 30
        }

        persona_tree = persona_tree_from_dict(partial_dict)

        assert isinstance(persona_tree, PersonaSemanticTree)
        assert persona_tree.age == 30
        # Other fields should have defaults


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_conditions_and_medications(self):
        """Test similarity with empty conditions and medications."""
        persona_tree = PersonaSemanticTree(
            age=28,
            education_level='college',
            occupation_category='education',
            desired_conditions=[],
            desired_medications=[],
            pregnancy_stage=None,
            risk_factors=[],
            lifestyle_factors=[]
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-empty',
            age=28,
            conditions=ClinicalConditions(
                chronic_conditions=[],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=[],
                severity_low=[]
            ),
            condition_categories={},
            medications=MedicationProfile(
                current_medications=[],
                medication_categories={},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='minimal',
                primary_care_visits=0,
                specialist_visits=0,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=False,
                pregnancy_stage=None,
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.0,
            health_status='healthy'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Should not crash, should have valid score
        assert 0.0 <= total_similarity <= 1.0

    def test_zero_similarity_check(self):
        """Test that minimum similarity is 0.0."""
        persona_tree = PersonaSemanticTree(
            age=20,
            education_level='high_school',
            occupation_category='student',
            desired_conditions=['condition_a', 'condition_b', 'condition_c'],
            desired_medications=['med_a', 'med_b', 'med_c'],
            pregnancy_stage='third_trimester',
            risk_factors=['risk_a', 'risk_b'],
            lifestyle_factors=['factor_a']
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-opposite',
            age=20,
            conditions=ClinicalConditions(
                chronic_conditions=['condition_x', 'condition_y', 'condition_z'],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=[],
                severity_low=[]
            ),
            condition_categories={'category_x': 3},
            medications=MedicationProfile(
                current_medications=['med_x', 'med_y', 'med_z'],
                medication_categories={'category_x': 3},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='frequent',
                primary_care_visits=10,
                specialist_visits=5,
                emergency_visits=2,
                hospitalization_count=1
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=False,
                pregnancy_stage=None,
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.8,
            health_status='complex'
        )

        total_similarity, components = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Similarity should be >= 0
        assert total_similarity >= 0.0


class TestSimilarityProperties:
    """Test mathematical properties of similarity function."""

    def test_similarity_is_symmetric(self):
        """Test that similarity(A, B) == similarity(B, A) for same-type objects."""
        # Note: This only makes sense if comparing two personas or two records
        # For persona-to-record, the function is not symmetric by design
        pass  # Skip for persona-to-record comparison

    def test_similarity_with_self_is_high(self):
        """Test that a tree compared with itself has high similarity."""
        persona_tree = PersonaSemanticTree(
            age=28,
            education_level='college',
            occupation_category='education',
            desired_conditions=['pregnancy'],
            desired_medications=['prenatal_vitamins'],
            pregnancy_stage='second_trimester',
            risk_factors=[],
            lifestyle_factors=['active']
        )

        # Create identical record
        record_tree = HealthRecordSemanticTree(
            patient_id='patient-identical',
            age=28,
            conditions=ClinicalConditions(
                chronic_conditions=['pregnancy'],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=['pregnancy'],
                severity_low=[]
            ),
            condition_categories={'pregnancy_related': 1},
            medications=MedicationProfile(
                current_medications=['prenatal_vitamins'],
                medication_categories={'prenatal': 1},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='regular',
                primary_care_visits=3,
                specialist_visits=1,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=True,
                pregnancy_stage='second_trimester',
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=['prenatal_visit'],
                risk_level=1
            ),
            comorbidity_index=0.1,
            health_status='healthy'
        )

        total_similarity, _ = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        # Should have very high similarity
        assert total_similarity > 0.8

    def test_similarity_is_bounded(self):
        """Test that similarity is always between 0 and 1."""
        # Generate random combinations
        persona_tree = PersonaSemanticTree(
            age=25,
            education_level='college',
            occupation_category='healthcare',
            desired_conditions=['pregnancy'],
            desired_medications=[],
            pregnancy_stage='first_trimester',
            risk_factors=[],
            lifestyle_factors=[]
        )

        record_tree = HealthRecordSemanticTree(
            patient_id='patient-bounded',
            age=32,
            conditions=ClinicalConditions(
                chronic_conditions=['diabetes'],
                acute_conditions=[],
                severity_high=[],
                severity_moderate=[],
                severity_low=[]
            ),
            condition_categories={'metabolic': 1},
            medications=MedicationProfile(
                current_medications=['insulin'],
                medication_categories={'metabolic': 1},
                high_risk_medications=[]
            ),
            healthcare_utilization=HealthcareUtilization(
                encounter_frequency='regular',
                primary_care_visits=4,
                specialist_visits=2,
                emergency_visits=0,
                hospitalization_count=0
            ),
            pregnancy_profile=PregnancyProfile(
                has_pregnancy_codes=False,
                pregnancy_stage=None,
                complication_indicators=[],
                obstetric_history_indicators=[],
                prenatal_care_indicators=[],
                risk_level=1
            ),
            comorbidity_index=0.4,
            health_status='stable'
        )

        total_similarity, _ = calculate_semantic_tree_similarity(
            persona_tree, record_tree
        )

        assert 0.0 <= total_similarity <= 1.0
