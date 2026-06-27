import Foundation

/// Umm al-Qura Calendar Conversion Library
public class UmmAlQuraCalendar {
    static let libraryVersion = "1.0.0"
    
    private let months: [MonthInfo]
    private let monthIndex: [String: MonthInfo]
    private let sortedMonths: [MonthInfo]
    private let gregorianYearRange: (Int, Int)
    private let dataVersion: String
    private let dataChecksum: String
    private let hijriRange: (Int, Int)
    private let defaultLocale: String
    
    private static let gregorianMonthsEn = [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    ]
    private static let gregorianMonthsAr = [
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    ]
    private static let hijriMonthsEn = [
        "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
        "Jumada al-Ula", "Jumada al-Thani", "Rajab", "Sha'ban",
        "Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah"
    ]
    private static let hijriMonthsAr = [
        "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
        "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
    ]
    
    public init(dataPath: String? = nil, defaultLocale: String = "en") throws {
        self.defaultLocale = defaultLocale
        
        let path: String
        if let dataPath = dataPath {
            path = dataPath
        } else {
            path = try Self.findDataFile()
        }
        
        let data = try Data(contentsOf: URL(fileURLWithPath: path))
        guard let json = try JSONSerialization.jsonObject(with: data) as? [String: Any] else {
            throw CalendarError(errorCode: .malformedInput, message: "Invalid JSON format in data file")
        }
        
        guard let dataVersion = json["version"] as? String else {
            throw CalendarError(errorCode: .malformedInput, message: "Missing version in data file")
        }
        self.dataVersion = dataVersion
        
        guard let dataChecksum = json["checksum"] as? String else {
            throw CalendarError(errorCode: .malformedInput, message: "Missing checksum in data file")
        }
        self.dataChecksum = dataChecksum
        
        guard let range = json["hijri_range"] as? [String: Int],
              let rangeStart = range["start"],
              let rangeEnd = range["end"] else {
            throw CalendarError(errorCode: .malformedInput, message: "Missing hijri_range in data file")
        }
        self.hijriRange = (rangeStart, rangeEnd)
        
        guard let monthsArray = json["months"] as? [[String: Int]] else {
            throw CalendarError(errorCode: .malformedInput, message: "Missing months array in data file")
        }
        self.months = try monthsArray.map { m in
            guard let hijriYear = m["hijri_year"],
                  let hijriMonth = m["hijri_month"],
                  let monthLength = m["month_length"],
                  let firstDayJdn = m["first_day_jdn"] else {
                throw CalendarError(errorCode: .malformedInput, message: "Invalid month entry in data file")
            }
            return MonthInfo(
                hijriYear: hijriYear,
                hijriMonth: hijriMonth,
                monthLength: monthLength,
                firstDayJdn: firstDayJdn
            )
        }
        
        self.monthIndex = Core.buildMonthIndex(self.months)
        self.sortedMonths = Core.buildJdnIndex(self.months)
        self.gregorianYearRange = Core.getGregorianYearRange(self.months)
    }
    
    private static func findDataFile() throws -> String {
        let paths = [
            "../../data/ummalqura-months.json",
            "data/ummalqura-months.json",
        ]
        
        for path in paths {
            if FileManager.default.fileExists(atPath: path) {
                return path
            }
        }
        
        throw CalendarError(errorCode: .outOfRange, message: "Could not find ummalqura-months.json data file")
    }
    
    public var version: String { Self.libraryVersion }
    public var dataVersionInfo: String { dataVersion }
    public var dataChecksumInfo: String { dataChecksum }
    
    public func gregorianToHijri(_ year: Int, _ month: Int, _ day: Int, locale: String? = nil) throws -> ConversionResult {
        if let error = Core.validateGregorian(year, month, day, gregorianYearRange.0, gregorianYearRange.1) {
            throw error
        }
        
        let jdn = Core.gregorianToJdn(year, month, day)
        let hijri = try Core.jdnToHijri(jdn, sortedMonths)
        let dow = Core.dayOfWeekFromJdn(jdn)
        
        return ConversionResult(
            input: GregorianDate(year: year, month: month, day: day),
            output: hijri,
            jdn: jdn,
            dayOfWeek: dow,
            locale: locale ?? defaultLocale,
            libraryVersion: Self.libraryVersion,
            dataVersion: dataVersion
        )
    }
    
    public func hijriToGregorian(_ year: Int, _ month: Int, _ day: Int, locale: String? = nil) throws -> ConversionResult {
        if let error = Core.validateHijri(year, month, day, monthIndex) {
            throw error
        }
        
        let jdn = try Core.hijriToJdn(year, month, day, monthIndex)
        let gregorian = Core.jdnToGregorian(jdn)
        let dow = Core.dayOfWeekFromJdn(jdn)
        
        return ConversionResult(
            input: HijriDate(year: year, month: month, day: day),
            output: gregorian,
            jdn: jdn,
            dayOfWeek: dow,
            locale: locale ?? defaultLocale,
            libraryVersion: Self.libraryVersion,
            dataVersion: dataVersion
        )
    }
    
    public func validateGregorianDate(_ year: Int, _ month: Int, _ day: Int) -> ValidationResult {
        let error = Core.validateGregorian(year, month, day, gregorianYearRange.0, gregorianYearRange.1)
        return ValidationResult(valid: error == nil, error: error)
    }
    
    public func validateHijriDate(_ year: Int, _ month: Int, _ day: Int) -> ValidationResult {
        let error = Core.validateHijri(year, month, day, monthIndex)
        return ValidationResult(valid: error == nil, error: error)
    }
    
    public func getDayOfWeek(_ jdn: Int) -> DayOfWeek {
        return Core.dayOfWeekFromJdn(jdn)
    }
    
    public func getDayOfWeekGregorian(_ year: Int, _ month: Int, _ day: Int) -> DayOfWeek {
        return Core.dayOfWeekFromJdn(Core.gregorianToJdn(year, month, day))
    }
    
    public func getDayOfWeekHijri(_ year: Int, _ month: Int, _ day: Int) throws -> DayOfWeek {
        let jdn = try Core.hijriToJdn(year, month, day, monthIndex)
        return Core.dayOfWeekFromJdn(jdn)
    }
    
    public func getGregorianMonthLength(_ year: Int, _ month: Int) -> Int {
        return Core.gregorianMonthLength(year, month)
    }
    
    public func getHijriMonthLength(_ year: Int, _ month: Int) throws -> Int {
        let key = "\(year)-\(month)"
        guard let entry = monthIndex[key] else {
            throw CalendarError(errorCode: .outOfRange, message: "Hijri date \(key) is outside the supported range")
        }
        return entry.monthLength
    }
    
    public func isGregorianLeapYear(_ year: Int) -> Bool {
        return Core.isGregorianLeapYear(year)
    }
}
