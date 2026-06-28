package com.ummalqura

internal object Core {
    private val UMAL_QURA_LEAP_YEARS = setOf(2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29)
    private val DAYS_EN = arrayOf("Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday")
    private val DAYS_AR = arrayOf("الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت")
    private val GREGORIAN_MONTH_DAYS = intArrayOf(0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)

    fun isGregorianLeapYear(year: Int): Boolean {
        return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0)
    }

    fun gregorianMonthLength(year: Int, month: Int): Int {
        if (month == 2 && isGregorianLeapYear(year)) return 29
        return GREGORIAN_MONTH_DAYS[month]
    }

    fun isUmAlQuraLeapYear(year: Int): Boolean {
        return (year % 30) in UMAL_QURA_LEAP_YEARS
    }

    fun gregorianToJdn(year: Int, month: Int, day: Int): Int {
        val a = (14 - month) / 12
        val y = year + 4800 - a
        val m = month + 12 * a - 3
        return day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045
    }

    fun jdnToGregorian(jdn: Int): GregorianDate {
        val a = jdn + 32044
        val b = (4 * a + 3) / 146097
        val c = a - (146097 * b) / 4
        val d = (4 * c + 3) / 1461
        val e = c - (1461 * d) / 4
        val m = (5 * e + 2) / 153
        val day = e - (153 * m + 2) / 5 + 1
        val month = m + 3 - 12 * (m / 10)
        val year = 100 * b + d - 4800 + m / 10
        return GregorianDate(year, month, day)
    }

    fun dayOfWeekFromJdn(jdn: Int): DayOfWeek {
        val index = (jdn + 1) % 7
        return DayOfWeek(index, DAYS_EN[index], DAYS_AR[index])
    }

    fun hijriToJdn(year: Int, month: Int, day: Int, monthIndex: Map<String, MonthInfo>): Int {
        val key = "$year-$month"
        val entry = monthIndex[key] ?: throw CalendarError(
            ErrorCode.OUT_OF_RANGE,
            "Hijri date $key is outside the supported range"
        )
        return entry.firstDayJdn + day - 1
    }

    fun jdnToHijri(jdn: Int, sortedMonths: Array<MonthInfo>): HijriDate {
        if (sortedMonths.isEmpty()) {
            throw CalendarError(ErrorCode.OUT_OF_RANGE, "Month table is empty")
        }
        if (jdn < sortedMonths[0].firstDayJdn) {
            throw CalendarError(ErrorCode.OUT_OF_RANGE, "JDN $jdn is before the supported range (first JDN: ${sortedMonths[0].firstDayJdn})")
        }

        val lastMonth = sortedMonths[sortedMonths.size - 1]
        val lastValidJdn = lastMonth.firstDayJdn + lastMonth.monthLength - 1
        if (jdn > lastValidJdn) {
            throw CalendarError(ErrorCode.OUT_OF_RANGE, "JDN $jdn is after the supported range (last JDN: $lastValidJdn)")
        }

        var left = 0
        var right = sortedMonths.size - 1

        while (left < right) {
            val mid = (left + right) / 2
            if (sortedMonths[mid].firstDayJdn <= jdn) {
                left = mid + 1
            } else {
                right = mid
            }
        }

        if (left >= sortedMonths.size) {
            left = sortedMonths.size - 1
        } else if (left > 0 && sortedMonths[left].firstDayJdn > jdn) {
            left--
        }

        val entry = sortedMonths[left]
        val day = jdn - entry.firstDayJdn + 1
        return HijriDate(entry.hijriYear, entry.hijriMonth, day)
    }

    fun validateGregorian(year: Int, month: Int, day: Int, minYear: Int, maxYear: Int): CalendarError? {
        if (month < 1 || month > 12) {
            return CalendarError(ErrorCode.INVALID_MONTH, "Month must be between 1 and 12, got $month", "month", month)
        }
        if (year < minYear || year > maxYear) {
            return CalendarError(ErrorCode.INVALID_YEAR, "Year must be between $minYear and $maxYear, got $year", "year", year)
        }
        val maxDay = gregorianMonthLength(year, month)
        if (day < 1 || day > maxDay) {
            return CalendarError(ErrorCode.INVALID_DAY, "Day must be between 1 and $maxDay for $year-${month.toString().padStart(2, '0')}, got $day", "day", day)
        }
        return null
    }

    fun validateHijri(year: Int, month: Int, day: Int, monthIndex: Map<String, MonthInfo>): CalendarError? {
        if (month < 1 || month > 12) {
            return CalendarError(ErrorCode.INVALID_MONTH, "Month must be between 1 and 12, got $month", "month", month)
        }
        val minYear = monthIndex.values.minOfOrNull { it.hijriYear } ?: 1318
        val maxYear = monthIndex.values.maxOfOrNull { it.hijriYear } ?: 1500
        if (year < minYear || year > maxYear) {
            return CalendarError(ErrorCode.INVALID_YEAR, "Year must be between $minYear and $maxYear, got $year", "year", year)
        }
        val key = "$year-$month"
        val entry = monthIndex[key] ?: return CalendarError(ErrorCode.OUT_OF_RANGE, "Hijri date $key is outside the supported range")
        if (day < 1 || day > entry.monthLength) {
            return CalendarError(ErrorCode.INVALID_DAY, "Day $day does not exist in Hijri month $key, which has ${entry.monthLength} days", "day", day)
        }
        return null
    }

    fun buildMonthIndex(months: List<MonthInfo>): Map<String, MonthInfo> {
        return months.associateBy { "${it.hijriYear}-${it.hijriMonth}" }
    }

    fun buildJdnIndex(months: List<MonthInfo>): Array<MonthInfo> {
        return months.sortedBy { it.firstDayJdn }.toTypedArray()
    }

    fun getGregorianYearRange(months: List<MonthInfo>): Pair<Int, Int> {
        if (months.isEmpty()) return Pair(0, 0)
        val first = jdnToGregorian(months.first().firstDayJdn)
        val last = months.last()
        val lastJdn = last.firstDayJdn + last.monthLength - 1
        val lastGreg = jdnToGregorian(lastJdn)
        return Pair(first.year, lastGreg.year)
    }
}
