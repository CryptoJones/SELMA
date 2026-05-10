# SELMA Security Evaluation & OWASP Compliance

## Document Purpose

This document provides a comprehensive security evaluation of SELMA against
two OWASP frameworks:

1. **OWASP Top 10 for LLM Applications (2025)** — AI/ML-specific threats
2. **OWASP Top 10 for Web Applications (2021)** — General software security

SELMA is a law enforcement tool that processes sensitive criminal justice
information. Security is not optional — it is a prerequisite for deployment.
This evaluation identifies threats, assesses SELMA's current posture, and
documents the controls required for compliant deployment.

---

## Part 1: OWASP Top 10 for LLM Applications (2025)

### LLM01:2025 — Prompt Injection

**Threat:** Adversaries craft inputs that alter SELMA's behavior, bypass safety
guidelines, cause it to produce incorrect legal analysis, or extract system
prompts. In a law enforcement context, a manipulated output could lead to
wrongful charges or missed violations.

**Risk Level for SELMA:** CRITICAL

**Attack Scenarios:**
- A suspect's statement is fed into SELMA and contains hidden instructions
  that cause the model to downplay or omit applicable charges
- An adversary injects instructions through incident report text fields that
  cause SELMA to output fabricated statute citations
- Indirect injection via embedded content in documents processed by SELMA

**SELMA Controls:**
- [ ] Input sanitization layer that strips known injection patterns before
  model processing
- [ ] Input length and character-set validation on all user-facing inputs
- [ ] Output validation against the statute index — any cited statute must
  exist in the verified database
- [ ] Separation of system prompt from user input at the architectural level
- [ ] Human-in-the-loop requirement: all outputs are advisory only, requiring
  qualified review before any action is taken
- [x] System prompt includes explicit disclaimer and scope limitations
- [x] Model is fine-tuned specifically on legal analysis, reducing
  susceptibility to off-topic injection

**Remediation Priority:** P0 — Must be addressed before any deployment

---

### LLM02:2025 — Sensitive Information Disclosure

**Threat:** SELMA could leak training data containing sensitive legal
information, PII from training examples, or internal system architecture details
through its outputs.

**Risk Level for SELMA:** HIGH

**Attack Scenarios:**
- Adversary prompts SELMA to reveal training data examples that contain PII
- Model memorizes and reproduces specific incident details from training set
- System prompt or internal configuration leaked through crafted queries

**SELMA Controls:**
- [x] Training data uses synthetic incidents only — no real case data, no real
  PII, no real names, addresses, or case numbers
- [x] All training examples are generated or derived from public statutory text
- [x] System prompt contains no secrets, credentials, or sensitive configuration
- [ ] Deploy output filtering that detects and redacts potential PII patterns
  (SSN, phone numbers, addresses) in model outputs
- [ ] Implement rate limiting to prevent bulk extraction attempts
- [ ] Regular audits of model outputs for training data leakage

**Remediation Priority:** P1

---

### LLM03:2025 — Supply Chain Vulnerabilities

**Threat:** Compromised dependencies, poisoned pre-trained models, or malicious
packages in the training/inference pipeline.

**Risk Level for SELMA:** HIGH

**Attack Scenarios:**
- A compromised HuggingFace model is substituted for the legitimate Llama 3.1
- Malicious code in a Python dependency exfiltrates data during training
- Tampered training data introduced through a compromised data source

**SELMA Controls:**
- [x] Base model sourced directly from Meta's official HuggingFace repository
  (meta-llama/Llama-3.1-70B-Instruct) with verified checksums
- [x] Model selection documents U.S.-origin provenance (see MODEL_SELECTION.md)
- [x] All dependencies pinned with minimum versions in requirements.txt
- [x] Training data provenance documented in DATA_SOURCES.md
- [x] Federal statutes sourced from official U.S. government XML
  (uscode.house.gov) — public domain, verifiable
- [ ] Implement hash verification for all downloaded model weights
- [ ] Use pip hash checking mode for dependency installation
- [ ] Establish a Software Bill of Materials (SBOM) for the project
- [ ] Sign all releases with GPG keys

**Remediation Priority:** P1

---

