# Test Suite Documentation

## Overview

This directory contains the test suite for the Gravidas synthetic healthcare interview pipeline. Tests cover core functionality including FHIR parsing, semantic tree generation, persona-record matching, and data validation.

## Current Test Coverage

**Overall Coverage:** 35% (as of 2025-11-17)

### Well-Tested Modules (≥75% coverage)
- `fhir_semantic_extractor.py`: **91%** (288 statements, 27 missed)
  - FHIR R4 parsing logic
  - Semantic tree generation
  - Pregnancy stage detection
- `retry_logic.py`: **94%** (65 statements, 4 missed)
  - API retry mechanisms
  - Exponential backoff logic
- `semantic_tree.py`: **79%** (327 statements, 69 missed)
  - Semantic tree data structures
  - Tree validation and manipulation

### Partially-Tested Modules (40-75% coverage)
- `validate_data.py`: **55%** (216 statements, 97 missed)
  - Data validation logic
  - Schema checking

### Untested Modules (0% coverage)
- `budget_tracker.py`: 0% (118 statements)
- `cost_monitor.py`: 0% (116 statements)
- `common_loaders.py`: 0% (210 statements)

**Total:** 2,171 statements, 1,418 missed (35% coverage)

## Running Tests

### Run All Tests
```bash
pytest tests/ -v
```

### Run Tests with Coverage Report
```bash
pytest tests/ --cov=scripts --cov-report=term-missing --cov-report=html
```

This generates an HTML report in `htmlcov/index.html`.

### Run Specific Test Files
```bash
# Semantic tree generation tests
pytest tests/test_semantic_tree_generation.py -v

# Anomaly detection tests
pytest tests/test_anomaly_detection.py -v

# Retry logic tests
pytest tests/test_retry_logic.py -v
```

## Test Status

**Passing:** 84 tests
**Failing:** 15 tests (primarily due to schema changes)

### Known Test Failures

#### 1. Import Errors (3 test files)
- `test_common_loaders.py`: ModuleNotFoundError for 'utils'
- `test_matching_algorithm.py`: FileNotFoundError for old script name
- `test_semantic_similarity.py`: ImportError for deprecated 'ClinicalConditions' class

**Cause:** Tests reference outdated imports and file names after code refactoring.

#### 2. Schema Validation Failures (12 tests)
- `test_integration_semantic_matching.py`: KeyError: 'persona_id'
- `test_validation.py`: AttributeError on data structure access

**Cause:** Persona and health record data structures updated; tests expect old schema format.

## Test Organization

### Core Functionality Tests
- `test_semantic_tree_generation.py` - FHIR parsing and semantic tree creation
- `test_anomaly_detection.py` - Outlier detection and threshold calibration
- `test_retry_logic.py` - API retry mechanisms

### Integration Tests
- `test_integration_semantic_matching.py` - End-to-end persona-record matching

### Data Validation Tests
- `test_validation.py` - Schema validation and data integrity checks

### Component Tests
- `test_common_loaders.py` - Data loading utilities (currently failing)
- `test_matching_algorithm.py` - Matching algorithm logic (currently failing)
- `test_semantic_similarity.py` - Semantic comparison functions (currently failing)

## Test Strategy

### Unit Tests
Focus on individual functions and modules in isolation. Use mocking for external dependencies (API calls, file I/O).

### Integration Tests
Test complete workflows from data input through final output. Use real data files from `data/` directory when possible.

### Coverage Goals
- **Target:** ≥60% overall coverage
- **Priority:** Core modules (FHIR extraction, semantic trees, matching) should have ≥80% coverage
- **Secondary:** Utility modules should have ≥50% coverage

## Improving Test Coverage

### High Priority (to reach 60% target)
1. Add tests for `cost_monitor.py` (0% → target 60%)
   - Token counting accuracy
   - Cost calculation logic
   - Multi-provider cost tracking

2. Add tests for `budget_tracker.py` (0% → target 60%)
   - Budget threshold monitoring
   - Forecast calculations

3. Add tests for `common_loaders.py` (0% → target 60%)
   - JSON loading/saving
   - Error handling

4. Improve `validate_data.py` coverage (55% → target 70%)
   - Edge cases in validation rules
   - Error message generation

### Medium Priority
1. Fix import errors in 3 test files
2. Update schema expectations in 12 failing tests
3. Increase `semantic_tree.py` coverage (79% → target 85%)

## Test Environment

### Requirements
- Python 3.11+
- pytest
- pytest-cov
- All dependencies from `requirements.txt`

### Installation
```bash
pip install pytest pytest-cov
pip install -r requirements.txt
```

## Continuous Integration

Tests should run automatically on:
- Pre-commit hooks (fast tests only)
- Pull requests (full suite)
- Main branch merges (full suite + coverage report)

**Target:** All tests pass in <2 minutes

## Recent Changes

### 2025-11-17
- Established baseline coverage: 35%
- Identified 15 failing tests due to schema changes
- Core modules well-tested: fhir_semantic_extractor (91%), retry_logic (94%)
- Documented untested modules: budget_tracker, cost_monitor, common_loaders
