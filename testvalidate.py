#!/usr/bin/env python3
"""
explore_profiles_nopandas.py
----------------------------
Lightweight validation for patient_profiles.csv
No external packages (no pandas/matplotlib) required.

Run:
    python3 explore_profiles_nopandas.py
"""

import csv
import statistics
from collections import Counter, defaultdict
from pathlib import Path

# ---------- Load the CSV ----------
CSV_PATH = Path("patient_profiles.csv")
if not CSV_PATH.exists():
    CSV_PATH = Path("/Users/safeenahaljunid/derm-benchmark/gold_profiles/patient_profiles.csv")

if not CSV_PATH.exists():
    raise FileNotFoundError("❌ Could not find patient_profiles.csv")

print(f"[OK] Reading {CSV_PATH}")
rows = []
with CSV_PATH.open("r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for r in reader:
        rows.append(r)

print(f"Loaded {len(rows)} profiles")

# ---------- Check for missing data ----------
missing_counts = defaultdict(int)
for r in rows:
    for k, v in r.items():
        if not str(v).strip():
            missing_counts[k] += 1

print("\n--- Missing Values ---")
for k, v in missing_counts.items():
    print(f"{k}: {v}")
if not missing_counts:
    print("✅ No missing values detected")

# ---------- Numeric stats (age) ----------
ages = [int(r["age"]) for r in rows if str(r.get("age", "")).isdigit()]
print("\n--- Age Stats ---")
if ages:
    print(f"Count: {len(ages)}")
    print(f"Min: {min(ages)}")
    print(f"Max: {max(ages)}")
    print(f"Mean: {statistics.mean(ages):.1f}")
    print(f"Median: {statistics.median(ages)}")
else:
    print("⚠️ No valid ages found")

# ---------- Simple categorical summaries ----------
def count_column(col):
    vals = [r[col] for r in rows if r.get(col)]
    return Counter(vals)

for col in ["sex", "pregnancy_status", "skin_type", "primary_concern"]:
    print(f"\n--- {col.upper()} ---")
    for k, v in count_column(col).items():
        print(f"{k}: {v}")

# ---------- Cross-tab (primary_concern × sex) ----------
print("\n--- Crosstab: Primary Concern × Sex ---")
crosstab = defaultdict(lambda: Counter())
for r in rows:
    crosstab[r["primary_concern"]][r["sex"]] += 1

for concern, sex_counts in crosstab.items():
    print(f"{concern:25s}", dict(sex_counts))

# ---------- Validation summary ----------
issues = []
if len(rows) != 25:
    issues.append(f"Expected 25 profiles, found {len(rows)}")

concerns = {r["primary_concern"] for r in rows}
if len(concerns) < 10:
    issues.append(f"Only {len(concerns)} unique primary_concern values (expected 10)")

if any(int(r["age"]) > 120 or int(r["age"]) < 0 for r in rows if r["age"].isdigit()):
    issues.append("Age out of valid range")

if not issues:
    print("\n✅ Dataset passes basic validation checks.")
else:
    print("\n⚠️ Validation issues found:")
    for i, msg in enumerate(issues, start=1):
        print(f"{i}. {msg}")

print("\nDone.")