### LLM04:2025 — Data and Model Poisoning

**Threat:** Training data manipulation that introduces backdoors, biases, or
degraded performance. For a law enforcement tool, poisoning could systematically
cause SELMA to miss certain categories of crimes or recommend charges for
innocent conduct.

**Risk Level for SELMA:** CRITICAL

**Attack Scenarios:**
- Adversary contributes poisoned training examples through pull requests that
  teach the model to ignore specific statutes
- Compromised statutory data that misrepresents elements of offenses
- Bias injection that causes different analysis quality based on demographic
  information in incident descriptions

**SELMA Controls:**
- [x] Federal statutes sourced from official government XML — authoritative and
  verifiable against published law
- [x] All synthetic training data is hand-crafted with cited statute references
  that can be cross-checked
- [x] Training data is version-controlled in the repository with full git history
- [x] Apache 2.0 licensing enables public audit of all training data
- [ ] Implement a training data review process requiring two-person sign-off
  for any additions to the training set
- [ ] Automated bias testing across demographic variables in incident descriptions
- [ ] Periodic re-validation of all training examples against current law
- [ ] Canary examples in training set to detect poisoning

**Remediation Priority:** P0

---

### LLM05:2025 — Improper Output Handling

**Threat:** SELMA's output is used by downstream systems without proper
validation, leading to injection attacks (XSS, SSRF, command injection) or
incorrect automated actions.

**Risk Level for SELMA:** MEDIUM

**Attack Scenarios:**
- SELMA's output is rendered in a web interface without sanitization, enabling
  XSS attacks via crafted model responses
- Model output containing statute citations is passed directly to a database
  query, enabling SQL injection
- Automated systems act on SELMA's charge recommendations without human review

**SELMA Controls:**
- [x] Architecture enforces human-in-the-loop — output is advisory only
- [x] Output is structured text, not executable code
- [ ] All integrating systems must sanitize SELMA output before rendering,
  database insertion, or further processing
- [ ] Output schema validation: responses must conform to expected format
  (statute citations, element analysis, charge classification)
- [ ] Content Security Policy (CSP) headers on any web-based deployment
- [ ] Statute citations in output verified against the statute index before
  display to the user

**Remediation Priority:** P2

---

### LLM06:2025 — Excessive Agency

**Threat:** SELMA is granted capabilities beyond what is necessary, enabling
it to take harmful actions autonomously.

**Risk Level for SELMA:** LOW (by design)

**Attack Scenarios:**
- SELMA is connected to a case management system with write access and
  autonomously files charges
- Model is given access to law enforcement databases and exfiltrates data
- SELMA autonomously contacts suspects or witnesses

**SELMA Controls:**
- [x] SELMA is designed as a READ-ONLY analytical tool — it has no agency,
  no tool use, no ability to take actions in external systems
- [x] Architecture is inference-only: input text in, analysis text out
- [x] No database connections, API calls, or system integrations in the model
  itself
- [ ] Deployment guidelines must explicitly prohibit granting SELMA write
  access to any law enforcement system
- [ ] If future versions add RAG, implement strict read-only database access
  with no mutation capabilities

**Remediation Priority:** P3 (low risk due to architecture)

---

### LLM07:2025 — System Prompt Leakage

**Threat:** The system prompt is extracted by adversaries, revealing SELMA's
instructions, analytical framework, or potential bypass techniques.

**Risk Level for SELMA:** LOW

**Attack Scenarios:**
- Adversary uses prompt extraction techniques to reveal SELMA's system prompt
- Leaked system prompt reveals analytical biases or blind spots that can be
  exploited by criminals

**SELMA Controls:**
- [x] System prompt is open source — there is no secret to leak. Full
  transparency is a feature, not a vulnerability. Defense attorneys and courts
  can inspect exactly how SELMA is instructed.
- [x] System prompt contains no credentials, API keys, or sensitive data
- [x] The prompt's analytical framework is publicly documented
- [ ] Monitor for attempts to extract system prompts as an indicator of
  adversarial behavior

**Remediation Priority:** P4 (low risk — open source model)

---

### LLM08:2025 — Vector and Embedding Weaknesses

