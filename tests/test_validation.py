"""
Tests for data validation functions.

Tests validation of personas, health records, matched pairs, and interviews.
"""

import pytest
import json
from pathlib import Path
from scripts.utils.validate_data import (
    ValidationResult,
    validate_personas,
    validate_health_records,
    validate_matched_pairs
)


@pytest.mark.validation
@pytest.mark.unit
class TestValidationResult:
    """Tests for ValidationResult class."""

    def test_create_validation_result(self):
        """Test creating a validation result."""
        result = ValidationResult("TestStage")

        assert result.stage == "TestStage"
        assert result.passed is True
        assert len(result.errors) == 0
        assert len(result.warnings) == 0
        assert len(result.info) == 0

    def test_add_error(self):
        """Test adding errors."""
        result = ValidationResult("TestStage")
        result.add_error("Test error")

        assert len(result.errors) == 1
        assert result.errors[0] == "Test error"
        assert result.passed is False

    def test_add_warning(self):
        """Test adding warnings."""
        result = ValidationResult("TestStage")
        result.add_warning("Test warning")

        assert len(result.warnings) == 1
        assert result.warnings[0] == "Test warning"
        assert result.passed is True  # Warnings don't fail validation

    def test_add_info(self):
        """Test adding info messages."""
        result = ValidationResult("TestStage")
        result.add_info("Test info")

        assert len(result.info) == 1
        assert result.info[0] == "Test info"
        assert result.passed is True

    def test_multiple_messages(self):
        """Test adding multiple types of messages."""
        result = ValidationResult("TestStage")
        result.add_info("Info 1")
        result.add_info("Info 2")
        result.add_warning("Warning 1")
        result.add_error("Error 1")

        assert len(result.info) == 2
        assert len(result.warnings) == 1
        assert len(result.errors) == 1
        assert result.passed is False


@pytest.mark.validation
@pytest.mark.unit
class TestValidatePersonas:
    """Tests for validate_personas function."""

    def test_validate_valid_personas(self, tmp_path):
        """Test validation of valid personas."""
        personas = [
            {
                'id': 'P001',
                'age': 28,
                'gender': 'female',
                'description': 'Test persona',
                'education': 'bachelors'
            },
            {
                'id': 'P002',
                'age': 32,
                'gender': 'female',
                'description': 'Another test persona',
                'education': 'masters'
            }
        ]

        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        assert result.passed is True
        assert len(result.errors) == 0

    def test_validate_nonexistent_file(self):
        """Test validation of non-existent file."""
        result = validate_personas("/nonexistent/file.json")

        assert result.passed is False
        assert len(result.errors) > 0
        assert "not found" in result.errors[0].lower()

    def test_validate_invalid_json(self, tmp_path):
        """Test validation of invalid JSON."""
        bad_file = tmp_path / "bad.json"
        bad_file.write_text("{ invalid json ")

        result = validate_personas(str(bad_file))

        assert result.passed is False
        assert len(result.errors) > 0

    def test_validate_missing_required_fields(self, tmp_path):
        """Test validation when required fields are missing."""
        personas = [
            {
                'id': 'P001',
                # Missing 'age', 'gender', 'description'
                'education': 'bachelors'
            }
        ]

        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        # Should have warnings for missing fields
        assert len(result.warnings) > 0

    def test_validate_age_out_of_range(self, tmp_path):
        """Test validation of ages outside expected range."""
        personas = [
            {
                'id': 'P001',
                'age': 5,  # Too young
                'gender': 'female',
                'description': 'Test'
            },
            {
                'id': 'P002',
                'age': 70,  # Too old
                'gender': 'female',
                'description': 'Test'
            }
        ]

        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        # Should have warnings for age range
        assert len(result.warnings) >= 2

    def test_validate_wrong_gender(self, tmp_path):
        """Test validation of non-female gender."""
        personas = [
            {
                'id': 'P001',
                'age': 28,
                'gender': 'male',  # Wrong gender for pregnancy study
                'description': 'Test'
            }
        ]

        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        # Should have warning for gender
        assert any('gender' in w.lower() for w in result.warnings)

    def test_validate_empty_personas_list(self, tmp_path):
        """Test validation of empty personas list."""
        personas = []

        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        # Should pass but show 0 personas loaded
        assert result.passed is True
        assert any('0 personas' in i.lower() for i in result.info)


@pytest.mark.validation
@pytest.mark.unit
class TestValidateHealthRecords:
    """Tests for validate_health_records function."""

    def test_validate_valid_records(self, tmp_path):
        """Test validation of valid health records."""
        records = [
            {
                'id': 'R001',
                'age': 28,
                'conditions': ['pregnancy'],
                'medications': []
            },
            {
                'id': 'R002',
                'age': 32,
                'conditions': ['pregnancy', 'gestational_diabetes'],
                'medications': ['insulin']
            }
        ]

        records_file = tmp_path / "records.json"
        with open(records_file, 'w') as f:
            json.dump(records, f)

        result = validate_health_records(str(records_file))

        # Should pass validation
        assert len(result.errors) == 0

    def test_validate_nonexistent_records_file(self):
        """Test validation of non-existent records file."""
        result = validate_health_records("/nonexistent/records.json")

        assert result.passed is False
        assert len(result.errors) > 0

    def test_validate_empty_records(self, tmp_path):
        """Test validation of empty records list."""
        records = []

        records_file = tmp_path / "records.json"
        with open(records_file, 'w') as f:
            json.dump(records, f)

        result = validate_health_records(str(records_file))

        # Should pass but show 0 records
        assert result.passed is True


