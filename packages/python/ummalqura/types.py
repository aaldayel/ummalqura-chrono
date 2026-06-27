"""
Type definitions for Umm al-Qura Calendar Conversion Library
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, Union


class ErrorCode(str, Enum):
    """Error codes for structured error responses"""
    INVALID_DAY = "INVALID_DAY"
    INVALID_MONTH = "INVALID_MONTH"
    INVALID_YEAR = "INVALID_YEAR"
    OUT_OF_RANGE = "OUT_OF_RANGE"
    UNSUPPORTED_CALENDAR = "UNSUPPORTED_CALENDAR"
    INVALID_TIMEZONE = "INVALID_TIMEZONE"
    MALFORMED_INPUT = "MALFORMED_INPUT"


@dataclass(frozen=True)
class GregorianDate:
    """Gregorian date representation"""
    year: int
    month: int
    day: int
    calendar: str = "gregorian"


@dataclass(frozen=True)
class HijriDate:
    """Hijri (Umm al-Qura) date representation"""
    year: int
    month: int
    day: int
    calendar: str = "hijri-ummalqura"


CalendarDate = Union[GregorianDate, HijriDate]


@dataclass(frozen=True)
class DayOfWeek:
    """Day of week information"""
    index: int
    name_en: str
    name_ar: str


@dataclass(frozen=True)
class ConversionResult:
    """Conversion result"""
    input: CalendarDate
    output: CalendarDate
    jdn: int
    day_of_week: DayOfWeek
    locale: str
    library_version: str
    data_version: str


@dataclass(frozen=True)
class CalendarError:
    """Structured error response"""
    error_code: ErrorCode
    message: str
    field: Optional[str] = None
    value: Optional[Union[int, str]] = None

    def __str__(self) -> str:
        return f"{self.error_code}: {self.message}"


@dataclass(frozen=True)
class ValidationResult:
    """Validation result"""
    valid: bool
    error: Optional[CalendarError] = None


@dataclass(frozen=True)
class MonthInfo:
    """Month information from the data table"""
    hijri_year: int
    hijri_month: int
    month_length: int
    first_day_jdn: int


@dataclass(frozen=True)
class MonthTableData:
    """Month-length table data structure"""
    version: str
    description: str
    source: str
    hijri_range_start: int
    hijri_range_end: int
    total_months: int
    generated_at: str
    checksum: str
    months: list


@dataclass(frozen=True)
class DayInfo:
    """Day information for calendar view"""
    gregorian: GregorianDate
    hijri: HijriDate
    jdn: int
    day_of_week: DayOfWeek
    is_today: bool = False


@dataclass(frozen=True)
class MonthCalendar:
    """Month calendar response"""
    calendar: str
    year: int
    month: int
    days: list
    month_name_en: str
    month_name_ar: str


class CalendarException(Exception):
    """Exception for calendar errors"""
    def __init__(self, error: CalendarError):
        self.error = error
        super().__init__(str(error))
