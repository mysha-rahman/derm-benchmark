"""Generate synthetic patient profiles from real dermatology datasets."""

import csv
import random
import json
import zipfile
import xml.etree.ElementTree as ET
from pathlib import Path

# Configuration
NUM_PROFILES = 1500  # Scaled up for research significance
OUTPUT_FILE = 'dialogues/patient_profiles_1500.csv'
FITZPATRICK_FILE = 'datasets/Fitzpatrick17k/fitzpatrick17k.csv'
HAM_FILE = 'datasets/HAM10000/metadata/HAM10000_metadata.csv'
MEDICAL_KNOWLEDGE_FILE = 'datasets/Medical_Knowledge/All Diseases Data.xlsx'


def parse_xlsx_standard_library(xlsx_path):
    """Parse XLSX file using zipfile and xml.etree."""
    with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
        # Read shared strings (for text values)
        shared_strings = []
        try:
            with zip_ref.open('xl/sharedStrings.xml') as f:
                tree = ET.parse(f)
                root = tree.getroot()
                ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
                # Extract all text elements
                for si in root.findall('.//main:si', ns):
                    texts = [t.text for t in si.findall('.//main:t', ns) if t.text]
                    shared_strings.append(''.join(texts))
        except KeyError:
            pass  # No shared strings in this file

        # Read the first worksheet
        with zip_ref.open('xl/worksheets/sheet1.xml') as f:
            tree = ET.parse(f)
            root = tree.getroot()
            ns = {'main': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}

            rows = []
            for row_elem in root.findall('.//main:row', ns):
                cells = []
                for cell in row_elem.findall('.//main:c', ns):
                    v = cell.find('main:v', ns)
                    t = cell.get('t')

                    if v is not None:
                        if t == 's':  # String from shared strings
                            cells.append(shared_strings[int(v.text)])
                        else:
                            cells.append(v.text)
                    else:
                        cells.append('')

                rows.append(cells)

            return rows


def load_medical_knowledge_data():
    """Load conditions and treatments from All Diseases Data.xlsx."""
    try:
        rows = parse_xlsx_standard_library(MEDICAL_KNOWLEDGE_FILE)

        # Skip header row
        data_rows = rows[1:]

        conditions = []
        treatments = {}

        for row in data_rows:
            if len(row) < 5:
                continue

            condition_name = row[1] if len(row) > 1 else ''
            treatment_text = row[4] if len(row) > 4 else ''

            if not condition_name or not treatment_text:
                continue

            # Normalize condition name
            normalized = condition_name.strip().title()
            conditions.append(normalized)

            # Extract treatment keywords from treatment text
            # Look for common treatment patterns
            treatment_list = []

            # Common treatment patterns to extract
            treatment_keywords = [
                'topical', 'oral', 'systemic', 'corticosteroid', 'retinoid',
                'antibiotic', 'antifungal', 'steroid', 'phototherapy', 'laser',
                'immunosuppressant', 'biologic', 'excision', 'surgery', 'cryotherapy'
            ]

            treatment_lower = treatment_text.lower()
            for keyword in treatment_keywords:
                if keyword in treatment_lower:
                    # Extract phrase containing keyword
                    if 'topical' in keyword and 'topical' in treatment_lower:
                        treatment_list.append('Topical corticosteroids')
                    elif 'oral' in keyword and 'oral' in treatment_lower:
                        if 'antibiotic' in treatment_lower:
                            treatment_list.append('Oral antibiotics')
                        elif 'corticosteroid' in treatment_lower or 'prednisone' in treatment_lower:
                            treatment_list.append('Oral corticosteroids')
                    elif 'retinoid' in keyword and 'retinoid' in treatment_lower:
                        treatment_list.append('Topical retinoids')
                    elif 'phototherapy' in keyword:
                        treatment_list.append('Phototherapy')
                    elif 'laser' in keyword:
                        treatment_list.append('Laser therapy')
                    elif 'excision' in keyword or 'surgery' in keyword:
                        treatment_list.append('Surgical excision')
                    elif 'cryotherapy' in keyword:
                        treatment_list.append('Cryotherapy')

            # Remove duplicates
            treatment_list = list(set(treatment_list))

            if treatment_list:
                treatments[normalized.lower()] = treatment_list

        print(f"  ✓ Loaded {len(conditions)} conditions from medical knowledge base")
        print(f"  ✓ Extracted treatment info for {len(treatments)} conditions")

        return conditions, treatments

    except Exception as e:
        print(f"  ⚠️  Could not load medical knowledge data: {e}")
        return [], {}


