# OpenClaw Python Skills

[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Python-based extensible skills framework for [OpenClaw](https://openclaw.ai) - Personal AI Assistant.

This package provides a framework for building custom Python skills that integrate seamlessly with OpenClaw, enabling advanced text analysis, data processing, and custom integrations.

## Features

- 🐍 **Pure Python** - No Node.js dependency, all Python
- 🔌 **Extensible** - Easy base class to create custom skills
- 📊 **Example Skill** - Text analyzer with statistics, sentiment analysis, and pattern detection
- 🧪 **Well-tested** - Comprehensive test suite with pytest
- 📦 **Production-ready** - Type hints, error handling, async support
- 📚 **Documented** - Clear docstrings and examples

## Installation

### From source

```bash
git clone https://github.com/kasi09/openclaw-python.git
cd openclaw-python
pip install -e ".[dev]"
```

### Requirements

- Python 3.9+
- pydantic >= 2.0
- httpx >= 0.24.0

## Quick Start

### Using the Text Analyzer Skill

```python
import asyncio
from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import TextAnalyzerSkill

async def main():
    skill = TextAnalyzerSkill()
    
    # Analyze text statistics
    result = await skill.execute(SkillInput(
        action="text_stats",
        parameters={"text": "Hello world! This is a test."}
    ))
    
    print(result.model_dump_json(indent=2))

asyncio.run(main())
```

### Output

```json
{
  "success": true,
  "result": {
    "word_count": 5,
    "char_count": 31,
    "sentence_count": 2,
    "avg_word_length": 4.8,
    "avg_words_per_sentence": 2.5
  },
  "error": null,
  "metadata": {
    "execution_time_ms": 1.23,
    "skill": "text-analyzer",
    "version": "1.0.0"
  }
}
```

## Creating Custom Skills

1. **Create a skill class** inheriting from `Skill`:

```python
from openclaw_python_skill import Skill

class MySkill(Skill):
    def __init__(self):
        super().__init__(name="my-skill", version="1.0.0")
    
    def process(self, action: str, parameters: dict) -> dict:
        if action == "my_action":
            return {"result": "success"}
        raise ValueError(f"Unknown action: {action}")
```

2. **Implement the `process` method** to handle different actions

3. **Use with OpenClaw**:

```python
skill = MySkill()
output = await skill.execute(SkillInput(
    action="my_action",
    parameters={"param1": "value"}
))
```

## Available Skills

### TextAnalyzerSkill

Text processing with three main actions:

- **`text_stats`** - Word count, character count, sentence count, averages
- **`text_sentiment`** - Basic sentiment classification (positive/negative/neutral)
- **`text_patterns`** - Extract URLs, emails, and phone numbers

Example:

```python
# Sentiment analysis
result = await skill.execute(SkillInput(
    action="text_sentiment",
    parameters={"text": "I love this! It's amazing!"}
))

# Pattern detection
result = await skill.execute(SkillInput(
    action="text_patterns",
    parameters={"text": "Email: test@example.com, URL: https://example.com"}
))
```

## Development

### Setup development environment

```bash
pip install -e ".[dev]"
```

### Run tests

```bash
pytest                    # Run all tests
pytest --cov             # With coverage report
pytest -v                # Verbose output
```

### Code formatting & linting

```bash
black src tests           # Format code
ruff check src tests      # Lint code
mypy src                  # Type checking
```

### Run all quality checks

```bash
make lint    # If you have make installed
# or
black src tests && ruff check src tests && mypy src && pytest --cov
```

## Project Structure

```
openclaw-python/
├── src/openclaw_python_skill/     # Main package
│   ├── __init__.py                 # Package exports
│   ├── skill.py                    # Base Skill class
│   ├── models.py                   # Pydantic models (SkillInput, SkillOutput)
│   └── skills/                     # Built-in skills
│       ├── __init__.py
│       └── text_analyzer.py        # Text analysis skill
├── tests/                          # Test suite
│   └── test_skills.py
├── pyproject.toml                  # Project configuration
├── requirements.txt                # Runtime dependencies
├── requirements-dev.txt            # Development dependencies
├── README.md                       # This file
└── LICENSE                         # MIT License
```

## Testing

This project includes comprehensive tests:

```bash
# Run tests
pytest tests/

# With coverage
pytest tests/ --cov=src/openclaw_python_skill

# Watch mode (requires pytest-watch)
ptw tests/
```

## Integration with OpenClaw

To use these skills with OpenClaw:

1. **Install the package** in your OpenClaw environment
2. **Register the skill** with OpenClaw's skill registry
3. **Use in prompts** - The AI can call your skill actions

Example in OpenClaw prompt:

```
@text-analyzer analyze this text for statistics:
"Hello world! How are you today?"
```

## API Reference

### Skill Base Class

```python
class Skill(ABC):
    async def execute(skill_input: SkillInput) -> SkillOutput
    def process(action: str, parameters: dict) -> dict
    def describe() -> dict
```

### SkillInput Model

```python
class SkillInput(BaseModel):
    action: str                          # Action to perform
    parameters: Dict[str, Any]           # Action parameters
    context: Optional[Dict[str, Any]]    # Optional execution context
```

### SkillOutput Model

```python
class SkillOutput(BaseModel):
    success: bool                        # Execution success status
    result: Optional[Dict[str, Any]]     # Result data
    error: Optional[str]                 # Error message
    metadata: Dict[str, Any]             # Execution metadata
```

## Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/my-skill`)
3. Make your changes and add tests
4. Format code with `black` and lint with `ruff`
5. Ensure all tests pass
6. Submit a pull request

## Roadmap

- [ ] More built-in skills (Math, Data Processing, Web Scraping)
- [ ] Async/await patterns for I/O-bound skills
- [ ] Skill marketplace integration
- [ ] Performance monitoring and metrics
- [ ] Advanced error handling and retry logic

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Support

- 📖 [OpenClaw Documentation](https://docs.openclaw.ai)
- 💬 [Discord Community](https://discord.gg/clawd)
- 🐛 [Report Issues](https://github.com/kasi09/openclaw-python/issues)
- 💡 [Discussions](https://github.com/kasi09/openclaw-python/discussions)

## Related Projects

- [OpenClaw Main](https://github.com/openclaw/openclaw) - Core OpenClaw project
- [OpenClaw Extensions](https://github.com/openclaw/openclaw/tree/main/extensions) - Official extensions
- [ClawHub](https://clawhub.com) - Skill registry

---

**Made with ❤️ for the OpenClaw community**
