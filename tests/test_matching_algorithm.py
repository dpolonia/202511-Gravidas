"""
Tests for matching algorithm functions.

Tests compatibility scoring between personas and health records.
"""

import pytest
import sys
import os
from pathlib import Path
import importlib.util

# Add project root and scripts to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "scripts"))

# Import the matching module using importlib (since filename starts with number)
spec = importlib.util.spec_from_file_location(
    "match_personas_records",
    project_root / "scripts" / "03_match_personas_records.py"
)
matching_module = importlib.util.module_from_spec(spec)
sys.modules['match_personas_records'] = matching_module
spec.loader.exec_module(matching_module)

# Extract functions
calculate_age_compatibility = matching_module.calculate_age_compatibility
calculate_socioeconomic_compatibility = matching_module.calculate_socioeconomic_compatibility
calculate_compatibility_score = matching_module.calculate_compatibility_score
normalize_education = matching_module.normalize_education
normalize_income = matching_module.normalize_income

# Create a module-like namespace for cleaner test code
class matching:
    """Namespace for matching functions."""
    calculate_age_compatibility = staticmethod(calculate_age_compatibility)
    calculate_socioeconomic_compatibility = staticmethod(calculate_socioeconomic_compatibility)
    calculate_compatibility_score = staticmethod(calculate_compatibility_score)
    normalize_education = staticmethod(normalize_education)
    normalize_income = staticmethod(normalize_income)


@pytest.mark.matching
@pytest.mark.unit
class TestAgeCompatibility:
    """Tests for calculate_age_compatibility function."""

    def test_perfect_age_match(self):
        """Test that identical ages give perfect score."""
        score = matching.calculate_age_compatibility(28, 28, tolerance=2)
        assert score == 1.0

    def test_age_within_tolerance(self):
        """Test ages within tolerance range."""
        # 1 year difference with tolerance=2
        score = matching.calculate_age_compatibility(28, 29, tolerance=2)
        assert 0.8 <= score < 1.0

        # 2 year difference (at tolerance boundary)
        score = matching.calculate_age_compatibility(28, 30, tolerance=2)
        assert 0.6 <= score <= 0.8

    def test_age_beyond_tolerance(self):
        """Test ages beyond tolerance but still reasonable."""
        # 3 years apart (tolerance * 1.5)
        score = matching.calculate_age_compatibility(28, 31, tolerance=2)
        assert 0.5 <= score < 0.8

        # 4 years apart (tolerance * 2)
        score = matching.calculate_age_compatibility(28, 32, tolerance=2)
        assert 0.2 <= score <= 0.5

    def test_age_far_apart(self):
        """Test ages very far apart."""
        # 10 years apart
        score = matching.calculate_age_compatibility(28, 38, tolerance=2)
        assert 0.0 <= score < 0.2

        # 20 years apart
        score = matching.calculate_age_compatibility(28, 48, tolerance=2)
        assert score < 0.1

    def test_age_compatibility_symmetric(self):
        """Test that age compatibility is symmetric."""
        score1 = matching.calculate_age_compatibility(28, 32, tolerance=2)
        score2 = matching.calculate_age_compatibility(32, 28, tolerance=2)
        assert score1 == score2

    def test_custom_tolerance(self):
        """Test age compatibility with different tolerance values."""
        # Stricter tolerance
        score_strict = matching.calculate_age_compatibility(28, 30, tolerance=1)
        score_loose = matching.calculate_age_compatibility(28, 30, tolerance=3)

        # With stricter tolerance, score should be lower
        assert score_strict < score_loose

    def test_zero_age_edge_case(self):
        """Test edge case with zero age (handled by caller but test anyway)."""
        # This shouldn't happen in practice, but function should handle it
        score = matching.calculate_age_compatibility(0, 28, tolerance=2)
        assert 0.0 <= score <= 1.0


@pytest.mark.matching
@pytest.mark.unit
class TestEducationNormalization:
    """Tests for normalize_education function."""

    def test_all_education_levels(self):
        """Test all education level mappings."""
        assert matching.normalize_education('no_degree') == 0
        assert matching.normalize_education('unknown') == 1
        assert matching.normalize_education('high_school') == 2
        assert matching.normalize_education('bachelors') == 3
        assert matching.normalize_education('masters') == 4
        assert matching.normalize_education('doctorate') == 5

    def test_case_insensitive(self):
        """Test that education normalization is case-insensitive."""
        assert matching.normalize_education('HIGH_SCHOOL') == 2
        assert matching.normalize_education('Bachelors') == 3
        assert matching.normalize_education('MASTERS') == 4

    def test_unknown_education(self):
        """Test handling of unknown education values."""
        assert matching.normalize_education('invalid_level') == 1
        assert matching.normalize_education('') == 1


