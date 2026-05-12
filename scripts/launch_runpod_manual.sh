#!/bin/bash
# SELMA RunPod Training Launcher (Manual)
#
# This script validates your credentials and prints step-by-step instructions
# to launch a GPU pod on RunPod for SELMA fine-tuning.
#
# Usage: bash scripts/launch_runpod_manual.sh

set -e

echo "============================================================"
echo "SELMA — RunPod Training Setup"
echo "============================================================"
echo ""

# Check for RunPod API key
if [ -z "$RUNPOD_API_KEY" ]; then
    echo "ERROR: RUNPOD_API_KEY not set"
    echo "Set it with: export RUNPOD_API_KEY='your_key_here'"
    exit 1
fi

# Check for HuggingFace token
if [ -z "$HF_TOKEN" ]; then
    echo "ERROR: HF_TOKEN not set"
    echo "Set it with: export HF_TOKEN='your_token_here'"
    exit 1
fi

echo "✓ RUNPOD_API_KEY found"
echo "✓ HF_TOKEN found"
echo ""

echo "============================================================"
echo "Step 1: Create a GPU Pod on RunPod"
echo "============================================================"
echo ""
echo "1. Go to: https://www.runpod.io/console/pods"
echo "2. Click 'Deploy'"
echo "3. Select these options:"
echo "   • GPU: NVIDIA A100 80GB PCIe (or SXM if preferred)"
echo "   • Template: RunPod PyTorch 2.2"
echo "   • Storage: 100GB volume"
echo ""
echo "4. Under 'Environment Variables', add:"
echo "   Key: HF_TOKEN"
echo "   Value: $HF_TOKEN"
echo ""
echo "5. Click 'Deploy On-Demand'"
echo "6. Wait for the pod to show 'Running' status"
echo ""

echo "============================================================"
echo "Step 2: Connect and Train"
echo "============================================================"
echo ""
echo "Once the pod is running:"
echo ""
echo "1. In the RunPod console, click the pod's 'Connect' button"
echo "2. Copy the SSH command (looks like: ssh -p PORT user@HOST)"
echo "3. Paste and run it in your terminal"
echo "4. Once SSH'd into the pod, run:"
echo ""
echo "   git clone https://codeberg.org/Ronin48/SELMA.git"
echo "   cd SELMA"
echo "   ./scripts/train.sh --skip-merge"
echo ""
echo "Training will take 8-10 hours. The adapter saves to output/selma-qlora/final/"
echo ""

echo "============================================================"
echo "Step 3: Upload Adapter (After Training)"
echo "============================================================"
echo ""
echo "When training finishes:"
echo ""
echo "   huggingface-cli upload YOUR-USERNAME/selma-70b-adapter output/selma-qlora/final/"
echo ""
echo "Then open a PR on https://codeberg.org/Ronin48/SELMA with:"
echo "   • HuggingFace adapter URL"
echo "   • GPU used and training time"
echo "   • Which state jurisdiction was trained"
echo ""

echo "============================================================"
echo "Cost Breakdown"
echo "============================================================"
echo ""
echo "A100-80GB on RunPod (on-demand):"
echo "   • Training: ~9 hrs × $2.50/hr = ~$22.50"
echo "   • Setup/buffer: ~$3.50"
echo "   • Total: ~$25-30 per state model"
echo ""
echo "============================================================"
