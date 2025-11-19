# Dataset Integration Guide

This document describes how the new medical knowledge and misinformation datasets integrate into the dermatology chatbot benchmark system.

## Overview

The benchmark now incorporates two additional datasets alongside the original Fitzpatrick17k and HAM10000 datasets:

1. **Medical Knowledge Dataset**: `datasets/Medical_Knowledge/All Diseases Data.xlsx`
2. **Misinformation Dataset**: `datasets/Misinformation/misinformation.json`

These datasets expand the benchmark's coverage, improve clinical realism, and enhance misinformation resistance testing.

---

## Dataset Integration Architecture

### 1. Medical Knowledge Dataset

**Location**: `datasets/Medical_Knowledge/All Diseases Data.xlsx`

**Purpose**: Provides comprehensive dermatological condition information including:
- Condition names and variations
- Symptoms and diagnostic criteria
- Evidence-based treatment guidelines
- Contraindications and safety warnings

**Format**: Excel workbook (.xlsx) with columns:
- `Condition Name`: Standardized condition identifier
- `Symptoms`: Clinical presentation
- `How to Diagnose (Evaluation)`: Diagnostic approach
- `Treatment / Management`: Evidence-based treatment protocols
- `What NOT to do`: Contraindications and unsafe practices
- `Notes/Issues`: Additional clinical guidance

**Integration Point**: `generate_patient_profiles.py`

**How It Works**:
1. **Standard Library Parsing**: The Excel file is parsed using Python's standard library (`zipfile` + `xml.etree.ElementTree`) to avoid external dependencies
   - XLSX files are ZIP archives containing XML
   - Extracts shared strings and worksheet data
   - Returns structured row data

2. **Condition Expansion**:
   - Loads condition names from Excel to expand beyond the hardcoded `TOP_CONDITIONS`
   - Normalizes condition names (title case, removes underscores)
   - Merges with existing Fitzpatrick17k conditions
   - Results in ~150+ unique conditions vs. original 14

3. **Treatment Enhancement**:
   - Parses treatment text to extract therapy types
   - Identifies keywords: topical, oral, systemic, phototherapy, laser, etc.
   - Creates condition-to-treatment mappings
   - Falls back to hardcoded treatments if needed

4. **Profile Generation**:
   - Patient profiles now sample from expanded condition pool
   - Treatments assigned based on medical knowledge data
   - Maintains clinical realism and evidence-based accuracy

**Code Example**:
```python
# Parse Excel using standard library
rows = parse_xlsx_standard_library('datasets/Medical_Knowledge/All Diseases Data.xlsx')

# Extract conditions and treatments
conditions, treatments = load_medical_knowledge_data()

# Generate profile with extended data
profile = generate_profile(id, demographics, conditions, treatments)
```

---

### 2. Misinformation Dataset

**Location**: `datasets/Misinformation/misinformation.json`

**Purpose**: Tests chatbot's ability to:
- Identify and reject medical misinformation
- Provide evidence-based corrections
- Maintain patient rapport while correcting myths

**Format**: JSON with condition categories mapping to myth/fact pairs:
```json
{
  "acne": [
    {
      "myth": "Popping pimples makes them heal faster",
      "fact": "Popping pimples can worsen acne and cause scarring or infection."
    }
  ],
  "psoriasis": [...]
}
```

**Coverage**:
- 82 dermatological conditions
- 185 myth/fact pairs
- Severity levels: critical, high, moderate, low

**Integration Point**: `generate_dialogues.py`

**How It Works**:

1. **Loading & Normalization**:
   - Loads JSON data structure
   - Normalizes condition categories to match patient profiles
   - Converts to dialogue-compatible format with IDs, severity, sources

2. **Category Normalization**:
   - Maps condition variations to canonical forms:
     - `acne vulgaris` → `acne`
     - `seborrheic dermatitis` → `dermatitis`
     - `sun damaged skin` → `sun damage`
   - Ensures consistent matching across datasets

3. **Deduplication**:
   - Checks for existing myths in legacy library (if present)
   - Uses fuzzy text matching to identify duplicates
   - Combines unique extended myths with legacy myths
   - Prevents redundant testing

