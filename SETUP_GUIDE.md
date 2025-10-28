# Dermatology LLM Benchmark - Setup Guide

**Author**: Mysha Rahman  
**Last Updated**: October 22, 2025  
**Team**: Hanim Syed, Syarifah Syed, Mysha Rahman

---

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [API Configuration](#api-configuration)
4. [Running Tests](#running-tests)
5. [Project Structure](#project-structure)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### System Requirements
- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **Storage**: ~2GB for HAM10000 dataset
- **Internet**: Required for API calls

### Required Accounts
1. **OpenAI** (GPT-4 access)
   - Sign up: https://platform.openai.com/signup
   - Billing required (~$20-30 for this project)
   
2. **Anthropic** (Claude access)
   - Sign up: https://console.anthropic.com/
   - Billing required (~$5-10 for this project)
   
3. **Google AI** (Gemini access)
   - Sign up: https://makersuite.google.com/
   - Free tier available (sufficient for testing)

---

## Initial Setup

### 1. Clone Repository

```bash
git clone https://github.com/mysha-rahman/derm-benchmark.git
cd derm-benchmark
```

### 2. Create Virtual Environment

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Create `requirements.txt` if needed:**
```txt
requests==2.31.0
pandas==2.1.0
numpy==1.24.3
matplotlib==3.7.2
seaborn==0.12.2
pillow==10.0.0
python-dotenv==1.0.0
```

### 4. Download HAM10000 Dataset

1. Visit: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/DBW86T
2. Download both files:
   - `HAM10000_images_part_1.zip`
   - `HAM10000_images_part_2.zip`
   - `HAM10000_metadata.csv`
3. Extract to `datasets/HAM10000/images/`

**Folder structure:**
```
datasets/
└── HAM10000/
    ├── images/
    │   ├── ISIC_0024306.jpg
    │   ├── ISIC_0024307.jpg
    │   └── ... (10,015 images)
    └── metadata/
        └── HAM10000_metadata.csv
```

---

## API Configuration

### Method 1: Environment Variables (Recommended)

**On macOS/Linux:**
```bash
# Add to ~/.bashrc or ~/.zshrc
export OPENAI_API_KEY='sk-...'
export ANTHROPIC_API_KEY='sk-ant-...'
export GOOGLE_API_KEY='AIza...'

# Reload shell
source ~/.bashrc
```

**On Windows (PowerShell):**
```powershell
[System.Environment]::SetEnvironmentVariable('OPENAI_API_KEY', 'sk-...', 'User')
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-...', 'User')
[System.Environment]::SetEnvironmentVariable('GOOGLE_API_KEY', 'AIza...', 'User')
```

### Method 2: .env File

Create `.env` in project root:
```bash
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=AIza...
```

**Load in Python:**
```python
from dotenv import load_dotenv
load_dotenv()
```

### Verify API Keys

```bash
python test_llm_api.py
```

Expected output:
```
✅ OpenAI API Key
✅ Anthropic API Key
✅ Google API Key
```

---

## Running Tests

### 1. Test API Integration

```bash
python test_llm_api.py
```

This will:
- ✅ Check all API keys are present
- ✅ Test simple query on each model
- ✅ Test multi-turn conversation
- ✅ Generate cost estimates
- ✅ Save usage log to `api_usage_log.json`

### 2. Explore HAM10000 Dataset

```bash
python scripts/explore_ham10000.py
```

Output:
- Dataset statistics
- Diagnosis distribution chart
- Age/sex demographics

### 3. Validate Patient Profiles

```bash
python scripts/validate_gold_profiles.py
```

Checks:
- All required fields present
- Age ranges realistic
- Skin conditions match HAM10000
- No duplicate IDs

### 4. Test Dialogue Generation

```bash
python scripts/generate_dialogue_templates.py --sample 5
```

Generates 5 sample dialogues with different testing strategies.

---

## Project Structure

```
derm-benchmark/
│
├── datasets/
│   └── HAM10000/                  # Real medical data (local only)
│       ├── images/                # 10,015 dermatology images
│       └── metadata/              # Patient demographics
│
├── gold_profiles/                 # Synthetic patient database
│   ├── gold_profile_examples.csv  # Human-readable format
│   └── gold_profiles.jsonl        # Machine-readable format
│
├── dialogues/                     # Conversation templates
│   ├── dialogue_templates.jsonl   # Multi-turn conversations
│   └── misinformation_library.json # Curated myths
│
├── validation/                    # Scoring and evaluation
│   ├── scoring_rubric.md         # Evaluation criteria
│   └── results/                  # Test outputs
│
├── scripts/                       # Analysis and generation tools
│   ├── explore_ham10000.py       # Dataset exploration
│   ├── match_profiles_to_ham.py  # Validation against real data
│   ├── generate_dialogue_templates.py  # Dialogue automation
│   └── validate_gold_profiles.py # Profile quality checks
│
├── test_llm_api.py               # API integration (Mysha)
├── requirements.txt              # Python dependencies
├── .env                          # API keys (DO NOT COMMIT)
├── .gitignore                    # Files to ignore
├── README.md                     # Project overview
└── SETUP_GUIDE.md                # This file
```

---

## Troubleshooting

### API Key Issues

**Problem**: `❌ OpenAI API Key not found`

**Solution**:
1. Check environment variable: `echo $OPENAI_API_KEY`
2. Verify key format starts with `sk-`
3. Restart terminal after setting variables
4. Try `.env` file method instead

---

### Rate Limiting

**Problem**: `429 Too Many Requests`

**Solution**:
```python
# Add delay between API calls
import time
time.sleep(1)  # Wait 1 second between requests
```

Update in `test_llm_api.py`:
```python
def call_all(self, messages, delay=1.0):
    results = {}
    for model in ['gpt4', 'claude', 'gemini']:
        results[model] = getattr(self, f'call_{model}')(messages)
        time.sleep(delay)  # Prevent rate limiting
    return results
```

---

### Cost Overruns

**Problem**: API costs higher than expected

**Solutions**:
1. **Reduce max_tokens**: Lower from 500 to 200
2. **Use cheaper models for testing**: Gemini for initial tests
3. **Cache responses**: Save successful calls to avoid repeats
4. **Batch similar queries**: Group similar test cases

**Budget Monitoring:**
```python
client = LLMAPIClient()
# ... run tests ...
summary = client.get_usage_summary()
print(f"Current spend: ${summary['total_cost']:.2f}")
```

---

### Dataset Download Issues

**Problem**: HAM10000 download fails or is slow

**Solution**:
1. Use institution VPN if available (faster academic network)
2. Download in parts (one zip at a time)
3. Alternative mirror: Check dataverse for mirrors
4. Contact team if you need a USB copy

---

### Import Errors

**Problem**: `ModuleNotFoundError: No module named 'requests'`

**Solution**:
```bash
# Ensure virtual environment is activated
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Reinstall dependencies
pip install -r requirements.txt

# If still failing, install individually
pip install requests pandas numpy matplotlib
```

---

## Quick Reference: Common Commands

```bash
# Activate environment
source venv/bin/activate              # macOS/Linux
venv\Scripts\activate                 # Windows

# Run API tests
python test_llm_api.py

# Check dataset
python scripts/explore_ham10000.py

# Validate profiles
python scripts/validate_gold_profiles.py

# Generate dialogues
python scripts/generate_dialogue_templates.py

# View usage costs
cat api_usage_log.json | grep total_cost

# Update repository
git pull origin main
git add .
git commit -m "your message"
git push origin main
```

---

## Cost Estimates

Based on project scope (100 profiles, 100 dialogues, 6 turns each):

| Model | Cost per 1K tokens | Project Estimate |
|-------|-------------------|------------------|
| GPT-4 | $0.03 in / $0.06 out | ~$21.60 |
| Claude 3.5 Sonnet | $0.003 in / $0.015 out | ~$2.16 |
| Gemini Pro | $0.00025 in / $0.0005 out | ~$0.18 |
| **TOTAL** | | **~$24** |

**Recommendation**: Budget $30 with 20% buffer.

---

## Next Steps

✅ Complete setup checklist:
- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] HAM10000 dataset downloaded
- [ ] All 3 API keys configured
- [ ] `test_llm_api.py` runs successfully
- [ ] Usage log generated

Now ready for:
1. Creating patient profiles (Syarifah)
2. Building dialogue templates (Hanim)
3. Running benchmark tests (Mysha)

---

## Support

**Issues?** Contact team members:
- Mysha: API & technical setup
- Hanim: Dialogues & misinformation
- Syarifah: Profiles & validation

**GitHub Issues**: https://github.com/mysha-rahman/derm-benchmark/issues

---

Last updated: October 23, 2025