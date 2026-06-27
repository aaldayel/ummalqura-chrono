# Kotlin Implementation (Beta)

Idiomatic Kotlin implementation of the Umm al-Qura calendar conversion library, published to [Maven Central](https://central.sonatype.com).

## Status

Beta — functional implementation available.

## Usage

```kotlin
import com.ummalqura.UmmAlQuraCalendar

val cal = UmmAlQuraCalendar(dataPath = null, defaultLocale = "en")
val result = cal.gregorianToHijri(2024, 3, 15, locale = null)
// result.output.year == 1445
```

See [Contributing](../../CONTRIBUTING.md) for development setup.
