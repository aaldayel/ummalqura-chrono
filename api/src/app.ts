import express from 'express';
import cors from 'cors';
import helmet from 'helmet';
import swaggerUi from 'swagger-ui-express';
import YAML from 'yamljs';
import path from 'path';
import { UmmAlQuraCalendar, ErrorCode } from 'ummalqura-chrono';

const calendar = new UmmAlQuraCalendar();
const openApiPath = path.join(__dirname, '..', 'openapi.yaml');
const swaggerDocument = YAML.load(openApiPath);
const app = express();

app.use(helmet());
app.use(cors());
app.use(express.json());
app.use('/docs', swaggerUi.serve, swaggerUi.setup(swaggerDocument));

function handleError(res: express.Response, error: any) {
  if (error.error_code) {
    const statusCode = error.error_code === ErrorCode.MALFORMED_INPUT ? 400 : 422;
    return res.status(statusCode).json(error);
  }
  console.error('Unexpected error:', error);
  return res.status(500).json({
    error_code: 'INTERNAL_ERROR',
    message: 'An unexpected error occurred'
  });
}

app.post('/v1/convert', (req, res) => {
  try {
    const { year, month, day, from, to } = req.body;
    const locale = (req.query.locale as string) || 'en';

    if (year === undefined || month === undefined || day === undefined || !from || !to) {
      return res.status(400).json({
        error_code: ErrorCode.MALFORMED_INPUT,
        message: 'Missing required fields: year, month, day, from, to'
      });
    }

    if (!['gregorian', 'hijri-ummalqura'].includes(from) ||
        !['gregorian', 'hijri-ummalqura'].includes(to)) {
      return res.status(400).json({
        error_code: ErrorCode.UNSUPPORTED_CALENDAR,
        message: 'Unsupported calendar type'
      });
    }

    let result;
    if (from === 'gregorian' && to === 'hijri-ummalqura') {
      result = calendar.gregorianToHijri(year, month, day, { locale });
    } else if (from === 'hijri-ummalqura' && to === 'gregorian') {
      result = calendar.hijriToGregorian(year, month, day, { locale });
    } else {
      return res.status(400).json({
        error_code: ErrorCode.UNSUPPORTED_CALENDAR,
        message: 'Conversion between same calendars is not supported'
      });
    }

    return res.json(result);
  } catch (error) {
    return handleError(res, error);
  }
});

app.post('/v1/convert/batch', (req, res) => {
  try {
    const { dates, from, to } = req.body;
    const locale = (req.query.locale as string) || 'en';

    if (!Array.isArray(dates) || dates.length === 0) {
      return res.status(400).json({
        error_code: ErrorCode.MALFORMED_INPUT,
        message: 'dates must be a non-empty array'
      });
    }

    if (dates.length > 1000) {
      return res.status(400).json({
        error_code: ErrorCode.MALFORMED_INPUT,
        message: 'Maximum 1000 dates per batch'
      });
    }

    let results;
    if (from === 'gregorian' && to === 'hijri-ummalqura') {
      results = calendar.batchGregorianToHijri(dates, { locale });
    } else if (from === 'hijri-ummalqura' && to === 'gregorian') {
      results = calendar.batchHijriToGregorian(dates, { locale });
    } else {
      return res.status(400).json({
        error_code: ErrorCode.UNSUPPORTED_CALENDAR,
        message: 'Unsupported conversion'
      });
    }

    return res.json({ results, total: results.length });
  } catch (error) {
    return handleError(res, error);
  }
});

app.get('/v1/today', (req, res) => {
  try {
    const timezone = req.query.timezone as string;
    const locale = (req.query.locale as string) || 'en';

    if (!timezone) {
      return res.status(400).json({
        error_code: ErrorCode.INVALID_TIMEZONE,
        message: 'timezone parameter is required'
      });
    }

    let now: Date;
    try {
      const formatter = new Intl.DateTimeFormat('en-US', {
        timeZone: timezone,
        year: 'numeric',
        month: 'numeric',
        day: 'numeric'
      });
      const parts = formatter.formatToParts(new Date());
      const year = parseInt(parts.find(p => p.type === 'year')!.value);
      const month = parseInt(parts.find(p => p.type === 'month')!.value);
      const day = parseInt(parts.find(p => p.type === 'day')!.value);
      now = new Date(year, month - 1, day);
    } catch {
      return res.status(400).json({
        error_code: ErrorCode.INVALID_TIMEZONE,
        message: `Invalid timezone: ${timezone}`
      });
    }

    const gYear = now.getFullYear();
    const gMonth = now.getMonth() + 1;
    const gDay = now.getDate();

    const result = calendar.gregorianToHijri(gYear, gMonth, gDay, { locale });

    return res.json({
      gregorian: { year: gYear, month: gMonth, day: gDay, calendar: 'gregorian' },
      hijri: result.output,
      jdn: result.jdn,
      day_of_week: result.day_of_week,
      timezone,
      locale
    });
  } catch (error) {
    return handleError(res, error);
  }
});

