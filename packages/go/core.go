package ummalqura

import (
	"fmt"
	"sort"
)

// Umm al-Qura leap year positions (mod 30)
var umalQuraLeapYears = map[int]bool{
	2: true, 5: true, 7: true, 10: true, 13: true,
	16: true, 18: true, 21: true, 24: true, 26: true, 29: true,
}

// Day of week names
var daysEn = []string{"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"}
var daysAr = []string{"الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"}

// Gregorian month lengths (non-leap year)
var gregorianMonthDays = []int{0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31}

// IsGregorianLeapYear checks if a Gregorian year is a leap year
func IsGregorianLeapYear(year int) bool {
	return (year%4 == 0) && (year%100 != 0 || year%400 == 0)
}

// GregorianMonthLength returns the number of days in a Gregorian month
func GregorianMonthLength(year, month int) int {
	if month == 2 && IsGregorianLeapYear(year) {
		return 29
	}
	return gregorianMonthDays[month]
}

// IsUmAlQuraLeapYear checks if a Hijri year is a leap year
func IsUmAlQuraLeapYear(year int) bool {
	return umalQuraLeapYears[year%30]
}

// GregorianToJdn converts Gregorian date to Julian Day Number
func GregorianToJdn(year, month, day int) int {
	a := (14 - month) / 12
	y := year + 4800 - a
	m := month + 12*a - 3
	return day + (153*m+2)/5 + 365*y + y/4 - y/100 + y/400 - 32045
}

// JdnToGregorian converts Julian Day Number to Gregorian date
func JdnToGregorian(jdn int) GregorianDate {
	a := jdn + 32044
	b := (4*a + 3) / 146097
	c := a - (146097*b)/4
	d := (4*c + 3) / 1461
	e := c - (1461*d)/4
	m := (5*e + 2) / 153

	day := e - (153*m+2)/5 + 1
	month := m + 3 - 12*(m/10)
	year := 100*b + d - 4800 + m/10

	return GregorianDate{Year: year, Month: month, Day: day, Calendar: CalendarGregorian}
}

// DayOfWeekFromJdn calculates day of week from JDN
func DayOfWeekFromJdn(jdn int) DayOfWeek {
	index := (jdn + 1) % 7
	return DayOfWeek{Index: index, NameEn: daysEn[index], NameAr: daysAr[index]}
}

// HijriToJdn converts Hijri date to Julian Day Number
func HijriToJdn(year, month, day int, monthIndex map[string]*MonthInfo) (int, error) {
	key := fmt.Sprintf("%d-%d", year, month)
	entry, ok := monthIndex[key]
	if !ok {
		return 0, &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   fmt.Sprintf("Hijri date %s is outside the supported range", key),
		}
	}
	return entry.FirstDayJdn + day - 1, nil
}

// JdnToHijri converts Julian Day Number to Hijri date using binary search.
// The sortedMonths slice must be sorted by FirstDayJdn in ascending order.
func JdnToHijri(jdn int, sortedMonths []*MonthInfo) (HijriDate, error) {
	if len(sortedMonths) == 0 {
		return HijriDate{}, &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   "Month table is empty",
		}
	}
	if jdn < sortedMonths[0].FirstDayJdn {
		return HijriDate{}, &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   fmt.Sprintf("JDN %d is before the supported range (first JDN: %d)", jdn, sortedMonths[0].FirstDayJdn),
		}
	}

	lastMonth := sortedMonths[len(sortedMonths)-1]
	lastValidJdn := lastMonth.FirstDayJdn + lastMonth.MonthLength - 1
	if jdn > lastValidJdn {
		return HijriDate{}, &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   fmt.Sprintf("JDN %d is after the supported range (last JDN: %d)", jdn, lastValidJdn),
		}
	}

	// Binary search for the month containing this JDN
	left := 0
	right := len(sortedMonths) - 1

	for left < right {
		mid := (left + right) / 2
		if sortedMonths[mid].FirstDayJdn <= jdn {
			left = mid + 1
		} else {
			right = mid
		}
	}

	// Clamp to valid range
	if left >= len(sortedMonths) {
		left = len(sortedMonths) - 1
	} else if left > 0 && sortedMonths[left].FirstDayJdn > jdn {
		left--
	}

	entry := sortedMonths[left]
	day := jdn - entry.FirstDayJdn + 1

	return HijriDate{Year: entry.HijriYear, Month: entry.HijriMonth, Day: day, Calendar: CalendarHijriUmAlQura}, nil
}

