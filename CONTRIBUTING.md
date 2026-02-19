# Contributing to OpenClaw Python Skills

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing.

## Code of Conduct

Please be respectful, inclusive, and professional in all interactions.

## Getting Started

1. Fork the repository
2. Clone your fork locally
3. Create a virtual environment and activate it
4. Install development dependencies: `pip install -e ".[dev]"`

## Development Workflow

### Creating a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### Writing Code

- Follow PEP 8 style guidelines
- Use type hints for all functions
- Write comprehensive docstrings
- Keep functions focused and testable

### Running Tests

```bash
# Run all tests
pytest

# With coverage
pytest --cov=src/openclaw_python_skill

# Specific test file
pytest tests/test_skills.py
```

### Code Quality Checks

```bash
# Format code
black src tests

# Lint
ruff check src tests

# Type checking
mypy src
```

## Submitting Changes

1. Ensure all tests pass
2. Ensure code is formatted with `black`
3. Ensure no linting issues with `ruff`
4. Ensure type checking passes with `mypy`
5. Commit with clear, descriptive messages
6. Push to your fork
7. Submit a pull request to the main branch

### Pull Request Guidelines

- Reference related issues
- Describe the changes clearly
- Include any new tests
- Update documentation if needed
- Keep PRs focused on a single feature/fix

## Creating a New Skill

To contribute a new skill:

1. Create a new file in `src/openclaw_python_skill/skills/`
2. Inherit from the `Skill` base class
3. Implement the `process` method
4. Add comprehensive tests in `tests/`
5. Update `src/openclaw_python_skill/skills/__init__.py`
6. Update README with usage examples

Example:

```python
from openclaw_python_skill import Skill

class MySkill(Skill):
    """Description of your skill."""
    
    def __init__(self):
        super().__init__(name="my-skill", version="1.0.0")
    
    def process(self, action: str, parameters: dict) -> dict:
        if action == "my_action":
            # Implement your logic
            return {"result": "value"}
        raise ValueError(f"Unknown action: {action}")
```

## Reporting Issues

- Use GitHub Issues to report bugs
- Provide clear descriptions and steps to reproduce
- Include Python version and environment details
- Attach relevant code samples or error messages

## Questions or Discussions

- Use GitHub Discussions for questions
- Join the OpenClaw Discord for community support

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

Thank you for contributing to OpenClaw Python Skills! 🎉
