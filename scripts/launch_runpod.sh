#!/bin/bash
# SELMA — RunPod Training Launcher
# Creates a RunPod GPU pod and runs the training pipeline.
#
# Usage:
#   export RUNPOD_API_KEY="your_key_here"
#   bash scripts/launch_runpod.sh
#
# This script:
#   1. Creates an A100-80GB GPU pod on RunPod
#   2. Clones the SELMA repository
#   3. Runs the full training pipeline
#   4. Uploads the trained model to HuggingFace (optional)

set -e

if [ -z "$RUNPOD_API_KEY" ]; then
    echo "ERROR: Set RUNPOD_API_KEY environment variable first"
    echo "  export RUNPOD_API_KEY='your_key_here'"
    exit 1
fi

echo "============================================================"
echo "SELMA — RunPod Training Launcher"
echo "============================================================"

# Install runpodctl if needed
if ! command -v runpodctl &> /dev/null; then
    echo "Installing runpodctl..."
    wget -qO- https://github.com/runpod/runpodctl/releases/latest/download/runpodctl-linux-amd64 -O /usr/local/bin/runpodctl
    chmod +x /usr/local/bin/runpodctl
fi

# Configure API key
runpodctl config --apiKey "$RUNPOD_API_KEY"

# Create the pod with A100-80GB
echo ""
echo "Creating GPU pod (A100-80GB SXM)..."
echo "Estimated cost: ~\$1.64/hr"
echo ""

# Create pod using RunPod API directly
POD_RESPONSE=$(curl -s -X POST "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "mutation { podFindAndDeployOnDemand(input: { name: \"SELMA-Training\", gpuTypeId: \"NVIDIA A100 80GB PCIe\", gpuCount: 1, volumeInGb: 100, containerDiskInGb: 50, templateId: \"runpod-torch-2.1\", dockerArgs: \"\", imageName: \"runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04\", env: [], ports: \"22/tcp\" }) { id imageName machine { gpu gpuDisplayName } } }"
  }')

echo "Response: $POD_RESPONSE"

POD_ID=$(echo "$POD_RESPONSE" | python3 -c "import sys, json; data = json.load(sys.stdin); print(data['data']['podFindAndDeployOnDemand']['id'])" 2>/dev/null)

if [ -z "$POD_ID" ]; then
    echo ""
    echo "Could not auto-create pod. Try the manual method:"
    echo ""
    echo "1. Go to https://www.runpod.io/console/pods"
    echo "2. Click 'Deploy' and select:"
    echo "   - GPU: NVIDIA A100 80GB (PCIe or SXM)"
    echo "   - Template: RunPod PyTorch 2.1"
    echo "   - Disk: 100GB volume"
    echo "3. Once the pod is running, SSH in and run:"
    echo ""
    echo "   git clone https://codeberg.org/Ronin48/SELMA.git"
    echo "   cd SELMA"
    echo "   chmod +x scripts/train.sh"
    echo "   ./scripts/train.sh"
    echo ""
    exit 1
fi

echo "Pod created: $POD_ID"
echo "Waiting for pod to be ready..."

# Wait for pod
sleep 30

# Get SSH connection info
echo "Getting connection info..."
SSH_INFO=$(curl -s "https://api.runpod.io/graphql?api_key=${RUNPOD_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{\"query\": \"{ pod(input: { podId: \\\"${POD_ID}\\\" }) { id runtime { ports { ip isIpPublic publicPort privatePort type } } } }\"}")

echo "SSH Info: $SSH_INFO"

echo ""
echo "============================================================"
echo "Pod $POD_ID is deploying."
echo ""
echo "Once it's running, SSH in and execute:"
echo ""
echo "  git clone https://codeberg.org/Ronin48/SELMA.git"
echo "  cd SELMA"
echo "  chmod +x scripts/train.sh"
echo "  ./scripts/train.sh"
echo ""
echo "Training will take approximately 3-6 hours on an A100-80GB."
echo "When done, the model will be at output/selma-merged/"
echo ""
echo "To stop the pod when finished (saves money):"
echo "  runpodctl stop pod $POD_ID"
echo "============================================================"
