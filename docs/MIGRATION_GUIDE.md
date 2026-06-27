# Migration Guide

## From `hijri-js`

`hijri-js` is a lightweight tabular Islamic calendar library.

```javascript
// Before (hijri-js)
const hijri = require('hijri-js');
const date = hijri.gregorianToHijri(2024, 3, 15);
console.log(date); // { year: 1445, month: 9, day: 4 }

// After (ummalqura)
import { UmmAlQuraCalendar } from 'ummalqura';
const cal = new UmmAlQuraCalendar();
const result = cal.gregorianToHijri(2024, 3, 15);
console.log(result.output); // { year: 1445, month: 9, day: 5, calendar: 'hijri-ummalqura' }
```

> **Note**: `hijri-js` uses a tabular (arithmetic) Islamic calendar which can differ from Umm al-Qura by 1-2 days. The Umm al-Qura calendar is the official calendar of Saudi Arabia.

## From `moment-hijri`

```javascript
// Before (moment-hijri)
const moment = require('moment-hijri');
const m = moment('2024-03-15', 'YYYY-MM-DD');
console.log(m.format('iYYYY/iM/iD')); // 1445/09/04

// After (ummalqura)
import { UmmAlQuraCalendar } from 'ummalqura';
const cal = new UmmAlQuraCalendar();
const result = cal.gregorianToHijri(2024, 3, 15);
const { year, month, day } = result.output;
console.log(`${year}/${month}/${day}`); // 1445/9/5
```

## From .NET `UmmAlQuraCalendar`

```csharp
// Before (.NET System.Globalization)
var cal = new System.Globalization.UmmAlQuraCalendar();
var dt = new DateTime(2024, 3, 15, cal);
Console.WriteLine($"{cal.GetYear(dt)}/{cal.GetMonth(dt)}/{cal.GetDayOfMonth(dt)}");
// This library is verified against the .NET implementation.

// After (ummalqura .NET wrapper — coming soon)
using UmAlQura;
var cal = new UmmAlQuraCalendar();
var result = cal.GregorianToHijri(2024, 3, 15);
Console.WriteLine($"{result.Output.Year}/{result.Output.Month}/{result.Output.Day}");
```

## From Python `hijri-converter`

```python
# Before (hijri-converter)
from hijri_converter import convert
hijri = convert.Gregorian(2024, 3, 15).to_hijri()
print(hijri)  # 1445-09-05

# After (ummalqura)
from ummalqura import UmmAlQuraCalendar
cal = UmmAlQuraCalendar()
result = cal.gregorian_to_hijri(2024, 3, 15)
print(f"{result.output.year}-{result.output.month:02d}-{result.output.day:02d}")
# 1445-09-05
```

## Key Differences

| Feature | Other Libraries | Umm al-Qura |
|---------|----------------|-------------|
| Data source | Tabular/arithmetic | Official KACST table |
| Offline | Usually | Always |
| Cross-language parity | Not guaranteed | Verified by golden values |
| Error handling | Often silent | Structured error codes |
| Supported range | Varies | 1300-1700 AH |
| Timezone handling | Inconsistent | Explicit, separate from core |

## Common Pitfalls

1. **Date differences**: The Umm al-Qura calendar may differ from tabular Islamic calendars by 1-2 days. Always verify against an authoritative source.

2. **Month numbering**: Months are 1-indexed (1 = Muharram, 12 = Dhul Hijjah), not 0-indexed.

3. **Supported range**: Dates outside 1300-1700 AH will produce an `OUT_OF_RANGE` error.

4. **Calendar identifiers**: Use `'hijri-ummalqura'` (not `'hijri'` or `'islamic'`) as the calendar type identifier.
