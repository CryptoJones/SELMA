# SELMA Training Guide

## Prerequisites

### Hardware Requirements

| Model | GPU | VRAM | Notes |
|-------|-----|------|-------|
| Qwen3-32B (QLoRA) | A100-80GB | ~64GB | Recommended |
| Qwen3-32B (QLoRA) | 2x A100-40GB | ~80GB | Multi-GPU alternative |
| Qwen3-14B (QLoRA) | A100-40GB | ~28GB | Budget option |
| Qwen3-14B (QLoRA) | RTX 4090 x2 | ~48GB | Consumer option |

### Software Requirements

- Python 3.10+
- CUDA 12.1+
- PyTorch 2.3+
- Flash Attention 2

## Step 1: Data Collection

```bash
# Download federal statutes (U.S. Code Title 18)
python scripts/data_collection/fetch_federal_statutes.py

# Download Georgia statutes (O.C.G.A. Title 16)
python scripts/data_collection/fetch_georgia_statutes.py

# Download legal NLP datasets from HuggingFace
python scripts/data_collection/fetch_legal_datasets.py
```

## Step 2: Dataset Preparation

```bash
python scripts/training/prepare_dataset.py
```

This combines:
- Statute knowledge examples (federal + Georgia)
- Synthetic incident-to-charge training examples
- Legal reasoning examples from HuggingFace datasets

Output: `data/processed/train.jsonl` and `data/processed/eval.jsonl`

## Step 3: Fine-tuning

```bash
python scripts/training/train_qlora.py --config configs/training_config.yaml
```

### Key Training Parameters

- **LoRA rank:** 64
- **LoRA alpha:** 128
- **Learning rate:** 2e-4 with cosine decay
- **Batch size:** 2 per device, 8 gradient accumulation = effective 16
- **Epochs:** 3
- **Max sequence length:** 4096 tokens

### Monitoring

Training logs are saved to `output/selma-qlora/`. Monitor loss curves for convergence.

## Step 4: Merge Adapter

```bash
python scripts/training/merge_adapter.py --config configs/model_config.yaml
```

This creates a standalone model at `output/selma-merged/` that can be loaded without PEFT.

## Step 5: Evaluation

```bash
python scripts/evaluation/evaluate_model.py \
    --config configs/model_config.yaml \
    --test-file data/processed/eval.jsonl \
    --output output/evaluation_results.json
```

## Tips

- Start with Qwen3-14B for faster iteration before scaling to 32B
- Use the benchmark suite (`scripts/evaluation/benchmark_suite.py`) for qualitative testing
- Monitor VRAM usage with `nvidia-smi` during training
- If you run out of memory, reduce `per_device_train_batch_size` or `max_seq_length`