# Realistic names by region
NAMES = {
    'Northeast USA': ['Alex', 'Maya', 'Jordan', 'Sam', 'Taylor', 'Morgan', 'Casey', 'Riley'],
    'Southeast USA': ['Emily', 'James', 'Sarah', 'Michael', 'Jessica', 'David', 'Ashley', 'Chris'],
    'Midwest USA': ['Emma', 'Noah', 'Olivia', 'Liam', 'Ava', 'Mason', 'Sophia', 'Lucas'],
    'Southwest USA': ['Isabella', 'Diego', 'Sofia', 'Carlos', 'Mia', 'Luis', 'Camila', 'Jose'],
    'Pacific Northwest USA': ['Ella', 'Aiden', 'Grace', 'Jackson', 'Lily', 'Ethan', 'Chloe', 'Oliver'],
    'Canada': ['Liam', 'Emma', 'Noah', 'Olivia', 'William', 'Ava', 'James', 'Emily'],
    'Middle East': ['Fatima', 'Omar', 'Aisha', 'Hassan', 'Zahra', 'Ali', 'Layla', 'Karim'],
    'South Korea': ['Jisoo', 'Min-jun', 'Seo-yeon', 'Ji-hoon', 'Ji-woo', 'Ye-jun', 'Su-bin', 'Do-yun'],
    'Japan': ['Yuki', 'Haruto', 'Sakura', 'Sota', 'Hina', 'Riku', 'Yui', 'Ren'],
    'Philippines': ['Maria', 'Jose', 'Ana', 'Juan', 'Angela', 'Miguel', 'Sofia', 'Luis'],
    'Nigeria': ['Amara', 'Chukwu', 'Nneka', 'Emeka', 'Zara', 'Kelechi', 'Adanna', 'Chidera'],
    'Ghana': ['Kofi', 'Akua', 'Kwame', 'Ama', 'Yaw', 'Efua', 'Kojo', 'Abena'],
    'Egypt': ['Ahmed', 'Mariam', 'Mohamed', 'Nour', 'Omar', 'Sara', 'Ali', 'Fatima'],
    'Pakistan': ['Muhammad', 'Fatima', 'Ali', 'Aisha', 'Hassan', 'Zainab', 'Ahmed', 'Mariam'],
    'Germany': ['Lukas', 'Emma', 'Leon', 'Mia', 'Finn', 'Hannah', 'Jonas', 'Sophia'],
}

SURNAMES = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Martinez', 'Rodriguez',
            'Lee', 'Kim', 'Park', 'Chen', 'Wang', 'Singh', 'Patel', 'Rahman', 'Ahmed',
            'Lopez', 'Gonzalez', 'Wilson', 'Anderson', 'Thomas', 'Taylor', 'Moore', 'Jackson',
            'Okoye', 'Nwankwo', 'Santos', 'Silva', 'Petrova', 'Ivanov', 'Mueller', 'Schmidt']

REGIONS = list(NAMES.keys())

# Top conditions from Fitzpatrick17k (based on actual frequencies)
TOP_CONDITIONS = [
    'Psoriasis', 'Acne', 'Eczema', 'Contact Dermatitis', 'Rosacea',
    'Melasma', 'Seborrheic Dermatitis', 'Sun Damage', 'Hyperpigmentation',
    'Folliculitis', 'Lupus', 'Dermatitis', 'Lichen Planus', 'Vitiligo'
]

# Map conditions to realistic treatments based on clinical guidelines
CONDITION_TREATMENTS = {
    'psoriasis': ['Topical corticosteroids', 'Calcipotriene', 'Methotrexate', 'Phototherapy', 'Coal tar'],
    'acne': ['Benzoyl peroxide', 'Topical retinoids', 'Salicylic acid', 'Antibiotics', 'Azelaic acid'],
    'eczema': ['Emollients', 'Topical corticosteroids', 'Tacrolimus', 'Antihistamines', 'Barrier repair creams'],
    'contact dermatitis': ['Topical corticosteroids', 'Antihistamines', 'Cool compresses', 'Moisturizers'],
    'rosacea': ['Metronidazole gel', 'Azelaic acid', 'Ivermectin', 'Brimonidine', 'Gentle skincare'],
    'melasma': ['Hydroquinone', 'Tretinoin', 'Kojic acid', 'Azelaic acid', 'Sunscreen SPF 50+'],
    'seborrheic dermatitis': ['Ketoconazole shampoo', 'Zinc pyrithione', 'Selenium sulfide', 'Topical corticosteroids'],
}

