# Architecture

## Design Philosophy

The Umm al-Qura Calendar library follows these core principles:

1. **Deterministic correctness first** — All conversions produce identical results across all implementations
2. **Pure-function core** — No side effects, no I/O, no global mutable state in conversion logic
3. **Data-driven** — A single versioned data file is the source of truth for all calculations
4. **Language-portable** — Identical algorithms implemented idiomatically in each language

## System Architecture

```
                    ┌──────────────────────────────────┐
                    │     Authoritative Data File        │
                    │  data/ummalqura-months.json        │
                    │  (versioned, SHA-256 checksummed)  │
                    └──────────┬───────────────────────┘
                               │
          ┌────────────────────┼────────────────────┐
          │                    │                    │
          ▼                    ▼                    ▼
   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
   │  JS/TS Core  │    │  Python Core │    │  Go Core     │ ...
   │  (packages/  │    │  (packages/  │    │  (packages/  │
   │   js/)       │    │   python/)   │    │   go/)       │
   └──────┬───────┘    └──────┬───────┘    └──────┬───────┘
          │                   │                    │
          └───────────────────┼────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Golden Values   │
                    │  Cross-Language  │
                    │  Parity Tests    │
                    └─────────────────┘
```

## Conversion Pipeline

All conversions follow a strict two-step pipeline:

```
Gregorian  ←→  Julian Day Number (JDN)  ←→  Umm al-Qura (Hijri)
```

Direct Gregorian ↔ Hijri mapping without JDN as an intermediate is **prohibited**. JDN serves as the universal intermediate representation.

### Step 1: Gregorian ↔ JDN

Uses the Fliegel & Van Flandern (1968) algorithm for proleptic Gregorian calendar:

- `gregorian_to_jdn(year, month, day) → jdn`
- `jdn_to_gregorian(jdn) → (year, month, day)`

**Complexity**: O(1) time and space.

### Step 2: JDN ↔ Umm al-Qura

Uses the authoritative month-length table via binary search:

- `hijri_to_jdn(year, month, day) → jdn` — O(1) with hash table lookup
- `jdn_to_hijri(jdn) → (year, month, day)` — O(log n) binary search

## Wrapper Strategy

**Chosen: Option B — Independent native ports**

Each language has an independent, idiomatic implementation of the same algorithms. All wrappers share:

- The same conversion algorithms
- The same data file (symlinked or copied at build time)
- The same golden-value test vectors

**Rationale**: Independent native ports provide the best developer experience (native types, native package managers, no FFI overhead) while cross-language parity tests guarantee correctness.

## Package Structure

```
ummalqura/
├── data/              # Single source of truth
│   ├── ummalqura-months.json
│   ├── ummalqura-months.sha256
│   └── locales/
├── packages/          # Language implementations
│   ├── js/            # npm package
│   ├── python/        # PyPI package
│   ├── php/           # Packagist package
│   ├── go/            # Go module
│   ├── dotnet/        # NuGet package (planned)
│   ├── java/          # Maven package (planned)
│   ├── rust/          # crates.io (planned)
│   ├── dart/          # pub.dev (planned)
│   ├── swift/         # SPM (planned)
│   └── kotlin/        # Maven Central (planned)
├── api/               # REST API (Express.js)
├── cli/               # CLI tool
├── playground/        # Web PWA
├── tests/             # Cross-language tests
│   ├── golden/        # Golden-value CSV
│   └── cross-language/ # Parity test runner
├── benchmarks/        # Performance benchmarks
└── docs/              # Documentation
```

## Data Flow

1. **Data Generation**: `scripts/generate_data.py` produces `ummalqura-months.json` from the KACST algorithm
2. **Integrity**: SHA-256 checksum is committed alongside the data file
3. **Loading**: Each language wrapper loads the JSON data file at initialization
4. **Indexing**: Month entries are indexed by key (`year-month`) for O(1) lookup and sorted by JDN for binary search
5. **Conversion**: All conversion calls go through the JDN intermediate

## Error Handling

All errors follow a structured format:

```json
{
  "error_code": "INVALID_DAY",
  "message": "Day 30 does not exist in Hijri month 1445-09, which has 29 days.",
  "field": "day",
  "value": 30
}
```

Error codes are a closed enumeration: `INVALID_DAY`, `INVALID_MONTH`, `INVALID_YEAR`, `OUT_OF_RANGE`, `UNSUPPORTED_CALENDAR`, `INVALID_TIMEZONE`, `MALFORMED_INPUT`.

No library function silently corrects invalid input — all errors are explicitly returned or thrown.
