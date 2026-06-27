package com.ummalqura;

import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonElement;
import com.google.gson.JsonObject;

import java.io.*;
import java.nio.charset.StandardCharsets;
import java.util.*;
import java.util.stream.Collectors;

/**
 * Umm al-Qura Calendar Conversion Library
 * Provides methods for converting between Gregorian and Umm al-Qura calendars.
 */
public class UmmAlQuraCalendar {
    private static final String LIBRARY_VERSION = "1.0.0";
    
    private final MonthInfo[] months;
    private final Map<String, MonthInfo> monthIndex;
    private final MonthInfo[] sortedMonths;
    private final int[] gregorianYearRange;
    private final String dataVersion;
    private final String dataChecksum;
    private final int hijriRangeStart;
    private final int hijriRangeEnd;
    private final String defaultLocale;

    private static final String[] GREGORIAN_MONTHS_EN = {
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"
    };
    private static final String[] GREGORIAN_MONTHS_AR = {
        "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
        "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
    };
    private static final String[] HIJRI_MONTHS_EN = {
        "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
        "Jumada al-Ula", "Jumada al-Thani", "Rajab", "Sha'ban",
        "Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah"
    };
    private static final String[] HIJRI_MONTHS_AR = {
        "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
        "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
        "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
    };

    public UmmAlQuraCalendar() {
        this(null, "en");
    }

    public UmmAlQuraCalendar(String dataPath, String defaultLocale) {
        this.defaultLocale = defaultLocale != null ? defaultLocale : "en";
        
        try {
            String json;
            if (dataPath != null) {
                json = new String(java.nio.file.Files.readAllBytes(java.nio.file.Paths.get(dataPath)), StandardCharsets.UTF_8);
            } else {
                InputStream is = getClass().getClassLoader().getResourceAsStream("data/ummalqura-months.json");
                if (is == null) {
                    // Try file system
                    File f = new File("../../data/ummalqura-months.json");
                    if (f.exists()) {
                        json = new String(java.nio.file.Files.readAllBytes(f.toPath()), StandardCharsets.UTF_8);
                    } else {
                        throw new FileNotFoundException("Data file not found");
                    }
                } else {
                    json = new String(is.readAllBytes(), StandardCharsets.UTF_8);
                }
            }

            Gson gson = new Gson();
            JsonObject root = gson.fromJson(json, JsonObject.class);
            
            this.dataVersion = root.get("version").getAsString();
            this.dataChecksum = root.get("checksum").getAsString();
            
            JsonObject range = root.getAsJsonObject("hijri_range");
            this.hijriRangeStart = range.get("start").getAsInt();
            this.hijriRangeEnd = range.get("end").getAsInt();

            JsonArray monthsArray = root.getAsJsonArray("months");
            this.months = new MonthInfo[monthsArray.size()];
            for (int i = 0; i < monthsArray.size(); i++) {
                JsonObject item = monthsArray.get(i).getAsJsonObject();
                this.months[i] = new MonthInfo(
                    item.get("hijri_year").getAsInt(),
                    item.get("hijri_month").getAsInt(),
                    item.get("month_length").getAsInt(),
                    item.get("first_day_jdn").getAsInt()
                );
            }

            List<MonthInfo> monthList = Arrays.asList(this.months);
            this.monthIndex = Core.buildMonthIndex(monthList);
            this.sortedMonths = Core.buildJdnIndex(monthList);
            this.gregorianYearRange = Core.getGregorianYearRange(monthList);

        } catch (IOException e) {
            throw new RuntimeException("Failed to load month table", e);
        }
    }

    public String getVersion() { return LIBRARY_VERSION; }
    public String getDataVersion() { return dataVersion; }
    public String getDataChecksum() { return dataChecksum; }
    public int getHijriRangeStart() { return hijriRangeStart; }
    public int getHijriRangeEnd() { return hijriRangeEnd; }
    public int getGregorianRangeMin() { return gregorianYearRange[0]; }
    public int getGregorianRangeMax() { return gregorianYearRange[1]; }