@pytest.mark.matching
@pytest.mark.unit
class TestIncomeNormalization:
    """Tests for normalize_income function."""

    def test_all_income_levels(self):
        """Test all income level mappings."""
        assert matching.normalize_income('low') == 0
        assert matching.normalize_income('lower_middle') == 1
        assert matching.normalize_income('middle') == 2
        assert matching.normalize_income('upper_middle') == 3
        assert matching.normalize_income('high') == 4

    def test_unknown_income_defaults_to_middle(self):
        """Test that unknown income defaults to middle class."""
        assert matching.normalize_income('unknown') == 2
        assert matching.normalize_income('invalid_level') == 2

    def test_case_insensitive_income(self):
        """Test that income normalization is case-insensitive."""
        assert matching.normalize_income('LOW') == 0
        assert matching.normalize_income('Upper_Middle') == 3
        assert matching.normalize_income('HIGH') == 4


@pytest.mark.matching
@pytest.mark.unit
class TestSocioeconomicCompatibility:
    """Tests for calculate_socioeconomic_compatibility function."""

    def test_perfect_socioeconomic_match(self):
        """Test personas with identical socioeconomic factors."""
        persona = {
            'education': 'bachelors',
            'income_level': 'middle',
            'marital_status': 'married'
        }
        record = {
            'education': 'bachelors',
            'income_level': 'middle',
            'marital_status': 'married'
        }

        score = matching.calculate_socioeconomic_compatibility(persona, record)
        assert score >= 0.9  # Should be very high

    def test_education_mismatch(self):
        """Test education level differences."""
        persona_high = {
            'education': 'masters',
            'income_level': 'middle'
        }
        persona_low = {
            'education': 'high_school',
            'income_level': 'middle'
        }
        record = {'income_level': 'middle'}

        score_high = matching.calculate_socioeconomic_compatibility(persona_high, record)
        score_low = matching.calculate_socioeconomic_compatibility(persona_low, record)

        # Both should have positive scores
        assert 0.0 < score_high <= 1.0
        assert 0.0 < score_low <= 1.0

    def test_income_mismatch(self):
        """Test income level differences."""
        persona = {
            'income_level': 'high',
            'education': 'bachelors'
        }
        record = {
            'income_level': 'low',
            'education': 'bachelors'
        }

        score = matching.calculate_socioeconomic_compatibility(persona, record)

        # Should have reduced score due to income mismatch
        assert 0.0 < score < 1.0

    def test_missing_fields(self):
        """Test handling of missing socioeconomic fields."""
        persona = {}  # No fields
        record = {}

        score = matching.calculate_socioeconomic_compatibility(persona, record)

        # Should return default neutral score
        assert score == 0.5

    def test_partial_fields(self):
        """Test with only some fields present."""
        persona = {
            'education': 'bachelors'
            # Missing income and marital status
        }
        record = {}

        score = matching.calculate_socioeconomic_compatibility(persona, record)

        # Should compute score based on available data
        assert 0.0 <= score <= 1.0


@pytest.mark.matching
@pytest.mark.unit
class TestOverallCompatibility:
    """Tests for calculate_compatibility_score function."""

    def test_perfect_match(self, sample_persona, sample_health_record):
        """Test perfect compatibility score."""
        # Ensure ages match
        persona = sample_persona.copy()
        record = sample_health_record.copy()
        persona['age'] = 28
        record['age'] = 28
        persona['education'] = 'bachelors'
        record['education'] = 'bachelors'

        score = matching.calculate_compatibility_score(persona, record)

        # Should be very high
        assert score >= 0.85

    def test_age_dominance(self):
        """Test that age has more weight than socioeconomic factors."""
        persona = {
            'age': 28,
            'education': 'bachelors',
            'income_level': 'middle'
        }

        # Perfect age, poor socioeconomic match
        record1 = {
            'age': 28,
            'education': 'no_degree',
            'income_level': 'low'
        }

        # Poor age, perfect socioeconomic match
        record2 = {
            'age': 45,
            'education': 'bachelors',
            'income_level': 'middle'
        }

        score1 = matching.calculate_compatibility_score(persona, record1)
        score2 = matching.calculate_compatibility_score(persona, record2)

        # Perfect age should score higher (age_weight = 0.6)
        assert score1 > score2

    def test_custom_weights(self):
        """Test compatibility with custom weights."""
        persona = {
            'age': 28,
            'education': 'bachelors',
            'income_level': 'middle'
        }
        record = {
            'age': 32,
            'education': 'high_school',
            'income_level': 'low'
        }

        # Default weights (age=0.6, socioeconomic=0.4)
        score_default = matching.calculate_compatibility_score(
            persona, record,
            age_weight=0.6,
            socioeconomic_weight=0.4
        )

        # Equal weights
        score_equal = matching.calculate_compatibility_score(
            persona, record,
            age_weight=0.5,
            socioeconomic_weight=0.5
        )

        # Scores should be different
        assert score_default != score_equal

    def test_missing_ages(self):
        """Test handling of missing age data."""
        persona = {'education': 'bachelors'}
        record = {'education': 'masters'}

        score = matching.calculate_compatibility_score(persona, record)

        # Should use default age score of 0.5
        assert 0.0 < score < 1.0

    def test_score_range(self):
        """Test that scores are always in valid range."""
        personas = [
            {'age': 20, 'education': 'high_school'},
            {'age': 30, 'education': 'bachelors'},
            {'age': 40, 'education': 'masters'},
        ]
        records = [
            {'age': 25, 'education': 'bachelors'},
            {'age': 35, 'education': 'doctorate'},
            {'age': 50, 'education': 'no_degree'},
        ]

        for persona in personas:
            for record in records:
                score = matching.calculate_compatibility_score(persona, record)
                assert 0.0 <= score <= 1.0, f"Score {score} out of range for {persona} + {record}"