@pytest.mark.validation
@pytest.mark.unit
class TestValidateMatchedPairs:
    """Tests for validate_matched_pairs function."""

    def test_validate_valid_matched_pairs(self, tmp_path, sample_matched_pair):
        """Test validation of valid matched pairs."""
        matched_pairs = [sample_matched_pair]

        matched_file = tmp_path / "matched.json"
        with open(matched_file, 'w') as f:
            json.dump(matched_pairs, f)

        result = validate_matched_pairs(str(matched_file))

        # Should pass validation
        assert len(result.errors) == 0

    def test_validate_nonexistent_matched_file(self):
        """Test validation of non-existent matched file."""
        result = validate_matched_pairs("/nonexistent/matched.json")

        assert result.passed is False
        assert len(result.errors) > 0

    def test_validate_missing_compatibility_score(self, tmp_path):
        """Test validation when compatibility score is missing."""
        matched_pairs = [
            {
                'persona': {'id': 'P001', 'age': 28},
                'health_record': {'id': 'R001', 'age': 28}
                # Missing 'compatibility_score'
            }
        ]

        matched_file = tmp_path / "matched.json"
        with open(matched_file, 'w') as f:
            json.dump(matched_pairs, f)

        result = validate_matched_pairs(str(matched_file))

        # Should have warnings or errors for missing score
        assert len(result.warnings) > 0 or len(result.errors) > 0

    def test_validate_invalid_compatibility_score(self, tmp_path):
        """Test validation with out-of-range compatibility score."""
        matched_pairs = [
            {
                'persona': {'id': 'P001', 'age': 28},
                'health_record': {'id': 'R001', 'age': 28},
                'compatibility_score': 1.5  # Invalid: > 1.0
            }
        ]

        matched_file = tmp_path / "matched.json"
        with open(matched_file, 'w') as f:
            json.dump(matched_pairs, f)

        result = validate_matched_pairs(str(matched_file))

        # Should have warnings for invalid score
        assert len(result.warnings) > 0


@pytest.mark.validation
@pytest.mark.integration
class TestValidationWorkflow:
    """Integration tests for complete validation workflow."""

    def test_validate_complete_pipeline_data(self, tmp_path):
        """Test validation of complete pipeline data."""
        # Create personas
        personas = [
            {
                'id': 'P001',
                'age': 28,
                'gender': 'female',
                'description': 'Test persona',
                'education': 'bachelors'
            }
        ]
        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        # Create health records
        records = [
            {
                'id': 'R001',
                'age': 28,
                'conditions': ['pregnancy']
            }
        ]
        records_file = tmp_path / "records.json"
        with open(records_file, 'w') as f:
            json.dump(records, f)

        # Create matched pairs
        matched = [
            {
                'persona': personas[0],
                'health_record': records[0],
                'compatibility_score': 0.95
            }
        ]
        matched_file = tmp_path / "matched.json"
        with open(matched_file, 'w') as f:
            json.dump(matched, f)

        # Validate all
        result_personas = validate_personas(str(personas_file))
        result_records = validate_health_records(str(records_file))
        result_matched = validate_matched_pairs(str(matched_file))

        # All should pass
        assert result_personas.passed is True
        assert result_records.passed is True
        assert result_matched.passed is True

    def test_validate_inconsistent_data(self, tmp_path):
        """Test validation catches inconsistencies."""
        # Persona with age 28
        personas = [
            {
                'id': 'P001',
                'age': 28,
                'gender': 'female',
                'description': 'Test'
            }
        ]

        # Matched with record age 45 (large mismatch)
        matched = [
            {
                'persona': {'id': 'P001', 'age': 28},
                'health_record': {'id': 'R001', 'age': 45},
                'compatibility_score': 0.95  # High score despite age mismatch
            }
        ]

        matched_file = tmp_path / "matched.json"
        with open(matched_file, 'w') as f:
            json.dump(matched, f)

        result = validate_matched_pairs(str(matched_file))

        # Validation should flag this inconsistency
        # (High score with poor age match)
        assert len(result.warnings) > 0 or len(result.errors) > 0


@pytest.mark.validation
@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases in validation."""

    def test_validate_large_dataset(self, tmp_path):
        """Test validation of large dataset."""
        # Create 1000 personas
        personas = [
            {
                'id': f'P{i:04d}',
                'age': 20 + (i % 30),
                'gender': 'female',
                'description': f'Persona {i}'
            }
            for i in range(1000)
        ]

        personas_file = tmp_path / "large_personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        # Should handle large dataset
        assert '1000 personas' in ' '.join(result.info)

    def test_validate_unicode_content(self, tmp_path):
        """Test validation with unicode characters."""
        personas = [
            {
                'id': 'P001',
                'age': 28,
                'gender': 'female',
                'description': 'Persona with émojis 🤰 and spëcial çharacters'
            }
        ]

        personas_file = tmp_path / "unicode_personas.json"
        with open(personas_file, 'w', encoding='utf-8') as f:
            json.dump(personas, f, ensure_ascii=False)

        result = validate_personas(str(personas_file))

        # Should handle unicode
        assert result.passed is True

    def test_validate_null_values(self, tmp_path):
        """Test validation with null values."""
        personas = [
            {
                'id': 'P001',
                'age': None,
                'gender': None,
                'description': 'Test'
            }
        ]

        personas_file = tmp_path / "null_personas.json"
        with open(personas_file, 'w') as f:
            json.dump(personas, f)

        result = validate_personas(str(personas_file))

        # Should handle nulls gracefully
        assert len(result.warnings) > 0  # May warn about missing data
