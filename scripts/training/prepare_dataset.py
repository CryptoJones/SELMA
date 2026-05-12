#!/usr/bin/env python3
"""
Prepare training dataset for SELMA fine-tuning.

Combines statutory data, legal datasets, and synthetic examples
into a unified training format compatible with Llama 3.1 chat template.
"""

import json
import random
import sys
from pathlib import Path

from tqdm import tqdm

# Resolve paths relative to repo root regardless of CWD
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PROCESSED_DIR = REPO_ROOT / "data" / "processed"
SYNTHETIC_DIR = REPO_ROOT / "data" / "synthetic"
RAW_DIR = REPO_ROOT / "data" / "raw"
OUTPUT_DIR = REPO_ROOT / "data" / "processed"

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


def load_casehold(path: Path) -> list[dict]:
    """Convert CaseHOLD holdings into legal reasoning examples.

    CSV-loaded schema uses numeric string keys:
      "0" = citing prompt, "1"-"5" = holdings, "11" = correct label (int)
    """
    examples = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            # Support both original field names and numeric CSV keys
            citing_prompt = (row.get("citing_prompt") or row.get("0") or "").strip()
            raw_label = row.get("label") if "label" in row else row.get("11")
            if raw_label is None or citing_prompt == "":
                continue
            try:
                label = int(float(raw_label))
            except (ValueError, TypeError):
                continue
            if label < 0 or label > 4:
                continue
            holding_key = f"holding_{label}" if f"holding_{label}" in row else str(label + 1)
            holding = row.get(holding_key, "").strip()
            if not holding:
                continue
            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"In the following legal passage, identify the applicable legal holding:\n\n{citing_prompt}"},
                    {"role": "assistant", "content": holding},
                ],
                "type": "case_holding",
                "jurisdiction": "federal",
            })
    return examples


def load_alea(path: Path) -> list[dict]:
    """Convert ALEA US Courts case filings into classification examples.

    Schema: source_identifier, nos_code, nos_desc, cause, text
    """
    examples = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            text = (row.get("text") or "").strip()
            nos_desc = (row.get("nos_desc") or "").strip()
            cause = (row.get("cause") or "").strip()
            if not text or (not nos_desc and not cause):
                continue
            label_parts = []
            if nos_desc:
                label_parts.append(nos_desc)
            if cause:
                label_parts.append(f"cause of action: {cause}")
            label = "; ".join(label_parts)
            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": f"Classify the following federal court filing by cause of action or nature of suit:\n\n{text}"},
                    {"role": "assistant", "content": f"This filing involves: {label}"},
                ],
                "type": "case_classification",
                "jurisdiction": "federal",
            })
    return examples


def load_legalbench(path: Path) -> list[dict]:
    """Convert LegalBench tasks into legal reasoning examples."""
    examples = []
    with open(path) as f:
        for line in f:
            row = json.loads(line)
            question = (row.get("question") or row.get("input") or row.get("text") or "").strip()
            answer = (row.get("answer") or row.get("output") or row.get("label") or "")
            if not question or not answer:
                continue
            examples.append({
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": question},
                    {"role": "assistant", "content": str(answer).strip()},
                ],
                "type": "legal_reasoning",
                "jurisdiction": "federal",
            })
    return examples


def load_legal_datasets() -> list[dict]:
    """Load and convert HuggingFace legal datasets from data/raw/ if present."""
    examples = []

    if not RAW_DIR.exists():
        return examples

    casehold_path = RAW_DIR / "casehold.jsonl"
    if casehold_path.exists():
        loaded = load_casehold(casehold_path)
        print(f"  CaseHOLD: {len(loaded)} examples")
        examples.extend(loaded)

    alea_path = RAW_DIR / "alea_courts.jsonl"
    if alea_path.exists():
        loaded = load_alea(alea_path)
        print(f"  ALEA US Courts: {len(loaded)} examples")
        examples.extend(loaded)

    legalbench_path = RAW_DIR / "legalbench.jsonl"
    if legalbench_path.exists():
        loaded = load_legalbench(legalbench_path)
        print(f"  LegalBench: {len(loaded)} examples")
        examples.extend(loaded)

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

    print("\nLoading HuggingFace legal datasets...")
    legal_examples = load_legal_datasets()
    print(f"  {len(legal_examples)} legal dataset examples")
    all_examples.extend(legal_examples)

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
        "legal_datasets": len(legal_examples),
    }
    with open(OUTPUT_DIR / "dataset_stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print(f"\nDataset saved to {OUTPUT_DIR}/")
    print(json.dumps(stats, indent=2))


if __name__ == "__main__":
    main()
