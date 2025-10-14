"""
Gold Profile Dataset Builder (beginner-friendly)
-----------------------------------------------
Run with:  python build_gold_profiles.py

What it does:
1) Creates a folder called `gold_profiles/`
2) Saves:
   - gold_profile_template.csv  (blank template)
   - gold_profile_examples.csv  (3 example rows)
   - gold_profiles.jsonl        (JSON Lines with the same 3 examples)
3) Lets you easily add more profiles by editing the CSV.
   Later, you can convert CSV -> JSONL by re-running this script.

No extra installs needed. Uses only Python's standard library.
"""

from pathlib import Path
import csv, json

# ---------- 1) Configuration you can edit ----------

OUT_DIR = Path("gold_profiles")
TEMPLATE_CSV = OUT_DIR / "gold_profile_template.csv"
EXAMPLES_CSV = OUT_DIR / "gold_profile_examples.csv"
JSONL_PATH   = OUT_DIR / "gold_profiles.jsonl"

# Allowed values to keep things tidy
ALLOWED_SKIN_TYPES = {"Dry", "Oily", "Combination", "Sensitive", "Normal"}
ALLOWED_CONCERNS = {
    "Acne","Eczema","Psoriasis","Melasma","Dermatitis","Rosacea",
    "Hyperpigmentation","Sun Damage","Dandruff","Seborrheic Dermatitis"
}

# Column schema (simple and flat for beginners)
COLUMNS = [
    "id","name","age","sex","pregnancy_status","region",
    "skin_type","primary_concern","secondary_concern",
    "allergies","drug_sensitivities","past_treatments","adverse_reactions",
    "routine","environment","habits"
]

# ---------- 2) Minimal examples to get you started ----------

EXAMPLES = [
    {
        "id": 1, "name": "Alex Kim", "age": 16, "sex": "Male", "pregnancy_status": "N/A",
        "region": "Northeast USA", "skin_type": "Oily",
        "primary_concern": "Acne", "secondary_concern": "Hyperpigmentation",
        "allergies": "None", "drug_sensitivities": "Retinoids cause dryness",
        "past_treatments": "Benzoyl peroxide 2.5% wash", "adverse_reactions": "Mild irritation week 1",
        "routine": "Sunscreen sometimes; uses gym often", "environment": "Humid summers",
        "habits": "Touches face during sports"
    },
    {
        "id": 2, "name": "Maya Lopez", "age": 14, "sex": "Female", "pregnancy_status": "Not Pregnant",
        "region": "Southwest USA", "skin_type": "Sensitive",
        "primary_concern": "Eczema", "secondary_concern": "Post-inflammatory redness",
        "allergies": "Fragrance mix", "drug_sensitivities": "AHAs sting",
        "past_treatments": "Hydrocortisone 1% short courses", "adverse_reactions": "None reported",
        "routine": "Moisturizes nightly", "environment": "Dry climate",
        "habits": "Long hot showers"
    },
    {
        "id": 3, "name": "Jordan Singh", "age": 18, "sex": "Male", "pregnancy_status": "N/A",
        "region": "Midwest USA", "skin_type": "Combination",
        "primary_concern": "Melasma", "secondary_concern": "Uneven tone",
        "allergies": "None", "drug_sensitivities": "None",
        "past_treatments": "Sunscreen daily (inconsistent)", "adverse_reactions": "None",
        "routine": "Forgets sunscreen on cloudy days", "environment": "High UV in summer",
        "habits": "Outdoor sports"
    }
]

# ---------- 3) Helpers ----------

def ensure_outdir():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

def write_template_csv():
    with TEMPLATE_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS)
        writer.writeheader()
    print(f"[OK] Template: {TEMPLATE_CSV}")

