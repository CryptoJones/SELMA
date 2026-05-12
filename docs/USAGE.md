# SELMA Usage Guide

## Installation

```bash
git clone https://codeberg.org/Ronin48/SELMA.git
cd SELMA
pip install -r requirements.txt
```

## Running Inference

### Command Line

```bash
# Analyze an incident from text
python -m src.selma.model --input "A person broke into a house in Atlanta, GA and stole electronics."

# Analyze from a file
python -m src.selma.model --input-file incident_report.txt

# Disable thinking mode for faster (but less detailed) analysis
python -m src.selma.model --input "Description..." --no-thinking

# Save output to file
python -m src.selma.model --input "Description..." --output analysis.txt
```

### Python API

```python
from src.selma.model import load_config, load_model, analyze_incident

config = load_config("configs/model_config.yaml")
model, tokenizer = load_model(config)

incident = """
Officers responded to a 911 call at 123 Main St, Atlanta, GA.
Upon arrival, they found the front door forced open. The homeowner
reported a laptop, jewelry, and a firearm missing. Security camera
footage shows an individual entering through the front door at 2:15 AM.
"""

analysis = analyze_incident(model, tokenizer, incident, config)
print(analysis)
```

### Statute Lookup

```python
from src.selma.statute_index import StatuteIndex

index = StatuteIndex()
index.load()

# Look up a specific statute
statute = index.lookup("federal", "1111")
print(statute)

# Search by keyword
results = index.search("robbery")
for r in results:
    print(f"{r['citation']}: {r['title']}")
```

### Ollama (Local — No Python Required)

Once you have a trained model, SELMA can run via [Ollama](https://ollama.com) on any
machine — no GPU required for the Q4_K_M quantized version (runs on CPU, ~4.5GB RAM for 8B).

**Export to Ollama after training:**

```bash
# First merge the adapter into the base model
python scripts/training/merge_adapter.py --config configs/model_config.yaml

# Then export to Ollama (downloads llama.cpp, converts, quantizes, registers)
./scripts/export_ollama.sh

# Run
ollama run selma
```

**Advanced export options:**

```bash
# Use a different quantization (larger = higher quality)
./scripts/export_ollama.sh --quant Q5_K_M

# Export the 70B model
./scripts/export_ollama.sh --model-path ./output/selma-merged --name selma-70b

# Build and push to the Ollama registry in one step
./scripts/export_ollama.sh --push yourusername/selma
```

**Quantization size guide (8B model):**

| Quantization | File size | RAM needed | Quality |
|---|---|---|---|
| Q4_K_M | ~4.5GB | ~6GB | Good — recommended default |
| Q5_K_M | ~5.3GB | ~7GB | Better |
| Q8_0 | ~8.5GB | ~10GB | Near-lossless |
| f16 | ~16GB | ~18GB | Full precision |

**Ollama API (for integrations):**

```bash
curl http://localhost:11434/api/generate -d '{
  "model": "selma",
  "prompt": "A suspect broke into a home and assaulted the owner.",
  "stream": false
}'
```

## Analysis Modes

SELMA supports two analysis modes:

- **Deep analysis** (default): Chain-of-thought reasoning for complex
  incidents with multiple potential charges or jurisdictional issues.
  Uses explicit step-by-step prompting for thorough legal analysis.
- **Quick analysis** (`--no-thinking`): Faster responses for simple lookups
  or well-defined scenarios with fewer potential charges.

## Disclaimer

SELMA is a research and investigative assistance tool. It is NOT a substitute
for qualified legal counsel. Always have analyses reviewed by a licensed
attorney before taking any legal action.
