#!/usr/bin/env python3
"""
SELMA Multi-State Training Script.

Trains a SELMA model for a specific state jurisdiction.
Each state model includes federal law (Title 18) as baseline.

Usage:
    python scripts/training/train_state.py --state georgia
    python scripts/training/train_state.py --state federal
    python scripts/training/train_state.py --state all  # Train all available
"""

import argparse
import json
import sys
from pathlib import Path

import yaml


def get_available_states() -> list[str]:
    """List all states that have training data ready."""
    models_dir = Path("models")
    ready = []
    for state_dir in sorted(models_dir.iterdir()):
        if not state_dir.is_dir():
            continue
        config_path = state_dir / "config.yaml"
        if not config_path.exists():
            continue
        # Check if training data exists
        with open(config_path) as f:
            config = yaml.safe_load(f)
        federal_data = Path(config["training"]["federal_data"])
        has_federal = federal_data.exists()
        state_data_path = config["training"].get("state_data")
        has_state = True  # federal model doesn't need state data
        if state_data_path:
            has_state = Path(state_dir / state_data_path).exists()
        if has_federal:
            ready.append(state_dir.name)
    return ready


def prepare_state_dataset(state: str) -> tuple[Path, Path]:
    """Prepare training dataset for a specific state."""
    from scripts.training.prepare_dataset import (
        load_statute_knowledge,
        split_dataset,
        save_dataset,
    )

    state_dir = Path(f"models/{state}")
    config_path = state_dir / "config.yaml"

    with open(config_path) as f:
        config = yaml.safe_load(f)

    print(f"\nPreparing dataset for: {config['jurisdiction']['name']}")
    print(f"Criminal code: {config['jurisdiction']['code_citation']}")

    # Load federal baseline (always included)
    all_examples = load_statute_knowledge()
    print(f"  Federal baseline: {len(all_examples)} examples")

    # Load state-specific synthetic data if available
    synthetic_path = state_dir / config["training"]["synthetic_data"]
    if synthetic_path.exists():
        with open(synthetic_path) as f:
            for line in f:
                all_examples.append(json.loads(line))
        print(f"  State synthetic: {sum(1 for _ in open(synthetic_path))} examples")

    # Load state statute data if available
    state_data_path = config["training"].get("state_data")
    if state_data_path:
        full_state_path = state_dir / state_data_path
        if full_state_path.exists():
            with open(full_state_path) as f:
                state_statutes = json.load(f)
            # Create knowledge examples from state statutes
            system_prompt = "You are SELMA, an AI assistant trained to help law enforcement identify potential violations of criminal law."
            for section_num, statute in state_statutes.items():
                if statute.get("title") and statute.get("text"):
                    all_examples.append({
                        "messages": [
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": f"What are the key provisions of {statute.get('citation', section_num)}?"},
                            {"role": "assistant", "content": f"## {statute.get('citation', section_num)} — {statute['title']}\n\n{statute['text']}"},
                        ],
                        "type": "statute_knowledge",
                        "jurisdiction": state,
                    })
            print(f"  State statutes: {len(state_statutes)} sections")

    print(f"  Total examples: {len(all_examples)}")

    # Split and save
    output_dir = Path(config["training"]["output_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)

    train, eval_set = split_dataset(all_examples)

    train_path = output_dir / "train.jsonl"
    eval_path = output_dir / "eval.jsonl"

    save_dataset(train, train_path)
    save_dataset(eval_set, eval_path)

    print(f"  Train: {len(train)}, Eval: {len(eval_set)}")
    return train_path, eval_path


def train_state(state: str):
    """Train a SELMA model for a specific state."""
    state_dir = Path(f"models/{state}")
    config_path = state_dir / "config.yaml"

    if not config_path.exists():
        print(f"ERROR: No config found for state '{state}'")
        print(f"Expected: {config_path}")
        sys.exit(1)

    with open(config_path) as f:
        state_config = yaml.safe_load(f)

    # Load base training config
    base_config_path = state_dir / state_config["training"]["base_config"]
    with open(base_config_path) as f:
        training_config = yaml.safe_load(f)

    # Override output directory
    training_config["training"]["output_dir"] = state_config["training"]["output_dir"]

    print("=" * 60)
    print(f"SELMA — Training model for: {state_config['jurisdiction']['name']}")
    print(f"Criminal code: {state_config['jurisdiction']['code_citation']}")
    print(f"Base model: {state_config['model']['base']}")
    print("=" * 60)

    # Prepare dataset
    train_path, eval_path = prepare_state_dataset(state)

    # Update data paths
    training_config["data"]["train_file"] = str(train_path)
    training_config["data"]["eval_file"] = str(eval_path)

    # Run training
    from scripts.training.train_qlora import train
    train(training_config)

    print(f"\nModel saved to {state_config['training']['output_dir']}")


def main():
    parser = argparse.ArgumentParser(description="SELMA Multi-State Training")
    parser.add_argument(
        "--state",
        type=str,
        required=True,
        help="State to train (e.g., 'georgia', 'federal', 'all', 'list')",
    )
    parser.add_argument(
        "--prepare-only",
        action="store_true",
        help="Only prepare the dataset, don't train",
    )
    args = parser.parse_args()

    if args.state == "list":
        available = get_available_states()
        print("Available states with training data:")
        for s in available:
            print(f"  - {s}")
        print(f"\nTotal: {len(available)} states ready")
        return

    if args.state == "all":
        available = get_available_states()
        print(f"Training all {len(available)} available states...")
        for state in available:
            if args.prepare_only:
                prepare_state_dataset(state)
            else:
                train_state(state)
        return

    if args.prepare_only:
        prepare_state_dataset(args.state)
    else:
        train_state(args.state)


if __name__ == "__main__":
    main()
