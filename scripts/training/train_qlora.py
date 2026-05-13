#!/usr/bin/env python3
"""
SELMA QLoRA Fine-tuning Script.

Fine-tunes Llama 3.1 70B with QLoRA for criminal law analysis.
Requires: A100-80GB GPU (or equivalent).
"""

import argparse
import json
import os
from pathlib import Path

import torch
import yaml
from datasets import load_dataset
from peft import LoraConfig, get_peft_model, prepare_model_for_kbit_training
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BitsAndBytesConfig,
    TrainingArguments,
)
from trl import SFTTrainer


def load_config(config_path: str) -> dict:
    """Load training configuration."""
    with open(config_path) as f:
        return yaml.safe_load(f)


def setup_model(config: dict):
    """Load and prepare model for QLoRA training."""
    model_name = config["model"]["name"]
    quant_config = config["quantization"]
    lora_config = config["lora"]

    print(f"Loading model: {model_name}")

    # Quantization config
    bnb_config = BitsAndBytesConfig(
        load_in_4bit=quant_config["load_in_4bit"],
        bnb_4bit_compute_dtype=getattr(torch, quant_config["bnb_4bit_compute_dtype"]),
        bnb_4bit_quant_type=quant_config["bnb_4bit_quant_type"],
        bnb_4bit_use_double_quant=quant_config["bnb_4bit_use_double_quant"],
    )

    # Load model
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        quantization_config=bnb_config,
        attn_implementation=config["model"].get("attn_implementation", "eager"),
        trust_remote_code=True,
    )

    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Prepare for k-bit training
    model = prepare_model_for_kbit_training(model, use_gradient_checkpointing=True)

    # LoRA config
    peft_config = LoraConfig(
        r=lora_config["r"],
        lora_alpha=lora_config["lora_alpha"],
        lora_dropout=lora_config["lora_dropout"],
        target_modules=lora_config["target_modules"],
        task_type=lora_config["task_type"],
        bias=lora_config["bias"],
    )

    model = get_peft_model(model, peft_config)
    model.print_trainable_parameters()

    return model, tokenizer


def load_training_data(config: dict):
    """Load training and evaluation datasets."""
    data_config = config["data"]

    train_dataset = load_dataset(
        "json",
        data_files=data_config["train_file"],
        split="train",
    )

    eval_dataset = None
    if data_config.get("eval_file"):
        eval_dataset = load_dataset(
            "json",
            data_files=data_config["eval_file"],
            split="train",
        )

    print(f"Train: {len(train_dataset)} examples")
    if eval_dataset:
        print(f"Eval: {len(eval_dataset)} examples")

    return train_dataset, eval_dataset


def train(config: dict):
    """Run QLoRA fine-tuning."""
    model, tokenizer = setup_model(config)
    train_dataset, eval_dataset = load_training_data(config)

    training_config = config["training"]

    training_args = TrainingArguments(
        output_dir=training_config["output_dir"],
        num_train_epochs=training_config["num_train_epochs"],
        per_device_train_batch_size=training_config["per_device_train_batch_size"],
        per_device_eval_batch_size=training_config.get("per_device_eval_batch_size", 2),
        gradient_accumulation_steps=training_config["gradient_accumulation_steps"],
        learning_rate=training_config["learning_rate"],
        weight_decay=training_config.get("weight_decay", 0.01),
        warmup_ratio=training_config.get("warmup_ratio", 0.05),
        lr_scheduler_type=training_config.get("lr_scheduler_type", "cosine"),
        logging_steps=training_config.get("logging_steps", 10),
        save_steps=training_config.get("save_steps", 200),
        eval_steps=training_config.get("eval_steps", 200),
        eval_strategy=training_config.get("eval_strategy", "steps"),
        save_total_limit=training_config.get("save_total_limit", 3),
        bf16=training_config.get("bf16", True),
        gradient_checkpointing=training_config.get("gradient_checkpointing", True),
        max_grad_norm=training_config.get("max_grad_norm", 1.0),
        group_by_length=training_config.get("group_by_length", True),
        dataloader_num_workers=training_config.get("dataloader_num_workers", 4),
        report_to=training_config.get("report_to", "none"),
        seed=config.get("seed", 42),
    )

    trainer = SFTTrainer(
        model=model,
        processing_class=tokenizer,
        args=training_args,
        train_dataset=train_dataset,
        eval_dataset=eval_dataset,
        max_seq_length=config["data"].get("max_seq_length", 4096),
    )

    print("\nStarting training...")
    trainer.train()

    # Save final adapter
    final_path = Path(training_config["output_dir"]) / "final"
    trainer.save_model(str(final_path))
    tokenizer.save_pretrained(str(final_path))
    print(f"\nModel saved to {final_path}")


def main():
    parser = argparse.ArgumentParser(description="SELMA QLoRA Training")
    parser.add_argument(
        "--config",
        type=str,
        default="configs/training_config.yaml",
        help="Path to training config",
    )
    args = parser.parse_args()

    config = load_config(args.config)
    train(config)


if __name__ == "__main__":
    main()
