# Contributing to Gravidas

Thank you for your interest in contributing to Gravidas! This document provides guidelines for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inclusive environment for all contributors, regardless of experience level, background, or identity.

### Expected Behavior

- Be respectful and constructive in all interactions
- Welcome diverse perspectives and experiences
- Accept constructive criticism gracefully
- Focus on what is best for the community and project
- Show empathy towards other community members

### Unacceptable Behavior

- Harassment, discriminatory language, or personal attacks
- Trolling, insulting comments, or sustained disruption
- Publishing others' private information without permission
- Any conduct that would be inappropriate in a professional setting

---

## Getting Started

### Prerequisites

- Python 3.11 or higher
- Git
- API keys for at least one AI provider (Anthropic, OpenAI, Google, or xAI)
- Basic understanding of healthcare data (FHIR format helpful but not required)

### Quick Start for Contributors

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/202511-Gravidas.git
   cd 202511-Gravidas
   ```

2. **Create a development branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Set up your environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # Install dependencies
   pip install -r requirements.txt

   # Set up environment variables
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Verify your setup**
   ```bash
   # Test API access
   python scripts/validate_api_access.py

   # Run a quick test
   python scripts/01b_generate_personas.py --count 5
   ```

---

## Development Setup

### Development Environment

**Recommended IDE:** VS Code, PyCharm, or any Python-capable editor

**Required Extensions/Tools:**
- Python linter (pylint, flake8, or ruff)
- Type checker (mypy)
- Formatter (black or ruff)

### Project Structure

```
202511-Gravidas/
├── scripts/              # Main pipeline scripts
│   ├── 01b_generate_personas.py
│   ├── 02_generate_health_records.py
│   ├── 03_match_personas_records_enhanced.py
│   ├── 04_conduct_interviews.py
│   ├── 05_analyze_interviews.py
│   ├── utils/           # Utility modules
│   └── ...
├── data/                # Data files
│   ├── personas/
│   ├── health_records/
│   ├── matched/
│   └── interview_protocols.json
├── outputs/             # Generated outputs
├── docs/                # Documentation
├── config/              # Configuration files
│   └── workflow_config.yaml
├── tests/               # Test suite (coming soon)
└── README.md
```

### Configuration

Edit `config/workflow_config.yaml` to customize:
- AI provider and model selection
- Workflow parameters
- Cost limits and monitoring
- Output paths

---

## How to Contribute

### Types of Contributions

We welcome various types of contributions:

#### 1. Bug Fixes
- Fix identified bugs
- Improve error handling
- Add missing edge case handling

#### 2. New Features
- New interview protocols
- Additional AI provider support
- Enhanced analysis capabilities
- Performance optimizations

#### 3. Documentation
- Improve existing documentation
- Add usage examples
- Create tutorials
- Fix typos and clarify unclear sections

#### 4. Testing
- Add unit tests
- Create integration tests
- Improve test coverage
- Add test fixtures

#### 5. Research & Analysis
- Clinical protocol validation
- Cost optimization studies
- Quality metrics research
- Bias analysis and mitigation

---

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some modifications:

**Line Length:**
- Aim for 88 characters (Black default)
- Hard limit: 100 characters

**Naming Conventions:**
```python
# Modules and packages
lowercase_with_underscores.py

# Classes
class PersonaGenerator:
    pass

# Functions and variables
def calculate_semantic_similarity(persona, record):
    match_score = 0.0
    return match_score

# Constants
MAX_RETRY_ATTEMPTS = 3
API_TIMEOUT_SECONDS = 30
```

**Type Hints:**
```python
from typing import List, Dict, Optional, Tuple

def match_personas(
    personas: List[Dict],
    records: List[Dict],
    threshold: float = 0.7
) -> List[Tuple[Dict, Dict, float]]:
    """
    Match personas to health records.

    Args:
        personas: List of persona dictionaries
        records: List of health record dictionaries
        threshold: Minimum match score (default: 0.7)

    Returns:
        List of (persona, record, score) tuples
    """
    matches = []
    # Implementation
    return matches
```

**Docstrings:**
Use Google-style docstrings:
```python
def conduct_interview(persona: Dict, protocol: Dict) -> Dict:
    """
    Conduct an AI-powered interview with a synthetic persona.

    This function orchestrates a multi-turn conversation following
    the specified interview protocol.

    Args:
        persona: Persona dictionary with demographics and health profile
        protocol: Interview protocol with questions and structure

    Returns:
        Interview transcript with metadata and quality metrics

    Raises:
        ValueError: If persona or protocol is invalid
        APIError: If AI provider call fails

    Example:
        >>> persona = {"age": 28, "gravida": 1, ...}
        >>> protocol = load_protocol("prenatal_care.json")
        >>> interview = conduct_interview(persona, protocol)
        >>> print(f"Interview completed with {len(interview['transcript'])} turns")
    """
    # Implementation
    pass
