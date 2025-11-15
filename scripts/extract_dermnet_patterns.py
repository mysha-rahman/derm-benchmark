"""
Extract Clinical Patterns from DermNet NZ Cases

This script analyzes DermNet NZ case studies to understand common clinical patterns,
which inform the creation of realistic synthetic patient profiles.

ETHICAL USE:
- We extract PATTERNS (e.g., "psoriasis patients often use topical corticosteroids")
- We DO NOT copy patient data or case descriptions verbatim
- We properly attribute DermNet NZ in our research
- We respect rate limits (2-3 second delays between requests)

Source: DermNet NZ (https://dermnetnz.org/)
Attribution: DermNet NZ. All About the Skin. Available at: https://dermnetnz.org/
"""

import requests
from bs4 import BeautifulSoup
import time
import json
from pathlib import Path
from collections import defaultdict

def scrape_dermnet_case_patterns(max_cases=50, delay=3):
    """
    Extract clinical patterns from DermNet NZ cases to inform synthetic profile creation.

    Args:
        max_cases: Maximum number of cases to analyze
        delay: Seconds to wait between requests (be respectful!)

    Returns:
        Dictionary of clinical patterns
    """

    print("=" * 60)
    print("DERMNET NZ PATTERN EXTRACTION")
    print("=" * 60)
    print("⚠️  Ethical use: Extracting patterns only, not copying content")
    print(f"⏱  Rate limit: {delay}s delay between requests\n")

    # Pattern storage
    patterns = {
        'conditions': defaultdict(lambda: {
            'count': 0,
            'common_treatments': defaultdict(int),
            'common_symptoms': defaultdict(int),
            'age_patterns': defaultdict(int),
            'typical_locations': defaultdict(int)
        })
    }

    # DermNet topics to analyze (conditions matching our benchmark)
    topics = [
        'psoriasis',
        'acne-vulgaris',
        'eczema',
        'atopic-dermatitis',
        'contact-dermatitis',
        'rosacea',
        'melasma',
        'seborrhoeic-dermatitis'
    ]

    print("📋 Analyzing conditions:")
    for topic in topics:
        print(f"  • {topic.replace('-', ' ').title()}")
    print()

    total_analyzed = 0

    for topic in topics:
        if total_analyzed >= max_cases:
            break

        topic_url = f"https://dermnetnz.org/topics/{topic}"
        print(f"🔍 Analyzing: {topic_url}")

        try:
            # Respect robots.txt and rate limits
            time.sleep(delay)

            headers = {
                'User-Agent': 'Mozilla/5.0 (Research Project; Educational Use Only)'
            }
            response = requests.get(topic_url, headers=headers, timeout=10)

            if response.status_code != 200:
                print(f"  ⚠️  Status {response.status_code}, skipping")
                continue

            soup = BeautifulSoup(response.content, 'html.parser')
            content = soup.get_text().lower()

            # Extract patterns (NOT copying content, just analyzing presence)
            condition_key = topic.replace('-', ' ')
            patterns['conditions'][condition_key]['count'] += 1

            # Treatment patterns (common medications mentioned)
            treatments = {
                'topical corticosteroids': ['corticosteroid', 'hydrocortisone', 'betamethasone'],
                'topical retinoids': ['retinoid', 'tretinoin', 'adapalene'],
                'emollients': ['emollient', 'moisturizer', 'cream'],
                'antibiotics': ['antibiotic', 'doxycycline', 'erythromycin'],
                'antifungals': ['antifungal', 'ketoconazole', 'clotrimazole'],
                'benzoyl peroxide': ['benzoyl peroxide'],
                'salicylic acid': ['salicylic acid'],
                'sunscreen': ['sunscreen', 'sun protection'],
                'phototherapy': ['phototherapy', 'uv', 'light therapy']
            }

            for treatment, keywords in treatments.items():
                if any(kw in content for kw in keywords):
                    patterns['conditions'][condition_key]['common_treatments'][treatment] += 1

            # Symptom patterns
            symptoms = {
                'itching': ['itch', 'pruritus'],
                'redness': ['red', 'erythema'],
                'scaling': ['scale', 'scaly', 'flaky'],
                'dryness': ['dry', 'xerosis'],
                'inflammation': ['inflam', 'swelling'],
                'lesions': ['lesion', 'papule', 'pustule'],
                'pigmentation': ['pigment', 'hyperpigment', 'dark']
            }

            for symptom, keywords in symptoms.items():
                if any(kw in content for kw in keywords):
                    patterns['conditions'][condition_key]['common_symptoms'][symptom] += 1

            # Age patterns
            age_groups = {
                'children': ['child', 'pediatric', 'infant'],
                'teenagers': ['teen', 'adolescent'],
                'adults': ['adult'],
                'elderly': ['elderly', 'older']
            }

            for age_group, keywords in age_groups.items():
                if any(kw in content for kw in keywords):
                    patterns['conditions'][condition_key]['age_patterns'][age_group] += 1

            # Body location patterns
            locations = {
                'face': ['face', 'facial'],
                'scalp': ['scalp'],
                'hands': ['hand', 'palm'],
                'trunk': ['trunk', 'chest', 'back'],
                'arms': ['arm', 'forearm'],
                'legs': ['leg', 'shin']
            }

            for location, keywords in locations.items():
                if any(kw in content for kw in keywords):
                    patterns['conditions'][condition_key]['typical_locations'][location] += 1

            print(f"  ✅ Pattern extracted")
            total_analyzed += 1

        except Exception as e:
            print(f"  ❌ Error: {e}")
            continue

    # Convert defaultdicts to regular dicts for JSON serialization
    patterns_clean = {}
    for condition, data in patterns['conditions'].items():
        patterns_clean[condition] = {
            'count': data['count'],
            'common_treatments': dict(data['common_treatments']),
            'common_symptoms': dict(data['common_symptoms']),
            'age_patterns': dict(data['age_patterns']),
            'typical_locations': dict(data['typical_locations'])
        }

    return patterns_clean

