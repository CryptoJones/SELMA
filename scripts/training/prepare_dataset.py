#!/usr/bin/env python3
"""
Prepare training dataset for SELMA fine-tuning.

Combines statutory data, legal datasets, and synthetic examples
into a unified training format compatible with Qwen3 chat template.
"""

import json
import random
from pathlib import Path

from tqdm import tqdm

PROCESSED_DIR = Path("data/processed")
SYNTHETIC_DIR = Path("data/synthetic")
OUTPUT_DIR = Path("data/processed")

SYSTEM_PROMPT = """You are SELMA (Specified Encapsulated Limitless Memory Archive), an AI assistant \
trained to help law enforcement identify potential violations of criminal law.

Given an incident description, you will:
1. Identify all potentially applicable criminal statutes (federal and/or state)
2. For each statute, list the required elements of the offense
3. Map the facts of the incident to each element
4. Classify the potential charge (felony/misdemeanor, degree)
5. Note any jurisdictional considerations
6. Flag related or lesser included offenses

Always cite specific statute numbers. Be thorough but precise."""


def load_statute_knowledge() -> list[dict]:
    """Create training examples from parsed statutes."""
    examples = []

    # Federal statutes
    federal_path = PROCESSED_DIR / "federal_statutes.json"
    if federal_path.exists():
        with open(federal_path) as f:
            federal = json.load(f)

        for section_num, statute in federal.items():
            if statute.get("title") and statute.get("text"):
                # Create a statute knowledge example
                examples.append({
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"What are the key provisions of {statute['citation']} ({statute['title']})?",
                        },
                        {
                            "role": "assistant",
                            "content": f"## {statute['citation']} — {statute['title']}\n\n{statute['text']}",
                        },
                    ],
                    "type": "statute_knowledge",
                    "jurisdiction": "federal",
                })

    # Georgia statutes
    georgia_path = PROCESSED_DIR / "georgia_statutes.json"
    if georgia_path.exists():
        with open(georgia_path) as f:
            georgia = json.load(f)

        for section_num, statute in georgia.items():
            if statute.get("title") and statute.get("text"):
                examples.append({
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {
                            "role": "user",
                            "content": f"What are the key provisions of {statute['citation']} ({statute['title']})?",
                        },
                        {
                            "role": "assistant",
                            "content": f"## {statute['citation']} — {statute['title']}\n\n{statute['text']}",
                        },
                    ],
                    "type": "statute_knowledge",
                    "jurisdiction": "georgia",
                })

    return examples


def load_synthetic_examples() -> list[dict]:
    """Load synthetic incident-to-charge training examples."""
    examples = []
    synthetic_path = SYNTHETIC_DIR / "synthetic_training.jsonl"

    if synthetic_path.exists():
        with open(synthetic_path) as f:
            for line in f:
                example = json.loads(line)
                examples.append(example)

    return examples


def split_dataset(examples: list[dict], eval_ratio: float = 0.05) -> tuple:
    """Split examples into train and eval sets."""
    random.shuffle(examples)
    split_idx = int(len(examples) * (1 - eval_ratio))
    return examples[:split_idx], examples[split_idx:]


def save_dataset(examples: list[dict], output_path: Path):
    """Save examples as JSONL."""
    with open(output_path, "w") as f:
        for example in examples:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    """Main entry point."""
    print("=" * 60)
    print("SELMA — Preparing Training Dataset")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Collect all examples
    all_examples = []

    print("\nLoading statute knowledge examples...")
    statute_examples = load_statute_knowledge()
    print(f"  {len(statute_examples)} statute examples")
    all_examples.extend(statute_examples)

    print("\nLoading synthetic examples...")
    synthetic_examples = load_synthetic_examples()
    print(f"  {len(synthetic_examples)} synthetic examples")
    all_examples.extend(synthetic_examples)

    print(f"\nTotal examples: {len(all_examples)}")

    # Split
    train, eval_set = split_dataset(all_examples)
    print(f"Train: {len(train)}, Eval: {len(eval_set)}")

    # Save
    save_dataset(train, OUTPUT_DIR / "train.jsonl")
    save_dataset(eval_set, OUTPUT_DIR / "eval.jsonl")

    # Save stats
    stats = {
        "total_examples": len(all_examples),
        "train_examples": len(train),
        "eval_examples": len(eval_set),
        "statute_knowledge": len(statute_examples),
        "synthetic": len(synthetic_examples),
    }
    with open(OUTPUT_DIR / "dataset_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nDataset saved to {OUTPUT_DIR}/")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
