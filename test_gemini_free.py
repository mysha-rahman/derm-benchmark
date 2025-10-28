"""
Dermatology LLM Benchmark - FREE API Testing (Gemini Only)
Author: Mysha Rahman
Date: October 2025

This version uses ONLY Google Gemini Pro (FREE tier)
No credit card required for basic testing!
"""

import os
import json
import time
from datetime import datetime
from typing import List, Dict
import requests


class GeminiFreeClient:
    """Free LLM testing using only Google Gemini"""
    
    def __init__(self, api_key: str = None):
        """
        Initialize with Gemini API key (free!)
        
        Args:
            api_key: Google API key (get free at https://makersuite.google.com/app/apikey)
        """
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        self.usage_log = []
        
        if not self.api_key:
            print("\n⚠️  Google API Key not found!")
            print("Get a FREE key at: https://makersuite.google.com/app/apikey")
            print("\nThen set it:")
            print("  Windows: $env:GOOGLE_API_KEY='your-key'")
            print("  Mac/Linux: export GOOGLE_API_KEY='your-key'")
    
    def call_gemini(self, messages: List[Dict[str, str]], 
                   temperature: float = 0.7,
                   max_tokens: int = 500) -> Dict:
        """
        Call Google Gemini Pro API (FREE!)
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dict with 'response', 'model', 'tokens', 'cost' (always $0!)
        """
        if not self.api_key:
            return {'error': 'Google API key not found', 'model': 'gemini-pro'}
        
        try:
            # Convert messages to Gemini format
            gemini_messages = []
            for msg in messages:
                role = 'user' if msg['role'] in ['user', 'system'] else 'model'
                gemini_messages.append({
                    'role': role,
                    'parts': [{'text': msg['content']}]
                })
            
            payload = {
                'contents': gemini_messages,
                'generationConfig': {
                    'temperature': temperature,
                    'maxOutputTokens': max_tokens
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_key}",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            
            # Extract response text
            response_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Estimate tokens (Gemini doesn't always return counts)
            input_tokens = sum(len(msg['content'].split()) * 1.3 for msg in messages)
            output_tokens = len(response_text.split()) * 1.3
            
            result = {
                'model': 'gemini-pro (FREE)',
                'response': response_text,
                'tokens': {
                    'input': int(input_tokens),
                    'output': int(output_tokens),
                    'total': int(input_tokens + output_tokens)
                },
                'cost': 0.00,  # FREE!
                'latency': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_usage(result)
            return result
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Gemini API error: {str(e)}', 'model': 'gemini-pro'}
    
    def _log_usage(self, result: Dict):
        """Log API usage for tracking"""
        self.usage_log.append(result)
    
    def get_usage_summary(self) -> Dict:
        """Get summary of API usage"""
        summary = {
            'total_calls': len(self.usage_log),
            'total_tokens': 0,
            'total_cost': 0.00,  # Always free!
            'average_latency': 0
        }
        
        for entry in self.usage_log:
            if 'error' not in entry:
                summary['total_tokens'] += entry['tokens']['total']
                summary['average_latency'] += entry['latency']
        
        if summary['total_calls'] > 0:
            summary['average_latency'] /= summary['total_calls']
        
        return summary
    
    def save_usage_log(self, filepath: str = 'gemini_usage_log.json'):
        """Save usage log to file"""
        with open(filepath, 'w') as f:
            json.dump({
                'log': self.usage_log,
                'summary': self.get_usage_summary()
            }, f, indent=2)
        print(f"Usage log saved to {filepath}")


def test_dermatology_query():
    """Test with a real dermatology question"""
    print("=" * 60)
    print("Testing Gemini with Dermatology Question")
    print("=" * 60)
    
    client = GeminiFreeClient()
    
    if not client.api_key:
        print("\n❌ Cannot proceed without API key")
        print("Get yours FREE at: https://makersuite.google.com/app/apikey")
        return None
    
    messages = [
        {
            'role': 'system',
            'content': 'You are a helpful dermatology assistant. Provide brief, accurate medical information.'
        },
        {
            'role': 'user',
            'content': 'What are the main symptoms of eczema?'
        }
    ]
    
    print("\n📤 Sending query to Gemini...")
    result = client.call_gemini(messages, max_tokens=300)
    
    if 'error' in result:
        print(f"❌ {result['error']}")
        return None
    else:
        print(f"\n✅ Success! (FREE)")
        print(f"Tokens: {result['tokens']['total']}")
        print(f"Cost: ${result['cost']:.2f}")
        print(f"Latency: {result['latency']:.2f}s")
        print(f"\n📝 Response:\n{result['response'][:200]}...")
        
    return client


def test_memory_conversation():
    """Test multi-turn conversation (memory test)"""
    print("\n" + "=" * 60)
    print("Testing Memory Across Multiple Turns")
    print("=" * 60)
    
    client = GeminiFreeClient()
    
    if not client.api_key:
        return None
    
    # Turn 1: Patient introduces themselves
    conversation = [
        {
            'role': 'system',
            'content': 'You are a dermatology assistant. Remember all patient details.'
        },
        {
            'role': 'user',
            'content': "Hi, I'm 28 years old and I have eczema on my elbows. I have dry skin and I'm allergic to fragrance."
        }
    ]
    
    print("\n[Turn 1] Patient shares information...")
    result1 = client.call_gemini(conversation, max_tokens=200)
    
    if 'error' not in result1:
        print(f"✅ Gemini responds ({result1['tokens']['total']} tokens)")
        
        # Add response to conversation
        conversation.append({
            'role': 'assistant',
            'content': result1['response']
        })
        
        # Turn 2: Ask unrelated question (distraction)
        conversation.append({
            'role': 'user',
            'content': "What's the difference between chemical and physical sunscreen?"
        })
        
        print("\n[Turn 2] Asking about sunscreen (distraction)...")
        result2 = client.call_gemini(conversation, max_tokens=200)
        
        if 'error' not in result2:
            print(f"✅ Gemini responds ({result2['tokens']['total']} tokens)")
            
            # Add response
            conversation.append({
                'role': 'assistant',
                'content': result2['response']
            })
            
            # Turn 3: MEMORY TEST - recall age
            conversation.append({
                'role': 'user',
                'content': "What was my age again?"
            })
            
            print("\n[Turn 3] MEMORY TEST: Can Gemini recall age?...")
            result3 = client.call_gemini(conversation, max_tokens=100)
            
            if 'error' not in result3:
                print(f"✅ Gemini responds: {result3['response']}")
                
                # Check if it remembered
                if '28' in result3['response']:
                    print("\n🎉 SUCCESS! Gemini correctly remembered the age!")
                else:
                    print("\n⚠️  WARNING: Gemini may not have remembered correctly")
    
    return client


def estimate_free_tier_limits():
    """Show what you can do on the free tier"""
    print("\n" + "=" * 60)
    print("Google Gemini FREE Tier Limits")
    print("=" * 60)
    
    print("\n📊 What You Get (FREE):")
    print("  • 60 requests per minute")
    print("  • 1,500 requests per day")
    print("  • 1 million tokens per day")
    
    print("\n🎯 For Your Project:")
    print("  • 100 dialogues × 6 turns = 600 requests")
    print("  • Can complete in ~10 minutes")
    print("  • Estimated tokens: ~180,000 (well under 1M limit)")
    print("  • Cost: $0.00 ✅")
    
    print("\n💡 Tuesday Demo:")
    print("  • Run 5-10 test conversations")
    print("  • ~30-60 requests total")
    print("  • Takes ~1 minute")
    print("  • Cost: $0.00 ✅")
    
    print("\n✅ You can do your ENTIRE project for FREE!")


def main():
    """Main execution"""
    print("\n" + "=" * 60)
    print("🆓 DERMATOLOGY LLM BENCHMARK - FREE VERSION")
    print("Using Google Gemini Pro (No Credit Card Required!)")
    print("=" * 60)
    
    # Check for API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ Google API Key found!")
    else:
        print("❌ Google API Key not found")
        print("\n📝 To get started:")
        print("1. Visit: https://makersuite.google.com/app/apikey")
        print("2. Click 'Create API Key' (it's FREE)")
        print("3. Set it in your terminal:")
        print("   Windows: $env:GOOGLE_API_KEY='your-key-here'")
        print("   Mac/Linux: export GOOGLE_API_KEY='your-key-here'")
        print("\n4. Run this script again!")
        return
    
    # Show free tier limits
    estimate_free_tier_limits()
    
    # Ask to run tests
    print("\n" + "=" * 60)
    choice = input("\nRun tests? (y/n): ").lower()
    
    if choice == 'y':
        # Test 1: Simple query
        client = test_dermatology_query()
        
        if client:
            # Test 2: Memory test
            test_memory_conversation()
            
            # Summary
            print("\n" + "=" * 60)
            print("Usage Summary")
            print("=" * 60)
            summary = client.get_usage_summary()
            print(f"Total API Calls: {summary['total_calls']}")
            print(f"Total Tokens: {summary['total_tokens']}")
            print(f"Total Cost: ${summary['total_cost']:.2f} (FREE!)")
            print(f"Average Latency: {summary['average_latency']:.2f}s")
            
            # Save log
            client.save_usage_log('gemini_usage_log.json')
            
            print("\n✅ All tests complete! Ready for Tuesday demo!")
    
    print("\n" + "=" * 60)
    print("Next Steps:")
    print("1. ✅ Push this script to GitHub")
    print("2. 🔑 Monday: Get Gemini API key (FREE)")
    print("3. 🧪 Tuesday: Run tests and demo")
    print("4. 💰 Later: Decide if you want to add paid APIs")
    print("=" * 60)


if __name__ == '__main__':
    main()
    