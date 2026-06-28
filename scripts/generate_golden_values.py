#!/usr/bin/env python3
"""
Generate golden-value test CSV for cross-language validation.

This script generates a comprehensive set of test vectors (Gregorian, Hijri, JDN triples)
that all language wrappers must use for validation.

Usage:
    python generate_golden_values.py [--output PATH] [--count N]
"""

import json
import csv
import sys
from pathlib import Path
from datetime import date, timedelta

# Load the month-length data
DATA_DIR = Path(__file__).parent.parent / "data"

def load_month_data():
    """Load the Umm al-Qura month-length table."""
    with open(DATA_DIR / "ummalqura-months.json", 'r', encoding='utf-8') as f:
        return json.load(f)

def gregorian_to_jdn(year: int, month: int, day: int) -> int:
    """
    Convert a Gregorian date to Julian Day Number.
    
    Uses the proleptic Gregorian calendar algorithm.
    Reference: Fliegel & Van Flandern (1968)
    """
    a = (14 - month) // 12
    y = year + 4800 - a
    m = month + 12 * a - 3
    
    jdn = day + (153 * m + 2) // 5 + 365 * y + y // 4 - y // 100 + y // 400 - 32045
    return jdn

def jdn_to_gregorian(jdn: int) -> tuple:
    """
    Convert Julian Day Number to Gregorian date.
    
    Reference: Fliegel & Van Flandern (1968)
    """
    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - (146097 * b) // 4
    d = (4 * c + 3) // 1461
    e = c - (1461 * d) // 4
    m = (5 * e + 2) // 153
    
    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10
    
    return (year, month, day)

def jdn_to_hijri(jdn: int, month_data: dict) -> tuple:
    """
    Convert Julian Day Number to Hijri (Umm al-Qura) date.
    
    Uses binary search on the month-length table.
    """
    months = month_data["months"]
    
    # Binary search for the month
    left, right = 0, len(months) - 1
    
    while left < right:
        mid = (left + right) // 2
        if months[mid]["first_day_jdn"] <= jdn:
            left = mid + 1
        else:
            right = mid
    
    # Adjust if we went too far
    if left > 0 and months[left]["first_day_jdn"] > jdn:
        left -= 1
    
    month_entry = months[left]
    day = jdn - month_entry["first_day_jdn"] + 1
    
    return (month_entry["hijri_year"], month_entry["hijri_month"], day)

def hijri_to_jdn(year: int, month: int, day: int, month_data: dict) -> int:
    """
    Convert Hijri (Umm al-Qura) date to Julian Day Number.
    
    Uses the month-length table for lookup.
    """
    months = month_data["months"]
    
    # Find the matching month entry
    for entry in months:
        if entry["hijri_year"] == year and entry["hijri_month"] == month:
            return entry["first_day_jdn"] + day - 1
    
    raise ValueError(f"Invalid Hijri date: {year}-{month:02d}-{day:02d}")

def get_day_of_week(jdn: int) -> tuple:
    """
    Get the day of week from JDN.
    
    Returns (index, name_en, name_ar) where index 0 = Sunday.
    """
    day_index = (jdn + 1) % 7  # JDN 0 is Monday, so +1 for Sunday=0
    
    days = [
        (0, "Sunday", "الأحد"),
        (1, "Monday", "الاثنين"),
        (2, "Tuesday", "الثلاثاء"),
        (3, "Wednesday", "الأربعاء"),
        (4, "Thursday", "الخميس"),
        (5, "Friday", "الجمعة"),
        (6, "Saturday", "السبت")
    ]
    
    return days[day_index]

