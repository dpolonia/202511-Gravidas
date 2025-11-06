"""
Tests for scripts/utils/common_loaders.py

Tests data loading functions used across the pipeline.
"""

import pytest
import json
import yaml
from pathlib import Path
from scripts.utils.common_loaders import (
    load_config,
    load_personas,
    load_health_records,
    load_matched_pairs
)


@pytest.mark.loaders
@pytest.mark.unit
class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_valid_config(self, temp_config_file):
        """Test loading a valid config file."""
        config = load_config(str(temp_config_file))

        assert config is not None
        assert isinstance(config, dict)
        assert 'active_provider' in config
        assert config['active_provider'] == 'anthropic'

    def test_load_nonexistent_config(self, tmp_path):
        """Test loading a non-existent config file."""
        nonexistent = tmp_path / "nonexistent.yaml"
        config = load_config(str(nonexistent))

        # Should return empty dict on error
        assert config == {}

    def test_load_invalid_yaml(self, tmp_path):
        """Test loading invalid YAML file."""
        invalid_yaml = tmp_path / "invalid.yaml"
        invalid_yaml.write_text("{ invalid: yaml: content:")

        config = load_config(str(invalid_yaml))

        # Should return empty dict on YAML error
        assert config == {}

    def test_load_config_with_retry_section(self, temp_config_file):
        """Test that config includes retry configuration."""
        config = load_config(str(temp_config_file))

        assert 'retry' in config
        assert config['retry']['max_retries'] == 3
        assert config['retry']['strategy'] == 'exponential'


@pytest.mark.loaders
@pytest.mark.unit
class TestLoadPersonas:
    """Tests for load_personas function."""

    def test_load_valid_personas(self, temp_personas_file):
        """Test loading valid personas file."""
        personas = load_personas(str(temp_personas_file))

        assert personas is not None
        assert isinstance(personas, list)
        assert len(personas) == 3
        assert personas[0]['id'] == 'persona_001'

    def test_load_nonexistent_personas(self, tmp_path):
        """Test loading non-existent personas file."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit):
            load_personas(str(nonexistent))

    def test_load_invalid_json(self, invalid_json_file):
        """Test loading invalid JSON file."""
        with pytest.raises(SystemExit):
            load_personas(str(invalid_json_file))

    def test_load_personas_not_list(self, tmp_path):
        """Test loading JSON that's not a list."""
        not_list = tmp_path / "not_list.json"
        not_list.write_text('{"key": "value"}')

        with pytest.raises(SystemExit):
            load_personas(str(not_list))

    def test_load_empty_personas_list(self, tmp_path):
        """Test loading empty personas list."""
        empty_list = tmp_path / "empty_list.json"
        empty_list.write_text('[]')

        personas = load_personas(str(empty_list))
        assert personas == []


@pytest.mark.loaders
@pytest.mark.unit
class TestLoadHealthRecords:
    """Tests for load_health_records function."""

    def test_load_valid_records(self, temp_records_file):
        """Test loading valid health records file."""
        records = load_health_records(str(temp_records_file))

        assert records is not None
        assert isinstance(records, list)
        assert len(records) == 3
        assert records[0]['id'] == 'record_001'

    def test_load_nonexistent_records(self, tmp_path):
        """Test loading non-existent records file."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit):
            load_health_records(str(nonexistent))

    def test_load_invalid_json_records(self, invalid_json_file):
        """Test loading invalid JSON file."""
        with pytest.raises(SystemExit):
            load_health_records(str(invalid_json_file))

    def test_load_records_not_list(self, tmp_path):
        """Test loading JSON that's not a list."""
        not_list = tmp_path / "not_list.json"
        not_list.write_text('{"key": "value"}')

        with pytest.raises(SystemExit):
            load_health_records(str(not_list))


@pytest.mark.loaders
@pytest.mark.unit
class TestLoadMatchedPairs:
    """Tests for load_matched_pairs function."""

    def test_load_valid_matched_pairs(self, tmp_path, sample_matched_pair):
        """Test loading valid matched pairs file."""
        matched_file = tmp_path / "matched.json"
        with open(matched_file, 'w') as f:
            json.dump([sample_matched_pair], f)

        pairs = load_matched_pairs(str(matched_file))

        assert pairs is not None
        assert isinstance(pairs, list)
        assert len(pairs) == 1
        assert 'persona' in pairs[0]
        assert 'health_record' in pairs[0]
        assert 'compatibility_score' in pairs[0]

    def test_load_nonexistent_matched_pairs(self, tmp_path):
        """Test loading non-existent matched pairs file."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(SystemExit):
            load_matched_pairs(str(nonexistent))

    def test_load_empty_matched_pairs(self, tmp_path):
        """Test loading empty matched pairs list."""
        empty_list = tmp_path / "empty_matched.json"
        empty_list.write_text('[]')

        pairs = load_matched_pairs(str(empty_list))
        assert pairs == []


@pytest.mark.loaders
@pytest.mark.integration
class TestLoadersIntegration:
    """Integration tests for loaders working together."""

    def test_load_all_pipeline_files(self, tmp_path, sample_config, sample_personas, sample_health_records):
        """Test loading all pipeline files in sequence."""
        # Create all files
        config_file = tmp_path / "config.yaml"
        with open(config_file, 'w') as f:
            yaml.dump(sample_config, f)

        personas_file = tmp_path / "personas.json"
        with open(personas_file, 'w') as f:
            json.dump(sample_personas, f)

        records_file = tmp_path / "records.json"
        with open(records_file, 'w') as f:
            json.dump(sample_health_records, f)

        # Load all files
        config = load_config(str(config_file))
        personas = load_personas(str(personas_file))
        records = load_health_records(str(records_file))

        # Verify all loaded correctly
        assert config is not None
        assert len(personas) == 3
        assert len(records) == 3
        assert config['active_provider'] == 'anthropic'
