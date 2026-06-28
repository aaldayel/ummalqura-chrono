# Frequently Asked Questions

## General

### What is the Umm al-Qura calendar?

The Umm al-Qura calendar is the official civil calendar of the Kingdom of Saudi Arabia, published by King Abdulaziz City for Science and Technology (KACST). It is a lunar (Hijri) calendar where each month is either 29 or 30 days, determined by official observation and pre-calculation.

### How is this different from other Islamic calendars?

Other libraries often use tabular (arithmetic) Islamic calendars with fixed leap-year cycles. The Umm al-Qura calendar uses the actual published month-length table from KACST, making it authoritative for Saudi Arabia and many Gulf countries.

### Is this library offline?

Yes. All conversion logic runs entirely offline. No network calls are ever made. The month-length data table is bundled with the library.

### What date range is supported?

- Hijri: 1318 AH – 1500 AH
- Gregorian: approximately 1900 CE – 2077 CE

### How accurate is the conversion?

The library uses the Fliegel & Van Flandern (1968) algorithm for Gregorian↔JDN conversion and the official KACST month-length table (via Microsoft `UmAlQuraCalendar`) for JDN↔Umm al-Qura conversion. CI runs `scripts/validate_microsoft_parity.py` against the reference data.

## Usage

### Why do I get different results than other libraries?

Other libraries may use tabular (arithmetic) Islamic calendars which can differ from the official Umm al-Qura calendar by 1–2 days. This library uses the authoritative per-year month-length flags from KACST, not a fixed 30-year tabular formula.

### Can I convert dates outside 1318–1500 AH?

No. The published official tables cover this range. Attempting to convert outside this range will produce an `OUT_OF_RANGE` error.

### How do I add my own locale?

See [CONTRIBUTING.md](../CONTRIBUTING.md#adding-a-locale). Create a JSON file in `data/locales/` following the existing schema.

### Does the library support timezone conversion?

The core conversion functions are timezone-independent. The REST API and CLI support timezones only for the `/today` endpoint. Date values never carry timezone information.

### Can I use a custom data file?

Yes. Pass a custom `dataPath` to the constructor:

```typescript
const cal = new UmmAlQuraCalendar({ dataPath: '/path/to/ummalqura-months.json' });
```

## Development

### How do I contribute?

See [CONTRIBUTING.md](../CONTRIBUTING.md) for development setup and guidelines.

### How are cross-language results verified?

A golden-values CSV file with 10,000+ test vectors is run against all language wrappers in CI. All implementations must produce identical results.

### Why independent implementations instead of shared native code?

Independent native ports provide the best developer experience: native types, native package managers, no FFI overhead. Cross-language parity tests guarantee correctness across all implementations.

### How do I add a new language wrapper?

1. Implement the core conversion functions (Gregorian↔JDN, JDN↔Umm al-Qura)
2. Load the shared `data/ummalqura-months.json` file
3. Implement full validation with all error codes
4. Pass golden-value parity tests
5. Add to CI pipeline

## Data

### How is the data file generated?

`scripts/generate_data.py` imports month-length flags from `scripts/UmAlQuraCalendar.cs.reference` (Microsoft .NET, sourced from KACST `UmAlQura.xls`). The SHA-256 checksum is committed alongside the data for integrity verification. Run `scripts/validate_microsoft_parity.py` to verify correctness.

### When is the data updated?

When KACST publishes new Umm al-Qura month data (typically annually), the data file can be updated. See [CONTRIBUTING.md](../CONTRIBUTING.md#extending-the-date-range).

### What does the data file contain?

Each entry contains:
- `hijri_year` and `hijri_month` (1-12)
- `month_length` (29 or 30 days)
- `first_day_jdn` (Julian Day Number of the 1st day of the month)

## REST API & CLI

### Is the API production-ready?

Yes. The API includes health checks, structured error responses, request validation, and is fully stateless. It can be self-hosted behind a reverse proxy.

### Does the API require a database?

No. The API is fully stateless and requires no external database or service.

### Can I batch convert dates?

Yes. The `/v1/convert/batch` endpoint accepts up to 1000 dates per request.
