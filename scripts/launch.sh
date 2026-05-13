#!/bin/bash
# SELMA — infrastructure-agnostic training launcher
#
# Works on any Linux machine with an NVIDIA GPU and internet access.
# Tested on: RunPod, Lambda Labs, Vast.ai, local workstation
#
# Usage:
#   bash scripts/launch.sh
#
# Or from a fresh machine (no repo cloned yet):
#   bash <(curl -s https://codeberg.org/Ronin48/SELMA/raw/branch/main/scripts/launch.sh)

set -e

REPO_URL="https://codeberg.org/Ronin48/SELMA.git"
REPO_NAME="SELMA"
WORKSPACE="${WORKSPACE:-/workspace}"
REPO_DIR="$WORKSPACE/$REPO_NAME"
LOG_DIR="$WORKSPACE/logs"
LOG="$LOG_DIR/train.log"

mkdir -p "$LOG_DIR"
exec > >(tee -a "$LOG") 2>&1

echo "=== $REPO_NAME training launch $(date) ==="
echo "Workspace: $WORKSPACE"

# HuggingFace cache — always on the large volume, never the container disk
export HF_HOME="${HF_HOME:-$WORKSPACE/hf_cache}"
export TRANSFORMERS_CACHE="$HF_HOME"
mkdir -p "$HF_HOME"
echo "HF cache: $HF_HOME"

# Validate HF token
if [ -z "$HF_TOKEN" ]; then
    echo "ERROR: HF_TOKEN is not set. Export it before running:"
    echo "  export HF_TOKEN=your_token_here"
    exit 1
fi
echo "HF_TOKEN: set"

# Clone or update repo
if [ -d "$REPO_DIR/.git" ]; then
    echo "[git] updating $REPO_NAME..."
    git -C "$REPO_DIR" pull
else
    echo "[git] cloning $REPO_NAME..."
    git clone "$REPO_URL" "$REPO_DIR"
fi
cd "$REPO_DIR"

# Dependencies
echo "[pip] upgrading pip..."
pip install -q --upgrade pip

echo "[pip] installing dependencies..."
pip install -q \
    "transformers==4.44.2" \
    "peft==0.12.0" \
    "trl==0.11.4" \
    "bitsandbytes==0.43.1" \
    "accelerate" \
    "datasets" \
    "pyyaml" \
    "requests" \
    "tqdm" \
    "rich"

# Data
echo "[data] generating synthetic examples..."
python scripts/data_collection/generate_synthetic.py

echo "[data] preparing dataset..."
python scripts/training/prepare_dataset.py

# Train
echo "[train] starting QLoRA training..."
python scripts/training/train_qlora.py --config configs/training_config.yaml

echo "=== $REPO_NAME training complete $(date) ==="
