package com.ummalqura;

import java.util.*;

/**
 * Core conversion algorithms for Umm al-Qura calendar.
 * All methods are pure, deterministic, and stateless.
 */
final class Core {
    private static final Set<Integer> UMAL_QURA_LEAP_YEARS = new HashSet<>(Arrays.asList(2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29));
    private static final String[] DAYS_EN = {"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"};
    private static final String[] DAYS_AR = {"الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"};
    private static final int[] GREGORIAN_MONTH_DAYS = {0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};

    private Core() {}

    static boolean isGregorianLeapYear(int year) {
        return (year % 4 == 0) && (year % 100 != 0 || year % 400 == 0);
    }

    static int gregorianMonthLength(int year, int month) {
        if (month == 2 && isGregorianLeapYear(year)) return 29;
        return GREGORIAN_MONTH_DAYS[month];
    }

    static boolean isUmAlQuraLeapYear(int year) {
        return UMAL_QURA_LEAP_YEARS.contains(year % 30);
    }

    static int gregorianToJdn(int year, int month, int day) {
        int a = (14 - month) / 12;
        int y = year + 4800 - a;
        int m = month + 12 * a - 3;
        return day + (153 * m + 2) / 5 + 365 * y + y / 4 - y / 100 + y / 400 - 32045;
    }

    static GregorianDate jdnToGregorian(int jdn) {
        int a = jdn + 32044;
        int b = (4 * a + 3) / 146097;
        int c = a - (146097 * b) / 4;
        int d = (4 * c + 3) / 1461;
        int e = c - (1461 * d) / 4;
        int m = (5 * e + 2) / 153;
        int day = e - (153 * m + 2) / 5 + 1;
        int month = m + 3 - 12 * (m / 10);
        int year = 100 * b + d - 4800 + m / 10;
        return new GregorianDate(year, month, day);
    }

    static DayOfWeek dayOfWeekFromJdn(int jdn) {
        int index = (jdn + 1) % 7;
        return new DayOfWeek(index, DAYS_EN[index], DAYS_AR[index]);
    }

    static int hijriToJdn(int year, int month, int day, Map<String, MonthInfo> monthIndex) {
        String key = year + "-" + month;
        MonthInfo entry = monthIndex.get(key);
        if (entry == null) {
            throw new CalendarError(ErrorCode.OUT_OF_RANGE,
                "Hijri date " + year + "-" + String.format("%02d", month) + " is outside the supported range");
        }
        return entry.getFirstDayJdn() + day - 1;
    }

    static HijriDate jdnToHijri(int jdn, MonthInfo[] sortedMonths) {
        if (sortedMonths.length == 0) {
            throw new CalendarError(ErrorCode.OUT_OF_RANGE, "Month table is empty");
        }
        if (jdn < sortedMonths[0].getFirstDayJdn()) {
            throw new CalendarError(ErrorCode.OUT_OF_RANGE,
                "JDN " + jdn + " is before the supported range (first JDN: " + sortedMonths[0].getFirstDayJdn() + ")");
        }

        MonthInfo lastMonth = sortedMonths[sortedMonths.length - 1];
        int lastValidJdn = lastMonth.getFirstDayJdn() + lastMonth.getMonthLength() - 1;
        if (jdn > lastValidJdn) {
            throw new CalendarError(ErrorCode.OUT_OF_RANGE,
                "JDN " + jdn + " is after the supported range (last JDN: " + lastValidJdn + ")");
        }

        int left = 0;
        int right = sortedMonths.length - 1;

        while (left < right) {
            int mid = (left + right) / 2;
            if (sortedMonths[mid].getFirstDayJdn() <= jdn) {
                left = mid + 1;
            } else {
                right = mid;
            }
        }

        if (left >= sortedMonths.length) {
            left = sortedMonths.length - 1;
        } else if (left > 0 && sortedMonths[left].getFirstDayJdn() > jdn) {
            left--;
        }

        MonthInfo entry = sortedMonths[left];
        int day = jdn - entry.getFirstDayJdn() + 1;
        return new HijriDate(entry.getHijriYear(), entry.getHijriMonth(), day);
    }

    static CalendarError validateGregorian(int year, int month, int day, int minYear, int maxYear) {
        if (month < 1 || month > 12) {
            return new CalendarError(ErrorCode.INVALID_MONTH,
                "Month must be between 1 and 12, got " + month, "month", month);
        }
        if (year < minYear || year > maxYear) {
            return new CalendarError(ErrorCode.INVALID_YEAR,
                "Year must be between " + minYear + " and " + maxYear + ", got " + year, "year", year);
        }
        int maxDay = gregorianMonthLength(year, month);
        if (day < 1 || day > maxDay) {
            return new CalendarError(ErrorCode.INVALID_DAY,
                "Day must be between 1 and " + maxDay + " for " + year + "-" + String.format("%02d", month) + ", got " + day, "day", day);
        }
        return null;
    }

    static CalendarError validateHijri(int year, int month, int day, Map<String, MonthInfo> monthIndex) {
        if (month < 1 || month > 12) {
            return new CalendarError(ErrorCode.INVALID_MONTH,
                "Month must be between 1 and 12, got " + month, "month", month);
        }
        int minYear = monthIndex.values().stream().mapToInt(MonthInfo::getHijriYear).min().orElse(1318);
        int maxYear = monthIndex.values().stream().mapToInt(MonthInfo::getHijriYear).max().orElse(1500);
        if (year < minYear || year > maxYear) {
            return new CalendarError(ErrorCode.INVALID_YEAR,
                "Year must be between " + minYear + " and " + maxYear + ", got " + year, "year", year);
        }
        String key = year + "-" + month;
        MonthInfo entry = monthIndex.get(key);
        if (entry == null) {
            return new CalendarError(ErrorCode.OUT_OF_RANGE,
                "Hijri date " + year + "-" + String.format("%02d", month) + " is outside the supported range");
        }
        if (day < 1 || day > entry.getMonthLength()) {
            return new CalendarError(ErrorCode.INVALID_DAY,
                "Day " + day + " does not exist in Hijri month " + year + "-" + String.format("%02d", month) +
                ", which has " + entry.getMonthLength() + " days", "day", day);
        }
        return null;
    }

    static Map<String, MonthInfo> buildMonthIndex(List<MonthInfo> months) {
        Map<String, MonthInfo> index = new HashMap<>(months.size());
        for (MonthInfo month : months) {
            index.put(month.getHijriYear() + "-" + month.getHijriMonth(), month);
        }
        return index;
    }

    static MonthInfo[] buildJdnIndex(List<MonthInfo> months) {
        MonthInfo[] sorted = months.toArray(new MonthInfo[0]);
        Arrays.sort(sorted, Comparator.comparingInt(MonthInfo::getFirstDayJdn));
        return sorted;
    }

    static int[] getGregorianYearRange(List<MonthInfo> months) {
        if (months.isEmpty()) return new int[]{0, 0};
        GregorianDate first = jdnToGregorian(months.get(0).getFirstDayJdn());
        MonthInfo last = months.get(months.size() - 1);
        int lastJdn = last.getFirstDayJdn() + last.getMonthLength() - 1;
        GregorianDate lastGreg = jdnToGregorian(lastJdn);
        return new int[]{first.getYear(), lastGreg.getYear()};
    }
}