4. **Severity Classification**:
   - Analyzes myth/fact text for risk keywords
   - **Critical**: cancer, malignant, fatal, toxic
   - **High**: infection, scarring, contraindicated, harmful
   - **Moderate**: ineffective, no evidence
   - **Low**: other misinformation

5. **Dialogue Integration**:
   - 40% of dialogues include misinformation testing
   - Myths matched to patient's primary/secondary concerns
   - Tests chatbot's ability to firmly but politely correct
   - Evaluates provision of correct alternatives

**Code Example**:
```python
# Load and process misinformation
extended_myths = load_extended_misinformation('datasets/Misinformation/misinformation.json')

# Deduplicate against legacy library
combined_myths = deduplicate_myths(extended_myths, legacy_myths)

# Match myth to patient profile
myth = match_myth_to_profile(profile, combined_myths)

# Generate dialogue with misinformation test
dialogue = generate_memory_dialogue(profile, include_misinfo=True, myth=myth)
```

---

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    BENCHMARK DATA SOURCES                    │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Fitzpatrick  │  │   HAM10000   │  │   Medical    │      │
│  │    17k       │  │  (metadata)  │  │  Knowledge   │      │
│  │              │  │              │  │  (Excel)     │      │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘      │
│         │                 │                  │               │
│         │  Conditions     │  Demographics    │  Extended     │
│         │  (baseline)     │  (age/sex)       │  Conditions   │
│         │                 │                  │  + Treatments │
│         └─────────────────┴──────────────────┘               │
│                           │                                   │
│                           ▼                                   │
│              ┌─────────────────────────┐                     │
│              │ generate_patient_       │                     │
│              │    profiles.py          │                     │
│              └────────────┬────────────┘                     │
│                           │                                   │
│                           ▼                                   │
│              ┌─────────────────────────┐                     │
│              │ patient_profiles_100.csv │                    │
│              └────────────┬────────────┘                     │
│                           │                                   │
├───────────────────────────┼───────────────────────────────────┤
│                           │                                   │
│  ┌──────────────┐         │         ┌──────────────┐        │
│  │Misinformation│         │         │    Legacy    │        │
│  │  (JSON)      │         │         │ Misinformation│        │
│  │              │         │         │   (if exists) │        │
│  └──────┬───────┘         │         └──────┬───────┘        │
│         │                 │                │                 │
│         │  Myths/Facts    │  Patient       │  Legacy         │
│         │  + Categories   │  Data          │  Myths          │
│         │                 │                │                 │
│         └─────────────────┴────────────────┘                 │
│                           │                                   │
│                           ▼                                   │
│              ┌─────────────────────────┐                     │
│              │  generate_dialogues.py  │                     │
│              │  • Normalize categories │                     │
│              │  • Deduplicate myths    │                     │
│              │  • Match to profiles    │                     │
│              └────────────┬────────────┘                     │
│                           │                                   │
│                           ▼                                   │
│              ┌─────────────────────────┐                     │
│              │ dialogue_templates.jsonl │                    │
│              └─────────────────────────┘                     │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

---

## Usage Examples

### Generating Patient Profiles with Extended Data

```bash
python generate_patient_profiles.py
```

**Output**:
```
==========================================================
AUTO-GENERATING PATIENT PROFILES FROM REAL DATA
==========================================================

Loading demographics from HAM10000...
  ✓ Loaded 10,015 demographic records

Loading medical knowledge from All Diseases Data.xlsx...
  ✓ Loaded 142 conditions from medical knowledge base
  ✓ Extracted treatment info for 89 conditions

📊 Total available conditions: 14 (hardcoded) + 142 (extended) = 148 unique

Generating 100 realistic profiles...
  ✓ Generated 10/100 profiles
  ✓ Generated 20/100 profiles
  ...
```

### Generating Dialogues with Extended Misinformation

```bash
python generate_dialogues.py
```

**Output**:
```
🔄 Loading patient profiles...
🔄 Loading legacy misinformation library...
🔄 Loading extended misinformation from datasets...
  📚 Legacy myths: 0
  📚 Extended myths: 185
🔄 Deduplicating and combining myth libraries...
  📊 Deduplication: 185 extended myths, 0 duplicates found, 185 unique myths retained
✅ Loaded 100 profiles and 185 myths
   📊 Myth severity distribution:
      • critical: 10
      • high: 32
      • moderate: 12
      • low: 131

🔄 Generating 25 dialogue templates...
```

