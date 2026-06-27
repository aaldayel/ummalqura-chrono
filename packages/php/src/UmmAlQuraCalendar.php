<?php

namespace UmmAlQura;

class UmmAlQuraCalendar
{
    private const LIBRARY_VERSION = '1.0.0';
    private const GREGORIAN_MONTHS_EN = [
        'January', 'February', 'March', 'April', 'May', 'June',
        'July', 'August', 'September', 'October', 'November', 'December'
    ];
    private const GREGORIAN_MONTHS_AR = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ];
    private const HIJRI_MONTHS_EN = [
        'Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani',
        'Jumada al-Ula', 'Jumada al-Thani', 'Rajab', 'Sha\'ban',
        'Ramadan', 'Shawwal', 'Dhul Qi\'dah', 'Dhul Hijjah'
    ];
    private const HIJRI_MONTHS_AR = [
        'محرم', 'صفر', 'ربيع الأول', 'ربيع الثاني',
        'جمادى الأولى', 'جمادى الثانية', 'رجب', 'شعبان',
        'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'
    ];

    private array $months;
    private array $monthIndex;
    private array $sortedMonths;
    private array $gregorianYearRange;
    private string $dataVersion;
    private string $dataChecksum;
    private int $hijriRangeStart;
    private int $hijriRangeEnd;
    private string $defaultLocale;

    public function __construct(?string $dataPath = null, string $defaultLocale = 'en')
    {
        $this->defaultLocale = $defaultLocale;

        $dataPath = $dataPath ?? $this->findDataFile();
        $json = file_get_contents($dataPath);
        if ($json === false) {
            throw new \RuntimeException("Failed to read data file: $dataPath");
        }
        $data = json_decode($json, true);

        $this->dataVersion = $data['version'];
        $this->dataChecksum = $data['checksum'];
        $this->hijriRangeStart = $data['hijri_range']['start'];
        $this->hijriRangeEnd = $data['hijri_range']['end'];

        $this->months = array_map(function ($m) {
            return new MonthInfo(
                $m['hijri_year'],
                $m['hijri_month'],
                $m['month_length'],
                $m['first_day_jdn']
            );
        }, $data['months']);

        $this->monthIndex = Core::buildMonthIndex($this->months);
        $this->sortedMonths = Core::buildJdnIndex($this->months);
        $this->gregorianYearRange = Core::getGregorianYearRange($this->months);
    }

    private function findDataFile(): string
    {
        $paths = [
            __DIR__ . '/../../../data/ummalqura-months.json',
            __DIR__ . '/../../../../data/ummalqura-months.json',
            __DIR__ . '/../../data/ummalqura-months.json',
            getcwd() . '/data/ummalqura-months.json',
        ];

        foreach ($paths as $path) {
            if (file_exists($path)) {
                return $path;
            }
        }

        throw new \RuntimeException('Could not find ummalqura-months.json data file');
    }

    public function getVersion(): string
    {
        return self::LIBRARY_VERSION;
    }

    public function getDataVersion(): string
    {
        return $this->dataVersion;
    }

    public function getDataChecksum(): string
    {
        return $this->dataChecksum;
    }

    public function getHijriRange(): array
    {
        return ['start' => $this->hijriRangeStart, 'end' => $this->hijriRangeEnd];
    }

    public function getGregorianRange(): array
    {
        return ['min' => $this->gregorianYearRange[0], 'max' => $this->gregorianYearRange[1]];
    }

    public function gregorianToHijri(int $year, int $month, int $day, ?string $locale = null): ConversionResult
    {
        $error = Core::validateGregorian($year, $month, $day, $this->gregorianYearRange[0], $this->gregorianYearRange[1]);
        if ($error !== null) {
            throw $error;
        }

        $jdn = Core::gregorianToJdn($year, $month, $day);
        $hijri = Core::jdnToHijri($jdn, $this->sortedMonths);
        $dow = Core::dayOfWeekFromJdn($jdn);

        return new ConversionResult(
            new GregorianDate($year, $month, $day),
            $hijri,
            $jdn,
            $dow,
            $locale ?? $this->defaultLocale,
            self::LIBRARY_VERSION,
            $this->dataVersion
        );
    }

    public function hijriToGregorian(int $year, int $month, int $day, ?string $locale = null): ConversionResult
    {
        $error = Core::validateHijri($year, $month, $day, $this->monthIndex);
        if ($error !== null) {
            throw $error;
        }

        $jdn = Core::hijriToJdn($year, $month, $day, $this->monthIndex);
        $gregorian = Core::jdnToGregorian($jdn);
        $dow = Core::dayOfWeekFromJdn($jdn);

        return new ConversionResult(
            new HijriDate($year, $month, $day),
            $gregorian,
            $jdn,
            $dow,
            $locale ?? $this->defaultLocale,
            self::LIBRARY_VERSION,
            $this->dataVersion
        );
    }

    public function validateGregorianDate(int $year, int $month, int $day): ValidationResult
    {
        $error = Core::validateGregorian($year, $month, $day, $this->gregorianYearRange[0], $this->gregorianYearRange[1]);
        return new ValidationResult($error === null, $error);
    }

    public function validateHijriDate(int $year, int $month, int $day): ValidationResult
    {
        $error = Core::validateHijri($year, $month, $day, $this->monthIndex);
        return new ValidationResult($error === null, $error);
    }

    public function getDayOfWeek(int $jdn): DayOfWeek
    {
        return Core::dayOfWeekFromJdn($jdn);
    }

    public function getDayOfWeekGregorian(int $year, int $month, int $day): DayOfWeek
    {
        return Core::dayOfWeekFromJdn(Core::gregorianToJdn($year, $month, $day));
    }

    public function getDayOfWeekHijri(int $year, int $month, int $day): DayOfWeek
    {
        return Core::dayOfWeekFromJdn(Core::hijriToJdn($year, $month, $day, $this->monthIndex));
    }

    public function getGregorianMonthLength(int $year, int $month): int
    {
        return Core::gregorianMonthLength($year, $month);
    }

    public function getGregorianMonth(int $year, int $month, ?string $locale = null): MonthCalendar
    {
        $daysInMonth = Core::gregorianMonthLength($year, $month);
        $days = [];

        for ($day = 1; $day <= $daysInMonth; $day++) {
            $jdn = Core::gregorianToJdn($year, $month, $day);
            $hijri = Core::jdnToHijri($jdn, $this->sortedMonths);
            $dow = Core::dayOfWeekFromJdn($jdn);

            $days[] = new DayInfo(
                new GregorianDate($year, $month, $day),
                $hijri,
                $jdn,
                $dow
            );
        }

        $loc = $locale ?? $this->defaultLocale;
        $monthNameEn = self::GREGORIAN_MONTHS_EN[$month - 1];
        $monthNameAr = self::GREGORIAN_MONTHS_AR[$month - 1];

        return new MonthCalendar('gregorian', $year, $month, $days, $monthNameEn, $monthNameAr);
    }

    public function getHijriMonth(int $year, int $month, ?string $locale = null): MonthCalendar
    {
        $key = "$year-$month";
        if (!isset($this->monthIndex[$key])) {
            throw new CalendarError(ErrorCode::OUT_OF_RANGE, "Hijri date $key is outside the supported range");
        }

        $entry = $this->monthIndex[$key];
        $days = [];

        for ($day = 1; $day <= $entry->getMonthLength(); $day++) {
            $jdn = Core::hijriToJdn($year, $month, $day, $this->monthIndex);
            $gregorian = Core::jdnToGregorian($jdn);
            $dow = Core::dayOfWeekFromJdn($jdn);

            $days[] = new DayInfo(
                $gregorian,
                new HijriDate($year, $month, $day),
                $jdn,
                $dow
            );
        }

        $loc = $locale ?? $this->defaultLocale;
        $monthNameEn = self::HIJRI_MONTHS_EN[$month - 1];
        $monthNameAr = self::HIJRI_MONTHS_AR[$month - 1];

        return new MonthCalendar('hijri-ummalqura', $year, $month, $days, $monthNameEn, $monthNameAr);
    }

    public function getHijriMonthLength(int $year, int $month): int
    {
        $key = "$year-$month";
        if (!isset($this->monthIndex[$key])) {
            throw new CalendarError(ErrorCode::OUT_OF_RANGE, "Hijri date $key is outside the supported range");
        }
        return $this->monthIndex[$key]->getMonthLength();
    }

    public function isGregorianLeapYear(int $year): bool
    {
        return Core::isGregorianLeapYear($year);
    }

    public function batchGregorianToHijri(array $dates, ?string $locale = null): array
    {
        return array_map(fn($d) => $this->gregorianToHijri($d['year'], $d['month'], $d['day'], $locale), $dates);
    }

    public function batchHijriToGregorian(array $dates, ?string $locale = null): array
    {
        return array_map(fn($d) => $this->hijriToGregorian($d['year'], $d['month'], $d['day'], $locale), $dates);
    }
}
