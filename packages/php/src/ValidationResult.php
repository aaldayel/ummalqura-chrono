<?php

namespace UmmAlQura;

class ValidationResult
{
    public function __construct(
        private bool $valid,
        private ?CalendarError $error = null
    ) {}

    public function isValid(): bool { return $this->valid; }
    public function getError(): ?CalendarError { return $this->error; }

    public function toArray(): array
    {
        $result = ['valid' => $this->valid];
        if ($this->error !== null) {
            $result['error'] = $this->error->toJson();
        }
        return $result;
    }
}
