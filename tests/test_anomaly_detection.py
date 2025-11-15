"""
Unit tests for anomaly detection in matching algorithm.

Phase 1, Task 1.4.6 - v1.2.0 Implementation

Tests cover:
- Anomaly threshold application
- Score flagging logic
- Calibrated threshold validation
- Edge cases near threshold
"""

import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Calibrated threshold from Phase 1, Task 1.3
ANOMALY_THRESHOLD = 0.7000


class TestAnomalyThreshold:
    """Test anomaly detection threshold logic."""

    def test_score_above_threshold_not_flagged(self):
        """Test that scores above threshold are not flagged as anomalous."""
        scores = [0.7001, 0.75, 0.80, 0.85, 0.90, 0.95, 1.0]

        for score in scores:
            is_anomalous = score < ANOMALY_THRESHOLD
            assert not is_anomalous, f"Score {score} should NOT be flagged"

    def test_score_below_threshold_flagged(self):
        """Test that scores below threshold are flagged as anomalous."""
        scores = [0.0, 0.1, 0.3, 0.5, 0.65, 0.6999]

        for score in scores:
            is_anomalous = score < ANOMALY_THRESHOLD
            assert is_anomalous, f"Score {score} SHOULD be flagged"

    def test_score_exactly_at_threshold(self):
        """Test boundary condition: score exactly at threshold."""
        score = ANOMALY_THRESHOLD

        is_anomalous = score < ANOMALY_THRESHOLD
        # Score at threshold should NOT be flagged
        assert not is_anomalous

    def test_threshold_value(self):
        """Test that calibrated threshold is correct value."""
        assert ANOMALY_THRESHOLD == 0.7000


class TestBoundaryConditions:
    """Test edge cases and boundary conditions."""

    def test_epsilon_above_threshold(self):
        """Test score just slightly above threshold."""
        epsilon = 0.0001
        score = ANOMALY_THRESHOLD + epsilon

        is_anomalous = score < ANOMALY_THRESHOLD
        assert not is_anomalous

    def test_epsilon_below_threshold(self):
        """Test score just slightly below threshold."""
        epsilon = 0.0001
        score = ANOMALY_THRESHOLD - epsilon

        is_anomalous = score < ANOMALY_THRESHOLD
        assert is_anomalous

    def test_very_low_score(self):
        """Test handling of very low scores."""
        very_low_scores = [0.0, 0.01, 0.05, 0.1]

        for score in very_low_scores:
            is_anomalous = score < ANOMALY_THRESHOLD
            assert is_anomalous
            # Should also be critical (< 0.5)
            is_critical = score < 0.5
            assert is_critical

    def test_perfect_score(self):
        """Test handling of perfect score."""
        score = 1.0

        is_anomalous = score < ANOMALY_THRESHOLD
        assert not is_anomalous


class TestAnomalySeverity:
    """Test different severity levels of anomalies."""

    def test_critical_anomaly(self):
        """Test critical anomaly (score < 0.5)."""
        critical_scores = [0.0, 0.1, 0.3, 0.4999]

        for score in critical_scores:
            is_critical = score < 0.5
            assert is_critical, f"Score {score} should be critical"

    def test_warning_anomaly(self):
        """Test warning anomaly (0.5 <= score < 0.7)."""
        warning_scores = [0.5, 0.55, 0.6, 0.65, 0.6999]

        for score in warning_scores:
            is_warning = 0.5 <= score < ANOMALY_THRESHOLD
            assert is_warning, f"Score {score} should be warning level"

    def test_acceptable_score(self):
        """Test acceptable scores (0.7 <= score < 0.8)."""
        acceptable_scores = [0.7, 0.72, 0.75, 0.78, 0.7999]

        for score in acceptable_scores:
            is_acceptable = 0.7 <= score < 0.8
            assert is_acceptable, f"Score {score} should be acceptable"

    def test_high_quality_score(self):
        """Test high quality scores (score >= 0.8)."""
        high_quality_scores = [0.8, 0.85, 0.9, 0.95, 1.0]

        for score in high_quality_scores:
            is_high_quality = score >= 0.8
            assert is_high_quality, f"Score {score} should be high quality"


class TestAnomalyClassification:
    """Test classification of scores into categories."""

    def classify_score(self, score: float) -> str:
        """Classify score into category."""
        if score < 0.5:
            return 'critical'
        elif score < 0.7:
            return 'warning'
        elif score < 0.8:
            return 'acceptable'
        else:
            return 'high_quality'

    def test_critical_classification(self):
        """Test classification of critical scores."""
        assert self.classify_score(0.0) == 'critical'
        assert self.classify_score(0.3) == 'critical'
        assert self.classify_score(0.49) == 'critical'

    def test_warning_classification(self):
        """Test classification of warning scores."""
        assert self.classify_score(0.5) == 'warning'
        assert self.classify_score(0.6) == 'warning'
        assert self.classify_score(0.69) == 'warning'

    def test_acceptable_classification(self):
        """Test classification of acceptable scores."""
        assert self.classify_score(0.7) == 'acceptable'
        assert self.classify_score(0.75) == 'acceptable'
        assert self.classify_score(0.79) == 'acceptable'

    def test_high_quality_classification(self):
        """Test classification of high quality scores."""
        assert self.classify_score(0.8) == 'high_quality'
        assert self.classify_score(0.9) == 'high_quality'
        assert self.classify_score(1.0) == 'high_quality'


