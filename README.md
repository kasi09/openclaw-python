# OpenClaw Python Skills

[![Tests](https://github.com/kasi09/openclaw-python/actions/workflows/tests.yml/badge.svg)](https://github.com/kasi09/openclaw-python/actions/workflows/tests.yml)
[![GitHub license](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Code style: ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)

Python-based extensible skills framework for [OpenClaw](https://openclaw.ai) - Personal AI Assistant.

This package provides a framework for building custom Python skills that integrate seamlessly with OpenClaw, enabling text analysis, math evaluation, web scraping, and custom integrations.

## Features

- **Skill Framework** - Abstract base class with async execution, timing, and error handling
- **Skill Registry** - Thread-safe registry for skill discovery and management
- **Skill Pipeline** - Chain multiple skills together with data mapping and fail-fast execution
- **4 Built-in Skills** - Text analysis, math, web fetching, and web scraping
- **Well-tested** - 109 tests, 96% code coverage
- **Type-safe** - Pydantic v2 models, mypy checked

## Installation

```bash
git clone https://github.com/kasi09/openclaw-python.git
cd openclaw-python
pip install -e ".[dev]"
```

For web scraping with BeautifulSoup:

```bash
pip install -e ".[scraper]"
```

### Requirements

- Python 3.9+
- pydantic >= 2.0
- httpx >= 0.24.0
- beautifulsoup4 >= 4.12.0 (optional, for `WebScraperSkill`)

## Quick Start

```python
import asyncio
from openclaw_python_skill import SkillInput
from openclaw_python_skill.skills import MathSkill

async def main():
    skill = MathSkill()

    result = await skill.execute(SkillInput(
        action="evaluate",
        parameters={"expression": "sqrt(16) + pi * 2"}
    ))
    print(result.result)  # {'expression': 'sqrt(16) + pi * 2', 'result': 10.283...}

asyncio.run(main())
```

## Available Skills

### MathSkill

Safe mathematical evaluation, unit conversion, and statistics.

```python
from openclaw_python_skill.skills import MathSkill
skill = MathSkill()
```

| Action | Parameters | Description |
|--------|-----------|-------------|
| `evaluate` | `expression` | Evaluate math expressions safely via `ast.parse()` (supports +, -, *, /, **, sqrt, sin, cos, log, pi, e, ...) |
| `convert_units` | `value`, `from_unit`, `to_unit` | Convert between units (length, weight, temperature, time) |
| `statistics` | `numbers`, `operation?` | Compute mean, median, stdev, variance, min, max, sum (default: summary) |

### TextAnalyzerSkill

Text processing and analysis.

```python
from openclaw_python_skill.skills import TextAnalyzerSkill
skill = TextAnalyzerSkill()
```

| Action | Parameters | Description |
|--------|-----------|-------------|
| `text_stats` | `text` | Word count, character count, sentence count, averages |
| `text_sentiment` | `text` | Basic sentiment classification (positive/negative/neutral) |
| `text_patterns` | `text` | Extract URLs, emails, and phone numbers |

### WebFetchSkill

Basic web fetching using httpx and regex (no external HTML parser needed).

```python
from openclaw_python_skill.skills import WebFetchSkill
skill = WebFetchSkill()
```

| Action | Parameters | Description |
|--------|-----------|-------------|
| `fetch` | `url`, `headers?`, `timeout?` | Fetch URL and return status, headers, content |
| `extract_links` | `url` | Extract all `<a href>` links via regex |
| `extract_text` | `url` | Strip HTML tags and return plain text |

### WebScraperSkill

Advanced web scraping with BeautifulSoup (requires `beautifulsoup4`).

```python
from openclaw_python_skill.skills import WebScraperSkill
skill = WebScraperSkill()
```

| Action | Parameters | Description |
|--------|-----------|-------------|
| `extract_meta` | `url` | Extract title, meta description, and Open Graph tags |
| `extract_elements` | `url`, `selector` | Extract elements matching a CSS selector |

## Skill Registry

Thread-safe registry for managing and discovering skills.

```python
from openclaw_python_skill import SkillRegistry
from openclaw_python_skill.skills import MathSkill, TextAnalyzerSkill

registry = SkillRegistry()
registry.register(MathSkill())
registry.register(TextAnalyzerSkill())

# Lookup
skill = registry.get("math")
print(registry.skill_names())  # ['math', 'text-analyzer']
```

## Skill Pipeline

Chain skills together for multi-step processing.

```python
from openclaw_python_skill import SkillPipeline
from openclaw_python_skill.skills import TextAnalyzerSkill, MathSkill

text_skill = TextAnalyzerSkill()

pipeline = (
    SkillPipeline(name="word-count-pipeline")
    .add_step(skill=text_skill, action="text_stats")
)

result = await pipeline.execute({"text": "Hello world! How are you?"})
print(result.final_result)  # {'word_count': 5, ...}
print(result.metadata)      # {'pipeline_name': '...', 'total_execution_time_ms': ...}
```

Pipelines support:
- **Fluent chaining** with `.add_step()`
- **Data mapping** between steps via `mapper` functions
- **Fail-fast execution** - stops on first error
- **Registry-based** or direct skill references
- **Detailed metadata** with per-step timing

## Creating Custom Skills

```python
from typing import Any
from openclaw_python_skill import Skill

class MySkill(Skill):
    def __init__(self):
        super().__init__(name="my-skill", version="1.0.0")

    def process(self, action: str, parameters: dict[str, Any]) -> dict[str, Any]:
        if action == "greet":
            name = parameters.get("name", "World")
            return {"greeting": f"Hello, {name}!"}
        raise ValueError(f"Unknown action: {action}")
```

## Development

```bash
# Install dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Format and lint
ruff format src tests
ruff check src tests

# Type checking
mypy src
```

## Project Structure

```
openclaw-python/
├── src/openclaw_python_skill/
│   ├── __init__.py          # Package exports
│   ├── skill.py             # Base Skill ABC
│   ├── models.py            # Pydantic models (SkillInput, SkillOutput, Pipeline*)
│   ├── registry.py          # SkillRegistry + global registry
│   ├── pipeline.py          # SkillPipeline
│   └── skills/
│       ├── __init__.py
│       ├── text_analyzer.py # TextAnalyzerSkill
│       ├── math_skill.py    # MathSkill
│       ├── web_fetch.py     # WebFetchSkill
│       └── web_scraper.py   # WebScraperSkill (requires beautifulsoup4)
├── tests/
│   ├── test_base_skill.py
│   ├── test_math_skill.py
│   ├── test_pipeline.py
│   ├── test_registry.py
│   ├── test_skills.py
│   ├── test_web_fetch.py
│   └── test_web_scraper.py
├── .github/workflows/
│   └── tests.yml            # CI: Python 3.9-3.12
├── pyproject.toml
└── LICENSE
```

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Links

- [Report Issues](https://github.com/kasi09/openclaw-python/issues)
- [OpenClaw Documentation](https://docs.openclaw.ai)
