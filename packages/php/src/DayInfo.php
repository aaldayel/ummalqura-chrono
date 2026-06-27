<?php

namespace UmmAlQura;

class DayInfo
{
    public function __construct(
        private GregorianDate $gregorian,
        private HijriDate $hijri,
        private int $jdn,
        private DayOfWeek $dayOfWeek
    ) {}

    public function getGregorian(): GregorianDate { return $this->gregorian; }
    public function getHijri(): HijriDate { return $this->hijri; }
    public function getJdn(): int { return $this->jdn; }
    public function getDayOfWeek(): DayOfWeek { return $this->dayOfWeek; }

    public function toArray(): array
    {
        return [
            'gregorian' => $this->gregorian->toArray(),
            'hijri' => $this->hijri->toArray(),
            'jdn' => $this->jdn,
            'day_of_week' => $this->dayOfWeek->toArray(),
        ];
    }
}
