#!/usr/bin/env python3
"""
Generate synthetic SELMA training data using Claude API.

Produces diverse incident-to-charge training examples covering federal
(Title 18) and state criminal codes. Appends to the existing synthetic
training file so it can be run multiple times to scale up the dataset.

Usage:
    export ANTHROPIC_API_KEY="sk-ant-..."
    python scripts/data_collection/generate_synthetic_ai.py
    python scripts/data_collection/generate_synthetic_ai.py --count 500 --jurisdiction georgia
    python scripts/data_collection/generate_synthetic_ai.py --count 2000 --jurisdiction all
"""

import argparse
import json
import sys
import time
from pathlib import Path

import anthropic

OUTPUT_PATH = Path("data/synthetic/synthetic_training.jsonl")

SYSTEM_PROMPT = """You are SELMA (Specified Encapsulated Limitless Memory Archive), an AI assistant \
trained to help law enforcement identify potential violations of criminal law.

Given an incident description, you will:
1. Identify all potentially applicable criminal statutes (federal and/or state)
2. For each statute, list the required elements of the offense
3. Map the facts of the incident to each element
4. Classify the potential charge (felony/misdemeanor, degree)
5. Note any jurisdictional considerations
6. Flag related or lesser included offenses

Always cite specific statute numbers. Be thorough but precise.
If the facts are insufficient to support a charge, explain what additional \
information would be needed.

DISCLAIMER: This analysis is for investigative assistance only and does not \
constitute legal advice. All conclusions should be reviewed by qualified legal counsel."""

FEDERAL_CRIME_TYPES = [
    ("bank robbery", "18 U.S.C. § 2113"),
    ("wire fraud", "18 U.S.C. § 1343"),
    ("mail fraud", "18 U.S.C. § 1341"),
    ("identity theft / aggravated identity theft", "18 U.S.C. § 1028A"),
    ("drug trafficking (controlled substances)", "21 U.S.C. § 841"),
    ("money laundering", "18 U.S.C. § 1956"),
    ("computer fraud (CFAA)", "18 U.S.C. § 1030"),
    ("securities fraud", "18 U.S.C. § 1348"),
    ("tax evasion", "26 U.S.C. § 7201"),
    ("bribery of a federal public official", "18 U.S.C. § 201"),
    ("kidnapping", "18 U.S.C. § 1201"),
    ("carjacking", "18 U.S.C. § 2119"),
    ("Hobbs Act robbery / extortion", "18 U.S.C. § 1951"),
    ("human trafficking / sex trafficking", "18 U.S.C. § 1591"),
    ("child exploitation (CSAM)", "18 U.S.C. § 2252"),
    ("use of firearm during crime of violence", "18 U.S.C. § 924(c)"),
    ("domestic terrorism / threats against government", "18 U.S.C. § 2332b"),
    ("healthcare fraud", "18 U.S.C. § 1347"),
    ("bank fraud", "18 U.S.C. § 1344"),
    ("civil rights violations under color of law", "18 U.S.C. § 242"),
]

GEORGIA_CRIME_TYPES = [
    ("aggravated assault", "O.C.G.A. § 16-5-21"),
    ("aggravated battery", "O.C.G.A. § 16-5-24"),
    ("armed robbery", "O.C.G.A. § 16-8-41"),
    ("burglary (first degree)", "O.C.G.A. § 16-7-1"),
    ("theft by taking", "O.C.G.A. § 16-8-2"),
    ("DUI and vehicular homicide", "O.C.G.A. § 40-6-393"),
    ("drug trafficking (methamphetamine / cocaine)", "O.C.G.A. § 16-13-31"),
    ("family violence battery / domestic violence", "O.C.G.A. § 16-5-23.1"),
    ("stalking / aggravated stalking", "O.C.G.A. § 16-5-91"),
    ("murder / felony murder", "O.C.G.A. § 16-5-1"),
    ("rape / aggravated sexual battery", "O.C.G.A. § 16-6-1"),
    ("child cruelty / abuse", "O.C.G.A. § 16-5-70"),
    ("arson (first degree)", "O.C.G.A. § 16-7-60"),
    ("fleeing and eluding a police officer", "O.C.G.A. § 40-6-395"),
    ("criminal trespass / criminal damage to property", "O.C.G.A. § 16-7-21"),
]

BATCH_SIZE = 5


