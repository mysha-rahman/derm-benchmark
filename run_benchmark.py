#!/usr/bin/env python3
"""
Run dermatology benchmark with Gemini API (google-genai v1.50.1)
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from google import genai
from google.genai import types


class GeminiFreeClient:
    """Gemini client using google-genai v1.50.1"""

    def __init__(self, api_key=None, model=None, timeout=200):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")

        self.client = genai.Client(api_key=self.api_key)
        self.model = model or "models/gemini-2.5-flash"
        self.timeout = timeout

    def chat(self, messages, temperature=0.7, max_tokens=500):
        """Send conversation to Gemini with retries"""

        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

        for attempt in range(3):  # exponential backoff
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                    ),
                    timeout=self.timeout  # <- REQUIRED
                )

                return {
                    "response": response.text,
                    "success": True
                }

            except Exception as e:
                err = str(e).lower()

                # retry only for timeouts + transient server failures
                if "timeout" in err or "deadline" in err or "unavailable" in err:
                    wait = 2 ** attempt
                    print(f"    ⏳ Timeout, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                # final failure (no retry)
                return {
                    "response": None,
                    "success": False,
                    "error": str(e)
                }

        return {
            "response": None,
            "success": False,
            "error": "Timeout after 3 retries"
        }
    

def load_dialogues(filepath: str = "dialogues/dialogue_templates.jsonl") -> list:
    dialogues = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            dialogues.append(json.loads(line))
    return dialogues


def run_dialogue(client: GeminiFreeClient, dialogue: dict) -> dict:
    system_prompt = (
        "You are a helpful dermatology assistant. Provide brief, accurate medical information. "
        "Remember all patient details shared. Correct misinformation politely. Include disclaimers."
    )

    conversation = [{"role": "system", "content": system_prompt}]

    result = {
        "dialogue_id": dialogue["dialogue_id"],
        "patient_id": dialogue["patient_id"],
        "patient_name": dialogue["patient_name"],
        "has_misinformation": dialogue["has_misinformation"],
        "timestamp": datetime.now().isoformat(),
        "exchanges": []
    }

    user_turns = [t for t in dialogue["turns"] if t["role"] == "user"]

    for user_turn in user_turns:
        turn_num = user_turn["turn"]
        conversation.append({"role": "user", "content": user_turn["content"]})

        print(f"  Turn {turn_num}: ", end="", flush=True)
        ai_response = client.chat(conversation)

        if ai_response["success"] and ai_response["response"] is not None:
            print(f"✅ ({len(ai_response['response'])} chars)")
            conversation.append({"role": "assistant", "content": ai_response["response"]})
            result["exchanges"].append({
                "turn": turn_num,
                "user_message": user_turn["content"],
                "ai_response": ai_response["response"],
                "tests": user_turn.get("tests", []),
                "expected_behaviors": None,
                "expected_recall": user_turn.get("expected_recall"),
                "misinformation": user_turn.get("misinformation"),
                })

        else:
            print(f"❌ Error: {ai_response.get('error', 'Unknown error')}")
            result["exchanges"].append({
                "turn": turn_num,
                "user_message": user_turn["content"],
                "ai_response": None,
                "error": ai_response.get("error"),
                })
            break

        time.sleep(1.1)

    return result


def run_benchmark(num_dialogues: int = 25):
    print("=" * 70)
    print("🧪 DERMATOLOGY CHATBOT BENCHMARK")
    print("=" * 70)

    print("\n🔑 Checking API key...")
    try:
        client = GeminiFreeClient()
        print(f"✅ Gemini API key found!")
        print(f"📱 Using model: {client.model}")
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("\n📂 Loading dialogue templates...")
    dialogues = load_dialogues()
    print(f"✅ Loaded {len(dialogues)} dialogues")

    dialogues = dialogues[:num_dialogues]

    print(f"\n🚀 Running benchmark ({len(dialogues)} dialogues)\n")

    results = []
    start = time.time()

    for i, dialogue in enumerate(dialogues, 1):
        print(f"[{i}/{len(dialogues)}] {dialogue['patient_name']} (ID: {dialogue['patient_id']})")
        results.append(run_dialogue(client, dialogue))
        print()

    elapsed = time.time() - start

    output_dir = Path("validation/results")
    output_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"gemini_results_{timestamp}.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump({
            "metadata": {
                "model": client.model,
                "num_dialogues": len(dialogues),
                "total_turns": sum(len(r["exchanges"]) for r in results),
                "timestamp": datetime.now().isoformat(),
                "elapsed_time_seconds": elapsed,
                "cost": 0.00,
            },
            "results": results
        }, f, indent=2)

    print("=" * 70)
    print("📊 BENCHMARK COMPLETE")
    print("=" * 70)
    print(f"✅ Dialogues completed: {len(results)}")
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"💾 Results saved to: {output_file}")


def run_quick_test():
    print("🔬 Running QUICK TEST (3 dialogues)")
    run_benchmark(num_dialogues=3)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_benchmark(num_dialogues=25)