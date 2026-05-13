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
export HF_HUB_DISABLE_XET=1  # workaround for XET background writer crash on large model downloads

# bitsandbytes CUDA 13 library (installed via pip nvidia packages)
_nvidia_lib=$(python3 -c "import site; print(site.getsitepackages()[0])")/nvidia/cu13/lib
[ -d "$_nvidia_lib" ] && export LD_LIBRARY_PATH="$_nvidia_lib:${LD_LIBRARY_PATH:-}"
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
# torchvision ships pre-built for older torch and breaks on torch 2.11+
pip uninstall -q -y torchvision 2>/dev/null || true
pip install -q --upgrade \
    "transformers>=4.46.0,<4.50.0" \
    "peft" \
    "trl>=0.12.0,<1.0.0" \
    "bitsandbytes" \
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

# Train — nohup so terminal disconnects don't kill the process
echo "[train] starting QLoRA training..."
nohup python scripts/training/train_qlora.py --config configs/training_config.yaml >> "$LOG" 2>&1 &
TRAIN_PID=$!
echo "[train] PID $TRAIN_PID — follow logs: tail -f $LOG"
wait $TRAIN_PID

echo "=== $REPO_NAME training complete $(date) ==="

# Upload adapter to HuggingFace
ADAPTER_DIR="$REPO_DIR/output/selma-qlora/final"
HF_REPO="Ronin48/selma-lora-adapter"
if [ -d "$ADAPTER_DIR" ]; then
    echo "[upload] pushing adapter to $HF_REPO..."
    huggingface-cli upload "$HF_REPO" "$ADAPTER_DIR" --token "$HF_TOKEN"
    echo "[upload] done: $HF_REPO"
else
    echo "[upload] WARNING: adapter not found at $ADAPTER_DIR — upload manually"
fi