```

### Code Quality

**Before committing:**
1. **Format code** with Black:
   ```bash
   black scripts/
   ```

2. **Lint code**:
   ```bash
   pylint scripts/
   # or
   ruff check scripts/
   ```

3. **Type check**:
   ```bash
   mypy scripts/
   ```

4. **Run tests** (when available):
   ```bash
   pytest tests/
   ```

### Logging Standards

Use Python's logging module:
```python
import logging

logger = logging.getLogger(__name__)

# Use appropriate levels
logger.debug("Detailed diagnostic information")
logger.info("General informational messages")
logger.warning("Warning messages for unexpected situations")
logger.error("Error messages for failures")
logger.critical("Critical errors that may crash the system")
```

### Error Handling

```python
# Good: Specific exception handling with recovery
try:
    response = ai_client.generate(prompt)
except APIConnectionError as e:
    logger.error(f"API connection failed: {e}")
    # Attempt retry with exponential backoff
    response = retry_with_backoff(ai_client.generate, prompt)
except APIRateLimitError as e:
    logger.warning(f"Rate limit hit: {e}")
    time.sleep(60)  # Wait before retry
    response = ai_client.generate(prompt)

# Bad: Catching all exceptions
try:
    response = ai_client.generate(prompt)
except Exception as e:  # Too broad!
    logger.error(f"Something failed: {e}")
```

---

## Testing Guidelines

### Test Structure

```
tests/
├── unit/              # Unit tests
│   ├── test_semantic_tree.py
│   ├── test_matching.py
│   └── test_cost_monitor.py
├── integration/       # Integration tests
│   ├── test_workflow.py
│   └── test_api_clients.py
├── fixtures/          # Test data
│   ├── sample_personas.json
│   └── sample_health_records.json
└── conftest.py        # Pytest configuration
```

### Writing Tests

```python
import pytest
from scripts.utils.semantic_tree import calculate_semantic_similarity

def test_semantic_similarity_identical_personas():
    """Test that identical personas have similarity score of 1.0"""
    persona = {
        "age": 28,
        "education": "Bachelor's",
        "income": 50000
    }

    score = calculate_semantic_similarity(persona, persona)

    assert score == pytest.approx(1.0, rel=0.01)

def test_semantic_similarity_different_ages():
    """Test age difference impact on similarity score"""
    persona1 = {"age": 25, "education": "Bachelor's", "income": 50000}
    persona2 = {"age": 45, "education": "Bachelor's", "income": 50000}

    score = calculate_semantic_similarity(persona1, persona2)

    assert score < 0.9  # Should be lower due to age difference
```

### Test Coverage

Aim for:
- **Critical paths:** 90%+ coverage
- **Core utilities:** 80%+ coverage
- **Overall project:** 60%+ coverage

Run coverage:
```bash
pytest --cov=scripts tests/
```

---

## Documentation

### Types of Documentation

1. **Code Comments**
   - Explain "why" not "what"
   - Document complex algorithms
   - Note assumptions and limitations

2. **Docstrings**
   - All public functions, classes, and modules
   - Google-style format
   - Include examples when helpful

3. **README Files**
   - Main README.md for project overview
   - Module-specific READMEs for complex components

4. **User Documentation**
   - Located in `docs/` directory
   - Include tutorials, guides, and references

### Documentation Standards

**Good Documentation Example:**
```python
def calculate_interview_cost(
    transcript: List[Dict],
    model: str,
    pricing: Dict[str, float]
) -> Dict[str, float]:
    """
    Calculate the cost of a completed interview based on token usage.

    This function estimates the cost by counting tokens in the transcript
    and applying the model's pricing structure. It accounts for both
    input and output tokens separately, as most providers charge
    different rates for each.

    Args:
        transcript: List of conversation turns with 'role' and 'content'
        model: Model identifier (e.g., 'claude-haiku-4-5')
        pricing: Dict with 'input' and 'output' prices per 1M tokens

    Returns:
        Dictionary containing:
            - total_cost: Total cost in USD
            - input_tokens: Number of input tokens
            - output_tokens: Number of output tokens
            - cost_breakdown: Detailed cost by input/output

    Example:
        >>> transcript = [
        ...     {"role": "user", "content": "Hello"},
        ...     {"role": "assistant", "content": "Hi there!"}
        ... ]
        >>> pricing = {"input": 1.0, "output": 5.0}  # Per 1M tokens
        >>> cost = calculate_interview_cost(transcript, "claude-haiku-4-5", pricing)
        >>> print(f"Total cost: ${cost['total_cost']:.4f}")
        Total cost: $0.0032

    Note:
        Token counting uses an approximation of 0.75 tokens per word.
        For exact costs, use the token counts returned by the AI API.
    """
    # Implementation
    pass