**Threat:** If SELMA uses RAG (Retrieval Augmented Generation), the vector
database could be poisoned, manipulated, or accessed without authorization.

**Risk Level for SELMA:** MEDIUM (future risk)

**Attack Scenarios:**
- Poisoned statute embeddings cause incorrect retrieval of legal text
- Access control failures expose embeddings containing case-sensitive information
- Adversary injects malicious content into the vector store

**SELMA Controls:**
- [x] Current architecture does NOT use RAG — this is a future risk only
- [x] Statute index is a static JSON lookup, not a vector database
- [ ] If RAG is added: implement strict access controls on vector database
- [ ] If RAG is added: embeddings must be generated from verified statutory
  sources only, with integrity checks
- [ ] If RAG is added: separate vector stores for different classification
  levels of information

**Remediation Priority:** P3 (future consideration)

---

### LLM09:2025 — Misinformation / Hallucination

**Threat:** SELMA generates plausible but incorrect legal analysis —
fabricated statutes, wrong elements of offenses, incorrect severity
classifications, or flawed legal reasoning. This is the HIGHEST RISK for
a law enforcement tool.

**Risk Level for SELMA:** CRITICAL

**Attack Scenarios:**
- SELMA cites a statute number that does not exist ("hallucinated citation")
- Model correctly identifies a statute but lists incorrect elements of the offense
- SELMA misclassifies a misdemeanor as a felony (or vice versa)
- Model applies a statute from the wrong jurisdiction

**SELMA Controls:**
- [x] Human-in-the-loop architecture — all output requires review by qualified
  legal professional before action
- [x] Statute index cross-reference available to verify cited statutes exist
- [x] Training data derived from verified statutory text, not generated legal
  knowledge
- [x] Evaluation benchmark suite tests against known-correct scenario analyses
- [x] Prominent disclaimer on all outputs
- [ ] Implement automated hallucination detection: every statute cited in output
  is verified against the statute index in real-time
- [ ] Confidence scoring: model outputs a confidence level for each identified
  charge
- [ ] Flag any statute citation not found in the verified database
- [ ] Regular evaluation against updated benchmark scenarios
- [ ] Jurisdiction validation: verify cited statutes match the incident's
  jurisdiction

**Remediation Priority:** P0 — Most critical risk for law enforcement

---

### LLM10:2025 — Unbounded Consumption

**Threat:** Denial of service through excessive resource consumption, model
theft through repeated queries, or economic attacks through API abuse.

**Risk Level for SELMA:** MEDIUM

**Attack Scenarios:**
- Adversary sends thousands of long incident descriptions to exhaust GPU resources
- Systematic querying to extract model weights (model theft)
- Economic attack: drive up cloud compute costs

**SELMA Controls:**
- [ ] Rate limiting: maximum queries per user per time period
- [ ] Input length limits: maximum token count for incident descriptions
- [ ] Authentication required for all API access
- [ ] Usage monitoring and alerting for anomalous patterns
- [ ] Budget caps on cloud compute resources
- [ ] Query logging for forensic analysis

**Remediation Priority:** P2

---

## Part 2: OWASP Top 10 for Web Applications (2021)

These apply to any web-based deployment of SELMA (API server, web interface).

### A01:2021 — Broken Access Control

**Risk:** Unauthorized users access SELMA or view other users' analyses.

**SELMA Requirements:**
- [ ] Role-based access control (RBAC): only authorized law enforcement
  personnel can access SELMA
- [ ] Multi-factor authentication (MFA) required for all users
- [ ] Session management with automatic timeout
- [ ] Audit logging of all access and queries
- [ ] CJIS Security Policy compliance for authentication
- [ ] Principle of least privilege for all service accounts

---

### A02:2021 — Cryptographic Failures

**Risk:** Sensitive data transmitted or stored without proper encryption.

**SELMA Requirements:**
- [ ] TLS 1.3 for all data in transit (HTTPS only, no HTTP)
- [ ] Encryption at rest for any stored incident data or analysis results
- [ ] FIPS 140-2/140-3 validated cryptographic modules for government deployment
- [ ] No sensitive data in logs (incident descriptions, analysis results)
- [ ] Secure key management (HSM or equivalent for production)

