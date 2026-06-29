"""
Umm al-Qura Calendar Conversion Library

Main module providing public API for calendar conversions.
"""

import json
from typing import List, Optional, Dict
from pathlib import Path

from .types import (
    GregorianDate,
    HijriDate,
    ConversionResult,
    DayOfWeek,
    MonthInfo,
    MonthCalendar,
    DayInfo,
    ValidationResult,
    CalendarError,
    ErrorCode,
    CalendarException
)
from .core import (
    gregorian_to_jdn,
    jdn_to_gregorian,
    hijri_to_jdn,
    jdn_to_hijri,
    day_of_week_from_jdn,
    gregorian_month_length,
    is_gregorian_leap_year,
    validate_gregorian,
    validate_hijri,
    build_month_index,
    build_jdn_index,
    get_gregorian_year_range
)
from .locale import get_gregorian_month_name, get_hijri_month_name

# Library version
LIBRARY_VERSION = "1.0.0"

def _resolve_data_path(data_path: Optional[str] = None) -> str:
    if data_path and Path(data_path).exists():
        return data_path
    paths_to_try = [
        Path(__file__).parent / "data" / "ummalqura-months.json",
        Path(__file__).parent.parent.parent.parent / "data" / "ummalqura-months.json",
    ]
    for p in paths_to_try:
        if p.exists():
            return str(p)
    raise FileNotFoundError(
        "Cannot find ummalqura-months.json. "
        "Ensure the data directory is included in the package or specify a custom dataPath."
    )


