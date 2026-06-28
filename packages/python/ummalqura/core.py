"""
Core conversion algorithms for Umm al-Qura calendar

All functions are pure, deterministic, and stateless.
No global mutable state is used.
"""

from typing import Dict, List, Tuple, Optional
from .types import (
    MonthInfo,
    DayOfWeek,
    ErrorCode,
    CalendarError,
    CalendarException
)

# Umm al-Qura leap year positions (mod 30)
UMM_AL_QURA_LEAP_YEARS = {2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29}

# Day of week names
DAYS_EN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
DAYS_AR = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت']

# Gregorian month lengths (non-leap year)
GREGORIAN_MONTH_DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]


def is_gregorian_leap_year(year: int) -> bool:
    """Check if a Gregorian year is a leap year"""
    return (year % 4 == 0) and (year % 100 != 0 or year % 400 == 0)


def gregorian_month_length(year: int, month: int) -> int:
    """Get the number of days in a Gregorian month"""
    if month == 2 and is_gregorian_leap_year(year):
        return 29
    return GREGORIAN_MONTH_DAYS[month]


def is_ummalqura_leap_year(year: int) -> bool:
    """Check if a Hijri year is a leap year in Umm al-Qura calendar"""
    return (year % 30) in UMM_AL_QURA_LEAP_YEARS


