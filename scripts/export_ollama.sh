#!/bin/bash
# SELMA → Ollama Export Pipeline
#
# Converts a merged SELMA model to GGUF format and registers it with Ollama.
# Supports both the 8B community model and the full 70B model.
#
# Usage:
#   ./scripts/export_ollama.sh                        # 8B default paths
#   ./scripts/export_ollama.sh --model-path ./output/selma-merged --name selma-70b
#   ./scripts/export_ollama.sh --quant Q5_K_M         # higher quality quantization
#   ./scripts/export_ollama.sh --push username/selma  # build + push to Ollama registry
#
# Requirements:
#   - ollama installed (https://ollama.com/download)
#   - Python 3.10+, git
#   - ~10GB free disk space for intermediate GGUF files

set -e

# ── Defaults ─────────────────────────────────────────────────────────────────
MODEL_PATH="./output/selma-8b-merged"
MODEL_NAME="selma"
QUANT="Q4_K_M"
PUSH_TARGET=""
LLAMACPP_DIR="$HOME/.cache/selma/llama.cpp"
OUTPUT_DIR="./output/ollama"

# ── Argument parsing ──────────────────────────────────────────────────────────
while [[ $# -gt 0 ]]; do
    case $1 in
        --model-path) MODEL_PATH="$2"; shift 2 ;;
        --name)       MODEL_NAME="$2"; shift 2 ;;
        --quant)      QUANT="$2"; shift 2 ;;
        --push)       PUSH_TARGET="$2"; shift 2 ;;
        --help|-h)
            sed -n '2,15p' "$0" | sed 's/^# //'
            exit 0
            ;;
        *) echo "Unknown option: $1" >&2; exit 1 ;;
    esac
done

# ── Validation ────────────────────────────────────────────────────────────────
echo "============================================================"
echo "SELMA → Ollama Export"
echo "============================================================"
echo "  Model path : $MODEL_PATH"
echo "  Model name : $MODEL_NAME"
echo "  Quantize   : $QUANT"
echo "  Push target: ${PUSH_TARGET:-none}"
echo ""

if [ ! -d "$MODEL_PATH" ]; then
    echo "ERROR: Model path not found: $MODEL_PATH"
    echo "Run scripts/training/merge_adapter.py first to create a merged model."
    exit 1
fi

if ! command -v ollama &>/dev/null; then
    echo "ERROR: ollama not found. Install from https://ollama.com/download"
    exit 1
fi

# ── Step 1: Get llama.cpp ─────────────────────────────────────────────────────
echo "Step 1: Setting up llama.cpp conversion tools..."
if [ ! -d "$LLAMACPP_DIR" ]; then
    echo "  Cloning llama.cpp..."
    git clone --depth=1 https://github.com/ggerganov/llama.cpp.git "$LLAMACPP_DIR"
else
    echo "  Using cached llama.cpp at $LLAMACPP_DIR"
fi

# Install conversion dependencies
pip install -q -r "$LLAMACPP_DIR/requirements/requirements-convert_hf_to_gguf.txt" 2>/dev/null \
    || pip install -q gguf sentencepiece

# ── Step 2: Convert to GGUF ──────────────────────────────────────────────────
mkdir -p "$OUTPUT_DIR"
F16_GGUF="$OUTPUT_DIR/${MODEL_NAME}.f16.gguf"

echo ""
echo "Step 2: Converting to GGUF (f16)..."
python "$LLAMACPP_DIR/convert_hf_to_gguf.py" \
    "$MODEL_PATH" \
    --outtype f16 \
    --outfile "$F16_GGUF"

echo "  Created: $F16_GGUF ($(du -sh "$F16_GGUF" | cut -f1))"

# ── Step 3: Quantize ─────────────────────────────────────────────────────────
echo ""
echo "Step 3: Quantizing to $QUANT..."
QUANT_GGUF="$OUTPUT_DIR/${MODEL_NAME}.${QUANT}.gguf"

# Build quantize tool if needed
if [ ! -f "$LLAMACPP_DIR/quantize" ]; then
    echo "  Building llama.cpp quantize tool..."
    cmake -B "$LLAMACPP_DIR/build" -S "$LLAMACPP_DIR" -DCMAKE_BUILD_TYPE=Release -DLLAMA_NATIVE=OFF
    cmake --build "$LLAMACPP_DIR/build" --config Release --target quantize -j$(nproc)
    cp "$LLAMACPP_DIR/build/bin/quantize" "$LLAMACPP_DIR/quantize" 2>/dev/null \
        || cp "$LLAMACPP_DIR/build/quantize" "$LLAMACPP_DIR/quantize"
fi

"$LLAMACPP_DIR/quantize" "$F16_GGUF" "$QUANT_GGUF" "$QUANT"
echo "  Created: $QUANT_GGUF ($(du -sh "$QUANT_GGUF" | cut -f1))"

# Clean up f16 to save space
rm -f "$F16_GGUF"
echo "  Removed intermediate f16 file."

# ── Step 4: Generate Modelfile ───────────────────────────────────────────────
echo ""
echo "Step 4: Generating Modelfile..."
MODELFILE="$OUTPUT_DIR/Modelfile"

# Use the template from the repo, replacing the FROM line with the actual GGUF path
sed "s|FROM .*|FROM $(realpath "$QUANT_GGUF")|" ollama/Modelfile > "$MODELFILE"

echo "  Modelfile written to $MODELFILE"

# ── Step 5: Register with Ollama ─────────────────────────────────────────────
echo ""
echo "Step 5: Registering with local Ollama..."
ollama create "$MODEL_NAME" -f "$MODELFILE"

echo ""
echo "  Model registered as '$MODEL_NAME'"
echo "  Test it: ollama run $MODEL_NAME"

# ── Step 6: Push (optional) ──────────────────────────────────────────────────
if [ -n "$PUSH_TARGET" ]; then
    echo ""
    echo "Step 6: Pushing to Ollama registry as '$PUSH_TARGET'..."
    echo "  (Requires an account at https://ollama.com)"
    ollama cp "$MODEL_NAME" "$PUSH_TARGET"
    ollama push "$PUSH_TARGET"
    echo "  Pushed! Available at: https://ollama.com/$PUSH_TARGET"
fi

# ── Done ─────────────────────────────────────────────────────────────────────
echo ""
echo "============================================================"
echo "Export complete!"
echo ""
echo "  GGUF file : $QUANT_GGUF"
echo "  Modelfile  : $MODELFILE"
echo ""
echo "Run SELMA locally:"
echo "  ollama run $MODEL_NAME"
echo ""
echo "Or via API:"
echo "  curl http://localhost:11434/api/generate -d '{"
echo '    "model": "'"$MODEL_NAME"'",'
echo '    "prompt": "A suspect broke into a home and assaulted the owner."'
echo "  }'"
echo "============================================================"
