package com.ummalqura;

/**
 * Gregorian date representation
 */
public class GregorianDate {
    private final int year;
    private final int month;
    private final int day;

    public GregorianDate(int year, int month, int day) {
        this.year = year;
        this.month = month;
        this.day = day;
    }

    public int getYear() { return year; }
    public int getMonth() { return month; }
    public int getDay() { return day; }
    public String getCalendar() { return "gregorian"; }

    @Override
    public String toString() {
        return String.format("%d-%02d-%02d", year, month, day);
    }
}