    public ConversionResult gregorianToHijri(int year, int month, int day) {
        return gregorianToHijri(year, month, day, null);
    }

    public ConversionResult gregorianToHijri(int year, int month, int day, String locale) {
        CalendarError error = Core.validateGregorian(year, month, day, gregorianYearRange[0], gregorianYearRange[1]);
        if (error != null) throw error;

        int jdn = Core.gregorianToJdn(year, month, day);
        HijriDate hijri = Core.jdnToHijri(jdn, sortedMonths);
        DayOfWeek dow = Core.dayOfWeekFromJdn(jdn);

        return new ConversionResult(
            new GregorianDate(year, month, day),
            new HijriDate(hijri.getYear(), hijri.getMonth(), hijri.getDay()),
            jdn, dow, locale != null ? locale : defaultLocale, LIBRARY_VERSION, dataVersion
        );
    }

    public ConversionResult hijriToGregorian(int year, int month, int day) {
        return hijriToGregorian(year, month, day, null);
    }

    public ConversionResult hijriToGregorian(int year, int month, int day, String locale) {
        CalendarError error = Core.validateHijri(year, month, day, monthIndex);
        if (error != null) throw error;

        int jdn = Core.hijriToJdn(year, month, day, monthIndex);
        GregorianDate gregorian = Core.jdnToGregorian(jdn);
        DayOfWeek dow = Core.dayOfWeekFromJdn(jdn);

        return new ConversionResult(
            new HijriDate(year, month, day),
            new GregorianDate(gregorian.getYear(), gregorian.getMonth(), gregorian.getDay()),
            jdn, dow, locale != null ? locale : defaultLocale, LIBRARY_VERSION, dataVersion
        );
    }

    public ValidationResult validateGregorianDate(int year, int month, int day) {
        CalendarError error = Core.validateGregorian(year, month, day, gregorianYearRange[0], gregorianYearRange[1]);
        return new ValidationResult(error == null, error);
    }

    public ValidationResult validateHijriDate(int year, int month, int day) {
        CalendarError error = Core.validateHijri(year, month, day, monthIndex);
        return new ValidationResult(error == null, error);
    }

    public DayOfWeek getDayOfWeek(int jdn) {
        return Core.dayOfWeekFromJdn(jdn);
    }

    public DayOfWeek getDayOfWeekGregorian(int year, int month, int day) {
        return Core.dayOfWeekFromJdn(Core.gregorianToJdn(year, month, day));
    }

    public DayOfWeek getDayOfWeekHijri(int year, int month, int day) {
        return Core.dayOfWeekFromJdn(Core.hijriToJdn(year, month, day, monthIndex));
    }

    public int getGregorianMonthLength(int year, int month) {
        return Core.gregorianMonthLength(year, month);
    }

    public int getHijriMonthLength(int year, int month) {
        String key = year + "-" + month;
        MonthInfo entry = monthIndex.get(key);
        if (entry == null) {
            throw new CalendarError(ErrorCode.OUT_OF_RANGE,
                "Hijri date " + year + "-" + String.format("%02d", month) + " is outside the supported range");
        }
        return entry.getMonthLength();
    }

    public boolean isGregorianLeapYear(int year) {
        return Core.isGregorianLeapYear(year);
    }

    public List<ConversionResult> batchGregorianToHijri(List<int[]> dates, String locale) {
        return dates.stream()
            .map(d -> gregorianToHijri(d[0], d[1], d[2], locale))
            .collect(Collectors.toList());
    }

    public List<ConversionResult> batchHijriToGregorian(List<int[]> dates, String locale) {
        return dates.stream()
            .map(d -> hijriToGregorian(d[0], d[1], d[2], locale))
            .collect(Collectors.toList());
    }
}
