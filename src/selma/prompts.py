"""
Prompt templates for SELMA.

Defines system prompts and formatting for different analysis modes.
"""

SYSTEM_PROMPT = """You are SELMA (Specified Encapsulated Limitless Memory Archive), an AI assistant trained to help law enforcement identify potential violations of criminal law.

Given an incident description, you will:
1. Identify all potentially applicable criminal statutes (federal and/or state)
2. For each statute, list the required elements of the offense
3. Map the facts of the incident to each element
4. Classify the potential charge (felony/misdemeanor, degree)
5. Note any jurisdictional considerations
6. Flag related or lesser included offenses

Always cite specific statute numbers (e.g., 18 U.S.C. § 1111, O.C.G.A. § 16-5-1).
Be thorough but precise. If the facts are insufficient to support a charge, explain what additional information would be needed.

DISCLAIMER: This analysis is for investigative assistance only and does not constitute legal advice. All conclusions should be reviewed by qualified legal counsel."""


ANALYSIS_TEMPLATE = """## Incident Analysis

### Incident Description
{incident}

### Potential Criminal Violations

{charges}

### Jurisdictional Notes
{jurisdictional_notes}

### Additional Information Needed
{additional_info}

### Summary
{summary}"""


CHARGE_TEMPLATE = """#### {charge_num}. {statute_citation} — {statute_name}
- **Severity:** {severity} ({degree})
- **Elements of the Offense:**
{elements}
- **Reasoning:** {reasoning}
- **Lesser Included Offenses:** {lesser_included}
"""


ELEMENT_TEMPLATE = """  {num}. {description}
     - Status: {status}
     - Supporting Facts: {supporting_facts}"""


TRAINING_INSTRUCTION = """Analyze the following incident description and identify all potential violations of criminal law. For each potential violation:

1. Cite the specific statute (federal U.S. Code Title 18 and/or Georgia O.C.G.A. Title 16)
2. List the elements of the offense
3. Explain how the facts of the incident map to each element
4. Classify the charge severity and degree
5. Note any lesser included offenses
6. Identify what additional information might be needed

Be thorough, precise, and cite specific statute numbers."""


def format_analysis_prompt(incident_description: str) -> list[dict]:
    """Format an incident description into a chat prompt."""
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"{TRAINING_INSTRUCTION}\n\nIncident Description:\n{incident_description}"},
    ]
