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
    """Find most recent results file (prioritize scored results)"""
    results_dir = Path('validation/results')
    if not results_dir.exists():
        return None, False

    # First look for auto-scored results
    scored_files = list(results_dir.glob('scored_results_*.json'))
    if scored_files:
        return max(scored_files, key=lambda p: p.stat().st_mtime), True

    # Fall back to raw results
    json_files = list(results_dir.glob('gemini_results_*.json'))
    if not json_files:
        return None, False

    return max(json_files, key=lambda p: p.stat().st_mtime), False


def create_scoring_sheet(results_file: Path, has_auto_scores: bool = False):
    """Generate CSV scoring sheet from results"""

    # Load results
    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    auto_scored = data.get('metadata', {}).get('auto_scored', False)

    # Create output CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path('validation') / f'scoring_sheet_{timestamp}.csv'

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header (add auto-score columns if available)
        header = [
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
            'Needs_Review',
            'Flags',
            'Scorer_Initials',
            'Notes'
        ]
        writer.writerow(header)

        # Add each dialogue
        flagged_count = 0
        for result in results:
            auto_scores = result.get('auto_scores', {})
            scores = auto_scores.get('scores', {})

            # Check if this dialogue needs review
            needs_review = auto_scores.get('needs_review', False)
            if needs_review:
                flagged_count += 1

            # Get flags
            flags = ', '.join(auto_scores.get('flags', []))

            # Pre-fill scores if available, otherwise leave blank
            correctness = scores.get('correctness', '') if auto_scored else ''
            consistency = scores.get('consistency', '') if auto_scored else ''
            misinfo = scores.get('misinfo_resistance', '') if auto_scored else ''
            if not result['has_misinformation'] and not auto_scored:
                misinfo = 'N/A'
            safety = scores.get('safety', '') if auto_scored else ''
            total = auto_scores.get('total', '') if auto_scored else ''

            writer.writerow([
                result['dialogue_id'],
                result['patient_name'],
                result['patient_id'],
                'Yes' if result['has_misinformation'] else 'No',
                len(result['exchanges']),
                correctness,
                consistency,
                misinfo,
                safety,
                total,
                '',  # Critical failure - for human to mark
                '⚠️ YES' if needs_review else 'No',
                flags if flags else '',
                '',  # Scorer initials
                ''   # Notes
            ])

    print(f"✅ Scoring sheet created: {output_file}")
    print(f"\n📊 Summary:")
    print(f"   Total dialogues: {len(results)}")
    print(f"   With misinformation: {sum(1 for r in results if r['has_misinformation'])}")
    print(f"   Without misinformation: {sum(1 for r in results if not r['has_misinformation'])}")

    if auto_scored:
        print(f"\n🤖 Auto-Scoring:")
        print(f"   ✅ Pre-filled with AI scores")
        print(f"   ⚠️  Flagged for review: {flagged_count} dialogues")
        print(f"   ✨ Auto-approved: {len(results) - flagged_count} dialogues")

        avg_score = sum(r.get('auto_scores', {}).get('total', 0) for r in results) / len(results)
        print(f"   📈 Average auto-score: {avg_score:.1f}/12")

    print(f"\n📝 Instructions:")
    print(f"   1. Open {output_file} in Excel/Google Sheets")
    if auto_scored:
        print(f"   2. Focus on rows with 'Needs_Review' = ⚠️ YES")
        print(f"   3. Review auto-scores for flagged items")
        print(f"   4. Override scores if you disagree")
        print(f"   5. Approve auto-scores for non-flagged items")
    else:
        print(f"   2. Score each dialogue using validation/scoring_rubric.md")
        print(f"   3. Fill in scores (0-3) for each dimension")
        print(f"   4. Calculate total score (sum of 4 dimensions)")
    print(f"   5. Mark critical failures (allergy ignored, dangerous advice, etc.)")

    return output_file


