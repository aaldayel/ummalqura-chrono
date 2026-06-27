# Umm al-Qura Calendar Conversion Algorithm

## Overview

This document describes the mathematical algorithms for converting dates between the Gregorian calendar and the Umm al-Qura Hijri calendar. All conversions use the Julian Day Number (JDN) as an intermediate representation.

## Conversion Pipeline

```
Gregorian ←→ Julian Day Number (JDN) ←→ Umm al-Qura (Hijri)
```

**Rule**: Direct Gregorian ↔ Hijri mapping without JDN is prohibited.

## 1. Julian Day Number (JDN)

The Julian Day Number is a continuous count of days since January 1, 4713 BCE (Julian calendar). JDN 0 corresponds to Monday, January 1, 4713 BCE (Julian).

### Reference Points
- JDN 0 = Monday, January 1, 4713 BCE (Julian)
- JDN 2299161 = October 15, 1582 CE (Gregorian, start of Gregorian calendar)
- JDN 2451545 = January 1, 2000 CE (J2000.0 epoch)

## 2. Gregorian ↔ JDN Conversion

### 2.1 Gregorian to JDN

**Algorithm**: Fliegel & Van Flandern (1968)

```
FUNCTION gregorian_to_jdn(year, month, day):
    a ← (14 - month) / 12          // Integer division
    y ← year + 4800 - a
    m ← month + 12 * a - 3
    
    jdn ← day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045
    RETURN jdn
```

**Where**: All divisions are integer division (floor division).

**Mathematical Reference**: 
- Fliegel, H. F., & Van Flandern, T. C. (1968). "A Machine Algorithm for Processing Calendar Dates." Communications of the ACM, 11(10), 657.

### 2.2 JDN to Gregorian

**Algorithm**: Fliegel & Van Flandern (1968), inverse

```
FUNCTION jdn_to_gregorian(jdn):
    a ← jdn + 32044
    b ← (4 * a + 3) / 146097
    c ← a - (146097 * b) / 4
    d ← (4 * c + 3) / 1461
    e ← c - (1461 * d) / 4
    m ← (5 * e + 2) / 153
    
    day ← e - (153 * m + 2) / 5 + 1
    month ← m + 3 - 12 * (m / 10)
    year ← 100 * b + d - 4800 + m / 10
    
    RETURN (year, month, day)
```

**Where**: All divisions are integer division (floor division).

## 3. Umm al-Qura Calendar System

### 3.1 Calendar Structure

The Umm al-Qura calendar is a lunar calendar with:
- 12 months per year
- Odd months (1, 3, 5, 7, 9, 11) have 30 days
- Even months (2, 4, 6, 8, 10) have 29 days
- Month 12 (Dhul Hijjah) has 30 days in leap years, 29 otherwise

### 3.2 Leap Year Cycle

The Umm al-Qura calendar uses a 30-year cycle. Leap years occur at positions:
```
{2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29} (mod 30)
```

**Rule**: A year `y` is a leap year if `(y mod 30)` is in the set above.

### 3.3 Month-Length Table

The authoritative month-length table is stored in `data/ummalqura-months.json`. Each entry contains:
- `hijri_year`: The Hijri year (1300-1700)
- `hijri_month`: The month number (1-12)
- `month_length`: Number of days (29 or 30)
- `first_day_jdn`: JDN of the first day of the month

**Reference Point**: 1 Muharram 1300 AH = JDN 2402132 (September 17, 1864 CE)

> **Note**: The worked examples in Section 9 use illustrative values and do not
> correspond to entries in the actual `data/ummalqura-months.json` file. They are
> provided solely to demonstrate the conversion algorithm's mechanics. For
> authoritative conversions, always rely on the month-length table.

## 4. Umm al-Qura ↔ JDN Conversion

### 4.1 Umm al-Qura to JDN

```
FUNCTION hijri_to_jdn(year, month, day, month_table):
    FOR EACH entry IN month_table:
        IF entry.hijri_year = year AND entry.hijri_month = month:
            RETURN entry.first_day_jdn + day - 1
    
    RAISE ERROR "Invalid Hijri date"
```

**Optimization**: Use binary search or hash table for O(1) lookup.

### 4.2 JDN to Umm al-Qura

```
FUNCTION jdn_to_hijri(jdn, month_table):
    // Binary search for the month
    left ← 0
    right ← LENGTH(month_table) - 1
    
    WHILE left < right:
        mid ← (left + right) / 2
        IF month_table[mid].first_day_jdn <= jdn:
            left ← mid + 1
        ELSE:
            right ← mid
    
    // Adjust if we went too far
    IF left > 0 AND month_table[left].first_day_jdn > jdn:
        left ← left - 1
    
    entry ← month_table[left]
    day ← jdn - entry.first_day_jdn + 1
    
    RETURN (entry.hijri_year, entry.hijri_month, day)
```

## 5. Day of Week Calculation

```
FUNCTION day_of_week(jdn):
    // JDN 0 is Monday (index 1)
    // We want Sunday = 0, Monday = 1, ..., Saturday = 6
    index ← (jdn + 1) MOD 7
    
    names_en ← ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    names_ar ← ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    
    RETURN (index, names_en[index], names_ar[index])
```

## 6. Validation Functions

### 6.1 Gregorian Validation

