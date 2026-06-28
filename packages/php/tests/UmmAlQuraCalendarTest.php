<?php

namespace UmmAlQura\Tests;

use PHPUnit\Framework\TestCase;
use UmmAlQura\UmmAlQuraCalendar;
use UmmAlQura\CalendarError;
use UmmAlQura\ErrorCode;

class UmmAlQuraCalendarTest extends TestCase
{
    private UmmAlQuraCalendar $calendar;

    protected function setUp(): void
    {
        $this->calendar = new UmmAlQuraCalendar();
    }

    public function testVersion(): void
    {
        $this->assertSame('1.0.0', $this->calendar->getVersion());
    }

    public function testDataVersion(): void
    {
        $this->assertNotEmpty($this->calendar->getDataVersion());
    }

    public function testDataChecksum(): void
    {
        $this->assertNotEmpty($this->calendar->getDataChecksum());
    }

    public function testHijriRange(): void
    {
        $range = $this->calendar->getHijriRange();
        $this->assertSame(1318, $range['start']);
        $this->assertSame(1500, $range['end']);
    }

    public function testGregorianRange(): void
    {
        $range = $this->calendar->getGregorianRange();
        $this->assertGreaterThan($range['min'], $range['max']);
        $this->assertGreaterThan(1800, $range['min']);
        $this->assertLessThan(2300, $range['max']);
    }

    public function testGregorianToHijriKnownDate(): void
    {
        $result = $this->calendar->gregorianToHijri(2024, 3, 15);
        $this->assertSame(1445, $result->getOutput()->getYear());
        $this->assertSame(9, $result->getOutput()->getMonth());
        $this->assertSame(5, $result->getOutput()->getDay());
    }

    public function testGregorianToHijriJdn(): void
    {
        $result = $this->calendar->gregorianToHijri(2024, 3, 15);
        $this->assertSame(2460385, $result->getJdn());
    }

    public function testGregorianToHijriDayOfWeek(): void
    {
        $result = $this->calendar->gregorianToHijri(2024, 3, 15);
        $dow = $result->getDayOfWeek();
        $this->assertSame(5, $dow->getIndex());
        $this->assertSame('Friday', $dow->getNameEn());
    }

    public function testGregorianToHijriInvalidMonth(): void
    {
        $this->expectException(CalendarError::class);
        $this->calendar->gregorianToHijri(2024, 13, 1);
    }

    public function testGregorianToHijriInvalidDay(): void
    {
        $this->expectException(CalendarError::class);
        $this->calendar->gregorianToHijri(2024, 2, 30);
    }

    public function testGregorianToHijriYearOutOfRange(): void
    {
        $this->expectException(CalendarError::class);
        $this->calendar->gregorianToHijri(1800, 1, 1);
    }

    public function testHijriToGregorianKnownDate(): void
    {
        $result = $this->calendar->hijriToGregorian(1445, 9, 5);
        $this->assertSame(2024, $result->getOutput()->getYear());
        $this->assertSame(3, $result->getOutput()->getMonth());
        $this->assertSame(15, $result->getOutput()->getDay());
    }

    public function testHijriToGregorianInvalidMonth(): void
    {
        $this->expectException(CalendarError::class);
        $this->calendar->hijriToGregorian(1445, 13, 1);
    }

    public function testHijriToGregorianInvalidDay(): void
    {
        $this->expectException(CalendarError::class);
        $this->calendar->hijriToGregorian(1445, 9, 31);
    }

    public function testHijriToGregorianYearOutOfRange(): void
    {
        $this->expectException(CalendarError::class);
        $this->calendar->hijriToGregorian(1200, 1, 1);
    }

    public function testRoundTripGregorian(): void
    {
        $dates = [
            [2024, 3, 15],
            [2000, 1, 1],
            [1900, 6, 15],
            [2024, 12, 31]
        ];

        foreach ($dates as [$year, $month, $day]) {
            $hijri = $this->calendar->gregorianToHijri($year, $month, $day);
            $gregorian = $this->calendar->hijriToGregorian(
                $hijri->getOutput()->getYear(),
                $hijri->getOutput()->getMonth(),
                $hijri->getOutput()->getDay()
            );
            $this->assertSame($year, $gregorian->getOutput()->getYear());
            $this->assertSame($month, $gregorian->getOutput()->getMonth());
            $this->assertSame($day, $gregorian->getOutput()->getDay());
        }
    }

    public function testRoundTripHijri(): void
    {
        $dates = [
            [1445, 9, 5],
            [1400, 1, 1],
            [1350, 6, 15],
            [1500, 12, 29]
        ];

        foreach ($dates as [$year, $month, $day]) {
            $gregorian = $this->calendar->hijriToGregorian($year, $month, $day);
            $hijri = $this->calendar->gregorianToHijri(
                $gregorian->getOutput()->getYear(),
                $gregorian->getOutput()->getMonth(),
                $gregorian->getOutput()->getDay()
            );
            $this->assertSame($year, $hijri->getOutput()->getYear());
            $this->assertSame($month, $hijri->getOutput()->getMonth());
            $this->assertSame($day, $hijri->getOutput()->getDay());
        }
    }

