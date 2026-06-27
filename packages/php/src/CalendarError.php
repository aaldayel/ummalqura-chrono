<?php

namespace UmmAlQura;

class CalendarError extends \Exception
{
    private ErrorCode $errorCode;
    private ?string $field;
    private mixed $value;

    public function __construct(ErrorCode $errorCode, string $message, ?string $field = null, mixed $value = null)
    {
        parent::__construct($message);
        $this->errorCode = $errorCode;
        $this->field = $field;
        $this->value = $value;
    }

    public function getErrorCode(): ErrorCode
    {
        return $this->errorCode;
    }

    public function getField(): ?string
    {
        return $this->field;
    }

    public function getValue(): mixed
    {
        return $this->value;
    }

    public function toArray(): array
    {
        $result = [
            'error_code' => $this->errorCode->value,
            'message' => $this->getMessage(),
        ];
        if ($this->field !== null) {
            $result['field'] = $this->field;
        }
        if ($this->value !== null) {
            $result['value'] = $this->value;
        }
        return $result;
    }

    public function toJson(): array
    {
        return $this->toArray();
    }
}
