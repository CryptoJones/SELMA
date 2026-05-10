#!/bin/bash
# SELMA Training Launch Script
# Run this on a machine with an A100-80GB GPU (or equivalent)
#
# Prerequisites:
#   - NVIDIA GPU with 80GB+ VRAM (A100-80GB recommended)
#   - CUDA 12.1+
#   - Python 3.10+
#
# Usage:
#   chmod +x scripts/train.sh
#   ./scripts/train.sh

set -e

echo "============================================================"
echo "SELMA — Training Pipeline"
echo "Specified Encapsulated Limitless Memory Archive"
echo "============================================================"
echo ""

# Check GPU
if ! command -v nvidia-smi &> /dev/null; then
    echo "ERROR: nvidia-smi not found. This script requires a CUDA-capable GPU."
    echo "Recommended: A100-80GB or H100-80GB"
    exit 1
fi

echo "GPU Info:"
nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo ""

# Check HuggingFace token (required for Llama 3.1 gated model)
if [ -z "$HF_TOKEN" ]; then
    echo "WARNING: HF_TOKEN not set. Llama 3.1 is a gated model."
    echo "You need to:"
    echo "  1. Accept the license at https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct"
    echo "  2. Set your token: export HF_TOKEN='hf_...'"
    echo ""
    read -p "Enter HuggingFace token (or press Enter to try without): " HF_TOKEN
    if [ -n "$HF_TOKEN" ]; then
        export HF_TOKEN
    fi
fi

if [ -n "$HF_TOKEN" ]; then
    echo "HuggingFace token set. Logging in..."
    huggingface-cli login --token "$HF_TOKEN" 2>/dev/null || true
fi
echo ""

# Install dependencies
echo "Step 1: Installing dependencies..."
pip install -r requirements.txt
pip install flash-attn --no-build-isolation 2>/dev/null || echo "Note: flash-attn install failed (optional but recommended)"
echo ""

# Check if data already exists
if [ ! -f "data/processed/train.jsonl" ]; then
    echo "Step 2: Collecting training data..."

    # Federal statutes
    if [ ! -f "data/processed/federal_statutes.json" ]; then
        echo "  Fetching U.S. Code Title 18..."
        python scripts/data_collection/fetch_federal_statutes.py
    fi

    # Georgia statutes
    if [ ! -f "data/processed/georgia_statutes.json" ]; then
        echo "  Fetching Georgia O.C.G.A. Title 16..."
        python scripts/data_collection/fetch_georgia_statutes.py
    fi

    # Synthetic data
    if [ ! -f "data/synthetic/synthetic_training.jsonl" ]; then
        echo "  Generating synthetic training data..."
        python scripts/data_collection/generate_synthetic.py
    fi

    # Prepare dataset
    echo "  Preparing training dataset..."
    python scripts/training/prepare_dataset.py
else
    echo "Step 2: Training data already prepared. Skipping collection."
fi
echo ""

# Train
echo "Step 3: Starting QLoRA fine-tuning..."
echo "  Base model: meta-llama/Llama-3.1-70B-Instruct"
echo "  Method: QLoRA (4-bit NF4)"
echo "  LoRA rank: 64, alpha: 128"
echo "  This will take 6-10 hours on a single A100-80GB." 
echo ""

python scripts/training/train_qlora.py --config configs/training_config.yaml

echo ""
echo "Step 4: Merging adapter..."
python scripts/training/merge_adapter.py --config configs/model_config.yaml

echo ""
echo "Step 5: Running evaluation..."
python scripts/evaluation/evaluate_model.py \
    --config configs/model_config.yaml \
    --test-file data/processed/eval.jsonl \
    --output output/evaluation_results.json

echo ""
echo "============================================================"
echo "SELMA training complete!"
echo "Merged model: output/selma-merged/"
echo "Evaluation: output/evaluation_results.json"
echo "============================================================"
