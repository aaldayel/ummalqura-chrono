# Contributing to Umm al-Qura Calendar

Thank you for your interest in contributing! This document provides guidelines
for contributing to the Umm al-Qura Calendar Conversion Library.

## Code of Conduct

This project adheres to the [Contributor Covenant Code of Conduct](CODE_OF_CONDUCT.md).
By participating, you are expected to uphold this code.

## Development Setup

### Prerequisites

- Node.js >= 18 (for JavaScript/TypeScript)
- Python >= 3.8 (for Python)
- PHP >= 8.0 (for PHP)
- Go >= 1.21 (for Go)

### Getting Started

```bash
# Clone the repository
git clone https://github.com/ummalqura/ummalqura-chrono.git
cd ummalqura-chrono

# JavaScript/TypeScript
cd packages/js
npm install
npm test

# Python
cd packages/python
pip install -e ".[dev]"
pytest

# PHP
cd packages/php
composer install
./vendor/bin/phpunit

# Go
cd packages/go
go test ./...
```

## Project Structure

```
ummalqura/
├── data/                    # Authoritative data files
│   ├── ummalqura-months.json # Month-length table
│   ├── ummalqura-months.sha256
│   └── locales/              # Locale files
├── packages/                 # Language implementations
│   ├── js/                   # JavaScript/TypeScript (npm)
│   ├── python/               # Python (PyPI)
│   ├── php/                  # PHP (Packagist)
│   └── go/                   # Go
├── api/                      # REST API
├── cli/                      # CLI tool
├── playground/               # Web playground (PWA)
├── tests/                    # Shared tests
│   ├── golden/               # Golden-value test vectors
│   └── cross-language/       # Parity test runner
├── scripts/                  # Utility scripts
├── benchmarks/               # Performance benchmarks
└── docs/                     # Documentation
```

## Branching Model

- `main` — Stable, releasable code
- `develop` — Integration branch for features
- Feature branches — `feature/description` branched from `develop`
- Hotfix branches — `hotfix/description` branched from `main`

## Commit Message Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

```
type(scope): description

feat(js): add batch conversion support
fix(python): correct leap year calculation
docs(readme): update installation instructions
test(golden): add boundary test cases
```

Types: `feat`, `fix`, `docs`, `test`, `refactor`, `chore`, `perf`, `ci`

## Pull Request Process

1. Fork the repository and create a feature branch
2. Ensure your code follows the existing style conventions
3. Add tests for new functionality
4. Ensure all tests pass (`npm test`, `pytest`, etc.)
5. Update documentation if needed
6. Run linters (`npm run lint`, `ruff check .`)
7. Submit a PR against the `develop` branch
8. Ensure CI checks pass

### PR Checklist

- [ ] Code follows project conventions
- [ ] Tests added and passing
- [ ] Documentation updated
- [ ] No breaking changes without prior discussion
- [ ] Cross-language parity maintained (for algorithm changes)
- [ ] Locale files validated (for locale changes)

## Adding a Locale

1. Copy an existing locale file from `data/locales/` (e.g., `en.json`)
2. Translate all string fields
3. Set the correct `code` (BCP 47 language tag) and `rtl` flag
4. Run `python scripts/validate_locales.py` to validate
5. Submit a PR

## Extending the Date Range

When KACST (King Abdulaziz City for Science and Technology) publishes new
Umm al-Qura month data:

1. Update `data/ummalqura-months.json` with the new month entries
2. Run `python scripts/generate_data.py` to regenerate with new bounds
3. Update `data/ummalqura-months.sha256` (generated automatically)
4. Run `python scripts/generate_golden_values.py` to refresh test vectors
5. Verify golden value tests pass in all language wrappers
6. Update `CHANGELOG.md` with the data version bump
7. Submit a PR with the tag `data-update`

## Cross-Language Parity

All language wrappers must produce identical results for the same inputs.
To verify:

```bash
python tests/cross-language/run_parity_tests.py
```

## Getting Help

- Open a [GitHub Discussion](https://github.com/ummalqura/ummalqura-chrono/discussions) for questions
- Open a [GitHub Issue](https://github.com/ummalqura/ummalqura-chrono/issues) for bugs
- See [SECURITY.md](SECURITY.md) for vulnerability reporting
