#!/usr/bin/env python3
"""
Validate data/ummalqura-months.json against Microsoft's UmAlQuraCalendar reference.

Exits with code 1 on any mismatch. Used in CI for authoritative correctness checks.
"""

import json
import re
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
ROOT = SCRIPT_DIR.parent
DATA_FILE = ROOT / "data" / "ummalqura-months.json"
REFERENCE_FILE = SCRIPT_DIR / "UmAlQuraCalendar.cs.reference"

YEAR_PATTERN = re.compile(
    r"(\d{4})\*/0x([0-9A-Fa-f]+),\s*(\d+),\s*(\d+),\s*(\d+)"
)


def gregorian_to_jdn(year: int, month: int, day: int) -> int:
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


def parse_reference() -> dict[int, dict]:
    years = {}
    for line in REFERENCE_FILE.read_text(encoding="utf-8").splitlines():
        match = YEAR_PATTERN.search(line)
        if not match:
            continue
        hy = int(match.group(1))
        flags = int(match.group(2), 16)
        lengths = [30 if (flags & (1 << i)) else 29 for i in range(12)]
        years[hy] = {
            "muharram": (int(match.group(3)), int(match.group(4)), int(match.group(5))),
            "lengths": lengths,
        }
    return years


def load_library_by_year() -> dict[int, dict]:
    with DATA_FILE.open(encoding="utf-8") as f:
        data = json.load(f)

    by_year: dict[int, dict] = {}
    for entry in data["months"]:
        y = entry["hijri_year"]
        if y not in by_year:
            by_year[y] = {"months": {}, "first_muharram_jdn": None}
        by_year[y]["months"][entry["hijri_month"]] = entry
        if entry["hijri_month"] == 1:
            by_year[y]["first_muharram_jdn"] = entry["first_day_jdn"]

    return by_year


def main() -> int:
    if not DATA_FILE.exists():
        print(f"Missing data file: {DATA_FILE}", file=sys.stderr)
        return 1
    if not REFERENCE_FILE.exists():
        print(f"Missing reference file: {REFERENCE_FILE}", file=sys.stderr)
        return 1

    ms = parse_reference()
    lib = load_library_by_year()

    mismatches = []
    for hy, ms_year in sorted(ms.items()):
        if hy not in lib:
            mismatches.append(f"Missing Hijri year {hy} in library data")
            continue

        lib_year = lib[hy]
        gy, gm, gd = ms_year["muharram"]
        expected_jdn = gregorian_to_jdn(gy, gm, gd)
        if lib_year["first_muharram_jdn"] != expected_jdn:
            mismatches.append(
                f"{hy}-01-01 JDN: library={lib_year['first_muharram_jdn']} "
                f"expected={expected_jdn} ({gy}-{gm:02d}-{gd:02d})"
            )

        for month in range(1, 13):
            expected_len = ms_year["lengths"][month - 1]
            actual_len = lib_year["months"][month]["month_length"]
            if actual_len != expected_len:
                mismatches.append(
                    f"{hy}-{month:02d} length: library={actual_len} expected={expected_len}"
                )

    # Canonical conversion spot checks
    spot_checks = [
        ((2024, 3, 15), (1445, 9, 5)),
        ((2023, 7, 19), (1445, 1, 1)),
        ((2024, 4, 10), (1445, 10, 1)),
    ]
    sys.path.insert(0, str(ROOT / "packages" / "python"))
    from ummalqura import UmmAlQuraCalendar  # noqa: E402

    cal = UmmAlQuraCalendar()
    for g, expected_h in spot_checks:
        result = cal.gregorian_to_hijri(*g)
        got = (result.output.year, result.output.month, result.output.day)
        if got != expected_h:
            mismatches.append(f"G2H {g}: got {got} expected {expected_h}")

    if mismatches:
        print(f"Microsoft parity validation FAILED ({len(mismatches)} issues):")
        for m in mismatches[:20]:
            print(f"  - {m}")
        if len(mismatches) > 20:
            print(f"  ... and {len(mismatches) - 20} more")
        return 1

    print(f"Microsoft parity validation passed ({len(ms)} Hijri years).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
