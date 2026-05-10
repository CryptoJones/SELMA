# SELMA Model Selection Rationale

## Decision: Meta Llama 3.1 70B Instruct

**Date:** May 2026
**Decision Makers:** Ronin 48, LLC
**Status:** Final

---

## Executive Summary

SELMA uses Meta's Llama 3.1 70B Instruct as its base model. This decision was
made after evaluating all major open-source LLMs against five criteria: technical
performance, national security suitability, licensing, fine-tuning feasibility,
and long-term viability for law enforcement applications. This document records
the rationale for transparency and due diligence.

---

## The Problem

SELMA is an AI model designed to assist law enforcement in identifying potential
violations of criminal law. This places it in a uniquely sensitive category:

1. It will process law enforcement sensitive information (incident reports,
   evidence descriptions, case details)
2. Its outputs may influence charging decisions and investigative priorities
3. It must be trustworthy to federal, state, and local agencies
4. It must comply with CJIS Security Policy and agency procurement requirements
5. It must withstand scrutiny from oversight bodies, defense attorneys, and courts

The choice of base model is not purely a technical decision — it is a national
security, legal, and institutional trust decision.

---

## Models Evaluated

| Model | Origin | Parameters | License | Context | Status |
|-------|--------|-----------|---------|---------|--------|
| Qwen3-32B | Alibaba (China) | 32B | Apache 2.0 | 131K | **REJECTED** |
| Qwen3-14B | Alibaba (China) | 14B | Apache 2.0 | 128K | **REJECTED** |
| DeepSeek-R1 | DeepSeek (China) | 671B MoE | MIT | 128K | **REJECTED** |
| DeepSeek-V3 | DeepSeek (China) | 671B MoE | MIT | 128K | **REJECTED** |
| **Llama 3.1 70B** | **Meta (USA)** | **70B** | **Llama 3.1** | **128K** | **SELECTED** |
| Llama 3.1 8B | Meta (USA) | 8B | Llama 3.1 | 128K | Viable fallback |
| Mistral Small 3 | Mistral (France) | 24B | Apache 2.0 | 32K | Viable but limited |
| Mistral Large | Mistral (France) | 123B | MRL | 128K | License too restrictive |
| Gemma 2 27B | Google (USA) | 27B | Gemma | 8K | Context too short |

---

## Rejection of Chinese-Origin Models

### Qwen3 (Alibaba Cloud / China)

Qwen3-32B was initially selected as the base model due to its strong benchmark
performance, Apache 2.0 license, and efficient fine-tuning characteristics.
However, upon further review, this selection was reversed for the following reasons:

**1. National Security Concerns**

SELMA is a law enforcement tool. Using a model developed by a Chinese
state-adjacent corporation (Alibaba Group is subject to Chinese Communist Party
oversight and China's National Intelligence Law, which requires organizations to
"support, assist, and cooperate with national intelligence work") introduces
unacceptable risk for a U.S. law enforcement application.

Even though the model weights are open and inspectable, the following risks remain:

- **Training data opacity:** The full training corpus is not disclosed. There is
  no way to verify what information, biases, or behaviors were encoded during
  pretraining.
- **Perception of compromise:** Regardless of technical safety, the *perception*
  of using Chinese AI in U.S. law enforcement would undermine institutional trust
  and public confidence.
- **Supply chain risk:** Future model updates, tooling, or dependencies could
  introduce vulnerabilities that are difficult to detect.

**2. Regulatory and Procurement Barriers**

- **Executive Order 13873** (Securing the Information and Communications
  Technology and Services Supply Chain) and subsequent orders restrict use of
  technology from foreign adversaries in sensitive applications.
- **CJIS Security Policy** (FBI Criminal Justice Information Services) imposes
  strict requirements on systems that process criminal justice information.
  Chinese-origin AI components would face heightened scrutiny.
- **Federal Acquisition Regulation (FAR)** and state procurement rules
  increasingly restrict Chinese technology in government contracts.
- **Section 889 of the NDAA** prohibits certain federal agencies from procuring
  telecommunications and video surveillance equipment from specified Chinese
  companies. While not directly applicable to AI models, it signals the
  legislative direction.

**3. Institutional Adoption**

No federal law enforcement agency (FBI, DEA, ATF, USMS, HSI) or major state/local
agency would adopt a tool built on a Chinese AI model. This is not speculation —
it is a practical reality of government IT procurement. Building on Qwen3 would
make SELMA dead on arrival for its intended users.

### DeepSeek (China)

Rejected for the same national security reasons as Qwen3. Additionally:
- 671B MoE architecture is impractical for fine-tuning
- Requires massive compute infrastructure for inference

---

## Selection of Llama 3.1 70B Instruct

### Why Llama 3.1

**1. American Origin**

Meta Platforms, Inc. is a U.S. corporation headquartered in Menlo Park,
California. Meta has active relationships with U.S. government agencies and
defense contractors. Llama models have been adopted by the U.S. Department of
Defense and intelligence community partners.

**2. Technical Performance**

Llama 3.1 70B is one of the strongest open-weight models available:

