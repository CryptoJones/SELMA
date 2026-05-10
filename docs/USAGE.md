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

## Thinking Mode

SELMA supports Qwen3's dual-mode reasoning:

- **Thinking mode** (default): Deep chain-of-thought analysis. Best for complex
  incidents with multiple potential charges or jurisdictional issues.
- **Non-thinking mode** (`--no-thinking`): Fast responses for simple lookups
  or well-defined scenarios.

## Disclaimer

SELMA is a research and investigative assistance tool. It is NOT a substitute
for qualified legal counsel. Always have analyses reviewed by a licensed
attorney before taking any legal action.
