package ummalqura

// CalendarType represents supported calendar systems
type CalendarType string

const (
	CalendarGregorian      CalendarType = "gregorian"
	CalendarHijriUmAlQura  CalendarType = "hijri-ummalqura"
)

// ErrorCode represents error codes for structured error responses
type ErrorCode string

const (
	ErrorCodeInvalidDay         ErrorCode = "INVALID_DAY"
	ErrorCodeInvalidMonth       ErrorCode = "INVALID_MONTH"
	ErrorCodeInvalidYear        ErrorCode = "INVALID_YEAR"
	ErrorCodeOutOfRange         ErrorCode = "OUT_OF_RANGE"
	ErrorCodeUnsupportedCal     ErrorCode = "UNSUPPORTED_CALENDAR"
	ErrorCodeInvalidTimezone    ErrorCode = "INVALID_TIMEZONE"
	ErrorCodeMalformedInput     ErrorCode = "MALFORMED_INPUT"
)

// GregorianDate represents a Gregorian date
type GregorianDate struct {
	Year     int          `json:"year"`
	Month    int          `json:"month"`
	Day      int          `json:"day"`
	Calendar CalendarType `json:"calendar"`
}

// HijriDate represents a Hijri (Umm al-Qura) date
type HijriDate struct {
	Year     int          `json:"year"`
	Month    int          `json:"month"`
	Day      int          `json:"day"`
	Calendar CalendarType `json:"calendar"`
}

// DayOfWeek represents day of week information
type DayOfWeek struct {
	Index  int    `json:"index"`
	NameEn string `json:"name_en"`
	NameAr string `json:"name_ar"`
}

// ConversionResult represents a conversion result
type ConversionResult struct {
	Input         interface{} `json:"input"`
	Output        interface{} `json:"output"`
	Jdn           int         `json:"jdn"`
	DayOfWeek     DayOfWeek   `json:"day_of_week"`
	Locale        string      `json:"locale"`
	LibraryVersion string     `json:"library_version"`
	DataVersion   string      `json:"data_version"`
}

// CalendarError represents a structured error
type CalendarError struct {
	ErrorCode ErrorCode   `json:"error_code"`
	Message   string      `json:"message"`
	Field     string      `json:"field,omitempty"`
	Value     interface{} `json:"value,omitempty"`
}

func (e *CalendarError) Error() string {
	return e.Message
}

// ValidationResult represents a validation result
type ValidationResult struct {
	Valid bool           `json:"valid"`
	Error *CalendarError `json:"error,omitempty"`
}

// MonthInfo represents month information from the data table
type MonthInfo struct {
	HijriYear    int `json:"hijri_year"`
	HijriMonth   int `json:"hijri_month"`
	MonthLength  int `json:"month_length"`
	FirstDayJdn  int `json:"first_day_jdn"`
}

// DayInfo represents day information for calendar view
type DayInfo struct {
	Gregorian GregorianDate `json:"gregorian"`
	Hijri     HijriDate     `json:"hijri"`
	Jdn       int           `json:"jdn"`
	DayOfWeek DayOfWeek     `json:"day_of_week"`
}

// MonthCalendar represents a month calendar response
type MonthCalendar struct {
	Calendar     string    `json:"calendar"`
	Year         int       `json:"year"`
	Month        int       `json:"month"`
	Days         []DayInfo `json:"days"`
	MonthNameEn  string    `json:"month_name_en"`
	MonthNameAr  string    `json:"month_name_ar"`
}