# Common allergies
ALLERGIES = ['None', 'Fragrance mix', 'Nickel', 'Latex', 'Dust mites', 'Pollen',
             'Preservatives', 'Lanolin', 'Propylene glycol']

# Drug sensitivities
SENSITIVITIES = ['None', 'Retinoids cause dryness', 'AHAs sting', 'Benzoyl peroxide irritates',
                 'Alcohol-based toners sting', 'Propylene glycol stings']

# Skin types
SKIN_TYPES = ['Dry', 'Oily', 'Combination', 'Sensitive', 'Normal']

# Adverse reactions
ADVERSE_REACTIONS = ['None', 'Mild irritation week 1', 'Peeling when overused',
                     'Transient dryness', 'Dryness after use', 'Redness initially']

# Routines
ROUTINES = ['Minimal routine', 'Double cleanse at night', 'SPF reapplication mid-day',
            'Moisturizer after bath', 'Barrier-repair moisturizer focus',
            'Mineral sunscreen; avoid triggers', 'Gentle cleansing routine']

# Environments
ENVIRONMENTS = ['Urban pollution', 'Dry climate', 'Humid summers', 'Cold winters',
                'High UV in summer', 'Tropical sun', 'Arid, high UV', 'Mild winters']

# Habits (age/gender appropriate assignments)
HABITS_GENERAL = ['Touches face during sports', 'Long hot showers', 'Outdoor sports',
                  'Daily cycling outdoors', 'Swimming regularly', 'Tennis mid-morning',
                  'Hot showers', 'Helmet use for cycling', 'Hair oiling weekly', 'Spicy foods']

HABITS_MALE = ['Beard grooming with oils', 'Shaving daily', 'Frequent gym use']

