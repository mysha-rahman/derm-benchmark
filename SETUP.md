# Setup Instructions

## Quick Setup (3 steps)

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install:
- `google-genai` - Google Gemini API (NEW SDK)
- Other required packages

### 2. Get Your FREE API Key

1. Visit: https://makersuite.google.com/app/apikey
2. Click **"Create API Key"** (no credit card needed!)
3. Copy your API key (starts with `AIza...`)

### 3. Set Environment Variable

**Linux/Mac:**
```bash
export GOOGLE_API_KEY='your-api-key-here'
```

**Windows (PowerShell):**
```powershell
$env:GOOGLE_API_KEY='your-api-key-here'
```

**Windows (Command Prompt):**
```cmd
set GOOGLE_API_KEY=your-api-key-here
```

### Verify Setup

```bash
python run_benchmark.py --quick
```

Expected output:
```
✅ Gemini API key found!
✅ Loaded 25 dialogues
🚀 Running benchmark (3 dialogues)
```

## Troubleshooting

### "Missing GOOGLE_API_KEY environment variable"

Your API key is not set. Run:
```bash
echo $GOOGLE_API_KEY  # Linux/Mac
echo %GOOGLE_API_KEY%  # Windows
```

If empty, set it again following step 3 above.

### "ModuleNotFoundError: No module named 'google'"

Dependencies not installed. Run:
```bash
pip install -r requirements.txt
```

### API Timeout Errors

The benchmark now includes:
- **60-second timeout** (configurable)
- **Auto-retry with exponential backoff** (up to 3 attempts)
- **Smart retry detection** (only retries on network/timeout errors)

If you still get timeouts:
1. Check your internet connection
2. Increase timeout: Edit `run_benchmark.py:22` and change `timeout=60` to `timeout=120`
3. Check Gemini API status: https://status.cloud.google.com/

### Rate Limit Errors

The script already includes 1.1s delay between calls. If you still hit rate limits:
- Wait 1 minute and try again
- Gemini free tier: 60 requests/minute, 1,500/day

## Advanced Configuration

### Custom Timeout

Edit `run_benchmark.py`:
```python
client = GeminiFreeClient(timeout=120)  # 2 minutes
```

### Custom Retry Count

Edit the `chat()` call in `run_dialogue()`:
```python
ai_response = client.chat(conversation, max_retries=5)
```

### Different Model

Edit `run_benchmark.py:31`:
```python
self.model = model or "gemini-1.5-flash"  # or other Gemini models
```

## What's Fixed

### API Timeout Issues ✅
- Added 60-second timeout configuration
- API calls won't hang indefinitely

### Network Errors ✅
- Automatic retry with exponential backoff
- Retries: 2s → 4s → 8s delay
- Intelligent retry detection (only retries recoverable errors)

### Better Error Messages ✅
- Shows which attempt failed
- Displays retry countdown
- Clear error reporting

## Next Steps

Once setup is complete:
1. Run quick test: `python run_benchmark.py --quick`
2. Run full benchmark: `python run_benchmark.py`
3. Auto-score results: `python auto_score.py`
4. Generate scoring sheet: `python create_scoring_sheet.py`

## Need Help?

Check:
- [QUICK_START.md](QUICK_START.md) - Complete workflow guide
- [README.md](README.md) - Project overview
- [GitHub Issues](https://github.com/mysha-rahman/derm-benchmark/issues)
