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
- Source: Common patient misconceptions and medical myths
- Fact-checking: Evidence-based corrections from clinical literature
- Format: JSON for programmatic access and version control
- Structure: Nested dict (condition → list of myth/fact objects)
- Last updated: 2024

See `DATASET_INTEGRATION.md` for full technical documentation.
