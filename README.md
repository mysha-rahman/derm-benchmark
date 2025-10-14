# Derm Benchmark (Gold Profiles)

This repo builds a dermatology “gold profile” dataset to test LLMs for
memory consistency and misinformation resistance.

## Quick Start
1) Install Python 3.
2) Run: `python build_gold_profiles.py`
3) Edit: `gold_profiles/gold_profile_examples.csv` (duplicate a row, change values).
4) Run again to regenerate `gold_profiles.jsonl`.

## Team Workflow
- Make a branch: `git checkout -b feat/add-profiles`
- Edit CSV → run the script → `git add .` → `git commit -m "add: N profiles"`
- `git push -u origin feat/add-profiles` and open a Pull Request.

## Files
- `build_gold_profiles.py` — creates template, examples, and JSONL
- `gold_profiles/` — data folder (CSV kept, JSONL ignored by git)
