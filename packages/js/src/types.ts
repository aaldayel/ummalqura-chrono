/**
 * Umm al-Qura Calendar Conversion Library - Type Definitions
 */

/** Supported calendar systems */
export type CalendarType = 'gregorian' | 'hijri-ummalqura';

/** Gregorian date representation */
export interface GregorianDate {
  year: number;
  month: number;
  day: number;
  calendar: 'gregorian';
}

/** Hijri (Umm al-Qura) date representation */
export interface HijriDate {
  year: number;
  month: number;
  day: number;
  calendar: 'hijri-ummalqura';
}

/** Union type for any supported date */
export type CalendarDate = GregorianDate | HijriDate;

/** Day of week information */
export interface DayOfWeek {
  index: number;
  name_en: string;
  name_ar: string;
}

/** Conversion result */
export interface ConversionResult {
  input: CalendarDate;
  output: CalendarDate;
  jdn: number;
  day_of_week: DayOfWeek;
  locale: string;
  library_version: string;
  data_version: string;
}

/** Error codes */
export enum ErrorCode {
  INVALID_DAY = 'INVALID_DAY',
  INVALID_MONTH = 'INVALID_MONTH',
  INVALID_YEAR = 'INVALID_YEAR',
  OUT_OF_RANGE = 'OUT_OF_RANGE',
  UNSUPPORTED_CALENDAR = 'UNSUPPORTED_CALENDAR',
  INVALID_TIMEZONE = 'INVALID_TIMEZONE',
  MALFORMED_INPUT = 'MALFORMED_INPUT'
}

/** Structured error response */
export interface CalendarError {
  error_code: ErrorCode;
  message: string;
  field?: string;
  value?: number | string;
}

/** Month information */
export interface MonthInfo {
  hijri_year: number;
  hijri_month: number;
  month_length: number;
  first_day_jdn: number;
}

/** Month-length table data structure */
export interface MonthTableData {
  version: string;
  description: string;
  source: string;
  hijri_range: { start: number; end: number };
  total_months: number;
  generated_at: string;
  checksum?: string;
  months: MonthInfo[];
}

/** Day information for calendar view */
export interface DayInfo {
  gregorian: GregorianDate;
  hijri: HijriDate;
  jdn: number;
  day_of_week: DayOfWeek;
  is_today?: boolean;
}

/** Month calendar response */
export interface MonthCalendar {
  calendar: CalendarType;
  year: number;
  month: number;
  days: DayInfo[];
  month_name_en: string;
  month_name_ar: string;
}

/** Validation result */
export interface ValidationResult {
  valid: boolean;
  error?: CalendarError;
}

/** Locale configuration */
export interface LocaleData {
  code: string;
  name: string;
  gregorian_months: string[];
  gregorian_months_short: string[];
  hijri_months: string[];
  hijri_months_short: string[];
  days: string[];
  days_short: string[];
  days_min: string[];
  meridiem: { am: string; pm: string };
  rtl: boolean;
}

/** Options for conversion */
export interface ConversionOptions {
  locale?: string;
  include_jdn?: boolean;
  include_day_of_week?: boolean;
}

/** Library configuration */
export interface LibraryConfig {
  dataPath?: string;
  defaultLocale?: string;
}
