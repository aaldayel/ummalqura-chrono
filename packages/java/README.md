# Java Implementation (Beta)

Idiomatic Java implementation of the Umm al-Qura calendar conversion library, published to [Maven Central](https://central.sonatype.com).

## Status

Beta — functional implementation available.

## Usage

```java
import com.ummalqura.UmmAlQuraCalendar;

UmmAlQuraCalendar cal = new UmmAlQuraCalendar(null, "en");
ConversionResult result = cal.gregorianToHijri(2024, 3, 15, null);
// result.getOutput().getYear() == 1445
```

See [Contributing](../../CONTRIBUTING.md) for development setup.
