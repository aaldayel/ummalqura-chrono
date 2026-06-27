package ummalqura

import (
	"crypto/sha256"
	"encoding/json"
	"fmt"
	"os"
	"path/filepath"
	"runtime"
)

const libraryVersion = "1.0.0"

var gregorianMonthsEn = []string{
	"January", "February", "March", "April", "May", "June",
	"July", "August", "September", "October", "November", "December",
}

var gregorianMonthsAr = []string{
	"يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
	"يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر",
}

var hijriMonthsEn = []string{
	"Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
	"Jumada al-Ula", "Jumada al-Thani", "Rajab", "Sha'ban",
	"Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah",
}

var hijriMonthsAr = []string{
	"محرم", "صفر", "ربيع الأول", "ربيع الثاني",
	"جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
	"رمضان", "شوال", "ذو القعدة", "ذو الحجة",
}

// UmmAlQuraCalendar provides methods for calendar conversion
type UmmAlQuraCalendar struct {
	months             []*MonthInfo
	monthIndex         map[string]*MonthInfo
	sortedMonths       []*MonthInfo
	gregorianYearRange [2]int
	dataVersion        string
	dataChecksum       string
	hijriRange         [2]int
	defaultLocale      string
}

// NewCalendar creates a new UmmAlQuraCalendar instance
func NewCalendar(dataPath string, defaultLocale string) (*UmmAlQuraCalendar, error) {
	if defaultLocale == "" {
		defaultLocale = "en"
	}

	if dataPath == "" {
		dataPath = findDataFile()
	}

	data, err := os.ReadFile(dataPath)
	if err != nil {
		return nil, fmt.Errorf("failed to read data file: %w", err)
	}

	// Compute actual SHA-256 checksum of the raw data
	checksum := fmt.Sprintf("%x", sha256.Sum256(data))

	var root struct {
		Version  string `json:"version"`
		HijriRange struct {
			Start int `json:"start"`
			End   int `json:"end"`
		} `json:"hijri_range"`
		Months []MonthInfo `json:"months"`
	}

	if err := json.Unmarshal(data, &root); err != nil {
		return nil, fmt.Errorf("failed to parse data file: %w", err)
	}

	months := make([]*MonthInfo, len(root.Months))
	for i := range root.Months {
		months[i] = &root.Months[i]
	}

	monthIndex := BuildMonthIndex(months)
	sortedMonths := BuildJdnIndex(months)
	minYear, maxYear := GetGregorianYearRange(months)

	return &UmmAlQuraCalendar{
		months:             months,
		monthIndex:         monthIndex,
		sortedMonths:       sortedMonths,
		gregorianYearRange: [2]int{minYear, maxYear},
		dataVersion:        root.Version,
		dataChecksum:       checksum,
		hijriRange:         [2]int{root.HijriRange.Start, root.HijriRange.End},
		defaultLocale:      defaultLocale,
	}, nil
}

func findDataFile() string {
	_, filename, _, _ := runtime.Caller(0)
	dir := filepath.Dir(filename)

	paths := []string{
		filepath.Join(dir, "..", "..", "data", "ummalqura-months.json"),
		filepath.Join(dir, "data", "ummalqura-months.json"),
		"../../data/ummalqura-months.json",
		"data/ummalqura-months.json",
	}

	for _, p := range paths {
		if _, err := os.Stat(p); err == nil {
			return p
		}
	}

	return "../../data/ummalqura-months.json"
}

// Version returns the library version
func (c *UmmAlQuraCalendar) Version() string {
	return libraryVersion
}

// DataVersion returns the data version
func (c *UmmAlQuraCalendar) DataVersion() string {
	return c.dataVersion
}

// DataChecksum returns the data checksum
func (c *UmmAlQuraCalendar) DataChecksum() string {
	return c.dataChecksum
}

// HijriRange returns the supported Hijri year range
func (c *UmmAlQuraCalendar) HijriRange() (int, int) {
	return c.hijriRange[0], c.hijriRange[1]
}

// GregorianRange returns the supported Gregorian year range
func (c *UmmAlQuraCalendar) GregorianRange() (int, int) {
	return c.gregorianYearRange[0], c.gregorianYearRange[1]
}

