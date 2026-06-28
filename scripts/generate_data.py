#!/usr/bin/env python3
"""
Generate the Umm al-Qura month-length data table from official Saudi tables.

Data is extracted from Microsoft's UmAlQuraCalendar implementation, which is
sourced from KACST UmAlQura.xls (see scripts/UmAlQuraCalendar.cs.reference).

Supported Hijri range: 1318 AH – 1500 AH (matches the official published tables).

Usage:
    python scripts/generate_data.py
"""

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
REFERENCE_FILE = SCRIPT_DIR / "UmAlQuraCalendar.cs.reference"
OUTPUT_FILE = ROOT / "data" / "ummalqura-months.json"
CHECKSUM_FILE = ROOT / "data" / "ummalqura-months.sha256"

# Package-local copies for standalone installs
PACKAGE_DATA_PATHS = [
    ROOT / "packages" / "python" / "ummalqura" / "data" / "ummalqura-months.json",
    ROOT / "packages" / "js" / "data" / "ummalqura-months.json",
]

YEAR_PATTERN = re.compile(
    r"(\d{4})\*/0x([0-9A-Fa-f]+),\s*(\d+),\s*(\d+),\s*(\d+)"
)


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """Fliegel & Van Flandern (1968), proleptic Gregorian."""
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    return (
        day
        + (153 * m + 2) // 5
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )


def month_lengths_from_flags(flags: int) -> list[int]:
    """Each bit: 1 = 30 days, 0 = 29 days (months 1–12, LSB = month 1)."""
    return [30 if (flags & (1 << i)) else 29 for i in range(12)]


def parse_reference_years() -> list[dict]:
    """Parse year entries from the downloaded UmAlQuraCalendar.cs reference."""
    if not REFERENCE_FILE.exists():
        raise FileNotFoundError(
            f"Missing {REFERENCE_FILE}. Download from dotnet/runtime "
            "System/Globalization/UmAlQuraCalendar.cs"
        )

    years = []
    for line in REFERENCE_FILE.read_text(encoding="utf-8").splitlines():
        match = YEAR_PATTERN.search(line)
        if not match:
            continue
        hijri_year = int(match.group(1))
        flags = int(match.group(2), 16)
        g_year = int(match.group(3))
        g_month = int(match.group(4))
        g_day = int(match.group(5))
        years.append(
            {
                "hijri_year": hijri_year,
                "flags": flags,
                "muharram_gregorian": (g_year, g_month, g_day),
                "month_lengths": month_lengths_from_flags(flags),
            }
        )

    years.sort(key=lambda y: y["hijri_year"])
    return years


def generate_month_table(years: list[dict]) -> list[dict]:
    """Build per-month rows with first_day_jdn and month_length."""
    months = []
    for year_info in years:
        hijri_year = year_info["hijri_year"]
        lengths = year_info["month_lengths"]
        gy, gm, gd = year_info["muharram_gregorian"]
        current_jdn = gregorian_to_jdn(gy, gm, gd)

        for month in range(1, 13):
            length = lengths[month - 1]
            months.append(
                {
                    "hijri_year": hijri_year,
                    "hijri_month": month,
                    "month_length": length,
                    "first_day_jdn": current_jdn,
                }
            )
            current_jdn += length

    return months


def compute_checksum(data: dict) -> str:
    payload = {k: v for k, v in data.items() if k != "checksum"}
    data_str = json.dumps(payload, separators=(",", ":"), sort_keys=True)
    return hashlib.sha256(data_str.encode("utf-8")).hexdigest()


def write_data_file(data: dict, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def main() -> None:
    print("Parsing official UmAlQura calendar reference...")
    years = parse_reference_years()
    if not years:
        raise RuntimeError("No year entries parsed from reference file")

    hijri_start = years[0]["hijri_year"]
    hijri_end = years[-1]["hijri_year"]
    months = generate_month_table(years)

    data = {
        "version": "2026-06",
        "description": "Umm al-Qura Hijri Calendar - Month Length Table",
        "source": (
            "KACST UmAlQura.xls via Microsoft .NET UmAlQuraCalendar "
            "(scripts/UmAlQuraCalendar.cs.reference)"
        ),
        "hijri_range": {"start": hijri_start, "end": hijri_end},
        "total_months": len(months),
        "generated_at": datetime.now(timezone.utc)
        .isoformat()
        .replace("+00:00", "Z"),
        "months": months,
    }
    data["checksum"] = compute_checksum(data)

    write_data_file(data, OUTPUT_FILE)
    CHECKSUM_FILE.write_text(f"{data['checksum']}  ummalqura-months.json\n", encoding="utf-8")

    for package_path in PACKAGE_DATA_PATHS:
        write_data_file(data, package_path)
        print(f"Written: {package_path}")

    print(f"\nSummary:")
    print(f"  Version: {data['version']}")
    print(f"  Hijri range: {hijri_start} - {hijri_end}")
    print(f"  Total months: {len(months)}")
    print(f"  Checksum: {data['checksum'][:16]}...")

    # Spot-check against Microsoft anchor dates
    checks = [
        (1318, 1, 1, (1900, 4, 30)),
        (1445, 1, 1, (2023, 7, 19)),
        (1445, 9, 5, (2024, 3, 15)),
        (1500, 12, 30, None),  # last day existence only
    ]
    month_index = {
        (m["hijri_year"], m["hijri_month"]): m for m in months
    }
    for hy, hm, hd, expected_g in checks:
        entry = month_index[(hy, hm)]
        jdn = entry["first_day_jdn"] + hd - 1
        if expected_g:
            from_jdn = _jdn_to_gregorian(jdn)
            assert from_jdn == expected_g, f"{hy}-{hm:02d}-{hd:02d}: {from_jdn} != {expected_g}"
            print(f"  ✓ {hy}-{hm:02d}-{hd:02d} = {expected_g[0]}-{expected_g[1]:02d}-{expected_g[2]:02d}")

    print("\nDone.")


def _jdn_to_gregorian(jdn: int) -> tuple[int, int, int]:
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    return year, month, day


if __name__ == "__main__":
    main()
