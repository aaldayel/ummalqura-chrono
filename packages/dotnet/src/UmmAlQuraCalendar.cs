using System.Text.Json;

namespace UmmAlQura;

/// <summary>
/// Umm al-Qura Calendar Conversion Library
/// Provides methods for converting between Gregorian and Umm al-Qura calendars.
/// </summary>
public class UmmAlQuraCalendar
{
    private const string LibraryVersion = "1.0.0";
    
    private readonly MonthInfo[] _months;
    private readonly Dictionary<string, MonthInfo> _monthIndex;
    private readonly MonthInfo[] _sortedMonths;
    private readonly (int Min, int Max) _gregorianYearRange;
    private readonly string _dataVersion;
    private readonly string _dataChecksum;
    private readonly (int Start, int End) _hijriRange;
    private readonly string _defaultLocale;

    // Gregorian month names
    private static readonly string[] GregorianMonthsEn = {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    };
    private static readonly string[] GregorianMonthsAr = {
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    };

    // Hijri month names
    private static readonly string[] HijriMonthsEn = {
        "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
        "Jumada al-Ula", "Jumada al-Thani", "Rajab", "Sha'ban",
        "Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah"
    };
    private static readonly string[] HijriMonthsAr = {
        "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
        "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
    };

    /// <summary>
    /// Create a new UmmAlQuraCalendar instance
    /// </summary>
    /// <param name="dataPath">Optional path to the month-length table JSON file</param>
    /// <param name="defaultLocale">Default locale for names</param>
    public UmmAlQuraCalendar(string? dataPath = null, string defaultLocale = "en")
    {
        _defaultLocale = defaultLocale;
        
        // Find data file
        dataPath ??= FindDataFile();
        
        // Load and parse JSON
        var json = File.ReadAllText(dataPath);
        using var doc = JsonDocument.Parse(json);
        var root = doc.RootElement;

        _dataVersion = root.GetProperty("version").GetString() ?? "";
        _dataChecksum = root.GetProperty("checksum").GetString() ?? "";
        
        var range = root.GetProperty("hijri_range");
        _hijriRange = (range.GetProperty("start").GetInt32(), range.GetProperty("end").GetInt32());

        // Parse months
        var monthsArray = root.GetProperty("months");
        _months = new MonthInfo[monthsArray.GetArrayLength()];
        var i = 0;
        foreach (var item in monthsArray.EnumerateArray())
        {
            _months[i++] = new MonthInfo(
                item.GetProperty("hijri_year").GetInt32(),
                item.GetProperty("hijri_month").GetInt32(),
                item.GetProperty("month_length").GetInt32(),
                item.GetProperty("first_day_jdn").GetInt32()
            );
        }

        // Build indexes
        _monthIndex = Core.BuildMonthIndex(_months);
        _sortedMonths = Core.BuildJdnIndex(_months);
        _gregorianYearRange = Core.GetGregorianYearRange(_months);
    }