// GregorianToHijri converts a Gregorian date to Hijri.
// If locale is empty, the calendar's default locale is used.
func (c *UmmAlQuraCalendar) GregorianToHijri(year, month, day int, locale string) (*ConversionResult, error) {
	if err := ValidateGregorian(year, month, day, c.gregorianYearRange[0], c.gregorianYearRange[1]); err != nil {
		return nil, err
	}

	jdn := GregorianToJdn(year, month, day)
	hijri, err := JdnToHijri(jdn, c.sortedMonths)
	if err != nil {
		return nil, err
	}
	dow := DayOfWeekFromJdn(jdn)

	if locale == "" {
		locale = c.defaultLocale
	}

	return &ConversionResult{
		Input:          GregorianDate{Year: year, Month: month, Day: day, Calendar: CalendarGregorian},
		Output:         hijri,
		Jdn:            jdn,
		DayOfWeek:      dow,
		Locale:         locale,
		LibraryVersion: libraryVersion,
		DataVersion:    c.dataVersion,
	}, nil
}

// HijriToGregorian converts a Hijri date to Gregorian.
func (c *UmmAlQuraCalendar) HijriToGregorian(year, month, day int, locale string) (*ConversionResult, error) {
	if err := ValidateHijri(year, month, day, c.monthIndex, c.hijriRange[0], c.hijriRange[1]); err != nil {
		return nil, err
	}

	jdn, err := HijriToJdn(year, month, day, c.monthIndex)
	if err != nil {
		return nil, err
	}

	gregorian := JdnToGregorian(jdn)
	dow := DayOfWeekFromJdn(jdn)

	if locale == "" {
		locale = c.defaultLocale
	}

	return &ConversionResult{
		Input:          HijriDate{Year: year, Month: month, Day: day, Calendar: CalendarHijriUmAlQura},
		Output:         gregorian,
		Jdn:            jdn,
		DayOfWeek:      dow,
		Locale:         locale,
		LibraryVersion: libraryVersion,
		DataVersion:    c.dataVersion,
	}, nil
}

// ValidateGregorianDate validates a Gregorian date
func (c *UmmAlQuraCalendar) ValidateGregorianDate(year, month, day int) ValidationResult {
	err := ValidateGregorian(year, month, day, c.gregorianYearRange[0], c.gregorianYearRange[1])
	return ValidationResult{Valid: err == nil, Error: err}
}

// ValidateHijriDate validates a Hijri date.
func (c *UmmAlQuraCalendar) ValidateHijriDate(year, month, day int) ValidationResult {
	err := ValidateHijri(year, month, day, c.monthIndex, c.hijriRange[0], c.hijriRange[1])
	return ValidationResult{Valid: err == nil, Error: err}
}

// GetDayOfWeek returns day of week from JDN
func (c *UmmAlQuraCalendar) GetDayOfWeek(jdn int) DayOfWeek {
	return DayOfWeekFromJdn(jdn)
}

// GetDayOfWeekGregorian returns day of week for Gregorian date
func (c *UmmAlQuraCalendar) GetDayOfWeekGregorian(year, month, day int) DayOfWeek {
	return DayOfWeekFromJdn(GregorianToJdn(year, month, day))
}

// GetDayOfWeekHijri returns day of week for a Hijri date, or an error.
func (c *UmmAlQuraCalendar) GetDayOfWeekHijri(year, month, day int) (DayOfWeek, error) {
	jdn, err := HijriToJdn(year, month, day, c.monthIndex)
	if err != nil {
		return DayOfWeek{}, err
	}
	return DayOfWeekFromJdn(jdn), nil
}

// GetGregorianMonthLength returns the number of days in a Gregorian month
func (c *UmmAlQuraCalendar) GetGregorianMonthLength(year, month int) int {
	return GregorianMonthLength(year, month)
}

// GetHijriMonthLength returns the number of days in a Hijri month
func (c *UmmAlQuraCalendar) GetHijriMonthLength(year, month int) (int, error) {
	key := fmt.Sprintf("%d-%d", year, month)
	entry, ok := c.monthIndex[key]
	if !ok {
		return 0, &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   fmt.Sprintf("Hijri date %s is outside the supported range", key),
		}
	}
	return entry.MonthLength, nil
}

