# SELMA — Alaska

**Criminal Code:** Alaska Stat. Title 11 — Criminal Law

This model is trained on Alaska's criminal statutes
(Alaska Stat. Title 11) plus all federal criminal law (18 U.S.C.).

## Training Status

- [ ] Statutory data collected
- [ ] Synthetic training examples created
- [ ] Model trained
- [ ] Model evaluated

## Published Model

A base version of SELMA is available now on Ollama (no training required):

```bash
ollama run Ronin48/selma
```

This uses Llama 3.1 8B with SELMA's full system prompt. The state-specific
fine-tuned adapter below will replace it once trained.

## Training

```bash
python scripts/training/train_state.py --state alaska
```
