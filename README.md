# UmmAlQura-Chrono: Umm al-Qura Calendar Conversion Library

[![CI](https://github.com/aaldayel/ummalqura-chrono/actions/workflows/ci.yml/badge.svg)](https://github.com/aaldayel/ummalqura-chrono/actions/workflows/ci.yml)
[![npm version](https://badge.fury.io/js/ummalqura-chrono.svg)](https://www.npmjs.com/package/ummalqura-chrono)
[![PyPI version](https://badge.fury.io/py/ummalqura-chrono.svg)](https://pypi.org/project/ummalqura-chrono/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A **production-grade, fully offline, open-source** calendar conversion library for accurate and deterministic conversion between Gregorian and Umm al-Qura Hijri calendars.

## Overview

The Umm al-Qura calendar is the official civil calendar of the Kingdom of Saudi Arabia, published by King Abdulaziz City for Science and Technology (KACST). This library provides:

- **Accurate conversion** between Gregorian and Umm al-Qura calendars
- **Offline operation** — no network calls required
- **Cross-platform support** — JavaScript, Python, PHP, Go, and more
- **Production-ready** — suitable for government, financial, healthcare, and general-purpose use

## Supported Date Range

| Calendar | Range |
|----------|-------|
| Hijri | 1318 AH – 1500 AH |
| Gregorian | 1900 CE – 2077 CE |

## Quick Start

### JavaScript / TypeScript

```bash
npm install ummalqura-chrono
```

```typescript
import { UmmAlQuraCalendar } from 'ummalqura-chrono';

const calendar = new UmmAlQuraCalendar();

// Gregorian to Hijri
const result = calendar.gregorianToHijri(2024, 3, 15);
console.log(result.output); // { year: 1445, month: 9, day: 5, calendar: 'hijri-ummalqura' }

// Hijri to Gregorian
const result2 = calendar.hijriToGregorian(1445, 9, 5);
console.log(result2.output); // { year: 2024, month: 3, day: 15, calendar: 'gregorian' }
```

### Python

```bash
pip install ummalqura-chrono
```

```python
from ummalqura import UmmAlQuraCalendar

calendar = UmmAlQuraCalendar()

# Gregorian to Hijri
result = calendar.gregorian_to_hijri(2024, 3, 15)
print(result.output)  # HijriDate(year=1445, month=9, day=5, calendar='hijri-ummalqura')

# Hijri to Gregorian
result2 = calendar.hijri_to_gregorian(1445, 9, 5)
print(result2.output)  # GregorianDate(year=2024, month=3, day=15, calendar='gregorian')
```

### PHP

```bash
composer require ummalqura-chrono/ummalqura-chrono
```

```php
use UmmAlQura\UmmAlQuraCalendar;

$calendar = new UmmAlQuraCalendar();

// Gregorian to Hijri
$result = $calendar->gregorianToHijri(2024, 3, 15);
echo $result->getOutput()->getYear(); // 1445
```

### Go

```bash
go get github.com/ummalqura/ummalqura-chrono-go
```

```go
import "github.com/ummalqura/ummalqura-chrono-go"

cal, _ := ummalqura.NewCalendar("", "en")
result, _ := cal.GregorianToHijri(2024, 3, 15, "")
// result.Output.Year == 1445
```

## API Reference

### Constructor

```typescript
new UmmAlQuraCalendar(config?: {
  dataPath?: string;      // Path to custom data file
  defaultLocale?: string; // Default locale (default: 'en')
})
```

### Methods

| Method | Description |
|--------|-------------|
| `gregorianToHijri(year, month, day, options?)` | Convert Gregorian to Hijri |
| `hijriToGregorian(year, month, day, options?)` | Convert Hijri to Gregorian |
| `validateGregorianDate(year, month, day)` | Validate Gregorian date |
| `validateHijriDate(year, month, day)` | Validate Hijri date |
| `getDayOfWeek(jdn)` | Get day of week from JDN |
| `getGregorianMonth(year, month, locale?)` | Get all days in a Gregorian month |
| `getHijriMonth(year, month, locale?)` | Get all days in a Hijri month |
| `batchGregorianToHijri(dates, options?)` | Batch convert Gregorian to Hijri |
| `batchHijriToGregorian(dates, options?)` | Batch convert Hijri to Gregorian |

## REST API

```bash
cd api
npm install
npm start
```

API documentation is available at `http://localhost:3000/docs`.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/convert` | Convert a single date |
| `POST` | `/v1/convert/batch` | Batch convert dates |
| `GET` | `/v1/today` | Get today's date |
| `GET` | `/v1/calendar/{calendar}/{year}/{month}` | Get month calendar |
| `GET` | `/v1/validate` | Validate a date |
| `GET` | `/v1/day-of-week` | Get day of week |
| `GET` | `/v1/health` | Health check |

## CLI

```bash
# Install globally
npm install -g ummalqura-cli

# Convert date
uaq convert --from gregorian --to hijri --date 2024-03-15

# Get today's date
uaq today --timezone Asia/Riyadh

# Validate date
uaq validate --calendar hijri --date 1445-09-05

# Show calendar
uaq calendar --calendar hijri --year 1445 --month 9
```

## Supported Languages

| Language | Status | Package |
|----------|--------|---------|
| JavaScript / TypeScript | Stable | npm |
| Python | Stable | PyPI |
| PHP | Stable | Packagist |
| Go | Stable | pkg.go.dev |
| .NET (C#) | Beta | NuGet (planned) |
| Java | Beta | Maven Central (planned) |
| Kotlin | Beta | Maven Central (planned) |
| Dart / Flutter | Alpha | pub.dev (planned) |
| Swift | Alpha | Swift Package Manager (planned) |
| Rust | Planned | crates.io (planned) |

## Internationalization

Locale files for month names, day names, and other human-readable strings are
stored in `data/locales/`. Currently supported:

| Code | Language |
|------|----------|
| `ar` | Arabic |
| `en` | English |
| `fr` | French |
| `tr` | Turkish |
| `ms` | Malay |
| `id` | Indonesian |
| `fa` | Persian |
| `es` | Spanish |
| `pt` | Portuguese |
| `de` | German |
| `ja` | Japanese |
| `zh-Hans` | Chinese (Simplified) |
| `ko` | Korean |
| `ru` | Russian |
| `ur` | Urdu |

To add a new locale, see [CONTRIBUTING.md](CONTRIBUTING.md#adding-a-locale).

## Data Source

The month-length table is imported from the official Saudi UmAlQura tables via Microsoft's `UmAlQuraCalendar` reference implementation (sourced from KACST `UmAlQura.xls`). The data file includes a version identifier and SHA-256 checksum for integrity verification. Regenerate with `python scripts/generate_data.py` and validate with `python scripts/validate_microsoft_parity.py`.

## Testing

### JavaScript

```bash
cd packages/js
npm test
```

### Python

```bash
cd packages/python
pytest
```

### PHP

```bash
cd packages/php
composer install
./vendor/bin/phpunit
```

### Go

```bash
cd packages/go
go test ./...
```

### Cross-Language Parity

All language wrappers must produce identical results. Golden-value tests run in CI:

```bash
python tests/cross-language/run_parity_tests.py
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, branching model, and PR guidelines.

## Security

See [SECURITY.md](SECURITY.md) for vulnerability reporting.

## License

MIT License — see [LICENSE](LICENSE) for details.

## Acknowledgments

- King Abdulaziz City for Science and Technology (KACST) for the official Umm al-Qura calendar data
- Microsoft for the `UmmAlQuraCalendar` reference implementation