---

### A03:2021 — Injection

**Risk:** SQL injection, command injection, or other injection attacks through
SELMA's input fields or API.

**SELMA Requirements:**
- [ ] Parameterized queries for any database interactions
- [ ] Input validation on all API endpoints
- [ ] Output encoding for web display
- [ ] No direct system command execution from user input
- [ ] Content-Type validation on all API requests

---

### A04:2021 — Insecure Design

**Risk:** Architectural flaws that cannot be fixed by implementation alone.

**SELMA Controls (by design):**
- [x] Human-in-the-loop architecture — SELMA cannot autonomously take actions
- [x] Read-only analytical tool — no write access to external systems
- [x] Open-source design enables public security audit
- [x] Separation of model inference from application logic
- [x] Training pipeline isolated from inference pipeline

---

### A05:2021 — Security Misconfiguration

**Risk:** Default credentials, unnecessary features enabled, verbose error
messages exposing system internals.

**SELMA Requirements:**
- [ ] Hardened deployment configuration templates provided
- [ ] No default credentials in any component
- [ ] Error messages sanitized — no stack traces or internal paths exposed
- [ ] Unnecessary HTTP methods disabled
- [ ] Security headers configured (HSTS, CSP, X-Frame-Options, etc.)
- [ ] Regular configuration audits

---

### A06:2021 — Vulnerable and Outdated Components

**Risk:** Known vulnerabilities in dependencies.

**SELMA Controls:**
- [x] Dependencies documented in requirements.txt with minimum versions
- [x] Open-source project enabling dependency scanning
- [ ] Automated dependency vulnerability scanning (Dependabot, Snyk, or similar)
- [ ] Regular dependency update cycle (monthly minimum)
- [ ] SBOM (Software Bill of Materials) published with each release

---

### A07:2021 — Identification and Authentication Failures

**Risk:** Weak authentication allows unauthorized access.

**SELMA Requirements:**
- [ ] Integration with agency identity providers (SAML, OIDC)
- [ ] Multi-factor authentication mandatory
- [ ] Account lockout after failed attempts
- [ ] Session tokens with appropriate expiration
- [ ] CJIS-compliant authentication (minimum requirements per CJIS Security Policy 5.6)

---

### A08:2021 — Software and Data Integrity Failures

**Risk:** Compromised CI/CD pipeline, unsigned updates, untrusted deserialization.

**SELMA Controls:**
- [x] Source code hosted on Codeberg with git integrity
- [x] Model provenance documented (MODEL_SELECTION.md)
- [ ] GPG-signed commits and releases
- [ ] Checksum verification for model weights
- [ ] Reproducible build process
- [ ] CI/CD pipeline security hardening

---

### A09:2021 — Security Logging and Monitoring Failures

**Risk:** Attacks go undetected due to insufficient logging.

**SELMA Requirements:**
- [ ] Log all authentication events (success and failure)
- [ ] Log all queries with timestamp, user, and input hash (not full content
  for privacy)
- [ ] Log all administrative actions
- [ ] Centralized log management with tamper-evident storage
- [ ] Real-time alerting for anomalous patterns
- [ ] Log retention per CJIS requirements (minimum 1 year)

---

### A10:2021 — Server-Side Request Forgery (SSRF)

**Risk:** SELMA server is tricked into making requests to internal resources.

**SELMA Controls:**
- [x] Current architecture has no outbound request capability from the
  inference endpoint
- [ ] Network segmentation: inference server isolated from internal networks
- [ ] Egress filtering: whitelist only necessary outbound connections
- [ ] No URL parsing or fetching from user-provided input

---

## Part 3: Compliance Summary Dashboard

### OWASP LLM Top 10 (2025) Compliance Status

