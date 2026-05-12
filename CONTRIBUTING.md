# Contributing to SELMA

Thank you for your interest in contributing to SELMA!

## How to Contribute

1. **Fork** the repository on Codeberg
2. **Create a branch** for your feature or fix
3. **Make your changes** with clear commit messages
4. **Run tests** to ensure nothing is broken
5. **Submit a pull request** with a description of your changes

## Development Setup

```bash
git clone https://codeberg.org/Ronin48/SELMA.git
cd SELMA
pip install -r requirements.txt
python tests/test_schema.py
```

---

## Training a State Model (Community Contribution)

One of the most valuable things you can do is train a state model on your own
hardware and contribute the adapter. Each state is independent — you only need
to train one.

### Option A — Google Colab or Kaggle (Free, no hardware required)

Open `notebooks/train_colab.ipynb` in Google Colab or Kaggle Notebooks.
The notebook walks through data collection, training, and uploading your adapter.

| Platform | GPU | VRAM | Est. Time |
|---|---|---|---|
| Google Colab free | T4 | 16GB | ~6–8 hrs |
| Kaggle free | P100 | 16GB | ~7–9 hrs |
| Google Colab Pro | A100 40GB | 40GB | ~1.5 hrs |

### Option B — Your own GPU (16GB+ VRAM)

```bash
# Install dependencies
pip install -r requirements.txt
pip install flash-attn --no-build-isolation  # optional but faster

# Authenticate (Llama 3.1 is gated — accept license first)
# https://huggingface.co/meta-llama/Llama-3.1-8B-Instruct
huggingface-cli login

# Collect data for your state
python scripts/data_collection/fetch_federal_statutes.py
python scripts/data_collection/fetch_state_statutes.py --jurisdiction <your_state>
python scripts/data_collection/fetch_legal_datasets.py
python scripts/data_collection/generate_synthetic.py
python scripts/training/prepare_dataset.py

# Train (8B config — RTX 3090/4090 ~2–3 hours)
python scripts/training/train_qlora.py --config configs/training_config_8b.yaml
```

### Option C — Vast.ai or RunPod (~$15–25 per state model)

Rent an A100-80GB spot instance, then:

```bash
chmod +x scripts/train.sh
./scripts/train.sh
```

### Testing Against the Published Model

Before submitting, verify your fine-tuned adapter improves over the baseline.
The baseline is the published model on the Ollama registry:

```bash
ollama run Ronin48/selma
```

Run the same incident descriptions through both the published model and your
fine-tuned version. Your adapter should show tighter statute citations and
more accurate element mapping for the state you trained.

### Submitting Your Adapter

1. Upload to HuggingFace:
   ```bash
   huggingface-cli upload <your-username>/selma-8b-<state>-adapter \
       output/selma-8b-qlora/final/
   ```
2. Open a pull request on Codeberg with:
   - HuggingFace adapter URL
   - GPU used and training time
   - Evaluation results (`scripts/evaluation/evaluate_model.py`)
   - Which state jurisdiction was trained

### Adding a New State's Statute Source

Before training a state not yet in `configs/trusted_sources.yaml`, add it:

```bash
python scripts/add_source.py \
    --id <state>_leginfo \
    --name "<State> Penal Code (<source domain>)" \
    --jurisdiction <state> \
    --type statute \
    --url-pattern "https://<official-source-domain>/" \
    --format html \
    --license public_domain

git add configs/trusted_sources.yaml
git commit -m "Add <state> statute source"
```

Submit the trusted_sources.yaml change as its own PR so the source domain can
be reviewed before anyone trains on it.

---

## Areas for Contribution

- **State models** — Train and submit adapters for any of the 48 remaining states
- **Statute sources** — Add official state legislature URLs to the trusted sources allowlist
- **Training data** — Create high-quality incident-to-charge training examples
- **Evaluation** — Expand the benchmark suite with new test scenarios
- **Documentation** — Improve guides and examples
- **Model improvements** — Experiment with training configurations

## Code Style

- Follow PEP 8
- Add docstrings to all public functions
- Include type hints
- Write tests for new functionality — every bug fix and new feature must include tests

## License

By contributing, you agree that your contributions will be licensed under
the Apache License 2.0.
