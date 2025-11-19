# Main Workflow Scripts

This directory contains the core scripts for running the benchmark workflow.

---

## 🚀 Main Workflow

### 1. `run_benchmark.py`
**Purpose:** Run the dermatology chatbot benchmark with Gemini 2.5 Flash.

**Usage:**
```bash
# Quick test (3 dialogues)
python scripts/run_benchmark.py --quick

# Small test (10 dialogues)
python scripts/run_benchmark.py 10

# Full benchmark (1,500 dialogues)
python scripts/run_benchmark.py
```

**What it does:**
- Loads dialogue templates from `dialogues/dialogue_templates.jsonl`
- Runs conversations with Gemini 2.5 Flash API
- Saves results to `validation/results/gemini_results_TIMESTAMP.json`

**Requirements:**
- `GOOGLE_API_KEY` environment variable
- Valid Gemini API key (get free at https://makersuite.google.com/app/apikey)

**Output:**
- JSON file with all conversation results
- Metadata (model, timestamp, number of dialogues, cost)
- Individual dialogue transcripts with AI responses

---

### 2. `auto_score.py`
**Purpose:** Automatically score benchmark results using LLM-as-judge pattern.

**Usage:**
```bash
# Auto-score latest results
python scripts/auto_score.py

# Auto-score specific results file
python scripts/auto_score.py validation/results/gemini_results_20251119.json

# Retry only failed dialogues
python scripts/auto_score.py --retry
```

**What it does:**
- Loads benchmark results
- Uses Gemini as judge to score each conversation (0-12 scale)
- Scores 4 dimensions: Correctness, Consistency, Misinformation Resistance, Safety
- Flags dialogues needing manual review
- Saves scored results to `validation/results/scored_results_TIMESTAMP.json`

**Features:**
- ✅ Structured JSON output with confidence scores
- ✅ Few-shot calibration for consistent scoring
- ✅ Dynamic rate limiting (adapts to API health)
- ✅ Broadened flagging (catches borderline cases)
- ✅ Auto-awards misinformation resistance when N/A

**Configuration (Optional):**
```bash
export GEMINI_BASE_DELAY=3.0   # Normal delay (default: 3.0s)
export GEMINI_MIN_DELAY=1.0    # Fast when healthy (default: 1.0s)
export GEMINI_MAX_DELAY=10.0   # Slow during errors (default: 10.0s)
```

**Output:**
- Scored results JSON
- Summary statistics
- Flagging breakdown
- Performance analytics by test type

---

### 3. `create_scoring_sheet.py`
**Purpose:** Generate easy-to-read scoring sheets from auto-scored results.

**Usage:**
```bash
# Generate sheets from latest scored results
python scripts/create_scoring_sheet.py

# Generate sheets from specific file
python scripts/create_scoring_sheet.py validation/results/scored_results_20251119.json
```

**What it does:**
- Loads auto-scored results
- Creates 4 output files for different review purposes:
  1. **EASY_READ_SUMMARY** - Plain language overview
  2. **scoring_sheet.csv** - Excel-ready spreadsheet
  3. **flagged_only_review.txt** - Only problematic conversations
  4. **detailed_review_ALL.txt** - Complete record

**Output Files:**
- `validation/EASY_READ_SUMMARY_TIMESTAMP.txt`
- `validation/scoring_sheet_TIMESTAMP.csv`
- `validation/flagged_only_review_TIMESTAMP.txt`
- `validation/detailed_review_ALL_TIMESTAMP.txt`

---

## 🛠️ Utility Scripts

### `verify_setup.py`
**Purpose:** Verify that your environment is set up correctly.

**Usage:**
```bash
python scripts/verify_setup.py
```

**What it checks:**
- Python version (3.8+)
- Required packages installed
- Dataset files present
- Dialogue templates exist
- API key configured

---

### `test_api.py`
**Purpose:** Test Gemini API connection and functionality.

**Usage:**
```bash
python scripts/test_api.py
```

**What it does:**
- Tests API key validity
- Sends a simple test query
- Verifies response parsing
- Shows sample output

---

## 📖 Complete Workflow Example

```bash
# 1. Verify setup
python scripts/verify_setup.py

# 2. Run quick benchmark test (2 min)
python scripts/run_benchmark.py --quick

# 3. Auto-score results (1 min)
python scripts/auto_score.py

# 4. Generate scoring sheets
python scripts/create_scoring_sheet.py

# 5. Review flagged conversations
#    Open: validation/flagged_only_review_TIMESTAMP.txt
#    Review: validation/scoring_sheet_TIMESTAMP.csv
```

---

## 💡 Tips

**For Class Demo:**
1. Use `--quick` mode for fast demonstration (3 dialogues, ~2 min)
2. Show the EASY_READ_SUMMARY for plain language results
3. Open CSV in Excel/Google Sheets for visual review
4. Focus on flagged_only_review to show the hybrid approach

**Time Estimates:**
- Quick test (3 dialogues): ~5 minutes total
- Small test (10 dialogues): ~15 minutes total
- Full benchmark (1,500 dialogues): ~4.5 hours total

**Cost Estimates (Gemini free tier):**
- Quick test: $0.00 (FREE)
- Small test: $0.00 (FREE)
- Full benchmark: ~$1.26 (paid tier required)

---

## 📚 Related Documentation

- [Quick Start Guide](../docs/QUICK_START.md) - Step-by-step setup
- [Main README](../README.md) - Project overview
- [Troubleshooting](../docs/TROUBLESHOOTING.md) - Common issues
