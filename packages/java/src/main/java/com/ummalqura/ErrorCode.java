package com.ummalqura;

/**
 * Error codes for structured error responses
 */
public enum ErrorCode {
    INVALID_DAY("INVALID_DAY"),
    INVALID_MONTH("INVALID_MONTH"),
    INVALID_YEAR("INVALID_YEAR"),
    OUT_OF_RANGE("OUT_OF_RANGE"),
    UNSUPPORTED_CALENDAR("UNSUPPORTED_CALENDAR"),
    INVALID_TIMEZONE("INVALID_TIMEZONE"),
    MALFORMED_INPUT("MALFORMED_INPUT");

    private final String value;

    ErrorCode(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
