package com.ummalqura

import com.google.gson.Gson
import com.google.gson.JsonObject
import java.io.File

class UmmAlQuraCalendar(
    dataPath: String? = null,
    private val defaultLocale: String = "en"
) {
    companion object {
        const val LIBRARY_VERSION = "1.0.0"
        
        private val GREGORIAN_MONTHS_EN = arrayOf(
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        )
        private val GREGORIAN_MONTHS_AR = arrayOf(
            "يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو",
            "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"
        )
        private val HIJRI_MONTHS_EN = arrayOf(
            "Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani",
            "Jumada al-Ula", "Jumada al-Thani", "Rajab", "Sha'ban",
            "Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah"
        )
        private val HIJRI_MONTHS_AR = arrayOf(
            "محرم", "صفر", "ربيع الأول", "ربيع الثاني",
            "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان",
            "رمضان", "شوال", "ذو القعدة", "ذو الحجة"
        )
    }

    private val months: List<MonthInfo>
    private val monthIndex: Map<String, MonthInfo>
    private val sortedMonths: Array<MonthInfo>
    private val gregorianYearRange: Pair<Int, Int>
    private val dataVersion: String
    private val dataChecksum: String
    private val hijriRange: Pair<Int, Int>

    init {
        val path = dataPath ?: findDataFile()
        val json = File(path).readText()
        val gson = Gson()
        val root = gson.fromJson(json, JsonObject::class.java)

        dataVersion = root.get("version").asString
        dataChecksum = root.get("checksum").asString

        val range = root.getAsJsonObject("hijri_range")
        hijriRange = Pair(range.get("start").asInt, range.get("end").asInt)

        val monthsArray = root.getAsJsonArray("months")
        months = monthsArray.map { item ->
            val obj = item.asJsonObject
            MonthInfo(
                hijriYear = obj.get("hijri_year").asInt,
                hijriMonth = obj.get("hijri_month").asInt,
                monthLength = obj.get("month_length").asInt,
                firstDayJdn = obj.get("first_day_jdn").asInt
            )
        }

        monthIndex = Core.buildMonthIndex(months)
        sortedMonths = Core.buildJdnIndex(months)
        gregorianYearRange = Core.getGregorianYearRange(months)
    }

    private fun findDataFile(): String {
        val paths = listOf(
            "../../data/ummalqura-months.json",
            "data/ummalqura-months.json",
        )
        for (path in paths) {
            if (File(path).exists()) return path
        }
        throw RuntimeException("Could not find ummalqura-months.json data file")
    }

    fun getVersion(): String = LIBRARY_VERSION
    fun getDataVersion(): String = dataVersion
    fun getDataChecksum(): String = dataChecksum
    fun getHijriRange(): Pair<Int, Int> = hijriRange
    fun getGregorianRange(): Pair<Int, Int> = gregorianYearRange

    fun gregorianToHijri(year: Int, month: Int, day: Int, locale: String? = null): ConversionResult {
        val error = Core.validateGregorian(year, month, day, gregorianYearRange.first, gregorianYearRange.second)
        if (error != null) throw error

        val jdn = Core.gregorianToJdn(year, month, day)
        val hijri = Core.jdnToHijri(jdn, sortedMonths)
        val dow = Core.dayOfWeekFromJdn(jdn)

        return ConversionResult(
            input = GregorianDate(year, month, day),
            output = hijri,
            jdn = jdn,
            dayOfWeek = dow,
            locale = locale ?: defaultLocale,
            libraryVersion = LIBRARY_VERSION,
            dataVersion = dataVersion
        )
    }

    fun hijriToGregorian(year: Int, month: Int, day: Int, locale: String? = null): ConversionResult {
        val error = Core.validateHijri(year, month, day, monthIndex)
        if (error != null) throw error

        val jdn = Core.hijriToJdn(year, month, day, monthIndex)
        val gregorian = Core.jdnToGregorian(jdn)
        val dow = Core.dayOfWeekFromJdn(jdn)

        return ConversionResult(
            input = HijriDate(year, month, day),
            output = gregorian,
            jdn = jdn,
            dayOfWeek = dow,
            locale = locale ?: defaultLocale,
            libraryVersion = LIBRARY_VERSION,
            dataVersion = dataVersion
        )
    }

    fun validateGregorianDate(year: Int, month: Int, day: Int): ValidationResult {
        val error = Core.validateGregorian(year, month, day, gregorianYearRange.first, gregorianYearRange.second)
        return ValidationResult(valid = error == null, error = error)
    }

    fun validateHijriDate(year: Int, month: Int, day: Int): ValidationResult {
        val error = Core.validateHijri(year, month, day, monthIndex)
        return ValidationResult(valid = error == null, error = error)
    }

    fun getDayOfWeek(jdn: Int): DayOfWeek = Core.dayOfWeekFromJdn(jdn)

    fun getDayOfWeekGregorian(year: Int, month: Int, day: Int): DayOfWeek =
        Core.dayOfWeekFromJdn(Core.gregorianToJdn(year, month, day))

    fun getDayOfWeekHijri(year: Int, month: Int, day: Int): DayOfWeek =
        Core.dayOfWeekFromJdn(Core.hijriToJdn(year, month, day, monthIndex))

    fun getGregorianMonthLength(year: Int, month: Int): Int = Core.gregorianMonthLength(year, month)

    fun getHijriMonthLength(year: Int, month: Int): Int {
        val key = "$year-$month"
        val entry = monthIndex[key] ?: throw CalendarError(
            ErrorCode.OUT_OF_RANGE, "Hijri date $key is outside the supported range"
        )
        return entry.monthLength
    }

    fun isGregorianLeapYear(year: Int): Boolean = Core.isGregorianLeapYear(year)
}
