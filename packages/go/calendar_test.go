package ummalqura

import (
	"testing"
)

func createTestCalendar(t *testing.T) *UmmAlQuraCalendar {
	t.Helper()
	cal, err := NewCalendar("", "en")
	if err != nil {
		t.Fatalf("Failed to create calendar: %v", err)
	}
	return cal
}

func TestVersion(t *testing.T) {
	cal := createTestCalendar(t)
	if v := cal.Version(); v != "1.0.0" {
		t.Errorf("Expected version 1.0.0, got %s", v)
	}
}

func TestDataVersion(t *testing.T) {
	cal := createTestCalendar(t)
	if v := cal.DataVersion(); v == "" {
		t.Error("Data version should not be empty")
	}
}

func TestDataChecksum(t *testing.T) {
	cal := createTestCalendar(t)
	if v := cal.DataChecksum(); v == "" {
		t.Error("Data checksum should not be empty")
	}
}

func TestHijriRange(t *testing.T) {
	cal := createTestCalendar(t)
	start, end := cal.HijriRange()
	if start != 1300 || end != 1700 {
		t.Errorf("Expected range 1300-1700, got %d-%d", start, end)
	}
}

func TestGregorianRange(t *testing.T) {
	cal := createTestCalendar(t)
	min, max := cal.GregorianRange()
	if min >= max {
		t.Errorf("Expected min < max, got min=%d max=%d", min, max)
	}
	if min <= 1800 {
		t.Errorf("Expected min > 1800, got %d", min)
	}
	if max >= 2300 {
		t.Errorf("Expected max < 2300, got %d", max)
	}
}

func TestGregorianToHijriKnownDate(t *testing.T) {
	cal := createTestCalendar(t)
	result, err := cal.GregorianToHijri(2024, 3, 15, "")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	h := result.Output.(HijriDate)
	if h.Year != 1445 || h.Month != 9 || h.Day != 5 {
		t.Errorf("Expected 1445-09-05, got %d-%02d-%02d", h.Year, h.Month, h.Day)
	}
}

func TestGregorianToHijriJdn(t *testing.T) {
	cal := createTestCalendar(t)
	result, err := cal.GregorianToHijri(2024, 3, 15, "")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if result.Jdn != 2460385 {
		t.Errorf("Expected JDN 2460385, got %d", result.Jdn)
	}
}

func TestGregorianToHijriDayOfWeek(t *testing.T) {
	cal := createTestCalendar(t)
	result, err := cal.GregorianToHijri(2024, 3, 15, "")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if result.DayOfWeek.Index != 5 || result.DayOfWeek.NameEn != "Friday" {
		t.Errorf("Expected Friday (index 5), got %s (index %d)", result.DayOfWeek.NameEn, result.DayOfWeek.Index)
	}
}

func TestGregorianToHijriInvalidMonth(t *testing.T) {
	cal := createTestCalendar(t)
	_, err := cal.GregorianToHijri(2024, 13, 1, "")
	if err == nil {
		t.Error("Expected error for invalid month")
	}
}

func TestGregorianToHijriInvalidDay(t *testing.T) {
	cal := createTestCalendar(t)
	_, err := cal.GregorianToHijri(2024, 2, 30, "")
	if err == nil {
		t.Error("Expected error for invalid day")
	}
}

func TestHijriToGregorianKnownDate(t *testing.T) {
	cal := createTestCalendar(t)
	result, err := cal.HijriToGregorian(1445, 9, 5, "")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	g := result.Output.(GregorianDate)
	if g.Year != 2024 || g.Month != 3 || g.Day != 15 {
		t.Errorf("Expected 2024-03-15, got %d-%02d-%02d", g.Year, g.Month, g.Day)
	}
}

func TestHijriToGregorianInvalidMonth(t *testing.T) {
	cal := createTestCalendar(t)
	_, err := cal.HijriToGregorian(1445, 13, 1, "")
	if err == nil {
		t.Error("Expected error for invalid month")
	}
}

func TestHijriToGregorianInvalidDay(t *testing.T) {
	cal := createTestCalendar(t)
	_, err := cal.HijriToGregorian(1445, 9, 31, "")
	if err == nil {
		t.Error("Expected error for invalid day")
	}
}

func TestRoundTripGregorian(t *testing.T) {
	cal := createTestCalendar(t)
	dates := []struct{ y, m, d int }{
		{2024, 3, 15},
		{2000, 1, 1},
		{1900, 6, 15},
		{2024, 12, 31},
	}
	for _, dt := range dates {
		h, _ := cal.GregorianToHijri(dt.y, dt.m, dt.d, "")
		hi := h.Output.(HijriDate)
		g, _ := cal.HijriToGregorian(hi.Year, hi.Month, hi.Day, "")
		gi := g.Output.(GregorianDate)
		if gi.Year != dt.y || gi.Month != dt.m || gi.Day != dt.d {
			t.Errorf("Round-trip failed: %d-%02d-%02d -> %d-%02d-%02d", dt.y, dt.m, dt.d, gi.Year, gi.Month, gi.Day)
		}
	}
}

