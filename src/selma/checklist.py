"""
Elements checklist generator for SELMA.

Generates field-ready plain-text checklists from PotentialCharge objects that
officers can use during an investigation or when writing an arrest affidavit.
"""

from typing import TYPE_CHECKING

from src.selma.schema import ChargeCategory, PotentialCharge

if TYPE_CHECKING:
    from src.selma.schema import IncidentAnalysis

_DIVIDER = "═" * 55


def _charge_header(charge: PotentialCharge) -> str:
    """Build the charge title line."""
    citation = charge.statute.full_citation
    name = charge.statute.name or ""
    severity = charge.severity.value.upper() if charge.severity else ""
    degree = charge.degree

    parts = []
    if severity:
        parts.append(severity)
    if degree:
        parts.append(degree.title())
    bracket = f" [{' — '.join(parts)}]" if parts else ""

    if name:
        return f"{citation} — {name}{bracket}"
    return f"{citation}{bracket}"


def _format_sentencing(charge: PotentialCharge) -> str:
    """Format the sentencing block, or empty string if none."""
    s = charge.sentencing
    if s is None:
        return ""

    section = f"USSG § {s.guideline_section}" if s.guideline_section else s.source
    level = f"Offense Level {s.offense_level}" if s.offense_level is not None else ""
    ch = f"CH {s.criminal_history_category}" if s.criminal_history_category else ""

    if s.max_months is None:
        range_str = "Life"
    elif s.min_months is not None:
        range_str = f"{s.min_months}–{s.max_months} months"
    else:
        range_str = ""

    pieces = [p for p in [section, level, ch] if p]
    summary = " | ".join(pieces)
    if range_str:
        summary = f"{summary}: {range_str}"

    return f"\nSENTENCING (if convicted):\n  {summary}\n"


def generate_checklist(charge: PotentialCharge) -> str:
    """
    Returns a plain-text checklist for a single charge.

    Format:
    ═══════════════════════════════════════════════════════
    CHARGE: 18 U.S.C. § 1111 — Murder [FELONY — First Degree]
    ═══════════════════════════════════════════════════════

    ELEMENTS CHECKLIST
    Officers must be able to articulate facts supporting each element.

    [ ] 1. Unlawful killing of a human being
           Evidence type: Physical, witness testimony
           Status: NOT MET
           Supporting facts: —

    [x] 2. With malice aforethought
           ...
    """
    lines = [
        _DIVIDER,
        f"CHARGE: {_charge_header(charge)}",
        _DIVIDER,
        "",
        "ELEMENTS CHECKLIST",
        "Officers must be able to articulate facts supporting each element.",
    ]

    for i, element in enumerate(charge.elements, start=1):
        box = "[x]" if element.met_by_facts else "[ ]"
        status = "MET" if element.met_by_facts else "NOT MET"
        facts = element.supporting_facts.strip() if element.supporting_facts.strip() else "—"
        evidence_type = element.element_type.replace("_", " ").title()

        lines.append("")
        lines.append(f"{box} {i}. {element.description}")
        lines.append(f"       Evidence type: {evidence_type}")
        lines.append(f"       Status: {status}")
        lines.append(f"       Supporting facts: {facts}")

    sentencing_block = _format_sentencing(charge)
    if sentencing_block:
        lines.append(sentencing_block.rstrip())

    if charge.notes:
        lines.append("")
        lines.append(f"NOTES: {charge.notes}")

    lines.append("")
    return "\n".join(lines)


def generate_full_checklist(analysis: "IncidentAnalysis") -> str:
    """
    Generate checklist for all criminal charges in an IncidentAnalysis.
    Civil parallels are noted briefly at the end.
    """
    sections = []

    criminal_charges = [c for c in analysis.potential_charges if c.category == ChargeCategory.CRIMINAL]
    for charge in criminal_charges:
        sections.append(generate_checklist(charge))

    if analysis.civil_parallels:
        sections.append("CIVIL PARALLELS (for awareness only — not actionable by the officer):")
        for cp in analysis.civil_parallels:
            citation = cp.statute.full_citation
            name = cp.statute.name or ""
            label = f"  - {citation}"
            if name:
                label += f" — {name}"
            sections.append(label)
        sections.append("")

    return "\n".join(sections)


def checklist_to_dict(charge: PotentialCharge) -> dict:
    """Return checklist as a structured dict (for JSON export or API use)."""
    elements = []
    for element in charge.elements:
        elements.append({
            "description": element.description,
            "element_type": element.element_type,
            "met": element.met_by_facts,
            "supporting_facts": element.supporting_facts or None,
        })

    sentencing = None
    if charge.sentencing:
        s = charge.sentencing
        sentencing = {
            "source": s.source,
            "guideline_section": s.guideline_section or None,
            "offense_level": s.offense_level,
            "criminal_history_category": s.criminal_history_category,
            "min_months": s.min_months,
            "max_months": s.max_months,
            "notes": s.notes or None,
        }

    return {
        "charge": _charge_header(charge),
        "statute": charge.statute.full_citation,
        "category": charge.category.value,
        "severity": charge.severity.value if charge.severity else None,
        "degree": charge.degree or None,
        "elements": elements,
        "sentencing": sentencing,
        "notes": charge.notes or None,
    }
