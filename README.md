# SELMA — Specified Encapsulated Limitless Memory Archive

**An Open-Source Model Trained for Law Enforcement**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

## Overview

SELMA is an open-source machine learning model fine-tuned to help law enforcement
identify potential violations of criminal law. Given an incident description or
fact pattern, SELMA identifies applicable criminal statutes, explains the elements
of each offense, and provides structured legal reasoning.

## Architecture

- **Base Model:** [Qwen3-32B](https://huggingface.co/Qwen/Qwen3-32B) (Apache 2.0)
- **Fine-tuning Method:** QLoRA (4-bit quantization with Low-Rank Adaptation)
- **Context Window:** 131K tokens (via YaRN extension)
- **Reasoning:** Dual-mode thinking/non-thinking for deep legal analysis vs. quick lookups

## Jurisdictions Covered

- **Federal:** U.S. Code Title 18 — Crimes and Criminal Procedure
- **State:** Georgia O.C.G.A. Title 16 — Crimes and Offenses

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
├── configs/
│   ├── training_config.yaml         # QLoRA fine-tuning configuration
│   └── model_config.yaml            # Model architecture configuration
├── data/
│   ├── raw/
│   │   ├── federal/                 # U.S. Code Title 18 (USLM XML)
│   │   └── georgia/                 # O.C.G.A. Title 16
│   ├── processed/                   # Cleaned, structured statute data
│   └── synthetic/                   # Generated training examples
├── scripts/
│   ├── data_collection/
│   │   ├── fetch_federal_statutes.py
│   │   ├── fetch_georgia_statutes.py
│   │   └── fetch_legal_datasets.py
│   ├── training/
│   │   ├── prepare_dataset.py
│   │   ├── train_qlora.py
│   │   └── merge_adapter.py
│   └── evaluation/
│       ├── evaluate_model.py
│       └── benchmark_suite.py
├── src/selma/
│   ├── __init__.py
│   ├── model.py                     # Model loading and inference
│   ├── prompts.py                   # Prompt templates
│   ├── statute_index.py             # Statute lookup and indexing
│   └── schema.py                    # Data schemas
├── tests/
│   └── test_schema.py
└── docs/
    ├── TRAINING.md                  # Training guide
    ├── DATA_SOURCES.md              # Data provenance documentation
    └── USAGE.md                     # Usage guide
```

## Quick Start

```bash
# Clone the repository
git clone https://codeberg.org/Ronin48/SELMA.git
cd SELMA

# Install dependencies
pip install -r requirements.txt

# Download training data
python scripts/data_collection/fetch_federal_statutes.py
python scripts/data_collection/fetch_georgia_statutes.py
python scripts/data_collection/fetch_legal_datasets.py

# Prepare the dataset
python scripts/training/prepare_dataset.py

# Fine-tune the model (requires A100-80GB or equivalent)
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

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

Copyright 2026 Ronin 48, LLC

Licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE) for details.
