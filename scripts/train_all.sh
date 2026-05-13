#!/bin/bash
# Train all Ronin 48 models sequentially on a single pod.
# Run this from /workspace after fixing deps.
#
# Usage:
#   HF_TOKEN=hf_... bash <(curl -s https://codeberg.org/Ronin48/SELMA/raw/branch/main/scripts/train_all.sh)

set -e

WORKSPACE="${WORKSPACE:-/workspace}"
LOG="$WORKSPACE/logs/train_all.log"
mkdir -p "$WORKSPACE/logs"
exec > >(tee -a "$LOG") 2>&1

export HF_HOME="$WORKSPACE/hf_cache"
export TRANSFORMERS_CACHE="$HF_HOME"
mkdir -p "$HF_HOME"

if [ -z "$HF_TOKEN" ]; then
    echo "ERROR: HF_TOKEN is not set."
    exit 1
fi

MODELS="ABBY SELMA BONES BRUNO"

for MODEL in $MODELS; do
    echo ""
    echo "============================================================"
    echo "  Starting $MODEL — $(date)"
    echo "============================================================"

    REPO_URL="https://codeberg.org/Ronin48/$MODEL.git"
    REPO_DIR="$WORKSPACE/$MODEL"

    if [ -d "$REPO_DIR/.git" ]; then
        echo "[git] updating $MODEL..."
        git -C "$REPO_DIR" pull
    else
        echo "[git] cloning $MODEL..."
        git clone "$REPO_URL" "$REPO_DIR"
    fi

    cd "$REPO_DIR"

    echo "[data] generating synthetic examples..."
    python scripts/data_collection/generate_synthetic.py

    echo "[data] preparing dataset..."
    python scripts/training/prepare_dataset.py

    echo "[train] starting QLoRA training for $MODEL..."
    python scripts/training/train_qlora.py --config configs/training_config.yaml

    echo "✓ $MODEL complete — $(date)"
    cd "$WORKSPACE"
done

echo ""
echo "============================================================"
echo "  All models complete: $MODELS"
echo "  ATTICUS is ON HOLD — top up credits before queuing."
echo "============================================================"