def generate_golden_values(count: int = 10000):
    """
    Generate golden-value test vectors.
    
    Generates a comprehensive set of test vectors covering:
    - First and last day of every month in the range
    - Random dates throughout the range
    - Boundary cases
    """
    month_data = load_month_data()
    months = month_data["months"]
    
    vectors = []
    seen_jdns = set()
    
    # 1. First and last day of every Hijri month
    for entry in months:
        year = entry["hijri_year"]
        month = entry["hijri_month"]
        first_jdn = entry["first_day_jdn"]
        last_jdn = first_jdn + entry["month_length"] - 1
        
        # First day
        if first_jdn not in seen_jdns:
            g_year, g_month, g_day = jdn_to_gregorian(first_jdn)
            dow = get_day_of_week(first_jdn)
            vectors.append({
                "gregorian_year": g_year,
                "gregorian_month": g_month,
                "gregorian_day": g_day,
                "hijri_year": year,
                "hijri_month": month,
                "hijri_day": 1,
                "jdn": first_jdn,
                "day_of_week_index": dow[0],
                "day_of_week_en": dow[1],
                "day_of_week_ar": dow[2]
            })
            seen_jdns.add(first_jdn)
        
        # Last day
        if last_jdn not in seen_jdns:
            g_year, g_month, g_day = jdn_to_gregorian(last_jdn)
            dow = get_day_of_week(last_jdn)
            vectors.append({
                "gregorian_year": g_year,
                "gregorian_month": g_month,
                "gregorian_day": g_day,
                "hijri_year": year,
                "hijri_month": month,
                "hijri_day": entry["month_length"],
                "jdn": last_jdn,
                "day_of_week_index": dow[0],
                "day_of_week_en": dow[1],
                "day_of_week_ar": dow[2]
            })
            seen_jdns.add(last_jdn)
    
    # 2. Add specific reference dates (computed from the table, not hardcoded)
    reference_gregorian_dates = [
        (2024, 3, 15),
        (2024, 1, 1),
        (2000, 1, 1),
        (1900, 4, 30),
    ]

    for greg in reference_gregorian_dates:
        jdn = gregorian_to_jdn(*greg)
        if jdn not in seen_jdns:
            h_year, h_month, h_day = jdn_to_hijri(jdn, month_data)
            dow = get_day_of_week(jdn)
            vectors.append({
                "gregorian_year": greg[0],
                "gregorian_month": greg[1],
                "gregorian_day": greg[2],
                "hijri_year": h_year,
                "hijri_month": h_month,
                "hijri_day": h_day,
                "jdn": jdn,
                "day_of_week_index": dow[0],
                "day_of_week_en": dow[1],
                "day_of_week_ar": dow[2]
            })
            seen_jdns.add(jdn)
    
    # 3. Generate additional random-ish dates to reach target count
    # Use a deterministic sequence for reproducibility
    start_jdn = months[0]["first_day_jdn"]
    end_jdn = months[-1]["first_day_jdn"] + months[-1]["month_length"] - 1
    
    step = max(1, (end_jdn - start_jdn) // (count - len(vectors)))
    
    current_jdn = start_jdn
    while len(vectors) < count and current_jdn <= end_jdn:
        if current_jdn not in seen_jdns:
            g_year, g_month, g_day = jdn_to_gregorian(current_jdn)
            h_year, h_month, h_day = jdn_to_hijri(current_jdn, month_data)
            dow = get_day_of_week(current_jdn)
            
            vectors.append({
                "gregorian_year": g_year,
                "gregorian_month": g_month,
                "gregorian_day": g_day,
                "hijri_year": h_year,
                "hijri_month": h_month,
                "hijri_day": h_day,
                "jdn": current_jdn,
                "day_of_week_index": dow[0],
                "day_of_week_en": dow[1],
                "day_of_week_ar": dow[2]
            })
            seen_jdns.add(current_jdn)
        
        current_jdn += step
    
    # Sort by JDN for consistency
    vectors.sort(key=lambda v: v["jdn"])
    
    return vectors

def main():
    output_dir = Path(__file__).parent.parent / "tests" / "golden"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating golden-value test vectors...")
    vectors = generate_golden_values(count=10000)
    
    # Write CSV
    output_file = output_dir / "golden-values.csv"
    fieldnames = [
        "gregorian_year", "gregorian_month", "gregorian_day",
        "hijri_year", "hijri_month", "hijri_day",
        "jdn", "day_of_week_index", "day_of_week_en", "day_of_week_ar"
    ]
    
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(vectors)
    
    print(f"Written: {output_file}")
    print(f"Total vectors: {len(vectors)}")
    
    # Print some statistics
    jdns = [v["jdn"] for v in vectors]
    print(f"JDN range: {min(jdns)} - {max(jdns)}")
    print(f"Gregorian range: {vectors[0]['gregorian_year']} - {vectors[-1]['gregorian_year']}")
    print(f"Hijri range: {vectors[0]['hijri_year']} - {vectors[-1]['hijri_year']}")

if __name__ == "__main__":
    main()
