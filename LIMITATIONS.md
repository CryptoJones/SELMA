# SELMA — Limitations, Scope, and Use Guidance

Read this before deploying SELMA in any operational context.

---

## What SELMA Does

Given a factual description of a criminal incident, SELMA identifies potentially applicable federal and state statutes, outlines the elements of each offense, summarizes sentencing ranges, and explains the legal reasoning connecting the facts to the charges.

## What SELMA Does Not Do

- **SELMA is not a licensed attorney.** Its outputs do not constitute legal advice and do not create an attorney-client relationship.
- **SELMA cannot access real-time legal databases.** It has a training data cutoff and cannot reflect legislation passed or case law decided after that date.
- **SELMA does not know your jurisdiction's charging preferences.** Prosecutor discretion, local diversion programs, plea policies, and charging thresholds vary by office and are not modeled.
- **SELMA does not cover local ordinances.** Municipal and county codes are not included in training data.
- **SELMA does not account for federal circuit splits.** Where federal circuits disagree on an interpretation, SELMA may reflect one circuit's view without flagging the conflict.
- **SELMA cannot read case files.** It works from what you tell it. Garbage in, garbage out.
- **SELMA can hallucinate statute numbers and case citations.** Always verify statute numbers and case citations against primary sources before including them in any official document.

---

## Scope of Practice

SELMA is designed to assist sworn law enforcement officers, detectives, and special agents in:

- Identifying potential charges based on facts of an incident
- Understanding elements of offenses for report writing and probable cause affidavits
- Preliminary research on unfamiliar statutes
- Training and scenario-based learning

**SELMA outputs must be reviewed by a prosecutor or attorney before use in charging documents, arrest affidavits, or court filings.**

---

## Known Limitations

| Area | Limitation |
|------|-----------|
| Currency | Training data has a cutoff date; recent legislation and case law may not be reflected |
| Local law | Municipal ordinances, county codes, and local rules not included |
| Sentencing | Sentencing ranges are general; guidelines departures, enhancements, and local practices not modeled |
| Case citations | Citations should always be verified — hallucination risk is real |
| Federal circuits | Circuit-specific interpretations may not be flagged as such |
| Training size | Fine-tuned on a small dataset; performance on edge cases and unusual fact patterns may degrade |

---

## Before You Deploy

- Have your agency attorney review sample outputs for your jurisdiction
- Establish a written policy on when SELMA may be consulted and what review is required before outputs are used in official documents
- Train officers on the difference between AI decision support and legal authority
- Do not allow SELMA outputs to substitute for consultation with the prosecuting attorney's office

---

## Version and Training Data

| Field | Value |
|-------|-------|
| Base model | meta-llama/Llama-3.3-70B-Instruct |
| Fine-tune method | QLoRA (4-bit) |
| Adapter | [Ronin48LLC/selma-lora-adapter](https://huggingface.co/Ronin48LLC/selma-lora-adapter) |
| Training date | May 2026 |
| Training data cutoff | See base model documentation |

---

## Reporting Errors

If SELMA produces an incorrect, dangerous, or misleading output:

- **GitHub:** [CryptoJones/SELMA/issues](https://github.com/CryptoJones/SELMA/issues)
- **Codeberg:** [Ronin48/SELMA/issues](https://codeberg.org/Ronin48/SELMA/issues)

Include the input, the output, and what the correct answer should have been. This directly improves future training data.
