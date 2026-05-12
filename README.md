# SELMA — Specified Encapsulated Limitless Memory Archive

**An Open-Source Model Trained for Law Enforcement**

[![License](https://img.shields.io/badge/License-Apache_2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Ollama](https://img.shields.io/badge/Ollama-Ronin48%2Fselma-black)](https://ollama.com/Ronin48/selma)
[![HuggingFace](https://img.shields.io/badge/HuggingFace-Ronin48%2Fselma-yellow)](https://huggingface.co/Ronin48/selma)
[![Version](https://img.shields.io/badge/version-v0.1.0-blue)](CHANGELOG.md)

```
python3 assets/banner.py
```

> *"Justice will not be served until those who are unaffected are as outraged as those who are."*
> — Benjamin Franklin

---

## Supporters

SELMA is community-funded. Every contribution — great or small — keeps this project free, open,
and in the hands of the people it is meant to serve.

| Donor | Amount | Note |
|---|---|---|
| Ronin 48, LLC | N/A | Founding donor |
| Ronin 48, LLC | N/A | Primary sponsor of research time and equipment |

*Want to support SELMA? See [CONTRIBUTING.md](CONTRIBUTING.md) or reach out to the maintainers.*

---

## Overview

SELMA is an open-source machine learning model fine-tuned to assist law enforcement professionals
in identifying potential violations of criminal law. Given an incident description or fact pattern,
SELMA identifies applicable federal and state criminal statutes, carefully breaks down the elements
of each offense, maps those elements to the facts at hand, and provides structured, transparent
legal reasoning — all in plain language.

SELMA was built on the conviction that good tools should be open, accountable, and freely available
to every agency regardless of budget. It does not replace prosecutors, attorneys, or judicial
review — it is a force-multiplier for the investigator who needs a place to start.

### Sister Project: ATTICUS

SELMA does not stand alone. It is one half of a balanced system.

[**ATTICUS**](https://codeberg.org/Ronin48/ATTICUS) — *Automated Trial and Legal Intelligence for
Criminal Defense Use Cases and Support* — is SELMA's companion model, built for the other side of
the courtroom. Where SELMA identifies what the prosecution may charge, ATTICUS builds the defense.
Where SELMA maps evidence to statutes, ATTICUS maps evidence to constitutional protections.

This symmetry is intentional. A system that only serves prosecution is a system that can cause
harm. ATTICUS ensures that every capability SELMA gives law enforcement has a counterpart in
the hands of the public defender.

| | SELMA | ATTICUS |
|---|---|---|
| **Purpose** | Prosecution-side statute identification | Defense-side strategy and analysis |
| **Users** | Patrol officers, detectives, special agents | Public defenders, defense attorneys |
| **Output** | Applicable charges and elements, legal reasoning | Defense theories, constitutional violations, evidentiary weaknesses |
| **Training data** | Criminal statutes, case law, charging documents | Suppression motions, acquittals, Brady/Giglio material, exoneration data |
| **Repository** | [Ronin48/SELMA](https://codeberg.org/Ronin48/SELMA) | [Ronin48/ATTICUS](https://codeberg.org/Ronin48/ATTICUS) |

---

## Architecture

- **Base Model:** [Meta Llama 3.3 70B Instruct](https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct) (Llama 3.1 Community License)
- **Fine-tuning Method:** QLoRA (4-bit quantization with Low-Rank Adaptation)
- **Context Window:** 128K tokens (native)
- **Quantization:** NF4 double quantization via bitsandbytes
- **Origin:** Meta Platforms, Inc. (United States)

> **Why Llama 3.3 70B?** See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for the full
> rationale, including national security, licensing, and performance considerations.

---

## Capabilities

Given an incident description, SELMA can:

1. **Statute Identification** — Identify which federal and/or state criminal statutes may have
   been violated, cited by title, chapter, and section
2. **Element Analysis** — Break down the elements of each identified offense and map them to
   specific facts present in the incident description
3. **Charge Classification** — Classify potential charges by severity (felony/misdemeanor), degree,
   and jurisdiction, including mandatory minimum and maximum penalties
4. **Legal Reasoning** — Provide transparent, chain-of-thought reasoning explaining why each
   statute applies or does not apply, so the operator can evaluate the analysis rather than
   simply accepting it
5. **Cross-Reference** — Flag related statutes, lesser included offenses, concurrent jurisdiction
   issues, and federal/state overlap
---

## Constitutional Override

The U.S. Constitution is the supreme law of the land, and SELMA is trained to know it.
No statute, regulation, or agency policy overrides the Bill of Rights. Where SELMA identifies
a potential charge that implicates constitutional protections — an unlawful search, a coerced
confession, a due process violation — it will say so plainly:

> ⚠ **CONSTITUTIONAL CONCERN** — evidence obtained through this method may be subject to
> suppression under the [Amendment]. SELMA recommends consulting with the prosecuting attorney
> before charging.

This is not a limitation. It is the feature.

---

## Jurisdictions Covered

SELMA trains a separate model per jurisdiction. Every state model includes federal law as
baseline. See [docs/MULTI_STATE_ARCHITECTURE.md](docs/MULTI_STATE_ARCHITECTURE.md).

- **Federal:** U.S. Code Title 18 — Crimes and Criminal Procedure (baseline for all models)
- **50 State Models:** Each state's criminal code + federal law
- **Priority states:** Georgia (O.C.G.A. Title 16), California, Texas, New York, Florida

---

## Where to Get SELMA

SELMA is published on multiple platforms. Choose the one that fits your environment:

### Ollama (Recommended for most users)

No Python, no GPU, no configuration required. Works on any machine with Ollama installed:

```bash
ollama run Ronin48/selma
```

The published model uses Llama 3.1 8B with SELMA's full system prompt and inference
parameters. A fine-tuned QLoRA version (v1.0.0) will replace it upon training completion.

### HuggingFace

Adapter weights and merged model weights will be published at:

- **LoRA Adapter:** `Ronin48/selma-lora-adapter` — the fine-tuned adapter only (smaller download)
- **Merged Model:** `Ronin48/selma-70b` — full merged weights, ready for inference
- **Quantized (GGUF):** `Ronin48/selma-70b-GGUF` — for use with llama.cpp, LM Studio, and Ollama

```python
from transformers import AutoModelForCausalLM, AutoTokenizer
model = AutoModelForCausalLM.from_pretrained("Ronin48/selma-70b")
```

### LM Studio

Once the GGUF weights are published to HuggingFace, SELMA will be searchable and
downloadable directly inside LM Studio. Search for `Ronin48/selma`.

---

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
    ├── MODEL_SELECTION.md           # Why Llama 3.3 70B (not Chinese models)
    ├── MULTI_STATE_ARCHITECTURE.md  # 50-state model design
    ├── OWASP_COMPLIANCE.md          # Full security evaluation
    └── SECURITY.md
```

---

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt
# flash-attn is optional but strongly recommended for training speed
pip install flash-attn --no-build-isolation

# Authenticate with HuggingFace (required — Llama 3.1 is a gated model)
# First accept the license at: https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
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

---

## Training Data Sources

| Source | Description | Size | License |
|--------|-------------|------|---------|
| U.S. Code Title 18 | Federal criminal statutes (USLM XML) | ~2,700 sections | Public Domain |
| O.C.G.A. Title 16 | Georgia criminal code | ~500 sections | Fair Use |
| ALEA US Courts | Federal court filings with NOS codes | 491K examples | Open |
| LegalBench | Legal reasoning benchmark tasks | 91.8K examples | Open |
| CaseHOLD | Legal holding classification | 585K examples | Open |
| Digital Forensics Case Law | CFAA prosecutions, search/seizure digital | ~5K opinions | Public Domain |
| Synthetic | Generated incident-to-statute mappings | ~50K examples | Apache 2.0 |

---

## Disclaimer

SELMA is a research tool designed to assist law enforcement professionals. It is
**NOT** a substitute for legal counsel, prosecutorial judgment, or judicial review.
All outputs should be verified by qualified legal professionals before any action
is taken. The model may produce incorrect or incomplete legal analysis.

SELMA does not advocate for any outcome. It identifies what the law says. The decision
to charge, to investigate further, or to pursue alternative courses of action remains
entirely with the human operator and the appropriate legal authorities.

This software is provided "AS IS" without warranty of any kind. The developers assume
no liability for decisions made based on SELMA's outputs.

---

## Security

SELMA has been evaluated against:
- **OWASP Top 10 for LLM Applications (2025)** — AI-specific threats
- **OWASP Top 10 for Web Applications (2021)** — General software security

See [docs/OWASP_COMPLIANCE.md](docs/OWASP_COMPLIANCE.md) for the full evaluation
and [SECURITY.md](SECURITY.md) for the security policy.

---

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.
Subject matter experts in criminal law, digital forensics, and constitutional law are
especially encouraged to contribute.

---

## License

**Project Code, Data, and Documentation:** Apache License 2.0 — Copyright 2026 Ronin 48, LLC. See [LICENSE](LICENSE).

**Base Model Weights:** Meta Llama 3.1 Community License. See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for details.
Fine-tuned adapter weights and all original SELMA contributions remain Apache 2.0.
