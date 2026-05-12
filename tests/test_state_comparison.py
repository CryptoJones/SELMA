"""Tests for src/selma/state_comparison.py."""

import sys

sys.path.insert(0, ".")

from src.selma.state_comparison import (
    STATUTE_CROSSREF,
    compare_jurisdictions,
    get_crossref,
)
from src.selma.schema import (
    ChargeCategory,
    Jurisdiction,
    PotentialCharge,
    Severity,
    StatuteReference,
)


def _make_charge(full_citation: str, name: str = "", severity: Severity = Severity.FELONY) -> PotentialCharge:
    statute = StatuteReference(
        jurisdiction=Jurisdiction.FEDERAL,
        title="",
        section="",
        name=name,
        full_citation=full_citation,
    )
    return PotentialCharge(statute=statute, severity=severity)


# ---------------------------------------------------------------------------
# get_crossref
# ---------------------------------------------------------------------------

def test_crossref_murder_to_georgia():
    result = get_crossref("18 U.S.C. § 1111", "georgia")
    assert result == "O.C.G.A. § 16-5-1"


def test_crossref_murder_to_california():
    result = get_crossref("18 U.S.C. § 1111", "california")
    assert result == "Cal. Penal Code § 187"


def test_crossref_trafficking_to_georgia():
    result = get_crossref("21 U.S.C. § 841(a)(1)", "georgia")
    assert result == "O.C.G.A. § 16-13-31"


def test_crossref_unknown_federal_returns_none():
    result = get_crossref("18 U.S.C. § 9999", "georgia")
    assert result is None


def test_crossref_unknown_jurisdiction_returns_none():
    result = get_crossref("18 U.S.C. § 1111", "mars")
    assert result is None


def test_crossref_table_has_entries():
    assert len(STATUTE_CROSSREF) >= 10


# ---------------------------------------------------------------------------
# compare_jurisdictions
# ---------------------------------------------------------------------------

def test_compare_jurisdictions_returns_list():
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    results = compare_jurisdictions("Suspect shot victim.", charges, [Jurisdiction.GEORGIA])
    assert isinstance(results, list)
    assert len(results) == 1


def test_compare_jurisdictions_correct_jurisdiction():
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    results = compare_jurisdictions("desc", charges, [Jurisdiction.GEORGIA])
    assert results[0].jurisdiction == Jurisdiction.GEORGIA


def test_compare_jurisdictions_maps_statute():
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    results = compare_jurisdictions("desc", charges, [Jurisdiction.GEORGIA])
    mapped = results[0].charges
    assert len(mapped) == 1
    assert mapped[0].statute.full_citation == "O.C.G.A. § 16-5-1"


def test_compare_jurisdictions_key_differences_populated():
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    results = compare_jurisdictions("desc", charges, [Jurisdiction.GEORGIA])
    assert results[0].key_differences != ""


def test_compare_jurisdictions_unknown_statute_excluded():
    """Unknown federal statute produces empty charge list, not an error."""
    charges = [_make_charge("18 U.S.C. § 9999", "Unknown")]
    results = compare_jurisdictions("desc", charges, [Jurisdiction.GEORGIA])
    assert results[0].charges == []
    assert "No cross-reference" in results[0].notes


def test_compare_jurisdictions_unknown_jurisdiction_empty_charges():
    """A Jurisdiction value not in the crossref table produces empty charge mapping."""
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    # FEDERAL is not a valid compare_to target in the crossref, simulating unknown
    results = compare_jurisdictions("desc", charges, [Jurisdiction.FEDERAL])
    # federal key isn't in crossref dict sub-entries, so charges should be empty
    assert isinstance(results, list)
    assert len(results) == 1
    assert results[0].charges == []


def test_compare_jurisdictions_multiple_jurisdictions():
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    results = compare_jurisdictions("desc", charges, [Jurisdiction.GEORGIA, Jurisdiction.FEDERAL])
    assert len(results) == 2


def test_compare_jurisdictions_notes_field():
    charges = [_make_charge("18 U.S.C. § 1111", "Murder")]
    results = compare_jurisdictions("desc", charges, [Jurisdiction.GEORGIA])
    assert results[0].notes != ""


if __name__ == "__main__":
    test_crossref_murder_to_georgia()
    test_crossref_murder_to_california()
    test_crossref_trafficking_to_georgia()
    test_crossref_unknown_federal_returns_none()
    test_crossref_unknown_jurisdiction_returns_none()
    test_crossref_table_has_entries()
    test_compare_jurisdictions_returns_list()
    test_compare_jurisdictions_correct_jurisdiction()
    test_compare_jurisdictions_maps_statute()
    test_compare_jurisdictions_key_differences_populated()
    test_compare_jurisdictions_unknown_statute_excluded()
    test_compare_jurisdictions_unknown_jurisdiction_empty_charges()
    test_compare_jurisdictions_multiple_jurisdictions()
    test_compare_jurisdictions_notes_field()
    print("All state comparison tests passed!")
