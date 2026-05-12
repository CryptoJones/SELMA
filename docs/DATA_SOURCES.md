# SELMA Data Sources

## Primary Statutory Sources

### U.S. Code Title 18 — Crimes and Criminal Procedure

- **Source:** Office of the Law Revision Counsel, U.S. House of Representatives
- **URL:** Discovered dynamically from https://uscode.house.gov/download/download.shtml at fetch time; falls back to the pinned release `xml_usc18@119-88.zip` if discovery fails
- **Format:** USLM XML (United States Legislative Markup)
- **License:** Public Domain (U.S. Government Work)
- **Currency:** Always fetches the latest available release point
- **Coverage:** All federal criminal statutes (~2,700 sections)
  - Part I: Crimes (§§ 1–2725)
  - Part II: Criminal Procedure (§§ 3001–3772)
  - Part III: Prisons and Prisoners (§§ 4001–4353)
  - Part IV: Correction of Youthful Offenders (§§ 5001–5043)
  - Part V: Immunity of Witnesses (§§ 6001–6005)

### Georgia O.C.G.A. Title 16 — Crimes and Offenses

- **Source:** law.onecle.com (unofficial mirror)
- **Official Source:** https://www.lexisnexis.com/hottopics/gacode/
- **Format:** HTML (scraped to JSON)
- **License:** Fair Use (educational/research purposes)
- **Currency:** Last updated ~2016 on onecle.com; verify against official source
- **Coverage:** 17 chapters of Georgia criminal law
- **Note:** Georgia's official code is copyrighted. No official bulk download exists.

## Legal NLP Datasets (HuggingFace)

### ALEA US Courts NOS/Cause Classification
- **URL:** https://huggingface.co/datasets/alea-institute/alea-legal-benchmark-uscourts-nos-cause
- **Size:** 491K examples
- **Task:** Federal court filing → Nature of Suit code (151 categories)

### LegalBench
- **URL:** https://huggingface.co/datasets/nguha/legalbench
- **Size:** 91.8K examples across 162 tasks
- **Task:** Legal reasoning benchmark (issue-spotting, rule-recall, interpretation)

### CaseHOLD
- **URL:** https://huggingface.co/datasets/casehold/casehold
- **Size:** 585K examples
- **Task:** Legal holding classification from US case law

## Synthetic Training Data

Generated incident-to-charge mappings covering common criminal scenarios for
both federal (Title 18) and Georgia (Title 16) jurisdictions. See
`data/synthetic/` for the generated dataset and generation scripts.

## Base Model

- **Model:** Meta Llama 3.3 70B Instruct
- **Source:** https://huggingface.co/meta-llama/Llama-3.3-70B-Instruct
- **License:** Llama 3.1 Community License (Meta Platforms, Inc.)
- **Origin:** United States
- **Rationale:** See [MODEL_SELECTION.md](MODEL_SELECTION.md) for full rationale

## Trusted Sources Allowlist

All URLs fetched by SELMA's data collection scripts are validated against
`configs/trusted_sources.yaml` before any network request is made. A fetch
against an unlisted domain is blocked with an error, preventing malicious
or spoofed feeds from reaching training data.

### Viewing the allowlist

```bash
python scripts/add_source.py list
python scripts/add_source.py list --jurisdiction georgia
```

### Adding a new source

New sources require an explicit entry in the allowlist. Only HTTPS URLs are
accepted. After adding, commit `configs/trusted_sources.yaml` — the git
history is the audit trail for every source addition.

```bash
# Example: adding California Penal Code from leginfo.legislature.ca.gov
python scripts/add_source.py \
    --id california_leginfo \
    --name "California Penal Code (leginfo.legislature.ca.gov)" \
    --jurisdiction california \
    --type statute \
    --url-pattern "https://leginfo.legislature.ca.gov/" \
    --format html \
    --license public_domain

# Then commit the allowlist change
git add configs/trusted_sources.yaml
git commit -m "Add California Penal Code source (leginfo.legislature.ca.gov)"
```

### Allowlist fields

| Field | Required | Description |
|---|---|---|
| `id` | Yes | Unique snake_case identifier |
| `name` | Yes | Human-readable description |
| `jurisdiction` | Yes | `federal`, or a state name (e.g. `georgia`, `california`) |
| `type` | Yes | `statute`, `caselaw`, or `dataset` |
| `url_patterns` | Yes | One or more HTTPS URL prefixes; fetched URLs must start with one |
| `format` | Yes | `uslm_xml`, `html`, `csv`, `jsonl`, `json`, or `pdf` |
| `license` | Yes | `public_domain`, `fair_use`, `open`, `cc_by`, etc. |
| `discovery_url` | No | Page to scrape to find the current download URL |
| `discovery_regex` | No | Regex to extract the download URL from `discovery_url` |
| `note` | No | Caveats, currency notes, or verification guidance |

## Data Provenance

All training data sources are documented here for reproducibility and
legal compliance. Users should verify statutory text against official
sources before relying on it for operational purposes.