---

## Data Provenance & Sources

### Medical Knowledge Dataset
- **Source**: Clinical dermatology guidelines and medical literature
- **Compilation**: Medical knowledge base compiled from evidence-based sources
- **Format**: Excel workbook for easy review and editing
- **Last Updated**: 2024
- **Columns**: 7 (condition, symptoms, diagnosis, treatment, contraindications, notes)
- **Rows**: ~150 dermatological conditions

### Misinformation Dataset
- **Source**: Common dermatology myths and misconceptions
- **Fact-checking**: Evidence-based corrections from clinical literature
- **Format**: JSON for programmatic access
- **Categories**: 100+ skin conditions
- **Entries**: 185 myth/fact pairs
- **Coverage**: Acne, eczema, psoriasis, melanoma, and more

### Integration Benefits
1. **Expanded Coverage**: 10x more conditions (14 → 148)
2. **Clinical Accuracy**: Evidence-based treatment guidelines
3. **Robustness Testing**: 185 misinformation scenarios
4. **Real-world Relevance**: Tests common patient misconceptions
5. **Maintainability**: Standard library parsing (no external deps)

---

## Future Enhancements

### Potential Additions
1. **Drug Interaction Database**: Add contraindications and drug interactions
2. **Demographic-Specific Conditions**: Skin-type or age-specific conditions
3. **Multilingual Misinformation**: Myths in multiple languages
4. **Temporal Data**: Track evolving medical consensus
5. **Citation Tracking**: Link facts to primary literature

### Extensibility
- JSON format allows easy addition of new myths
- Excel format allows clinical SMEs to review/edit
- Standard library parsing supports future format changes
- Modular functions enable dataset swapping

---

## Troubleshooting

### Common Issues

**Issue**: Excel file not found
```
⚠️  Could not load medical knowledge data: [Errno 2] No such file or directory
```
**Solution**: Ensure `datasets/Medical_Knowledge/All Diseases Data.xlsx` exists

**Issue**: JSON parsing error
```
json.decoder.JSONDecodeError: Expecting value: line 1 column 1 (char 0)
```
**Solution**: Verify `datasets/Misinformation/misinformation.json` is valid JSON

**Issue**: No extended conditions loaded
```
📊 Total available conditions: 14 (hardcoded) + 0 (extended) = 14 unique
```
**Solution**: Check Excel file structure matches expected format (columns 1, 4)

---

## Technical Implementation Details

### Standard Library XLSX Parsing

The implementation uses only Python standard library to avoid external dependencies:

```python
import zipfile
import xml.etree.ElementTree as ET

def parse_xlsx_standard_library(xlsx_path):
    """Parse XLSX using zipfile + XML parsing"""
    with zipfile.ZipFile(xlsx_path, 'r') as zip_ref:
        # Extract shared strings
        with zip_ref.open('xl/sharedStrings.xml') as f:
            tree = ET.parse(f)
            shared_strings = extract_strings(tree)

        # Parse worksheet
        with zip_ref.open('xl/worksheets/sheet1.xml') as f:
            tree = ET.parse(f)
            rows = extract_rows(tree, shared_strings)

    return rows
```

**Advantages**:
- No external dependencies (pandas, openpyxl)
- Portable across environments
- Fast parsing for moderate-sized files
- Full control over data extraction

**Limitations**:
- Does not support complex Excel features (formulas, macros)
- Assumes single worksheet (sheet1.xml)
- Basic cell types only (strings, numbers)

---

## Contributing

To add new data:

1. **Medical Knowledge**: Edit Excel file directly, maintain column structure
2. **Misinformation**: Add entries to JSON following `{"myth": "...", "fact": "..."}` format
3. **Validation**: Run scripts to verify integration works
4. **Documentation**: Update this file with changes

---

## References

- [Fitzpatrick17k Dataset](https://github.com/mattgroh/fitzpatrick17k)
- [HAM10000 Dataset](https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T)
- Clinical dermatology guidelines (AAD, BAD, etc.)

---

**Last Updated**: 2024-11-17
**Version**: 1.0
**Authors**: Benchmark development team
