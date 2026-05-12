# SELMA — Specified Encapsulated Limitless Memory Archive

**An Open-Source Model Trained for Law Enforcement**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ollama](https://img.shields.io/badge/Ollama-Ronin48%2Fselma-black)](https://ollama.com/Ronin48/selma)

```
python3 assets/banner.py
```

## Supporters

SELMA is community-funded. Thank you to everyone who has contributed to keeping this project open and free.

| Donor | Amount | Note |
|---|---|---|
| Joe Sixpack (anonymous) | $200 | Founding donor |

*Want to support SELMA? See [CONTRIBUTING.md](CONTRIBUTING.md) or reach out to the maintainers.*

---

## Overview

SELMA is an open-source machine learning model fine-tuned to help law enforcement
identify potential violations of criminal law. Given an incident description or
fact pattern, SELMA identifies applicable criminal statutes, explains the elements
of each offense, and provides structured legal reasoning.

## Architecture

- **Base Model:** [Meta Llama 3.1 70B Instruct](https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct) (Llama 3.1 Community License)
- **Fine-tuning Method:** QLoRA (4-bit quantization with Low-Rank Adaptation)
- **Context Window:** 128K tokens (native)
- **Origin:** Meta Platforms, Inc. (United States)

> **Why Llama 3.1 70B?** See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for the full
> rationale, including national security, licensing, and performance considerations.

## Jurisdictions Covered

SELMA trains a separate model per jurisdiction. Every state model includes
federal law as baseline. See [docs/MULTI_STATE_ARCHITECTURE.md](docs/MULTI_STATE_ARCHITECTURE.md).

- **Federal:** U.S. Code Title 18 — Crimes and Criminal Procedure (baseline for all models)
- **50 State Models:** Each state's criminal code + federal law
- **Priority states:** Georgia (O.C.G.A. Title 16), California, Texas, New York, Florida

## Capabilities

Given an incident description, SELMA can:

1. **Statute Identification** — Identify which federal and/or state criminal statutes
   may have been violated
2. **Element Analysis** — Break down the elements of each identified offense and map
   them to facts in the incident
3. **Charge Classification** — Classify potential charges by severity (felony/misdemeanor),
   degree, and jurisdiction
4. **Legal Reasoning** — Provide chain-of-thought reasoning explaining why each statute
   applies or does not apply
5. **Cross-Reference** — Flag related statutes, lesser included offenses, and
   jurisdictional considerations

## Project Structure

```
SELMA/
├── LICENSE                          # Apache 2.0
├── README.md                        # This file
├── SECURITY.md                      # Security policy
├── CONTRIBUTING.md                  # Contribution guidelines
├── models/
│   ├── federal/                     # Federal-only model (18 U.S.C.)
│   │   ├── config.yaml
│   │   ├── README.md
│   │   └── training_data/
│   ├── georgia/                     # Georgia + federal
│   │   ├── config.yaml
│   │   ├── README.md
│   │   └── training_data/
│   ├── california/                  # California + federal
│   │   └── ...
│   └── [48 more states]/            # One directory per state
├── configs/
│   ├── training_config.yaml         # Base QLoRA fine-tuning configuration
│   └── model_config.yaml            # Model inference configuration
├── data/
│   ├── raw/                         # Downloaded source data
│   ├── processed/                   # Cleaned, structured statute data
│   └── synthetic/                   # Generated training examples
├── scripts/
│   ├── data_collection/
│   ├── training/
│   │   ├── train_qlora.py           # Core QLoRA trainer
│   │   ├── train_state.py           # Multi-state training orchestrator
│   │   ├── prepare_dataset.py
│   │   └── merge_adapter.py
│   └── evaluation/
├── src/selma/                       # Core Python modules
├── tests/
└── docs/
    ├── TRAINING.md
    ├── DATA_SOURCES.md
    ├── USAGE.md
    ├── MODEL_SELECTION.md           # Why Llama 3.1 70B (not Chinese models)
    ├── MULTI_STATE_ARCHITECTURE.md  # 50-state model design
    ├── OWASP_COMPLIANCE.md          # Full security evaluation
    └── SECURITY.md
```

## Try It Now

SELMA is published on the Ollama registry. No training or Python required:

```bash
ollama run Ronin48/selma
```

The published model uses Llama 3.1 8B as its base with SELMA's full system prompt and
inference parameters. A fine-tuned version will be published once training is complete.

## Quick Start

# Install dependencies
pip install -r requirements.txt
# flash-attn is optional but strongly recommended for training speed
pip install flash-attn --no-build-isolation

# Authenticate with HuggingFace (required — Llama 3.1 is a gated model)
# First accept the license at: https://huggingface.co/meta-llama/Llama-3.1-70B-Instruct
huggingface-cli login

# Download training data
python scripts/data_collection/fetch_federal_statutes.py
python scripts/data_collection/fetch_georgia_statutes.py
python scripts/data_collection/fetch_legal_datasets.py

# Generate synthetic training examples (~50K incident-to-statute pairs)
python scripts/data_collection/generate_synthetic.py

# Prepare the dataset
python scripts/training/prepare_dataset.py

# Fine-tune the model (requires A100-80GB or equivalent, ~6-10 hours)
# The merge step (merge_adapter.py) requires ~140GB system RAM
python scripts/training/train_qlora.py --config configs/training_config.yaml

# Merge LoRA adapter into base model
python scripts/training/merge_adapter.py

# Run inference
python -m src.selma.model --input "Describe an incident..."
```

## Training Data Sources

| Source | Description | Size | License |
|--------|-------------|------|---------|
| U.S. Code Title 18 | Federal criminal statutes (USLM XML) | ~2,700 sections | Public Domain |
| O.C.G.A. Title 16 | Georgia criminal code | ~500 sections | Fair Use |
| ALEA US Courts | Federal court filings with NOS codes | 491K examples | Open |
| LegalBench | Legal reasoning benchmark tasks | 91.8K examples | Open |
| CaseHOLD | Legal holding classification | 585K examples | Open |
| Synthetic | Generated incident-to-statute mappings | ~50K examples | Apache 2.0 |

## Disclaimer

SELMA is a research tool designed to assist law enforcement professionals. It is
**NOT** a substitute for legal counsel, prosecutorial judgment, or judicial review.
All outputs should be verified by qualified legal professionals before any action
is taken. The model may produce incorrect or incomplete legal analysis.

This software is provided "AS IS" without warranty of any kind. The developers
assume no liability for decisions made based on SELMA's outputs.

## Security

SELMA has been evaluated against:
- **OWASP Top 10 for LLM Applications (2025)** — AI-specific threats
- **OWASP Top 10 for Web Applications (2021)** — General software security

See [docs/OWASP_COMPLIANCE.md](docs/OWASP_COMPLIANCE.md) for the full evaluation
and [SECURITY.md](SECURITY.md) for the security policy.

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

**Project Code, Data, and Documentation:** Apache License 2.0 — Copyright 2026 Ronin 48, LLC. See [LICENSE](LICENSE).

**Base Model Weights:** Meta Llama 3.1 Community License. See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for details.
Fine-tuned adapter weights and all original SELMA contributions remain Apache 2.0.
