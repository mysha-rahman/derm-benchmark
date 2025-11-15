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

    def __init__(self, api_key=None, model=None, timeout=300):
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError("Missing GOOGLE_API_KEY environment variable")

        # Configure timeout via HttpOptions (timeout in milliseconds)
        self.client = genai.Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(timeout=timeout * 1000)  # Convert seconds to milliseconds
        )
        self.model = model or "models/gemini-2.5-flash"
        self.timeout = timeout

    def _extract_text(self, response):
        """
        Extract text from Gemini response, handling cases where response.text is None.
        Falls back to extracting from candidates[0].content.parts when needed.

        This handles MAX_TOKENS and other cases where response.text isn't populated.
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

    def chat(self, messages, temperature=0.7, max_tokens=2048):
        """Send conversation to Gemini with retries"""

        prompt = "\n".join(f"{m['role']}: {m['content']}" for m in messages)

        for attempt in range(3):  # exponential backoff
            try:
                # Try without any config first to see if safety_settings are causing issues
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=temperature,
                        max_output_tokens=max_tokens
                        # TEMPORARILY REMOVED safety_settings to test if they're causing issues
                    )
                    # timeout is configured via HttpOptions in __init__
                )

                # Check if response is valid
                if not response:
                    raise ValueError("Empty response from API")

                # Check prompt_feedback for blocking (happens BEFORE response is generated)
                if hasattr(response, 'prompt_feedback') and response.prompt_feedback:
                    feedback = response.prompt_feedback
                    if hasattr(feedback, 'block_reason') and feedback.block_reason:
                        raise ValueError(f"Content blocked by Gemini: {feedback.block_reason}. Feedback: {feedback}")

                # Check candidates for finish_reason (blocking during generation)
                if hasattr(response, 'candidates') and response.candidates:
                    candidate = response.candidates[0]
                    if hasattr(candidate, 'finish_reason'):
                        reason = str(candidate.finish_reason)
                        # Print finish_reason for debugging
                        if reason != 'STOP' and reason != '1':  # 1 is FinishReason.STOP
                            print(f"DEBUG: finish_reason={reason}")
                        # Gemini blocks with finish_reason = SAFETY, RECITATION, or OTHER
                        if 'SAFETY' in reason.upper() or 'RECITATION' in reason.upper() or 'OTHER' in reason.upper():
                            # Get safety ratings if available
                            safety_info = ""
                            if hasattr(candidate, 'safety_ratings'):
                                safety_info = f" Safety ratings: {candidate.safety_ratings}"
                            raise ValueError(f"Content blocked during generation (finish_reason: {reason}){safety_info}")

                # Extract text using helper (handles response.text or candidates.parts)
                extracted_text = self._extract_text(response)

                if not extracted_text:
                    # Build debug info
                    debug_info = f"candidates={len(response.candidates) if hasattr(response, 'candidates') else 'none'}"
                    if hasattr(response, 'prompt_feedback'):
                        debug_info += f", prompt_feedback={response.prompt_feedback}"
                    if hasattr(response, 'candidates') and response.candidates:
                        candidate = response.candidates[0]
                        if hasattr(candidate, 'finish_reason'):
                            debug_info += f", finish_reason={candidate.finish_reason}"
                    raise ValueError(f"No text in response. Debug: {debug_info}")

                return {
                    "response": extracted_text,
                    "success": True
                }

            except AttributeError as e:
                # This happens when response.text doesn't exist
                full_error = f"Response missing text attribute: {str(e)}"
                print(f"❌ API Error: {full_error}")
                return {
                    "response": None,
                    "success": False,
                    "error": full_error
                }
            except Exception as e:
                err = str(e).lower()
                full_error = str(e)

                # retry only for timeouts + transient server failures
                if "timeout" in err or "deadline" in err or "unavailable" in err:
                    wait = 2 ** attempt
                    print(f"    ⏳ Timeout, retrying in {wait}s...")
                    time.sleep(wait)
                    continue

                # final failure (no retry) - print actual error for debugging
                print(f"❌ API Error: {full_error}")
                return {
                    "response": None,
                    "success": False,
                    "error": full_error
                }

        # All retries exhausted
        print(f"❌ Timeout after 3 retries")
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