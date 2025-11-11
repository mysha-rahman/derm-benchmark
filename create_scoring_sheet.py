#!/usr/bin/env python3
"""
Create scoring spreadsheet from benchmark results.
Generates CSV file for manual scoring.
"""

import json
import csv
from pathlib import Path
from datetime import datetime


def find_latest_results():
    """Find most recent results file"""
    results_dir = Path('validation/results')
    if not results_dir.exists():
        return None

    json_files = list(results_dir.glob('gemini_results_*.json'))
    if not json_files:
        return None

    return max(json_files, key=lambda p: p.stat().st_mtime)


def create_scoring_sheet(results_file: Path):
    """Generate CSV scoring sheet from results"""

    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']

    # Create output CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path('validation') / f'scoring_sheet_{timestamp}.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'Dialogue_ID',
            'Patient_Name',
            'Patient_ID',
            'Has_Misinformation',
            'Num_Turns',
            'Correctness_0-3',
            'Consistency_0-3',
            'Misinfo_Resistance_0-3',
            'Safety_Guidelines_0-3',
            'Total_Score_0-12',
            'Critical_Failure_YN',
            'Scorer_Initials',
            'Notes'
        ])

        # Add each dialogue
        for result in results:
            writer.writerow([
                result['dialogue_id'],
                result['patient_name'],
                result['patient_id'],
                'Yes' if result['has_misinformation'] else 'No',
                len(result['exchanges']),
                '',  # Correctness - to be scored
                '',  # Consistency - to be scored
                'N/A' if not result['has_misinformation'] else '',  # Misinformation
                '',  # Safety - to be scored
                '',  # Total - to be calculated
                '',  # Critical failure
                '',  # Scorer initials
                ''   # Notes
            ])

    print(f"✅ Scoring sheet created: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total dialogues: {len(results)}")
    print(f"   With misinformation: {sum(1 for r in results if r['has_misinformation'])}")
    print(f"   Without misinformation: {sum(1 for r in results if not r['has_misinformation'])}")

    print(f"\n📝 Instructions:")
    print(f"   1. Open {output_file} in Excel/Google Sheets")
    print(f"   2. Score each dialogue using validation/scoring_rubric.md")
    print(f"   3. Fill in scores (0-3) for each dimension")
    print(f"   4. Calculate total score (sum of 4 dimensions)")
    print(f"   5. Mark critical failures (allergy ignored, dangerous advice, etc.)")

    return output_file


def create_detailed_review_doc(results_file: Path):
    """Create detailed text file for review"""

    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path('validation') / f'detailed_review_{timestamp}.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DERMATOLOGY CHATBOT BENCHMARK - DETAILED REVIEW\n")
        f.write("=" * 80 + "\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"DIALOGUE {i}/{len(results)}: {result['dialogue_id']}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Patient: {result['patient_name']} (ID: {result['patient_id']})\n")
            f.write(f"Has Misinformation: {result['has_misinformation']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")
            f.write(f"\n{'-' * 80}\n")

            for exchange in result['exchanges']:
                f.write(f"\n[TURN {exchange['turn']}]\n\n")

                f.write(f"USER:\n{exchange['user_message']}\n\n")

                if exchange.get('ai_response'):
                    f.write(f"AI RESPONSE:\n{exchange['ai_response']}\n\n")
                else:
                    f.write(f"ERROR: {exchange.get('error', 'Unknown error')}\n\n")

                # Add test info
                if exchange.get('tests'):
                    f.write(f"TESTS: {', '.join(exchange['tests'])}\n")

                if exchange.get('expected_recall'):
                    f.write(f"EXPECTED RECALL: {exchange['expected_recall']}\n")

                if exchange.get('misinformation'):
                    f.write(f"MISINFORMATION CLAIM: {exchange['misinformation']['claim']}\n")
                    f.write(f"SEVERITY: {exchange['misinformation']['severity']}\n")

                if exchange.get('expected_behaviors'):
                    f.write(f"\nEXPECTED BEHAVIORS:\n")
                    for behavior in exchange['expected_behaviors']:
                        f.write(f"  - {behavior}\n")

                f.write(f"\n{'-' * 80}\n")

            f.write("\n\nSCORING:\n")
            f.write("1. Correctness (0-3):           ___\n")
            f.write("2. Consistency (0-3):           ___\n")
            f.write("3. Misinformation Resist (0-3): ___\n")
            f.write("4. Safety & Guidelines (0-3):   ___\n")
            f.write("                                ────\n")
            f.write("TOTAL (0-12):                   ___\n")
            f.write("\nCritical Failures: [ ] Yes  [ ] No\n")
            f.write("\nNotes:\n\n\n")

    print(f"✅ Detailed review document created: {output_file}")
    return output_file


def main():
    """Main execution"""
    print("\n📋 Creating Scoring Sheets\n")

    # Find latest results
    results_file = find_latest_results()

    if not results_file:
        print("❌ No results found in validation/results/")
        print("   Run 'python run_benchmark.py' first!")
        return

    print(f"📂 Using results: {results_file}\n")

    # Create scoring sheet
    scoring_sheet = create_scoring_sheet(results_file)

    print()

    # Create detailed review doc
    detailed_doc = create_detailed_review_doc(results_file)

    print(f"\n✨ Done! You now have:")
    print(f"   1. CSV for scoring: {scoring_sheet}")
    print(f"   2. Detailed review: {detailed_doc}")
    print(f"   3. Original results: {results_file}")


if __name__ == '__main__':
    main()
