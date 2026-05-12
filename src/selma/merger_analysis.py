"""
Merger doctrine analysis for SELMA charge sets.

Implements rule-based merger/lesser-included analysis for federal (Blockburger test)
and Georgia (required evidence test) jurisdictions.
"""

from __future__ import annotations

from src.selma.schema import MergerAnalysis, PotentialCharge

# ---------------------------------------------------------------------------
# Federal merger rules (Blockburger test)
# ---------------------------------------------------------------------------

FEDERAL_MERGER_RULES: dict[str, MergerAnalysis] = {
    # Homicide
    "18 U.S.C. § 1111": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Voluntary manslaughter (§ 1112) is lesser included; cannot convict of both",
    ),
    "18 U.S.C. § 1112": MergerAnalysis(
        separately_punishable=False,
        merges_with=["18 U.S.C. § 1111"],
        lesser_included_of="18 U.S.C. § 1111",
        notes="Merges into murder if both charged; cannot convict of both",
    ),
    # Kidnapping / false imprisonment
    "18 U.S.C. § 1201": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Kidnapping; false imprisonment (§ 1201(a) lesser) merges in",
    ),
    "18 U.S.C. § 1201(a)": MergerAnalysis(
        separately_punishable=False,
        merges_with=["18 U.S.C. § 1201"],
        lesser_included_of="18 U.S.C. § 1201",
        notes="False imprisonment merges into kidnapping",
    ),
    # Robbery / larceny
    "18 U.S.C. § 2111": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Special maritime/territorial robbery; larceny is lesser included",
    ),
    "18 U.S.C. § 661": MergerAnalysis(
        separately_punishable=False,
        merges_with=["18 U.S.C. § 2111"],
        lesser_included_of="18 U.S.C. § 2111",
        notes="Larceny/theft merges into robbery when same conduct",
    ),
    # Assault / assault with intent
    "18 U.S.C. § 113(a)(1)": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Assault with intent to commit murder; simple assault is lesser included",
    ),
    "18 U.S.C. § 113(a)(4)": MergerAnalysis(
        separately_punishable=False,
        merges_with=["18 U.S.C. § 113(a)(1)"],
        lesser_included_of="18 U.S.C. § 113(a)(1)",
        notes="Simple assault merges into aggravated assault when same act",
    ),
    # Drug trafficking / possession
    "21 U.S.C. § 841(a)(1)": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Drug trafficking; simple possession (§ 844) merges in when same transaction",
    ),
    "21 U.S.C. § 844": MergerAnalysis(
        separately_punishable=False,
        merges_with=["21 U.S.C. § 841(a)(1)"],
        lesser_included_of="21 U.S.C. § 841(a)(1)",
        notes="Simple possession is lesser included of trafficking; merges when same drugs",
    ),
    # Carjacking / vehicle theft
    "18 U.S.C. § 2119": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Carjacking; motor vehicle theft (§ 2312) can be lesser included",
    ),
    "18 U.S.C. § 2312": MergerAnalysis(
        separately_punishable=False,
        merges_with=["18 U.S.C. § 2119"],
        lesser_included_of="18 U.S.C. § 2119",
        notes="Interstate transport of stolen vehicle merges into carjacking when same vehicle",
    ),
}

# ---------------------------------------------------------------------------
# Georgia merger rules (required evidence test)
# ---------------------------------------------------------------------------

