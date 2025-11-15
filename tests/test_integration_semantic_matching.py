"""
Integration tests for end-to-end semantic matching workflow.

Phase 1, Task 1.4.5 - v1.2.0 Implementation

Tests cover:
- Complete matching workflow from FHIR to match scores
- Integration between semantic tree generation and similarity calculation
- Real data integration tests
- Performance and scalability tests
"""

import pytest
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.fhir_semantic_extractor import build_semantic_tree_from_fhir
from scripts.utils.semantic_tree import (
    calculate_semantic_tree_similarity,
    persona_tree_from_dict
)


class TestEndToEndMatching:
    """Test complete matching workflow."""

    def test_fhir_to_match_score(self, sample_fhir_bundle, sample_persona_with_semantic_tree):
        """Test complete flow from FHIR data to match score."""
        # Step 1: Build semantic tree from FHIR
        patient_id = 'patient-123'
        age = 28

        record_tree = build_semantic_tree_from_fhir(sample_fhir_bundle, patient_id, age)

        # Step 2: Convert persona to tree
        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        # Step 3: Calculate similarity
        similarity, components = calculate_semantic_tree_similarity(persona_tree, record_tree)

        # Verify complete workflow
        assert 0.0 <= similarity <= 1.0
        assert isinstance(components, dict)
        assert len(components) > 0

    def test_multiple_personas_to_single_record(
        self,
        sample_fhir_bundle,
        sample_persona_with_semantic_tree
    ):
        """Test matching multiple personas to a single health record."""
        # Build health record tree
        record_tree = build_semantic_tree_from_fhir(sample_fhir_bundle, 'patient-123', 28)

        # Create variations of persona
        personas = [
            sample_persona_with_semantic_tree,
            {**sample_persona_with_semantic_tree, 'age': 25},
            {**sample_persona_with_semantic_tree, 'age': 35}
        ]

        scores = []
        for persona in personas:
            persona_tree = persona_tree_from_dict(persona['semantic_tree'])
            similarity, _ = calculate_semantic_tree_similarity(persona_tree, record_tree)
            scores.append(similarity)

        # All scores should be valid
        assert all(0.0 <= score <= 1.0 for score in scores)
        # Scores should vary based on persona differences
        assert len(set(scores)) > 1  # Not all identical

    def test_persona_to_multiple_records(
        self,
        sample_fhir_bundle,
        minimal_fhir_bundle,
        edge_case_fhir_bundle,
        sample_persona_with_semantic_tree
    ):
        """Test matching a single persona to multiple health records."""
        # Build multiple record trees
        records = [
            build_semantic_tree_from_fhir(sample_fhir_bundle, 'patient-1', 28),
            build_semantic_tree_from_fhir(minimal_fhir_bundle, 'patient-2', 30),
            build_semantic_tree_from_fhir(edge_case_fhir_bundle, 'patient-3', 32)
        ]

        # Build persona tree
        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        # Calculate scores
        scores = []
        for record_tree in records:
            similarity, _ = calculate_semantic_tree_similarity(persona_tree, record_tree)
            scores.append(similarity)

        # All scores should be valid
        assert all(0.0 <= score <= 1.0 for score in scores)


class TestRealDataIntegration:
    """Integration tests with real data."""

    def test_real_persona_to_real_record(
        self,
        real_fhir_file_path,
        real_personas_file_path
    ):
        """Test matching with real persona and FHIR data."""
        if real_fhir_file_path is None or real_personas_file_path is None:
            pytest.skip("Real data files not available")

        # Load real FHIR data
        with open(real_fhir_file_path, 'r') as f:
            fhir_data = json.load(f)

        # Load real personas
        with open(real_personas_file_path, 'r') as f:
            personas = json.load(f)

        if not personas:
            pytest.skip("No personas in file")

        # Build record tree
        record_tree = build_semantic_tree_from_fhir(fhir_data, real_fhir_file_path.stem, 30)

        # Test with first persona
        persona = personas[0]
        persona_tree = persona_tree_from_dict(persona['semantic_tree'])

        similarity, components = calculate_semantic_tree_similarity(persona_tree, record_tree)

        # Verify workflow completes successfully
        assert 0.0 <= similarity <= 1.0
        assert len(components) > 0

    def test_all_personas_to_sample_records(self, real_personas_file_path):
        """Test all real personas against sample records."""
        if real_personas_file_path is None:
            pytest.skip("Personas file not available")

        # Load personas
        with open(real_personas_file_path, 'r') as f:
            personas = json.load(f)

        # Load sample FHIR files
        fhir_dir = Path('synthea/output/fhir')
        if not fhir_dir.exists():
            pytest.skip("FHIR directory not found")

        fhir_files = list(fhir_dir.glob('*.json'))[:5]  # Test with first 5
        fhir_files = [f for f in fhir_files if 'hospitalInformation' not in f.name and 'practitionerInformation' not in f.name]

        if not fhir_files:
            pytest.skip("No FHIR files found")

        # Build record trees
        records = []
        for fhir_file in fhir_files:
            with open(fhir_file, 'r') as f:
                fhir_data = json.load(f)
            record_tree = build_semantic_tree_from_fhir(fhir_data, fhir_file.stem, 30)
            records.append(record_tree)

        # Test each persona against each record
        total_matches = 0
        for persona in personas:
            persona_tree = persona_tree_from_dict(persona['semantic_tree'])

            for record_tree in records:
                similarity, _ = calculate_semantic_tree_similarity(persona_tree, record_tree)
                assert 0.0 <= similarity <= 1.0
                total_matches += 1

        # Verify we tested all combinations
        assert total_matches == len(personas) * len(records)


