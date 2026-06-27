"""
Locale data loader

Loads locale data from JSON files in data/locales/.
Falls back to hard-coded defaults for 'en' and 'ar'.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from functools import lru_cache
from dataclasses import dataclass


@dataclass(frozen=True)
class LocaleData:
    code: str
    name: str
    gregorian_months: List[str]
    gregorian_months_short: List[str]
    hijri_months: List[str]
    hijri_months_short: List[str]
    days: List[str]
    days_short: List[str]
    days_min: List[str]
    meridiem: Dict[str, str]
    rtl: bool


def _find_locales_dir() -> Path:
    paths = [
        Path(__file__).parent / "data" / "locales",
        Path(__file__).parent.parent.parent.parent / "data" / "locales",
    ]
    for p in paths:
        if p.exists():
            return p
    return Path(__file__).parent / "data" / "locales"

LOCALES_DIR = _find_locales_dir()

_DEFAULT_EN = LocaleData(
    code="en",
    name="English",
    gregorian_months=["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"],
    gregorian_months_short=["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
    hijri_months=["Muharram", "Safar", "Rabi al-Awwal", "Rabi al-Thani", "Jumada al-Ula", "Jumada al-Thani", "Rajab", "Sha'ban", "Ramadan", "Shawwal", "Dhul Qi'dah", "Dhul Hijjah"],
    hijri_months_short=["Muh", "Saf", "Rab1", "Rab2", "Jum1", "Jum2", "Raj", "Sha", "Ram", "Shaw", "DhuQ", "DhuH"],
    days=["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"],
    days_short=["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"],
    days_min=["Su", "Mo", "Tu", "We", "Th", "Fr", "Sa"],
    meridiem={"am": "AM", "pm": "PM"},
    rtl=False,
)

_DEFAULT_AR = LocaleData(
    code="ar",
    name="العربية",
    gregorian_months=["يناير", "فبراير", "مارس", "أبريل", "مايو", "يونيو", "يوليو", "أغسطس", "سبتمبر", "أكتوبر", "نوفمبر", "ديسمبر"],
    gregorian_months_short=["ينا", "فبر", "مار", " أبر", "ماي", "يون", "يول", "أغس", "سبت", "أكت", "نوف", "ديس"],
    hijri_months=["محرم", "صفر", "ربيع الأول", "ربيع الثاني", "جمادى الأولى", "جمادى الثانية", "رجب", "شعبان", "رمضان", "شوال", "ذو القعدة", "ذو الحجة"],
    hijri_months_short=["محر", "صفر", "ربيع1", "ربيع2", "جمع1", "جمع2", "رجب", "شعب", "رمض", "شوا", "قعد", "حج"],
    days=["الأحد", "الاثنين", "الثلاثاء", "الأربعاء", "الخميس", "الجمعة", "السبت"],
    days_short=["أحد", "اثن", "ثلا", "أرب", "خمي", "جمع", "سبت"],
    days_min=["أح", "اث", "ث", "أر", "خ", "ج", "س"],
    meridiem={"am": "صباحاً", "pm": "مساءً"},
    rtl=True,
)

_DEFAULTS: Dict[str, LocaleData] = {
    "en": _DEFAULT_EN,
    "ar": _DEFAULT_AR,
}


@lru_cache(maxsize=32)
def load_locale(locale: str) -> LocaleData:
    """Load locale data, with filesystem + caching + fallback."""
    # Try loading from file
    file_path = LOCALES_DIR / f"{locale}.json"
    try:
        if file_path.exists():
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return LocaleData(
                code=data["code"],
                name=data["name"],
                gregorian_months=data["gregorian_months"],
                gregorian_months_short=data["gregorian_months_short"],
                hijri_months=data["hijri_months"],
                hijri_months_short=data["hijri_months_short"],
                days=data["days"],
                days_short=data["days_short"],
                days_min=data["days_min"],
                meridiem=data["meridiem"],
                rtl=data["rtl"],
            )
    except (json.JSONDecodeError, OSError, KeyError):
        pass

    # Fall back to hard-coded defaults
    return _DEFAULTS.get(locale, _DEFAULTS["en"])


def get_gregorian_month_name(month: int, locale: str) -> str:
    loc = load_locale(locale)
    return loc.gregorian_months[month - 1]


def get_hijri_month_name(month: int, locale: str) -> str:
    loc = load_locale(locale)
    return loc.hijri_months[month - 1]


def get_day_names(locale: str) -> List[str]:
    loc = load_locale(locale)
    return loc.days