GEORGIA_MERGER_RULES: dict[str, MergerAnalysis] = {
    # Homicide
    "O.C.G.A. § 16-5-1": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Murder; voluntary manslaughter (§ 16-5-2) and felony murder merge in",
    ),
    "O.C.G.A. § 16-5-2": MergerAnalysis(
        separately_punishable=False,
        merges_with=["O.C.G.A. § 16-5-1"],
        lesser_included_of="O.C.G.A. § 16-5-1",
        notes="Voluntary manslaughter merges into murder; cannot convict of both",
    ),
    "O.C.G.A. § 16-5-3": MergerAnalysis(
        separately_punishable=False,
        merges_with=["O.C.G.A. § 16-5-1"],
        lesser_included_of="O.C.G.A. § 16-5-1",
        notes="Involuntary manslaughter merges into murder under required evidence test",
    ),
    # Assault / battery
    "O.C.G.A. § 16-5-20": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Simple assault; aggravated assault (§ 16-5-21) is greater offense",
    ),
    "O.C.G.A. § 16-5-21": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Aggravated assault; simple assault (§ 16-5-20) merges in",
    ),
    "O.C.G.A. § 16-5-23": MergerAnalysis(
        separately_punishable=False,
        merges_with=["O.C.G.A. § 16-5-21"],
        lesser_included_of="O.C.G.A. § 16-5-21",
        notes="Simple battery merges into aggravated assault under required evidence test",
    ),
    # Robbery / armed robbery
    "O.C.G.A. § 16-8-40": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Robbery; theft (§ 16-8-2) merges in when same taking",
    ),
    "O.C.G.A. § 16-8-41": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Armed robbery; robbery (§ 16-8-40) merges in as lesser included",
    ),
    "O.C.G.A. § 16-8-2": MergerAnalysis(
        separately_punishable=False,
        merges_with=["O.C.G.A. § 16-8-40", "O.C.G.A. § 16-8-41"],
        lesser_included_of="O.C.G.A. § 16-8-40",
        notes="Theft by taking merges into robbery when same transaction",
    ),
    # Kidnapping / false imprisonment
    "O.C.G.A. § 16-5-40": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Kidnapping; false imprisonment (§ 16-5-41) merges in as lesser included",
    ),
    "O.C.G.A. § 16-5-41": MergerAnalysis(
        separately_punishable=False,
        merges_with=["O.C.G.A. § 16-5-40"],
        lesser_included_of="O.C.G.A. § 16-5-40",
        notes="False imprisonment merges into kidnapping under required evidence test",
    ),
    # Drug offenses
    "O.C.G.A. § 16-13-30": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Purchase, possession, manufacture, distribution — trafficking (§ 16-13-31) is greater",
    ),
    "O.C.G.A. § 16-13-31": MergerAnalysis(
        separately_punishable=True,
        merges_with=[],
        lesser_included_of="",
        notes="Drug trafficking; possession (§ 16-13-30) merges in as lesser included",
    ),
}

# Combined lookup across both rule sets
_ALL_RULES: dict[str, MergerAnalysis] = {**FEDERAL_MERGER_RULES, **GEORGIA_MERGER_RULES}


def _get_rule(citation: str) -> MergerAnalysis | None:
    return _ALL_RULES.get(citation)


def analyze_merger(charges: list[PotentialCharge]) -> list[PotentialCharge]:
    """Annotate each charge with merger analysis.

    Flags charges that cannot be stacked, identifies lesser-included relationships.
    Returns charges with .merger field populated.
    """
    citations_present = {c.statute.full_citation for c in charges}

    for charge in charges:
        citation = charge.statute.full_citation
        rule = _get_rule(citation)
        if rule is None:
            # No known merger rule — default to separately punishable
            charge.merger = MergerAnalysis(separately_punishable=True)
            continue

        # Determine if the greater offense is actually in this charge set
        merges_with_present = [c for c in rule.merges_with if c in citations_present]
        lesser_included_present = (
            rule.lesser_included_of != "" and rule.lesser_included_of in citations_present
        )

        charge.merger = MergerAnalysis(
            separately_punishable=rule.separately_punishable and not (merges_with_present or lesser_included_present),
            merges_with=merges_with_present,
            lesser_included_of=rule.lesser_included_of if lesser_included_present else "",
            double_jeopardy_bar=bool(merges_with_present or lesser_included_present),
            notes=rule.notes,
        )

    return charges


def merger_warnings(charges: list[PotentialCharge]) -> list[str]:
    """Return human-readable warning strings for problematic charge combinations."""
    warnings: list[str] = []

    for charge in charges:
        if charge.merger is None:
            continue
        citation = charge.statute.full_citation
        name = charge.statute.name or citation

        if charge.merger.lesser_included_of:
            greater = charge.merger.lesser_included_of
            warnings.append(
                f"WARNING: {citation} ({name}) merges into {greater} — cannot convict of both."
            )
        elif charge.merger.merges_with:
            for greater in charge.merger.merges_with:
                warnings.append(
                    f"WARNING: {citation} ({name}) merges with {greater} — cannot stack these charges."
                )

        if charge.merger.double_jeopardy_bar:
            warnings.append(
                f"DOUBLE JEOPARDY: {citation} ({name}) cannot be charged separately — double jeopardy bar applies."
            )

    return warnings
