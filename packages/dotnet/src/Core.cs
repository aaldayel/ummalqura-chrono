namespace UmmAlQura;

/// <summary>
/// Core conversion algorithms for Umm al-Qura calendar.
/// All methods are pure, deterministic, and stateless.
/// </summary>
internal static class Core
{
    // Umm al-Qura leap year positions (mod 30)
    private static readonly HashSet<int> UmAlQuraLeapYears = new() { 2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29 };

    // Day of week names
    private static readonly string[] DaysEn = { "Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday" };
    private static readonly string[] DaysAr = { "الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت" };

    // Gregorian month lengths (non-leap year)
    private static readonly int[] GregorianMonthDays = { 0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31 };

    /// <summary>
    /// Check if a Gregorian year is a leap year
    /// </summary>
    public static bool IsGregorianLeapYear(int year)
    {
        return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0);
    }

    /// <summary>
    /// Get the number of days in a Gregorian month
    /// </summary>
    public static int GregorianMonthLength(int year, int month)
    {
        if (month == 2 && IsGregorianLeapYear(year))
            return 29;
        return GregorianMonthDays[month];
    }

    /// <summary>
    /// Check if a Hijri year is a leap year in Umm al-Qura calendar
    /// </summary>
    public static bool IsUmAlQuraLeapYear(int year)
    {
        return UmAlQuraLeapYears.Contains(year % 30);
    }

    /// <summary>
    /// Convert Gregorian date to Julian Day Number (JDN)
    /// Algorithm: Fliegel &amp; Van Flandern (1968)
    /// </summary>
    public static int GregorianToJdn(int year, int month, int day)
    {
        var a = (14 - month) / 12;
        var y = year + 4800 - a;
        var m = month + 12 * a - 3;

        return day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
    }

    /// <summary>
    /// Convert Julian Day Number (JDN) to Gregorian date
    /// Algorithm: Fliegel &amp; Van Flandern (1968), inverse
    /// </summary>
    public static GregorianDate JdnToGregorian(int jdn)
    {
        var a = jdn + 32044;
        var b = (4 * a + 3) / 146097;
        var c = a - (146097 * b) / 4;
        var d = (4 * c + 3) / 1461;
        var e = c - (1461 * d) / 4;
        var m = (5 * e + 2) / 153;

        var day = e - (153 * m + 2) / 5 + 1;
        var month = m + 3 - 12 * (m / 10);
        var year = 100 * b + d - 4800 + m / 10;

        return new GregorianDate(year, month, day);
    }

    /// <summary>
    /// Calculate day of week from JDN
    /// </summary>
    public static DayOfWeek DayOfWeekFromJdn(int jdn)
    {
        var index = (jdn + 1) % 7;
        return new DayOfWeek(index, DaysEn[index], DaysAr[index]);
    }

    /// <summary>
    /// Convert Hijri date to Julian Day Number (JDN)
    /// </summary>
    public static int HijriToJdn(int year, int month, int day, Dictionary<string, MonthInfo> monthIndex)
    {
        var key = $"{year}-{month}";
        if (!monthIndex.TryGetValue(key, out var entry))
        {
            throw new CalendarError(
                ErrorCode.OutOfRange,
                $"Hijri date {year}-{month:D2} is outside the supported range"
            );
        }
        return entry.FirstDayJdn + day - 1;
    }

    /// <summary>
    /// Convert Julian Day Number (JDN) to Hijri date using binary search
    /// </summary>
    public static HijriDate JdnToHijri(int jdn, MonthInfo[] sortedMonths)
    {
        if (sortedMonths.Length == 0)
        {
            throw new CalendarError(ErrorCode.OutOfRange, "Month table is empty");
        }
        if (jdn < sortedMonths[0].FirstDayJdn)
        {
            throw new CalendarError(ErrorCode.OutOfRange, $"JDN {jdn} is before the supported range (first JDN: {sortedMonths[0].FirstDayJdn})");
        }

        var lastMonth = sortedMonths[^1];
        var lastValidJdn = lastMonth.FirstDayJdn + lastMonth.MonthLength - 1;
        if (jdn > lastValidJdn)
        {
            throw new CalendarError(ErrorCode.OutOfRange, $"JDN {jdn} is after the supported range (last JDN: {lastValidJdn})");
        }

        var left = 0;
        var right = sortedMonths.Length - 1;

        while (left < right)
        {
            var mid = (left + right) / 2;
            if (sortedMonths[mid].FirstDayJdn <= jdn)
                left = mid + 1;
            else
                right = mid;
        }

        if (left >= sortedMonths.Length)
            left = sortedMonths.Length - 1;
        else if (left > 0 && sortedMonths[left].FirstDayJdn > jdn)
            left--;

        var entry = sortedMonths[left];
        var day = jdn - entry.FirstDayJdn + 1;

        return new HijriDate(entry.HijriYear, entry.HijriMonth, day);
    }

    /// <summary>
    /// Validate a Gregorian date
    /// </summary>
    public static CalendarError? ValidateGregorian(int year, int month, int day, int minYear, int maxYear)
    {
        if (month < 1 || month > 12)
            return new CalendarError(ErrorCode.InvalidMonth, $"Month must be between 1 and 12, got {month}", "month", month);

        if (year < minYear || year > maxYear)
            return new CalendarError(ErrorCode.InvalidYear, $"Year must be between {minYear} and {maxYear}, got {year}", "year", year);

        var maxDay = GregorianMonthLength(year, month);
        if (day < 1 || day > maxDay)
            return new CalendarError(ErrorCode.InvalidDay, $"Day must be between 1 and {maxDay} for {year}-{month:D2}, got {day}", "day", day);

        return null;
    }

    /// <summary>
    /// Validate a Hijri date
    /// </summary>
    public static CalendarError? ValidateHijri(int year, int month, int day, Dictionary<string, MonthInfo> monthIndex)
    {
        if (month < 1 || month > 12)
            return new CalendarError(ErrorCode.InvalidMonth, $"Month must be between 1 and 12, got {month}", "month", month);

        var minYear = monthIndex.Values.Min(m => m.HijriYear);
        var maxYear = monthIndex.Values.Max(m => m.HijriYear);
        if (year < minYear || year > maxYear)
            return new CalendarError(ErrorCode.InvalidYear, $"Year must be between {minYear} and {maxYear}, got {year}", "year", year);

        var key = $"{year}-{month}";
        if (!monthIndex.TryGetValue(key, out var entry))
            return new CalendarError(ErrorCode.OutOfRange, $"Hijri date {year}-{month:D2} is outside the supported range");

        if (day < 1 || day > entry.MonthLength)
            return new CalendarError(ErrorCode.InvalidDay, $"Day {day} does not exist in Hijri month {year}-{month:D2}, which has {entry.MonthLength} days", "day", day);

        return null;
    }

    /// <summary>
    /// Build an index for fast month lookup
    /// </summary>
    public static Dictionary<string, MonthInfo> BuildMonthIndex(IReadOnlyList<MonthInfo> months)
    {
        var index = new Dictionary<string, MonthInfo>(months.Count);
        foreach (var month in months)
        {
            index[$"{month.HijriYear}-{month.HijriMonth}"] = month;
        }
        return index;
    }

    /// <summary>
    /// Build a sorted array for binary search by JDN
    /// </summary>
    public static MonthInfo[] BuildJdnIndex(IReadOnlyList<MonthInfo> months)
    {
        var sorted = new MonthInfo[months.Count];
        months.CopyTo(sorted, 0);
        Array.Sort(sorted, (a, b) => a.FirstDayJdn.CompareTo(b.FirstDayJdn));
        return sorted;
    }

    /// <summary>
    /// Get the Gregorian year range from month data
    /// </summary>
    public static (int Min, int Max) GetGregorianYearRange(IReadOnlyList<MonthInfo> months)
    {
        if (months.Count == 0) return (0, 0);

        var firstGregorian = JdnToGregorian(months[0].FirstDayJdn);
        var lastMonth = months[months.Count - 1];
        var lastJdn = lastMonth.FirstDayJdn + lastMonth.MonthLength - 1;
        var lastGregorian = JdnToGregorian(lastJdn);

        return (firstGregorian.Year, lastGregorian.Year);
    }
}
