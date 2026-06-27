import Foundation

/// Core conversion algorithms for Umm al-Qura calendar.
/// All methods are pure, deterministic, and stateless.
internal struct Core {
    static let umalQuraLeapYears: Set<Int> = [2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29]
    static let daysEn = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
    static let daysAr = ["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"]
    static let gregorianMonthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    
    static func isGregorianLeapYear(_ year: Int) -> Bool {
        return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0)
    }
    
    static func gregorianMonthLength(_ year: Int, _ month: Int) -> Int {
        if month == 2 && isGregorianLeapYear(year) {
            return 29
        }
        return gregorianMonthDays[month]
    }
    
    static func isUmAlQuraLeapYear(_ year: Int) -> Bool {
        return umalQuraLeapYears.contains(year % 30)
    }
    
    static func gregorianToJdn(_ year: Int, _ month: Int, _ day: Int) -> Int {
        let a = (14 - month) / 12
        let y = year + 4800 - a
        let m = month + 12 * a - 3
        return day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045
    }
    
    static func jdnToGregorian(_ jdn: Int) -> GregorianDate {
        let a = jdn + 32044
        let b = (4 * a + 3) / 146097
        let c = a - (146097 * b) / 4
        let d = (4 * c + 3) / 1461
        let e = c - (1461 * d) / 4
        let m = (5 * e + 2) / 153
        let day = e - (153 * m + 2) / 5 + 1
        let month = m + 3 - 12 * (m / 10)
        let year = 100 * b + d - 4800 + m / 10
        return GregorianDate(year: year, month: month, day: day)
    }
    
    static func dayOfWeekFromJdn(_ jdn: Int) -> DayOfWeek {
        let index = (jdn + 1) % 7
        return DayOfWeek(index: index, nameEn: daysEn[index], nameAr: daysAr[index])
    }
    
    static func hijriToJdn(_ year: Int, _ month: Int, _ day: Int, _ monthIndex: [String: MonthInfo]) throws -> Int {
        let key = "\(year)-\(month)"
        guard let entry = monthIndex[key] else {
            throw CalendarError(errorCode: .outOfRange, message: "Hijri date \(key) is outside the supported range (1300-1700 AH)")
        }
        return entry.firstDayJdn + day - 1
    }
    
    static func jdnToHijri(_ jdn: Int, _ sortedMonths: [MonthInfo]) throws -> HijriDate {
        if sortedMonths.isEmpty {
            throw CalendarError(errorCode: .outOfRange, message: "Month table is empty")
        }
        if jdn < sortedMonths[0].firstDayJdn {
            throw CalendarError(errorCode: .outOfRange, message: "JDN \(jdn) is before the supported range (first JDN: \(sortedMonths[0].firstDayJdn))")
        }

        var left = 0
        var right = sortedMonths.count - 1
        
        while left < right {
            let mid = (left + right) / 2
            if sortedMonths[mid].firstDayJdn <= jdn {
                left = mid + 1
            } else {
                right = mid
            }
        }
        
        if left >= sortedMonths.count {
            left = sortedMonths.count - 1
        } else if left > 0 && sortedMonths[left].firstDayJdn > jdn {
            left -= 1
        }
        
        let entry = sortedMonths[left]
        let day = jdn - entry.firstDayJdn + 1
        return HijriDate(year: entry.hijriYear, month: entry.hijriMonth, day: day)
    }
    
    static func validateGregorian(_ year: Int, _ month: Int, _ day: Int, _ minYear: Int, _ maxYear: Int) -> CalendarError? {
        if month < 1 || month > 12 {
            return CalendarError(errorCode: .invalidMonth, message: "Month must be between 1 and 12, got \(month)", field: "month", value: month)
        }
        if year < minYear || year > maxYear {
            return CalendarError(errorCode: .invalidYear, message: "Year must be between \(minYear) and \(maxYear), got \(year)", field: "year", value: year)
        }
        let maxDay = gregorianMonthLength(year, month)
        if day < 1 || day > maxDay {
            return CalendarError(errorCode: .invalidDay, message: "Day must be between 1 and \(maxDay) for \(year)-\(String(format: "%02d", month)), got \(day)", field: "day", value: day)
        }
        return nil
    }
    
    static func validateHijri(_ year: Int, _ month: Int, _ day: Int, _ monthIndex: [String: MonthInfo]) -> CalendarError? {
        if month < 1 || month > 12 {
            return CalendarError(errorCode: .invalidMonth, message: "Month must be between 1 and 12, got \(month)", field: "month", value: month)
        }
        if year < 1300 || year > 1700 {
            return CalendarError(errorCode: .invalidYear, message: "Year must be between 1300 and 1700, got \(year)", field: "year", value: year)
        }
        let key = "\(year)-\(month)"
        guard let entry = monthIndex[key] else {
            return CalendarError(errorCode: .outOfRange, message: "Hijri date \(key) is outside the supported range")
        }
        if day < 1 || day > entry.monthLength {
            return CalendarError(errorCode: .invalidDay, message: "Day \(day) does not exist in Hijri month \(key), which has \(entry.monthLength) days", field: "day", value: day)
        }
        return nil
    }
    
    static func buildMonthIndex(_ months: [MonthInfo]) -> [String: MonthInfo] {
        var index: [String: MonthInfo] = [:]
        for month in months {
            let key = "\(month.hijriYear)-\(month.hijriMonth)"
            index[key] = month
        }
        return index
    }
    
    static func buildJdnIndex(_ months: [MonthInfo]) -> [MonthInfo] {
        return months.sorted { $0.firstDayJdn < $1.firstDayJdn }
    }
    
    static func getGregorianYearRange(_ months: [MonthInfo]) -> (Int, Int) {
        guard !months.isEmpty else { return (0, 0) }
        let first = jdnToGregorian(months[0].firstDayJdn)
        let last = months.last!
        let lastJdn = last.firstDayJdn + last.monthLength - 1
        let lastGreg = jdnToGregorian(lastJdn)
        return (first.year, lastGreg.year)
    }
}
