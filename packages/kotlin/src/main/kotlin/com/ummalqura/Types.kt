package com.ummalqura

enum class CalendarType(val value: String) {
    GREGORIAN("gregorian"),
    HIJRI_UMMALQURA("hijri-ummalqura")
}

enum class ErrorCode(val value: String) {
    INVALID_DAY("INVALID_DAY"),
    INVALID_MONTH("INVALID_MONTH"),
    INVALID_YEAR("INVALID_YEAR"),
    OUT_OF_RANGE("OUT_OF_RANGE"),
    UNSUPPORTED_CALENDAR("UNSUPPORTED_CALENDAR"),
    INVALID_TIMEZONE("INVALID_TIMEZONE"),
    MALFORMED_INPUT("MALFORMED_INPUT")
}

data class GregorianDate(
    val year: Int,
    val month: Int,
    val day: Int,
    val calendar: String = "gregorian"
)

data class HijriDate(
    val year: Int,
    val month: Int,
    val day: Int,
    val calendar: String = "hijri-ummalqura"
)

data class DayOfWeek(
    val index: Int,
    val nameEn: String,
    val nameAr: String
)

data class ConversionResult(
    val input: Any,
    val output: Any,
    val jdn: Int,
    val dayOfWeek: DayOfWeek,
    val locale: String,
    val libraryVersion: String,
    val dataVersion: String
)

class CalendarError(
    val errorCode: ErrorCode,
    override val message: String,
    val field: String? = null,
    val value: Any? = null
) : RuntimeException(message)

data class ValidationResult(
    val valid: Boolean,
    val error: CalendarError? = null
)

data class MonthInfo(
    val hijriYear: Int,
    val hijriMonth: Int,
    val monthLength: Int,
    val firstDayJdn: Int
)
