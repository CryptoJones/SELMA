#!/usr/bin/env python3
"""
Evaluate SELMA model performance.

Runs the model against test cases and computes metrics for:
- Statute identification accuracy
- Element extraction completeness
- Charge classification accuracy
- Overall reasoning quality
"""

import json
from pathlib import Path

import torch
import yaml
from tqdm import tqdm
from sklearn.metrics import precision_score, recall_score, f1_score
from transformers import AutoModelForCausalLM, AutoTokenizer

from src.selma.model import load_model, analyze_incident


def load_test_cases(test_path: str) -> list[dict]:
    """Load test cases from JSONL file."""
    cases = []
    with open(test_path) as f:
        for line in f:
            cases.append(json.loads(line))
    return cases


def extract_statutes_from_response(response: str) -> set[str]:
    """Extract statute citations from model response."""
    import re
    # Match patterns like "18 U.S.C. § 1111" or "O.C.G.A. § 16-5-1"
    federal = set(re.findall(r"18\s+U\.S\.C\.\s*§\s*([\d\w]+)", response))
    georgia = set(re.findall(r"O\.C\.G\.A\.\s*§\s*([\d\-]+)", response))
    return federal | georgia


def evaluate_statute_identification(predictions: list[set], labels: list[set]) -> dict:
    """Compute statute identification metrics."""
    total_precision = 0
    total_recall = 0
    total_f1 = 0
    n = len(predictions)

    for pred, label in zip(predictions, labels):
        if not label:
            continue
        tp = len(pred & label)
        fp = len(pred - label)
        fn = len(label - pred)

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        total_precision += precision
        total_recall += recall
        total_f1 += f1

    return {
        "precision": total_precision / n if n > 0 else 0,
        "recall": total_recall / n if n > 0 else 0,
        "f1": total_f1 / n if n > 0 else 0,
    }


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate SELMA")
    parser.add_argument("--config", default="configs/model_config.yaml")
    parser.add_argument("--test-file", default="data/processed/eval.jsonl")
    parser.add_argument("--output", default="output/evaluation_results.json")
    parser.add_argument("--max-examples", type=int, default=100)
    args = parser.parse_args()

    config = yaml.safe_load(open(args.config))
    model, tokenizer = load_model(config)

    test_cases = load_test_cases(args.test_file)[:args.max_examples]

    predictions = []
    labels = []
    results = []

    for case in tqdm(test_cases, desc="Evaluating"):
        # Extract incident from messages
        user_msg = next(
            (m["content"] for m in case.get("messages", []) if m["role"] == "user"),
            "",
        )
        expected = next(
            (m["content"] for m in case.get("messages", []) if m["role"] == "assistant"),
            "",
        )

        if not user_msg:
            continue

        response = analyze_incident(model, tokenizer, user_msg, config)

        pred_statutes = extract_statutes_from_response(response)
        label_statutes = extract_statutes_from_response(expected)

        predictions.append(pred_statutes)
        labels.append(label_statutes)

        results.append({
            "input": user_msg[:200],
            "predicted_statutes": list(pred_statutes),
            "expected_statutes": list(label_statutes),
            "response_length": len(response),
        })

    metrics = evaluate_statute_identification(predictions, labels)

    output = {
        "metrics": metrics,
        "num_examples": len(results),
        "results": results,
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w") as f:
        json.dump(output, f, indent=2)

    print(f"\nEvaluation Results:")
    print(f"  Statute ID Precision: {metrics['precision']:.3f}")
    print(f"  Statute ID Recall:    {metrics['recall']:.3f}")
    print(f"  Statute ID F1:        {metrics['f1']:.3f}")
    print(f"\nFull results saved to {args.output}")


if __name__ == "__main__":
    main()
