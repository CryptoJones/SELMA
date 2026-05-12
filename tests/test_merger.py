"""Tests for src/selma/merger_analysis.py."""

import sys

sys.path.insert(0, ".")

from src.selma.merger_analysis import (
    FEDERAL_MERGER_RULES,
    GEORGIA_MERGER_RULES,
    analyze_merger,
    merger_warnings,
)
from src.selma.schema import (
    ChargeCategory,
    Jurisdiction,
    MergerAnalysis,
    PotentialCharge,
    StatuteReference,
)


def _make_charge(full_citation: str, name: str = "", jurisdiction: Jurisdiction = Jurisdiction.FEDERAL) -> PotentialCharge:
    """Build a minimal PotentialCharge with the given full citation."""
    statute = StatuteReference(
        jurisdiction=jurisdiction,
        title="",
        section="",
        name=name,
        full_citation=full_citation,
    )
    return PotentialCharge(statute=statute)


# ---------------------------------------------------------------------------
# Rule table sanity checks
# ---------------------------------------------------------------------------

def test_federal_rules_not_empty():
    assert len(FEDERAL_MERGER_RULES) >= 6


def test_georgia_rules_not_empty():
    assert len(GEORGIA_MERGER_RULES) >= 6


def test_murder_is_separately_punishable():
    rule = FEDERAL_MERGER_RULES["18 U.S.C. § 1111"]
    assert rule.separately_punishable is True
    assert rule.lesser_included_of == ""


def test_manslaughter_merges_into_murder():
    rule = FEDERAL_MERGER_RULES["18 U.S.C. § 1112"]
    assert rule.separately_punishable is False
    assert "18 U.S.C. § 1111" in rule.merges_with
    assert rule.lesser_included_of == "18 U.S.C. § 1111"


def test_georgia_murder_is_separately_punishable():
    rule = GEORGIA_MERGER_RULES["O.C.G.A. § 16-5-1"]
    assert rule.separately_punishable is True


def test_georgia_voluntary_manslaughter_merges():
    rule = GEORGIA_MERGER_RULES["O.C.G.A. § 16-5-2"]
    assert rule.separately_punishable is False
    assert "O.C.G.A. § 16-5-1" in rule.merges_with


# ---------------------------------------------------------------------------
# analyze_merger
# ---------------------------------------------------------------------------

def test_analyze_merger_flags_lesser_included():
    murder = _make_charge("18 U.S.C. § 1111", "Murder")
    manslaughter = _make_charge("18 U.S.C. § 1112", "Voluntary Manslaughter")
    charges = analyze_merger([murder, manslaughter])

    # Manslaughter should be flagged as merging into murder
    mans_result = next(c for c in charges if c.statute.full_citation == "18 U.S.C. § 1112")
    assert mans_result.merger is not None
    assert mans_result.merger.double_jeopardy_bar is True
    assert mans_result.merger.lesser_included_of == "18 U.S.C. § 1111"


def test_analyze_merger_non_merging_charges_unaffected():
    """Two independently punishable charges should not trigger merger warnings."""
    murder = _make_charge("18 U.S.C. § 1111", "Murder")
    trafficking = _make_charge("21 U.S.C. § 841(a)(1)", "Drug Trafficking")
    charges = analyze_merger([murder, trafficking])

    murder_result = next(c for c in charges if c.statute.full_citation == "18 U.S.C. § 1111")
    assert murder_result.merger.separately_punishable is True
    assert murder_result.merger.double_jeopardy_bar is False


def test_analyze_merger_unknown_citation_defaults_to_punishable():
    charge = _make_charge("18 U.S.C. § 9999", "Unknown")
    charges = analyze_merger([charge])
    assert charges[0].merger.separately_punishable is True


def test_analyze_merger_without_greater_offense():
    """If only manslaughter is charged (without murder), no merge warning."""
    manslaughter = _make_charge("18 U.S.C. § 1112", "Voluntary Manslaughter")
    charges = analyze_merger([manslaughter])
    mans_result = charges[0]
    # merges_with present in rules, but murder is not in the charge set
    assert mans_result.merger.merges_with == []
    assert mans_result.merger.double_jeopardy_bar is False


# ---------------------------------------------------------------------------
# merger_warnings
# ---------------------------------------------------------------------------

def test_merger_warnings_returns_strings():
    murder = _make_charge("18 U.S.C. § 1111", "Murder")
    manslaughter = _make_charge("18 U.S.C. § 1112", "Voluntary Manslaughter")
    charges = analyze_merger([murder, manslaughter])
    warnings = merger_warnings(charges)
    assert isinstance(warnings, list)
    assert len(warnings) > 0
    assert all(isinstance(w, str) for w in warnings)


def test_merger_warnings_content():
    murder = _make_charge("18 U.S.C. § 1111", "Murder")
    manslaughter = _make_charge("18 U.S.C. § 1112", "Voluntary Manslaughter")
    charges = analyze_merger([murder, manslaughter])
    warnings = merger_warnings(charges)
    combined = " ".join(warnings)
    assert "1112" in combined
    assert "1111" in combined


def test_merger_warnings_empty_for_non_merging():
    murder = _make_charge("18 U.S.C. § 1111", "Murder")
    trafficking = _make_charge("21 U.S.C. § 841(a)(1)", "Drug Trafficking")
    charges = analyze_merger([murder, trafficking])
    warnings = merger_warnings(charges)
    assert warnings == []


def test_merger_warnings_no_merger_field():
    """Charges with merger=None are skipped gracefully."""
    charge = _make_charge("18 U.S.C. § 9998", "Fake")
    charge.merger = None
    warnings = merger_warnings([charge])
    assert warnings == []


if __name__ == "__main__":
    test_federal_rules_not_empty()
    test_georgia_rules_not_empty()
    test_murder_is_separately_punishable()
    test_manslaughter_merges_into_murder()
    test_georgia_murder_is_separately_punishable()
    test_georgia_voluntary_manslaughter_merges()
    test_analyze_merger_flags_lesser_included()
    test_analyze_merger_non_merging_charges_unaffected()
    test_analyze_merger_unknown_citation_defaults_to_punishable()
    test_analyze_merger_without_greater_offense()
    test_merger_warnings_returns_strings()
    test_merger_warnings_content()
    test_merger_warnings_empty_for_non_merging()
    test_merger_warnings_no_merger_field()
    print("All merger tests passed!")
