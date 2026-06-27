import 'dart:convert';
import 'dart:io';
import 'package:path/path.dart' as path;
import 'types.dart';
import 'core.dart';

const _libraryVersion = '1.0.0';

const _gregorianMonthsEn = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December'
];
const _gregorianMonthsAr = [
  'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
  'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
];
const _hijriMonthsEn = [
  'Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani',
  'Jumada al-Ula', 'Jumada al-Thani', 'Rajab', 'Sha\'ban',
  'Ramadan', 'Shawwal', 'Dhul Qi\'dah', 'Dhul Hijjah'
];
const _hijriMonthsAr = [
  'محرم', 'صفر', 'ربيع الأول', 'ربيع الثاني',
  'جمادى الأولى', 'جمادى الثانية', 'رجب', 'شعبان',
  'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
];

/// Umm al-Qura Calendar Conversion Library
class UmmAlQuraCalendar {
  late final List<MonthInfo> _months;
  late final Map<String, MonthInfo> _monthIndex;
  late final List<MonthInfo> _sortedMonths;
  late final (int, int) _gregorianYearRange;
  late final String _dataVersion;
  late final String _dataChecksum;
  late final (int, int) _hijriRange;
  final String _defaultLocale;

  UmmAlQuraCalendar({String? dataPath, String defaultLocale = 'en'})
      : _defaultLocale = defaultLocale {
    dataPath ??= _findDataFile();
    final json = File(dataPath).readAsStringSync();
    final data = jsonDecode(json);

    _dataVersion = data['version'];
    _dataChecksum = data['checksum'];
    _hijriRange = (data['hijri_range']['start'], data['hijri_range']['end']);

    final monthsList = (data['months'] as List).map((m) => MonthInfo(
      m['hijri_year'],
      m['hijri_month'],
      m['month_length'],
      m['first_day_jdn'],
    )).toList();

    _months = monthsList;
    _monthIndex = Core.buildMonthIndex(_months);
    _sortedMonths = Core.buildJdnIndex(_months);
    _gregorianYearRange = Core.getGregorianYearRange(_months);
  }

  String _findDataFile() {
    final scriptDir = path.dirname(Platform.script.toFilePath());
    final paths = [
      path.join(scriptDir, '..', '..', '..', 'data', 'ummalqura-months.json'),
      path.join(scriptDir, '..', 'data', 'ummalqura-months.json'),
      path.join(Directory.current.path, 'data', 'ummalqura-months.json'),
    ];

    for (final p in paths) {
      if (File(p).existsSync()) return p;
    }

    throw FileSystemException('Could not find ummalqura-months.json data file');
  }

  String get version => _libraryVersion;
  String get dataVersion => _dataVersion;
  String get dataChecksum => _dataChecksum;
  (int, int) get hijriRange => _hijriRange;
  (int, int) get gregorianRange => _gregorianYearRange;

  ConversionResult gregorianToHijri(int year, int month, int day, {String? locale}) {
    final error = Core.validateGregorian(year, month, day, _gregorianYearRange.$1, _gregorianYearRange.$2);
    if (error != null) throw error;

    final jdn = Core.gregorianToJdn(year, month, day);
    final hijri = Core.jdnToHijri(jdn, _sortedMonths);
    final dow = Core.dayOfWeekFromJdn(jdn);

    return ConversionResult(
      input: GregorianDate(year, month, day),
      output: hijri,
      jdn: jdn,
      dayOfWeek: dow,
      locale: locale ?? _defaultLocale,
      libraryVersion: _libraryVersion,
      dataVersion: _dataVersion,
    );
  }

  ConversionResult hijriToGregorian(int year, int month, int day, {String? locale}) {
    final error = Core.validateHijri(year, month, day, _monthIndex);
    if (error != null) throw error;

    final jdn = Core.hijriToJdn(year, month, day, _monthIndex);
    final gregorian = Core.jdnToGregorian(jdn);
    final dow = Core.dayOfWeekFromJdn(jdn);

    return ConversionResult(
      input: HijriDate(year, month, day),
      output: gregorian,
      jdn: jdn,
      dayOfWeek: dow,
      locale: locale ?? _defaultLocale,
      libraryVersion: _libraryVersion,
      dataVersion: _dataVersion,
    );
  }

