<?php

namespace UmmAlQura;

final class Core
{
    private const UMAL_QURA_LEAP_YEARS = [2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29];
    private const DAYS_EN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
    private const DAYS_AR = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];
    private const GREGORIAN_MONTH_DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

    private function __construct() {}

    public static function isGregorianLeapYear(int $year): bool
    {
        return ($year % 4 === 0) && ($year % 100 !== 0 || $year % 400 === 0);
    }

    public static function gregorianMonthLength(int $year, int $month): int
    {
        if ($month === 2 && self::isGregorianLeapYear($year)) {
            return 29;
        }
        return self::GREGORIAN_MONTH_DAYS[$month];
    }

    public static function isUmAlQuraLeapYear(int $year): bool
    {
        return in_array($year % 30, self::UMAL_QURA_LEAP_YEARS);
    }

    public static function gregorianToJdn(int $year, int $month, int $day): int
    {
        $a = intdiv(14 - $month, 12);
        $y = $year + 4800 - $a;
        $m = $month + 12 * $a - 3;
        return $day + intdiv(153 * $m + 2, 5) + 365 * $y + intdiv($y, 4) - intdiv($y, 100) + intdiv($y, 400) - 32045;
    }

    public static function jdnToGregorian(int $jdn): GregorianDate
    {
        $a = $jdn + 32044;
        $b = intdiv(4 * $a + 3, 146097);
        $c = $a - intdiv(146097 * $b, 4);
        $d = intdiv(4 * $c + 3, 1461);
        $e = $c - intdiv(1461 * $d, 4);
        $m = intdiv(5 * $e + 2, 153);

        $day = $e - intdiv(153 * $m + 2, 5) + 1;
        $month = $m + 3 - 12 * intdiv($m, 10);
        $year = 100 * $b + $d - 4800 + intdiv($m, 10);

        return new GregorianDate($year, $month, $day);
    }

    public static function dayOfWeekFromJdn(int $jdn): DayOfWeek
    {
        $index = ($jdn + 1) % 7;
        return new DayOfWeek($index, self::DAYS_EN[$index], self::DAYS_AR[$index]);
    }

    public static function hijriToJdn(int $year, int $month, int $day, array $monthIndex): int
    {
        $key = "$year-$month";
        if (!isset($monthIndex[$key])) {
            throw new CalendarError(
                ErrorCode::OUT_OF_RANGE,
                "Hijri date $key is outside the supported range (1300-1700 AH)"
            );
        }
        return $monthIndex[$key]->getFirstDayJdn() + $day - 1;
    }

    public static function jdnToHijri(int $jdn, array $sortedMonths): HijriDate
    {
        if (count($sortedMonths) === 0) {
            throw new CalendarError(ErrorCode::OUT_OF_RANGE, 'Month table is empty');
        }
        if ($jdn < $sortedMonths[0]->getFirstDayJdn()) {
            throw new CalendarError(ErrorCode::OUT_OF_RANGE, "JDN $jdn is before the supported range (first JDN: {$sortedMonths[0]->getFirstDayJdn()})");
        }

        $left = 0;
        $right = count($sortedMonths) - 1;

        while ($left < $right) {
            $mid = intdiv($left + $right, 2);
            if ($sortedMonths[$mid]->getFirstDayJdn() <= $jdn) {
                $left = $mid + 1;
            } else {
                $right = $mid;
            }
        }

        if ($left === count($sortedMonths)) {
            $left = count($sortedMonths) - 1;
        } elseif ($left > 0 && $sortedMonths[$left]->getFirstDayJdn() > $jdn) {
            $left--;
        }

        $entry = $sortedMonths[$left];
        $day = $jdn - $entry->getFirstDayJdn() + 1;

        return new HijriDate($entry->getHijriYear(), $entry->getHijriMonth(), $day);
    }

    public static function validateGregorian(int $year, int $month, int $day, int $minYear, int $maxYear): ?CalendarError
    {
        if ($month < 1 || $month > 12) {
            return new CalendarError(ErrorCode::INVALID_MONTH, "Month must be between 1 and 12, got $month", 'month', $month);
        }
        if ($year < $minYear || $year > $maxYear) {
            return new CalendarError(ErrorCode::INVALID_YEAR, "Year must be between $minYear and $maxYear, got $year", 'year', $year);
        }
        $maxDay = self::gregorianMonthLength($year, $month);
        if ($day < 1 || $day > $maxDay) {
            return new CalendarError(ErrorCode::INVALID_DAY, "Day must be between 1 and $maxDay for $year-" . sprintf('%02d', $month) . ", got $day", 'day', $day);
        }
        return null;
    }

    public static function validateHijri(int $year, int $month, int $day, array $monthIndex): ?CalendarError
    {
        if ($month < 1 || $month > 12) {
            return new CalendarError(ErrorCode::INVALID_MONTH, "Month must be between 1 and 12, got $month", 'month', $month);
        }
        $minYear = !empty($monthIndex) ? min(array_map(fn($m) => $m->getHijriYear(), $monthIndex)) : 1300;
        $maxYear = !empty($monthIndex) ? max(array_map(fn($m) => $m->getHijriYear(), $monthIndex)) : 1700;
        if ($year < $minYear || $year > $maxYear) {
            return new CalendarError(ErrorCode::INVALID_YEAR, "Year must be between $minYear and $maxYear, got $year", 'year', $year);
        }
        $key = "$year-$month";
        if (!isset($monthIndex[$key])) {
            return new CalendarError(ErrorCode::OUT_OF_RANGE, "Hijri date $key is outside the supported range");
        }
        $entry = $monthIndex[$key];
        if ($day < 1 || $day > $entry->getMonthLength()) {
            return new CalendarError(ErrorCode::INVALID_DAY, "Day $day does not exist in Hijri month $key, which has " . $entry->getMonthLength() . " days", 'day', $day);
        }
        return null;
    }

    public static function buildMonthIndex(array $months): array
    {
        $index = [];
        foreach ($months as $month) {
            $key = $month->getHijriYear() . '-' . $month->getHijriMonth();
            $index[$key] = $month;
        }
        return $index;
    }

    public static function buildJdnIndex(array $months): array
    {
        $sorted = $months;
        usort($sorted, fn($a, $b) => $a->getFirstDayJdn() <=> $b->getFirstDayJdn());
        return $sorted;
    }

    public static function getGregorianYearRange(array $months): array
    {
        if (empty($months)) {
            return [0, 0];
        }
        $sorted = self::buildJdnIndex($months);
        $first = self::jdnToGregorian($sorted[0]->getFirstDayJdn());
        $last = $sorted[count($sorted) - 1];
        $lastJdn = $last->getFirstDayJdn() + $last->getMonthLength() - 1;
        $lastGreg = self::jdnToGregorian($lastJdn);
        return [$first->getYear(), $lastGreg->getYear()];
    }
}
