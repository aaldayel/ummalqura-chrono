#!/usr/bin/env python3
"""
Cross-Language Parity Test Runner

This script runs the golden-value test suite against all language wrappers
to ensure they produce identical results.

Usage:
    python run_parity_tests.py [--verbose]
"""

import csv
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Any

# Project root
ROOT = Path(__file__).parent.parent.parent
GOLDEN_VALUES_PATH = ROOT / "tests" / "golden" / "golden-values.csv"

def load_golden_values(sample_size: int = 1000) -> List[Dict[str, Any]]:
    """Load golden values from CSV"""
    values = []
    with open(GOLDEN_VALUES_PATH, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= sample_size:
                break
            values.append({
                'gregorian_year': int(row['gregorian_year']),
                'gregorian_month': int(row['gregorian_month']),
                'gregorian_day': int(row['gregorian_day']),
                'hijri_year': int(row['hijri_year']),
                'hijri_month': int(row['hijri_month']),
                'hijri_day': int(row['hijri_day']),
                'jdn': int(row['jdn']),
                'day_of_week_index': int(row['day_of_week_index']),
            })
    return values

def test_javascript(values: List[Dict], verbose: bool = False) -> Dict[str, Any]:
    """Test JavaScript wrapper"""
    js_dir = ROOT / "packages" / "js"
    
    # Create test script
    test_script = """
const { UmmAlQuraCalendar } = require('./dist/index');
const calendar = new UmmAlQuraCalendar();

const values = VALUES_PLACEHOLDER;
const results = [];

for (const v of values) {
    try {
        const gToH = calendar.gregorianToHijri(v.gregorian_year, v.gregorian_month, v.gregorian_day);
        const hToG = calendar.hijriToGregorian(v.hijri_year, v.hijri_month, v.hijri_day);
        
        results.push({
            gregorian_year: v.gregorian_year,
            gregorian_month: v.gregorian_month,
            gregorian_day: v.gregorian_day,
            hijri_year: v.hijri_year,
            hijri_month: v.hijri_month,
            hijri_day: v.hijri_day,
            jdn: v.jdn,
            g2h_year: gToH.output.year,
            g2h_month: gToH.output.month,
            g2h_day: gToH.output.day,
            h2g_year: hToG.output.year,
            h2g_month: hToG.output.month,
            h2g_day: hToG.output.day,
        });
    } catch (e) {
        results.push({ error: e.message, ...v });
    }
}

console.log(JSON.stringify(results));
"""
    
    test_script = test_script.replace('VALUES_PLACEHOLDER', json.dumps(values))
    test_file = js_dir / "_parity_test.js"
    test_file.write_text(test_script)
    
    try:
        result = subprocess.run(
            ["node", str(test_file)],
            capture_output=True,
            text=True,
            cwd=str(js_dir)
        )
        
        if result.returncode != 0:
            return {"success": False, "error": result.stderr}
        
        return {"success": True, "results": json.loads(result.stdout)}
    finally:
        test_file.unlink(missing_ok=True)

def test_python(values: List[Dict], verbose: bool = False) -> Dict[str, Any]:
    """Test Python wrapper"""
    try:
        sys.path.insert(0, str(ROOT / "packages" / "python"))
        from ummalqura import UmmAlQuraCalendar
        
        calendar = UmmAlQuraCalendar()
        results = []
        
        for v in values:
            try:
                g2h = calendar.gregorian_to_hijri(v['gregorian_year'], v['gregorian_month'], v['gregorian_day'])
                h2g = calendar.hijri_to_gregorian(v['hijri_year'], v['hijri_month'], v['hijri_day'])
                
                results.append({
                    'gregorian_year': v['gregorian_year'],
                    'gregorian_month': v['gregorian_month'],
                    'gregorian_day': v['gregorian_day'],
                    'hijri_year': v['hijri_year'],
                    'hijri_month': v['hijri_month'],
                    'hijri_day': v['hijri_day'],
                    'jdn': v['jdn'],
                    'g2h_year': g2h.output.year,
                    'g2h_month': g2h.output.month,
                    'g2h_day': g2h.output.day,
                    'h2g_year': h2g.output.year,
                    'h2g_month': h2g.output.month,
                    'h2g_day': h2g.output.day,
                })
            except Exception as e:
                results.append({'error': str(e), **v})
        
        return {"success": True, "results": results}
    except Exception as e:
        return {"success": False, "error": str(e)}

def compare_results(js_results: List[Dict], py_results: List[Dict]) -> Dict[str, Any]:
    """Compare results from different language implementations"""
    mismatches = []
    
    for i, (js, py) in enumerate(zip(js_results, py_results)):
        if 'error' in js or 'error' in py:
            if js.get('error') != py.get('error'):
                mismatches.append({
                    'index': i,
                    'type': 'error_mismatch',
                    'javascript': js,
                    'python': py
                })
            continue
        
        for key in ['g2h_year', 'g2h_month', 'g2h_day', 'h2g_year', 'h2g_month', 'h2g_day']:
            if js.get(key) != py.get(key):
                mismatches.append({
                    'index': i,
                    'type': 'value_mismatch',
                    'field': key,
                    'javascript': js.get(key),
                    'python': py.get(key),
                    'input': {
                        'gregorian': f"{js['gregorian_year']}-{js['gregorian_month']:02d}-{js['gregorian_day']:02d}",
                        'hijri': f"{js['hijri_year']}-{js['hijri_month']:02d}-{js['hijri_day']:02d}",
                    }
                })
    
    return {
        'total': len(js_results),
        'mismatches': len(mismatches),
        'match_rate': (len(js_results) - len(mismatches)) / len(js_results) * 100 if js_results else 0,
        'details': mismatches[:10]  # First 10 mismatches
    }

def main():
    verbose = '--verbose' in sys.argv
    
    print("=" * 60)
    print("Cross-Language Parity Test Runner")
    print("=" * 60)
    
    # Load golden values
    print("\nLoading golden values...")
    values = load_golden_values(sample_size=1000)
    print(f"Loaded {len(values)} test vectors")
    
    # Test JavaScript
    print("\n[1/2] Testing JavaScript wrapper...")
    js_result = test_javascript(values, verbose)
    if js_result['success']:
        print(f"  ✓ JavaScript: {len(js_result['results'])} tests completed")
    else:
        print(f"  ✗ JavaScript failed: {js_result['error']}")
    
    # Test Python
    print("\n[2/2] Testing Python wrapper...")
    py_result = test_python(values, verbose)
    if py_result['success']:
        print(f"  ✓ Python: {len(py_result['results'])} tests completed")
    else:
        print(f"  ✗ Python failed: {py_result['error']}")
    
    # Compare results
    if js_result['success'] and py_result['success']:
        print("\nComparing results...")
        comparison = compare_results(js_result['results'], py_result['results'])
        
        print(f"\nResults:")
        print(f"  Total tests: {comparison['total']}")
        print(f"  Mismatches: {comparison['mismatches']}")
        print(f"  Match rate: {comparison['match_rate']:.2f}%")
        
        if comparison['mismatches'] > 0:
            print("\nFirst mismatches:")
            for m in comparison['details'][:5]:
                print(f"  - {m}")
            return 1
        else:
            print("\n✓ All tests passed! JavaScript and Python produce identical results.")
            return 0
    else:
        print("\n✗ Cannot compare results due to implementation failures")
        return 1

if __name__ == '__main__':
    sys.exit(main())
