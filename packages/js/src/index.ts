/**
 * Umm al-Qura Calendar Conversion Library
 * 
 * Main entry point providing public API for calendar conversions.
 * All functions are pure, deterministic, and stateless.
 */

import * as fs from 'fs';
import * as path from 'path';
import {
  GregorianDate,
  HijriDate,
  CalendarDate,
  ConversionResult,
  DayOfWeek,
  MonthInfo,
  MonthTableData,
  MonthCalendar,
  DayInfo,
  ValidationResult,
  ConversionOptions,
  LibraryConfig,
  ErrorCode,
  CalendarError
} from './types.js';

import {
  gregorianToJdn,
  jdnToGregorian,
  hijriToJdn,
  jdnToHijri,
  dayOfWeekFromJdn,
  gregorianMonthLength,
  isGregorianLeapYear,
  validateGregorian,
  validateHijri,
  buildMonthIndex,
  buildJdnIndex,
  getGregorianYearRange,
  createError
} from './core.js';

import { getGregorianMonthName, getHijriMonthName } from './locale.js';

// Library version
const LIBRARY_VERSION = '1.0.0';

function findDataFile(): string {
  const paths = [
    path.join(__dirname, '..', '..', '..', 'data', 'ummalqura-months.json'),
    path.join(__dirname, '..', 'data', 'ummalqura-months.json'),
    path.join(__dirname, '..', '..', 'data', 'ummalqura-months.json'),
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return path.join(__dirname, '..', '..', 'data', 'ummalqura-months.json');
}

// Default data path
const DEFAULT_DATA_PATH = findDataFile();

/**
 * Umm al-Qura Calendar class
 * 
 * Provides methods for converting between Gregorian and Umm al-Qura calendars.
 * Loads the month-length table on initialization.
 */
export class UmmAlQuraCalendar {
  private monthTable: MonthTableData;
  private monthIndex: Map<string, MonthInfo>;
  private sortedMonths: MonthInfo[];
  private gregorianYearRange: { min: number; max: number };
  private defaultLocale: string;
  
  /**
   * Create a new UmmAlQuraCalendar instance
   * 
   * @param config - Optional configuration
   */
  constructor(config?: LibraryConfig) {
    const dataPath = config?.dataPath || DEFAULT_DATA_PATH;
    this.defaultLocale = config?.defaultLocale || 'en';
    
    // Load month table data
    try {
      const data = fs.readFileSync(dataPath, 'utf-8');
      this.monthTable = JSON.parse(data);
    } catch (error) {
      throw new Error(`Failed to load month table from ${dataPath}: ${error}`);
    }
    
    // Build indexes for fast lookup
    this.monthIndex = buildMonthIndex(this.monthTable.months);
    this.sortedMonths = buildJdnIndex(this.monthTable.months);
    this.gregorianYearRange = getGregorianYearRange(this.monthTable.months);
  }
  
  /**
   * Get the library version
   */
  getVersion(): string {
    return LIBRARY_VERSION;
  }
  
  /**
   * Get the data version
   */
  getDataVersion(): string {
    return this.monthTable.version;
  }
  
  /**
   * Get the data checksum
   */
  getDataChecksum(): string {
    return this.monthTable.checksum || '';
  }
  
  /**
   * Get the supported Hijri year range
   */
  getHijriRange(): { start: number; end: number } {
    return this.monthTable.hijri_range;
  }
  
  /**
   * Get the supported Gregorian year range
   */
  getGregorianRange(): { min: number; max: number } {
    return this.gregorianYearRange;
  }
  
  /**
   * Convert a Gregorian date to Hijri (Umm al-Qura)
   * 
   * @param year - Gregorian year
   * @param month - Gregorian month (1-12)
   * @param day - Gregorian day
   * @param options - Conversion options
   * @returns Conversion result
   */
  gregorianToHijri(
    year: number,
    month: number,
    day: number,
    options?: ConversionOptions
  ): ConversionResult {
    // Validate input
    const error = validateGregorian(
      year, month, day,
      this.gregorianYearRange.min,
      this.gregorianYearRange.max
    );
    if (error) {
      throw error;
    }
    
    // Convert to JDN
    const jdn = gregorianToJdn(year, month, day);
    
    // Convert JDN to Hijri
    const hijri = jdnToHijri(jdn, this.sortedMonths);
    
    // Get day of week
    const dow = dayOfWeekFromJdn(jdn);
    
    return {
      input: { year, month, day, calendar: 'gregorian' },
      output: { 
        year: hijri.year, 
        month: hijri.month, 
        day: hijri.day, 
        calendar: 'hijri-ummalqura' 
      },
      jdn,
      day_of_week: dow,
      locale: options?.locale || this.defaultLocale,
      library_version: LIBRARY_VERSION,
      data_version: this.monthTable.version
    };
  }
  
  /**
   * Convert a Hijri (Umm al-Qura) date to Gregorian
   * 
   * @param year - Hijri year (1300-1700)
   * @param month - Hijri month (1-12)
   * @param day - Hijri day
   * @param options - Conversion options
   * @returns Conversion result
   */
  hijriToGregorian(
    year: number,
    month: number,
    day: number,
    options?: ConversionOptions
  ): ConversionResult {
    // Validate input
    const error = validateHijri(year, month, day, this.monthIndex);
    if (error) {
      throw error;
    }
    
    // Convert to JDN
    const jdn = hijriToJdn(year, month, day, this.monthIndex);
    
    // Convert JDN to Gregorian
    const gregorian = jdnToGregorian(jdn);
    
    // Get day of week
    const dow = dayOfWeekFromJdn(jdn);
    
    return {
      input: { year, month, day, calendar: 'hijri-ummalqura' },
      output: { 
        year: gregorian.year, 
        month: gregorian.month, 
        day: gregorian.day, 
        calendar: 'gregorian' 
      },
      jdn,
      day_of_week: dow,
      locale: options?.locale || this.defaultLocale,
      library_version: LIBRARY_VERSION,
      data_version: this.monthTable.version
    };
  }
  
  /**
   * Validate a Gregorian date
   * 
   * @param year - Gregorian year
   * @param month - Gregorian month
   * @param day - Gregorian day
   * @returns Validation result
   */
  validateGregorianDate(year: number, month: number, day: number): ValidationResult {
    const error = validateGregorian(
      year, month, day,
      this.gregorianYearRange.min,
      this.gregorianYearRange.max
    );
    
    return {
      valid: error === null,
      error: error || undefined
    };
  }
  
  /**
   * Validate a Hijri date
   * 
   * @param year - Hijri year
   * @param month - Hijri month
   * @param day - Hijri day
   * @returns Validation result
   */
  validateHijriDate(year: number, month: number, day: number): ValidationResult {
    const error = validateHijri(year, month, day, this.monthIndex);
    
    return {
      valid: error === null,
      error: error || undefined
    };
  }
  
  /**
   * Get the day of week for a JDN
   * 
   * @param jdn - Julian Day Number
   * @returns Day of week information
   */
  getDayOfWeek(jdn: number): DayOfWeek {
    return dayOfWeekFromJdn(jdn);
  }
  
  /**
   * Get the day of week for a Gregorian date
   * 
   * @param year - Gregorian year
   * @param month - Gregorian month
   * @param day - Gregorian day
   * @returns Day of week information
   */
  getDayOfWeekGregorian(year: number, month: number, day: number): DayOfWeek {
    const jdn = gregorianToJdn(year, month, day);
    return dayOfWeekFromJdn(jdn);
  }
  
  /**
   * Get the day of week for a Hijri date
   * 
   * @param year - Hijri year
   * @param month - Hijri month
   * @param day - Hijri day
   * @returns Day of week information
   */
  getDayOfWeekHijri(year: number, month: number, day: number): DayOfWeek {
    const jdn = hijriToJdn(year, month, day, this.monthIndex);
    return dayOfWeekFromJdn(jdn);
  }
  
  /**
   * Get the number of days in a Gregorian month
   * 
   * @param year - Gregorian year
   * @param month - Gregorian month (1-12)
   * @returns Number of days
   */
  getGregorianMonthLength(year: number, month: number): number {
    return gregorianMonthLength(year, month);
  }
  
  /**
   * Get the number of days in a Hijri month
   * 
   * @param year - Hijri year
   * @param month - Hijri month (1-12)
   * @returns Number of days
   */
  getHijriMonthLength(year: number, month: number): number {
    const key = `${year}-${month}`;
    const entry = this.monthIndex.get(key);
    
    if (!entry) {
      throw createError(
        ErrorCode.OUT_OF_RANGE,
        `Hijri date ${year}-${String(month).padStart(2, '0')} is outside the supported range`
      );
    }
    
    return entry.month_length;
  }
  
  /**
   * Check if a Gregorian year is a leap year
   * 
   * @param year - Gregorian year
   * @returns true if leap year
   */
  isGregorianLeapYear(year: number): boolean {
    return isGregorianLeapYear(year);
  }
  
  /**
   * Get all days in a Gregorian month with both calendar representations
   * 
   * @param year - Gregorian year
   * @param month - Gregorian month (1-12)
   * @param locale - Locale for month/day names
   * @returns Month calendar information
   */
  getGregorianMonth(year: number, month: number, locale?: string): MonthCalendar {
    const loc = locale || this.defaultLocale;
    const daysInMonth = gregorianMonthLength(year, month);
    const days: DayInfo[] = [];
    
    for (let day = 1; day <= daysInMonth; day++) {
      const jdn = gregorianToJdn(year, month, day);
      const hijri = jdnToHijri(jdn, this.sortedMonths);
      const dow = dayOfWeekFromJdn(jdn);
      
      days.push({
        gregorian: { year, month, day, calendar: 'gregorian' },
        hijri: { 
          year: hijri.year, 
          month: hijri.month, 
          day: hijri.day, 
          calendar: 'hijri-ummalqura' 
        },
        jdn,
        day_of_week: dow
      });
    }
    
    return {
      calendar: 'gregorian',
      year,
      month,
      days,
      month_name_en: getGregorianMonthName(month, loc),
      month_name_ar: getGregorianMonthName(month, 'ar')
    };
  }
  
  /**
   * Get all days in a Hijri month with both calendar representations
   * 
   * @param year - Hijri year
   * @param month - Hijri month (1-12)
   * @param locale - Locale for month/day names
   * @returns Month calendar information
   */
  getHijriMonth(year: number, month: number, locale?: string): MonthCalendar {
    const loc = locale || this.defaultLocale;
    const key = `${year}-${month}`;
    const entry = this.monthIndex.get(key);
    
    if (!entry) {
      throw createError(
        ErrorCode.OUT_OF_RANGE,
        `Hijri date ${year}-${String(month).padStart(2, '0')} is outside the supported range`
      );
    }
    
    const days: DayInfo[] = [];
    
    for (let day = 1; day <= entry.month_length; day++) {
      const jdn = hijriToJdn(year, month, day, this.monthIndex);
      const gregorian = jdnToGregorian(jdn);
      const dow = dayOfWeekFromJdn(jdn);
      
      days.push({
        gregorian: { 
          year: gregorian.year, 
          month: gregorian.month, 
          day: gregorian.day, 
          calendar: 'gregorian' 
        },
        hijri: { year, month, day, calendar: 'hijri-ummalqura' },
        jdn,
        day_of_week: dow
      });
    }
    
    return {
      calendar: 'hijri-ummalqura',
      year,
      month,
      days,
      month_name_en: getHijriMonthName(month, loc),
      month_name_ar: getHijriMonthName(month, 'ar')
    };
  }
  
  /**
   * Batch convert Gregorian dates to Hijri
   * 
   * @param dates - Array of Gregorian dates
   * @param options - Conversion options
   * @returns Array of conversion results
   */
  batchGregorianToHijri(
    dates: Array<{ year: number; month: number; day: number }>,
    options?: ConversionOptions
  ): ConversionResult[] {
    return dates.map(d => this.gregorianToHijri(d.year, d.month, d.day, options));
  }
  
  /**
   * Batch convert Hijri dates to Gregorian
   * 
   * @param dates - Array of Hijri dates
   * @param options - Conversion options
   * @returns Array of conversion results
   */
  batchHijriToGregorian(
    dates: Array<{ year: number; month: number; day: number }>,
    options?: ConversionOptions
  ): ConversionResult[] {
    return dates.map(d => this.hijriToGregorian(d.year, d.month, d.day, options));
  }
}

// Export types
export * from './types.js';

// Export locale utilities
export { loadLocale, getLocaleData } from './locale.js';

// Export core functions for advanced usage
export {
  gregorianToJdn,
  jdnToGregorian,
  hijriToJdn,
  jdnToHijri,
  dayOfWeekFromJdn,
  gregorianMonthLength,
  isGregorianLeapYear,
  validateGregorian,
  validateHijri
} from './core.js';