```
FUNCTION is_valid_gregorian(year, month, day):
    IF month < 1 OR month > 12:
        RETURN FALSE
    
    IF year < MIN_YEAR OR year > MAX_YEAR:
        RETURN FALSE
    
    max_day ← gregorian_month_length(year, month)
    IF day < 1 OR day > max_day:
        RETURN FALSE
    
    RETURN TRUE
```

### 6.2 Gregorian Leap Year

```
FUNCTION is_gregorian_leap_year(year):
    RETURN (year MOD 4 = 0) AND (year MOD 100 ≠ 0 OR year MOD 400 = 0)
```

### 6.3 Gregorian Month Length

```
FUNCTION gregorian_month_length(year, month):
    IF month IN {1, 3, 5, 7, 8, 10, 12}:
        RETURN 31
    ELSE IF month IN {4, 6, 9, 11}:
        RETURN 30
    ELSE IF month = 2:
        IF is_gregorian_leap_year(year):
            RETURN 29
        ELSE:
            RETURN 28
```

### 6.4 Hijri Validation

```
FUNCTION is_valid_hijri(year, month, day, month_table):
    IF month < 1 OR month > 12:
        RETURN FALSE
    
    IF year < 1300 OR year > 1700:
        RETURN FALSE
    
    // Look up month length in table
    FOR EACH entry IN month_table:
        IF entry.hijri_year = year AND entry.hijri_month = month:
            IF day < 1 OR day > entry.month_length:
                RETURN FALSE
            RETURN TRUE
    
    RETURN FALSE
```

## 7. Batch Conversion

```
FUNCTION batch_convert_gregorian_to_hijri(dates, month_table):
    results ← []
    FOR EACH (year, month, day) IN dates:
        IF NOT is_valid_gregorian(year, month, day):
            RAISE ERROR "Invalid Gregorian date"
        
        jdn ← gregorian_to_jdn(year, month, day)
        (h_year, h_month, h_day) ← jdn_to_hijri(jdn, month_table)
        dow ← day_of_week(jdn)
        
        results.APPEND({
            input: (year, month, day, "gregorian"),
            output: (h_year, h_month, h_day, "hijri-ummalqura"),
            jdn: jdn,
            day_of_week: dow
        })
    
    RETURN results
```

## 8. Complexity Analysis

| Operation | Time Complexity | Space Complexity |
|-----------|----------------|------------------|
| Gregorian → JDN | O(1) | O(1) |
| JDN → Gregorian | O(1) | O(1) |
| Hijri → JDN | O(1) with hash, O(log n) with binary search | O(1) |
| JDN → Hijri | O(log n) binary search | O(1) |
| Day of week | O(1) | O(1) |
| Validation | O(1) with hash, O(log n) with binary search | O(1) |

## 9. Worked Examples

### Example 1: Gregorian to Hijri
**Input**: March 15, 2024 CE

1. Gregorian → JDN:
   ```
   a = (14 - 3) / 12 = 0
   y = 2024 + 4800 - 0 = 6824
   m = 3 + 0 - 3 = 0
   jdn = 15 + (0 + 2) / 5 + 365 * 6824 + 6824 / 4 - 6824 / 100 + 6824 / 400 - 32045
   jdn = 15 + 0 + 2490760 + 1706 - 68 + 17 - 32045
   jdn = 2460385
   ```

2. JDN → Hijri:
   - Binary search in month table
   - Find entry: Hijri 1445, Month 9 (Ramadan), first_day_jdn = 2460381
   - day = 2460385 - 2460381 + 1 = 5
   - **Result**: 1445-09-05 (5 Ramadan 1445 AH)

### Example 2: Hijri to Gregorian
**Input**: 1445-09-05 (5 Ramadan 1445 AH)

1. Hijri → JDN:
   - Lookup in table: 1445-09 first_day_jdn = 2460381
   - jdn = 2460381 + 5 - 1 = 2460385

2. JDN → Gregorian:
   ```
   a = 2460385 + 32044 = 2492429
   b = (4 * 2492429 + 3) / 146097 = 68
    c = 2492429 - (146097 * 68) / 4 = 8780
    d = (4 * 8780 + 3) / 1461 = 24
    e = 8780 - (1461 * 24) / 4 = 14
    m = (5 * 14 + 2) / 153 = 0

    day = 14 - (153 * 0 + 2) / 5 + 1 = 14 - 0 + 1 = 15
    month = 0 + 3 - 12 * (0 / 10) = 3
    year = 100 * 68 + 24 - 4800 + (0 / 10) = 6824 - 4800 + 0 = 2024
    ```

    **Result**: 2024-03-15 CE

    **Note**: Due to the way the Fliegel & Van Flandern algorithm shifts January
    and February into the previous year for calculation purposes, the month is
    derived as `month = m + 3 - 12 * (m / 10)`. When `m = 0` (as in this example),
    the result is month 3 (March). For dates where `m >= 10` (January/February),
    the formula adds 1 to the year and subtracts 12 from the month.

## 10. Implementation Notes

1. **Integer Division**: All divisions in the algorithms are integer (floor) divisions.
2. **Proleptic Gregorian**: The Gregorian calendar is extended backwards before 1582 CE using the same rules.
3. **No Year Zero**: There is no year 0 in the Gregorian calendar (1 BCE is followed by 1 CE).
4. **Data Table**: The month-length table is the single source of truth for Umm al-Qura dates.
5. **Immutability**: All data structures must be immutable after loading.
6. **Thread Safety**: All functions must be thread-safe (no global mutable state).