    private static string FindDataFile()
    {
        // Try common locations
        var paths = new[]
        {
            Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "data", "ummalqura-months.json"),
            Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "..", "..", "..", "data", "ummalqura-months.json"),
            Path.Combine(Directory.GetCurrentDirectory(), "data", "ummalqura-months.json"),
        };

        foreach (var path in paths)
        {
            if (File.Exists(path))
                return Path.GetFullPath(path);
        }

        throw new FileNotFoundException("Could not find ummalqura-months.json data file");
    }

    /// <summary>Get the library version</summary>
    public string Version => LibraryVersion;

    /// <summary>Get the data version</summary>
    public string DataVersion => _dataVersion;

    /// <summary>Get the data checksum</summary>
    public string DataChecksum => _dataChecksum;

    /// <summary>Get the supported Hijri year range</summary>
    public (int Start, int End) HijriRange => _hijriRange;

    /// <summary>Get the supported Gregorian year range</summary>
    public (int Min, int Max) GregorianRange => _gregorianYearRange;

    /// <summary>
    /// Convert a Gregorian date to Hijri (Umm al-Qura)
    /// </summary>
    public ConversionResult GregorianToHijri(int year, int month, int day, string? locale = null)
    {
        var error = Core.ValidateGregorian(year, month, day, _gregorianYearRange.Min, _gregorianYearRange.Max);
        if (error is not null) throw error;

        var jdn = Core.GregorianToJdn(year, month, day);
        var hijri = Core.JdnToHijri(jdn, _sortedMonths);
        var dow = Core.DayOfWeekFromJdn(jdn);

        return new ConversionResult(
            new GregorianCalendarDate(year, month, day),
            new HijriCalendarDate(hijri.Year, hijri.Month, hijri.Day),
            jdn, dow, locale ?? _defaultLocale, LibraryVersion, _dataVersion
        );
    }

    /// <summary>
    /// Convert a Hijri date to Gregorian
    /// </summary>
    public ConversionResult HijriToGregorian(int year, int month, int day, string? locale = null)
    {
        var error = Core.ValidateHijri(year, month, day, _monthIndex);
        if (error is not null) throw error;

        var jdn = Core.HijriToJdn(year, month, day, _monthIndex);
        var gregorian = Core.JdnToGregorian(jdn);
        var dow = Core.DayOfWeekFromJdn(jdn);

        return new ConversionResult(
            new HijriCalendarDate(year, month, day),
            new GregorianCalendarDate(gregorian.Year, gregorian.Month, gregorian.Day),
            jdn, dow, locale ?? _defaultLocale, LibraryVersion, _dataVersion
        );
    }

    /// <summary>Validate a Gregorian date</summary>
    public ValidationResult ValidateGregorianDate(int year, int month, int day)
    {
        var error = Core.ValidateGregorian(year, month, day, _gregorianYearRange.Min, _gregorianYearRange.Max);
        return new ValidationResult(error is null, error);
    }

    /// <summary>Validate a Hijri date</summary>
    public ValidationResult ValidateHijriDate(int year, int month, int day)
    {
        var error = Core.ValidateHijri(year, month, day, _monthIndex);
        return new ValidationResult(error is null, error);
    }

    /// <summary>Get day of week from JDN</summary>
    public DayOfWeek GetDayOfWeek(int jdn) => Core.DayOfWeekFromJdn(jdn);

    /// <summary>Get day of week for Gregorian date</summary>
    public DayOfWeek GetDayOfWeekGregorian(int year, int month, int day) =>
        Core.DayOfWeekFromJdn(Core.GregorianToJdn(year, month, day));

    /// <summary>Get day of week for Hijri date</summary>
    public DayOfWeek GetDayOfWeekHijri(int year, int month, int day) =>
        Core.DayOfWeekFromJdn(Core.HijriToJdn(year, month, day, _monthIndex));

    /// <summary>Get Gregorian month length</summary>
    public int GetGregorianMonthLength(int year, int month) => Core.GregorianMonthLength(year, month);

    /// <summary>Get Hijri month length</summary>
    public int GetHijriMonthLength(int year, int month)
    {
        var key = $"{year}-{month}";
        if (!_monthIndex.TryGetValue(key, out var entry))
            throw new CalendarError(ErrorCode.OutOfRange, $"Hijri date {year}-{month:D2} is outside the supported range");
        return entry.MonthLength;
    }

    /// <summary>Check if Gregorian year is leap year</summary>
    public bool IsGregorianLeapYear(int year) => Core.IsGregorianLeapYear(year);

    /// <summary>Batch convert Gregorian dates to Hijri</summary>
    public IReadOnlyList<ConversionResult> BatchGregorianToHijri(
        IReadOnlyList<(int Year, int Month, int Day)> dates, string? locale = null)
    {
        return dates.Select(d => GregorianToHijri(d.Year, d.Month, d.Day, locale)).ToList();
    }

    /// <summary>Batch convert Hijri dates to Gregorian</summary>
    public IReadOnlyList<ConversionResult> BatchHijriToGregorian(
        IReadOnlyList<(int Year, int Month, int Day)> dates, string? locale = null)
    {
        return dates.Select(d => HijriToGregorian(d.Year, d.Month, d.Day, locale)).ToList();
    }

    /// <summary>Get all days in a Gregorian month</summary>
    public MonthCalendar GetGregorianMonth(int year, int month, string? locale = null)
    {
        var daysInMonth = Core.GregorianMonthLength(year, month);
        var days = new List<DayInfo>(daysInMonth);

        for (var day = 1; day <= daysInMonth; day++)
        {
            var jdn = Core.GregorianToJdn(year, month, day);
            var hijri = Core.JdnToHijri(jdn, _sortedMonths);
            var dow = Core.DayOfWeekFromJdn(jdn);
            days.Add(new DayInfo(
                new GregorianDate(year, month, day),
                new HijriDate(hijri.Year, hijri.Month, hijri.Day),
                jdn, dow
            ));
        }

        return new MonthCalendar("gregorian", year, month, days,
            GregorianMonthsEn[month - 1], GregorianMonthsAr[month - 1]);
    }

    /// <summary>Get all days in a Hijri month</summary>
    public MonthCalendar GetHijriMonth(int year, int month, string? locale = null)
    {
        var key = $"{year}-{month}";
        if (!_monthIndex.TryGetValue(key, out var entry))
            throw new CalendarError(ErrorCode.OutOfRange, $"Hijri date {year}-{month:D2} is outside the supported range");

        var days = new List<DayInfo>(entry.MonthLength);
        for (var day = 1; day <= entry.MonthLength; day++)
        {
            var jdn = Core.HijriToJdn(year, month, day, _monthIndex);
            var gregorian = Core.JdnToGregorian(jdn);
            var dow = Core.DayOfWeekFromJdn(jdn);
            days.Add(new DayInfo(
                new GregorianDate(gregorian.Year, gregorian.Month, gregorian.Day),
                new HijriDate(year, month, day),
                jdn, dow
            ));
        }

        return new MonthCalendar("hijri-ummalqura", year, month, days,
            HijriMonthsEn[month - 1], HijriMonthsAr[month - 1]);
    }
}