// GetGregorianMonth returns all days in a Gregorian month with both calendar representations
func (c *UmmAlQuraCalendar) GetGregorianMonth(year, month int, locale string) *MonthCalendar {
	daysInMonth := GregorianMonthLength(year, month)
	days := make([]DayInfo, 0, daysInMonth)

	for day := 1; day <= daysInMonth; day++ {
		jdn := GregorianToJdn(year, month, day)
		hijri, _ := JdnToHijri(jdn, c.sortedMonths)
		dow := DayOfWeekFromJdn(jdn)
		days = append(days, DayInfo{
			Gregorian: GregorianDate{Year: year, Month: month, Day: day, Calendar: CalendarGregorian},
			Hijri:     hijri,
			Jdn:       jdn,
			DayOfWeek: dow,
		})
	}

	if locale == "" {
		locale = c.defaultLocale
	}
	monthNameEn := gregorianMonthsEn[month-1]
	monthNameAr := gregorianMonthsAr[month-1]

	return &MonthCalendar{
		Calendar:    CalendarGregorian,
		Year:        year,
		Month:       month,
		Days:        days,
		MonthNameEn: monthNameEn,
		MonthNameAr: monthNameAr,
	}
}

// GetHijriMonth returns all days in a Hijri month with both calendar representations
func (c *UmmAlQuraCalendar) GetHijriMonth(year, month int, locale string) (*MonthCalendar, error) {
	key := fmt.Sprintf("%d-%d", year, month)
	entry, ok := c.monthIndex[key]
	if !ok {
		return nil, &CalendarError{
			ErrorCode: ErrorCodeOutOfRange,
			Message:   fmt.Sprintf("Hijri date %s is outside the supported range", key),
		}
	}

	days := make([]DayInfo, 0, entry.MonthLength)
	for day := 1; day <= entry.MonthLength; day++ {
		jdn, err := HijriToJdn(year, month, day, c.monthIndex)
		if err != nil {
			return nil, err
		}
		gregorian := JdnToGregorian(jdn)
		dow := DayOfWeekFromJdn(jdn)
		days = append(days, DayInfo{
			Gregorian: gregorian,
			Hijri:     HijriDate{Year: year, Month: month, Day: day, Calendar: CalendarHijriUmAlQura},
			Jdn:       jdn,
			DayOfWeek: dow,
		})
	}

	if locale == "" {
		locale = c.defaultLocale
	}
	monthNameEn := hijriMonthsEn[month-1]
	monthNameAr := hijriMonthsAr[month-1]

	return &MonthCalendar{
		Calendar:    CalendarHijriUmAlQura,
		Year:        year,
		Month:       month,
		Days:        days,
		MonthNameEn: monthNameEn,
		MonthNameAr: monthNameAr,
	}, nil
}

// IsGregorianLeapYear checks if a Gregorian year is a leap year
func (c *UmmAlQuraCalendar) IsGregorianLeapYear(year int) bool {
	return IsGregorianLeapYear(year)
}

// BatchGregorianToHijri batch converts Gregorian dates to Hijri
func (c *UmmAlQuraCalendar) BatchGregorianToHijri(dates []struct{ Year, Month, Day int }, locale string) ([]*ConversionResult, error) {
	results := make([]*ConversionResult, len(dates))
	for i, d := range dates {
		r, err := c.GregorianToHijri(d.Year, d.Month, d.Day, locale)
		if err != nil {
			return nil, err
		}
		results[i] = r
	}
	return results, nil
}

// BatchHijriToGregorian batch converts Hijri dates to Gregorian
func (c *UmmAlQuraCalendar) BatchHijriToGregorian(dates []struct{ Year, Month, Day int }, locale string) ([]*ConversionResult, error) {
	results := make([]*ConversionResult, len(dates))
	for i, d := range dates {
		r, err := c.HijriToGregorian(d.Year, d.Month, d.Day, locale)
		if err != nil {
			return nil, err
		}
		results[i] = r
	}
	return results, nil
}