  ValidationResult validateGregorianDate(int year, int month, int day) {
    final error = Core.validateGregorian(year, month, day, _gregorianYearRange.$1, _gregorianYearRange.$2);
    return ValidationResult(error == null, error: error);
  }

  ValidationResult validateHijriDate(int year, int month, int day) {
    final error = Core.validateHijri(year, month, day, _monthIndex);
    return ValidationResult(error == null, error: error);
  }

  DayOfWeek getDayOfWeek(int jdn) => Core.dayOfWeekFromJdn(jdn);

  DayOfWeek getDayOfWeekGregorian(int year, int month, int day) =>
      Core.dayOfWeekFromJdn(Core.gregorianToJdn(year, month, day));

  DayOfWeek getDayOfWeekHijri(int year, int month, int day) =>
      Core.dayOfWeekFromJdn(Core.hijriToJdn(year, month, day, _monthIndex));

  int getGregorianMonthLength(int year, int month) => Core.gregorianMonthLength(year, month);

  int getHijriMonthLength(int year, int month) {
    final key = '$year-$month';
    final entry = _monthIndex[key];
    if (entry == null) {
      throw CalendarError(ErrorCode.outOfRange, 'Hijri date $key is outside the supported range');
    }
    return entry.monthLength;
  }

  MonthCalendar getGregorianMonth(int year, int month, {String? locale}) {
    final daysInMonth = Core.gregorianMonthLength(year, month);
    final days = <DayInfo>[];

    for (var day = 1; day <= daysInMonth; day++) {
      final jdn = Core.gregorianToJdn(year, month, day);
      final hijri = Core.jdnToHijri(jdn, _sortedMonths);
      final dow = Core.dayOfWeekFromJdn(jdn);

      days.add(DayInfo(
        gregorian: GregorianDate(year, month, day),
        hijri: hijri,
        jdn: jdn,
        dayOfWeek: dow,
      ));
    }

    final loc = locale ?? _defaultLocale;
    final monthNameEn = _gregorianMonthsEn[month - 1];
    final monthNameAr = _gregorianMonthsAr[month - 1];

    return MonthCalendar(
      calendar: 'gregorian',
      year: year,
      month: month,
      days: days,
      monthNameEn: monthNameEn,
      monthNameAr: monthNameAr,
    );
  }

  MonthCalendar getHijriMonth(int year, int month, {String? locale}) {
    final key = '$year-$month';
    final entry = _monthIndex[key];
    if (entry == null) {
      throw CalendarError(ErrorCode.outOfRange, 'Hijri date $key is outside the supported range');
    }

    final days = <DayInfo>[];
    for (var day = 1; day <= entry.monthLength; day++) {
      final jdn = Core.hijriToJdn(year, month, day, _monthIndex);
      final gregorian = Core.jdnToGregorian(jdn);
      final dow = Core.dayOfWeekFromJdn(jdn);

      days.add(DayInfo(
        gregorian: gregorian,
        hijri: HijriDate(year, month, day),
        jdn: jdn,
        dayOfWeek: dow,
      ));
    }

    final loc = locale ?? _defaultLocale;
    final monthNameEn = _hijriMonthsEn[month - 1];
    final monthNameAr = _hijriMonthsAr[month - 1];

    return MonthCalendar(
      calendar: 'hijri-ummalqura',
      year: year,
      month: month,
      days: days,
      monthNameEn: monthNameEn,
      monthNameAr: monthNameAr,
    );
  }

  bool isGregorianLeapYear(int year) => Core.isGregorianLeapYear(year);

  List<ConversionResult> batchGregorianToHijri(List<Map<String, int>> dates, {String? locale}) {
    return dates.map((d) => gregorianToHijri(d['year']!, d['month']!, d['day']!, locale: locale)).toList();
  }

  List<ConversionResult> batchHijriToGregorian(List<Map<String, int>> dates, {String? locale}) {
    return dates.map((d) => hijriToGregorian(d['year']!, d['month']!, d['day']!, locale: locale)).toList();
  }
}
