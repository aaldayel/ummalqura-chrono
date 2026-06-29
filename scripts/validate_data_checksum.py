#!/usr/bin/env python3
"""Validate ummalqura-months.json embedded checksum and on-disk SHA-256 file."""

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
DATA_FILE = ROOT / "data" / "ummalqura-months.json"
CHECKSUM_FILE = ROOT / "data" / "ummalqura-months.sha256"


def compute_payload_checksum(data: dict) -> str:
    payload = {key: value for key, value in data.items() if key != "checksum"}
    encoded = json.dumps(payload, separators=(",", ":"), sort_keys=True).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def main() -> int:
    if not DATA_FILE.exists():
        print(f"Missing data file: {DATA_FILE}", file=sys.stderr)
        return 1

    data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    embedded = data.get("checksum")
    if not embedded:
        print("Missing checksum field in data file", file=sys.stderr)
        return 1

    expected = compute_payload_checksum(data)
    if embedded != expected:
        print(
            f"Embedded checksum mismatch: file={embedded} expected={expected}",
            file=sys.stderr,
        )
        return 1

    file_digest = hashlib.sha256(DATA_FILE.read_bytes()).hexdigest()
    if CHECKSUM_FILE.exists():
        recorded = CHECKSUM_FILE.read_text(encoding="utf-8").strip().split()[0]
        if recorded != file_digest:
            print(
                f"SHA-256 file mismatch: recorded={recorded} file={file_digest}",
                file=sys.stderr,
            )
            return 1

    print("Data checksum validation passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