def generate_batch(
    client: anthropic.Anthropic,
    jurisdiction: str,
    crime_type: str,
    example_citation: str,
    batch_size: int = BATCH_SIZE,
) -> list[dict]:
    """Generate a batch of incident-to-analysis examples via Claude API."""

    if jurisdiction == "federal":
        code_ref = "U.S. Code Title 18 (and related federal statutes)"
        location_hint = "set in different U.S. cities and states"
    else:
        code_ref = f"Georgia Criminal Code (O.C.G.A. Title 16) and federal law where applicable"
        location_hint = "set in different Georgia cities and counties"

    prompt = f"""Generate {batch_size} realistic law enforcement incident descriptions involving \
{crime_type} under {code_ref}.

Each incident must be {location_hint}, with distinct facts and circumstances.

Return ONLY a valid JSON array of {batch_size} objects. Each object must have exactly these two keys:

{{
  "incident": "<realistic police report style incident description, 150-350 words>",
  "analysis": "<complete criminal law analysis — cite specific statutes like {example_citation}, \
list offense elements, map facts to elements, classify severity, note lesser included offenses \
and additional info needed. Use markdown headers for each statute.>"
}}

Return only the JSON array, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=8192,
            messages=[{"role": "user", "content": prompt}],
        )
    except anthropic.APIError as e:
        print(f"  API error: {e}", file=sys.stderr)
        return []

    text = response.content[0].text.strip()

    start = text.find("[")
    end = text.rfind("]") + 1
    if start == -1 or end == 0:
        print("  Warning: no JSON array found in response", file=sys.stderr)
        return []

    try:
        raw_examples = json.loads(text[start:end])
    except json.JSONDecodeError as e:
        print(f"  Warning: JSON parse error: {e}", file=sys.stderr)
        return []

    formatted = []
    for ex in raw_examples:
        incident = (ex.get("incident") or "").strip()
        analysis = (ex.get("analysis") or "").strip()
        if not incident or not analysis:
            continue
        formatted.append({
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {
                    "role": "user",
                    "content": f"Analyze the following incident for potential criminal violations:\n\n{incident}",
                },
                {"role": "assistant", "content": analysis},
            ],
            "type": "incident_analysis",
            "jurisdiction": jurisdiction,
        })

    return formatted


def count_existing() -> int:
    """Count examples already in the output file."""
    if not OUTPUT_PATH.exists():
        return 0
    with open(OUTPUT_PATH) as f:
        return sum(1 for _ in f)


def append_examples(examples: list[dict]):
    """Append examples to the output JSONL file."""
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, "a") as f:
        for ex in examples:
            f.write(json.dumps(ex, ensure_ascii=False) + "\n")


def main():
    parser = argparse.ArgumentParser(description="Generate synthetic SELMA training data via Claude API")
    parser.add_argument("--count", type=int, default=100, help="Number of examples to generate (default: 100)")
    parser.add_argument(
        "--jurisdiction",
        choices=["federal", "georgia", "all"],
        default="all",
        help="Jurisdiction to generate for (default: all)",
    )
    parser.add_argument("--model", type=str, default="claude-sonnet-4-6", help="Claude model to use")
    args = parser.parse_args()

    client = anthropic.Anthropic()

    existing = count_existing()
    print("=" * 60)
    print("SELMA — Synthetic Data Generator (Claude API)")
    print("=" * 60)
    print(f"Existing examples: {existing}")
    print(f"Target new examples: {args.count}")
    print(f"Jurisdiction: {args.jurisdiction}")
    print()

    if args.jurisdiction == "federal":
        crime_pool = [("federal", ct, cite) for ct, cite in FEDERAL_CRIME_TYPES]
    elif args.jurisdiction == "georgia":
        crime_pool = [("georgia", ct, cite) for ct, cite in GEORGIA_CRIME_TYPES]
    else:
        crime_pool = (
            [("federal", ct, cite) for ct, cite in FEDERAL_CRIME_TYPES]
            + [("georgia", ct, cite) for ct, cite in GEORGIA_CRIME_TYPES]
        )

    generated = 0
    crime_idx = 0

    while generated < args.count:
        remaining = args.count - generated
        batch_size = min(BATCH_SIZE, remaining)

        jur, crime_type, example_citation = crime_pool[crime_idx % len(crime_pool)]
        crime_idx += 1

        print(f"  [{generated}/{args.count}] Generating {batch_size}x {jur} / {crime_type}...", end=" ", flush=True)

        examples = generate_batch(client, jur, crime_type, example_citation, batch_size)

        if examples:
            append_examples(examples)
            generated += len(examples)
            print(f"OK ({len(examples)} saved)")
        else:
            print("FAILED (skipping)")

        # Respect rate limits
        if generated < args.count:
            time.sleep(0.5)

    print()
    print(f"Done. Generated {generated} new examples.")
    print(f"Total in {OUTPUT_PATH}: {count_existing()}")


if __name__ == "__main__":
    main()