app.get('/v1/calendar/:calendar/:year/:month', (req, res) => {
  try {
    const { calendar: cal, year: yearStr, month: monthStr } = req.params;
    const locale = (req.query.locale as string) || 'en';
    const year = parseInt(yearStr, 10);
    const month = parseInt(monthStr, 10);

    if (!['gregorian', 'hijri-ummalqura'].includes(cal)) {
      return res.status(400).json({
        error_code: ErrorCode.UNSUPPORTED_CALENDAR,
        message: 'Unsupported calendar type'
      });
    }

    if (isNaN(year) || isNaN(month)) {
      return res.status(400).json({
        error_code: ErrorCode.MALFORMED_INPUT,
        message: 'year and month must be integers'
      });
    }

    let result;
    if (cal === 'gregorian') {
      result = calendar.getGregorianMonth(year, month, locale);
    } else {
      result = calendar.getHijriMonth(year, month, locale);
    }

    return res.json(result);
  } catch (error) {
    return handleError(res, error);
  }
});

app.get('/v1/validate', (req, res) => {
  try {
    const cal = req.query.calendar as string;
    const year = parseInt(req.query.year as string, 10);
    const month = parseInt(req.query.month as string, 10);
    const day = parseInt(req.query.day as string, 10);

    if (!cal || isNaN(year) || isNaN(month) || isNaN(day)) {
      return res.status(400).json({
        error_code: ErrorCode.MALFORMED_INPUT,
        message: 'calendar, year, month, and day are required'
      });
    }

    let result;
    if (cal === 'gregorian') {
      result = calendar.validateGregorianDate(year, month, day);
    } else if (cal === 'hijri-ummalqura') {
      result = calendar.validateHijriDate(year, month, day);
    } else {
      return res.status(400).json({
        error_code: ErrorCode.UNSUPPORTED_CALENDAR,
        message: 'Unsupported calendar type'
      });
    }

    return res.json(result);
  } catch (error) {
    return handleError(res, error);
  }
});

app.get('/v1/day-of-week', (req, res) => {
  try {
    const cal = req.query.calendar as string;
    const year = parseInt(req.query.year as string, 10);
    const month = parseInt(req.query.month as string, 10);
    const day = parseInt(req.query.day as string, 10);
    const locale = (req.query.locale as string) || 'en';

    if (!cal || isNaN(year) || isNaN(month) || isNaN(day)) {
      return res.status(400).json({
        error_code: ErrorCode.MALFORMED_INPUT,
        message: 'calendar, year, month, and day are required'
      });
    }

    let dow;
    if (cal === 'gregorian') {
      dow = calendar.getDayOfWeekGregorian(year, month, day);
    } else if (cal === 'hijri-ummalqura') {
      dow = calendar.getDayOfWeekHijri(year, month, day);
    } else {
      return res.status(400).json({
        error_code: ErrorCode.UNSUPPORTED_CALENDAR,
        message: 'Unsupported calendar type'
      });
    }

    return res.json({
      calendar: cal,
      year,
      month,
      day,
      day_of_week: dow
    });
  } catch (error) {
    return handleError(res, error);
  }
});

app.get('/v1/health', (_req, res) => {
  return res.json({
    status: 'ok',
    library_version: calendar.getVersion(),
    data_version: calendar.getDataVersion(),
    data_checksum: calendar.getDataChecksum(),
    supported_hijri_range: calendar.getHijriRange()
  });
});

const port = process.env.PORT || 3000;
app.listen(port, () => {
  console.log(`Umm al-Qura Calendar API listening on port ${port}`);
});

export default app;
