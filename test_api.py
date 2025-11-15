#!/usr/bin/env python3
"""
Quick test to verify Google Gemini API is working correctly.
Run this to check your API key and connection before running the full benchmark.
"""

import os
import sys
from google import genai
from google.genai import types


def _extract_text(response):
    """
    Extract text from Gemini response, handling cases where response.text is None.
    Falls back to extracting from candidates[0].content.parts when needed.
    """
    # Try the simple case first
    if hasattr(response, 'text') and response.text:
        return response.text

    # Fall back to extracting from candidates
    if hasattr(response, 'candidates') and response.candidates:
        candidate = response.candidates[0]
        if hasattr(candidate, 'content') and candidate.content:
            if hasattr(candidate.content, 'parts') and candidate.content.parts:
                parts_text = []
                for part in candidate.content.parts:
                    if hasattr(part, 'text') and part.text:
                        parts_text.append(part.text)
                if parts_text:
                    return ''.join(parts_text)

    return None


def test_api():
    print("=" * 70)
    print("🔬 TESTING GOOGLE GEMINI API")
    print("=" * 70)
    print()

    # Check API key
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not set!")
        print("   Get your FREE API key at: https://makersuite.google.com/app/apikey")
        print("   Then set it:")
        print("   export GOOGLE_API_KEY='your-key-here'")
        return False

    print(f"✅ API Key found: {api_key[:15]}...")
    print()

    # Test connection
    print("🔄 Testing API connection...")
    try:
        client = genai.Client(
            api_key=api_key,
            http_options=types.HttpOptions(timeout=60000)  # 60 seconds
        )

        response = client.models.generate_content(
            model="models/gemini-2.5-flash",
            contents="Say 'Hello! API is working!' in one sentence.",
            config=types.GenerateContentConfig(
                temperature=0.7,
                max_output_tokens=50
            )
        )

        # Extract text (handles both response.text and candidates.parts)
        extracted_text = _extract_text(response)

        if extracted_text:
            print(f"✅ API Response: {extracted_text}")
            print()
            print("=" * 70)
            print("✅ SUCCESS! Your API is working correctly!")
            print("=" * 70)
            print()
            print("You can now run the benchmark:")
            print("  python run_benchmark.py --quick")
            return True
        else:
            print(f"❌ No text in response: {response}")
            return False

    except Exception as e:
        print(f"❌ API Error: {e}")
        print()
        print("Possible issues:")
        print("  1. Invalid API key")
        print("  2. API quota exceeded")
        print("  3. Network connection problem")
        print("  4. Gemini API service issue")
        print()
        print("Check API status: https://status.cloud.google.com/")
        return False


if __name__ == "__main__":
    success = test_api()
    sys.exit(0 if success else 1)
