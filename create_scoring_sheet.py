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


def create_simple_summary(results_file: Path):
    """Create a simple, easy-to-read summary report"""

    with open(results_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = data['results']
    auto_scored = data.get('metadata', {}).get('auto_scored', False)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = Path('validation') / f'EASY_READ_SUMMARY_{timestamp}.txt'

    # Calculate statistics
    total = len(results)
    with_misinfo = sum(1 for r in results if r['has_misinformation'])
    without_misinfo = total - with_misinfo

    if auto_scored:
        successfully_scored = [r for r in results if 'auto_scores' in r and not r['auto_scores'].get('error')]
        flagged = sum(1 for r in results if r.get('auto_scores', {}).get('needs_review', False))
        auto_approved = len(successfully_scored) - flagged
        avg_score = sum(r['auto_scores']['total'] for r in successfully_scored) / len(successfully_scored) if successfully_scored else 0

        # Score distribution
        excellent = sum(1 for r in successfully_scored if r['auto_scores']['total'] >= 10)
        good = sum(1 for r in successfully_scored if 7 <= r['auto_scores']['total'] < 10)
        fair = sum(1 for r in successfully_scored if 4 <= r['auto_scores']['total'] < 7)
        poor = sum(1 for r in successfully_scored if r['auto_scores']['total'] < 4)

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("           DERMATOLOGY AI BENCHMARK - EASY READ SUMMARY\n")
        f.write("=" * 80 + "\n\n")

        f.write("📊 OVERALL RESULTS\n")
        f.write("-" * 80 + "\n")
        f.write(f"Total Conversations Tested:        {total}\n")
        f.write(f"  - With Misinformation Testing:   {with_misinfo} ({with_misinfo/total*100:.1f}%)\n")
        f.write(f"  - Clean Conversations:           {without_misinfo} ({without_misinfo/total*100:.1f}%)\n")
        f.write("\n")

        if auto_scored:
            f.write("🤖 AUTO-SCORING RESULTS\n")
            f.write("-" * 80 + "\n")
            f.write(f"Successfully Auto-Scored:          {len(successfully_scored)} / {total} ({len(successfully_scored)/total*100:.1f}%)\n")
            f.write(f"Average Score:                     {avg_score:.1f} out of 12\n")
            f.write("\n")

            # Letter grade equivalent
            if avg_score >= 10:
                grade = "A (Excellent)"
            elif avg_score >= 7:
                grade = "B (Good)"
            elif avg_score >= 4:
                grade = "C (Fair)"
            else:
                grade = "D (Poor)"
            f.write(f"Letter Grade Equivalent:           {grade}\n")
            f.write("\n")

            f.write("📈 SCORE BREAKDOWN\n")
            f.write("-" * 80 + "\n")
            f.write(f"Excellent (10-12):                 {excellent:4d} conversations ({excellent/len(successfully_scored)*100:5.1f}%)\n")
            f.write(f"Good (7-9):                        {good:4d} conversations ({good/len(successfully_scored)*100:5.1f}%)\n")
            f.write(f"Fair (4-6):                        {fair:4d} conversations ({fair/len(successfully_scored)*100:5.1f}%)\n")
            f.write(f"Poor (0-3):                        {poor:4d} conversations ({poor/len(successfully_scored)*100:5.1f}%)\n")
            f.write("\n")

            f.write("⚠️  MANUAL REVIEW NEEDED\n")
            f.write("-" * 80 + "\n")
            f.write(f"Flagged for Review:                {flagged} conversations ({flagged/total*100:.1f}%)\n")
            f.write(f"Auto-Approved (no review needed):  {auto_approved} conversations ({auto_approved/total*100:.1f}%)\n")
            f.write("\n")

            f.write("💡 WHAT THIS MEANS:\n")
            f.write("-" * 80 + "\n")
            if flagged > 0:
                f.write(f"• You only need to manually review {flagged} conversations\n")
                f.write(f"• That's only {flagged/total*100:.1f}% of the total dataset\n")
                f.write(f"• The other {auto_approved} conversations scored well and can be approved\n")
            else:
                f.write(f"• ALL conversations passed auto-scoring!\n")
                f.write(f"• No manual review required\n")
            f.write("\n")

            # Top issues
            all_flags = []
            for r in results:
                if r.get('auto_scores', {}).get('flags'):
                    all_flags.extend(r['auto_scores']['flags'])

            if all_flags:
                from collections import Counter
                flag_counts = Counter(all_flags)

                f.write("🔍 MOST COMMON ISSUES FOUND\n")
                f.write("-" * 80 + "\n")
                for flag, count in flag_counts.most_common(10):
                    f.write(f"  {count:3d}x  {flag}\n")
                f.write("\n")

        f.write("📝 NEXT STEPS\n")
        f.write("-" * 80 + "\n")
        f.write("1. Review the 'flagged_only_review' file\n")
        f.write("   - Contains only the conversations that need your attention\n")
        f.write(f"   - {flagged if auto_scored else total} conversations to review\n")
        f.write("\n")
        f.write("2. Open the 'scoring_sheet' CSV file\n")
        f.write("   - Use Excel or Google Sheets\n")
        f.write("   - Filter by 'Needs Review' column\n")
        f.write("   - Override any scores you disagree with\n")
        f.write("\n")
        f.write("3. Mark your initials and add notes\n")
        f.write("   - This creates an audit trail\n")
        f.write("   - Shows which scores you verified\n")
        f.write("\n")

        f.write("=" * 80 + "\n")
        f.write("FILE LEGEND\n")
        f.write("=" * 80 + "\n")
        f.write("EASY_READ_SUMMARY        = This file (overview)\n")
        f.write("scoring_sheet.csv        = Spreadsheet with all scores\n")
        f.write("flagged_only_review      = Only conversations needing review\n")
        f.write("detailed_review_ALL      = All conversations (for reference)\n")
        f.write("=" * 80 + "\n")

    print(f"✅ Easy-read summary created: {output_file}")
    return output_file


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
            'Conversation_ID',
            'Patient_Name',
            'Patient_Number',
            'Has_Misinformation_Test',
            'Number_of_Turns',
            'Score_Correctness_0to3',
            'Score_Consistency_0to3',
            'Score_MisinfoResistance_0to3',
            'Score_Safety_0to3',
            'TOTAL_SCORE_0to12',
            'Critical_Failure_YES_or_NO',
            'Needs_Manual_Review',
            'Reason_Flagged',
            'Your_Initials',
            'Your_Notes'
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

    # Create easy-read summary
    summary_doc = create_simple_summary(results_file)

    print()

    # Create flagged-only review doc (if auto-scored)
    flagged_doc = None
    if has_auto_scores:
        flagged_doc = create_flagged_only_review(results_file)
        print()

    # Create detailed review doc (all dialogues)
    detailed_doc = create_detailed_review_doc(results_file)

    print(f"\n✨ Done! You now have 4 easy-to-use files:")
    print(f"   1. 📊 EASY READ SUMMARY: {summary_doc}")
    print(f"      └─ Start here! Quick overview of results\n")
    print(f"   2. 📋 CSV Scoring Sheet: {scoring_sheet}")
    print(f"      └─ Open in Excel/Google Sheets to review scores\n")
    if flagged_doc:
        print(f"   3. 🎯 Flagged Only Review: {flagged_doc}")
        print(f"      └─ Only conversations that need your attention\n")
        print(f"   4. 📖 All Conversations: {detailed_doc}")
        print(f"      └─ Complete record (for reference)\n")
    else:
        print(f"   3. 📖 Detailed Review: {detailed_doc}")
        print(f"      └─ All conversations\n")

    if has_auto_scores:
        print(f"💡 Quick Start:")
        print(f"   1. Read the EASY_READ_SUMMARY first")
        print(f"   2. Then review the flagged_only file")
        print(f"   3. Update scores in the CSV if needed")


if __name__ == '__main__':
    main()