def hijri_month_length_from_algorithm(year: int, month: int) -> int:
    """Get the number of days in a Hijri month using the algorithm"""
    if month % 2 == 1:
        return 30  # Odd months
    if month == 12:
        return 30 if is_ummalqura_leap_year(year) else 29  # Dhul Hijjah
    return 29  # Even months (2, 4, 6, 8, 10)


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """
    Convert Gregorian date to Julian Day Number (JDN)
    
    Algorithm: Fliegel & Van Flandern (1968)
    Uses proleptic Gregorian calendar rules
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    
    return day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045


def jdn_to_gregorian(jdn: int) -> Tuple[int, int, int]:
    """
    Convert Julian Day Number (JDN) to Gregorian date
    
    Algorithm: Fliegel & Van Flandern (1968), inverse
    """
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    
    return (year, month, day)


def day_of_week_from_jdn(jdn: int) -> DayOfWeek:
    """
    Calculate day of week from JDN
    
    Returns index (0=Sunday, 1=Monday, ..., 6=Saturday)
    """
    # JDN 0 is Monday, so (jdn + 1) % 7 gives Sunday=0
    index = (jdn + 1) % 7
    
    return DayOfWeek(
        index=index,
        name_en=DAYS_EN[index],
        name_ar=DAYS_AR[index]
    )


def build_month_index(months: List[MonthInfo]) -> Dict[str, MonthInfo]:
    """Build an index for fast month lookup from the month table"""
    index: Dict[str, MonthInfo] = {}
    
    for month in months:
        key = f"{month.hijri_year}-{month.hijri_month}"
        index[key] = month
    
    return index


def build_jdn_index(months: List[MonthInfo]) -> List[MonthInfo]:
    """Build a sorted array of month entries for binary search by JDN"""
    return sorted(months, key=lambda m: m.first_day_jdn)


def hijri_to_jdn(
    year: int,
    month: int,
    day: int,
    month_index: Dict[str, MonthInfo]
) -> int:
    """
    Convert Hijri (Umm al-Qura) date to Julian Day Number (JDN)
    
    Uses the month-length table for lookup
    """
    key = f"{year}-{month}"
    entry = month_index.get(key)
    
    if not entry:
        raise CalendarException(CalendarError(
            error_code=ErrorCode.OUT_OF_RANGE,
            message=f"Hijri date {year}-{month:02d} is outside the supported range"
        ))
    
    return entry.first_day_jdn + day - 1


def jdn_to_hijri(
    jdn: int,
    sorted_months: List[MonthInfo]
) -> Tuple[int, int, int]:
    """
    Convert Julian Day Number (JDN) to Hijri (Umm al-Qura) date
    
    Uses binary search on the sorted month table
    """
    if not sorted_months:
        raise CalendarException(CalendarError(
            error_code=ErrorCode.OUT_OF_RANGE,
            message="Month table is empty"
        ))
    if jdn < sorted_months[0].first_day_jdn:
        raise CalendarException(CalendarError(
            error_code=ErrorCode.OUT_OF_RANGE,
            message=f"JDN {jdn} is before the supported range (first JDN: {sorted_months[0].first_day_jdn})"
        ))

    last_month = sorted_months[-1]
    last_valid_jdn = last_month.first_day_jdn + last_month.month_length - 1
    if jdn > last_valid_jdn:
        raise CalendarException(CalendarError(
            error_code=ErrorCode.OUT_OF_RANGE,
            message=f"JDN {jdn} is after the supported range (last JDN: {last_valid_jdn})"
        ))

    # Binary search for the month containing this JDN
    left = 0
    right = len(sorted_months) - 1
    
    while left < right:
        mid = (left + right) // 2
        if sorted_months[mid].first_day_jdn <= jdn:
            left = mid + 1
        else:
            right = mid
    
    # Clamp to valid range
    if left >= len(sorted_months):
        left = len(sorted_months) - 1
    elif left > 0 and sorted_months[left].first_day_jdn > jdn:
        left -= 1
    
    entry = sorted_months[left]
    day = jdn - entry.first_day_jdn + 1
    
    return (entry.hijri_year, entry.hijri_month, day)


def validate_gregorian(
    year: int,
    month: int,
    day: int,
    min_year: int,
    max_year: int
) -> Optional[CalendarError]:
    """Validate a Gregorian date"""
    # Check for non-integer values
    if not isinstance(year, int) or not isinstance(month, int) or not isinstance(day, int):
        return CalendarError(
            error_code=ErrorCode.MALFORMED_INPUT,
            message="Year, month, and day must be integers",
            field="year",
            value=year
        )
    
    # Check month range
    if month < 1 or month > 12:
        return CalendarError(
            error_code=ErrorCode.INVALID_MONTH,
            message=f"Month must be between 1 and 12, got {month}",
            field="month",
            value=month
        )
    
    # Check year range
    if year < min_year or year > max_year:
        return CalendarError(
            error_code=ErrorCode.INVALID_YEAR,
            message=f"Year must be between {min_year} and {max_year}, got {year}",
            field="year",
            value=year
        )
    
    # Check day range
    max_day = gregorian_month_length(year, month)
    if day < 1 or day > max_day:
        return CalendarError(
            error_code=ErrorCode.INVALID_DAY,
            message=f"Day must be between 1 and {max_day} for {year}-{month:02d}, got {day}",
            field="day",
            value=day
        )
    
    return None


def validate_hijri(
    year: int,
    month: int,
    day: int,
    month_index: Dict[str, MonthInfo],
    min_year: Optional[int] = None,
    max_year: Optional[int] = None
) -> Optional[CalendarError]:
    """Validate a Hijri date"""
    # Check for non-integer values
    if not isinstance(year, int) or not isinstance(month, int) or not isinstance(day, int):
        return CalendarError(
            error_code=ErrorCode.MALFORMED_INPUT,
            message="Year, month, and day must be integers",
            field="year",
            value=year
        )
    
    # Check month range
    if month < 1 or month > 12:
        return CalendarError(
            error_code=ErrorCode.INVALID_MONTH,
            message=f"Month must be between 1 and 12, got {month}",
            field="month",
            value=month
        )
    
    # Use provided range or fall back to data-driven range from month_index
    if min_year is None:
        years = sorted({m.hijri_year for m in month_index.values()})
        min_year = years[0] if years else 1318
    if max_year is None:
        years = sorted({m.hijri_year for m in month_index.values()})
        max_year = years[-1] if years else 1500

    # Check year range
    if year < min_year or year > max_year:
        return CalendarError(
            error_code=ErrorCode.INVALID_YEAR,
            message=f"Year must be between {min_year} and {max_year}, got {year}",
            field="year",
            value=year
        )
    
    # Look up month length
    key = f"{year}-{month}"
    entry = month_index.get(key)
    
    if not entry:
        return CalendarError(
            error_code=ErrorCode.OUT_OF_RANGE,
            message=f"Hijri date {year}-{month:02d} is outside the supported range"
        )
    
    # Check day range
    if day < 1 or day > entry.month_length:
        return CalendarError(
            error_code=ErrorCode.INVALID_DAY,
            message=f"Day {day} does not exist in Hijri month {year}-{month:02d}, which has {entry.month_length} days",
            field="day",
            value=day
        )
    
    return None


def get_gregorian_year_range(months: List[MonthInfo]) -> Tuple[int, int]:
    """Get the Gregorian year range that corresponds to the Hijri year range"""
    if not months:
        return (0, 0)
    
    first_month = months[0]
    last_month = months[-1]
    
    first_gregorian = jdn_to_gregorian(first_month.first_day_jdn)
    last_jdn = last_month.first_day_jdn + last_month.month_length - 1
    last_gregorian = jdn_to_gregorian(last_jdn)
    
    return (first_gregorian[0], last_gregorian[0])
