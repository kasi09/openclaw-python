# OpenClaw Python Skills - Project Structure

```
openclaw-python/
│
├── src/openclaw_python_skill/           # Main package
│   ├── __init__.py                      # Package exports (Skill, SkillInput, SkillOutput)
│   ├── skill.py                         # Base Skill abstract class
│   ├── models.py                        # Pydantic data models
│   │                                    #   - SkillInput: Input schema
│   │                                    #   - SkillOutput: Output schema
│   └── skills/                          # Built-in skills
│       ├── __init__.py
│       └── text_analyzer.py             # TextAnalyzerSkill
│           ├── text_stats()             # Word/char/sentence counts
│           ├── text_sentiment()         # Sentiment classification
│           └── text_patterns()          # URL/email/phone detection
│
├── tests/                               # Test suite
│   ├── conftest.py                      # pytest configuration
│   ├── test_base_skill.py               # Tests for Skill base class
│   └── test_skills.py                   # Tests for TextAnalyzerSkill
│
├── .github/
│   └── workflows/
│       └── tests.yml                    # CI/CD - Auto runs tests on push/PR
│
├── pyproject.toml                       # Project metadata & dependencies
├── requirements.txt                     # Runtime dependencies
├── requirements-dev.txt                 # Development dependencies
├── setup.sh                             # Setup script for macOS/Linux
├── setup.bat                            # Setup script for Windows
├── example.py                           # Usage examples
├── README.md                            # Documentation
├── CONTRIBUTING.md                      # Contributing guidelines
├── LICENSE                              # MIT License
└── .gitignore                           # Git ignore patterns
```

## Quick Start

### Install
```bash
pip install -e ".[dev]"
```

### Run Example
```bash
python example.py
```

### Run Tests
```bash
pytest tests/
pytest tests/ --cov=src/openclaw_python_skill
```

### Code Quality
```bash
black src tests          # Format
ruff check src tests     # Lint
mypy src                 # Type check
```

## How It Works

1. **Base Skill Class** - Abstract base class you inherit from
2. **Process Method** - Implement to handle different actions
3. **Execute Method** - Handles async execution, timing, error handling
4. **Models** - Pydantic models for input/output schema

## Example Usage

```python
from openclaw_python_skill.skills import TextAnalyzerSkill
from openclaw_python_skill import SkillInput

skill = TextAnalyzerSkill()

# Use it
result = await skill.execute(SkillInput(
    action="text_stats",
    parameters={"text": "Hello world!"}
))
```

## Ready for GitHub

- [x] Comprehensive documentation (README.md)
- [x] Contributing guidelines (CONTRIBUTING.md)
- [x] MIT License
- [x] Example code and usage
- [x] Full test suite with pytest
- [x] Type hints throughout
- [x] CI/CD workflow (GitHub Actions)
- [x] Professional project structure
- [x] pyproject.toml for modern Python packaging
- [x] .gitignore configured
- [x] Requirements files
- [x] Setup scripts for easy installation
