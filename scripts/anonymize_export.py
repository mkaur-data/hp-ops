#!/usr/bin/env python3
"""Anonymize exported session data for public sharing.

Replaces:
  - Source IPs → hashed pseudonyms (SHA256 prefix, deterministic within run)
  - Internal hostnames → generic labels
  - Sensor IPs → removed
  - Timestamps → shifted by random offset (preserves relative ordering)

Usage:
    python3 anonymize_export.py --input exports/weekly.ndjson.gz --output exports/anon-weekly.ndjson.gz

sarah, 2026-01-08: initial
sarah, 2026-02-20: added timestamp shifting (reviewer feedback from blog draft)
"""

import argparse
import gzip
import hashlib
import json
import random
import sys
from datetime import datetime, timedelta


# Deterministic per-run salt (changes each invocation for different pseudonyms)
SALT = hashlib.sha256(str(random.getrandbits(256)).encode()).hexdigest()[:16]

# Internal references to strip
INTERNAL_PATTERNS = [
    "ops.internal",
    "10.8.",
    "sensor-us-01",
    "sensor-eu-01",
    "sensor-apac-01",
    "ingest-elk-01",
    "backup-nfs",
]


def pseudonymize_ip(ip: str) -> str:
    """Replace IP with deterministic pseudonym."""
    h = hashlib.sha256(f"{SALT}:{ip}".encode()).hexdigest()[:12]
    return f"anon-{h}"


def shift_timestamp(ts_str: str, offset: timedelta) -> str:
    """Shift ISO timestamp by offset."""
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        shifted = dt + offset
        return shifted.isoformat()
    except (ValueError, AttributeError):
        return ts_str


def clean_value(val: str) -> str:
    """Remove internal references from string values."""
    if not isinstance(val, str):
        return val
    for pattern in INTERNAL_PATTERNS:
        if pattern in val:
            return "[REDACTED]"
    return val


def anonymize_record(record: dict, ts_offset: timedelta) -> dict:
    """Anonymize a single session record."""
    out = {}
    for key, val in record.items():
        if key in ("src_ip", "source_ip", "attacker_ip", "peer_ip"):
            out[key] = pseudonymize_ip(str(val))
        elif key in ("dst_ip", "dest_ip", "sensor_ip", "host_ip"):
            out[key] = "[SENSOR]"
        elif "timestamp" in key or key in ("@timestamp", "starttime", "endtime"):
            out[key] = shift_timestamp(str(val), ts_offset)
        else:
            out[key] = clean_value(val)
    return out


def main():
    parser = argparse.ArgumentParser(description="Anonymize session exports")
    parser.add_argument("--input", required=True, help="Input NDJSON or .ndjson.gz")
    parser.add_argument("--output", required=True, help="Output path")
    args = parser.parse_args()

    # Random time offset: 1-14 days backward
    ts_offset = timedelta(days=-random.randint(1, 14), hours=-random.randint(0, 23))

    open_in = gzip.open if args.input.endswith(".gz") else open
    open_out = gzip.open if args.output.endswith(".gz") else open

    count = 0
    try:
        with open_in(args.input, "rt") as fin, open_out(args.output, "wt") as fout:
            for line in fin:
                line = line.strip()
                if not line:
                    continue
                record = json.loads(line)
                anon = anonymize_record(record, ts_offset)
                fout.write(json.dumps(anon) + "\n")
                count += 1
    except FileNotFoundError:
        print(f"ERROR: Input file not found: {args.input}", file=sys.stderr)
        sys.exit(1)

    print(f"Anonymized {count} records → {args.output}")
    print(f"Salt: {SALT} (save this if you need to correlate pseudonyms later)")


if __name__ == "__main__":
    main()
