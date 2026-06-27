<?php

namespace UmmAlQura;

class GregorianDate
{
    public function __construct(
        private int $year,
        private int $month,
        private int $day
    ) {}

    public function getYear(): int { return $this->year; }
    public function getMonth(): int { return $this->month; }
    public function getDay(): int { return $this->day; }
    public function getCalendar(): string { return 'gregorian'; }

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
