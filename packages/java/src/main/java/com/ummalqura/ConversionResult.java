package com.ummalqura;

/**
 * Conversion result
 */
public class ConversionResult {
    private final Object input;
    private final Object output;
    private final int jdn;
    private final DayOfWeek dayOfWeek;
    private final String locale;
    private final String libraryVersion;
    private final String dataVersion;

    public ConversionResult(Object input, Object output, int jdn, DayOfWeek dayOfWeek,
                          String locale, String libraryVersion, String dataVersion) {
        this.input = input;
        this.output = output;
        this.jdn = jdn;
        this.dayOfWeek = dayOfWeek;
        this.locale = locale;
        this.libraryVersion = libraryVersion;
        this.dataVersion = dataVersion;
    }

    public Object getInput() { return input; }
    public Object getOutput() { return output; }
    public int getJdn() { return jdn; }
    public DayOfWeek getDayOfWeek() { return dayOfWeek; }
    public String getLocale() { return locale; }
    public String getLibraryVersion() { return libraryVersion; }
    public String getDataVersion() { return dataVersion; }
}
