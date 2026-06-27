/// Supported calendar systems
enum CalendarType {
  gregorian,
  hijriUmAlQura,
}

/// Error codes for structured error responses
enum ErrorCode {
  invalidDay,
  invalidMonth,
  invalidYear,
  outOfRange,
  unsupportedCalendar,
  invalidTimezone,
  malformedInput,
}

/// Gregorian date representation
class GregorianDate {
  final int year;
  final int month;
  final int day;
  final String calendar = 'gregorian';

  GregorianDate(this.year, this.month, this.day);

  Map<String, dynamic> toJson() => {
    'year': year,
    'month': month,
    'day': day,
    'calendar': calendar,
  };
}

/// Hijri (Umm al-Qura) date representation
class HijriDate {
  final int year;
  final int month;
  final int day;
  final String calendar = 'hijri-ummalqura';

  HijriDate(this.year, this.month, this.day);

  Map<String, dynamic> toJson() => {
    'year': year,
    'month': month,
    'day': day,
    'calendar': calendar,
  };
}

/// Day of week information
class DayOfWeek {
  final int index;
  final String nameEn;
  final String nameAr;

  DayOfWeek(this.index, this.nameEn, this.nameAr);

  Map<String, dynamic> toJson() => {
    'index': index,
    'name_en': nameEn,
    'name_ar': nameAr,
  };
}

/// Conversion result
class ConversionResult {
  final dynamic input;
  final dynamic output;
  final int jdn;
  final DayOfWeek dayOfWeek;
  final String locale;
  final String libraryVersion;
  final String dataVersion;

  ConversionResult({
    required this.input,
    required this.output,
    required this.jdn,
    required this.dayOfWeek,
    required this.locale,
    required this.libraryVersion,
    required this.dataVersion,
  });

  Map<String, dynamic> toJson() => {
    'input': input is GregorianDate ? (input as GregorianDate).toJson() : (input as HijriDate).toJson(),
    'output': output is GregorianDate ? (output as GregorianDate).toJson() : (output as HijriDate).toJson(),
    'jdn': jdn,
    'day_of_week': dayOfWeek.toJson(),
    'locale': locale,
    'library_version': libraryVersion,
    'data_version': dataVersion,
  };
}

/// Structured error response
class CalendarError implements Exception {
  final ErrorCode errorCode;
  final String message;
  final String? field;
  final dynamic value;

  CalendarError(this.errorCode, this.message, {this.field, this.value});

  Map<String, dynamic> toJson() {
    final result = <String, dynamic>{
      'error_code': errorCode.name,
      'message': message,
    };
    if (field != null) result['field'] = field;
    if (value != null) result['value'] = value;
    return result;
  }

  @override
  String toString() => message;
}

/// Validation result
class ValidationResult {
  final bool valid;
  final CalendarError? error;

  ValidationResult(this.valid, {this.error});

  Map<String, dynamic> toJson() {
    final result = <String, dynamic>{'valid': valid};
    if (error != null) result['error'] = error!.toJson();
    return result;
  }
}

/// Month information from the data table
class MonthInfo {
  final int hijriYear;
  final int hijriMonth;
  final int monthLength;
  final int firstDayJdn;

  MonthInfo(this.hijriYear, this.hijriMonth, this.monthLength, this.firstDayJdn);
}

/// Day information for calendar view
class DayInfo {
  final GregorianDate gregorian;
  final HijriDate hijri;
  final int jdn;
  final DayOfWeek dayOfWeek;

  DayInfo({
    required this.gregorian,
    required this.hijri,
    required this.jdn,
    required this.dayOfWeek,
  });

  Map<String, dynamic> toJson() => {
    'gregorian': gregorian.toJson(),
    'hijri': hijri.toJson(),
    'jdn': jdn,
    'day_of_week': dayOfWeek.toJson(),
  };
}

/// Month calendar response
class MonthCalendar {
  final String calendar;
  final int year;
  final int month;
  final List<DayInfo> days;
  final String monthNameEn;
  final String monthNameAr;

  MonthCalendar({
    required this.calendar,
    required this.year,
    required this.month,
    required this.days,
    required this.monthNameEn,
    required this.monthNameAr,
  });

  Map<String, dynamic> toJson() => {
    'calendar': calendar,
    'year': year,
    'month': month,
    'days': days.map((d) => d.toJson()).toList(),
    'month_name_en': monthNameEn,
    'month_name_ar': monthNameAr,
  };
}
