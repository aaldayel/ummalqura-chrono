"""
Umm al-Qura Hijri Calendar Conversion Library

Accurate conversion between Gregorian and Umm al-Qura calendars.
"""

from .calendar import UmmAlQuraCalendar
from .locale import load_locale, LocaleData
from .types import (
    GregorianDate,
    HijriDate,
    CalendarDate,
    ConversionResult,
    DayOfWeek,
    ValidationResult,
    CalendarError,
    ErrorCode,
    CalendarException,
    DayInfo,
    MonthCalendar,
    MonthInfo,
    MonthTableData
)

__version__ = "1.0.0"
__all__ = [
    "UmmAlQuraCalendar",
    "load_locale",
    "LocaleData",
    "GregorianDate",
    "HijriDate",
    "CalendarDate",
    "ConversionResult",
    "DayOfWeek",
    "ValidationResult",
    "CalendarError",
    "ErrorCode",
    "CalendarException",
    "DayInfo",
    "MonthCalendar",
    "MonthInfo",
    "MonthTableData"
]
