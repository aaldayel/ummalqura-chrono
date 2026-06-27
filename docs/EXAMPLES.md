# Examples

## JavaScript / TypeScript

### Basic Conversion

```typescript
import { UmmAlQuraCalendar } from 'ummalqura';

const calendar = new UmmAlQuraCalendar();

// Gregorian to Hijri
const hijri = calendar.gregorianToHijri(2024, 3, 15);
console.log(hijri.output); // { year: 1445, month: 9, day: 5, calendar: 'hijri-ummalqura' }

// Hijri to Gregorian
const gregorian = calendar.hijriToGregorian(1445, 9, 5);
console.log(gregorian.output); // { year: 2024, month: 3, day: 15, calendar: 'gregorian' }
```

### Date Validation

```typescript
const valid = calendar.validateGregorianDate(2024, 3, 15);
console.log(valid.valid); // true

const invalid = calendar.validateGregorianDate(2024, 13, 1);
console.log(invalid.valid); // false
console.log(invalid.error?.error_code); // 'INVALID_MONTH'
```

### Batch Conversion

```typescript
const dates = [
  { year: 2024, month: 3, day: 15 },
  { year: 2024, month: 3, day: 16 },
  { year: 2024, month: 3, day: 17 }
];

const results = calendar.batchGregorianToHijri(dates);
results.forEach(r => {
  console.log(`${r.input.year}-${r.input.month}-${r.input.day} → ${r.output.year}-${r.output.month}-${r.output.day}`);
});
```

### Month Calendar

```typescript
const march = calendar.getGregorianMonth(2024, 3, 'en');
march.days.forEach(day => {
  console.log(`March ${day.gregorian.day} = ${day.hijri.day} ${day.hijri.month} ${day.hijri.year} AH (${day.day_of_week.name_en})`);
});
```

### Node.js

```javascript
const { UmmAlQuraCalendar } = require('ummalqura');
const cal = new UmmAlQuraCalendar();
const result = cal.gregorianToHijri(2024, 3, 15);
console.log(result.output); // { year: 1445, month: 9, day: 5, calendar: 'hijri-ummalqura' }
```

---

## Python

```python
from ummalqura import UmmAlQuraCalendar, CalendarException

cal = UmmAlQuraCalendar()

# Conversion
result = cal.gregorian_to_hijri(2024, 3, 15)
print(result.output)  # HijriDate(year=1445, month=9, day=5)

# Validation
valid = cal.validate_gregorian_date(2024, 3, 15)
print(valid.valid)  # True

# Error handling
try:
    cal.gregorian_to_hijri(2024, 13, 1)
except CalendarException as e:
    print(e.error.error_code)  # INVALID_MONTH

# Batch
dates = [
    {'year': 2024, 'month': 3, 'day': 15},
    {'year': 2024, 'month': 3, 'day': 16}
]
results = cal.batch_gregorian_to_hijri(dates)
for r in results:
    print(f"{r.input.year}-{r.input.month:02d}-{r.input.day:02d} → "
          f"{r.output.year}-{r.output.month:02d}-{r.output.day:02d}")
```

---

## PHP

```php
<?php

require 'vendor/autoload.php';

use UmmAlQura\UmmAlQuraCalendar;
use UmmAlQura\CalendarError;

$calendar = new UmmAlQuraCalendar();

// Convert Gregorian to Hijri
$result = $calendar->gregorianToHijri(2024, 3, 15);
echo "{$result->getOutput()->getYear()}-{$result->getOutput()->getMonth()}-{$result->getOutput()->getDay()}\n";
// 1445-9-5

// Convert Hijri to Gregorian
$result = $calendar->hijriToGregorian(1445, 9, 5);
echo "{$result->getOutput()->getYear()}-{$result->getOutput()->getMonth()}-{$result->getOutput()->getDay()}\n";
// 2024-3-15

// Validation
$valid = $calendar->validateGregorianDate(2024, 3, 15);
echo $valid->isValid() ? "Valid\n" : "Invalid\n"; // Valid

// Error handling
try {
    $calendar->gregorianToHijri(2024, 13, 1);
} catch (CalendarError $e) {
    echo $e->getErrorCode() . ': ' . $e->getMessage() . "\n";
}
```

---

## Go

```go
package main

import (
    "fmt"
    ummalqura "github.com/ummalqura/ummalqura-chrono-go"
)

func main() {
    cal, err := ummalqura.NewCalendar("", "en")
    if err != nil {
        panic(err)
    }

    // Gregorian to Hijri
    result, err := cal.GregorianToHijri(2024, 3, 15, "")
    if err != nil {
        panic(err)
    }
    h := result.Output.(ummalqura.HijriDate)
    fmt.Printf("%d-%02d-%02d\n", h.Year, h.Month, h.Day) // 1445-09-05

    // Hijri to Gregorian
    result, err = cal.HijriToGregorian(1445, 9, 5, "")
    g := result.Output.(ummalqura.GregorianDate)
    fmt.Printf("%d-%02d-%02d\n", g.Year, g.Month, g.Day) // 2024-03-15
}
```

---

## REST API

```bash
# Convert a date
curl -X POST http://localhost:3000/v1/convert \
  -H "Content-Type: application/json" \
  -d '{"year": 2024, "month": 3, "day": 15, "from": "gregorian", "to": "hijri-ummalqura"}'

# Get today's date
curl "http://localhost:3000/v1/today?timezone=Asia/Riyadh"

# Validate a date
curl "http://localhost:3000/v1/validate?calendar=hijri-ummalqura&year=1445&month=9&day=30"

# Health check
curl "http://localhost:3000/v1/health"
```

---

## CLI

```bash
# Convert date
uaq convert --from gregorian --to hijri --date 2024-03-15 --format json

# Today's date in Riyadh
uaq today --timezone Asia/Riyadh

# Validate
uaq validate --calendar hijri --date 1445-09-05

# Month calendar
uaq calendar --calendar hijri --year 1445 --month 9
```
