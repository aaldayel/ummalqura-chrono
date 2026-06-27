#!/usr/bin/env node

import { Command } from 'commander';
import { UmmAlQuraCalendar, ErrorCode } from 'ummalqura-chrono';

const calendar = new UmmAlQuraCalendar();
const program = new Command();

program
  .name('uaq')
  .description('Umm al-Qura Calendar Conversion CLI')
  .version(calendar.getVersion());

function formatDate(result: any, format: string): string {
  if (format === 'json') {
    return JSON.stringify(result, null, 2);
  }
  
  const input = result.input;
  const output = result.output;
  const inputStr = `${input.year}-${String(input.month).padStart(2, '0')}-${String(input.day).padStart(2, '0')}`;
  const outputStr = `${output.year}-${String(output.month).padStart(2, '0')}-${String(output.day).padStart(2, '0')}`;
  
  return `${inputStr} (${input.calendar}) = ${outputStr} (${output.calendar})\nJDN: ${result.jdn}\nDay: ${result.day_of_week.name_en}`;
}

function handleError(error: any): never {
  if (error.error_code) {
    console.error(`Error [${error.error_code}]: ${error.message}`);
    process.exit(1);
  }
  console.error('Unexpected error:', error);
  process.exit(2);
}

program
  .command('convert')
  .description('Convert a date between calendars')
  .requiredOption('--from <calendar>', 'Source calendar (gregorian or hijri)')
  .requiredOption('--to <calendar>', 'Target calendar (gregorian or hijri)')
  .requiredOption('--date <date>', 'Date in YYYY-MM-DD format')
  .option('--format <format>', 'Output format (json or text)', 'text')
  .action((options) => {
    try {
      const [yearStr, monthStr, dayStr] = options.date.split('-');
      const year = parseInt(yearStr, 10);
      const month = parseInt(monthStr, 10);
      const day = parseInt(dayStr, 10);
      
      if (isNaN(year) || isNaN(month) || isNaN(day)) {
        console.error('Error: Invalid date format. Use YYYY-MM-DD');
        process.exit(1);
      }
      
      const fromCal = options.from === 'hijri' ? 'hijri-ummalqura' : options.from;
      const toCal = options.to === 'hijri' ? 'hijri-ummalqura' : options.to;
      
      let result;
      if (fromCal === 'gregorian' && toCal === 'hijri-ummalqura') {
        result = calendar.gregorianToHijri(year, month, day);
      } else if (fromCal === 'hijri-ummalqura' && toCal === 'gregorian') {
        result = calendar.hijriToGregorian(year, month, day);
      } else {
        console.error('Error: Unsupported conversion');
        process.exit(1);
      }
      
      console.log(formatDate(result, options.format));
    } catch (error) {
      handleError(error);
    }
  });

program
  .command('today')
  .description('Get today\'s date in both calendars')
  .option('--timezone <tz>', 'Timezone (e.g., Asia/Riyadh)', 'Asia/Riyadh')
  .option('--format <format>', 'Output format (json or text)', 'text')
  .action((options) => {
    try {
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: options.timezone,
        year: 'numeric',
        month: 'numeric',
        day: 'numeric'
      });
      
      const parts = formatter.formatToParts(new Date());
      const year = parseInt(parts.find(p => p.type === 'year')!.value);
      const month = parseInt(parts.find(p => p.type === 'month')!.value);
      const day = parseInt(parts.find(p => p.type === 'day')!.value);
      
      const result = calendar.gregorianToHijri(year, month, day);
      
      if (options.format === 'json') {
        console.log(JSON.stringify({
          gregorian: { year, month, day, calendar: 'gregorian' },
          hijri: result.output,
          jdn: result.jdn,
          day_of_week: result.day_of_week,
          timezone: options.timezone
        }, null, 2));
      } else {
        const gregStr = `${year}-${String(month).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const hijri = result.output;
        const hijriStr = `${hijri.year}-${String(hijri.month).padStart(2, '0')}-${String(hijri.day).padStart(2, '0')}`;
        console.log(`Gregorian: ${gregStr}\nHijri: ${hijriStr}\nDay: ${result.day_of_week.name_en}`);
      }
    } catch (error) {
      handleError(error);
    }
  });

program
  .command('validate')
  .description('Validate a date')
  .requiredOption('--calendar <calendar>', 'Calendar (gregorian or hijri)')
  .requiredOption('--date <date>', 'Date in YYYY-MM-DD format')
  .option('--format <format>', 'Output format (json or text)', 'text')
  .action((options) => {
    try {
      const [yearStr, monthStr, dayStr] = options.date.split('-');
      const year = parseInt(yearStr, 10);
      const month = parseInt(monthStr, 10);
      const day = parseInt(dayStr, 10);
      
      if (isNaN(year) || isNaN(month) || isNaN(day)) {
        console.error('Error: Invalid date format. Use YYYY-MM-DD');
        process.exit(1);
      }
      
      const cal = options.calendar === 'hijri' ? 'hijri-ummalqura' : options.calendar;
      
      let result;
      if (cal === 'gregorian') {
        result = calendar.validateGregorianDate(year, month, day);
      } else if (cal === 'hijri-ummalqura') {
        result = calendar.validateHijriDate(year, month, day);
      } else {
        console.error('Error: Unsupported calendar');
        process.exit(1);
      }
      
      if (options.format === 'json') {
        console.log(JSON.stringify(result, null, 2));
      } else {
        if (result.valid) {
          console.log('Valid');
        } else {
          console.log(`Invalid: ${result.error?.message}`);
        }
      }
    } catch (error) {
      handleError(error);
    }
  });

program
  .command('calendar')
  .description('Show calendar for a month')
  .requiredOption('--calendar <calendar>', 'Calendar (gregorian or hijri)')
  .requiredOption('--year <year>', 'Year')
  .requiredOption('--month <month>', 'Month (1-12)')
  .option('--format <format>', 'Output format (json or text)', 'text')
  .action((options) => {
    try {
      const year = parseInt(options.year, 10);
      const month = parseInt(options.month, 10);
      
      if (isNaN(year) || isNaN(month)) {
        console.error('Error: Year and month must be integers');
        process.exit(1);
      }
      
      const cal = options.calendar === 'hijri' ? 'hijri-ummalqura' : options.calendar;
      
      let result;
      if (cal === 'gregorian') {
        result = calendar.getGregorianMonth(year, month);
      } else if (cal === 'hijri-ummalqura') {
        result = calendar.getHijriMonth(year, month);
      } else {
        console.error('Error: Unsupported calendar');
        process.exit(1);
      }
      
      if (options.format === 'json') {
        console.log(JSON.stringify(result, null, 2));
      } else {
        console.log(`${result.month_name_en} ${result.year} (${result.calendar})\n`);
        console.log('Day  Gregorian    Hijri       Day of Week');
        console.log('---  ----------   ----------  -----------');
        for (const day of result.days) {
          const g = day.gregorian;
          const h = day.hijri;
          const dayNum = String(day.gregorian.day).padStart(2, ' ');
          const gregDate = `${g.year}-${String(g.month).padStart(2, '0')}-${String(g.day).padStart(2, '0')}`;
          const hijriDate = `${h.year}-${String(h.month).padStart(2, '0')}-${String(h.day).padStart(2, '0')}`;
          console.log(`${dayNum}  ${gregDate}   ${hijriDate}  ${day.day_of_week.name_en}`);
        }
      }
    } catch (error) {
      handleError(error);
    }
  });

program.parse();
