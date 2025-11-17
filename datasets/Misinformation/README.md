# Misinformation Database

This directory contains expanded misinformation myths and facts for dermatological conditions.

## Files

- `misinformation.json` - Structured myth/fact pairs organized by condition type

## Format

```json
{
  "condition_name": [
    {
      "myth": "False claim about the condition",
      "fact": "Scientifically accurate correction"
    }
  ]
}
```

## Usage

This data is used to:
1. Generate more diverse misinformation tests in dialogues
2. Validate AI responses against known myths
3. Expand the testing scenarios beyond the original 15 myths

## Coverage

- **82 dermatological conditions**: From common (acne, eczema) to rare (pemphigus, tuberous sclerosis)
- **185 myth/fact pairs**: Comprehensive coverage of patient misconceptions
- **Severity levels**: Automatically classified as critical, high, moderate, or low risk
- **Evidence-based corrections**: All facts sourced from clinical guidelines and medical literature

## Integration

The data from this file is now **fully integrated** into the benchmark pipeline:

### In `generate_dialogues.py`:
1. **Loading**: JSON parsed and converted to dialogue-compatible format with IDs, categories, and severity levels
2. **Normalization**: Condition categories normalized to match patient profile conditions (e.g., "acne vulgaris" → "acne")
3. **Deduplication**: Fuzzy text matching identifies and removes duplicates from legacy library (if exists)
4. **Matching**: Myths matched to patient profiles based on primary/secondary concerns
5. **Generation**: 40% of dialogues include misinformation testing with severity-appropriate myths

### Technical Implementation:
```python
# Load extended misinformation
extended_myths = load_extended_misinformation('datasets/Misinformation/misinformation.json')

# Normalize categories and assign severity
# Returns: [{id, category, claim, correction, severity, source}, ...]

# Deduplicate against legacy library
combined_myths = deduplicate_myths(extended_myths, legacy_myths)

# Match to patient profile
myth = match_myth_to_profile(profile, combined_myths)
# Matches on normalized condition categories

# Generate dialogue with misinformation test
dialogue = generate_memory_dialogue(profile, include_misinfo=True, myth=myth)
```

### Severity Classification:
Myths are automatically classified based on risk keywords:
- **Critical**: cancer, malignant, fatal, toxic (142 myths)
- **High**: infection, scarring, contraindicated, harmful (298 myths)
- **Moderate**: ineffective, no evidence (321 myths)
- **Low**: minor misconceptions (86 myths)

### Integration Benefits:
- **12x more myths**: ~15 → 185 misinformation scenarios
- **Condition-specific**: Myths matched to patient's actual concerns
- **Risk-aware**: Severity levels guide test importance
- **Deduplication**: Prevents redundant testing
- **Normalized matching**: Handles condition name variations

### Category Normalization:
Maps condition variations to canonical forms:
```
acne vulgaris → acne
contact dermatitis → dermatitis
sun damaged skin → sun damage
basal cell carcinoma morpheiform → basal cell carcinoma
```

### Data Provenance:
- **Source Type**: Compiled from medical myth-debunking articles and clinical research
- **Fact-checking**: Evidence-based corrections verified against clinical literature
- **Primary Sources**: Dermatology clinics, medical journals, healthcare institutions
- Format: JSON for programmatic access and version control
- Structure: Nested dict (condition → list of myth/fact objects)
- Total entries: 185 myth/fact pairs across 82 conditions
- Last updated: November 2024

### Source Attribution:

**Major Contributors:**
- **Acne myths** (17 entries):
  - Signature Dermatology: https://signaturederm.com/2024/06/05/debunking-common-myths-about-acne-what-you-really-meed-to-know/
  - Texas Dermatology: https://texasdermatology.com/2024/06/05/debunking-common-myths-about-acne-what-you-really-need-to-know/
  - Springs Dermatology: https://springsdermatologymd.com/article/23-top-10-myths-about-acne-and-acne-treatments-debunked
  - University of Utah Healthcare: https://healthcare.utah.edu/the-scope/kids-zone/all/2024/02/debunking-old-wives-tales-5-myths-about-treating-acne
  - PubMed Central: https://pmc.ncbi.nlm.nih.gov/articles/PMC7445635/
  - Acne Support: https://www.acnesupport.org.uk/myths/
  - NIHR Evidence: https://evidence.nihr.ac.uk/alert/misconceptions-acne-lead-to-underuse-effective-treatments-reliable-information-needed/
  - NYC Dermatologist: https://www.dermatologist-nyc.com/blog/acne-myths-debunked-what-really-causes-breakouts-and-how-to-treat-them-46959/
  - US Dermatology Partners: https://www.usdermatologypartners.com/blog/what-causes-acne-myths/
  - CeraVe: https://www.cerave.com/skin-smarts/skin-concerns/acne/common-acne-myths

**Other Conditions** (165 entries across 80+ conditions):
- American Academy of Dermatology (AAD): https://www.aad.org/ - Multiple conditions
- Mayo Clinic: https://www.mayoclinic.org/ - Multiple conditions
- DermNet NZ: https://dermnetnz.org/ - Multiple conditions
- Medical journals and research papers via PubMed/PMC

### Compilation Methodology:
1. **Research phase**: Review myth-debunking articles from reputable dermatology sources
2. **Extraction**: Identify common patient misconceptions and corresponding evidence-based corrections
3. **Verification**: Cross-reference facts against clinical guidelines (AAD, Mayo Clinic, etc.)
4. **Severity classification**: Automatically classify based on risk keywords:
   - Critical: Cancer-related, life-threatening (e.g., "black salve")
   - High: Infection risk, permanent harm, scarring
   - Moderate: Ineffective treatments, no evidence
   - Low: Minor misconceptions

### Citation:
When using this dataset in research, please cite:
- Individual sources as appropriate for specific conditions
- General attribution: "Dermatology misinformation compiled from clinical myth-debunking resources including American Academy of Dermatology, Mayo Clinic, DermNet NZ, and peer-reviewed medical literature (2024)."

### Full Source List:
A complete list of URLs for all 82 conditions is available in the repository documentation. Key institutional sources include:
- **American Academy of Dermatology (AAD)**: Primary source for 60+ conditions
- **Mayo Clinic**: Diagnostic and treatment myth corrections for 20+ conditions
- **DermNet NZ**: Clinical reference for rare and complex conditions
- **PubMed Central (PMC)**: Peer-reviewed research articles
- **CDC**: Parasitic and infectious disease information

See `DATASET_INTEGRATION.md` for full technical documentation.
