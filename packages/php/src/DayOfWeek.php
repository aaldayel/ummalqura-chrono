<?php

namespace UmmAlQura;

class DayOfWeek
{
    public function __construct(
        private int $index,
        private string $nameEn,
        private string $nameAr
    ) {}

    public function getIndex(): int { return $this->index; }
    public function getNameEn(): string { return $this->nameEn; }
    public function getNameAr(): string { return $this->nameAr; }

    public function toArray(): array
    {
        return [
            'index' => $this->index,
            'name_en' => $this->nameEn,
            'name_ar' => $this->nameAr,
        ];
    }
}
