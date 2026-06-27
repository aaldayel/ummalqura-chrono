<?php

namespace UmmAlQura;

class ConversionResult
{
    public function __construct(
        private GregorianDate|HijriDate $input,
        private GregorianDate|HijriDate $output,
        private int $jdn,
        private DayOfWeek $dayOfWeek,
        private string $locale,
        private string $libraryVersion,
        private string $dataVersion
    ) {}

    public function getInput(): GregorianDate|HijriDate { return $this->input; }
    public function getOutput(): GregorianDate|HijriDate { return $this->output; }
    public function getJdn(): int { return $this->jdn; }
    public function getDayOfWeek(): DayOfWeek { return $this->dayOfWeek; }
    public function getLocale(): string { return $this->locale; }
    public function getLibraryVersion(): string { return $this->libraryVersion; }
    public function getDataVersion(): string { return $this->dataVersion; }

    public function toArray(): array
    {
        return [
            'input' => $this->input->toArray(),
            'output' => $this->output->toArray(),
            'jdn' => $this->jdn,
            'day_of_week' => $this->dayOfWeek->toArray(),
            'locale' => $this->locale,
            'library_version' => $this->libraryVersion,
            'data_version' => $this->dataVersion,
        ];
    }
}
