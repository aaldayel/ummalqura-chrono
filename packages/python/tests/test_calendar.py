"""
Umm al-Qura Calendar Conversion Library - Tests

Tests based on golden values and known conversion pairs.
"""

import pytest
import csv
from pathlib import Path
from typing import List, Dict, Any

from ummalqura import UmmAlQuraCalendar, CalendarException, ErrorCode


# Path to golden values CSV
GOLDEN_VALUES_PATH = Path(__file__).parent.parent.parent.parent / "tests" / "golden" / "golden-values.csv"


def load_golden_values() -> List[Dict[str, Any]]:
    """Load golden values from CSV"""
    values = []
    with open(GOLDEN_VALUES_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            values.append({
                'gregorian_year': int(row['gregorian_year']),
                'gregorian_month': int(row['gregorian_month']),
                'gregorian_day': int(row['gregorian_day']),
                'hijri_year': int(row['hijri_year']),
                'hijri_month': int(row['hijri_month']),
                'hijri_day': int(row['hijri_day']),
                'jdn': int(row['jdn']),
                'day_of_week_index': int(row['day_of_week_index']),
                'day_of_week_en': row['day_of_week_en'],
                'day_of_week_ar': row['day_of_week_ar']
            })
    return values


@pytest.fixture
def calendar():
    """Create a calendar instance for testing"""
    return UmmAlQuraCalendar()


@pytest.fixture
def golden_values():
    """Load golden values for testing"""
    return load_golden_values()


class TestVersionAndData:
    """Test version and data information"""
    
    def test_library_version(self, calendar):
        assert calendar.version == "1.0.0"
    
    def test_data_version(self, calendar):
        assert calendar.data_version_info is not None
        assert len(calendar.data_version_info) > 0
    
    def test_data_checksum(self, calendar):
        assert calendar.data_checksum_info is not None
        assert len(calendar.data_checksum_info) > 0
    
    def test_hijri_range(self, calendar):
        start, end = calendar.hijri_range
        assert start == 1318
        assert end == 1500
    
    def test_gregorian_range(self, calendar):
        min_year, max_year = calendar.gregorian_year_range
        assert min_year < max_year
        assert min_year >= 1900
        assert max_year < 2300


class TestGregorianToHijri:
    """Test Gregorian to Hijri conversion"""
    
    def test_known_date(self, calendar):
        """Test March 15, 2024 = 1445-09-05"""
        result = calendar.gregorian_to_hijri(2024, 3, 15)
        assert result.output.year == 1445
        assert result.output.month == 9
        assert result.output.day == 5
    
    def test_jdn_in_result(self, calendar):
        result = calendar.gregorian_to_hijri(2024, 3, 15)
        assert result.jdn == 2460385
    
    def test_day_of_week(self, calendar):
        result = calendar.gregorian_to_hijri(2024, 3, 15)
        assert result.day_of_week.index == 5
        assert result.day_of_week.name_en == "Friday"
        assert result.day_of_week.name_ar == "الجمعة"
    
    def test_invalid_month(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.gregorian_to_hijri(2024, 13, 1)
        assert exc_info.value.error.error_code == ErrorCode.INVALID_MONTH
    
    def test_invalid_day(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.gregorian_to_hijri(2024, 2, 30)
        assert exc_info.value.error.error_code == ErrorCode.INVALID_DAY
    
    def test_year_out_of_range(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.gregorian_to_hijri(1899, 1, 1)
        assert exc_info.value.error.error_code == ErrorCode.INVALID_YEAR


class TestHijriToGregorian:
    """Test Hijri to Gregorian conversion"""
    
    def test_known_date(self, calendar):
        """Test 1445-09-05 = March 15, 2024"""
        result = calendar.hijri_to_gregorian(1445, 9, 5)
        assert result.output.year == 2024
        assert result.output.month == 3
        assert result.output.day == 15
    
    def test_invalid_month(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.hijri_to_gregorian(1445, 13, 1)
        assert exc_info.value.error.error_code == ErrorCode.INVALID_MONTH
    
    def test_invalid_day(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.hijri_to_gregorian(1445, 9, 31)
        assert exc_info.value.error.error_code == ErrorCode.INVALID_DAY
    
    def test_year_out_of_range(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.hijri_to_gregorian(1317, 1, 1)
        assert exc_info.value.error.error_code == ErrorCode.INVALID_YEAR


class TestRoundTrip:
    """Test round-trip conversions"""
    
    def test_gregorian_to_hijri_to_gregorian(self, calendar):
        """Test Gregorian -> Hijri -> Gregorian round-trip"""
        dates = [
            (2024, 3, 15),
            (2000, 1, 1),
            (1900, 6, 15),
            (2024, 12, 31)
        ]
        
        for year, month, day in dates:
            hijri = calendar.gregorian_to_hijri(year, month, day)
            gregorian = calendar.hijri_to_gregorian(
                hijri.output.year,
                hijri.output.month,
                hijri.output.day
            )
            
            assert gregorian.output.year == year
            assert gregorian.output.month == month
            assert gregorian.output.day == day
    
    def test_hijri_to_gregorian_to_hijri(self, calendar):
        """Test Hijri -> Gregorian -> Hijri round-trip"""
        dates = [
            (1445, 9, 5),
            (1400, 1, 1),
            (1350, 6, 15),
            (1500, 12, 29)
        ]
        
        for year, month, day in dates:
            gregorian = calendar.hijri_to_gregorian(year, month, day)
            hijri = calendar.gregorian_to_hijri(
                gregorian.output.year,
                gregorian.output.month,
                gregorian.output.day
            )
            
            assert hijri.output.year == year
            assert hijri.output.month == month
            assert hijri.output.day == day


class TestDayOfWeek:
    """Test day of week calculations"""
    
    def test_from_jdn(self, calendar):
        """Test day of week from JDN"""
        dow = calendar.get_day_of_week(2460385)
        assert dow.index == 5
        assert dow.name_en == "Friday"
    
    def test_from_gregorian(self, calendar):
        """Test day of week for Gregorian date"""
        dow = calendar.get_day_of_week_gregorian(2024, 3, 15)
        assert dow.index == 5
        assert dow.name_en == "Friday"
    
    def test_from_hijri(self, calendar):
        """Test day of week for Hijri date"""
        dow = calendar.get_day_of_week_hijri(1445, 9, 5)
        assert dow.index == 5
        assert dow.name_en == "Friday"


class TestMonthLengths:
    """Test month length calculations"""
    
    def test_gregorian_month_lengths(self, calendar):
        """Test Gregorian month lengths"""
        assert calendar.get_gregorian_month_length(2024, 1) == 31  # January
        assert calendar.get_gregorian_month_length(2024, 2) == 29  # February (leap)
        assert calendar.get_gregorian_month_length(2023, 2) == 28  # February (non-leap)
        assert calendar.get_gregorian_month_length(2024, 4) == 30  # April
    
    def test_hijri_month_lengths(self, calendar):
        """Test Hijri month lengths"""
        assert calendar.get_hijri_month_length(1445, 1) == 29  # Muharram
        assert calendar.get_hijri_month_length(1445, 2) == 30  # Safar
        assert calendar.get_hijri_month_length(1445, 12) == 30  # Dhul Hijjah
    
    def test_leap_years(self, calendar):
        """Test leap year detection"""
        assert calendar.is_gregorian_leap_year(2024) is True
        assert calendar.is_gregorian_leap_year(2023) is False
        assert calendar.is_gregorian_leap_year(1900) is False
        assert calendar.is_gregorian_leap_year(2000) is True


class TestValidation:
    """Test date validation"""
    
    def test_valid_gregorian(self, calendar):
        result = calendar.validate_gregorian_date(2024, 3, 15)
        assert result.valid is True
        assert result.error is None
    
    def test_invalid_gregorian_month(self, calendar):
        result = calendar.validate_gregorian_date(2024, 13, 1)
        assert result.valid is False
        assert result.error.error_code == ErrorCode.INVALID_MONTH
    
    def test_invalid_gregorian_day(self, calendar):
        result = calendar.validate_gregorian_date(2024, 2, 30)
        assert result.valid is False
        assert result.error.error_code == ErrorCode.INVALID_DAY
    
    def test_valid_hijri(self, calendar):
        result = calendar.validate_hijri_date(1445, 9, 5)
        assert result.valid is True
        assert result.error is None
    
    def test_invalid_hijri_month(self, calendar):
        result = calendar.validate_hijri_date(1445, 13, 1)
        assert result.valid is False
        assert result.error.error_code == ErrorCode.INVALID_MONTH
    
    def test_invalid_hijri_day(self, calendar):
        result = calendar.validate_hijri_date(1445, 9, 31)
        assert result.valid is False
        assert result.error.error_code == ErrorCode.INVALID_DAY


class TestMonthCalendar:
    """Test month calendar generation"""
    
    def test_gregorian_month(self, calendar):
        result = calendar.get_gregorian_month(2024, 3)
        assert result.calendar == "gregorian"
        assert result.year == 2024
        assert result.month == 3
        assert len(result.days) == 31  # March has 31 days
        assert result.month_name_en == "March"
    
    def test_hijri_month(self, calendar):
        result = calendar.get_hijri_month(1445, 9)
        assert result.calendar == "hijri-ummalqura"
        assert result.year == 1445
        assert result.month == 9
        assert len(result.days) == 30  # Ramadan 1445 has 30 days
        assert result.month_name_en == "Ramadan"


class TestBatchConversion:
    """Test batch conversion"""
    
    def test_batch_gregorian_to_hijri(self, calendar):
        dates = [
            {'year': 2024, 'month': 3, 'day': 15},
            {'year': 2024, 'month': 3, 'day': 16}
        ]
        
        results = calendar.batch_gregorian_to_hijri(dates)
        assert len(results) == 2
        assert results[0].output.year == 1445
        assert results[0].output.month == 9
        assert results[0].output.day == 5
        assert results[1].output.day == 6
    
    def test_batch_hijri_to_gregorian(self, calendar):
        dates = [
            {'year': 1445, 'month': 9, 'day': 5},
            {'year': 1445, 'month': 9, 'day': 6}
        ]
        
        results = calendar.batch_hijri_to_gregorian(dates)
        assert len(results) == 2
        assert results[0].output.year == 2024
        assert results[0].output.month == 3
        assert results[0].output.day == 15
        assert results[1].output.day == 16


class TestGoldenValues:
    """Test against golden values"""
    
    def test_gregorian_to_hijri_sample(self, calendar, golden_values):
        """Test a sample of golden values for Gregorian to Hijri"""
        sample_size = 100
        step = max(1, len(golden_values) // sample_size)
        
        for i in range(0, len(golden_values), step):
            gv = golden_values[i]
            
            result = calendar.gregorian_to_hijri(
                gv['gregorian_year'],
                gv['gregorian_month'],
                gv['gregorian_day']
            )
            
            assert result.output.year == gv['hijri_year']
            assert result.output.month == gv['hijri_month']
            assert result.output.day == gv['hijri_day']
            assert result.jdn == gv['jdn']
            assert result.day_of_week.index == gv['day_of_week_index']
            assert result.day_of_week.name_en == gv['day_of_week_en']
    
    def test_hijri_to_gregorian_sample(self, calendar, golden_values):
        """Test a sample of golden values for Hijri to Gregorian"""
        sample_size = 100
        step = max(1, len(golden_values) // sample_size)
        
        for i in range(0, len(golden_values), step):
            gv = golden_values[i]
            
            result = calendar.hijri_to_gregorian(
                gv['hijri_year'],
                gv['hijri_month'],
                gv['hijri_day']
            )
            
            assert result.output.year == gv['gregorian_year']
            assert result.output.month == gv['gregorian_month']
            assert result.output.day == gv['gregorian_day']
            assert result.jdn == gv['jdn']


class TestErrorHandling:
    """Test error handling"""
    
    def test_structured_error_invalid_month(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.gregorian_to_hijri(2024, 13, 1)
        
        error = exc_info.value.error
        assert error.error_code == ErrorCode.INVALID_MONTH
        assert error.field == "month"
        assert error.value == 13
    
    def test_structured_error_invalid_day(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.hijri_to_gregorian(1445, 9, 31)
        
        error = exc_info.value.error
        assert error.error_code == ErrorCode.INVALID_DAY
        assert error.field == "day"
        assert error.value == 31
    
    def test_structured_error_year_out_of_range(self, calendar):
        with pytest.raises(CalendarException) as exc_info:
            calendar.gregorian_to_hijri(1899, 1, 1)
        
        error = exc_info.value.error
        assert error.error_code == ErrorCode.INVALID_YEAR
        assert error.field == "year"
