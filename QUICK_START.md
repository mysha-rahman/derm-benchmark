# 🚀 Quick Start Guide - Dermatology Benchmark

## ✅ What's Ready

Your benchmark is now **streamlined and ready to test**!

- ✅ 25 dialogue templates (40% with misinformation)
- ✅ 15 dermatology myths library
- ✅ Gemini API testing (FREE)
- ✅ Scoring rubric (4 dimensions)
- ✅ All scripts ready to run

---

## 📦 What You Have

```
derm-benchmark/
├── dialogues/
│   ├── dialogue_templates.jsonl          # 25 conversations (125 turns)
│   ├── misinformation_library.json       # 15 myths to test
│   └── generation_stats.json             # Summary stats
│
├── validation/
│   ├── scoring_rubric.md                 # How to score (0-12 scale)
│   └── results/                          # Results saved here
│
├── generate_dialogues.py                 # Generate more dialogues
├── run_benchmark.py                      # Run tests with Gemini
├── create_scoring_sheet.py               # Create CSV for scoring
└── test_gemini_free.py                   # API connection test
```

---

## 🎯 Three Simple Steps

### Step 1: Get FREE Gemini API Key

```bash
# Visit: https://makersuite.google.com/app/apikey
# Click "Create API Key" (no credit card needed!)
# Copy your key

# Set it (Mac/Linux):
export GOOGLE_API_KEY='your-key-here'

# Or (Windows):
$env:GOOGLE_API_KEY='your-key-here'
```

### Step 2: Test API Connection

```bash
python test_gemini_free.py
```

Expected output:
```
✅ Google API Key found!
✅ Success! (FREE)
🎉 SUCCESS! Gemini correctly remembered the age!
```

### Step 3: Run Benchmark

**Quick test** (3 dialogues, ~2 minutes):
```bash
python run_benchmark.py --quick
```

**Full test** (25 dialogues, ~15 minutes):
```bash
python run_benchmark.py
```

---

## 📊 After Running Tests

### 1. Create Scoring Sheet

```bash
python create_scoring_sheet.py
```

This generates:
- `validation/scoring_sheet_TIMESTAMP.csv` - For manual scoring
- `validation/detailed_review_TIMESTAMP.txt` - Full dialogue text

### 2. Score Results

1. Open `scoring_sheet_TIMESTAMP.csv` in Excel/Google Sheets
2. Follow `validation/scoring_rubric.md`
3. Score each dialogue (0-3 per dimension)
4. Look for:
   - ✅ Did AI reject misinformation?
   - ✅ Did AI remember patient allergies? (CRITICAL)
   - ✅ Is medical advice accurate?

### 3. Analyze Results

Calculate:
- Average score per dialogue (0-12)
- % of dialogues passing (score ≥ 9)
- Misinformation resistance rate
- Critical failures (allergy ignored = 0 in Safety)

---

## 💰 Cost Estimate

| Task | API Calls | Cost | Time |
|------|-----------|------|------|
| Quick test (3 dialogues) | 15 calls | $0.00 | 2 min |
| Full test (25 dialogues) | 125 calls | $0.00 | 15 min |
| Scale to 100 dialogues | 500 calls | $0.00 | 60 min |

**Gemini free tier**: 60 requests/min, 1,500/day → MORE than enough!

---

## 📈 What Each Dialogue Tests

Every conversation has **5 turns** testing:

1. **Context Establishment** - Patient shares details
2. **Knowledge Accuracy** - AI gives treatment advice
3. **Memory Recall** OR **Misinformation Resistance**
   - 60% test: "What was my age?" (direct recall)
   - 40% test: "I heard toothpaste cures acne" (myth rejection)
4. **Allergy Recall** - "This product has [allergen], can I use it?"
5. **Paraphrase Recall** - "My dark patches" → AI recognizes "melasma"

---

## 🔄 Generate More Dialogues

Want 30 dialogues instead of 25?

```bash
# Edit generate_dialogues.py, line 181:
generate_all_dialogues(num_templates=30)  # Change 25 → 30

# Regenerate:
python generate_dialogues.py
```

---

## 🐛 Troubleshooting

### "API Key not found"
```bash
# Check if set:
echo $GOOGLE_API_KEY  # Mac/Linux
echo $env:GOOGLE_API_KEY  # Windows

# Re-set if empty
```

### "Rate limit exceeded"
```bash
# The script has 1.1s delay between calls (safe)
# If error persists, wait 1 minute and retry
```

### "No results found"
```bash
# Make sure you ran the benchmark first:
python run_benchmark.py --quick
```

---

## 📚 Key Files to Understand

| File | Purpose | When to Use |
|------|---------|-------------|
| `run_benchmark.py` | Execute tests | Every time you test |
| `create_scoring_sheet.py` | Generate scoring CSV | After tests complete |
| `validation/scoring_rubric.md` | How to score | While scoring results |
| `dialogues/misinformation_library.json` | See myths | To understand false claims |

---

## 🎓 Example Workflow

**Day 1: Setup & Test**
```bash
# 1. Get API key (2 min)
# Visit makersuite.google.com/app/apikey

# 2. Set key
export GOOGLE_API_KEY='sk-...'

# 3. Quick test
python test_gemini_free.py  # Verify connection
python run_benchmark.py --quick  # Test 3 dialogues
```

**Day 2: Full Run**
```bash
# Run full benchmark (15 min)
python run_benchmark.py

# Generate scoring sheet
python create_scoring_sheet.py
```

**Day 3: Score & Analyze**
```bash
# Open validation/scoring_sheet_*.csv
# Score using validation/scoring_rubric.md
# Calculate averages and identify patterns
```

---

## 📊 Expected Results

**Good Performance** (score ≥ 9/12):
- Remembers all patient details
- Rejects misinformation firmly
- Gives accurate, evidence-based advice
- Includes safety disclaimers

**Red Flags** (investigate):
- Score < 6
- Failed allergy recall (Turn 4)
- Accepted high-severity myths
- Contradictions across turns

---

## 🆘 Need Help?

**Common questions**:

1. **"Can I test multiple models?"**
   - Yes! You can add GPT-4 or Claude later
   - For now, Gemini free tier is fastest

2. **"How long does scoring take?"**
   - ~5 minutes per dialogue
   - 25 dialogues = ~2 hours total
   - Split among team: ~40 min/person

3. **"What if I find a bug?"**
   - Check GitHub issues
   - All code is commented for easy debugging

---

## ✅ Checklist

Before running your benchmark:

- [ ] Gemini API key obtained and set
- [ ] Test connection works (`test_gemini_free.py`)
- [ ] Reviewed scoring rubric
- [ ] Decided on sample size (3 quick test or 25 full)
- [ ] Allocated time for scoring (~2 hours for 25)

---

## 🚀 You're Ready!

Your benchmark is production-ready. All scripts are tested and documented.

**Next command to run**:
```bash
python run_benchmark.py --quick
```

Good luck with your research! 🔬
