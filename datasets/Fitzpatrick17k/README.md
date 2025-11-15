# Fitzpatrick17k Dataset

## Overview

**Fitzpatrick17k** is a dermatology image dataset with **16,577 clinical images** across diverse skin tones, annotated with Fitzpatrick skin type classifications.

**Source**: [GitHub - mattgroh/fitzpatrick17k](https://github.com/mattgroh/fitzpatrick17k)

---

## Why This Dataset?

Unlike HAM10000 (which focuses on skin cancer/pigmented lesions), Fitzpatrick17k includes **common dermatology conditions** that align with our benchmark:

### ✅ Conditions Matching Our Benchmark
- **Psoriasis** (653 cases)
- **Acne vulgaris** (335 cases)
- **Eczema** (204 cases)
- **Allergic contact dermatitis** (430 cases)
- **Lichen planus** (491 cases)
- **Lupus erythematosus** (410 cases)

### ✅ Skin Tone Diversity
Fitzpatrick scale (1-6):
- **Type 1-2** (lighter tones): 7,755 cases
- **Type 3-4** (medium tones): 6,089 cases
- **Type 5-6** (darker tones): 2,168 cases

---

## Dataset Structure

**File**: `fitzpatrick17k.csv` (16,577 rows)

**Columns**:
- `md5hash` - Unique image identifier
- `fitzpatrick_scale` - Skin tone (1-6, -1 = unknown)
- `fitzpatrick_centaur` - Alternative skin tone annotation
- `label` - Dermatology condition (114 unique conditions)
- `nine_partition_label` - Grouped category (inflammatory, benign dermal, etc.)
- `three_partition_label` - High-level category (malignant, benign, non-neoplastic)
- `qc` - Quality control flag (optional)
- `url` - Image URL from DermAmin

---

## Top 20 Conditions

| Condition | Count |
|-----------|-------|
| Psoriasis | 653 |
| Squamous cell carcinoma | 581 |
| Lichen planus | 491 |
| Basal cell carcinoma | 468 |
| Allergic contact dermatitis | 430 |
| Lupus erythematosus | 410 |
| Neutrophilic dermatoses | 361 |
| Sarcoidosis | 349 |
| Photodermatoses | 348 |
| Folliculitis | 342 |
| Scabies | 339 |
| Acne vulgaris | 335 |
| Scleroderma | 309 |
| Pityriasis rubra pilaris | 278 |
| Melanoma | 261 |
| Nematode infection | 260 |
| Erythema multiforme | 236 |
| Granuloma annulare | 211 |
| Eczema | 204 |
| Drug eruption | 200 |

---

## How We Use It

This dataset **validates** our synthetic patient profiles by ensuring:
1. Conditions in our profiles match real-world dermatology cases
2. Age/demographics are realistic
3. Skin tone diversity is represented
4. Misinformation myths align with actual conditions patients experience

---

## Citation

If you use this dataset, cite:

```bibtex
@inproceedings{groh2021fitzpatrick17k,
  title={Evaluating Deep Neural Networks Trained on Clinical Images in Dermatology with the Fitzpatrick 17k Dataset},
  author={Groh, Matthew and Harris, Caleb and Soenksen, Luis and Lau, Felix and Han, Rachel and Kim, Aerin and Koochek, Arash and Badri, Omar},
  booktitle={Proceedings of the IEEE/CVF Conference on Computer Vision and Pattern Recognition},
  year={2021}
}
```

---

## License

Dataset is publicly available under the original terms from the authors.

**Images**: Sourced from DermAmin educational website (public domain for educational use)
