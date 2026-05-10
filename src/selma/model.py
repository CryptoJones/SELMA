"""
SELMA model loading and inference.

Handles loading the base model with QLoRA adapter,
and running inference for criminal law analysis.
"""

import argparse
import json
import sys
from pathlib import Path

import torch
import yaml
from transformers import AutoModelForCausalLM, AutoTokenizer, BitsAndBytesConfig
from peft import PeftModel

from .prompts import format_analysis_prompt


def load_config(config_path: str = "configs/model_config.yaml") -> dict:
    """Load model configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def load_model(config: dict, device_map: str = "auto"):
    """Load SELMA model with QLoRA adapter.

    Args:
        config: Model configuration dict.
        device_map: Device mapping strategy.

    Returns:
        Tuple of (model, tokenizer).
    """
    model_name = config["model"]["base"]
    adapter_path = config["model"].get("adapter_path")
    merged_path = config["model"].get("merged_path")

    # If a merged model exists, load it directly
    if merged_path and Path(merged_path).exists():
        print(f"Loading merged model from {merged_path}...")
        model = AutoModelForCausalLM.from_pretrained(
            merged_path,
            torch_dtype=torch.bfloat16,
            device_map=device_map,
            attn_implementation="flash_attention_2",
        )
        tokenizer = AutoTokenizer.from_pretrained(merged_path)
        return model, tokenizer

    # Otherwise, load base + adapter
    print(f"Loading base model {model_name}...")
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=True,
        bnb_4bit_compute_dtype=torch.bfloat16,
        bnb_4bit_quant_type="nf4",
        bnb_4bit_use_double_quant=True,
    )

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        device_map=device_map,
        attn_implementation="flash_attention_2",
    )

    tokenizer = AutoTokenizer.from_pretrained(model_name)

    if adapter_path and Path(adapter_path).exists():
        print(f"Loading LoRA adapter from {adapter_path}...")
        model = PeftModel.from_pretrained(model, adapter_path)

    return model, tokenizer


def analyze_incident(
    model,
    tokenizer,
    incident: str,
    config: dict,
    thinking_mode: bool = True,
) -> str:
    """Analyze an incident description for potential criminal violations.

    Args:
        model: The loaded SELMA model.
        tokenizer: The tokenizer.
        incident: Incident description text.
        config: Model configuration dict.
        thinking_mode: Enable chain-of-thought reasoning.

    Returns:
        Analysis text.
    """
    messages = format_analysis_prompt(incident)

    if thinking_mode:
        # Enable Qwen3 thinking mode
        messages[0]["content"] = "/think\n" + messages[0]["content"]

    text = tokenizer.apply_chat_template(
        messages,
        tokenize=False,
        add_generation_prompt=True,
    )

    inputs = tokenizer(text, return_tensors="pt").to(model.device)

    inference_config = config.get("inference", {})
    with torch.no_grad():
        outputs = model.generate(
            **inputs,
            max_new_tokens=inference_config.get("max_new_tokens", 2048),
            temperature=inference_config.get("temperature", 0.3),
            top_p=inference_config.get("top_p", 0.9),
            top_k=inference_config.get("top_k", 50),
            repetition_penalty=inference_config.get("repetition_penalty", 1.05),
            do_sample=inference_config.get("do_sample", True),
        )

    response = tokenizer.decode(
        outputs[0][inputs["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )

    return response


def main():
    """CLI entry point for SELMA inference."""
    parser = argparse.ArgumentParser(description="SELMA — Criminal Law Analysis")
    parser.add_argument("--input", type=str, help="Incident description text")
    parser.add_argument("--input-file", type=str, help="File containing incident description")
    parser.add_argument("--config", type=str, default="configs/model_config.yaml")
    parser.add_argument("--no-thinking", action="store_true", help="Disable thinking mode")
    parser.add_argument("--output", type=str, help="Output file path")
    args = parser.parse_args()

    if not args.input and not args.input_file:
        print("Error: Provide --input or --input-file", file=sys.stderr)
        sys.exit(1)

    incident = args.input
    if args.input_file:
        with open(args.input_file) as f:
            incident = f.read()

    config = load_config(args.config)
    model, tokenizer = load_model(config)

    print("Analyzing incident...\n")
    result = analyze_incident(
        model, tokenizer, incident, config,
        thinking_mode=not args.no_thinking,
    )

    if args.output:
        with open(args.output, "w") as f:
            f.write(result)
        print(f"Analysis saved to {args.output}")
    else:
        print(result)


if __name__ == "__main__":
    main()