func TestRoundTripHijri(t *testing.T) {
	cal := createTestCalendar(t)
	dates := []struct{ y, m, d int }{
		{1445, 9, 5},
		{1400, 1, 1},
		{1350, 6, 15},
		{1500, 12, 29},
	}
	for _, dt := range dates {
		g, _ := cal.HijriToGregorian(dt.y, dt.m, dt.d, "")
		gi := g.Output.(GregorianDate)
		h, _ := cal.GregorianToHijri(gi.Year, gi.Month, gi.Day, "")
		hi := h.Output.(HijriDate)
		if hi.Year != dt.y || hi.Month != dt.m || hi.Day != dt.d {
			t.Errorf("Round-trip failed: %d-%02d-%02d -> %d-%02d-%02d", dt.y, dt.m, dt.d, hi.Year, hi.Month, hi.Day)
		}
	}
}

func TestDayOfWeek(t *testing.T) {
	cal := createTestCalendar(t)
	dow := cal.GetDayOfWeek(2460385)
	if dow.Index != 5 || dow.NameEn != "Friday" {
		t.Errorf("Expected Friday, got %s", dow.NameEn)
	}
}

func TestDayOfWeekGregorian(t *testing.T) {
	cal := createTestCalendar(t)
	dow := cal.GetDayOfWeekGregorian(2024, 3, 15)
	if dow.Index != 5 || dow.NameEn != "Friday" {
		t.Errorf("Expected Friday, got %s", dow.NameEn)
	}
}

func TestGetDayOfWeekHijri(t *testing.T) {
	cal := createTestCalendar(t)
	dow, err := cal.GetDayOfWeekHijri(1445, 9, 5)
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if dow.Index != 5 || dow.NameEn != "Friday" {
		t.Errorf("Expected Friday (index 5), got %s (index %d)", dow.NameEn, dow.Index)
	}
}

func TestGetDayOfWeekHijriInvalid(t *testing.T) {
	cal := createTestCalendar(t)
	_, err := cal.GetDayOfWeekHijri(1200, 1, 1)
	if err == nil {
		t.Error("Expected error for invalid Hijri date")
	}
}

func TestGregorianMonthLengths(t *testing.T) {
	cal := createTestCalendar(t)
	if n := cal.GetGregorianMonthLength(2024, 1); n != 31 {
		t.Errorf("Jan: expected 31, got %d", n)
	}
	if n := cal.GetGregorianMonthLength(2024, 2); n != 29 {
		t.Errorf("Feb leap: expected 29, got %d", n)
	}
	if n := cal.GetGregorianMonthLength(2023, 2); n != 28 {
		t.Errorf("Feb non-leap: expected 28, got %d", n)
	}
	if n := cal.GetGregorianMonthLength(2024, 4); n != 30 {
		t.Errorf("Apr: expected 30, got %d", n)
	}
}

func TestHijriMonthLengths(t *testing.T) {
	cal := createTestCalendar(t)
	n1, _ := cal.GetHijriMonthLength(1445, 1)
	if n1 != 30 {
		t.Errorf("Muharram 1445: expected 30, got %d", n1)
	}
	n2, _ := cal.GetHijriMonthLength(1445, 2)
	if n2 != 29 {
		t.Errorf("Safar 1445: expected 29, got %d", n2)
	}
}

func TestLeapYears(t *testing.T) {
	cal := createTestCalendar(t)
	if !cal.IsGregorianLeapYear(2024) {
		t.Error("2024 should be leap year")
	}
	if cal.IsGregorianLeapYear(2023) {
		t.Error("2023 should not be leap year")
	}
	if cal.IsGregorianLeapYear(1900) {
		t.Error("1900 should not be leap year")
	}
	if !cal.IsGregorianLeapYear(2000) {
		t.Error("2000 should be leap year")
	}
}

func TestValidationValidGregorian(t *testing.T) {
	cal := createTestCalendar(t)
	result := cal.ValidateGregorianDate(2024, 3, 15)
	if !result.Valid {
		t.Error("Expected valid date")
	}
}

func TestValidationInvalidGregorianMonth(t *testing.T) {
	cal := createTestCalendar(t)
	result := cal.ValidateGregorianDate(2024, 13, 1)
	if result.Valid {
		t.Error("Expected invalid date")
	}
	if result.Error == nil || result.Error.ErrorCode != ErrorCodeInvalidMonth {
		t.Error("Expected INVALID_MONTH error")
	}
}

func TestValidationInvalidGregorianDay(t *testing.T) {
	cal := createTestCalendar(t)
	result := cal.ValidateGregorianDate(2024, 2, 30)
	if result.Valid {
		t.Error("Expected invalid date")
	}
}

func TestValidationValidHijri(t *testing.T) {
	cal := createTestCalendar(t)
	result := cal.ValidateHijriDate(1445, 9, 5)
	if !result.Valid {
		t.Error("Expected valid date")
	}
}

