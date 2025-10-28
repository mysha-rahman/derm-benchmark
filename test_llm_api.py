"""
Dermatology LLM Benchmark - API Integration Script
Supports: GPT-4, Claude 3.5 Sonnet, Gemini Pro
Author: Mysha Rahman
Date: October 2025
"""

import os
import json
import time
from typing import Dict, List, Optional
from datetime import datetime
import requests


class LLMAPIClient:
    """Unified client for testing multiple LLM APIs"""
    
    def __init__(self, api_keys: Optional[Dict[str, str]] = None):
        """
        Initialize API client with keys
        
        Args:
            api_keys: Dictionary with keys 'openai', 'anthropic', 'google'
                     If None, reads from environment variables
        """
        if api_keys is None:
            api_keys = {
                'openai': os.getenv('OPENAI_API_KEY'),
                'anthropic': os.getenv('ANTHROPIC_API_KEY'),
                'google': os.getenv('GOOGLE_API_KEY')
            }
        
        self.api_keys = api_keys
        self.usage_log = []
        self.cost_estimates = {
            'gpt-4': {'input': 0.03, 'output': 0.06},  # per 1K tokens
            'claude-3.5-sonnet': {'input': 0.003, 'output': 0.015},
            'gemini-pro': {'input': 0.00025, 'output': 0.0005}
        }
    
    def call_gpt4(self, messages: List[Dict[str, str]], 
                  temperature: float = 0.7,
                  max_tokens: int = 500) -> Dict:
        """
        Call OpenAI GPT-4 API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum response length
            
        Returns:
            Dict with 'response', 'model', 'tokens', 'cost'
        """
        if not self.api_keys['openai']:
            return {'error': 'OpenAI API key not found'}
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f"Bearer {self.api_keys['openai']}"
            }
            
            payload = {
                'model': 'gpt-4-turbo-preview',
                'messages': messages,
                'temperature': temperature,
                'max_tokens': max_tokens
            }
            
            start_time = time.time()
            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            
            result = {
                'model': 'gpt-4',
                'response': data['choices'][0]['message']['content'],
                'tokens': {
                    'input': data['usage']['prompt_tokens'],
                    'output': data['usage']['completion_tokens'],
                    'total': data['usage']['total_tokens']
                },
                'cost': self._calculate_cost('gpt-4', 
                                            data['usage']['prompt_tokens'],
                                            data['usage']['completion_tokens']),
                'latency': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_usage(result)
            return result
            
        except requests.exceptions.RequestException as e:
            return {'error': f'GPT-4 API error: {str(e)}', 'model': 'gpt-4'}
    
    def call_claude(self, messages: List[Dict[str, str]], 
                   temperature: float = 0.7,
                   max_tokens: int = 500) -> Dict:
        """
        Call Anthropic Claude 3.5 Sonnet API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dict with 'response', 'model', 'tokens', 'cost'
        """
        if not self.api_keys['anthropic']:
            return {'error': 'Anthropic API key not found'}
        
        try:
            headers = {
                'Content-Type': 'application/json',
                'x-api-key': self.api_keys['anthropic'],
                'anthropic-version': '2023-06-01'
            }
            
            # Convert messages format for Claude
            claude_messages = []
            system_message = None
            
            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    claude_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })
            
            payload = {
                'model': 'claude-3-5-sonnet-20241022',
                'messages': claude_messages,
                'max_tokens': max_tokens,
                'temperature': temperature
            }
            
            if system_message:
                payload['system'] = system_message
            
            start_time = time.time()
            response = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers=headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            
            result = {
                'model': 'claude-3.5-sonnet',
                'response': data['content'][0]['text'],
                'tokens': {
                    'input': data['usage']['input_tokens'],
                    'output': data['usage']['output_tokens'],
                    'total': data['usage']['input_tokens'] + data['usage']['output_tokens']
                },
                'cost': self._calculate_cost('claude-3.5-sonnet',
                                            data['usage']['input_tokens'],
                                            data['usage']['output_tokens']),
                'latency': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_usage(result)
            return result
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Claude API error: {str(e)}', 'model': 'claude-3.5-sonnet'}
    
    def call_gemini(self, messages: List[Dict[str, str]], 
                   temperature: float = 0.7,
                   max_tokens: int = 500) -> Dict:
        """
        Call Google Gemini Pro API
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum response length
            
        Returns:
            Dict with 'response', 'model', 'tokens', 'cost'
        """
        if not self.api_keys['google']:
            return {'error': 'Google API key not found'}
        
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
                f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={self.api_keys['google']}",
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            elapsed_time = time.time() - start_time
            
            data = response.json()
            
            # Extract response text
            response_text = data['candidates'][0]['content']['parts'][0]['text']
            
            # Estimate tokens (Gemini doesn't always return token counts)
            input_tokens = sum(len(msg['content'].split()) * 1.3 for msg in messages)
            output_tokens = len(response_text.split()) * 1.3
            
            result = {
                'model': 'gemini-pro',
                'response': response_text,
                'tokens': {
                    'input': int(input_tokens),
                    'output': int(output_tokens),
                    'total': int(input_tokens + output_tokens)
                },
                'cost': self._calculate_cost('gemini-pro',
                                            int(input_tokens),
                                            int(output_tokens)),
                'latency': elapsed_time,
                'timestamp': datetime.now().isoformat()
            }
            
            self._log_usage(result)
            return result
            
        except requests.exceptions.RequestException as e:
            return {'error': f'Gemini API error: {str(e)}', 'model': 'gemini-pro'}
    
    def call_all(self, messages: List[Dict[str, str]], 
                temperature: float = 0.7,
                max_tokens: int = 500) -> Dict[str, Dict]:
        """
        Call all three LLM APIs and return results
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            temperature: Sampling temperature
            max_tokens: Maximum response length
            
        Returns:
            Dict with keys 'gpt4', 'claude', 'gemini' containing results
        """
        return {
            'gpt4': self.call_gpt4(messages, temperature, max_tokens),
            'claude': self.call_claude(messages, temperature, max_tokens),
            'gemini': self.call_gemini(messages, temperature, max_tokens)
        }
    
    def _calculate_cost(self, model: str, input_tokens: int, output_tokens: int) -> float:
        """Calculate API cost for a request"""
        rates = self.cost_estimates.get(model, {'input': 0, 'output': 0})
        input_cost = (input_tokens / 1000) * rates['input']
        output_cost = (output_tokens / 1000) * rates['output']
        return round(input_cost + output_cost, 6)
    
    def _log_usage(self, result: Dict):
        """Log API usage for tracking"""
        self.usage_log.append(result)
    
    def get_usage_summary(self) -> Dict:
        """Get summary of API usage and costs"""
        summary = {
            'total_calls': len(self.usage_log),
            'by_model': {},
            'total_cost': 0,
            'total_tokens': 0,
            'average_latency': 0
        }
        
        for entry in self.usage_log:
            if 'error' in entry:
                continue
                
            model = entry['model']
            if model not in summary['by_model']:
                summary['by_model'][model] = {
                    'calls': 0,
                    'tokens': 0,
                    'cost': 0,
                    'avg_latency': 0
                }
            
            summary['by_model'][model]['calls'] += 1
            summary['by_model'][model]['tokens'] += entry['tokens']['total']
            summary['by_model'][model]['cost'] += entry['cost']
            summary['by_model'][model]['avg_latency'] += entry['latency']
            
            summary['total_cost'] += entry['cost']
            summary['total_tokens'] += entry['tokens']['total']
            summary['average_latency'] += entry['latency']
        
        # Calculate averages
        if summary['total_calls'] > 0:
            summary['average_latency'] /= summary['total_calls']
            for model in summary['by_model']:
                calls = summary['by_model'][model]['calls']
                summary['by_model'][model]['avg_latency'] /= calls
        
        return summary
    
    def save_usage_log(self, filepath: str = 'api_usage_log.json'):
        """Save usage log to file"""
        with open(filepath, 'w') as f:
            json.dump({
                'log': self.usage_log,
                'summary': self.get_usage_summary()
            }, f, indent=2)
        print(f"Usage log saved to {filepath}")


def test_simple_query():
    """Test all APIs with a simple dermatology question"""
    print("=" * 60)
    print("Testing LLM APIs with Simple Query")
    print("=" * 60)
    
    client = LLMAPIClient()
    
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
    
    print("\nTesting GPT-4...")
    gpt4_result = client.call_gpt4(messages, max_tokens=300)
    if 'error' in gpt4_result:
        print(f"❌ {gpt4_result['error']}")
    else:
        print(f"✅ Success! Cost: ${gpt4_result['cost']:.4f}, Tokens: {gpt4_result['tokens']['total']}")
        print(f"Response preview: {gpt4_result['response'][:100]}...")
    
    print("\nTesting Claude 3.5 Sonnet...")
    claude_result = client.call_claude(messages, max_tokens=300)
    if 'error' in claude_result:
        print(f"❌ {claude_result['error']}")
    else:
        print(f"✅ Success! Cost: ${claude_result['cost']:.4f}, Tokens: {claude_result['tokens']['total']}")
        print(f"Response preview: {claude_result['response'][:100]}...")
    
    print("\nTesting Gemini Pro...")
    gemini_result = client.call_gemini(messages, max_tokens=300)
    if 'error' in gemini_result:
        print(f"❌ {gemini_result['error']}")
    else:
        print(f"✅ Success! Cost: ${gemini_result['cost']:.4f}, Tokens: {gemini_result['tokens']['total']}")
        print(f"Response preview: {gemini_result['response'][:100]}...")
    
    # Print summary
    print("\n" + "=" * 60)
    print("API Usage Summary")
    print("=" * 60)
    summary = client.get_usage_summary()
    print(f"Total API Calls: {summary['total_calls']}")
    print(f"Total Cost: ${summary['total_cost']:.4f}")
    print(f"Total Tokens: {summary['total_tokens']}")
    print(f"Average Latency: {summary['average_latency']:.2f}s")
    
    # Save log
    client.save_usage_log()
    
    return client


def test_multi_turn_conversation():
    """Test a multi-turn conversation about a patient case"""
    print("\n" + "=" * 60)
    print("Testing Multi-Turn Conversation")
    print("=" * 60)
    
    client = LLMAPIClient()
    
    # Conversation scenario
    conversation = [
        {
            'role': 'system',
            'content': 'You are a dermatology assistant helping a patient. Remember all details they share.'
        },
        {
            'role': 'user',
            'content': 'I have red, itchy patches on my elbows. I\'m 28 years old with dry skin.'
        }
    ]
    
    print("\n[Turn 1] Patient describes symptoms...")
    results = client.call_all(conversation, max_tokens=200)
    
    # Add responses and continue conversation
    for model_name, result in results.items():
        if 'error' not in result:
            print(f"\n{model_name.upper()}: {result['response'][:80]}...")
    
    # Turn 2: Test memory
    conversation.extend([
        {
            'role': 'assistant',
            'content': results['claude']['response'] if 'error' not in results['claude'] else 'I understand.'
        },
        {
            'role': 'user',
            'content': 'What was my age again?'
        }
    ])
    
    print("\n[Turn 2] Testing memory recall...")
    memory_test = client.call_claude(conversation, max_tokens=100)
    if 'error' not in memory_test:
        print(f"Claude response: {memory_test['response']}")
        print(f"✅ Remembered correctly!" if '28' in memory_test['response'] else "❌ Memory failure")
    
    return client


def estimate_project_costs(num_profiles: int = 100, 
                          num_dialogues: int = 100,
                          turns_per_dialogue: int = 6):
    """Estimate total project costs"""
    print("\n" + "=" * 60)
    print("Project Cost Estimation")
    print("=" * 60)
    
    # Assumptions
    avg_input_tokens = 300  # Per turn
    avg_output_tokens = 200  # Per turn
    
    total_turns = num_dialogues * turns_per_dialogue
    total_calls_per_model = total_turns
    
    costs = {
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'claude-3.5-sonnet': {'input': 0.003, 'output': 0.015},
        'gemini-pro': {'input': 0.00025, 'output': 0.0005}
    }
    
    print(f"\nAssumptions:")
    print(f"- {num_profiles} patient profiles")
    print(f"- {num_dialogues} dialogues × {turns_per_dialogue} turns = {total_turns} total turns")
    print(f"- ~{avg_input_tokens} input tokens per turn")
    print(f"- ~{avg_output_tokens} output tokens per turn")
    print(f"- Testing with 3 models")
    
    print(f"\nCost per Model:")
    total_project_cost = 0
    
    for model, rates in costs.items():
        input_cost = (total_calls_per_model * avg_input_tokens / 1000) * rates['input']
        output_cost = (total_calls_per_model * avg_output_tokens / 1000) * rates['output']
        model_total = input_cost + output_cost
        total_project_cost += model_total
        print(f"{model:20s}: ${model_total:7.2f}")
    
    print(f"\n{'TOTAL PROJECT COST':20s}: ${total_project_cost:7.2f}")
    print(f"\nBudget Recommendation: ${total_project_cost * 1.2:.2f} (with 20% buffer)")
    
    return total_project_cost


if __name__ == '__main__':
    print("Dermatology LLM Benchmark - API Testing Suite\n")
    
    # Check for API keys
    print("Checking API Keys...")
    keys_present = {
        'OpenAI': bool(os.getenv('OPENAI_API_KEY')),
        'Anthropic': bool(os.getenv('ANTHROPIC_API_KEY')),
        'Google': bool(os.getenv('GOOGLE_API_KEY'))
    }
    
    for service, present in keys_present.items():
        status = "✅" if present else "❌"
        print(f"{status} {service} API Key")
    
    if not any(keys_present.values()):
        print("\n⚠️  No API keys found!")
        print("Set environment variables:")
        print("  export OPENAI_API_KEY='your-key'")
        print("  export ANTHROPIC_API_KEY='your-key'")
        print("  export GOOGLE_API_KEY='your-key'")
        print("\nOr pass them to LLMAPIClient(api_keys={...})")
    
    # Run tests
    print("\n" + "=" * 60)
    choice = input("\nRun tests? (y/n): ").lower()
    
    if choice == 'y':
        test_simple_query()
        test_multi_turn_conversation()
    
    # Always show cost estimate
    estimate_project_costs()