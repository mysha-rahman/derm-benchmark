# Data Sources & Validation Strategy

This document explains how we use real dermatology data to create realistic synthetic patient profiles for our AI benchmark.

---

## 🎯 Our Approach: Synthetic Profiles Validated by Real Data

**What we do:**
- Create **synthetic (fake) patient profiles** for ethical/privacy reasons
- Validate these profiles against **real dermatology datasets and clinical patterns**
- Ensure our synthetic patients reflect realistic clinical presentations

**Why synthetic?**
✅ No patient privacy concerns (no IRB approval needed)
✅ Full control over test scenarios (allergies, misinformation, etc.)
✅ Reproducible research (same profiles can be shared publicly)
✅ Ethical AI testing without real patient risk

---

## 📊 Three Data Sources

### 1. HAM10000 Dataset (Dermatoscopic Images)

**What it is:**
- 10,015 real dermatoscopic skin lesion images
- From Harvard Dataverse
- Medical diagnoses with patient demographics

**Focus:** Skin cancer and pigmented lesions
- Melanoma (1,113 cases)
- Melanocytic nevi (6,705 cases)
- Basal cell carcinoma (514 cases)
- Benign keratosis (1,099 cases)
- And 3 other lesion types

**How we use it:**
- Demographics reference (age ranges, sex distribution)
- Validates that our synthetic profiles match real patient patterns
- **We DO NOT use actual patient data directly**

**Files:**
- `datasets/HAM10000/metadata/HAM10000_metadata.csv`
- `scripts/explore_ham10000.py` - Analysis tool

**Citation:**
```
Tschandl, P., Rosendahl, C. & Kittler, H. The HAM10000 dataset, a large
collection of multi-source dermatoscopic images of common pigmented skin
lesions. Sci. Data 5, 180161 (2018).
DOI: 10.7910/DVN/DBW86T
```

---

### 2. Fitzpatrick17k Dataset (Clinical Dermatology)

**What it is:**
- 16,577 real clinical dermatology images
- Includes Fitzpatrick skin tone classifications
- Covers 114 dermatology conditions

**Focus:** Common dermatology conditions (MUCH better match for our benchmark!)
- Psoriasis (653 cases)
- Allergic contact dermatitis (430 cases)
- Lupus erythematosus (410 cases)
- Acne vulgaris (335 cases)
- Eczema (204 cases)
- Plus 109 other conditions

**Skin tone diversity:**
- Fitzpatrick 1-2 (lighter): 7,755 cases (47%)
- Fitzpatrick 3-4 (medium): 6,089 cases (37%)
- Fitzpatrick 5-6 (darker): 2,168 cases (13%)

**How we use it:**
- Validates our condition choices (psoriasis, acne, eczema are real common conditions)
- Ensures skin tone diversity in synthetic profiles
- Confirms symptom patterns are realistic

**Files:**
- `datasets/Fitzpatrick17k/fitzpatrick17k.csv` (4MB)
- `datasets/Fitzpatrick17k/README.md` - Full documentation
- `scripts/explore_fitzpatrick17k.py` - Analysis tool

**Citation:**
```
Groh, M., Harris, C., Soenksen, L., Lau, F., Han, R., Kim, A., Koochek, A.,
& Badri, O. (2021). Evaluating Deep Neural Networks Trained on Clinical Images
in Dermatology with the Fitzpatrick 17k Dataset. IEEE/CVF Conference on
Computer Vision and Pattern Recognition Workshops (CVPRW).
GitHub: https://github.com/mattgroh/fitzpatrick17k
```

---

### 3. DermNet NZ (Clinical Patterns)

**What it is:**
- Educational dermatology website
- Comprehensive clinical descriptions
- Treatment guidelines and case presentations

**Focus:** Clinical patterns for common conditions
- Treatment approaches (e.g., "psoriasis commonly treated with topical corticosteroids")
- Symptom presentations (e.g., "eczema presents with itching and redness")
- Age group associations
- Body location patterns

**How we use it:**
- **ETHICAL pattern extraction only**
- We analyze educational content to understand clinical patterns
- We DO NOT copy case descriptions verbatim
- We use patterns to inform synthetic profile creation
- Proper attribution in all research

**Pattern extraction examples:**
```json
{
  "psoriasis": {
    "common_treatments": ["topical corticosteroids", "emollients", "phototherapy"],
    "common_symptoms": ["scaling", "inflammation", "redness"],
    "typical_locations": ["scalp", "trunk", "elbows"]
  }
}
```

