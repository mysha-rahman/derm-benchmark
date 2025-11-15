# Troubleshooting Guide

## Common Errors and Solutions

### "No text in response" or "Unknown error"

**Cause**: Gemini's safety filters are blocking medical content. The response object exists but `response.text` is empty because content was filtered.

**This is now FIXED in the latest code!** Safety filters are disabled for educational medical content.

**Solution if you're still seeing this**:
1. **Pull latest code** with better error reporting:
   ```bash
   git pull origin your-branch-name
   ```

2. **Check the actual error** by looking at the console output for lines like:
   ```
   ❌ API Error: Content blocked by safety filter
   ❌ API Error: Response missing text attribute
   ```

3. **Try a different model** - Edit `run_benchmark.py` line 28:
   ```python
   # Try these models in order:
   self.model = model or "models/gemini-1.5-flash"  # More lenient
   # or
   self.model = model or "models/gemini-1.5-flash-latest"
   # or
   self.model = model or "models/gemini-pro"
   ```

4. **Check model availability**:
   ```bash
   python test_api.py
   ```

### Safety Filter Blocking Medical Content

**Pattern**: Some dialogues work, many fail on Turn 1
**Cause**: Gemini blocks certain medical terminology or patient descriptions

**Solutions**:

1. **Use Gemini 1.5 Flash instead of 2.5** (less restrictive):
   ```python
   # In run_benchmark.py line 28:
   self.model = model or "models/gemini-1.5-flash"
   ```

2. **Add safety settings** to bypass filters (use with caution):
   ```python
   # In run_benchmark.py, in the generate_content call:
   config=types.GenerateContentConfig(
       temperature=temperature,
       max_output_tokens=max_tokens,
       safety_settings=[
           types.SafetySetting(
               category='HARM_CATEGORY_MEDICAL',
               threshold='BLOCK_NONE'
           )
       ]
   )
   ```

3. **Rephrase prompts** - Some patient descriptions might trigger filters:
   - Avoid graphic descriptions
   - Use clinical terminology
   - Focus on symptoms rather than appearance

### High Failure Rate (>50% errors)

**Likely causes**:
1. **Rate limiting** - Hitting API quotas
2. **Content filtering** - Medical content being blocked
3. **Invalid API key** - Key expired or incorrect
4. **Network issues** - Timeouts or connection problems

**Debug steps**:

1. Test API connection:
   ```bash
   python test_api.py
   ```

2. Check quotas:
   - Free tier: 60 requests/minute, 1,500/day
   - If you've run multiple times, wait an hour or use a new API key

3. Run with just 1 dialogue to isolate:
   ```bash
   # Edit run_benchmark.py, change line 153:
   dialogues = dialogues[:1]  # Test just first dialogue
   ```

### Rate Limit Errors

**Error**: `429 Resource Exhausted` or `RESOURCE_EXHAUSTED`

**Cause**: Exceeded free tier limits
- 60 requests per minute
- 1,500 requests per day

**Solution**:
1. **Wait** - Quotas reset every minute/day
2. **Reduce load** - Test with fewer dialogues
3. **Get new API key** - Create another free key
4. **Upgrade** - Move to paid tier (if needed)

### Timeout Errors

**Error**: `Timeout` or `deadline exceeded`

**Causes**:
1. Network connection slow
2. API servers slow
3. Request too large

**Solutions**:
1. **Increase timeout** in `run_benchmark.py` line 18:
   ```python
   def __init__(self, api_key=None, model=None, timeout=600):  # 10 minutes
   ```

2. **Check internet** connection:
   ```bash
   ping google.com
   ```

3. **Reduce request size** - Lower max_tokens in line 32:
   ```python
   def chat(self, messages, temperature=0.7, max_tokens=300):  # Reduced from 500
   ```

### AttributeError: 'GenerateContentResponse' object has no attribute 'text'

**Cause**: Response blocked by safety filters or API returned unexpected structure

**Solution**:
1. Content was blocked - see "Safety Filter" section above
2. Check response structure by adding debug logging
3. Try different model (Gemini 1.5 Flash)

## Getting Help

1. **Enable debug mode** - Run with verbose errors:
   ```bash
   git pull  # Get latest error logging
   python run_benchmark.py --quick 2>&1 | tee debug.log
   ```

2. **Check API status**:
   - https://status.cloud.google.com/

3. **Verify setup**:
   ```bash
   python verify_setup.py
   ```

4. **Report issue** with:
   - Full error message
   - Output of `python test_api.py`
   - Number of times you've run benchmark today
   - Model you're using

## Quick Fixes Checklist

- [ ] Pulled latest code (`git pull`)
- [ ] API key is set (`echo $GOOGLE_API_KEY`)
- [ ] Tested API connection (`python test_api.py`)
- [ ] Not hitting rate limits (< 1,500 calls today)
- [ ] Using Gemini 1.5 Flash (more lenient)
- [ ] Internet connection working
- [ ] Tried with just 1-3 dialogues

## Still Stuck?

The most common issue is **content filtering**. Try:
1. Switch to Gemini 1.5 Flash
2. Test with just 1 dialogue
3. Check if that specific patient profile triggers filters
4. Modify patient descriptions to be less graphic
