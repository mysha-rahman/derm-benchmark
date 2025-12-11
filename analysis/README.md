# Analysis Scripts

This directory contains scripts for exploring datasets and extracting clinical patterns, as well as comprehensive benchmark results analysis.

---

## 📊 Benchmark Results & Visualizations

### Overall Performance: **93.3% (11.20/12)** - Grade A-

**Key Findings from 1,150 dialogues tested:**

| Dimension | Score | Performance |
|-----------|-------|-------------|
| Medical Correctness | 2.97/3 (99.1%) | ✅ A+ - Highly accurate |
| Memory Consistency | 2.94/3 (98.1%) | ✅ A+ - Excellent context |
| Misinformation Resistance | 2.98/3 (99.4%) | ✅ A+ - **96.9% perfect rejection** |
| Safety & Guidelines | 2.30/3 (76.6%) | ⚠️ C+ - Needs improvement |

### 🎨 Visualizations Generated

**5 comprehensive visualizations created:**

1. **benchmark_summary_infographic.png** - One-page executive summary with key metrics
2. **comprehensive_benchmark_analysis.png** - 15-panel detailed dashboard showing all dimensions
3. **safety_analysis_deep_dive.png** - Deep dive into weakest dimension (safety disclaimers)
4. **misinformation_resistance_analysis.png** - Analysis of strongest dimension (99.4% resistance)
5. **critical_failures_analysis.png** - Examination of 6 critical failure cases

### 📈 Key Insights

**Strengths:**
- 72.6% perfect scores (835/1,150 dialogues scored 12/12)
- Only 0.5% critical failures (6 dialogues)
- Novel finding: Performance improves when misinformation is present (+0.50 points)

**Priority Improvements:**
- Safety disclaimers: 19.3% missing "consult a doctor" warnings
- Target: Improve from 76.6% → 90%+ through prompt engineering

**Statistical Files:**
- `detailed_analysis_report.json` - Full statistical breakdown
- `summary_statistics.json` - Quick reference metrics

---

## 📊 Dataset Exploration Scripts

### `explore_ham10000.py`
Analyzes the HAM10000 dataset (10,015 dermatoscopic images).

**Usage:**
```bash
python analysis/explore_ham10000.py
```

**Output:**
- Dataset statistics
- Diagnosis distribution chart (`ham10000_diagnosis_distribution.png`)
- Demographics analysis

---

### `explore_fitzpatrick17k.py`
Analyzes the Fitzpatrick17k dataset (16,577 clinical dermatology images).

**Usage:**
```bash
python analysis/explore_fitzpatrick17k.py
```

**Requirements:**
- pandas
- matplotlib

**Output:**
- Condition distribution statistics
- Fitzpatrick skin tone analysis
- Visualization (`fitzpatrick17k_distribution.png`)

---

## 🔬 Clinical Pattern Extraction

### `extract_dermnet_patterns.py`

**Purpose:** Extracts clinical patterns from DermNet NZ educational content to inform synthetic patient profile creation.

**Ethical Use:**
- ✅ Extracts PATTERNS (e.g., "psoriasis commonly treated with topical corticosteroids")
- ✅ Used to make synthetic profiles more realistic
- ❌ Does NOT copy patient data or case descriptions verbatim
- ✅ Properly attributes DermNet NZ in research

**Usage:**
```bash
python analysis/extract_dermnet_patterns.py
```

**Requirements:**
- requests
- beautifulsoup4

**Install dependencies:**
```bash
pip install requests beautifulsoup4
```

**What it does:**
1. Analyzes DermNet NZ topic pages for conditions matching our benchmark
2. Extracts patterns for:
   - Common treatments (e.g., topical corticosteroids, retinoids)
   - Typical symptoms (e.g., itching, redness, scaling)
   - Age group associations
   - Body location patterns
3. Saves results to `validation/dermnet_patterns.json`
4. Creates attribution file `validation/DERMNET_ATTRIBUTION.md`

**Rate Limiting:**
- 3-second delay between requests (respectful to DermNet servers)
- Analyzes ~8 conditions by default
- Takes approximately 30-60 seconds to complete

**Output Files:**
- `validation/dermnet_patterns.json` - Extracted clinical patterns
- `validation/DERMNET_ATTRIBUTION.md` - Proper attribution text

**Example Pattern:**
```json
{
  "psoriasis": {
    "count": 1,
    "common_treatments": {
      "topical corticosteroids": 1,
      "emollients": 1,
      "phototherapy": 1
    },
    "common_symptoms": {
      "scaling": 1,
      "inflammation": 1,
      "redness": 1
    },
    "age_patterns": {
      "adults": 1
    },
    "typical_locations": {
      "scalp": 1,
      "trunk": 1
    }
  }
}
```

**Using Patterns in Synthetic Profiles:**

The extracted patterns help ensure our synthetic patient profiles reflect real clinical presentations:

```python
# Example: Use patterns to create realistic synthetic patient
if patient['condition'] == 'psoriasis':
    # Pattern shows psoriasis commonly uses topical corticosteroids
    patient['past_treatments'] = "Topical corticosteroids, emollients"
    patient['symptoms'] = "Red, scaly patches"
    patient['typical_location'] = "Scalp and trunk"
```

**Attribution Required:**

When publishing research using these patterns, include:

```
Clinical patterns informed by DermNet NZ educational content.
DermNet NZ. All About the Skin. Available at: https://dermnetnz.org/
(Accessed: November 2025)
```

---

## 📋 Notes

### Installation of Dependencies

If you need to run the exploration scripts:

```bash
pip install pandas matplotlib seaborn requests beautifulsoup4
```

### Ethical Considerations

1. **DermNet NZ Pattern Extraction:**
   - We extract patterns to understand clinical presentations
   - We do NOT copy content verbatim
   - We respect rate limits (3s delays)
   - We properly attribute the source

2. **Dataset Usage:**
   - HAM10000 and Fitzpatrick17k are used under their respective licenses
   - All datasets are properly cited in our research

3. **Synthetic Profiles:**
   - We use patterns to CREATE synthetic profiles
   - No real patient data is copied
   - All profiles are fictional but clinically realistic

---

## 🔗 Resources

- **DermNet NZ**: https://dermnetnz.org/
- **HAM10000**: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
- **Fitzpatrick17k**: https://github.com/mattgroh/fitzpatrick17k