func TestValidationInvalidHijriMonth(t *testing.T) {
	cal := createTestCalendar(t)
	result := cal.ValidateHijriDate(1445, 13, 1)
	if result.Valid {
		t.Error("Expected invalid date")
	}
}

func TestBatchGregorianToHijri(t *testing.T) {
	cal := createTestCalendar(t)
	dates := []struct{ Year, Month, Day int }{
		{2024, 3, 15},
		{2024, 3, 16},
	}
	results, err := cal.BatchGregorianToHijri(dates, "")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if len(results) != 2 {
		t.Fatalf("Expected 2 results, got %d", len(results))
	}
	h0 := results[0].Output.(HijriDate)
	if h0.Year != 1445 || h0.Month != 9 || h0.Day != 5 {
		t.Errorf("First result: expected 1445-09-05, got %d-%02d-%02d", h0.Year, h0.Month, h0.Day)
	}
	h1 := results[1].Output.(HijriDate)
	if h1.Day != 6 {
		t.Errorf("Second result: expected day 6, got %d", h1.Day)
	}
}

func TestBatchHijriToGregorian(t *testing.T) {
	cal := createTestCalendar(t)
	dates := []struct{ Year, Month, Day int }{
		{1445, 9, 5},
		{1445, 9, 6},
	}
	results, err := cal.BatchHijriToGregorian(dates, "")
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if len(results) != 2 {
		t.Fatalf("Expected 2 results, got %d", len(results))
	}
	g0 := results[0].Output.(GregorianDate)
	if g0.Year != 2024 || g0.Month != 3 || g0.Day != 15 {
		t.Errorf("First result: expected 2024-03-15, got %d-%02d-%02d", g0.Year, g0.Month, g0.Day)
	}
}

func TestIsGregorianLeapYear(t *testing.T) {
	if !IsGregorianLeapYear(2024) {
		t.Error("2024 should be leap")
	}
	if IsGregorianLeapYear(2023) {
		t.Error("2023 should not be leap")
	}
	if IsGregorianLeapYear(1900) {
		t.Error("1900 should not be leap")
	}
	if !IsGregorianLeapYear(2000) {
		t.Error("2000 should be leap")
	}
}

func TestGregorianToJdn(t *testing.T) {
	jdn := GregorianToJdn(2024, 3, 15)
	if jdn != 2460385 {
		t.Errorf("Expected JDN 2460385, got %d", jdn)
	}
}

func TestJdnToGregorian(t *testing.T) {
	g := JdnToGregorian(2460385)
	if g.Year != 2024 || g.Month != 3 || g.Day != 15 {
		t.Errorf("Expected 2024-03-15, got %d-%02d-%02d", g.Year, g.Month, g.Day)
	}
}

func TestIsUmAlQuraLeapYear(t *testing.T) {
	leapTests := []struct {
		year   int
		isLeap bool
	}{
		{1300, true},
		{1303, true},
		{1421, true},
		{1422, false},
		{1423, false},
		{1424, true},
		{1429, true},
		{1430, false},
	}
	for _, tt := range leapTests {
		if got := IsUmAlQuraLeapYear(tt.year); got != tt.isLeap {
			t.Errorf("IsUmAlQuraLeapYear(%d) = %v, want %v", tt.year, got, tt.isLeap)
		}
	}
}

func TestGregorianToHijriBoundaryFirstMonth(t *testing.T) {
	cal := createTestCalendar(t)
	result, err := cal.GregorianToHijri(1882, 11, 24, "")
	if err != nil {
		t.Fatalf("Unexpected error near start of range: %v", err)
	}
	h := result.Output.(HijriDate)
	if h.Year != 1300 || h.Month != 1 || h.Day != 1 {
		t.Errorf("Expected 1300-01-01, got %d-%02d-%02d", h.Year, h.Month, h.Day)
	}
}

func TestHijriToGregorianBoundaryLastMonth(t *testing.T) {
	cal := createTestCalendar(t)
	result, err := cal.HijriToGregorian(1700, 12, 29, "")
	if err != nil {
		t.Fatalf("Unexpected error near end of range: %v", err)
	}
	g := result.Output.(GregorianDate)
	if g.Year < 2270 || g.Year > 2280 {
		t.Errorf("Expected Gregorian year around 2277, got %d", g.Year)
	}
}

func TestJdnToHijriBoundary(t *testing.T) {
	cal := createTestCalendar(t)
	// Get the JDN of last day in the range
	jdn := GregorianToJdn(2278, 1, 1)
	_, _ = JdnToHijri(jdn, cal.sortedMonths)
}

func TestValidateHijriYearRange(t *testing.T) {
	cal := createTestCalendar(t)
	result := cal.ValidateHijriDate(1299, 1, 1)
	if result.Valid {
		t.Error("Expected 1299 to be invalid (before range)")
	}
	result = cal.ValidateHijriDate(1701, 1, 1)
	if result.Valid {
		t.Error("Expected 1701 to be invalid (after range)")
	}
}
