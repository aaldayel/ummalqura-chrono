import 'types.dart';

/// Core conversion algorithms for Umm al-Qura calendar.
/// All functions are pure, deterministic, and stateless.
class Core {
  static const _umalQuraLeapYears = {2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29};
  static const _daysEn = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
  static const _daysAr = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
  static const _gregorianMonthDays = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

  static bool isGregorianLeapYear(int year) {
    return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0);
  }

  static int gregorianMonthLength(int year, int month) {
    if (month == 2 && isGregorianLeapYear(year)) return 29;
    return _gregorianMonthDays[month];
  }

  static bool isUmAlQuraLeapYear(int year) {
    return _umalQuraLeapYears.contains(year % 30);
  }

  static int gregorianToJdn(int year, int month, int day) {
    final a = (14 - month) ~/ 12;
    final y = year + 4800 - a;
    final m = month + 12 * a - 3;
    return day + (153 * m + 2) ~/ 5 + 365 * y + y ~/ 4 - y ~/ 100 + y ~/ 400 - 32045;
  }

  static GregorianDate jdnToGregorian(int jdn) {
    final a = jdn + 32044;
    final b = (4 * a + 3) ~/ 146097;
    final c = a - (146097 * b) ~/ 4;
    final d = (4 * c + 3) ~/ 1461;
    final e = c - (1461 * d) ~/ 4;
    final m = (5 * e + 2) ~/ 153;
    final day = e - (153 * m + 2) ~/ 5 + 1;
    final month = m + 3 - 12 * (m ~/ 10);
    final year = 100 * b + d - 4800 + m ~/ 10;
    return GregorianDate(year, month, day);
  }

  static DayOfWeek dayOfWeekFromJdn(int jdn) {
    final index = (jdn + 1) % 7;
    return DayOfWeek(index, _daysEn[index], _daysAr[index]);
  }

  static int hijriToJdn(int year, int month, int day, Map<String, MonthInfo> monthIndex) {
    final key = '$year-$month';
    final entry = monthIndex[key];
    if (entry == null) {
      throw CalendarError(
        ErrorCode.outOfRange,
        'Hijri date $key is outside the supported range (1300-1700 AH)',
      );
    }
    return entry.firstDayJdn + day - 1;
  }

  static HijriDate jdnToHijri(int jdn, List<MonthInfo> sortedMonths) {
    if (sortedMonths.isEmpty) {
      throw CalendarError(ErrorCode.outOfRange, 'Month table is empty');
    }
    if (jdn < sortedMonths[0].firstDayJdn) {
      throw CalendarError(ErrorCode.outOfRange, 'JDN $jdn is before the supported range (first JDN: ${sortedMonths[0].firstDayJdn})');
    }

    var left = 0;
    var right = sortedMonths.length - 1;

    while (left < right) {
      final mid = (left + right) ~/ 2;
      if (sortedMonths[mid].firstDayJdn <= jdn) {
        left = mid + 1;
      } else {
        right = mid;
      }
    }

    if (left >= sortedMonths.length) {
      left = sortedMonths.length - 1;
    } else if (left > 0 && sortedMonths[left].firstDayJdn > jdn) {
      left--;
    }

    final entry = sortedMonths[left];
    final day = jdn - entry.firstDayJdn + 1;
    return HijriDate(entry.hijriYear, entry.hijriMonth, day);
  }

  static CalendarError? validateGregorian(int year, int month, int day, int minYear, int maxYear) {
    if (month < 1 || month > 12) {
      return CalendarError(ErrorCode.invalidMonth, 'Month must be between 1 and 12, got $month', field: 'month', value: month);
    }
    if (year < minYear || year > maxYear) {
      return CalendarError(ErrorCode.invalidYear, 'Year must be between $minYear and $maxYear, got $year', field: 'year', value: year);
    }
    final maxDay = gregorianMonthLength(year, month);
    if (day < 1 || day > maxDay) {
      return CalendarError(ErrorCode.invalidDay, 'Day must be between 1 and $maxDay for $year-${month.toString().padLeft(2, '0')}, got $day', field: 'day', value: day);
    }
    return null;
  }

  static CalendarError? validateHijri(int year, int month, int day, Map<String, MonthInfo> monthIndex) {
    if (month < 1 || month > 12) {
      return CalendarError(ErrorCode.invalidMonth, 'Month must be between 1 and 12, got $month', field: 'month', value: month);
    }
    if (year < 1300 || year > 1700) {
      return CalendarError(ErrorCode.invalidYear, 'Year must be between 1300 and 1700, got $year', field: 'year', value: year);
    }
    final key = '$year-$month';
    final entry = monthIndex[key];
    if (entry == null) {
      return CalendarError(ErrorCode.outOfRange, 'Hijri date $key is outside the supported range');
    }
    if (day < 1 || day > entry.monthLength) {
      return CalendarError(ErrorCode.invalidDay, 'Day $day does not exist in Hijri month $key, which has ${entry.monthLength} days', field: 'day', value: day);
    }
    return null;
  }

  static Map<String, MonthInfo> buildMonthIndex(List<MonthInfo> months) {
    final index = <String, MonthInfo>{};
    for (final month in months) {
      index['${month.hijriYear}-${month.hijriMonth}'] = month;
    }
    return index;
  }

  static List<MonthInfo> buildJdnIndex(List<MonthInfo> months) {
    final sorted = List<MonthInfo>.from(months);
    sorted.sort((a, b) => a.firstDayJdn.compareTo(b.firstDayJdn));
    return sorted;
  }

  static (int, int) getGregorianYearRange(List<MonthInfo> months) {
    if (months.isEmpty) return (0, 0);
    final first = jdnToGregorian(months.first.firstDayJdn);
    final last = months.last;
    final lastJdn = last.firstDayJdn + last.monthLength - 1;
    final lastGreg = jdnToGregorian(lastJdn);
    return (first.year, lastGreg.year);
  }
}