@pytest.mark.matching
@pytest.mark.integration
class TestMatchingIntegration:
    """Integration tests for complete matching workflow."""

    def test_realistic_matching_scenario(self):
        """Test realistic persona-record matching."""
        persona = {
            'id': 'P001',
            'age': 28,
            'education': 'bachelors',
            'income_level': 'middle',
            'marital_status': 'married'
        }

        # Good match
        record_good = {
            'id': 'R001',
            'age': 29,
            'education': 'bachelors',
            'income_level': 'middle'
        }

        # Poor match
        record_poor = {
            'id': 'R002',
            'age': 45,
            'education': 'no_degree',
            'income_level': 'low'
        }

        score_good = matching.calculate_compatibility_score(persona, record_good)
        score_poor = matching.calculate_compatibility_score(persona, record_poor)

        assert score_good > score_poor
        assert score_good >= 0.75
        assert score_poor < 0.50

    def test_multiple_candidates_ranking(self):
        """Test that multiple records can be ranked by compatibility."""
        persona = {
            'age': 30,
            'education': 'masters',
            'income_level': 'upper_middle'
        }

        records = [
            {'id': 'R1', 'age': 30, 'education': 'masters'},      # Perfect age + education
            {'id': 'R2', 'age': 31, 'education': 'bachelors'},    # Close age, lower education
            {'id': 'R3', 'age': 40, 'education': 'high_school'},  # Far age, much lower education
        ]

        scores = [
            (r['id'], matching.calculate_compatibility_score(persona, r))
            for r in records
        ]

        # Sort by score descending
        scores.sort(key=lambda x: x[1], reverse=True)

        # Best match should be R1
        assert scores[0][0] == 'R1'
        assert scores[1][0] == 'R2'
        assert scores[2][0] == 'R3'

        # Scores should be monotonically decreasing
        assert scores[0][1] > scores[1][1] > scores[2][1]


@pytest.mark.matching
@pytest.mark.unit
class TestEdgeCases:
    """Tests for edge cases and boundary conditions."""

    def test_extreme_age_differences(self):
        """Test very large age differences."""
        score = matching.calculate_age_compatibility(20, 60, tolerance=2)
        assert 0.0 <= score < 0.01  # Should be nearly zero

    def test_all_unknown_fields(self):
        """Test matching with all unknown fields."""
        persona = {
            'education': 'unknown',
            'income_level': 'unknown',
            'marital_status': 'unknown'
        }
        record = {
            'education': 'unknown',
            'income_level': 'unknown'
        }

        score = matching.calculate_socioeconomic_compatibility(persona, record)
        # Should handle gracefully
        assert 0.0 <= score <= 1.0

    def test_negative_ages(self):
        """Test that function handles negative ages (shouldn't happen but test defensively)."""
        # The function uses abs() for age difference, so should handle gracefully
        score = matching.calculate_age_compatibility(-5, 28, tolerance=2)
        assert 0.0 <= score <= 1.0

    def test_very_high_tolerance(self):
        """Test with unusually high tolerance value."""
        score = matching.calculate_age_compatibility(28, 35, tolerance=10)
        # With high tolerance, 7-year difference should score well
        assert score >= 0.7
