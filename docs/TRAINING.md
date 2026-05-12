# SELMA Training Guide

## Prerequisites

### Hardware Requirements

| Model | GPU | VRAM | Notes |
|-------|-----|------|-------|
| Llama 3.1 70B (QLoRA) | A100-80GB | ~72GB | Recommended |
| Llama 3.1 70B (QLoRA) | 2x A100-40GB | ~80GB | Multi-GPU alternative |
| Llama 3.1 70B (QLoRA) | H100-80GB | ~72GB | Fastest option |
| Llama 3.1 8B (QLoRA) | RTX 4090 | ~16GB | Lightweight/dev option |

### Software Requirements

- Python 3.10+
- CUDA 12.1+
- PyTorch 2.3+
- Flash Attention 2 (`pip install flash-attn --no-build-isolation`) — optional but strongly recommended for training speed; falls back to `sdpa` if not installed

### HuggingFace Authentication

Llama 3.1 70B is a gated model. Before downloading:

1. Accept the license at https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct
2. Authenticate:

```bash
huggingface-cli login
# or: export HF_TOKEN='hf_...' before running train.sh
```

## Step 1: Data Collection

```bash
# Download federal statutes (U.S. Code Title 18)
# The script automatically discovers the current release from uscode.house.gov
python scripts/data_collection/fetch_federal_statutes.py

# Download Georgia statutes (O.C.G.A. Title 16)
python scripts/data_collection/fetch_georgia_statutes.py

# Download legal NLP datasets from HuggingFace
python scripts/data_collection/fetch_legal_datasets.py

# Generate synthetic incident-to-charge training examples (~50K)
python scripts/data_collection/generate_synthetic.py
```

## Step 2: Dataset Preparation

```bash
python scripts/training/prepare_dataset.py
```

This combines:
- Statute knowledge examples (federal + Georgia)
- Synthetic incident-to-charge training examples
- Legal reasoning examples from HuggingFace datasets

> **Note:** If `data/synthetic/synthetic_training.jsonl` does not exist (i.e.,
> `generate_synthetic.py` was not run), the synthetic examples are silently
> skipped. The pipeline will still work but with ~50K fewer training examples.

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

> **RAM requirement:** Merging loads the full 70B model in float16 on CPU — expect ~140GB
> of system RAM. On machines with less RAM, the process will OOM. Consider using a
> high-memory CPU instance (e.g., AWS r6i.48xlarge, 1.5TB RAM) for this step only.

## Step 5: Evaluation

```bash
python scripts/evaluation/evaluate_model.py \
    --config configs/model_config.yaml \
    --test-file data/processed/eval.jsonl \
    --output output/evaluation_results.json
```

## Tips

- Use Llama 3.1 8B for faster iteration before scaling to 70B
- Use the benchmark suite (`scripts/evaluation/benchmark_suite.py`) for qualitative testing
- Monitor VRAM usage with `nvidia-smi` during training
- If you run out of memory, reduce `per_device_train_batch_size` or `max_seq_length`
