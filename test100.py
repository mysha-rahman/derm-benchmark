#!/usr/bin/env python3
"""
build_patient_profiles_100.py
-----------------------------
Generate 100 diverse patient profiles (10 per concern) and pick
'past_treatments' from ingredients listed in ingredientsList.csv.

Inputs (auto-discovered):
  - ./ingredientsList.csv    OR    ./data/ingredientsList.csv

Outputs (in gold_profiles/):
  - patient_profiles_100.csv
  - patient_profiles_100.jsonl
  - patient_profiles_100.xlsx  (optional, if pandas + xlsxwriter installed)
  - source_mapping_100.json    (which columns influenced suitability)

Run:
  python3 tools/build_patient_profiles_100.py
"""

from __future__ import annotations
import csv, json, random, re, sys
from collections import Counter
from pathlib import Path

# ---------------- Paths ----------------
INGREDIENT_FILE = Path("/Users/safeenahaljunid/derm-benchmark/gold_profiles/ingredientsList.csv")
ALT_PATH = Path("data/ingredientsList.csv")

OUT_DIR = Path("gold_profiles")
CSV_OUT = OUT_DIR / "patient_profiles_100.csv"
JSONL_OUT = OUT_DIR / "patient_profiles_100.jsonl"
XLSX_OUT = OUT_DIR / "patient_profiles_100.xlsx"
MAP_OUT = OUT_DIR / "source_mapping_100.json"

# ---------------- Schema / knobs ----------------
ALLOWED_CONCERNS = [
    "Acne","Eczema","Psoriasis","Melasma","Dermatitis","Rosacea",
    "Hyperpigmentation","Sun Damage","Dandruff","Seborrheic Dermatitis"
]
ALLOWED_SKIN_TYPES = {"Dry", "Oily", "Combination", "Sensitive", "Normal"}

# 10 profiles per concern = 100 total
TARGET_PER_CONCERN = 10

COLUMNS = [
    "id","name","age","sex","pregnancy_status","region",
    "skin_type","primary_concern","secondary_concern",
    "allergies","drug_sensitivities","past_treatments","adverse_reactions",
    "routine","environment","habits"
]

# Heuristic synonym maps (to interpret free-text columns in ingredients CSV)
SYN = {
    "sun damage": ["uv","uva","uvb","photoaging","sunscreen","spf","photoprotection"],
    "hyperpigmentation": ["pigment","melanin","dark spot","brighten","tone","tyrosinase","tranexamic","kojic","azelaic"],
    "dermatitis": ["irritation","barrier","anti-inflammatory","soothing","ceramide","calming","oat"],
    "dandruff": ["scalp","antifungal","flakes","malassezia","ketoconazole","zinc pyrithione"],
    "seborrheic dermatitis": ["scalp","antifungal","malassezia","sebum","ketoconazole"],
    "acne": ["comed","sebum","pore","antibacterial","benzoyl","salicylic","azelaic","retinoid"],
    "rosacea": ["redness","flush","soothing","anti-inflammatory","ivermectin","metronidazole"],
    "eczema": ["barrier","emollient","itch","ceramide","oat","urea","petrolatum"],
    "psoriasis": ["kerato","scaling","plaques","coal tar","vitamin d analog","calcipot","calcipotriene"],
    "melasma": ["pigment","brighten","azelaic","tranexamic","tyrosinase","hq","kojic"]
}
SKIN_SYNS = {
    "oily": ["oil-control","sebum","non-comed","lightweight"],
    "dry": ["emollient","occlusive","humectant","ceramide","urea","glycerin","shea"],
    "sensitive": ["fragrance-free","soothing","gentle","calming","low-irritant"],
    "combination": ["lightweight","balance","balanc"],
    "normal": []
}
PREG_AVOID = ["avoid in pregnancy","not in pregnancy","retinoid","tretinoin",
              "adapalene","isotretinoin","hydroquinone","high-dose salicylic"]

# Demographic pools
FIRST = ["Alex","Maya","Jordan","Sofia","Declan","Amara","Liam","Neha","Mateo","Hana","Ethan","Beatriz",
         "Thomas","Aisha","Noah","Chinwe","Carlos","Jisoo","Elena","Abdul","Riley","George","Zara",
         "Miguel","Lucía","Rahim","Farah","Ken","Yuki","Sara","Omar","Nora","Adam","Halim","Mysha","Hanim"]
LAST  = ["Kim","Lopez","Singh","Petrova","ONeill","Okoye","Thompson","Sharma","Garcia","Yamada","Brown",
         "Silva","Muller","Khan","Johnson","Nwankwo","Mendoza","Park","Rossi","Rahman","Carter","Williams",
         "Ahmad","Santos","Fernandez","Tan","Lim","Wong","Aziz","Gonzalez","Martinez","Chen","Lee","Kowalski",
         "Hassan","Ibrahim"]
