#!/usr/bin/env python3
"""Apply corrected URLs from review-state.csv to redirects.map."""

import csv
import re
import sys

CSV_FILE = "review-state.csv"
MAP_FILE = "../docs/website/provisioning/nginx/redirects.map"

# 1. Parse corrections from review CSV
corrections = {}  # canonical "from" path -> corrected URL
with open(CSV_FILE) as f:
    reader = csv.reader(f)
    next(reader)  # skip header
    for row in reader:
        if len(row) >= 5 and row[3] == "flagged" and row[4].strip():
            canonical = row[1].rstrip("/") or "/"
            corrections[canonical] = row[4].strip()

print(f"Loaded {len(corrections)} corrections from {CSV_FILE}")

# 2. Read and update redirects.map
with open(MAP_FILE) as f:
    lines = f.readlines()

updated = []
changed = 0
for line in lines:
    stripped = line.strip()
    if not stripped or stripped.startswith("#"):
        updated.append(line)
        continue

    match = re.match(r"^(\S+)\s+(\S+?);?\s*$", stripped)
    if not match:
        updated.append(line)
        continue

    from_path = match.group(1)
    old_to = match.group(2).rstrip(";")
    canonical = from_path.rstrip("/") or "/"

    if canonical in corrections:
        new_to = corrections[canonical]
        updated.append(f"{from_path} {new_to};\n")
        if old_to != new_to:
            changed += 1
    else:
        updated.append(line)

# 3. Write updated file
with open(MAP_FILE, "w") as f:
    f.writelines(updated)

print(f"Updated {changed} lines in {MAP_FILE}")
print(f"Expected ~{len(corrections) * 2} (453 × 2 slash variants)")
