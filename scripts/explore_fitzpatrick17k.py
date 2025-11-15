"""
Explore Fitzpatrick17k Dataset

Analyzes the Fitzpatrick17k dermatology dataset and generates statistics.
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Load dataset
DATA_PATH = Path("datasets/Fitzpatrick17k/fitzpatrick17k.csv")
df = pd.read_csv(DATA_PATH)

print("=" * 60)
print("FITZPATRICK17K DATASET EXPLORATION")
print("=" * 60)

# Basic statistics
print(f"\nTotal records: {len(df):,}")
print(f"Unique conditions: {df['label'].nunique()}")
print(f"Unique images: {df['md5hash'].nunique()}")

# Fitzpatrick scale distribution
print("\n" + "=" * 60)
print("FITZPATRICK SKIN TONE DISTRIBUTION")
print("=" * 60)
fitzpatrick_counts = df['fitzpatrick_scale'].value_counts().sort_index()
print(fitzpatrick_counts)
print("\nSkin Tone Groups:")
lighter = df[df['fitzpatrick_scale'].isin([1, 2])].shape[0]
medium = df[df['fitzpatrick_scale'].isin([3, 4])].shape[0]
darker = df[df['fitzpatrick_scale'].isin([5, 6])].shape[0]
unknown = df[df['fitzpatrick_scale'] == -1].shape[0]
print(f"  Lighter (1-2): {lighter:,} ({lighter/len(df)*100:.1f}%)")
print(f"  Medium (3-4):  {medium:,} ({medium/len(df)*100:.1f}%)")
print(f"  Darker (5-6):  {darker:,} ({darker/len(df)*100:.1f}%)")
print(f"  Unknown (-1):  {unknown:,} ({unknown/len(df)*100:.1f}%)")

# Top conditions
print("\n" + "=" * 60)
print("TOP 20 DERMATOLOGY CONDITIONS")
print("=" * 60)
top_conditions = df['label'].value_counts().head(20)
for i, (condition, count) in enumerate(top_conditions.items(), 1):
    print(f"{i:2d}. {condition:<35} {count:>5,} ({count/len(df)*100:>5.1f}%)")

# Category distribution
print("\n" + "=" * 60)
print("CONDITION CATEGORIES (3-partition)")
print("=" * 60)
category_counts = df['three_partition_label'].value_counts()
for category, count in category_counts.items():
    print(f"  {category:<20} {count:>5,} ({count/len(df)*100:>5.1f}%)")

# 9-partition distribution
print("\n" + "=" * 60)
print("CONDITION CATEGORIES (9-partition)")
print("=" * 60)
nine_partition_counts = df['nine_partition_label'].value_counts()
for category, count in nine_partition_counts.items():
    print(f"  {category:<30} {count:>5,} ({count/len(df)*100:>5.1f}%)")

# Conditions matching our benchmark
print("\n" + "=" * 60)
print("CONDITIONS MATCHING OUR BENCHMARK")
print("=" * 60)
benchmark_conditions = [
    'psoriasis', 'acne vulgaris', 'eczema', 'allergic contact dermatitis',
    'lupus erythematosus', 'lichen planus', 'rosacea', 'scabies',
    'folliculitis', 'drug eruption', 'photodermatoses'
]
matching = df[df['label'].str.lower().isin(benchmark_conditions)]
print(f"Total matching cases: {len(matching):,} ({len(matching)/len(df)*100:.1f}%)\n")
for condition in benchmark_conditions:
    count = df[df['label'].str.lower() == condition].shape[0]
    if count > 0:
        print(f"  {condition.capitalize():<35} {count:>5,}")

# Generate visualization
print("\n" + "=" * 60)
print("GENERATING VISUALIZATION")
print("=" * 60)

fig, axes = plt.subplots(2, 2, figsize=(14, 10))
fig.suptitle('Fitzpatrick17k Dataset Distribution', fontsize=16, fontweight='bold')

# 1. Top 15 conditions
ax1 = axes[0, 0]
top_15 = df['label'].value_counts().head(15)
top_15.plot(kind='barh', ax=ax1, color='steelblue')
ax1.set_xlabel('Number of Cases')
ax1.set_title('Top 15 Dermatology Conditions')
ax1.invert_yaxis()

# 2. Fitzpatrick scale distribution
ax2 = axes[0, 1]
fitz_clean = df[df['fitzpatrick_scale'] != -1]['fitzpatrick_scale']
fitz_clean.value_counts().sort_index().plot(kind='bar', ax=ax2, color='coral')
ax2.set_xlabel('Fitzpatrick Skin Tone Scale')
ax2.set_ylabel('Number of Cases')
ax2.set_title('Fitzpatrick Skin Tone Distribution')
ax2.set_xticklabels(ax2.get_xticklabels(), rotation=0)

# 3. 3-partition categories
ax3 = axes[1, 0]
df['three_partition_label'].value_counts().plot(kind='pie', ax=ax3, autopct='%1.1f%%', startangle=90)
ax3.set_ylabel('')
ax3.set_title('Condition Categories (3-partition)')

# 4. Benchmark conditions vs others
ax4 = axes[1, 1]
benchmark_count = len(matching)
other_count = len(df) - benchmark_count
ax4.pie([benchmark_count, other_count],
        labels=['Matches Our\nBenchmark', 'Other\nConditions'],
        autopct='%1.1f%%', colors=['#2ecc71', '#95a5a6'], startangle=90)
ax4.set_title('Relevance to Our Benchmark')

plt.tight_layout()
output_file = 'fitzpatrick17k_distribution.png'
plt.savefig(output_file, dpi=150, bbox_inches='tight')
print(f"✅ Saved visualization: {output_file}")

print("\n" + "=" * 60)
print("DATASET QUALITY")
print("=" * 60)
print(f"Missing values in 'label': {df['label'].isna().sum()}")
print(f"Missing values in 'fitzpatrick_scale': {df['fitzpatrick_scale'].isna().sum()}")
print(f"Records with quality control flags: {df['qc'].notna().sum()}")

print("\n" + "=" * 60)
print("EXPLORATION COMPLETE")
print("=" * 60)
print("\nKey Findings:")
print(f"  • {len(df):,} dermatology cases across {df['label'].nunique()} conditions")
print(f"  • Good skin tone diversity (Fitzpatrick 1-6)")
print(f"  • {len(matching):,} cases match our benchmark conditions")
print(f"  • {len(df[df['label'].str.contains('psoriasis', case=False, na=False)]):,} psoriasis cases")
print(f"  • {len(df[df['label'].str.contains('acne', case=False, na=False)]):,} acne cases")
print(f"  • {len(df[df['label'].str.contains('eczema', case=False, na=False)]):,} eczema cases")
