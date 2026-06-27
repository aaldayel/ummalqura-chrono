# Umm al-Qura Calendar Python Library (UmmAlQura-Chrono)

Accurate conversion between Gregorian and Umm al-Qura Hijri calendars.

## Installation

```bash
pip install ummalqura-chrono
```

## Quick Start

```python
from ummalqura import UmmAlQuraCalendar

cal = UmmAlQuraCalendar()

# Gregorian to Hijri
result = cal.gregorian_to_hijri(2024, 3, 15)
print(result.output)  # HijriDate(year=1445, month=9, day=5)

# Hijri to Gregorian
result = cal.hijri_to_gregorian(1445, 9, 5)
print(result.output)  # GregorianDate(year=2024, month=3, day=15)
```

## Supported Range

- Hijri: 1300 AH – 1700 AH
- Gregorian: ~1882 CE – ~2277 CE

## Documentation

Full API reference: [https://github.com/ummalqura/ummalqura-chrono](https://github.com/ummalqura/ummalqura-chrono)

## License

MIT