- **128K native context window** — sufficient for processing lengthy legal
  documents, case files, and multi-page incident reports without truncation
- **Strong reasoning capability** — demonstrated performance on legal reasoning
  benchmarks, including MMLU (law subset), HellaSwag, and ARC
- **Instruction-tuned** — the Instruct variant is already optimized for
  following complex analytical instructions, which aligns with SELMA's use case
- **70B parameters** — large enough for nuanced legal analysis while still
  feasible to fine-tune with QLoRA on accessible hardware

**3. Fine-tuning Ecosystem**

Llama 3.1 has the largest fine-tuning ecosystem of any open-weight model:

- Full support in HuggingFace Transformers, PEFT, TRL
- Extensive QLoRA/LoRA documentation and community experience
- Compatible with Unsloth for 2x training speedup
- Well-tested on A100 and H100 GPUs
- Hundreds of successful community fine-tunes demonstrate reliability

**4. Licensing**

The Llama 3.1 Community License is permissive for this use case:

- **Free for commercial use** — no license fees
- **Modification allowed** — fine-tuning is explicitly permitted
- **Distribution allowed** — derivative models can be shared
- **700M MAU threshold** — only restricts companies with over 700 million
  monthly active users (not applicable to SELMA)
- **No restriction on law enforcement use** — unlike some licenses that
  restrict "surveillance" or "military" applications

**Important note on licensing structure:**
- SELMA's project code, training data, synthetic examples, and documentation
  are licensed under **Apache 2.0**
- The base model weights and any derivative weights carry the
  **Llama 3.1 Community License**
- This dual-license structure is standard practice (similar to how Linux
  applications are MIT/Apache but the kernel is GPL)

**5. Long-term Viability**

- Meta has committed to continued development of the Llama family
- Large community ensures ongoing support, security audits, and improvements
- U.S. government investment in Llama ecosystem (DoD, IC community)
- Future Llama releases (4.x, 5.x) provide an upgrade path

---

## Why Not Other Western Models?

### Mistral Small 3 (24B, France)

- **Pro:** Apache 2.0 license, NATO-allied origin
- **Con:** Only 32K context window — insufficient for processing long legal
  documents, depositions, or complex multi-count indictments
- **Con:** 24B parameters limits analytical depth compared to 70B
- **Verdict:** Viable as a lightweight deployment option but not the primary model

### Mistral Large (123B, France)

- **Con:** Mistral Research License (MRL) — restrictive, not suitable for
  commercial or government deployment
- **Verdict:** License disqualifies it

### Gemma 2 27B (Google, USA)

- **Pro:** American origin, good performance
- **Con:** Only 8K context window — far too short for legal analysis
- **Con:** Gemma license has restrictions that may complicate government use
- **Verdict:** Context window is disqualifying

### Llama 3.1 8B (Meta, USA)

- **Pro:** Same advantages as 70B but runs on a single consumer GPU
- **Con:** Significantly less capable for complex multi-statute legal analysis
- **Verdict:** Viable as a "SELMA Lite" deployment for resource-constrained
  environments. May be offered as a secondary model.

---

## Hardware Requirements (Updated)

The move from 32B to 70B increases compute requirements:

| Configuration | GPU | VRAM | Est. Training Time |
|--------------|-----|------|--------------------|
| QLoRA 4-bit | 1x A100-80GB | ~72GB | 6-10 hours |
| QLoRA 4-bit | 2x A100-40GB | ~80GB | 6-10 hours |
| QLoRA 4-bit | 1x H100-80GB | ~72GB | 4-7 hours |
| Full fine-tune | 4x A100-80GB | ~320GB | 20-40 hours |

For inference (deployment):
| Configuration | GPU | VRAM |
|--------------|-----|------|
| QLoRA 4-bit (GPTQ/AWQ) | 1x A100-40GB | ~36GB |
| QLoRA 4-bit | 1x RTX 4090 | ~24GB (tight) |
| GGUF Q4_K_M | CPU + 64GB RAM | No GPU required |

---

## Risk Assessment

| Risk | Severity | Mitigation |
|------|----------|------------|
| Model bias in legal analysis | High | Extensive evaluation suite, human-in-the-loop design |
| Incorrect statute identification | High | Benchmark testing, mandatory human review |
| Hallucinated legal citations | Medium | Cross-reference against statute index |
| Model generates harmful advice | Medium | System prompts, guardrails, disclaimer requirements |
| License compliance | Low | Dual-license structure clearly documented |
| Supply chain compromise | Low | Llama weights are widely audited; U.S.-origin |

---

## Conclusion

Meta's Llama 3.1 70B Instruct is the right foundation for SELMA. It combines
strong technical performance with the institutional trust, national security
posture, and licensing flexibility required for a law enforcement AI tool.

The rejection of Chinese-origin models (Qwen3, DeepSeek) is not a reflection of
their technical quality — both are excellent models. It is a pragmatic decision
driven by the specific requirements of SELMA's intended deployment environment:
U.S. law enforcement agencies operating under strict procurement, security, and
public trust constraints.

---

*Document version: 1.0*
*Last updated: May 2026*
*Author: Ronin 48, LLC*
