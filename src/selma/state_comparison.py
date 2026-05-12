"""
State/jurisdiction comparison module for SELMA.

Maps primary charges to equivalent statutes in other jurisdictions using a
static cross-reference table. Does not re-run the ML model.
"""

from __future__ import annotations

from typing import Optional

from src.selma.schema import (
    ChargeCategory,
    Jurisdiction,
    PotentialCharge,
    StateComparison,
    StatuteReference,
)

# ---------------------------------------------------------------------------
# Cross-reference table: federal statute → nearest equivalent by jurisdiction
# ---------------------------------------------------------------------------

STATUTE_CROSSREF: dict[str, dict[str, str]] = {
    # Homicide
    "18 U.S.C. § 1111": {
        "georgia": "O.C.G.A. § 16-5-1",
        "california": "Cal. Penal Code § 187",
        "texas": "Tex. Penal Code § 19.02",
        "new_york": "N.Y. Penal Law § 125.25",
        "florida": "Fla. Stat. § 782.04",
    },
    "18 U.S.C. § 1112": {
        "georgia": "O.C.G.A. § 16-5-2",
        "california": "Cal. Penal Code § 192",
        "texas": "Tex. Penal Code § 19.04",
        "new_york": "N.Y. Penal Law § 125.20",
        "florida": "Fla. Stat. § 782.07",
    },
    # Kidnapping
    "18 U.S.C. § 1201": {
        "georgia": "O.C.G.A. § 16-5-40",
        "california": "Cal. Penal Code § 207",
        "texas": "Tex. Penal Code § 20.04",
        "new_york": "N.Y. Penal Law § 135.25",
        "florida": "Fla. Stat. § 787.01",
    },
    # Robbery
    "18 U.S.C. § 2111": {
        "georgia": "O.C.G.A. § 16-8-40",
        "california": "Cal. Penal Code § 211",
        "texas": "Tex. Penal Code § 29.02",
        "new_york": "N.Y. Penal Law § 160.10",
        "florida": "Fla. Stat. § 812.13",
    },
    # Carjacking
    "18 U.S.C. § 2119": {
        "georgia": "O.C.G.A. § 16-5-44.1",
        "california": "Cal. Penal Code § 215",
        "texas": "Tex. Penal Code § 29.02",
        "new_york": "N.Y. Penal Law § 160.15",
        "florida": "Fla. Stat. § 812.133",
    },
    # Assault
    "18 U.S.C. § 113(a)(1)": {
        "georgia": "O.C.G.A. § 16-5-21",
        "california": "Cal. Penal Code § 245",
        "texas": "Tex. Penal Code § 22.02",
        "new_york": "N.Y. Penal Law § 120.10",
        "florida": "Fla. Stat. § 784.021",
    },
    # Drug trafficking
    "21 U.S.C. § 841(a)(1)": {
        "georgia": "O.C.G.A. § 16-13-31",
        "california": "Cal. Health & Safety Code § 11352",
        "texas": "Tex. Health & Safety Code § 481.112",
        "new_york": "N.Y. Penal Law § 220.39",
        "florida": "Fla. Stat. § 893.135",
    },
    # Simple drug possession
    "21 U.S.C. § 844": {
        "georgia": "O.C.G.A. § 16-13-30",
        "california": "Cal. Health & Safety Code § 11350",
        "texas": "Tex. Health & Safety Code § 481.115",
        "new_york": "N.Y. Penal Law § 220.03",
        "florida": "Fla. Stat. § 893.13",
    },
    # Weapons — felon in possession
    "18 U.S.C. § 922(g)": {
        "georgia": "O.C.G.A. § 16-11-131",
        "california": "Cal. Penal Code § 29800",
        "texas": "Tex. Penal Code § 46.04",
        "new_york": "N.Y. Penal Law § 265.01-b",
        "florida": "Fla. Stat. § 790.23",
    },
    # Fraud / wire fraud
    "18 U.S.C. § 1343": {
        "georgia": "O.C.G.A. § 16-9-90",
        "california": "Cal. Penal Code § 532",
        "texas": "Tex. Penal Code § 32.46",
        "new_york": "N.Y. Penal Law § 190.65",
        "florida": "Fla. Stat. § 817.034",
    },
    # Theft / interstate transportation of stolen property
    "18 U.S.C. § 2314": {
        "georgia": "O.C.G.A. § 16-8-2",
        "california": "Cal. Penal Code § 496",
        "texas": "Tex. Penal Code § 31.03",
        "new_york": "N.Y. Penal Law § 165.54",
        "florida": "Fla. Stat. § 812.014",
    },
    # Arson
    "18 U.S.C. § 81": {
        "georgia": "O.C.G.A. § 16-7-60",
        "california": "Cal. Penal Code § 451",
        "texas": "Tex. Penal Code § 28.02",
        "new_york": "N.Y. Penal Law § 150.20",
        "florida": "Fla. Stat. § 806.01",
    },
    # Sexual assault
    "18 U.S.C. § 2242": {
        "georgia": "O.C.G.A. § 16-6-1",
        "california": "Cal. Penal Code § 261",
        "texas": "Tex. Penal Code § 22.011",
        "new_york": "N.Y. Penal Law § 130.35",
        "florida": "Fla. Stat. § 794.011",
    },
    # Stalking
    "18 U.S.C. § 2261A": {
        "georgia": "O.C.G.A. § 16-5-90",
        "california": "Cal. Penal Code § 646.9",
        "texas": "Tex. Penal Code § 42.072",
        "new_york": "N.Y. Penal Law § 120.45",
        "florida": "Fla. Stat. § 784.048",
    },
}