def load_ham_demographics():
    """Load age/sex from HAM10000 dataset"""
    demographics = []
    try:
        with open(HAM_FILE, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row.get('age') and row.get('sex'):
                    try:
                        age = int(float(row['age']))
                        sex = row['sex'].strip().capitalize()
                        if sex in ['Male', 'Female'] and 10 <= age <= 95:
                            demographics.append((age, sex))
                    except:
                        pass
    except FileNotFoundError:
        print("  ⚠️  HAM10000 file not found, using random demographics")
    return demographics if demographics else None

def get_age_sex(ham_demographics):
    """Get realistic age/sex"""
    if ham_demographics:
        age, sex = random.choice(ham_demographics)
        # Adjust age distribution (HAM skews older)
        if random.random() < 0.3:  # 30% younger patients
            age = random.randint(14, 35)
        return age, sex
    else:
        age = random.randint(14, 75)
        sex = random.choice(['Male', 'Female'])
        return age, sex

def get_treatments_for_condition(condition, extended_treatments=None):
    """Get treatments for condition from hardcoded list or extended data."""
    condition_lower = condition.lower()

    # First check extended treatments from medical knowledge base
    if extended_treatments and condition_lower in extended_treatments:
        treatments = extended_treatments[condition_lower]
        num_treatments = random.randint(1, min(3, len(treatments)))
        selected = random.sample(treatments, num_treatments)
        return ', '.join(selected)

    # Fall back to hardcoded treatments
    for key in CONDITION_TREATMENTS:
        if key in condition_lower:
            num_treatments = random.randint(1, 3)
            treatments = CONDITION_TREATMENTS[key]
            selected = random.sample(treatments, min(num_treatments, len(treatments)))
            return ', '.join(selected)

    return 'Topical treatments'

def generate_profile(profile_id, ham_demographics, extended_conditions=None, extended_treatments=None):
    """Generate one patient profile."""

    age, sex = get_age_sex(ham_demographics)

    # Region and name
    region = random.choice(REGIONS)
    first_name = random.choice(NAMES[region])
    surname = random.choice(SURNAMES)
    name = f"{first_name} {surname}"

    # Pregnancy status (only for females of childbearing age)
    if sex == 'Female' and 14 <= age <= 50:
        pregnancy_status = random.choice(['Not Pregnant'] * 9 + ['Pregnant'])  # 10% pregnant
    else:
        pregnancy_status = 'N/A'

    # Skin type and conditions
    skin_type = random.choice(SKIN_TYPES)

    # Combine hardcoded and extended conditions
    all_conditions = TOP_CONDITIONS.copy()
    if extended_conditions:
        # Add unique extended conditions (avoid duplicates)
        for cond in extended_conditions:
            if cond not in all_conditions:
                all_conditions.append(cond)

    primary_concern = random.choice(all_conditions)

    # Secondary concern (different from primary)
    available_conditions = [c for c in all_conditions if c != primary_concern]
    secondary_concern = random.choice(available_conditions) if available_conditions else 'None'

    # Allergies and sensitivities
    allergies = random.choice(ALLERGIES)
    drug_sensitivities = random.choice(SENSITIVITIES)

    # Treatments based on condition (with extended treatments)
    past_treatments = get_treatments_for_condition(primary_concern, extended_treatments)

    # Other attributes
    adverse_reactions = random.choice(ADVERSE_REACTIONS)
    routine = random.choice(ROUTINES)
    environment = random.choice(ENVIRONMENTS)

    # Gender/age appropriate habits
    if sex == 'Male' and age >= 16:
        habits = random.choice(HABITS_GENERAL + HABITS_MALE)
    else:
        habits = random.choice(HABITS_GENERAL)

    return [
        profile_id, name, age, sex, pregnancy_status, region, skin_type,
        primary_concern, secondary_concern, allergies, drug_sensitivities,
        past_treatments, adverse_reactions, routine, environment, habits
    ]

def main():
    print("=" * 60)
    print("AUTO-GENERATING PATIENT PROFILES FROM REAL DATA")
    print("=" * 60)

    # Load HAM demographics
    print("\nLoading demographics from HAM10000...")
    ham_demographics = load_ham_demographics()
    if ham_demographics:
        print(f"  ✓ Loaded {len(ham_demographics):,} demographic records")
    else:
        print("  ⚠️  Using random demographics")

    # Load medical knowledge data
    print("\nLoading medical knowledge from All Diseases Data.xlsx...")
    extended_conditions, extended_treatments = load_medical_knowledge_data()

    print(f"\n📊 Total available conditions: "
          f"{len(TOP_CONDITIONS)} (hardcoded) + {len(extended_conditions)} (extended) = "
          f"{len(set(TOP_CONDITIONS + extended_conditions))} unique")

    print(f"\nGenerating {NUM_PROFILES} realistic profiles...\n")

    # Generate profiles
    profiles = []
    for i in range(1, NUM_PROFILES + 1):
        profile = generate_profile(i, ham_demographics, extended_conditions, extended_treatments)
        profiles.append(profile)
        if i % 10 == 0:
            print(f"  ✓ Generated {i}/{NUM_PROFILES} profiles")

    # Save to CSV
    headers = ['id', 'name', 'age', 'sex', 'pregnancy_status', 'region', 'skin_type',
               'primary_concern', 'secondary_concern', 'allergies', 'drug_sensitivities',
               'past_treatments', 'adverse_reactions', 'routine', 'environment', 'habits']

    with open(OUTPUT_FILE, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(profiles)

    print(f"\n✅ SUCCESS! Saved {NUM_PROFILES} profiles to {OUTPUT_FILE}")

    # Print statistics
    print("\n" + "=" * 60)
    print("PROFILE STATISTICS")
    print("=" * 60)

    ages = [p[2] for p in profiles]
    print(f"\nAge distribution:")
    print(f"  • Min: {min(ages)}")
    print(f"  • Max: {max(ages)}")
    print(f"  • Mean: {sum(ages)/len(ages):.1f}")

    sexes = {}
    for p in profiles:
        sex = p[3]
        sexes[sex] = sexes.get(sex, 0) + 1
    print(f"\nSex distribution:")
    for sex, count in sexes.items():
        print(f"  • {sex}: {count}")

    conditions = {}
    for p in profiles:
        condition = p[7]
        conditions[condition] = conditions.get(condition, 0) + 1
    print(f"\nTop 10 conditions:")
    sorted_conditions = sorted(conditions.items(), key=lambda x: x[1], reverse=True)[:10]
    for condition, count in sorted_conditions:
        print(f"  • {condition}: {count}")

    print("\n" + "=" * 60)
    print("PROFILES READY FOR DIALOGUE GENERATION!")
    print("=" * 60)
    print(f"\nNext step: python generate_dialogues.py")

if __name__ == "__main__":
    main()
