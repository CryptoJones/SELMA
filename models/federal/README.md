# SELMA — Federal

**Criminal Code:** 18 U.S.C. — Crimes and Criminal Procedure

This is the federal-only model covering all of Title 18 U.S.C.
It is included as the baseline in every state model.

## Training Status

- [x] Statutory data collected
- [x] Synthetic training examples created
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
python scripts/training/train_state.py --state federal
```