// ValidateGregorian validates a Gregorian date
func ValidateGregorian(year, month, day, minYear, maxYear int) *CalendarError {
	if month < 1 || month > 12 {
		return &CalendarError{
			ErrorCode: ErrorCodeInvalidMonth,
			Message:   fmt.Sprintf("Month must be between 1 and 12, got %d", month),
			Field:     "month",
			Value:     month,
		}
	}
	if year < minYear || year > maxYear {
		return &CalendarError{
			ErrorCode: ErrorCodeInvalidYear,
			Message:   fmt.Sprintf("Year must be between %d and %d, got %d", minYear, maxYear, year),
			Field:     "year",
			Value:     year,
		}
	}
	maxDay := GregorianMonthLength(year, month)
	if day < 1 || day > maxDay {
		return &CalendarError{
			ErrorCode: ErrorCodeInvalidDay,
			Message:   fmt.Sprintf("Day must be between 1 and %d for %d-%02d, got %d", maxDay, year, month, day),
			Field:     "day",
			Value:     day,
		}
	}
	return nil
}

// ValidateHijri validates a Hijri date.
// minYear and maxYear provide the supported range; use 0 for data-driven range.
func ValidateHijri(year, month, day int, monthIndex map[string]*MonthInfo, minYear, maxYear int) *CalendarError {
	if month < 1 || month > 12 {
		return &CalendarError{
			ErrorCode: ErrorCodeInvalidMonth,
			Message:   fmt.Sprintf("Month must be between 1 and 12, got %d", month),
			Field:     "month",
			Value:     month,
		}
	}
	if minYear == 0 && maxYear == 0 {
		for _, m := range monthIndex {
			if minYear == 0 || m.HijriYear < minYear {
				minYear = m.HijriYear
			}
			if m.HijriYear > maxYear {
				maxYear = m.HijriYear
			}
		}
	}
	if year < minYear || year > maxYear {
		return &CalendarError{
			ErrorCode: ErrorCodeInvalidYear,
			Message:   fmt.Sprintf("Year must be between %d and %d, got %d", minYear, maxYear, year),
			Field:     "year",
			Value:     year,
		}
	}
	key := fmt.Sprintf("%d-%d", year, month)
	entry, ok := monthIndex[key]
	if !ok {
		return &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   fmt.Sprintf("Hijri date %s is outside the supported range", key),
		}
	}
	if day < 1 || day > entry.MonthLength {
		return &CalendarError{
			ErrorCode: ErrorCodeInvalidDay,
			Message:   fmt.Sprintf("Day %d does not exist in Hijri month %s, which has %d days", day, key, entry.MonthLength),
			Field:     "day",
			Value:     day,
		}
	}
	return nil
}

// BuildMonthIndex builds an index for fast month lookup
func BuildMonthIndex(months []*MonthInfo) map[string]*MonthInfo {
	index := make(map[string]*MonthInfo, len(months))
	for _, m := range months {
		key := fmt.Sprintf("%d-%d", m.HijriYear, m.HijriMonth)
		index[key] = m
	}
	return index
}

// BuildJdnIndex builds a sorted array for binary search by JDN
func BuildJdnIndex(months []*MonthInfo) []*MonthInfo {
	sorted := make([]*MonthInfo, len(months))
	copy(sorted, months)
	sort.Slice(sorted, func(i, j int) bool {
		return sorted[i].FirstDayJdn < sorted[j].FirstDayJdn
	})
	return sorted
}

// GetGregorianYearRange returns the Gregorian year range from month data
func GetGregorianYearRange(months []*MonthInfo) (int, int) {
	if len(months) == 0 {
		return 0, 0
	}
	first := JdnToGregorian(months[0].FirstDayJdn)
	last := months[len(months)-1]
	lastJdn := last.FirstDayJdn + last.MonthLength - 1
	lastGreg := JdnToGregorian(lastJdn)
	return first.Year, lastGreg.Year
}
