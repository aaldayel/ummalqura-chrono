<?php

namespace UmmAlQura;

class HijriDate
{
    public function __construct(
        private int $year,
        private int $month,
        private int $day
    ) {}

    public function getYear(): int { return $this->year; }
    public function getMonth(): int { return $this->month; }
    public function getDay(): int { return $this->day; }
    public function getCalendar(): string { return 'hijri-ummalqura'; }

    public function toArray(): array
    {
        return [
            'year' => $this->year,
            'month' => $this->month,
            'day' => $this->day,
            'calendar' => $this->getCalendar(),
        ];
    }
}
