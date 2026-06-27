# Rust Implementation (Planned)

This package will provide an idiomatic Rust implementation of the Umm al-Qura
calendar conversion library, published to [crates.io](https://crates.io).

## Status

🚧 In development — not yet available.

## Planned API

```rust
use ummalqura::UmmAlQuraCalendar;

let cal = UmmAlQuraCalendar::new(None, "en")?;
let result = cal.gregorian_to_hijri(2024, 3, 15, None)?;
// result.output.year == 1445
```

See [Contributing](../../CONTRIBUTING.md) if you'd like to help build this package.
