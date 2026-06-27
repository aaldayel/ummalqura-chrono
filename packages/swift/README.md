# Swift Implementation (Beta)

Idiomatic Swift implementation of the Umm al-Qura calendar conversion library, published via [Swift Package Manager](https://swift.org/package-manager/).

## Status

Beta — functional implementation available.

## Usage

```swift
import UmmAlQura

let cal = try UmmAlQuraCalendar(dataPath: nil, defaultLocale: "en")
let result = try cal.gregorianToHijri(2024, 3, 15, locale: nil)
// result.output.year == 1445
```

See [Contributing](../../CONTRIBUTING.md) for development setup.
