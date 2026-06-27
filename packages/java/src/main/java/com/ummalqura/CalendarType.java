package com.ummalqura;

/**
 * Supported calendar systems
 */
public enum CalendarType {
    GREGORIAN("gregorian"),
    HIJRI_UMMALQURA("hijri-ummalqura");

    private final String value;

    CalendarType(String value) {
        this.value = value;
    }

    public String getValue() {
        return value;
    }
}
