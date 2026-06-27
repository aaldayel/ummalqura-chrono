package com.ummalqura;

/**
 * Month information from the data table
 */
public class MonthInfo {
    private final int hijriYear;
    private final int hijriMonth;
    private final int monthLength;
    private final int firstDayJdn;

    public MonthInfo(int hijriYear, int hijriMonth, int monthLength, int firstDayJdn) {
        this.hijriYear = hijriYear;
        this.hijriMonth = hijriMonth;
        this.monthLength = monthLength;
        this.firstDayJdn = firstDayJdn;
    }

    public int getHijriYear() { return hijriYear; }
    public int getHijriMonth() { return hijriMonth; }
    public int getMonthLength() { return monthLength; }
    public int getFirstDayJdn() { return firstDayJdn; }
}