# Human-readable notes about key differences per jurisdiction
_JURISDICTION_NOTES: dict[str, str] = {
    "georgia": (
        "Georgia uses the 'required evidence test' for merger/lesser-included analysis. "
        "Sentencing is largely discretionary with mandatory minimums for serious violent felonies "
        "(O.C.G.A. § 17-10-6.1). No binding sentencing grid."
    ),
    "california": (
        "California uses indeterminate sentencing with determinate terms set by Penal Code. "
        "Proposition 36 and 47 affect drug offense treatment. Three-strikes law applies."
    ),
    "texas": (
        "Texas uses a tiered felony system (capital, 1st–3rd degree, state jail). "
        "Sentencing ranges are statutory with jury sentencing option. "
        "Enhancement statutes significantly increase ranges for repeat offenders."
    ),
    "new_york": (
        "New York uses a tiered felony/misdemeanor system with determinate sentencing "
        "for violent felonies. Drug law reform (MRTA 2021) decriminalized small amounts. "
        "Hate crime enhancement statute applies."
    ),
    "florida": (
        "Florida uses the Criminal Punishment Code (scoresheet-based sentencing). "
        "10-20-Life mandatory minimums for firearm offenses. "
        "Stand Your Ground law may affect self-defense analysis."
    ),
}

# Map Jurisdiction enum to string keys used in STATUTE_CROSSREF
_JURISDICTION_KEY: dict[Jurisdiction, str] = {
    Jurisdiction.FEDERAL: "federal",
    Jurisdiction.GEORGIA: "georgia",
}


def get_crossref(federal_citation: str, jurisdiction: str) -> Optional[str]:
    """Return the equivalent statute citation in the target jurisdiction, or None."""
    entry = STATUTE_CROSSREF.get(federal_citation)
    if entry is None:
        return None
    return entry.get(jurisdiction)


def compare_jurisdictions(
    incident_description: str,
    primary_charges: list[PotentialCharge],
    compare_to: list[Jurisdiction],
) -> list[StateComparison]:
    """Generate StateComparison entries for each requested jurisdiction.

    Maps each primary charge to an equivalent statute in the target jurisdiction
    using STATUTE_CROSSREF. Notes key differences in severity, elements, and
    sentencing approach.
    """
    comparisons: list[StateComparison] = []

    for jurisdiction in compare_to:
        jur_key = _JURISDICTION_KEY.get(jurisdiction, jurisdiction.value)
        mapped_charges: list[PotentialCharge] = []
        unmatched: list[str] = []

        for charge in primary_charges:
            federal_citation = charge.statute.full_citation
            equiv = get_crossref(federal_citation, jur_key)
            if equiv is None:
                unmatched.append(federal_citation)
                continue

            # Build a minimal equivalent charge referencing the mapped statute
            equiv_statute = StatuteReference(
                jurisdiction=jurisdiction,
                title="",
                section="",
                name=charge.statute.name,
                full_citation=equiv,
            )
            equiv_charge = PotentialCharge(
                statute=equiv_statute,
                category=charge.category,
                severity=charge.severity,
                degree=charge.degree,
                confidence=charge.confidence,
                reasoning=(
                    f"Equivalent to {federal_citation} in {jurisdiction.value} jurisdiction."
                ),
            )
            mapped_charges.append(equiv_charge)

        notes_parts = [_JURISDICTION_NOTES.get(jur_key, "")]
        if unmatched:
            notes_parts.append(
                f"No cross-reference found for: {', '.join(unmatched)}. "
                "Manual review required."
            )

        key_differences = _build_key_differences(primary_charges, mapped_charges, jur_key)

        comparisons.append(
            StateComparison(
                jurisdiction=jurisdiction,
                charges=mapped_charges,
                key_differences=key_differences,
                notes=" ".join(filter(None, notes_parts)),
            )
        )

    return comparisons


def _build_key_differences(
    primary: list[PotentialCharge],
    mapped: list[PotentialCharge],
    jur_key: str,
) -> str:
    """Produce a concise summary of key differences between charge sets."""
    if not primary:
        return ""

    differences: list[str] = []

    fed_citations = [c.statute.full_citation for c in primary]
    state_citations = [c.statute.full_citation for c in mapped]

    if fed_citations and state_citations:
        pairs = list(zip(fed_citations, state_citations))
        mapping_str = "; ".join(f"{f} → {s}" for f, s in pairs)
        differences.append(f"Statute mapping: {mapping_str}.")

    note = _JURISDICTION_NOTES.get(jur_key)
    if note:
        differences.append(note)

    return " ".join(differences)
