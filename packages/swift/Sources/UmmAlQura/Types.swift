import Foundation

/// Supported calendar systems
public enum CalendarType: String {
    case gregorian = "gregorian"
    case hijriUmAlQura = "hijri-ummalqura"
}

/// Error codes for structured error responses
public enum ErrorCode: String {
    case invalidDay = "INVALID_DAY"
    case invalidMonth = "INVALID_MONTH"
    case invalidYear = "INVALID_YEAR"
    case outOfRange = "OUT_OF_RANGE"
    case unsupportedCalendar = "UNSUPPORTED_CALENDAR"
    case invalidTimezone = "INVALID_TIMEZONE"
    case malformedInput = "MALFORMED_INPUT"
}

/// Gregorian date representation
public struct GregorianDate {
    public let year: Int
    public let month: Int
    public let day: Int
    public let calendar: String = "gregorian"
    
    public init(year: Int, month: Int, day: Int) {
        self.year = year
        self.month = month
        self.day = day
    }
}

/// Hijri (Umm al-Qura) date representation
public struct HijriDate {
    public let year: Int
    public let month: Int
    public let day: Int
    public let calendar: String = "hijri-ummalqura"
    
    public init(year: Int, month: Int, day: Int) {
        self.year = year
        self.month = month
        self.day = day
    }
}

/// Day of week information
public struct DayOfWeek {
    public let index: Int
    public let nameEn: String
    public let nameAr: String
    
    public init(index: Int, nameEn: String, nameAr: String) {
        self.index = index
        self.nameEn = nameEn
        self.nameAr = nameAr
    }
}

/// Conversion result
public struct ConversionResult {
    public let input: Any
    public let output: Any
    public let jdn: Int
    public let dayOfWeek: DayOfWeek
    public let locale: String
    public let libraryVersion: String
    public let dataVersion: String
    
    public init(input: Any, output: Any, jdn: Int, dayOfWeek: DayOfWeek,
                locale: String, libraryVersion: String, dataVersion: String) {
        self.input = input
        self.output = output
        self.jdn = jdn
        self.dayOfWeek = dayOfWeek
        self.locale = locale
        self.libraryVersion = libraryVersion
        self.dataVersion = dataVersion
    }
}

/// Structured error response
public struct CalendarError: Error {
    public let errorCode: ErrorCode
    public let message: String
    public let field: String?
    public let value: Any?
    
    public init(errorCode: ErrorCode, message: String, field: String? = nil, value: Any? = nil) {
        self.errorCode = errorCode
        self.message = message
        self.field = field
        self.value = value
    }
}

/// Validation result
public struct ValidationResult {
    public let valid: Bool
    public let error: CalendarError?
    
    public init(valid: Bool, error: CalendarError? = nil) {
        self.valid = valid
        self.error = error
    }
}

/// Month information from the data table
public struct MonthInfo {
    public let hijriYear: Int
    public let hijriMonth: Int
    public let monthLength: Int
    public let firstDayJdn: Int
    
    public init(hijriYear: Int, hijriMonth: Int, monthLength: Int, firstDayJdn: Int) {
        self.hijriYear = hijriYear
        self.hijriMonth = hijriMonth
        self.monthLength = monthLength
        self.firstDayJdn = firstDayJdn
    }
}
