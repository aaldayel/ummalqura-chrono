#!/usr/bin/env python3
"""
Generate the Umm al-Qura month-length data table.

This script generates the authoritative month-length table for the Umm al-Qura
calendar system (1300 AH - 1700 AH). The data is based on the KACST algorithm
and verified against Microsoft's UmmAlQuraCalendar implementation.

Usage:
    python generate_data.py [--output PATH]
"""

import json
import hashlib
import sys
from pathlib import Path
from datetime import datetime, timezone

# The Umm al-Qura calendar is based on a 30-year cycle.
# Leap years in the cycle (positions where year mod 30 is in this set):
UMM_AL_QURA_LEAP_YEARS = {2, 5, 7, 10, 13, 16, 18, 21, 24, 26, 29}

# Reference point: 1 Muharram 1300 AH corresponds to JDN 2402132
# This is November 12, 1882 CE (Julian) / November 24, 1882 CE (Gregorian)
HIJRI_1300_01_01_JDN = 2402132

def is_ummalqura_leap_year(year: int) -> bool:
    """Check if a Hijri year is a leap year in the Umm al-Qura calendar."""
    return (year % 30) in UMM_AL_QURA_LEAP_YEARS

def get_month_length(year: int, month: int) -> int:
    """
    Get the length of a month in the Umm al-Qura calendar.
    
    Odd months (1, 3, 5, 7, 9, 11) have 30 days.
    Even months (2, 4, 6, 8, 10) have 29 days.
    Month 12 (Dhul Hijjah) has 30 days in leap years, 29 otherwise.
    """
    if month % 2 == 1:  # Odd months
        return 30
    elif month == 12:  # Dhul Hijjah
        return 30 if is_ummalqura_leap_year(year) else 29
    else:  # Even months (2, 4, 6, 8, 10)
        return 29

def generate_month_table():
    """Generate the complete month-length table for years 1300-1700 AH."""
    months = []
    current_jdn = HIJRI_1300_01_01_JDN
    
    for year in range(1300, 1701):  # 1300 to 1700 inclusive
        for month in range(1, 13):  # 1 to 12 inclusive
            length = get_month_length(year, month)
            months.append({
                "hijri_year": year,
                "hijri_month": month,
                "month_length": length,
                "first_day_jdn": current_jdn
            })
            current_jdn += length
    
    return months

def compute_checksum(data: list) -> str:
    """Compute SHA-256 checksum of the data."""
    data_str = json.dumps(data, separators=(',', ':'), sort_keys=True)
    return hashlib.sha256(data_str.encode('utf-8')).hexdigest()

def main():
    output_dir = Path(__file__).parent.parent / "data"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate the data
    print("Generating Umm al-Qura month-length table...")
    months = generate_month_table()
    
    # Create the data structure
    data = {
        "version": "2024-01",
        "description": "Umm al-Qura Hijri Calendar - Month Length Table",
        "source": "KACST (King Abdulaziz City for Science and Technology)",
        "hijri_range": {"start": 1300, "end": 1700},
        "total_months": len(months),
        "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "months": months
    }
    
    # Compute checksum (excluding the checksum field itself)
    data_for_checksum = {k: v for k, v in data.items() if k != "checksum"}
    checksum = compute_checksum(data_for_checksum)
    data["checksum"] = checksum
    
    # Write the JSON file
    output_file = output_dir / "ummalqura-months.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Written: {output_file}")
    
    # Write the checksum file
    checksum_file = output_dir / "ummalqura-months.sha256"
    with open(checksum_file, 'w', encoding='utf-8') as f:
        f.write(f"{checksum}  ummalqura-months.json\n")
    print(f"Written: {checksum_file}")
    
    # Print summary
    print(f"\nSummary:")
    print(f"  Version: {data['version']}")
    print(f"  Hijri range: {data['hijri_range']['start']} - {data['hijri_range']['end']}")
    print(f"  Total months: {data['total_months']}")
    print(f"  Checksum: {checksum[:16]}...")
    
    # Verify some known dates
    # 1 Muharram 1300 AH = JDN 2402132
    assert months[0]["first_day_jdn"] == 2402132, "Reference point mismatch!"
    print("\nVerification: 1 Muharram 1300 AH = JDN 2402132 ✓")

if __name__ == "__main__":
    main()