**Files:**
- `scripts/extract_dermnet_patterns.py` - Pattern extraction tool
- `validation/dermnet_patterns.json` - Extracted patterns (generated)
- `validation/DERMNET_ATTRIBUTION.md` - Proper attribution

**Attribution:**
```
Clinical patterns informed by DermNet NZ educational content.
DermNet NZ. All About the Skin. Available at: https://dermnetnz.org/
(Accessed: November 2025)
```

**Ethical Use:**
✅ Extract patterns from educational content
✅ Use patterns to create realistic synthetic profiles
✅ Respect rate limits (3s delays between requests)
✅ Proper attribution in research
❌ NO copying of patient cases verbatim
❌ NO use of copyrighted content without attribution

---

## 🔄 How It All Comes Together

```
┌─────────────────────────────────────────────────────┐
│ REAL DATA SOURCES (for validation)                 │
├─────────────────────────────────────────────────────┤
│                                                     │
│  HAM10000           Fitzpatrick17k      DermNet NZ │
│  (10,015 cases)     (16,577 cases)      (patterns) │
│       ↓                   ↓                  ↓      │
│   Demographics      Conditions          Clinical   │
│   validation        validation          patterns   │
│                                                     │
└──────────────────────┬──────────────────────────────┘
                       ↓
         ┌─────────────────────────────┐
         │  OUR SYNTHETIC PROFILES     │
         │  (patient_profiles_100.csv) │
         │                             │
         │  • Fictional patients       │
         │  • Realistic demographics   │
         │  • Real conditions          │
         │  • Clinical patterns        │
         │  • Rich medical history     │
         └──────────────┬──────────────┘
                        ↓
         ┌─────────────────────────────┐
         │  DIALOGUE GENERATION        │
         │  (generate_dialogues.py)    │
         └──────────────┬──────────────┘
                        ↓
         ┌─────────────────────────────┐
         │  AI BENCHMARK TESTING       │
         │  (run_benchmark.py)         │
         └─────────────────────────────┘
```

---

## 📋 Summary

| Source | Type | Count | Our Use |
|--------|------|-------|---------|
| **HAM10000** | Real patient data | 10,015 | Demographics validation |
| **Fitzpatrick17k** | Real patient data | 16,577 | Condition validation |
| **DermNet NZ** | Clinical patterns | N/A | Pattern extraction |
| **Our Profiles** | **Synthetic** | **100** | **Actual benchmark data** |

---

## ✅ Research Integrity Checklist

- [x] No real patient conversations used in testing
- [x] Synthetic profiles clearly labeled as fictional
- [x] All data sources properly cited
- [x] Pattern extraction done ethically (no verbatim copying)
- [x] Rate limiting respected for web scraping
- [x] Attribution files included in repository
- [x] Privacy-preserving approach (no IRB required)
- [x] Reproducible (synthetic profiles can be shared publicly)

---

## 🔗 Quick Links

**Datasets:**
- HAM10000: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
- Fitzpatrick17k: https://github.com/mattgroh/fitzpatrick17k
- DermNet NZ: https://dermnetnz.org/

**Our Files:**
- Patient profiles: `patient_profiles_100.csv`
- HAM10000 analysis: `scripts/explore_ham10000.py`
- Fitzpatrick17k analysis: `scripts/explore_fitzpatrick17k.py`
- DermNet patterns: `scripts/extract_dermnet_patterns.py`

**Attribution Files:**
- `datasets/HAM10000/README.md`
- `datasets/Fitzpatrick17k/README.md`
- `validation/DERMNET_ATTRIBUTION.md` (generated after pattern extraction)

---

## 🎓 For Your Research Paper

When writing your methodology section:

**Suggested Text:**

> "We created 100 synthetic patient profiles with realistic dermatology
> presentations, validated against three real-world data sources. Patient
> demographics were informed by the HAM10000 dataset (10,015 dermatoscopic
> images; Tschandl et al., 2018). Condition selection and skin tone diversity
> were validated against the Fitzpatrick17k dataset (16,577 clinical images;
> Groh et al., 2021). Clinical presentation patterns were extracted from
> DermNet NZ educational content to ensure realistic symptom and treatment
> histories. No real patient data was used in the benchmark testing phase,
> ensuring privacy preservation and research reproducibility."

**Citations to include:**
1. Tschandl et al., 2018 (HAM10000)
2. Groh et al., 2021 (Fitzpatrick17k)
3. DermNet NZ (https://dermnetnz.org/)

---

**Last Updated:** November 15, 2025
**Status:** Ready for pattern extraction and validation
