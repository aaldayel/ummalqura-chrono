# Dart Implementation (Alpha)

Idiomatic Dart/Flutter implementation of the Umm al-Qura calendar conversion library, published to [pub.dev](https://pub.dev).

## Status

Alpha — core implementation available.

## Usage

```dart
import 'package:ummalqura/ummalqura.dart';

final cal = UmmAlQuraCalendar(dataPath: null, defaultLocale: 'en');
final result = cal.gregorianToHijri(2024, 3, 15, locale: null);
// result.output.year == 1445
```

See [Contributing](../../CONTRIBUTING.md) for development setup.
