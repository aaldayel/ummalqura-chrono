package com.ummalqura;

/**
 * Day of week information
 */
public class DayOfWeek {
    private final int index;
    private final String nameEn;
    private final String nameAr;

    public DayOfWeek(int index, String nameEn, String nameAr) {
        this.index = index;
        this.nameEn = nameEn;
        this.nameAr = nameAr;
    }

    public int getIndex() { return index; }
    public String getNameEn() { return nameEn; }
    public String getNameAr() { return nameAr; }
}