    public function testDayOfWeek(): void
    {
        $dow = $this->calendar->getDayOfWeek(2460385);
        $this->assertSame(5, $dow->getIndex());
        $this->assertSame('Friday', $dow->getNameEn());
    }

    public function testDayOfWeekGregorian(): void
    {
        $dow = $this->calendar->getDayOfWeekGregorian(2024, 3, 15);
        $this->assertSame(5, $dow->getIndex());
        $this->assertSame('Friday', $dow->getNameEn());
    }

    public function testDayOfWeekHijri(): void
    {
        $dow = $this->calendar->getDayOfWeekHijri(1445, 9, 5);
        $this->assertSame(5, $dow->getIndex());
        $this->assertSame('Friday', $dow->getNameEn());
    }

    public function testGregorianMonthLengths(): void
    {
        $this->assertSame(31, $this->calendar->getGregorianMonthLength(2024, 1));
        $this->assertSame(29, $this->calendar->getGregorianMonthLength(2024, 2));
        $this->assertSame(28, $this->calendar->getGregorianMonthLength(2023, 2));
        $this->assertSame(30, $this->calendar->getGregorianMonthLength(2024, 4));
    }

    public function testHijriMonthLengths(): void
    {
        $this->assertSame(29, $this->calendar->getHijriMonthLength(1445, 1));
        $this->assertSame(30, $this->calendar->getHijriMonthLength(1445, 2));
        $this->assertSame(30, $this->calendar->getHijriMonthLength(1445, 12));
    }

    public function testLeapYears(): void
    {
        $this->assertTrue($this->calendar->isGregorianLeapYear(2024));
        $this->assertFalse($this->calendar->isGregorianLeapYear(2023));
        $this->assertFalse($this->calendar->isGregorianLeapYear(1900));
        $this->assertTrue($this->calendar->isGregorianLeapYear(2000));
    }

    public function testValidationValidGregorian(): void
    {
        $result = $this->calendar->validateGregorianDate(2024, 3, 15);
        $this->assertTrue($result->isValid());
        $this->assertNull($result->getError());
    }

    public function testValidationInvalidGregorianMonth(): void
    {
        $result = $this->calendar->validateGregorianDate(2024, 13, 1);
        $this->assertFalse($result->isValid());
        $this->assertSame(ErrorCode::INVALID_MONTH, $result->getError()->getErrorCode());
    }

    public function testValidationInvalidGregorianDay(): void
    {
        $result = $this->calendar->validateGregorianDate(2024, 2, 30);
        $this->assertFalse($result->isValid());
        $this->assertSame(ErrorCode::INVALID_DAY, $result->getError()->getErrorCode());
    }

    public function testValidationValidHijri(): void
    {
        $result = $this->calendar->validateHijriDate(1445, 9, 5);
        $this->assertTrue($result->isValid());
        $this->assertNull($result->getError());
    }

    public function testValidationInvalidHijriMonth(): void
    {
        $result = $this->calendar->validateHijriDate(1445, 13, 1);
        $this->assertFalse($result->isValid());
        $this->assertSame(ErrorCode::INVALID_MONTH, $result->getError()->getErrorCode());
    }

    public function testBatchGregorianToHijri(): void
    {
        $dates = [
            ['year' => 2024, 'month' => 3, 'day' => 15],
            ['year' => 2024, 'month' => 3, 'day' => 16]
        ];

        $results = $this->calendar->batchGregorianToHijri($dates);
        $this->assertCount(2, $results);
        $this->assertSame(1445, $results[0]->getOutput()->getYear());
        $this->assertSame(9, $results[0]->getOutput()->getMonth());
        $this->assertSame(5, $results[0]->getOutput()->getDay());
        $this->assertSame(6, $results[1]->getOutput()->getDay());
    }

    public function testBatchHijriToGregorian(): void
    {
        $dates = [
            ['year' => 1445, 'month' => 9, 'day' => 5],
            ['year' => 1445, 'month' => 9, 'day' => 6]
        ];

        $results = $this->calendar->batchHijriToGregorian($dates);
        $this->assertCount(2, $results);
        $this->assertSame(2024, $results[0]->getOutput()->getYear());
        $this->assertSame(3, $results[0]->getOutput()->getMonth());
        $this->assertSame(15, $results[0]->getOutput()->getDay());
        $this->assertSame(16, $results[1]->getOutput()->getDay());
    }

    public function testStructuredErrorInvalidMonth(): void
    {
        try {
            $this->calendar->gregorianToHijri(2024, 13, 1);
            $this->fail('Should have thrown');
        } catch (CalendarError $e) {
            $this->assertSame(ErrorCode::INVALID_MONTH, $e->getErrorCode());
            $this->assertSame('month', $e->getField());
            $this->assertSame(13, $e->getValue());
        }
    }

    public function testStructuredErrorInvalidDay(): void
    {
        try {
            $this->calendar->hijriToGregorian(1445, 9, 31);
            $this->fail('Should have thrown');
        } catch (CalendarError $e) {
            $this->assertSame(ErrorCode::INVALID_DAY, $e->getErrorCode());
            $this->assertSame('day', $e->getField());
            $this->assertSame(31, $e->getValue());
        }
    }
}