class TestMatchingQuality:
    """Test matching quality and consistency."""

    def test_consistent_scoring(self, sample_fhir_bundle, sample_persona_with_semantic_tree):
        """Test that scoring is consistent across multiple runs."""
        # Build trees once
        record_tree = build_semantic_tree_from_fhir(sample_fhir_bundle, 'patient-123', 28)
        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        # Calculate score multiple times
        scores = []
        for _ in range(5):
            similarity, _ = calculate_semantic_tree_similarity(persona_tree, record_tree)
            scores.append(similarity)

        # All scores should be identical (deterministic)
        assert len(set(scores)) == 1, "Scoring should be deterministic"

    def test_score_ordering(
        self,
        sample_fhir_bundle,
        minimal_fhir_bundle,
        sample_persona_with_semantic_tree
    ):
        """Test that better matches score higher than worse matches."""
        # sample_fhir_bundle has pregnancy-related data
        # minimal_fhir_bundle has minimal data

        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        # Calculate scores
        rich_record = build_semantic_tree_from_fhir(sample_fhir_bundle, 'patient-rich', 28)
        minimal_record = build_semantic_tree_from_fhir(minimal_fhir_bundle, 'patient-minimal', 28)

        rich_score, _ = calculate_semantic_tree_similarity(persona_tree, rich_record)
        minimal_score, _ = calculate_semantic_tree_similarity(persona_tree, minimal_record)

        # Rich record should score higher (has more matching data)
        assert rich_score > minimal_score


class TestPerformance:
    """Test performance and scalability."""

    def test_single_match_performance(
        self,
        sample_fhir_bundle,
        sample_persona_with_semantic_tree
    ):
        """Test that single match completes quickly."""
        import time

        record_tree = build_semantic_tree_from_fhir(sample_fhir_bundle, 'patient-123', 28)
        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        start = time.time()
        similarity, components = calculate_semantic_tree_similarity(persona_tree, record_tree)
        elapsed = time.time() - start

        # Should complete in under 100ms
        assert elapsed < 0.1, f"Single match took {elapsed:.3f}s (expected < 0.1s)"

    def test_batch_matching_performance(
        self,
        sample_fhir_bundle,
        sample_persona_with_semantic_tree
    ):
        """Test performance of matching one persona to multiple records."""
        import time

        # Build persona tree once
        persona_tree = persona_tree_from_dict(sample_persona_with_semantic_tree['semantic_tree'])

        # Build multiple record trees
        num_records = 10
        records = []
        for i in range(num_records):
            record_tree = build_semantic_tree_from_fhir(sample_fhir_bundle, f'patient-{i}', 28 + i)
            records.append(record_tree)

        # Time the matching
        start = time.time()
        for record_tree in records:
            similarity, _ = calculate_semantic_tree_similarity(persona_tree, record_tree)
        elapsed = time.time() - start

        avg_time = elapsed / num_records

        # Should average under 50ms per match
        assert avg_time < 0.05, f"Average match time {avg_time:.3f}s (expected < 0.05s)"


class TestErrorHandling:
    """Test error handling in integration workflow."""

    def test_malformed_fhir_handling(self):
        """Test handling of malformed FHIR data."""
        malformed_bundle = {
            'resourceType': 'Bundle',
            # Missing required fields
        }

        # Should handle gracefully or raise appropriate error
        try:
            tree = build_semantic_tree_from_fhir(malformed_bundle, 'patient-test', 30)
            # If it succeeds, should return valid tree
            assert tree is not None
        except Exception as e:
            # If it fails, should be a meaningful error
            assert isinstance(e, (KeyError, ValueError, AttributeError))

    def test_missing_semantic_tree_fields(self):
        """Test handling of persona with incomplete semantic tree."""
        incomplete_tree = {
            'age': 28
            # Missing most fields
        }

        # Should handle gracefully
        persona_tree = persona_tree_from_dict(incomplete_tree)
        assert persona_tree is not None
        assert persona_tree.age == 28