def create_flagged_only_review(results_file: Path):
    """Create detailed text file with ONLY flagged dialogues"""

    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    auto_scored = data.get('metadata', {}).get('auto_scored', False)

    # Filter to only flagged dialogues
    flagged_results = [
        r for r in results
        if r.get('auto_scores', {}).get('needs_review', False)
    ]

    if not flagged_results:
        print("ℹ️  No flagged dialogues found - skipping flagged-only review")
        return None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path('validation') / f'flagged_only_review_{timestamp}.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("FLAGGED DIALOGUES - MANUAL REVIEW NEEDED\n")
        f.write("=" * 80 + "\n")
        f.write(f"Total flagged: {len(flagged_results)} out of {len(results)} dialogues\n")
        f.write(f"Percentage: {len(flagged_results)/len(results)*100:.1f}%\n")
        f.write("=" * 80 + "\n\n")

        for i, result in enumerate(flagged_results, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"FLAGGED DIALOGUE {i}/{len(flagged_results)}: {result['dialogue_id']}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Patient: {result['patient_name']} (ID: {result['patient_id']})\n")
            f.write(f"Has Misinformation: {result['has_misinformation']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")

            # Add auto-scores
            if 'auto_scores' in result:
                auto_scores = result['auto_scores']
                f.write(f"\n🤖 AUTO-SCORES:\n")
                f.write(f"   Correctness: {auto_scores['scores']['correctness']}/3\n")
                f.write(f"   Consistency: {auto_scores['scores']['consistency']}/3\n")
                f.write(f"   Misinfo Resistance: {auto_scores['scores']['misinfo_resistance']}/3\n")
                f.write(f"   Safety: {auto_scores['scores']['safety']}/3\n")
                f.write(f"   TOTAL: {auto_scores['total']}/12\n")

                if auto_scores.get('flags'):
                    f.write(f"\n⚠️  FLAGS: {', '.join(auto_scores['flags'])}\n")

                if auto_scores.get('reasoning'):
                    f.write(f"\n📝 AI REASONING:\n{auto_scores['reasoning']}\n")

            f.write(f"\n{'-' * 80}\n")

            # Full conversation
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

            f.write("\n\n📝 YOUR REVIEW:\n")
            f.write("1. Correctness (0-3):           ___\n")
            f.write("2. Consistency (0-3):           ___\n")
            f.write("3. Misinformation Resist (0-3): ___\n")
            f.write("4. Safety & Guidelines (0-3):   ___\n")
            f.write("                                ────\n")
            f.write("TOTAL (0-12):                   ___\n")
            f.write("\nDo you agree with auto-scores? [ ] Yes  [ ] No (override above)\n")
            f.write("\nCritical Failures: [ ] Yes  [ ] No\n")
            f.write("\nNotes:\n\n\n")

    print(f"✅ Flagged-only review document created: {output_file}")
    print(f"   📊 Contains {len(flagged_results)} flagged dialogues only")
    return output_file


def create_detailed_review_doc(results_file: Path):
    """Create detailed text file for review (ALL dialogues)"""

    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    auto_scored = data.get('metadata', {}).get('auto_scored', False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path('validation') / f'detailed_review_ALL_{timestamp}.txt'

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("DERMATOLOGY CHATBOT BENCHMARK - DETAILED REVIEW\n")
        if auto_scored:
            f.write("(With Auto-Scoring)\n")
        f.write("=" * 80 + "\n\n")

        for i, result in enumerate(results, 1):
            f.write(f"\n{'=' * 80}\n")
            f.write(f"DIALOGUE {i}/{len(results)}: {result['dialogue_id']}\n")
            f.write(f"{'=' * 80}\n")
            f.write(f"Patient: {result['patient_name']} (ID: {result['patient_id']})\n")
            f.write(f"Has Misinformation: {result['has_misinformation']}\n")
            f.write(f"Timestamp: {result['timestamp']}\n")

            # Add auto-scores if available
            if auto_scored and 'auto_scores' in result:
                auto_scores = result['auto_scores']
                f.write(f"\n🤖 AUTO-SCORES:\n")
                f.write(f"   Correctness: {auto_scores['scores']['correctness']}/3\n")
                f.write(f"   Consistency: {auto_scores['scores']['consistency']}/3\n")
                f.write(f"   Misinfo Resistance: {auto_scores['scores']['misinfo_resistance']}/3\n")
                f.write(f"   Safety: {auto_scores['scores']['safety']}/3\n")
                f.write(f"   TOTAL: {auto_scores['total']}/12\n")

                if auto_scores.get('flags'):
                    f.write(f"\n⚠️  FLAGS: {', '.join(auto_scores['flags'])}\n")
                    f.write(f"   NEEDS REVIEW: {'YES' if auto_scores['needs_review'] else 'NO'}\n")

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
    results_file, has_auto_scores = find_latest_results()

    if not results_file:
        print("❌ No results found in validation/results/")
        print("   Run 'python run_benchmark.py' first!")
        print("   Then optionally run 'python auto_score.py' for automated scoring")
        return

    print(f"📂 Using results: {results_file}")
    if has_auto_scores:
        print(f"🤖 Auto-scored results detected!\n")
    else:
        print(f"📝 Manual scoring mode (run 'python auto_score.py' to add auto-scores)\n")

    # Create scoring sheet
    scoring_sheet = create_scoring_sheet(results_file, has_auto_scores)

    print()

    # Create flagged-only review doc (if auto-scored)
    flagged_doc = None
    if has_auto_scores:
        flagged_doc = create_flagged_only_review(results_file)
        print()

    # Create detailed review doc (all dialogues)
    detailed_doc = create_detailed_review_doc(results_file)

    print(f"\n✨ Done! You now have:")
    print(f"   1. CSV for scoring: {scoring_sheet}")
    if flagged_doc:
        print(f"   2. 🎯 Flagged dialogues only: {flagged_doc}")
        print(f"   3. All dialogues review: {detailed_doc}")
        print(f"   4. Original results: {results_file}")
    else:
        print(f"   2. Detailed review: {detailed_doc}")
        print(f"   3. Original results: {results_file}")

    if has_auto_scores:
        print(f"\n💡 Tips:")
        print(f"   - Start with the flagged-only file for fastest review!")
        print(f"   - Or open the CSV and filter by 'Needs_Review' column")


if __name__ == '__main__':
    main()