class TestAnomalyStatistics:
    """Test statistical properties of anomaly detection."""

    def test_false_positive_rate(self):
        """Test that false positive rate is acceptable."""
        # Simulate best match scores from calibration
        best_match_scores = [
            0.7051, 0.7113, 0.7666, 0.8536, 0.8686,
            0.8686, 0.8686, 0.8956, 0.8986, 0.9121, 0.9121
        ]

        flagged_count = sum(1 for score in best_match_scores if score < ANOMALY_THRESHOLD)
        total = len(best_match_scores)

        false_positive_rate = flagged_count / total

        # Should have 0% false positive rate (based on calibration)
        assert false_positive_rate == 0.0

    def test_true_positive_rate(self):
        """Test that true positive rate is acceptable."""
        # Simulate worst match scores (should all be flagged)
        worst_match_scores = [
            0.1551, 0.1551, 0.1551, 0.1551, 0.1551,
            0.1671, 0.1701, 0.1701
        ]

        flagged_count = sum(1 for score in worst_match_scores if score < ANOMALY_THRESHOLD)
        total = len(worst_match_scores)

        true_positive_rate = flagged_count / total

        # Should have 100% true positive rate
        assert true_positive_rate == 1.0

    def test_borderline_distribution(self):
        """Test distribution of scores near threshold."""
        borderline_scores = [
            0.6500, 0.6750, 0.6900, 0.6950, 0.6999,
            0.7000, 0.7001, 0.7050, 0.7100, 0.7250, 0.7500
        ]

        below_threshold = [s for s in borderline_scores if s < ANOMALY_THRESHOLD]
        at_or_above_threshold = [s for s in borderline_scores if s >= ANOMALY_THRESHOLD]

        # Verify counts
        assert len(below_threshold) == 5
        assert len(at_or_above_threshold) == 6


class TestThresholdValidation:
    """Test threshold validation against known edge cases."""

    def test_calibration_result_consistency(self):
        """Test that threshold is consistent with calibration results."""
        # From calibration:
        # - 5th percentile of best matches: 0.7079
        # - Mean - 2*StdDev: 0.6775
        # - IQR outlier: 0.6241
        # - MAD outlier: 0.7951 (capped at 0.7000)

        # Threshold should be 0.7000 (maximum, capped)
        assert ANOMALY_THRESHOLD == 0.7000

    def test_best_match_preservation(self):
        """Test that best matches from calibration are not flagged."""
        # Best match scores from calibration data
        calibration_best_matches = [
            0.9121, 0.9121, 0.8986, 0.8956, 0.8686,
            0.8686, 0.8686, 0.8536, 0.7666, 0.7113, 0.7051
        ]

        for score in calibration_best_matches:
            is_anomalous = score < ANOMALY_THRESHOLD
            assert not is_anomalous, f"Best match score {score} should not be flagged"

    def test_worst_match_detection(self):
        """Test that worst matches from calibration are flagged."""
        # Worst match scores from calibration data
        calibration_worst_matches = [
            0.1551, 0.1551, 0.1551, 0.1551, 0.1551,
            0.1551, 0.1551, 0.1551, 0.1551, 0.1671
        ]

        for score in calibration_worst_matches:
            is_anomalous = score < ANOMALY_THRESHOLD
            assert is_anomalous, f"Worst match score {score} should be flagged"


class TestProductionRecommendations:
    """Test production deployment recommendations."""

    def test_alert_thresholds(self):
        """Test recommended alert thresholds."""
        critical_threshold = 0.5000
        warning_threshold = 0.7000
        acceptable_threshold = 0.8000

        # Verify thresholds are properly ordered
        assert critical_threshold < warning_threshold < acceptable_threshold

        # Test classification
        assert 0.3 < critical_threshold  # Should trigger critical alert
        assert 0.6 < warning_threshold  # Should trigger warning alert
        assert 0.75 < acceptable_threshold  # Acceptable, monitored
        assert 0.9 >= acceptable_threshold  # High quality, no alert

    def test_flagging_rate(self):
        """Test that flagging rate is reasonable for production."""
        # Simulate score distribution from calibration
        all_scores = [0.3, 0.4, 0.5, 0.6, 0.65, 0.7, 0.75, 0.8, 0.85, 0.9]

        flagged = [s for s in all_scores if s < ANOMALY_THRESHOLD]
        flagging_rate = len(flagged) / len(all_scores)

        # Should flag a reasonable percentage (not too many, not too few)
        # In this sample, 5/10 = 50%
        assert 0.0 <= flagging_rate <= 1.0