class UmmAlQuraCalendar:
    """
    Umm al-Qura Calendar class
    
    Provides methods for converting between Gregorian and Umm al-Qura calendars.
    Loads the month-length table on initialization.
    """
    
    def __init__(self, data_path: Optional[str] = None, default_locale: str = "en"):
        """
        Create a new UmmAlQuraCalendar instance
        
        Args:
            data_path: Path to the month-length table JSON file
            default_locale: Default locale for month/day names
        """
        self.default_locale = default_locale
        
        # Load month table data
        data_file = Path(_resolve_data_path(data_path))
        
        try:
            with open(data_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Month table not found at {data_file}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in month table: {e}")
        
        # Parse month data
        self.months = [
            MonthInfo(
                hijri_year=m['hijri_year'],
                hijri_month=m['hijri_month'],
                month_length=m['month_length'],
                first_day_jdn=m['first_day_jdn']
            )
            for m in data['months']
        ]
        
        self.data_version = data['version']
        self.data_checksum = data['checksum']
        self.hijri_range = (data['hijri_range']['start'], data['hijri_range']['end'])
        
        # Build indexes for fast lookup
        self.month_index = build_month_index(self.months)
        self.sorted_months = build_jdn_index(self.months)
        self.gregorian_year_range = get_gregorian_year_range(self.months)
    
    @property
    def version(self) -> str:
        """Get the library version"""
        return LIBRARY_VERSION
    
    @property
    def data_version_info(self) -> str:
        """Get the data version"""
        return self.data_version
    
    @property
    def data_checksum_info(self) -> str:
        """Get the data checksum"""
        return self.data_checksum
    
    def gregorian_to_hijri(
        self,
        year: int,
        month: int,
        day: int,
        locale: Optional[str] = None
    ) -> ConversionResult:
        """
        Convert a Gregorian date to Hijri (Umm al-Qura)
        
        Args:
            year: Gregorian year
            month: Gregorian month (1-12)
            day: Gregorian day
            locale: Optional locale for names
            
        Returns:
            ConversionResult with the converted date
            
        Raises:
            CalendarException: If the input date is invalid
        """
        # Validate input
        error = validate_gregorian(
            year, month, day,
            self.gregorian_year_range[0],
            self.gregorian_year_range[1]
        )
        if error:
            raise CalendarException(error)
        
        # Convert to JDN
        jdn = gregorian_to_jdn(year, month, day)
        
        # Convert JDN to Hijri
        h_year, h_month, h_day = jdn_to_hijri(jdn, self.sorted_months)
        
        # Get day of week
        dow = day_of_week_from_jdn(jdn)
        
        return ConversionResult(
            input=GregorianDate(year=year, month=month, day=day),
            output=HijriDate(year=h_year, month=h_month, day=h_day),
            jdn=jdn,
            day_of_week=dow,
            locale=locale or self.default_locale,
            library_version=LIBRARY_VERSION,
            data_version=self.data_version
        )
    
    def hijri_to_gregorian(
        self,
        year: int,
        month: int,
        day: int,
        locale: Optional[str] = None
    ) -> ConversionResult:
        """
        Convert a Hijri (Umm al-Qura) date to Gregorian
        
        Args:
            year: Hijri year (1300-1700)
            month: Hijri month (1-12)
            day: Hijri day
            locale: Optional locale for names
            
        Returns:
            ConversionResult with the converted date
            
        Raises:
            CalendarException: If the input date is invalid
        """
        # Validate input
        error = validate_hijri(year, month, day, self.month_index)
        if error:
            raise CalendarException(error)
        
        # Convert to JDN
        jdn = hijri_to_jdn(year, month, day, self.month_index)
        
        # Convert JDN to Gregorian
        g_year, g_month, g_day = jdn_to_gregorian(jdn)
        
        # Get day of week
        dow = day_of_week_from_jdn(jdn)
        
        return ConversionResult(
            input=HijriDate(year=year, month=month, day=day),
            output=GregorianDate(year=g_year, month=g_month, day=g_day),
            jdn=jdn,
            day_of_week=dow,
            locale=locale or self.default_locale,
            library_version=LIBRARY_VERSION,
            data_version=self.data_version
        )
    
    def validate_gregorian_date(
        self,
        year: int,
        month: int,
        day: int
    ) -> ValidationResult:
        """
        Validate a Gregorian date
        
        Args:
            year: Gregorian year
            month: Gregorian month
            day: Gregorian day
            
        Returns:
            ValidationResult
        """
        error = validate_gregorian(
            year, month, day,
            self.gregorian_year_range[0],
            self.gregorian_year_range[1]
        )
        
        return ValidationResult(valid=error is None, error=error)
    
    def validate_hijri_date(
        self,
        year: int,
        month: int,
        day: int
    ) -> ValidationResult:
        """
        Validate a Hijri date
        
        Args:
            year: Hijri year
            month: Hijri month
            day: Hijri day
            
        Returns:
            ValidationResult
        """
        error = validate_hijri(year, month, day, self.month_index)
        
        return ValidationResult(valid=error is None, error=error)
    
    def get_day_of_week(self, jdn: int) -> DayOfWeek:
        """
        Get the day of week for a JDN
        
        Args:
            jdn: Julian Day Number
            
        Returns:
            DayOfWeek information
        """
        return day_of_week_from_jdn(jdn)
    
    def get_day_of_week_gregorian(
        self,
        year: int,
        month: int,
        day: int
    ) -> DayOfWeek:
        """
        Get the day of week for a Gregorian date
        
        Args:
            year: Gregorian year
            month: Gregorian month
            day: Gregorian day
            
        Returns:
            DayOfWeek information
        """
        jdn = gregorian_to_jdn(year, month, day)
        return day_of_week_from_jdn(jdn)
    
    def get_day_of_week_hijri(
        self,
        year: int,
        month: int,
        day: int
    ) -> DayOfWeek:
        """
        Get the day of week for a Hijri date
        
        Args:
            year: Hijri year
            month: Hijri month
            day: Hijri day
            
        Returns:
            DayOfWeek information
        """
        jdn = hijri_to_jdn(year, month, day, self.month_index)
        return day_of_week_from_jdn(jdn)
    
    def get_gregorian_month_length(self, year: int, month: int) -> int:
        """
        Get the number of days in a Gregorian month
        
        Args:
            year: Gregorian year
            month: Gregorian month (1-12)
            
        Returns:
            Number of days
        """
        return gregorian_month_length(year, month)
    
    def get_hijri_month_length(self, year: int, month: int) -> int:
        """
        Get the number of days in a Hijri month
        
        Args:
            year: Hijri year
            month: Hijri month (1-12)
            
        Returns:
            Number of days
        """
        key = f"{year}-{month}"
        entry = self.month_index.get(key)
        
        if not entry:
            raise CalendarException(
                CalendarError(
                    error_code=ErrorCode.OUT_OF_RANGE,
                    message=f"Hijri date {year}-{month:02d} is outside the supported range"
                )
            )
        
        return entry.month_length
    
    def is_gregorian_leap_year(self, year: int) -> bool:
        """
        Check if a Gregorian year is a leap year
        
        Args:
            year: Gregorian year
            
        Returns:
            True if leap year
        """
        return is_gregorian_leap_year(year)
    
    def get_gregorian_month(
        self,
        year: int,
        month: int,
        locale: Optional[str] = None
    ) -> MonthCalendar:
        """
        Get all days in a Gregorian month with both calendar representations
        
        Args:
            year: Gregorian year
            month: Gregorian month (1-12)
            locale: Optional locale for names
            
        Returns:
            MonthCalendar with all days
        """
        days_in_month = gregorian_month_length(year, month)
        days = []
        
        for day in range(1, days_in_month + 1):
            jdn = gregorian_to_jdn(year, month, day)
            h_year, h_month, h_day = jdn_to_hijri(jdn, self.sorted_months)
            dow = day_of_week_from_jdn(jdn)
            
            days.append(DayInfo(
                gregorian=GregorianDate(year=year, month=month, day=day),
                hijri=HijriDate(year=h_year, month=h_month, day=h_day),
                jdn=jdn,
                day_of_week=dow
            ))
        
        loc = locale or self.default_locale

        return MonthCalendar(
            calendar="gregorian",
            year=year,
            month=month,
            days=days,
            month_name_en=get_gregorian_month_name(month, loc),
            month_name_ar=get_gregorian_month_name(month, 'ar')
        )
    
    def get_hijri_month(
        self,
        year: int,
        month: int,
        locale: Optional[str] = None
    ) -> MonthCalendar:
        """
        Get all days in a Hijri month with both calendar representations
        
        Args:
            year: Hijri year
            month: Hijri month (1-12)
            locale: Optional locale for names
            
        Returns:
            MonthCalendar with all days
        """
        key = f"{year}-{month}"
        entry = self.month_index.get(key)
        
        if not entry:
            raise CalendarException(
                CalendarError(
                    error_code=ErrorCode.OUT_OF_RANGE,
                    message=f"Hijri date {year}-{month:02d} is outside the supported range"
                )
            )
        
        days = []
        
        for day in range(1, entry.month_length + 1):
            jdn = hijri_to_jdn(year, month, day, self.month_index)
            g_year, g_month, g_day = jdn_to_gregorian(jdn)
            dow = day_of_week_from_jdn(jdn)
            
            days.append(DayInfo(
                gregorian=GregorianDate(year=g_year, month=g_month, day=g_day),
                hijri=HijriDate(year=year, month=month, day=day),
                jdn=jdn,
                day_of_week=dow
            ))
        
        loc = locale or self.default_locale
        
        return MonthCalendar(
            calendar="hijri-ummalqura",
            year=year,
            month=month,
            days=days,
            month_name_en=get_hijri_month_name(month, loc),
            month_name_ar=get_hijri_month_name(month, 'ar')
        )
    
    def batch_gregorian_to_hijri(
        self,
        dates: List[Dict[str, int]],
        locale: Optional[str] = None
    ) -> List[ConversionResult]:
        """
        Batch convert Gregorian dates to Hijri
        
        Args:
            dates: List of dicts with year, month, day
            locale: Optional locale for names
            
        Returns:
            List of ConversionResult
        """
        return [
            self.gregorian_to_hijri(d['year'], d['month'], d['day'], locale)
            for d in dates
        ]
    
    def batch_hijri_to_gregorian(
        self,
        dates: List[Dict[str, int]],
        locale: Optional[str] = None
    ) -> List[ConversionResult]:
        """
        Batch convert Hijri dates to Gregorian
        
        Args:
            dates: List of dicts with year, month, day
            locale: Optional locale for names
            
        Returns:
            List of ConversionResult
        """
        return [
            self.hijri_to_gregorian(d['year'], d['month'], d['day'], locale)
            for d in dates
        ]