| ID | Vulnerability | Risk | Status | Priority |
|----|--------------|------|--------|----------|
| LLM01 | Prompt Injection | CRITICAL | Partial | P0 |
| LLM02 | Sensitive Info Disclosure | HIGH | Good | P1 |
| LLM03 | Supply Chain | HIGH | Good | P1 |
| LLM04 | Data and Model Poisoning | CRITICAL | Good | P0 |
| LLM05 | Improper Output Handling | MEDIUM | Partial | P2 |
| LLM06 | Excessive Agency | LOW | Compliant | P3 |
| LLM07 | System Prompt Leakage | LOW | Compliant | P4 |
| LLM08 | Vector/Embedding Weakness | MEDIUM | N/A (no RAG) | P3 |
| LLM09 | Misinformation | CRITICAL | Partial | P0 |
| LLM10 | Unbounded Consumption | MEDIUM | Not Started | P2 |

### OWASP Web Top 10 (2021) Compliance Status

| ID | Vulnerability | Status | Priority |
|----|--------------|--------|----------|
| A01 | Broken Access Control | Not Started | P0 |
| A02 | Cryptographic Failures | Not Started | P0 |
| A03 | Injection | Partial | P1 |
| A04 | Insecure Design | Compliant | — |
| A05 | Security Misconfiguration | Not Started | P1 |
| A06 | Vulnerable Components | Partial | P2 |
| A07 | Auth Failures | Not Started | P0 |
| A08 | Integrity Failures | Partial | P1 |
| A09 | Logging Failures | Not Started | P1 |
| A10 | SSRF | Compliant | — |

### Legend
- **Compliant:** Controls fully implemented
- **Good:** Core controls in place, minor gaps remain
- **Partial:** Some controls exist, significant gaps remain
- **Not Started:** No controls implemented yet (deployment-phase items)

---

## Part 4: Security Architecture Recommendations

### Pre-Deployment (Required)

1. **Statute Verification Layer** — All model output statute citations must be
   validated against the verified statute index in real-time. Unverified
   citations must be flagged.

2. **Input Sanitization Pipeline** — All incident descriptions must pass through
   sanitization before model processing to detect and neutralize prompt injection.

3. **Output Schema Validation** — Model responses must conform to a defined
   schema. Malformed responses are rejected.

4. **Authentication & Authorization** — CJIS-compliant identity management
   with MFA, RBAC, and agency-level access controls.

### Deployment Phase

5. **Network Isolation** — Inference server on a dedicated, segmented network
   with strict ingress/egress rules.

6. **Encryption** — TLS 1.3 in transit, AES-256 at rest, FIPS 140-2 modules
   for government deployment.

7. **Audit Logging** — Comprehensive, tamper-evident logging with minimum
   1-year retention.

8. **Rate Limiting & Abuse Prevention** — Per-user query limits, input length
   caps, and anomaly detection.

### Ongoing Operations

9. **Regular Security Testing** — Quarterly penetration testing including
   adversarial prompt testing, red team exercises.

10. **Dependency Monitoring** — Automated CVE scanning of all dependencies
    with alerting and patching SLA.

11. **Bias Auditing** — Regular evaluation for demographic bias in model
    outputs using standardized test scenarios.

12. **Legal Currency Verification** — Quarterly review of training data
    against current law to ensure statutes have not been amended or repealed.

---

## Part 5: CJIS Security Policy Alignment

SELMA deployments that process Criminal Justice Information (CJI) must comply
with the FBI CJIS Security Policy (currently version 5.9.5). Key requirements:

| CJIS Requirement | SELMA Status |
|-------------------|-------------|
| 5.4 — Auditing and Accountability | Planned (logging framework) |
| 5.5 — Access Control | Planned (RBAC + MFA) |
| 5.6 — Identification and Authentication | Planned (agency IdP integration) |
| 5.7 — Configuration Management | Partial (version-controlled configs) |
| 5.8 — Media Protection | Planned (encryption at rest) |
| 5.9 — Physical Protection | Agency-dependent (data center security) |
| 5.10 — Systems and Communications Protection | Planned (TLS 1.3, network segmentation) |
| 5.11 — Formal Audits | Not Started |
| 5.12 — Personnel Security | Agency-dependent |
| 5.13 — Mobile Devices | N/A (server-based deployment) |

---

*Document version: 1.0*
*Last updated: May 2026*
*Framework versions: OWASP LLM Top 10 v2025, OWASP Web Top 10 v2021*
*Author: Ronin 48, LLC*