def write_examples_csv():
    # Create the CSV if missing; if present, ensure it has a header, but do not overwrite data.
    if not EXAMPLES_CSV.exists():
        with EXAMPLES_CSV.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            for row in EXAMPLES:
                writer.writerow(row)
        print(f"[OK] Examples created: {EXAMPLES_CSV}")
        return
    # If file exists but is empty / missing header, add header only.
    with EXAMPLES_CSV.open("r+", newline="", encoding="utf-8") as f:
        first_line = f.readline()
        if not first_line or "id,name,age" not in first_line.replace(" ", ""):
            f.seek(0)
            contents = f.read()
            f.seek(0)
            writer = csv.DictWriter(f, fieldnames=COLUMNS)
            writer.writeheader()
            f.write(contents)
            print(f"[OK] Header ensured on existing CSV: {EXAMPLES_CSV}")
        else:
            print(f"[OK] Examples already exist, not overwriting: {EXAMPLES_CSV}")

def validate_row(row, row_num):
    # Basic checks to help you avoid mistakes
    problems = []
    # Required minimal fields
    for key in ["id","name","age","sex","region","skin_type","primary_concern"]:
        if str(row.get(key, "")).strip() == "":
            problems.append(f"Missing required field '{key}'")

    # Simple type checks
    try:
        int(row.get("id", ""))
    except Exception:
        problems.append("id must be an integer")

    try:
        age = int(row.get("age", ""))
        if not (0 <= age <= 120):
            problems.append("age must be between 0 and 120")
    except Exception:
        problems.append("age must be an integer")

    # Allowed values sanity checks
    st = str(row.get("skin_type","")).strip()
    if st and st not in ALLOWED_SKIN_TYPES:
        problems.append(f"skin_type must be one of {sorted(ALLOWED_SKIN_TYPES)}")

    pc = str(row.get("primary_concern","")).strip()
    if pc and pc not in ALLOWED_CONCERNS:
        problems.append(f"primary_concern should be one of {sorted(ALLOWED_CONCERNS)}")

    return problems

def csv_to_jsonl(csv_path, jsonl_path):
    total = 0
    with csv_path.open("r", newline="", encoding="utf-8") as f_in, \
         jsonl_path.open("w", encoding="utf-8") as f_out:
        reader = csv.DictReader(f_in)
        for i, row in enumerate(reader, start=1):  # Auto-increment ID starting at 1
            # Override the ID with auto-generated sequential number
            row["id"] = str(i)
            
            problems = validate_row(row, i+1)  # i+1 for row number (accounting for header)
            if problems:
                print(f"[WARN] Row {i+1}: " + " | ".join(problems))
            
            # Convert flat CSV row to the nested JSON shape
            obj = {
                "id": i,  # Use auto-generated ID
                "personal_info": {
                    "name": row["name"],
                    "age": int(row["age"]),
                    "sex": row["sex"],
                    "pregnancy_status": row.get("pregnancy_status",""),
                    "region": row["region"]
                },
                "skin_status": {
                    "skin_type": row["skin_type"],
                    "primary_concern": row["primary_concern"],
                    "secondary_concern": row.get("secondary_concern","")
                },
                "safety": {
                    "allergies": [s.strip() for s in row.get("allergies","").split(",") if s.strip()],
                    "drug_sensitivities": [s.strip() for s in row.get("drug_sensitivities","").split(",") if s.strip()]
                },
                "medical_history": {
                    "past_treatments": [s.strip() for s in row.get("past_treatments","").split(",") if s.strip()],
                    "adverse_reactions": [s.strip() for s in row.get("adverse_reactions","").split(",") if s.strip()]
                },
                "lifestyle_preferences": {
                    "routine": row.get("routine",""),
                    "environment": row.get("environment",""),
                    "habits": row.get("habits","")
                }
            }
            f_out.write(json.dumps(obj, ensure_ascii=False) + "\n")
            total += 1
    print(f"[OK] Wrote {total} JSONL item(s) -> {jsonl_path}")
    
def main():
    ensure_outdir()
    write_template_csv()
    write_examples_csv()
    # Convert the examples CSV to JSONL so you can see both formats
    csv_to_jsonl(EXAMPLES_CSV, JSONL_PATH)
    print("\nNext steps:")
    print("1) Open gold_profile_examples.csv")
    print("2) Duplicate a row and change values to make your own patient")
    print("3) Save the CSV, then re-run:  python build_gold_profiles.py")
    print("   -> It will regenerate gold_profiles.jsonl for you.")

if __name__ == "__main__":
    main()
