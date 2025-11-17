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

## Integration

The data from this file is merged with `dialogues/misinformation_library.json` during dialogue generation to create more comprehensive testing scenarios.
