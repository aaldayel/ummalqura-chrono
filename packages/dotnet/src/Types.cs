namespace UmmAlQura;

/// <summary>
/// Supported calendar systems
/// </summary>
public enum CalendarType
{
    Gregorian,
    HijriUmAlQura
}

/// <summary>
/// Error codes for structured error responses
/// </summary>
public enum ErrorCode
{
    InvalidDay,
    InvalidMonth,
    InvalidYear,
    OutOfRange,
    UnsupportedCalendar,
    InvalidTimezone,
    MalformedInput
}

/// <summary>
/// Gregorian date representation
/// </summary>
public record GregorianDate(int Year, int Month, int Day)
{
    public string Calendar => "gregorian";
}

/// <summary>
/// Hijri (Umm al-Qura) date representation
/// </summary>
public record HijriDate(int Year, int Month, int Day)
{
    public string Calendar => "hijri-ummalqura";
}

/// <summary>
/// Day of week information
/// </summary>
public record DayOfWeek(int Index, string NameEn, string NameAr);

/// <summary>
/// Conversion result
/// </summary>
public record ConversionResult(
    CalendarDate Input,
    CalendarDate Output,
    int Jdn,
    DayOfWeek DayOfWeek,
    string Locale,
    string LibraryVersion,
    string DataVersion
);

/// <summary>
/// Base record for calendar dates
/// </summary>
public abstract record CalendarDate
{
    public abstract int Year { get; }
    public abstract int Month { get; }
    public abstract int Day { get; }
    public abstract string Calendar { get; }
}

/// <summary>
/// Gregorian calendar date
/// </summary>
public record GregorianCalendarDate(int Year, int Month, int Day) : CalendarDate
{
    public override string Calendar => "gregorian";
}

/// <summary>
/// Hijri calendar date
/// </summary>
public record HijriCalendarDate(int Year, int Month, int Day) : CalendarDate
{
    public override string Calendar => "hijri-ummalqura";
}

/// <summary>
/// Structured error response
/// </summary>
public record CalendarError(
    ErrorCode ErrorCode,
    string Message,
    string? Field = null,
    object? Value = null
) : Exception(Message);

/// <summary>
/// Validation result
/// </summary>
public record ValidationResult(bool Valid, CalendarError? Error = null);

/// <summary>
/// Month information from the data table
/// </summary>
public record MonthInfo(int HijriYear, int HijriMonth, int MonthLength, int FirstDayJdn);

/// <summary>
/// Day information for calendar view
/// </summary>
public record DayInfo(
    GregorianDate Gregorian,
    HijriDate Hijri,
    int Jdn,
    DayOfWeek DayOfWeek,
    bool IsToday = false
);

/// <summary>
/// Month calendar response
/// </summary>
public record MonthCalendar(
    string Calendar,
    int Year,
    int Month,
    IReadOnlyList<DayInfo> Days,
    string MonthNameEn,
    string MonthNameAr
);
