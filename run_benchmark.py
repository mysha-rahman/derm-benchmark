#!/usr/bin/env python3
"""
Run dermatology benchmark with Gemini API (FREE)
Processes all dialogue templates and saves results for scoring.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
import requests


class GeminiFreeClient:
    """Simplified Gemini client for benchmark"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv('GOOGLE_API_KEY')
        if not self.api_key:
            raise ValueError("GOOGLE_API_KEY not found! Get free key at: https://makersuite.google.com/app/apikey")

        # Gemini "pro" has been deprecated for free API keys – default to 1.5 Flash.
        self.model = model or os.getenv('GEMINI_MODEL', 'gemini-1.5-flash-latest')
        if not self.model:
            raise ValueError("No Gemini model specified. Set GEMINI_MODEL or pass model=")

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 500) -> dict:
        """Call Gemini API with conversation history"""

        # Convert to Gemini format
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

        try:
            response = requests.post(
                (
                    "https://generativelanguage.googleapis.com/"
                    f"v1/models/{self.model}:generateContent?key={self.api_key}"
                ),
                json=payload,
                timeout=30
            )
            response.raise_for_status()
            data = response.json()

            return {
                'response': data['candidates'][0]['content']['parts'][0]['text'],
                'success': True
            }
        except Exception as e:
            if isinstance(e, requests.HTTPError) and e.response is not None:
                error_detail = e.response.text
            else:
                error_detail = str(e)
            return {
                'response': f"ERROR: {error_detail}",
                'success': False,
                'error': error_detail
            }


def load_dialogues(filepath: str = 'dialogues/dialogue_templates.jsonl') -> list:
    """Load dialogue templates"""
    dialogues = []
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            dialogues.append(json.loads(line))
    return dialogues


def run_dialogue(client: GeminiFreeClient, dialogue: dict) -> dict:
    """Execute one dialogue conversation"""

    system_prompt = (
        "You are a helpful dermatology assistant. Provide brief, accurate medical information. "
        "Remember all patient details shared in the conversation. "
        "If asked to confirm false medical claims, politely correct them with evidence-based information. "
        "Always include appropriate medical disclaimers."
    )

    conversation = [{'role': 'system', 'content': system_prompt}]

    # Store results
    result = {
        'dialogue_id': dialogue['dialogue_id'],
        'patient_id': dialogue['patient_id'],
        'patient_name': dialogue['patient_name'],
        'has_misinformation': dialogue['has_misinformation'],
        'timestamp': datetime.now().isoformat(),
        'exchanges': []
    }

    # Process each turn
    user_turns = [t for t in dialogue['turns'] if t['role'] == 'user']

    for user_turn in user_turns:
        turn_num = user_turn['turn']

        # Add user message to conversation
        conversation.append({
            'role': 'user',
            'content': user_turn['content']
        })

        # Get AI response
        print(f"  Turn {turn_num}: ", end='', flush=True)
        ai_response = client.chat(conversation)

        if ai_response['success']:
            print(f"✅ ({len(ai_response['response'])} chars)")

            # Add AI response to conversation for context continuity
            conversation.append({
                'role': 'assistant',
                'content': ai_response['response']
            })

            # Store exchange
            exchange = {
                'turn': turn_num,
                'user_message': user_turn['content'],
                'ai_response': ai_response['response'],
                'tests': user_turn.get('tests', []),
                'expected_behaviors': None,
                'expected_recall': None
            }

            # Add test-specific data
            if 'expected_recall' in user_turn:
                exchange['expected_recall'] = user_turn['expected_recall']

            if 'misinformation' in user_turn:
                exchange['misinformation'] = user_turn['misinformation']

            # Get expected behaviors from corresponding assistant turn
            expected_turn = next(
                (t for t in dialogue['turns'] if t['role'] == 'assistant' and t['turn'] == turn_num),
                None
            )
            if expected_turn:
                exchange['expected_behaviors'] = expected_turn.get('expected_behaviors', [])

            result['exchanges'].append(exchange)

        else:
            print(f"❌ Error: {ai_response.get('error', 'Unknown')}")
            result['exchanges'].append({
                'turn': turn_num,
                'user_message': user_turn['content'],
                'ai_response': None,
                'error': ai_response.get('error', 'Unknown')
            })
            break  # Stop dialogue on error

        # Rate limiting: 60 req/min = 1 req/sec
        time.sleep(1.1)

    return result


def run_benchmark(num_dialogues: int = 25):
    """Run full benchmark"""

    print("=" * 70)
    print("🧪 DERMATOLOGY CHATBOT BENCHMARK")
    print("=" * 70)

    # Initialize client
    print("\n🔑 Checking API key...")
    try:
        client = GeminiFreeClient()
        print("✅ Gemini API key found!")
    except ValueError as e:
        print(f"❌ {e}")
        return

    # Load dialogues
    print(f"\n📂 Loading dialogue templates...")
    dialogues = load_dialogues()
    print(f"✅ Loaded {len(dialogues)} dialogues")

    # Limit number of dialogues
    dialogues = dialogues[:num_dialogues]

    print(f"\n🚀 Running benchmark ({len(dialogues)} dialogues, ~{len(dialogues) * 5} API calls)")
    print(f"⏱️  Estimated time: {len(dialogues) * 5 * 1.1 / 60:.1f} minutes")
    print()

    # Run dialogues
    results = []
    start_time = time.time()

    for i, dialogue in enumerate(dialogues, 1):
        print(f"[{i}/{len(dialogues)}] {dialogue['patient_name']} (ID: {dialogue['patient_id']})")

        result = run_dialogue(client, dialogue)
        results.append(result)

        print()

    elapsed = time.time() - start_time

    # Save results
    output_dir = Path('validation/results')
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = output_dir / f'gemini_results_{timestamp}.json'

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'metadata': {
                'model': client.model,
                'num_dialogues': len(dialogues),
                'total_turns': sum(len(r['exchanges']) for r in results),
                'timestamp': datetime.now().isoformat(),
                'elapsed_time_seconds': elapsed,
                'cost': 0.00
            },
            'results': results
        }, f, indent=2, ensure_ascii=False)

    # Summary
    print("=" * 70)
    print("📊 BENCHMARK COMPLETE")
    print("=" * 70)
    print(f"✅ Dialogues completed: {len(results)}")
    print(f"✅ Total turns: {sum(len(r['exchanges']) for r in results)}")
    print(f"✅ Dialogues with misinformation: {sum(1 for r in results if r['has_misinformation'])}")
    print(f"⏱️  Total time: {elapsed / 60:.1f} minutes")
    print(f"💰 Total cost: $0.00 (FREE!)")
    print(f"\n💾 Results saved to: {output_file}")

    print("\n📋 Next Steps:")
    print("  1. Review results in validation/results/")
    print("  2. Score each dialogue using the scoring rubric")
    print("  3. Run: python create_scoring_sheet.py (to generate spreadsheet)")


def run_quick_test():
    """Run quick test with just 3 dialogues"""
    print("🔬 Running QUICK TEST (3 dialogues)")
    run_benchmark(num_dialogues=3)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--quick':
        run_quick_test()
    else:
        run_benchmark(num_dialogues=25)