```

---

## Pull Request Process

### Before Submitting

1. **Update your branch**
   ```bash
   git checkout main
   git pull upstream main
   git checkout your-feature-branch
   git rebase main
   ```

2. **Run all checks**
   ```bash
   # Format code
   black scripts/

   # Lint
   pylint scripts/

   # Type check
   mypy scripts/

   # Run tests
   pytest tests/
   ```

3. **Update documentation**
   - Add/update docstrings
   - Update relevant docs/ files
   - Add entry to CHANGELOG.md

4. **Commit messages**
   Follow conventional commits format:
   ```
   type(scope): brief description

   Longer description if needed.

   Fixes #issue_number
   ```

   Types: feat, fix, docs, style, refactor, test, chore

   Example:
   ```
   feat(matching): add weighted semantic matching algorithm

   Implements a new semantic matching algorithm that weights different
   dimensions (age, education, income, etc.) to improve match quality.

   - Add calculate_weighted_similarity() function
   - Update matching algorithm to use weights
   - Add unit tests for weighted matching

   Fixes #42
   ```

### Submitting Pull Request

1. **Push your branch**
   ```bash
   git push origin your-feature-branch
   ```

2. **Create PR on GitHub**
   - Use descriptive title
   - Fill out the PR template
   - Link related issues
   - Add appropriate labels

3. **PR Description Template**
   ```markdown
   ## Description
   Brief summary of changes

   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Breaking change
   - [ ] Documentation update

   ## Testing
   - [ ] Unit tests added/updated
   - [ ] Integration tests added/updated
   - [ ] Manual testing completed

   ## Checklist
   - [ ] Code follows style guidelines
   - [ ] Self-review completed
   - [ ] Comments added for complex code
   - [ ] Documentation updated
   - [ ] No new warnings generated
   - [ ] Tests pass locally

   ## Related Issues
   Fixes #123
   Related to #456
   ```

### Review Process

1. **Automated Checks**
   - CI/CD pipeline runs tests
   - Code quality checks
   - Coverage reports

2. **Code Review**
   - At least one maintainer approval required
   - Address all comments
   - Make requested changes

3. **Merge**
   - Squash and merge (default)
   - Delete branch after merge

---

## Issue Reporting

### Before Creating an Issue

1. **Search existing issues**
   - Check if issue already reported
   - Add to existing discussion if relevant

2. **Gather information**
   - Error messages and stack traces
   - System information (OS, Python version)
   - Steps to reproduce

### Issue Templates

#### Bug Report

```markdown
**Describe the bug**
Clear and concise description of the bug.

**To Reproduce**
Steps to reproduce the behavior:
1. Run command '...'
2. With configuration '...'
3. See error

**Expected behavior**
What you expected to happen.

**Actual behavior**
What actually happened.

**Error messages**
```
Paste error messages or stack trace here
```

**Environment:**
 - OS: [e.g., Ubuntu 22.04]
 - Python version: [e.g., 3.11.5]
 - Gravidas version: [e.g., 1.2.0]
 - AI Provider: [e.g., Anthropic Claude]

**Additional context**
Any other relevant information.
```

#### Feature Request

```markdown
**Is your feature request related to a problem?**
Clear description of the problem.

**Describe the solution you'd like**
Clear and concise description of what you want to happen.

**Describe alternatives you've considered**
Other solutions or features you've considered.

**Additional context**
Any other context, mockups, or examples.
```

---

## Community and Communication

### Getting Help

- **GitHub Discussions:** For questions and general discussion
- **GitHub Issues:** For bug reports and feature requests
- **Documentation:** Check docs/ directory first

### Staying Updated

- Watch the repository for notifications
- Subscribe to release announcements
- Follow project roadmap in README.md

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Mentioned in release notes
- Credited in relevant documentation

Thank you for contributing to Gravidas!

---

**Last Updated:** 2025-11-16
**Version:** 1.2.3