REGIONS = ["Northeast USA","Southwest USA","Midwest USA","Southeast USA","Pacific Northwest USA",
           "Canada","UK","Ireland","Germany","Italy","Spain","Brazil","Argentina","Mexico",
           "Nigeria","Ghana","South Africa","Egypt","Middle East","Pakistan","India","Malaysia",
           "Japan","South Korea","Philippines","Australia","New Zealand"]
SEXES = ["Male","Female"]
SKIN_TYPES = list(ALLOWED_SKIN_TYPES)
AGES = [7,10,14,15,16,18,21,22,24,26,27,29,31,32,33,35,38,40,45,52,55,58,64,67,73]

# ---------------- Utilities ----------------
def set_seed(seed=7):
    random.seed(seed)

def find_ingredient_file() -> Path:
    if INGREDIENT_FILE.exists(): return INGREDIENT_FILE
    if ALT_PATH.exists(): return ALT_PATH
    print("[ERR] Could not find 'ingredientsList.csv' (root or ./data/).", file=sys.stderr)
    sys.exit(1)

def read_csv_rows(path: Path):
    with path.open("r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        cols = [c.strip().lower().replace(" ","_") for c in (reader.fieldnames or [])]
        rows = []
        for r in reader:
            nr = {}
            for k,v in r.items():
                nr[k.strip().lower().replace(" ","_")] = (v or "")
            rows.append(nr)
        return rows, cols

def find_cols(cols, keywords):
    out = []
    for c in cols:
        if any(k in c for k in keywords):
            out.append(c)
    return out

def row_text(row: dict) -> str:
    return " ".join(str(v) for v in row.values()).lower()

def has_positive_concern(row:dict, concern:str, condition_cols:list[str]) -> bool:
    c = concern.lower()
    for col in condition_cols:
        s = str(row.get(col,"")).lower()
        if c in s and not any(b in s for b in ["avoid","contraindicated","worsen","not for"]):
            return True
        for kw in SYN.get(c, []):
            if kw in s and not any(b in s for b in ["avoid","worsen","irritat","contraindicated"]):
                return True
    full = row_text(row)
    if c in full and "avoid" not in full:
        return True
    for kw in SYN.get(c, []):
        if kw in full and "avoid" not in full:
            return True
    return False

def matches_skin(row:dict, skin_type:str, skin_cols:list[str]) -> bool:
    t = skin_type.lower()
    for col in skin_cols:
        s = str(row.get(col,"")).lower()
        if t in s and not any(b in s for b in ["avoid","worsen","irritat","not for"]):
            return True
    full = row_text(row)
    if any(kw in full for kw in SKIN_SYNS.get(t, [])):
        return True
    return t == "normal"

def pregnancy_ok(row:dict, pregnant:bool, preg_cols:list[str]) -> bool:
    if not pregnant: return True
    full = row_text(row)
    if any(t in full for t in PREG_AVOID):
        return False
    for col in preg_cols:
        s = str(row.get(col,"")).lower()
        if any(w in s for w in ["safe","ok","yes"]) and not any(b in s for b in ["avoid","not"]):
            return True
    return True

def ingredients_from_rows(rows):
    sample = rows[0] if rows else {}
    cand = [c for c in sample.keys() if re.search(r"(ingredient|name|product|item|title)", c, re.I)]
    name_col = cand[0] if cand else (list(sample.keys())[0] if sample else "name")
    items = []
    for r in rows:
        nm = str(r.get(name_col,"")).strip()
        if nm:
            items.append({"name": nm, "row": r})
    return name_col, items

def choose_ing(items, concern, skin_type, pregnant, condition_cols, skin_cols, preg_cols, k=2):
    pool = [it["name"] for it in items
            if has_positive_concern(it["row"], concern, condition_cols)
            and matches_skin(it["row"], skin_type, skin_cols)
            and pregnancy_ok(it["row"], pregnant, preg_cols)]
    if len(pool) < k:
        pool = list(set(pool) | {
            it["name"] for it in items
            if has_positive_concern(it["row"], concern, condition_cols)
            and pregnancy_ok(it["row"], pregnant, preg_cols)
        })
    if len(pool) < k:
        pool = [it["name"] for it in items if pregnancy_ok(it["row"], pregnant, preg_cols)]
    if not pool:
        pool = [it["name"] for it in items]
    pool = list(dict.fromkeys(pool))
    random.shuffle(pool)
    return pool[:k]

def make_name():
    return f"{random.choice(FIRST)} {random.choice(LAST)}"

# ---------------- Build 100 profiles ----------------
def build_profiles_100(seed=7):
    set_seed(seed)
    ing_path = find_ingredient_file()
    rows, cols = read_csv_rows(ing_path)
    name_col, items = ingredients_from_rows(rows)

    condition_cols = find_cols(cols, ["acne","eczema","psoriasis","melasma","dermatitis","rosacea","hyperpig","sun","dandruff","seborr"])
    skin_cols = find_cols(cols, ["skin_type","skin type","dry","oily","sensitive","normal","combination"])
    preg_cols = find_cols(cols, ["pregnan","pregnancy","avoid","contra","warning"])

    # Build a plan: 10 entries for each concern
    plan = []
    for concern in ALLOWED_CONCERNS:
        plan.extend([concern] * TARGET_PER_CONCERN)
    random.shuffle(plan)

    profiles = []
    for i, concern in enumerate(plan, start=1):
        sex = random.choice(SEXES)
        preg = random.choices(["Pregnant","Not Pregnant"], weights=[1,5])[0] if sex=="Female" else "N/A"
        skin = random.choice(SKIN_TYPES)
        ings = choose_ing(items, concern, skin, preg=="Pregnant", condition_cols, skin_cols, preg_cols, k=2)
        profiles.append({
            "id": i, "name": make_name(), "age": random.choice(AGES),
            "sex": sex, "pregnancy_status": preg, "region": random.choice(REGIONS),
            "skin_type": skin, "primary_concern": concern,
            "secondary_concern": random.choice([c for c in ALLOWED_CONCERNS if c != concern]),
            "allergies": random.choice(["None","Fragrance mix","Lanolin","Nickel","Dust mites","Latex","Pollen","None"]),
            "drug_sensitivities": random.choice(["None","Retinoids cause dryness","AHAs sting","Alcohol-based toners sting","Propylene glycol stings","None"]),
            "past_treatments": ", ".join(ings),
            "adverse_reactions": random.choice(["None","Mild irritation week 1","Transient dryness","Peeling when overused","Dryness after use","None"]),
            "routine": random.choice([
                "Gentle cleanser + daily SPF","Double cleanse at night","Barrier-repair moisturizer focus",
                "Mineral sunscreen; avoid triggers","Moisturizer after bath","SPF reapplication mid-day"
            ]),
            "environment": random.choice(["Humid summers","Dry climate","High UV in summer","Cold winters","Urban pollution","Arid, high UV","Tropical sun","Mild winters","Hot, humid"]),
            "habits": random.choice(["Touches face during sports","Hot showers","Outdoor sports","Daily cycling outdoors","Hair oiling weekly","Beard grooming with oils","Spicy foods","Helmet use for cycling","Frequent handwashing","Tennis mid-morning"])
        })

    # Write outputs
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Mapping (audit trail)
    MAP_OUT.write_text(json.dumps({
        "source": ing_path.as_posix(),
        "name_col_guess": name_col,
        "condition_cols": condition_cols,
        "skin_cols": skin_cols,
        "preg_cols": preg_cols
    }, indent=2), encoding="utf-8")

    # CSV
    with CSV_OUT.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLUMNS)
        w.writeheader()
        for r in profiles:
            w.writerow({k: r.get(k,"") for k in COLUMNS})
    print(f"[OK] CSV -> {CSV_OUT}")

    # JSONL (nested shape)
    with JSONL_OUT.open("w", encoding="utf-8") as f:
        for r in profiles:
            obj = {
                "id": r["id"],
                "personal_info": {
                    "name": r["name"], "age": int(r["age"]),
                    "sex": r["sex"], "pregnancy_status": r["pregnancy_status"],
                    "region": r["region"],
                },
                "skin_status": {
                    "skin_type": r["skin_type"],
                    "primary_concern": r["primary_concern"],
                    "secondary_concern": r["secondary_concern"],
                },
                "safety": {
                    "allergies": [s.strip() for s in str(r["allergies"]).split(",") if s.strip()],
                    "drug_sensitivities": [s.strip() for s in str(r["drug_sensitivities"]).split(",") if s.strip()],
                },
                "medical_history": {
                    "past_treatments": [s.strip() for s in str(r["past_treatments"]).split(",") if s.strip()],
                    "adverse_reactions": [s.strip() for s in str(r["adverse_reactions"]).split(",") if s.strip()],
                },
                "lifestyle_preferences": {
                    "routine": r["routine"], "environment": r["environment"], "habits": r["habits"]
                }
            }
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"[OK] JSONL -> {JSONL_OUT}")

    # Optional Excel export if pandas is available
    try:
        import pandas as pd
        with pd.ExcelWriter(XLSX_OUT, engine="xlsxwriter") as w:
            pd.DataFrame(profiles, columns=COLUMNS).to_excel(w, index=False, sheet_name="profiles")
        print(f"[OK] Excel -> {XLSX_OUT}")
    except Exception:
        print("[INFO] Skipped Excel export (pandas + xlsxwriter not available)")

    # Coverage sanity log
    counts = Counter([p["primary_concern"] for p in profiles])
    print("[INFO] Coverage per concern:", dict(counts))

def main():
    # tweak the seed here if you want alternate draws
    build_profiles_100(seed=7)

if __name__ == "__main__":
    main()
