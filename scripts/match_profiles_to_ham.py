"""
Match Gold Profiles to Similar HAM10000 Cases
"""
import pandas as pd
import json
from pathlib import Path

# Load your gold profiles
gold_profiles = []
with open("gold_profiles/gold_profiles.jsonl", "r") as f:
    for line in f:
        gold_profiles.append(json.loads(line))

# Load HAM10000 metadata
ham_df = pd.read_csv("datasets/HAM10000/metadata/HAM10000_metadata.csv")

# Map your concerns to HAM10000 diagnoses
concern_to_dx = {
    "Acne": None,  # Not in HAM10000
    "Eczema": None,  # Not in HAM10000
    "Psoriasis": None,  # Not in HAM10000
    "Melasma": "mel",  # Melanoma (closest match)
    "Hyperpigmentation": "mel",  # Melanoma
    "Rosacea": None,  # Not in HAM10000
}

print("=== Matching Gold Profiles to HAM10000 ===\n")

for profile in gold_profiles:
    name = profile['personal_info']['name']
    age = profile['personal_info']['age']
    sex = profile['personal_info']['sex']
    concern = profile['skin_status']['primary_concern']
    
    print(f"\n{name} (Age: {age}, Sex: {sex})")
    print(f"Primary Concern: {concern}")
    
    # Try to find similar cases in HAM10000
    if concern in concern_to_dx and concern_to_dx[concern]:
        dx_code = concern_to_dx[concern]
        
        # Find cases with similar demographics
        similar = ham_df[
            (ham_df['dx'] == dx_code) &
            (ham_df['age'].between(age - 5, age + 5)) &
            (ham_df['sex'].str.lower() == sex.lower())
        ]
        
        print(f"  → Found {len(similar)} similar HAM10000 cases")
        if len(similar) > 0:
            print(f"  → Sample image IDs: {similar['image_id'].head(3).tolist()}")
    else:
        print(f"  → No direct match in HAM10000 (dataset focuses on pigmented lesions)")