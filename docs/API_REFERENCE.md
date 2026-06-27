# API Reference

## Core Types

### GregorianDate

```typescript
interface GregorianDate {
  year: number;      // Gregorian year (e.g., 2024)
  month: number;     // Month (1-12)
  day: number;       // Day (1-31)
  calendar: 'gregorian';
}
```

### HijriDate

```typescript
interface HijriDate {
  year: number;      // Hijri year (1300-1700)
  month: number;     // Month (1-12)
  day: number;       // Day (1-29 or 1-30)
  calendar: 'hijri-ummalqura';
}
```

### ConversionResult

```typescript
interface ConversionResult {
  input: CalendarDate;
  output: CalendarDate;
  jdn: number;
  day_of_week: DayOfWeek;
  locale: string;
  library_version: string;
  data_version: string;
}
```

### DayOfWeek

```typescript
interface DayOfWeek {
  index: number;     // 0=Sunday, 6=Saturday
  name_en: string;
  name_ar: string;
}
```

### ValidationResult

```typescript
interface ValidationResult {
  valid: boolean;
  error?: CalendarError;
}
```

### CalendarError

```typescript
interface CalendarError {
  error_code: ErrorCode;
  message: string;
  field?: string;
  value?: number | string;
}
```

### ErrorCode

```
INVALID_DAY          — Day is out of bounds for the given month
INVALID_MONTH        — Month is outside 1-12
INVALID_YEAR         — Year is outside the supported range
OUT_OF_RANGE         — Date is outside the data table bounds
UNSUPPORTED_CALENDAR — Calendar type is not recognized
INVALID_TIMEZONE     — Timezone identifier is invalid
MALFORMED_INPUT      — Input values are not integers or are missing
```

---

## JavaScript / TypeScript API

### `UmmAlQuraCalendar`

**Constructor**

```typescript
new UmmAlQuraCalendar(config?: {
  dataPath?: string;
  defaultLocale?: string;
})
```

**Methods**

#### `gregorianToHijri(year, month, day, options?)`

Convert a Gregorian date to Hijri.

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | `number` | Gregorian year |
| `month` | `number` | Month (1-12) |
| `day` | `number` | Day |
| `options.locale` | `string?` | Locale code (e.g., 'en', 'ar') |

Returns: `ConversionResult`
Throws: `CalendarError` on invalid input

#### `hijriToGregorian(year, month, day, options?)`

Convert a Hijri date to Gregorian.

| Parameter | Type | Description |
|-----------|------|-------------|
| `year` | `number` | Hijri year (1300-1700) |
| `month` | `number` | Month (1-12) |
| `day` | `number` | Day |
| `options.locale` | `string?` | Locale code |

Returns: `ConversionResult`
Throws: `CalendarError` on invalid input

#### `validateGregorianDate(year, month, day)`

Returns: `ValidationResult`

#### `validateHijriDate(year, month, day)`

Returns: `ValidationResult`

#### `getDayOfWeek(jdn)`

Get day of week from Julian Day Number.

Returns: `DayOfWeek`

#### `getDayOfWeekGregorian(year, month, day)`

Returns: `DayOfWeek`

#### `getDayOfWeekHijri(year, month, day)`

Returns: `DayOfWeek`

#### `getGregorianMonthLength(year, month)`

Returns: `number` (28-31)

#### `getHijriMonthLength(year, month)`

Returns: `number` (29 or 30)
Throws: `CalendarError` if date is out of range

#### `isGregorianLeapYear(year)`

Returns: `boolean`

#### `getGregorianMonth(year, month, locale?)`

Get all days in a Gregorian month with both calendar representations.

Returns: `MonthCalendar`

#### `getHijriMonth(year, month, locale?)`

Get all days in a Hijri month with both calendar representations.

Returns: `MonthCalendar`

#### `batchGregorianToHijri(dates, options?)`

Batch convert Gregorian dates to Hijri.

| Parameter | Type |
|-----------|------|
| `dates` | `Array<{year: number, month: number, day: number}>` |

Returns: `ConversionResult[]`

#### `batchHijriToGregorian(dates, options?)`

Batch convert Hijri dates to Gregorian.

Returns: `ConversionResult[]`

---

## Python API

The Python API mirrors the JavaScript API with Pythonic conventions:

```python
from ummalqura import UmmAlQuraCalendar

calendar = UmmAlQuraCalendar(data_path=None, default_locale="en")

# Methods (snake_case equivalents):
calendar.gregorian_to_hijri(year, month, day, locale=None)
calendar.hijri_to_gregorian(year, month, day, locale=None)
calendar.validate_gregorian_date(year, month, day)
calendar.validate_hijri_date(year, month, day)
calendar.get_day_of_week(jdn)
calendar.get_day_of_week_gregorian(year, month, day)
calendar.get_day_of_week_hijri(year, month, day)
calendar.get_gregorian_month_length(year, month)
calendar.get_hijri_month_length(year, month)
calendar.is_gregorian_leap_year(year)
calendar.get_gregorian_month(year, month, locale=None)
calendar.get_hijri_month(year, month, locale=None)
calendar.batch_gregorian_to_hijri(dates, locale=None)
calendar.batch_hijri_to_gregorian(dates, locale=None)
```

All Python types are frozen dataclasses for immutability.

## PHP API

```php
use UmmAlQura\UmmAlQuraCalendar;

$calendar = new UmmAlQuraCalendar(dataPath: null, defaultLocale: 'en');

$result = $calendar->gregorianToHijri(2024, 3, 15);
// $result->getOutput()->getYear() → 1445
// $result->getOutput()->getMonth() → 9
// $result->getOutput()->getDay() → 5
// $result->getJdn() → 2460385
// $result->getDayOfWeek()->getIndex() → 5
```

## Go API

```go
import "github.com/ummalqura/ummalqura-chrono-go"

cal, err := ummalqura.NewCalendar("", "en")
result, err := cal.GregorianToHijri(2024, 3, 15, "")
// result.Output.(HijriDate).Year → 1445
// result.Jdn → 2460385
```

## REST API

Full OpenAPI 3.1 specification at `api/openapi.yaml`.

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/convert` | Convert a single date |
| `POST` | `/v1/convert/batch` | Batch convert dates (max 1000) |
| `GET` | `/v1/today?timezone=Asia/Riyadh` | Get today's date |
| `GET` | `/v1/calendar/{calendar}/{year}/{month}` | Get month calendar |
| `GET` | `/v1/validate?calendar=hijri-ummalqura&year=1445&month=9&day=5` | Validate date |
| `GET` | `/v1/day-of-week?calendar=gregorian&year=2024&month=3&day=15` | Get day of week |
| `GET` | `/v1/health` | Health check |
