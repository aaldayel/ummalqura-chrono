/**
 * Locale data loader
 *
 * Loads locale data from JSON files in data/locales/.
 * Falls back to hard-coded defaults for 'en' and 'ar'.
 */

import * as fs from 'fs';
import * as path from 'path';
import { LocaleData } from './types.js';

function findLocalesDir(): string {
  const paths = [
    path.join(__dirname, '..', '..', '..', 'data', 'locales'),
    path.join(__dirname, '..', 'data', 'locales'),
    path.join(__dirname, '..', '..', 'data', 'locales'),
  ];
  for (const p of paths) {
    if (fs.existsSync(p)) {
      return p;
    }
  }
  return path.join(__dirname, '..', '..', 'data', 'locales');
}

const LOCALES_DIR = findLocalesDir();

const DEFAULT_EN: LocaleData = {
  code: 'en',
  name: 'English',
  gregorian_months: ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'],
  gregorian_months_short: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  hijri_months: ['Muharram', 'Safar', 'Rabi al-Awwal', 'Rabi al-Thani', 'Jumada al-Ula', 'Jumada al-Thani', 'Rajab', "Sha'ban", 'Ramadan', 'Shawwal', "Dhul Qi'dah", 'Dhul Hijjah'],
  hijri_months_short: ['Muh', 'Saf', 'Rab1', 'Rab2', 'Jum1', 'Jum2', 'Raj', 'Sha', 'Ram', 'Shaw', 'DhuQ', 'DhuH'],
  days: ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday'],
  days_short: ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'],
  days_min: ['Su', 'Mo', 'Tu', 'We', 'Th', 'Fr', 'Sa'],
  meridiem: { am: 'AM', pm: 'PM' },
  rtl: false,
};

const DEFAULT_AR: LocaleData = {
  code: 'ar',
  name: 'العربية',
  gregorian_months: ['يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو', 'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'],
  gregorian_months_short: ['ينا', 'فبر', 'مار', ' أبر', 'ماي', 'يون', 'يول', 'أغس', 'سبت', 'أكت', 'نوف', 'ديس'],
  hijri_months: ['محرم', 'صفر', 'ربيع الأول', 'ربيع الثاني', 'جمادى الأولى', 'جمادى الثانية', 'رجب', 'شعبان', 'رمضان', 'شوال', 'ذو القعدة', 'ذو الحجة'],
  hijri_months_short: ['محر', 'صفر', 'ربيع1', 'ربيع2', 'جمع1', 'جمع2', 'رجب', 'شعب', 'رمض', 'شوا', 'قعد', 'حج'],
  days: ['الأحد', 'الاثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة', 'السبت'],
  days_short: ['أحد', 'اثن', 'ثلا', 'أرب', 'خمي', 'جمع', 'سبت'],
  days_min: ['أح', 'اث', 'ث', 'أر', 'خ', 'ج', 'س'],
  meridiem: { am: 'صباحاً', pm: 'مساءً' },
  rtl: true,
};

const DEFAULTS: Record<string, LocaleData> = {
  en: DEFAULT_EN,
  ar: DEFAULT_AR,
};

const cache = new Map<string, LocaleData>();

export function loadLocale(locale: string): LocaleData {
  if (cache.has(locale)) {
    return cache.get(locale)!;
  }

  // Try loading from file
  try {
    const filePath = path.join(LOCALES_DIR, `${locale}.json`);
    if (fs.existsSync(filePath)) {
      const data = JSON.parse(fs.readFileSync(filePath, 'utf-8'));
      cache.set(locale, data);
      return data;
    }
  } catch {
    // Fall through to defaults
  }

  // Fall back to hard-coded defaults
  const fallback = DEFAULTS[locale] || DEFAULTS['en'];
  cache.set(locale, fallback);
  return fallback;
}

export function getGregorianMonthName(month: number, locale: string): string {
  const loc = loadLocale(locale);
  return loc.gregorian_months[month - 1] || `Month ${month}`;
}

export function getHijriMonthName(month: number, locale: string): string {
  const loc = loadLocale(locale);
  return loc.hijri_months[month - 1] || `Month ${month}`;
}

export function getDayNames(locale: string): string[] {
  const loc = loadLocale(locale);
  return loc.days;
}

export function getLocaleData(locale: string): LocaleData {
  return loadLocale(locale);
}
