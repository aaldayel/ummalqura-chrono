/**
 * Umm al-Qura Calendar Conversion Library - Tests
 * 
 * Tests based on golden values and known conversion pairs.
 */

import { describe, it, expect, beforeAll } from 'vitest';
import { UmmAlQuraCalendar } from '../index';
import * as fs from 'fs';
import * as path from 'path';
import * as csv from 'csv-parse/sync';

// Golden value test vector
interface GoldenValue {
  gregorian_year: number;
  gregorian_month: number;
  gregorian_day: number;
  hijri_year: number;
  hijri_month: number;
  hijri_day: number;
  jdn: number;
  day_of_week_index: number;
  day_of_week_en: string;
  day_of_week_ar: string;
}

describe('UmmAlQuraCalendar', () => {
  let calendar: UmmAlQuraCalendar;
  let goldenValues: GoldenValue[];
  
  beforeAll(() => {
    // Initialize calendar
    calendar = new UmmAlQuraCalendar();
    
    // Load golden values
    const csvPath = path.join(__dirname, '..', '..', '..', 'tests', 'golden', 'golden-values.csv');
    const csvContent = fs.readFileSync(csvPath, 'utf-8');
    goldenValues = csv.parse(csvContent, {
      columns: true,
      skip_empty_lines: true,
      cast: (value, context) => {
        if (context.column && ['gregorian_year', 'gregorian_month', 'gregorian_day', 
            'hijri_year', 'hijri_month', 'hijri_day', 'jdn', 'day_of_week_index'].includes(context.column)) {
          return parseInt(value, 10);
        }
        return value;
      }
    }) as GoldenValue[];
  });
  
  describe('Version and Data', () => {
    it('should return library version', () => {
      expect(calendar.getVersion()).toBe('1.0.0');
    });
    
    it('should return data version', () => {
      expect(calendar.getDataVersion()).toBeTruthy();
    });
    
    it('should return data checksum', () => {
      expect(calendar.getDataChecksum()).toBeTruthy();
    });
    
    it('should return Hijri range', () => {
      const range = calendar.getHijriRange();
      expect(range.start).toBe(1318);
      expect(range.end).toBe(1500);
    });
    
    it('should return Gregorian range', () => {
      const range = calendar.getGregorianRange();
      expect(range.min).toBeLessThan(range.max);
      expect(range.min).toBeGreaterThan(1800);
      expect(range.max).toBeLessThan(2300);
    });
  });
  
  describe('Gregorian to Hijri Conversion', () => {
    it('should convert March 15, 2024 to 1445-09-05', () => {
      const result = calendar.gregorianToHijri(2024, 3, 15);
      expect(result.output.year).toBe(1445);
      expect(result.output.month).toBe(9);
      expect(result.output.day).toBe(5);
    });
    
    it('should include JDN in result', () => {
      const result = calendar.gregorianToHijri(2024, 3, 15);
      expect(result.jdn).toBe(2460385);
    });
    
    it('should include day of week', () => {
      const result = calendar.gregorianToHijri(2024, 3, 15);
      expect(result.day_of_week.index).toBe(5);
      expect(result.day_of_week.name_en).toBe('Friday');
      expect(result.day_of_week.name_ar).toBe('الجمعة');
    });
    
    it('should throw error for invalid month', () => {
      expect(() => calendar.gregorianToHijri(2024, 13, 1)).toThrow();
    });
    
    it('should throw error for invalid day', () => {
      expect(() => calendar.gregorianToHijri(2024, 2, 30)).toThrow();
    });
    
    it('should throw error for year outside range', () => {
      expect(() => calendar.gregorianToHijri(1899, 1, 1)).toThrow();
    });
  });
  
  describe('Hijri to Gregorian Conversion', () => {
    it('should convert 1445-09-05 to March 15, 2024', () => {
      const result = calendar.hijriToGregorian(1445, 9, 5);
      expect(result.output.year).toBe(2024);
      expect(result.output.month).toBe(3);
      expect(result.output.day).toBe(15);
    });
    
    it('should throw error for invalid month', () => {
      expect(() => calendar.hijriToGregorian(1445, 13, 1)).toThrow();
    });
    
    it('should throw error for invalid day', () => {
      expect(() => calendar.hijriToGregorian(1445, 9, 31)).toThrow();
    });
    
    it('should throw error for year outside range', () => {
      expect(() => calendar.hijriToGregorian(1317, 1, 1)).toThrow();
    });
  });
  
  describe('Round-trip Conversion', () => {
    it('should round-trip Gregorian -> Hijri -> Gregorian', () => {
      const dates = [
        { year: 2024, month: 3, day: 15 },
        { year: 2000, month: 1, day: 1 },
        { year: 1900, month: 6, day: 15 },
        { year: 2024, month: 12, day: 31 }
      ];
      
      for (const date of dates) {
        const hijri = calendar.gregorianToHijri(date.year, date.month, date.day);
        const gregorian = calendar.hijriToGregorian(
          hijri.output.year, 
          hijri.output.month, 
          hijri.output.day
        );
        
        expect(gregorian.output.year).toBe(date.year);
        expect(gregorian.output.month).toBe(date.month);
        expect(gregorian.output.day).toBe(date.day);
      }
    });
    
    it('should round-trip Hijri -> Gregorian -> Hijri', () => {
      const dates = [
        { year: 1445, month: 9, day: 5 },
        { year: 1400, month: 1, day: 1 },
        { year: 1350, month: 6, day: 15 },
        { year: 1500, month: 12, day: 29 }
      ];
      
      for (const date of dates) {
        const gregorian = calendar.hijriToGregorian(date.year, date.month, date.day);
        const hijri = calendar.gregorianToHijri(
          gregorian.output.year, 
          gregorian.output.month, 
          gregorian.output.day
        );
        
        expect(hijri.output.year).toBe(date.year);
        expect(hijri.output.month).toBe(date.month);
        expect(hijri.output.day).toBe(date.day);
      }
    });
  });
  
  describe('Day of Week', () => {
    it('should calculate day of week from JDN', () => {
      // JDN 2460385 = March 15, 2024 = Friday
      const dow = calendar.getDayOfWeek(2460385);
      expect(dow.index).toBe(5);
      expect(dow.name_en).toBe('Friday');
    });
    
    it('should calculate day of week for Gregorian date', () => {
      // March 15, 2024 is Friday
      const dow = calendar.getDayOfWeekGregorian(2024, 3, 15);
      expect(dow.index).toBe(5);
      expect(dow.name_en).toBe('Friday');
    });
    
    it('should calculate day of week for Hijri date', () => {
      // 1445-09-05 = March 15, 2024 = Friday
      const dow = calendar.getDayOfWeekHijri(1445, 9, 5);
      expect(dow.index).toBe(5);
      expect(dow.name_en).toBe('Friday');
    });
  });
  
  describe('Month Lengths', () => {
    it('should return correct Gregorian month lengths', () => {
      expect(calendar.getGregorianMonthLength(2024, 1)).toBe(31); // January
      expect(calendar.getGregorianMonthLength(2024, 2)).toBe(29); // February (leap year)
      expect(calendar.getGregorianMonthLength(2023, 2)).toBe(28); // February (non-leap)
      expect(calendar.getGregorianMonthLength(2024, 4)).toBe(30); // April
    });
    
    it('should return correct Hijri month lengths', () => {
      // Official Umm al-Qura table for 1445 AH (not tabular odd/even)
      expect(calendar.getHijriMonthLength(1445, 1)).toBe(29); // Muharram
      expect(calendar.getHijriMonthLength(1445, 2)).toBe(30); // Safar
      expect(calendar.getHijriMonthLength(1445, 12)).toBe(30); // Dhul Hijjah
    });
    
    it('should check leap years correctly', () => {
      expect(calendar.isGregorianLeapYear(2024)).toBe(true);
      expect(calendar.isGregorianLeapYear(2023)).toBe(false);
      expect(calendar.isGregorianLeapYear(1900)).toBe(false);
      expect(calendar.isGregorianLeapYear(2000)).toBe(true);
    });
  });
  
  describe('Validation', () => {
    it('should validate correct Gregorian dates', () => {
      const result = calendar.validateGregorianDate(2024, 3, 15);
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });
    
    it('should reject invalid Gregorian dates', () => {
      const result1 = calendar.validateGregorianDate(2024, 13, 1);
      expect(result1.valid).toBe(false);
      expect(result1.error?.error_code).toBe('INVALID_MONTH');
      
      const result2 = calendar.validateGregorianDate(2024, 2, 30);
      expect(result2.valid).toBe(false);
      expect(result2.error?.error_code).toBe('INVALID_DAY');
    });
    
    it('should validate correct Hijri dates', () => {
      const result = calendar.validateHijriDate(1445, 9, 5);
      expect(result.valid).toBe(true);
      expect(result.error).toBeUndefined();
    });
    
    it('should reject invalid Hijri dates', () => {
      const result1 = calendar.validateHijriDate(1445, 13, 1);
      expect(result1.valid).toBe(false);
      expect(result1.error?.error_code).toBe('INVALID_MONTH');
      
      const result2 = calendar.validateHijriDate(1445, 9, 31);
      expect(result2.valid).toBe(false);
      expect(result2.error?.error_code).toBe('INVALID_DAY');
    });
  });
  
  describe('Month Calendar', () => {
    it('should return Gregorian month calendar', () => {
      const calendar2024 = calendar.getGregorianMonth(2024, 3);
      expect(calendar2024.calendar).toBe('gregorian');
      expect(calendar2024.year).toBe(2024);
      expect(calendar2024.month).toBe(3);
      expect(calendar2024.days.length).toBe(31); // March has 31 days
      expect(calendar2024.month_name_en).toBe('March');
    });
    
    it('should return Hijri month calendar', () => {
      const ramadan = calendar.getHijriMonth(1445, 9);
      expect(ramadan.calendar).toBe('hijri-ummalqura');
      expect(ramadan.year).toBe(1445);
      expect(ramadan.month).toBe(9);
      expect(ramadan.days.length).toBe(30); // Ramadan 1445 has 30 days
      expect(ramadan.month_name_en).toBe('Ramadan');
    });
  });
  
  describe('Batch Conversion', () => {
    it('should batch convert Gregorian to Hijri', () => {
      const dates = [
        { year: 2024, month: 3, day: 15 },
        { year: 2024, month: 3, day: 16 }
      ];
      
      const results = calendar.batchGregorianToHijri(dates);
      expect(results.length).toBe(2);
      expect(results[0].output.year).toBe(1445);
      expect(results[0].output.month).toBe(9);
      expect(results[0].output.day).toBe(5);
      expect(results[1].output.day).toBe(6);
    });
    
    it('should batch convert Hijri to Gregorian', () => {
      const dates = [
        { year: 1445, month: 9, day: 5 },
        { year: 1445, month: 9, day: 6 }
      ];
      
      const results = calendar.batchHijriToGregorian(dates);
      expect(results.length).toBe(2);
      expect(results[0].output.year).toBe(2024);
      expect(results[0].output.month).toBe(3);
      expect(results[0].output.day).toBe(15);
      expect(results[1].output.day).toBe(16);
    });
  });
  
  describe('Golden Value Tests', () => {
    it('should match all golden values for Gregorian to Hijri', () => {
      // Test a sample of golden values (full test would be too slow for unit tests)
      const sampleSize = 100;
      const step = Math.max(1, Math.floor(goldenValues.length / sampleSize));
      
      for (let i = 0; i < goldenValues.length; i += step) {
        const gv = goldenValues[i];
        
        const result = calendar.gregorianToHijri(
          gv.gregorian_year, 
          gv.gregorian_month, 
          gv.gregorian_day
        );
        
        expect(result.output.year).toBe(gv.hijri_year);
        expect(result.output.month).toBe(gv.hijri_month);
        expect(result.output.day).toBe(gv.hijri_day);
        expect(result.jdn).toBe(gv.jdn);
        expect(result.day_of_week.index).toBe(gv.day_of_week_index);
        expect(result.day_of_week.name_en).toBe(gv.day_of_week_en);
      }
    });
    
    it('should match all golden values for Hijri to Gregorian', () => {
      const sampleSize = 100;
      const step = Math.max(1, Math.floor(goldenValues.length / sampleSize));
      
      for (let i = 0; i < goldenValues.length; i += step) {
        const gv = goldenValues[i];
        
        const result = calendar.hijriToGregorian(
          gv.hijri_year, 
          gv.hijri_month, 
          gv.hijri_day
        );
        
        expect(result.output.year).toBe(gv.gregorian_year);
        expect(result.output.month).toBe(gv.gregorian_month);
        expect(result.output.day).toBe(gv.gregorian_day);
        expect(result.jdn).toBe(gv.jdn);
      }
    });
  });
  
  describe('Error Handling', () => {
    it('should throw structured error for invalid Gregorian month', () => {
      try {
        calendar.gregorianToHijri(2024, 13, 1);
        expect.fail('Should have thrown');
      } catch (error: any) {
        expect(error.error_code).toBe('INVALID_MONTH');
        expect(error.field).toBe('month');
        expect(error.value).toBe(13);
      }
    });
    
    it('should throw structured error for invalid Hijri day', () => {
      try {
        calendar.hijriToGregorian(1445, 9, 31);
        expect.fail('Should have thrown');
      } catch (error: any) {
        expect(error.error_code).toBe('INVALID_DAY');
        expect(error.field).toBe('day');
        expect(error.value).toBe(31);
      }
    });
    
    it('should throw structured error for year outside range', () => {
      try {
        calendar.gregorianToHijri(1899, 1, 1);
        expect.fail('Should have thrown');
      } catch (error: any) {
        expect(error.error_code).toBe('INVALID_YEAR');
        expect(error.field).toBe('year');
      }
    });
  });
});
