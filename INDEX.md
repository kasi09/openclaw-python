# OpenClaw Python Skills

> Python-based extensible skills framework for OpenClaw - Personal AI Assistant

Build custom Python skills that integrate with OpenClaw's AI assistant platform. This framework provides everything you need to create, test, and publish production-ready skills.

## Quick Links

- 📖 [Full Documentation](README.md)
- 🚀 [Quick Start Guide](README.md#quick-start)
- 🤝 [Contributing](CONTRIBUTING.md)
- 📝 [Changelog](CHANGELOG.md)
- 📦 [Project Structure](STRUCTURE.md)

## Features at a Glance

```
✓ Pure Python              ✓ Fully Typed             ✓ Well Tested
✓ Async Support            ✓ Easy to Extend          ✓ GitHub Ready
✓ Example Skills           ✓ CI/CD Included          ✓ MIT Licensed
```

## What This Does

This is a **skill framework** for the OpenClaw AI assistant - a personal AI that runs on your devices.

The framework lets you:

1. **Create custom skills** in Python
2. **Extend OpenClaw** with domain-specific functionality
3. **Package for GitHub** and share with the community
4. **Integrate with OpenClaw** using a simple async API

## Example: Text Analysis

```python
from openclaw_python_skill.skills import TextAnalyzerSkill
from openclaw_python_skill import SkillInput

skill = TextAnalyzerSkill()

# Analyze text statistics
result = await skill.execute(SkillInput(
    action="text_stats",
    parameters={"text": "Hello world!"}
))

# Result: word_count=2, sentence_count=1, char_count=12, ...
```

## Project Status

- ✅ **Functional** - Core framework and example skill working
- ✅ **Tested** - Comprehensive test suite included
- ✅ **Documented** - Full documentation and examples
- ✅ **GitHub Ready** - All files for publishing prepared
- 🚀 **Ready to Share** - Can be published to GitHub now

## Next Steps

1. **Review the code** - Everything is in `src/openclaw_python_skill/`
2. **Run the tests** - `pytest tests/`
3. **Try the example** - `python example.py`
4. **Create your skill** - Inherit from `Skill` class
5. **Publish to GitHub** - Push to your repository

## Requirements

- Python 3.9+
- pydantic >= 2.0
- httpx >= 0.24.0

Dev tools (optional):
- pytest for testing
- black for formatting
- ruff for linting
- mypy for type checking

## License

MIT License - See [LICENSE](LICENSE) for details
