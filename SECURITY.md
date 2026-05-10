# SELMA Security Policy

## Reporting Security Vulnerabilities

If you discover a security vulnerability in SELMA, please report it responsibly.

**DO NOT** open a public issue for security vulnerabilities.

**Email:** security@ronin48.io
**Subject:** [SELMA Security] Brief description

We will acknowledge receipt within 48 hours and provide a detailed response
within 7 business days.

## Security Design Principles

SELMA is designed with the following security principles:

### 1. Human-in-the-Loop (MANDATORY)

SELMA is an advisory tool. Its outputs MUST be reviewed by qualified legal
professionals before any law enforcement action is taken. SELMA must never be
deployed as an autonomous decision-making system.

### 2. No Agency

SELMA has no ability to take actions in external systems. It is a text-in,
text-out analytical tool. It cannot:
- Access law enforcement databases
- File charges or create reports
- Contact individuals
- Modify records in any system

### 3. Open Source Transparency

All code, training data, prompts, and analytical frameworks are open source.
This enables:
- Public security audit by independent researchers
- Defense attorney review of the system's methodology
- Judicial scrutiny of how conclusions are reached
- Community identification of biases or errors

### 4. Verified Legal Sources

Training data is derived from:
- Official U.S. government statutory text (public domain)
- Hand-crafted synthetic examples with verifiable citations
- No real case data, no real PII, no real incident reports

### 5. Supply Chain Security

- Base model: Meta Llama 3.1 70B (U.S.-origin, verified provenance)
- Chinese-origin models explicitly rejected (see docs/MODEL_SELECTION.md)
- All dependencies documented and version-pinned

## OWASP Compliance

See [docs/OWASP_COMPLIANCE.md](docs/OWASP_COMPLIANCE.md) for the full security
evaluation against:
- OWASP Top 10 for LLM Applications (2025)
- OWASP Top 10 for Web Applications (2021)

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.2.x   | Yes       |
| < 0.2   | No        |

## Security Contacts

- **Primary:** security@ronin48.io
- **Organization:** Ronin 48, LLC
- **PGP Key:** [Available upon request]
