#!/usr/bin/env python3
"""
Validate locale files against the expected schema.

Usage:
    python scripts/validate_locales.py
"""

import json
import sys
from pathlib import Path
from typing import List, Dict


REQUIRED_FIELDS = [
    "code", "name", "gregorian_months", "gregorian_months_short",
    "hijri_months", "hijri_months_short", "days", "days_short",
    "days_min", "meridiem", "rtl"
]

ARRAY_FIELDS_12 = [
    "gregorian_months", "gregorian_months_short",
    "hijri_months", "hijri_months_short"
]

ARRAY_FIELDS_7 = ["days", "days_short", "days_min"]


def validate_locale(filepath: Path) -> List[str]:
    errors = []

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return [f"{filepath.name}: Invalid JSON: {e}"]
    except Exception as e:
        return [f"{filepath.name}: Error reading file: {e}"]

    # Check required fields
    for field in REQUIRED_FIELDS:
        if field not in data:
            errors.append(f"{filepath.name}: Missing required field '{field}'")

    # Check array lengths
    for field in ARRAY_FIELDS_12:
        if field in data and len(data[field]) != 12:
            errors.append(f"{filepath.name}: '{field}' must have 12 items, got {len(data[field])}")

    for field in ARRAY_FIELDS_7:
        if field in data and len(data[field]) != 7:
            errors.append(f"{filepath.name}: '{field}' must have 7 items, got {len(data[field])}")

    # Check code is a valid string
    if "code" in data:
        if not isinstance(data["code"], str) or not data["code"]:
            errors.append(f"{filepath.name}: 'code' must be a non-empty string")

    # Check rtl is boolean
    if "rtl" in data:
        if not isinstance(data["rtl"], bool):
            errors.append(f"{filepath.name}: 'rtl' must be a boolean")

    # Check meridiem structure
    if "meridiem" in data:
        m = data["meridiem"]
        if not isinstance(m, dict) or "am" not in m or "pm" not in m:
            errors.append(f"{filepath.name}: 'meridiem' must be an object with 'am' and 'pm'")

    return errors


def main():
    locales_dir = Path(__file__).parent.parent / "data" / "locales"
    if not locales_dir.is_dir():
        print(f"Error: Locales directory not found at {locales_dir}")
        sys.exit(1)

    locale_files = sorted(locales_dir.glob("*.json"))
    if not locale_files:
        print("Error: No locale files found")
        sys.exit(1)

    print(f"Validating {len(locale_files)} locale files...\n")

    total_errors = 0
    for filepath in locale_files:
        errors = validate_locale(filepath)
        if errors:
            for err in errors:
                print(f"  ERROR: {err}")
            total_errors += len(errors)
        else:
            print(f"  OK: {filepath.name}")

    print(f"\n{'=' * 50}")
    if total_errors == 0:
        print(f"All {len(locale_files)} locale files are valid.")
        sys.exit(0)
    else:
        print(f"{total_errors} error(s) found in {len(locale_files)} file(s).")
        sys.exit(1)


if __name__ == "__main__":
    main()
