"""
Explore HAM10000 Dataset
"""
import pandas as pd
from pathlib import Path
import matplotlib.pyplot as plt
from PIL import Image

# Load the metadata
metadata_path = Path("datasets/HAM10000/metadata/HAM10000_metadata.csv")
df = pd.read_csv(metadata_path)

print("=== HAM10000 Dataset Overview ===\n")
print(f"Total images: {len(df)}")
print(f"Total unique lesions: {df['lesion_id'].nunique()}")
print(f"\nColumns: {list(df.columns)}")

# Show first few rows
print("\n=== Sample Data ===")
print(df.head())

# Diagnosis distribution
print("\n=== Diagnosis Distribution ===")
print(df['dx'].value_counts())

# Age distribution
print("\n=== Age Statistics ===")
print(df['age'].describe())

# Gender distribution
print("\n=== Gender Distribution ===")
print(df['sex'].value_counts())

# Localization (body part)
print("\n=== Body Location Distribution ===")
print(df['localization'].value_counts())

# Verification method
print("\n=== Diagnosis Verification Method ===")
print(df['dx_type'].value_counts())

# Visualize diagnosis distribution
plt.figure(figsize=(10, 6))
df['dx'].value_counts().plot(kind='bar')
plt.title('HAM10000 Diagnosis Distribution')
plt.xlabel('Diagnosis')
plt.ylabel('Count')
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig('ham10000_diagnosis_distribution.png')
print("\n✓ Saved diagnosis distribution chart")

# Show a sample image
print("\n=== Viewing Sample Image ===")
sample_image_id = df.iloc[0]['image_id']
image_path = Path(f"datasets/HAM10000/images/{sample_image_id}.jpg")
if image_path.exists():
    img = Image.open(image_path)
    print(f"Sample image: {sample_image_id}")
    print(f"Diagnosis: {df.iloc[0]['dx']}")
    print(f"Age: {df.iloc[0]['age']}, Sex: {df.iloc[0]['sex']}")
    print(f"Location: {df.iloc[0]['localization']}")
    img.show()