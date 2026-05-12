#!/bin/bash
# SELMA MLX LoRA Training — Apple Silicon
#
# Run this on a Mac with Apple Silicon (M1/M2/M3).
# Requires: pip install mlx-lm
#
# Usage:
#   chmod +x scripts/training/train_mlx.sh
#   ./scripts/training/train_mlx.sh
#   ./scripts/training/train_mlx.sh --iters 2000   # higher quality, longer run

set -e

echo "============================================================"
echo "SELMA — MLX Training (Apple Silicon)"
echo "============================================================"

# Check we're on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "ERROR: This script requires Apple Silicon (M1/M2/M3)."
    echo "Use scripts/train.sh for CUDA GPUs."
    exit 1
fi

# Check mlx-lm is installed
if ! python3 -c "import mlx_lm" 2>/dev/null; then
    echo "Installing mlx-lm..."
    pip install mlx-lm
fi

# Check HuggingFace auth
if ! huggingface-cli whoami &>/dev/null; then
    echo "ERROR: Not logged in to HuggingFace."
    echo "Run: huggingface-cli login"
    echo "Then accept the license at: https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct"
    exit 1
fi

# Parse optional args (pass-through to mlx_lm.lora)
EXTRA_ARGS="$@"

# Collect data if not already done
if [ ! -f "data/processed/train.jsonl" ]; then
    echo "Step 1: Collecting training data..."
    python scripts/data_collection/fetch_federal_statutes.py
    python scripts/data_collection/fetch_state_statutes.py --jurisdiction georgia
    python scripts/data_collection/fetch_legal_datasets.py
    python scripts/data_collection/generate_synthetic.py
    python scripts/training/prepare_dataset.py
else
    echo "Step 1: Training data already prepared — skipping."
fi

# Train
echo ""
echo "Step 2: Training with MLX LoRA..."
echo "  Model: meta-llama/Llama-3.1-8B-Instruct"
echo "  Config: configs/training_config_mlx.yaml"
echo ""

mlx_lm.lora --config configs/training_config_mlx.yaml $EXTRA_ARGS

# Fuse adapter into model
echo ""
echo "Step 3: Fusing LoRA adapter into model weights..."
mlx_lm.fuse \
    --model meta-llama/Llama-3.1-8B-Instruct \
    --adapter-path output/selma-mlx-adapters \
    --save-path output/selma-mlx-merged \
    --de-quantize

echo ""
echo "============================================================"
echo "Training complete!"
echo "  Adapter : output/selma-mlx-adapters/"
echo "  Merged  : output/selma-mlx-merged/"
echo ""
echo "Next: convert to GGUF for Ollama"
echo "  ./scripts/export_ollama.sh --model-path output/selma-mlx-merged"
echo "============================================================"
