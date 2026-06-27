package com.ummalqura;

/**
 * Hijri (Umm al-Qura) date representation
 */
public class HijriDate {
    private final int year;
    private final int month;
    private final int day;

    public HijriDate(int year, int month, int day) {
        this.year = year;
        this.month = month;
        this.day = day;
    }

    public int getYear() { return year; }
    public int getMonth() { return month; }
    public int getDay() { return day; }
    public String getCalendar() { return "hijri-ummalqura"; }

    @Override
    public String toString() {
        return String.format("%d-%02d-%02d", year, month, day);
    }
}
