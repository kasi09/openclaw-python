# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-19

### Added
- Initial release of OpenClaw Python Skills framework
- Base `Skill` class for creating custom skills
- `SkillInput` and `SkillOutput` Pydantic models for type-safe I/O
- `TextAnalyzerSkill` with three actions:
  - `text_stats` - Word/character/sentence counts and averages
  - `text_sentiment` - Basic sentiment classification
  - `text_patterns` - URL/email/phone number extraction
- Comprehensive test suite with pytest
- Example usage script
- Contributing guidelines
- GitHub Actions CI/CD workflow
- Setup scripts for Windows and Unix systems
- Full documentation with API reference

### Features
- Async/await support for skill execution
- Automatic error handling and timing measurement
- Type hints throughout for IDE support
- Pydantic validation for inputs/outputs
- Extensible architecture for custom skills

---

## Development

This project is in active development. See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.
