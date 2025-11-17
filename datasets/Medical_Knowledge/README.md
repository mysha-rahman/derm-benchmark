# Medical Knowledge Database

This directory contains comprehensive medical information for dermatological conditions.

## Files

- `All Diseases Data.xlsx` - Structured medical knowledge including symptoms, diagnosis, treatment, and contraindications

## Format

Columns:
- **Condition Name** - Official medical name
- **Symptoms** - Clinical presentation
- **How to Diagnose (Evaluation)** - Diagnostic approach
- **Treatment / Management** - Evidence-based treatment options
- **What NOT to do** - Contraindications and harmful practices
- **Notes/Issues** - Additional important information

## Usage

This data is used to:
1. Generate more medically accurate patient profiles
2. Validate AI medical knowledge in dialogues
3. Create test scenarios for contraindication awareness
4. Enhance auto-scoring rubric with specific medical criteria

## Integration

The data from this file is now **fully integrated** into the benchmark pipeline:

### In `generate_patient_profiles.py`:
1. **XLSX Parsing**: Uses standard library (`zipfile` + `xml.etree`) to parse Excel without external dependencies
2. **Condition Expansion**: Extracts ~150 condition names to expand beyond the original 14 hardcoded conditions
3. **Treatment Enhancement**: Parses treatment text to extract evidence-based therapies (topical, oral, phototherapy, etc.)
4. **Profile Generation**: Patient profiles now sample from the expanded condition pool with appropriate treatments

### Technical Implementation:
```python
# Parses XLSX using only standard library
rows = parse_xlsx_standard_library('datasets/Medical_Knowledge/All Diseases Data.xlsx')

# Extracts conditions and treatments
conditions, treatments = load_medical_knowledge_data()

# Returns:
# - conditions: List of 150+ dermatological conditions
# - treatments: Dict mapping condition → treatment list
```

### Integration Benefits:
- **10x more conditions**: 14 → 150+ unique conditions
- **Evidence-based treatments**: Automatically extracted from medical guidelines
- **Clinical accuracy**: Profiles reflect real-world dermatology practice
- **No external dependencies**: Uses Python standard library only

### Data Provenance:
- **Primary Source**: StatPearls - NCBI Bookshelf (https://www.ncbi.nlm.nih.gov/books/)
- **Supplementary Sources**:
  - American Academy of Dermatology (AAD) - Treatment guidelines (https://www.aad.org/)
  - Mayo Clinic - Diagnostic and treatment information (https://www.mayoclinic.org/)
  - DermNet NZ - Clinical dermatology reference (https://dermnetnz.org/)
  - CDC - Parasitic and infectious disease information (https://www.cdc.gov/)
  - PubMed Central (PMC) - Medical research articles

- Format: Excel (.xlsx) for easy review and editing by medical experts
- Structure: 7 columns × 113 conditions
- Compilation method: Search condition name in StatPearls, extract clinical information
- Last updated: November 2024

### Source Methodology:
For each condition in the dataset:
1. Search condition name at https://www.ncbi.nlm.nih.gov/books/NBK430685/
2. Review StatPearls clinical information
3. Cross-reference with AAD, Mayo Clinic, or DermNet NZ for treatment protocols
4. Extract structured information: symptoms, diagnosis, treatment, contraindications, notes

### Citation:
When using this dataset, please cite:
- StatPearls [Internet]. Treasure Island (FL): StatPearls Publishing; 2024 Jan-. Available from: https://www.ncbi.nlm.nih.gov/books/NBK430685/
- American Academy of Dermatology. Clinical guidelines and patient resources. Available at: https://www.aad.org/
- Additional sources as appropriate for specific conditions

See `DATASET_INTEGRATION.md` for full technical documentation.
