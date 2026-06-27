package com.ummalqura;

/**
 * Validation result
 */
public class ValidationResult {
    private final boolean valid;
    private final CalendarError error;

    public ValidationResult(boolean valid, CalendarError error) {
        this.valid = valid;
        this.error = error;
    }

    public boolean isValid() { return valid; }
    public CalendarError getError() { return error; }
}
