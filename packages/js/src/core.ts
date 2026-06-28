/**
 * Core conversion algorithms for Umm al-Qura calendar
 * 
 * All functions are pure, deterministic, and stateless.
 * No global mutable state is used.
 */

import { MonthInfo, MonthTableData, DayOfWeek, ErrorCode, CalendarError } from './types.js';

// Umm al-Qura leap year positions (mod 30)
const UMM_AL_QURA_LEAP_YEARS = new Set([2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29]);

// Day of week names
const DAYS_EN = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'];
const DAYS_AR = ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'];

// Gregorian month lengths (non-leap year)
const GREGORIAN_MONTH_DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31];

/**
 * Check if a Gregorian year is a leap year
 */
export function isGregorianLeapYear(year: number): boolean {
  return (year % 4 === 0) && (year % 100 !== 0 || year % 400 === 0);
}

/**
 * Get the number of days in a Gregorian month
 */
export function gregorianMonthLength(year: number, month: number): number {
  if (month === 2 && isGregorianLeapYear(year)) {
    return 29;
  }
  return GREGORIAN_MONTH_DAYS[month];
}

/**
 * Check if a Hijri year is a leap year in Umm al-Qura calendar
 */
export function isUmAlQuraLeapYear(year: number): boolean {
  return UMM_AL_QURA_LEAP_YEARS.has(year % 30);
}

/**
 * Get the number of days in a Hijri month using the algorithm
 * (used as fallback if table lookup fails)
 */
export function hijriMonthLengthFromAlgorithm(year: number, month: number): number {
  if (month % 2 === 1) {
    return 30; // Odd months
  }
  if (month === 12) {
    return isUmAlQuraLeapYear(year) ? 30 : 29; // Dhul Hijjah
  }
  return 29; // Even months (2, 4, 6, 8, 10)
}

/**
 * Convert Gregorian date to Julian Day Number (JDN)
 * 
 * Algorithm: Fliegel & Van Flandern (1968)
 * Uses proleptic Gregorian calendar rules
 */
export function gregorianToJdn(year: number, month: number, day: number): number {
  const a = Math.floor((14 - month) / 12);
  const y = year + 4800 - a;
  const m = month + 12 * a - 3;

  return day + Math.floor((153 * m + 2) / 5) + 365 * y + 
         Math.floor(y / 4) - Math.floor(y / 100) + Math.floor(y / 400) - 32045;
}

/**
 * Convert Julian Day Number (JDN) to Gregorian date
 * 
 * Algorithm: Fliegel & Van Flandern (1968), inverse
 */
export function jdnToGregorian(jdn: number): { year: number; month: number; day: number } {
  const a = jdn + 32044;
  const b = Math.floor((4 * a + 3) / 146097);
  const c = a - Math.floor((146097 * b) / 4);
  const d = Math.floor((4 * c + 3) / 1461);
  const e = c - Math.floor((1461 * d) / 4);
  const m = Math.floor((5 * e + 2) / 153);

  const day = e - Math.floor((153 * m + 2) / 5) + 1;
  const month = m + 3 - 12 * Math.floor(m / 10);
  const year = 100 * b + d - 4800 + Math.floor(m / 10);

  return { year, month, day };
}

/**
 * Calculate day of week from JDN
 * 
 * Returns index (0=Sunday, 1=Monday, ..., 6=Saturday)
 */
export function dayOfWeekFromJdn(jdn: number): DayOfWeek {
  // JDN 0 is Monday, so (jdn + 1) % 7 gives Sunday=0
  const index = (jdn + 1) % 7;
  
  return {
    index,
    name_en: DAYS_EN[index],
    name_ar: DAYS_AR[index]
  };
}

/**
 * Build an index for fast month lookup from the month table
 */
export function buildMonthIndex(months: MonthInfo[]): Map<string, MonthInfo> {
  const index = new Map<string, MonthInfo>();
  
  for (const month of months) {
    const key = `${month.hijri_year}-${month.hijri_month}`;
    index.set(key, month);
  }
  
  return index;
}

/**
 * Build a sorted array of month entries for binary search by JDN
 */
export function buildJdnIndex(months: MonthInfo[]): MonthInfo[] {
  // Months should already be sorted by first_day_jdn
  return [...months].sort((a, b) => a.first_day_jdn - b.first_day_jdn);
}

/**
 * Convert Hijri (Umm al-Qura) date to Julian Day Number (JDN)
 * 
 * Uses the month-length table for lookup
 */
export function hijriToJdn(
  year: number, 
  month: number, 
  day: number, 
  monthIndex: Map<string, MonthInfo>
): number {
  const key = `${year}-${month}`;
  const entry = monthIndex.get(key);
  
  if (!entry) {
    throw createError(
      ErrorCode.OUT_OF_RANGE,
      `Hijri date ${year}-${String(month).padStart(2, '0')} is outside the supported range`
    );
  }
  
  return entry.first_day_jdn + day - 1;
}

/**
 * Convert Julian Day Number (JDN) to Hijri (Umm al-Qura) date
 * 
 * Uses binary search on the sorted month table
 */
