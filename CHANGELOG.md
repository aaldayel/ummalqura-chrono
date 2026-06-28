# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-01

### Added
- Core conversion algorithm (Gregorian ↔ JDN ↔ Hijri)
- JavaScript/TypeScript wrapper with full API
- Python wrapper with full API
- REST API with OpenAPI 3.1 specification
- CLI tool with subcommands
- Umm al-Qura month-length data table (1300-1700 AH)
- Golden-value test CSV (10,000+ test vectors)
- Locale files for Arabic and English
- CI/CD pipeline with GitHub Actions
- Comprehensive documentation

### Features
- Pure-function, stateless, deterministic conversion
- Date validation for both calendars
- Day of week calculation
- Month calendar generation
- Batch conversion support
- Multi-language support (Arabic, English)
- Offline operation - no network calls required

### Technical Details
- Supported Hijri range: 1300-1700 AH
- Supported Gregorian range: ~1882-2277 CE
- Data file versioning with SHA-256 checksum
- Cross-language parity testing
- 100% line and branch coverage target

## [Unreleased]

### Fixed
- Replace tabular Hijri data with official KACST month-length flags (Microsoft `UmAlQuraCalendar` reference, 1318–1500 AH)
- Add upper-bound validation to `jdnToHijri` across all language implementations
- Fix Go package compilation errors
- Bundle data file in Python and JavaScript packages
- Fix JavaScript golden-value test CSV path
- Remove incorrect hardcoded golden-value reference rows

### Added
- `scripts/validate_microsoft_parity.py` for authoritative correctness checks in CI
- `scripts/UmAlQuraCalendar.cs.reference` as the data source snapshot
- .NET (C#) wrapper with full API
- Java wrapper with full API
- Kotlin wrapper with full API
- Go wrapper with full API
- PHP wrapper with full API
- Dart wrapper (core implementation)
- Swift wrapper (core implementation)
- Rust wrapper (planned, stub only)
- Additional locale files (French, Turkish, Malay, Indonesian, Persian, Spanish, Portuguese, German, Japanese, Chinese, Korean, Russian, Urdu)
- Cross-language parity test framework
- REST API with OpenAPI 3.1 specification
- CLI tool with subcommands
- Performance benchmarks framework (data pending)
