<?php

namespace UmmAlQura;

class MonthInfo
{
    public function __construct(
        private int $hijriYear,
        private int $hijriMonth,
        private int $monthLength,
        private int $firstDayJdn
    ) {}

    public function getHijriYear(): int { return $this->hijriYear; }
    public function getHijriMonth(): int { return $this->hijriMonth; }
    public function getMonthLength(): int { return $this->monthLength; }
    public function getFirstDayJdn(): int { return $this->firstDayJdn; }

    public function toArray(): array
    {
        return [
            'hijri_year' => $this->hijriYear,
            'hijri_month' => $this->hijriMonth,
            'month_length' => $this->monthLength,
            'first_day_jdn' => $this->firstDayJdn,
        ];
    }
}
