#!/usr/bin/env python3
"""
Fetch legal NLP datasets from HuggingFace for SELMA training.

Downloads and processes:
- ALEA US Courts NOS/Cause classification (491K examples)
- LegalBench legal reasoning tasks (91.8K examples)
- CaseHOLD legal holding classification (585K examples)
"""

import json
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm

OUTPUT_DIR = Path("data/raw")


def fetch_alea_courts():
    """Fetch ALEA US Courts NOS/Cause classification dataset."""
    print("\n" + "=" * 60)
    print("Fetching ALEA US Courts NOS/Cause dataset...")
    print("=" * 60)

    try:
        ds = load_dataset("alea-institute/alea-legal-benchmark-uscourts-nos-cause")
        output_path = OUTPUT_DIR / "alea_courts.jsonl"

        count = 0
        with open(output_path, "w") as f:
            for split in ds:
                for example in tqdm(ds[split], desc=f"Processing {split}"):
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    count += 1

        print(f"Saved {count} examples to {output_path}")
    except Exception as e:
        print(f"Warning: Could not fetch ALEA dataset: {e}")
        print("You may need to accept the dataset license on HuggingFace first.")


def fetch_legalbench():
    """Fetch LegalBench reasoning tasks."""
    print("\n" + "=" * 60)
    print("Fetching LegalBench dataset...")
    print("=" * 60)

    try:
        ds = load_dataset("nguha/legalbench")
        output_path = OUTPUT_DIR / "legalbench.jsonl"

        count = 0
        with open(output_path, "w") as f:
            for split in ds:
                for example in tqdm(ds[split], desc=f"Processing {split}"):
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    count += 1

        print(f"Saved {count} examples to {output_path}")
    except Exception as e:
        print(f"Warning: Could not fetch LegalBench dataset: {e}")


def fetch_casehold():
    """Fetch CaseHOLD legal holding classification dataset."""
    print("\n" + "=" * 60)
    print("Fetching CaseHOLD dataset...")
    print("=" * 60)

    try:
        ds = load_dataset("casehold/casehold")
        output_path = OUTPUT_DIR / "casehold.jsonl"

        count = 0
        with open(output_path, "w") as f:
            for split in ds:
                for example in tqdm(ds[split], desc=f"Processing {split}"):
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    count += 1

        print(f"Saved {count} examples to {output_path}")
    except Exception as e:
        print(f"Warning: Could not fetch CaseHOLD dataset: {e}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("SELMA — Fetching Legal NLP Datasets from HuggingFace")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fetch_alea_courts()
    fetch_legalbench()
    fetch_casehold()

    print("\nDone! Check data/raw/ for downloaded datasets.")


if __name__ == "__main__":
    main()
