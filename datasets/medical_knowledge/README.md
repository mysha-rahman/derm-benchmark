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

The data from this file enhances:
- Patient profile generation (`generate_patient_profiles.py`)
- Dialogue templates (`generate_dialogues.py`)
- Scoring rubric validation (`auto_score.py`)
