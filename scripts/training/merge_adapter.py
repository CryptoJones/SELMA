#!/usr/bin/env python3
"""
Merge QLoRA adapter weights into the base model.

Creates a standalone model that can be loaded without PEFT.
"""

import argparse

import torch
import yaml
from peft import PeftModel
from transformers import AutoModelForCausalLM, AutoTokenizer


def load_config(config_path: str) -> dict:
    with open(config_path) as f:
        return yaml.safe_load(f)


def merge_adapter(config: dict):
    """Merge LoRA adapter into base model."""
    base_model_name = config["model"]["base"]
    adapter_path = config["model"]["adapter_path"]
    merged_path = config["model"]["merged_path"]

    print(f"Loading base model: {base_model_name}")
    model = AutoModelForCausalLM.from_pretrained(
        base_model_name,
        torch_dtype=torch.bfloat16,
        device_map="cpu",  # Merge on CPU to avoid OOM
        trust_remote_code=True,
    )

    tokenizer = AutoTokenizer.from_pretrained(base_model_name, trust_remote_code=True)

    print(f"Loading adapter from: {adapter_path}")
    model = PeftModel.from_pretrained(model, adapter_path)

    print("Merging adapter weights...")
    model = model.merge_and_unload()

    print(f"Saving merged model to: {merged_path}")
    model.save_pretrained(merged_path)
    tokenizer.save_pretrained(merged_path)

    print("Done! Merged model saved.")


def main():
    parser = argparse.ArgumentParser(description="Merge SELMA LoRA adapter")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/model_config.yaml",
        help="Path to model config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    merge_adapter(config)


if __name__ == "__main__":
    main()
