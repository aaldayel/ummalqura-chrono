<?php

namespace UmmAlQura;

class MonthCalendar
{
    public function __construct(
        private string $calendar,
        private int $year,
        private int $month,
        private array $days,
        private string $monthNameEn,
        private string $monthNameAr
    ) {}

    public function getCalendar(): string { return $this->calendar; }
    public function getYear(): int { return $this->year; }
    public function getMonth(): int { return $this->month; }
    public function getDays(): array { return $this->days; }
    public function getMonthNameEn(): string { return $this->monthNameEn; }
    public function getMonthNameAr(): string { return $this->monthNameAr; }

    public function toArray(): array
    {
        return [
            'calendar' => $this->calendar,
            'year' => $this->year,
            'month' => $this->month,
            'days' => array_map(fn(DayInfo $d) => $d->toArray(), $this->days),
            'month_name_en' => $this->monthNameEn,
            'month_name_ar' => $this->monthNameAr,
        ];
    }
}