export function jdnToHijri(
  jdn: number, 
  sortedMonths: MonthInfo[]
): { year: number; month: number; day: number } {
  if (sortedMonths.length === 0) {
    throw createError(
      ErrorCode.OUT_OF_RANGE,
      'Month table is empty'
    );
  }

  const lastMonth = sortedMonths[sortedMonths.length - 1];
  const lastValidJdn = lastMonth.first_day_jdn + lastMonth.month_length - 1;

  if (jdn < sortedMonths[0].first_day_jdn) {
    throw createError(
      ErrorCode.OUT_OF_RANGE,
      `JDN ${jdn} is before the supported range (first JDN: ${sortedMonths[0].first_day_jdn})`
    );
  }

  if (jdn > lastValidJdn) {
    throw createError(
      ErrorCode.OUT_OF_RANGE,
      `JDN ${jdn} is after the supported range (last JDN: ${lastValidJdn})`
    );
  }

  // Binary search for the month containing this JDN
  let left = 0;
  let right = sortedMonths.length - 1;
  
  while (left < right) {
    const mid = Math.floor((left + right) / 2);
    if (sortedMonths[mid].first_day_jdn <= jdn) {
      left = mid + 1;
    } else {
      right = mid;
    }
  }
  
  // Clamp to valid range
  if (left >= sortedMonths.length) {
    left = sortedMonths.length - 1;
  } else if (left > 0 && sortedMonths[left].first_day_jdn > jdn) {
    left--;
  }
  
  const entry = sortedMonths[left];
  const day = jdn - entry.first_day_jdn + 1;
  
  return {
    year: entry.hijri_year,
    month: entry.hijri_month,
    day
  };
}

/**
 * Validate a Gregorian date
 */
export function validateGregorian(
  year: number, 
  month: number, 
  day: number,
  minYear: number,
  maxYear: number
): CalendarError | null {
  // Check for non-integer values
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) {
    return createError(
      ErrorCode.MALFORMED_INPUT,
      'Year, month, and day must be integers',
      'year',
      year
    );
  }
  
  // Check month range
  if (month < 1 || month > 12) {
    return createError(
      ErrorCode.INVALID_MONTH,
      `Month must be between 1 and 12, got ${month}`,
      'month',
      month
    );
  }
  
  // Check year range
  if (year < minYear || year > maxYear) {
    return createError(
      ErrorCode.INVALID_YEAR,
      `Year must be between ${minYear} and ${maxYear}, got ${year}`,
      'year',
      year
    );
  }
  
  // Check day range
  const maxDay = gregorianMonthLength(year, month);
  if (day < 1 || day > maxDay) {
    return createError(
      ErrorCode.INVALID_DAY,
      `Day must be between 1 and ${maxDay} for ${year}-${String(month).padStart(2, '0')}, got ${day}`,
      'day',
      day
    );
  }
  
  return null;
}

/**
 * Validate a Hijri date
 */
export function validateHijri(
  year: number, 
  month: number, 
  day: number,
  monthIndex: Map<string, MonthInfo>
): CalendarError | null {
  // Check for non-integer values
  if (!Number.isInteger(year) || !Number.isInteger(month) || !Number.isInteger(day)) {
    return createError(
      ErrorCode.MALFORMED_INPUT,
      'Year, month, and day must be integers',
      'year',
      year
    );
  }
  
  // Check month range
  if (month < 1 || month > 12) {
    return createError(
      ErrorCode.INVALID_MONTH,
      `Month must be between 1 and 12, got ${month}`,
      'month',
      month
    );
  }
  
  const hijriYears = [...new Set([...monthIndex.values()].map((m) => m.hijri_year))].sort((a, b) => a - b);
  const minYear = hijriYears[0] ?? 1318;
  const maxYear = hijriYears[hijriYears.length - 1] ?? 1500;

  // Check year range
  if (year < minYear || year > maxYear) {
    return createError(
      ErrorCode.INVALID_YEAR,
      `Year must be between ${minYear} and ${maxYear}, got ${year}`,
      'year',
      year
    );
  }
  
  // Look up month length
  const key = `${year}-${month}`;
  const entry = monthIndex.get(key);
  
  if (!entry) {
    return createError(
      ErrorCode.OUT_OF_RANGE,
      `Hijri date ${year}-${String(month).padStart(2, '0')} is outside the supported range`
    );
  }
  
  // Check day range
  if (day < 1 || day > entry.month_length) {
    return createError(
      ErrorCode.INVALID_DAY,
      `Day ${day} does not exist in Hijri month ${year}-${String(month).padStart(2, '0')}, which has ${entry.month_length} days`,
      'day',
      day
    );
  }
  
  return null;
}

/**
 * Create a structured error object
 */
export function createError(
  code: ErrorCode, 
  message: string, 
  field?: string, 
  value?: number | string
): CalendarError {
  const error: CalendarError = {
    error_code: code,
    message
  };
  
  if (field !== undefined) {
    error.field = field;
  }
  
  if (value !== undefined) {
    error.value = value;
  }
  
  return error;
}

/**
 * Get the Gregorian year range that corresponds to the Hijri year range
 */
export function getGregorianYearRange(
  months: MonthInfo[]
): { min: number; max: number } {
  if (months.length === 0) {
    return { min: 0, max: 0 };
  }
  
  const firstMonth = months[0];
  const lastMonth = months[months.length - 1];
  
  const firstGregorian = jdnToGregorian(firstMonth.first_day_jdn);
  const lastJdn = lastMonth.first_day_jdn + lastMonth.month_length - 1;
  const lastGregorian = jdnToGregorian(lastJdn);
  
  return {
    min: firstGregorian.year,
    max: lastGregorian.year
  };
}
