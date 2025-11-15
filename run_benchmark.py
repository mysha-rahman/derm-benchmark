#!/usr/bin/env python3
"""
Run dermatology benchmark with Gemini API (NEW 2025 SDK)
Processes all dialogue templates and saves results for scoring.
"""

import os
import json
import time
from pathlib import Path
from datetime import datetime
from google import genai


# ---------------------------------------------------------------------------
#  Gemini Client (NEW SDK)
# ---------------------------------------------------------------------------

class GeminiFreeClient:
    """Gemini client using the NEW google-genai SDK"""

    def __init__(self, api_key: str = None, model: str = None, timeout: int = 60):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")

        # Initialize Gemini client with timeout
        self.client = genai.Client(
            api_key=self.api_key,
            http_options={'timeout': timeout}
        )

        # Default model (works for new API keys)
        self.model = model or "gemini-2.5-flash"
        self.timeout = timeout

    def chat(self, messages: list, temperature: float = 0.7, max_tokens: int = 500, max_retries: int = 3) -> dict:
        """Send conversation to Gemini with retry logic."""

        # Flatten conversation into text prompt
        prompt = "\n".join(
            f"{m['role']}: {m['content']}"
            for m in messages
        )

        # Retry logic with exponential backoff
        for attempt in range(max_retries):
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config={
                        'temperature': temperature,
                        'max_output_tokens': max_tokens,
                    }
                )

                return {
                    "response": response.text,
                    "success": True,
                }

            except Exception as e:
                error_msg = str(e)

                # Check if it's a timeout or rate limit error
                is_retryable = (
                    "timeout" in error_msg.lower() or
                    "rate limit" in error_msg.lower() or
                    "429" in error_msg or
                    "503" in error_msg or
                    "connection" in error_msg.lower()
                )

                # If last attempt or not retryable, return error
                if attempt == max_retries - 1 or not is_retryable:
                    return {
                        "response": f"ERROR: {error_msg}",
                        "success": False,
                        "error": error_msg,
                    }

                # Wait before retrying (exponential backoff: 2s, 4s, 8s)
                wait_time = 2 ** (attempt + 1)
                print(f"⚠️  API error (attempt {attempt + 1}/{max_retries}): {error_msg}")
                print(f"   Retrying in {wait_time}s...")
                time.sleep(wait_time)

        # Should never reach here, but just in case
        return {
            "response": "ERROR: Max retries exceeded",
            "success": False,
            "error": "Max retries exceeded",
        }


# ---------------------------------------------------------------------------
#  Dialogue Loading
# ---------------------------------------------------------------------------

def load_dialogues(filepath: str = "dialogues/dialogue_templates.jsonl") -> list:
    """Load dialogue templates from JSONL."""
    dialogues = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            dialogues.append(json.loads(line))
    return dialogues


# ---------------------------------------------------------------------------
#  Run a Single Dialogue
# ---------------------------------------------------------------------------

def run_dialogue(client: GeminiFreeClient, dialogue: dict) -> dict:
    """Execute one dialogue conversation."""

    system_prompt = (
        "You are a helpful dermatology assistant. Provide brief, accurate medical information. "
        "Remember all patient details shared. Correct misinformation politely. Always include disclaimers."
    )

    conversation = [{"role": "system", "content": system_prompt}]

    result = {
        "dialogue_id": dialogue["dialogue_id"],
        "patient_id": dialogue["patient_id"],
        "patient_name": dialogue["patient_name"],
        "has_misinformation": dialogue["has_misinformation"],
        "timestamp": datetime.now().isoformat(),
        "exchanges": [],
    }

    user_turns = [t for t in dialogue["turns"] if t["role"] == "user"]

    for user_turn in user_turns:
        turn_num = user_turn["turn"]

        conversation.append({"role": "user", "content": user_turn["content"]})

        print(f"  Turn {turn_num}: ", end="", flush=True)
        ai_response = client.chat(conversation)

        if ai_response["success"]:
            print(f"✅ ({len(ai_response['response'])} chars)")

            # Add response to conversation history
            conversation.append(
                {"role": "assistant", "content": ai_response["response"]}
            )

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
            print(f"❌ Error: {ai_response['error']}")
            result["exchanges"].append({
                "turn": turn_num,
                "user_message": user_turn["content"],
                "ai_response": None,
                "error": ai_response["error"],
            })
            break

        time.sleep(1.1)

    return result


# ---------------------------------------------------------------------------
#  Benchmark Runner
# ---------------------------------------------------------------------------

def run_benchmark(num_dialogues: int = 25):
    print("=" * 70)
    print("🧪 DERMATOLOGY CHATBOT BENCHMARK")
    print("=" * 70)

    print("\n🔑 Checking API key...")
    try:
        client = GeminiFreeClient()
        print("✅ Gemini API key found!")
    except ValueError as e:
        print(f"❌ {e}")
        return

    print("\n📂 Loading dialogue templates...")
    dialogues = load_dialogues()
    print(f"✅ Loaded {len(dialogues)} dialogues")

    dialogues = dialogues[:num_dialogues]

    print(f"\n🚀 Running benchmark ({len(dialogues)} dialogues)")
    print(f"⏱️  Estimated time: {len(dialogues) * 5 * 1.1 / 60:.1f} minutes\n")

    results = []
    start = time.time()

    for i, dialogue in enumerate(dialogues, 1):
        print(f"[{i}/{len(dialogues)}] {dialogue['patient_name']} (ID: {dialogue['patient_id']})")
        results.append(run_dialogue(client, dialogue))
        print()

    elapsed = time.time() - start

    # Save results
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
            "results": results,
        }, f, indent=2)

    print("=" * 70)
    print("📊 BENCHMARK COMPLETE")
    print("=" * 70)
    print(f"✅ Dialogues completed: {len(results)}")
    print(f"⏱️  Total time: {elapsed/60:.1f} minutes")
    print(f"💾 Results saved to: {output_file}")


# ---------------------------------------------------------------------------
#  Entry Point
# ---------------------------------------------------------------------------

def run_quick_test():
    print("🔬 Running QUICK TEST (3 dialogues)")
    run_benchmark(num_dialogues=3)


if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        run_quick_test()
    else:
        run_benchmark(num_dialogues=25)
