# SELMA Changelog

## Versioning Scheme

| Component | When to bump | Example |
|---|---|---|
| **Major** (X.0.0) | Base model swap (e.g. 8B → 70B, Llama → Mistral) | v1.0.0 |
| **Minor** (0.X.0) | New training data, new states, significant prompt changes | v0.2.0 |
| **Patch** (0.0.X) | Parameter tuning, bug fixes, small prompt adjustments | v0.1.1 |

**Tags on Ollama:** `Ronin48/selma:latest` always points to the most recent stable version.
Named tags (`Ronin48/selma:v0.1.0`) are permanent and never overwritten.

**Pre-fine-tune versions (v0.x.x):** Base Llama 3.1 8B + SELMA system prompt.
No fine-tuned weights yet. These are prompt-engineered baselines.

**Fine-tuned versions (v1.x.x+):** QLoRA fine-tuned on SELMA training data.
Will be tagged per state (e.g. `v1.0.0-georgia`, `v1.0.0-federal`).

---

## [v0.1.0] — 2026-05-11

**Ollama:** `ollama run Ronin48/selma:v0.1.0`
**Base model:** `meta-llama/Llama-3.1-8B-Instruct` (no fine-tuning)
**Type:** Prompt-engineered baseline

### Added
- Initial SELMA system prompt with criminal statute analysis framework
- Civil/criminal distinction: civil statutes labeled "⚠ CIVIL — Not a criminal charge"
- **Constitutional Override** — U.S. Constitution hard-overrides all federal, state, and
  local law; charges conflicting with constitutional rights flagged
  "⚠ CONSTITUTIONAL CONCERN — may not survive challenge"
- Covers all 8 key amendments (1st–8th) plus 14th Amendment equal protection
- State constitution note: flags when state constitutions exceed federal floor
- Inference parameters tuned for legal precision (temp=0.3, top_p=0.9)
- Published to Ollama registry: https://ollama.com/Ronin48/selma

### Planned for v0.2.0
- Sentencing guideline integration in system prompt
- Jurisdiction-specific prompt variants (Georgia, Federal)

### Planned for v1.0.0
- First QLoRA fine-tuned weights (Llama 3.1 8B, Georgia + Federal)
- Trained on: U.S. Code Title 18, O.C.G.A. Title 16, CourtListener case law,
  USSG sentencing guidelines, ~50K synthetic incident-to-charge examples