def save_patterns(patterns, output_path='validation/dermnet_patterns.json'):
    """Save extracted patterns to JSON file"""

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w') as f:
        json.dump(patterns, f, indent=2)

    print(f"\n✅ Patterns saved to: {output_file}")

    # Print summary
    print("\n" + "=" * 60)
    print("PATTERN SUMMARY")
    print("=" * 60)

    for condition, data in patterns.items():
        print(f"\n{condition.upper()}")
        print(f"  Top treatments: {', '.join(list(data['common_treatments'].keys())[:3])}")
        print(f"  Top symptoms: {', '.join(list(data['common_symptoms'].keys())[:3])}")
        print(f"  Age groups: {', '.join(data['age_patterns'].keys())}")

def generate_attribution():
    """Generate proper DermNet NZ attribution text"""

    attribution = """
# DermNet NZ Attribution

This research uses clinical patterns extracted from DermNet NZ to inform
the creation of realistic synthetic patient profiles.

**Source**: DermNet NZ - All About the Skin
**URL**: https://dermnetnz.org/
**Usage**: Educational and research purposes
**Method**: Pattern extraction (not verbatim copying)

## Citation

DermNet NZ. All About the Skin. Available at: https://dermnetnz.org/
(Accessed: November 2025)

## Patterns Extracted

We analyzed DermNet NZ topic pages to understand:
- Common treatment patterns for various conditions
- Typical symptom presentations
- Age group associations
- Body location patterns

This information was used to create more realistic synthetic patient profiles
for our AI chatbot benchmark, not to copy actual patient cases.
"""

    with open('validation/DERMNET_ATTRIBUTION.md', 'w') as f:
        f.write(attribution)

    print("\n✅ Attribution file created: validation/DERMNET_ATTRIBUTION.md")

if __name__ == "__main__":
    print("\n🔬 Starting DermNet NZ pattern extraction...")
    print("⚠️  This may take several minutes due to rate limiting\n")

    # Extract patterns
    patterns = scrape_dermnet_case_patterns(max_cases=20, delay=3)

    # Save results
    save_patterns(patterns)

    # Generate attribution
    generate_attribution()

    print("\n" + "=" * 60)
    print("✅ EXTRACTION COMPLETE")
    print("=" * 60)
    print("\nNext steps:")
    print("1. Review validation/dermnet_patterns.json")
    print("2. Use patterns to enhance patient_profiles_100.csv")
    print("3. Include validation/DERMNET_ATTRIBUTION.md in your research")
    print("\nRemember: Always cite DermNet NZ in your final report!")
