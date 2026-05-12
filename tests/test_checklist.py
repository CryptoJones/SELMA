"""Tests for the checklist generator module."""

import sys
sys.path.insert(0, ".")

from src.selma.schema import (
    ChargeCategory,
    IncidentAnalysis,
    Jurisdiction,
    OffenseElement,
    PotentialCharge,
    Severity,
    SentencingRange,
    StatuteReference,
)
from src.selma.checklist import checklist_to_dict, generate_checklist, generate_full_checklist


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _murder_charge() -> PotentialCharge:
    ref = StatuteReference(
        jurisdiction=Jurisdiction.FEDERAL,
        title="18",
        section="1111",
        name="Murder",
    )
    elements = [
        OffenseElement(
            description="Unlawful killing of a human being",
            element_type="essential",
            met_by_facts=False,
            supporting_facts="",
        ),
        OffenseElement(
            description="With malice aforethought",
            element_type="essential",
            met_by_facts=True,
            supporting_facts="Suspect stated intent prior to incident",
        ),
    ]
    sentencing = SentencingRange(
        source="USSG 2023",
        guideline_section="2A1.1",
        offense_level=43,
        criminal_history_category="I",
        min_months=360,
        max_months=None,
        notes="Life",
    )
    return PotentialCharge(
        statute=ref,
        category=ChargeCategory.CRIMINAL,
        severity=Severity.FELONY,
        degree="first degree",
        elements=elements,
        sentencing=sentencing,
        notes="See also 18 U.S.C. § 1112 for manslaughter",
    )


def _civil_charge() -> PotentialCharge:
    ref = StatuteReference(
        jurisdiction=Jurisdiction.FEDERAL,
        title="42",
        section="1983",
        name="Civil Rights — Color of Law",
    )
    return PotentialCharge(
        statute=ref,
        category=ChargeCategory.CIVIL,
        severity=None,
    )


def _assault_charge() -> PotentialCharge:
    ref = StatuteReference(
        jurisdiction=Jurisdiction.FEDERAL,
        title="18",
        section="113",
        name="Assault",
    )
    elements = [
        OffenseElement(
            description="Intentional threat or attempt to cause bodily harm",
            element_type="essential",
            met_by_facts=True,
            supporting_facts="Victim reported threatening behavior",
        ),
    ]
    return PotentialCharge(
        statute=ref,
        category=ChargeCategory.CRIMINAL,
        severity=Severity.MISDEMEANOR,
        elements=elements,
    )


# ---------------------------------------------------------------------------
# generate_checklist tests
# ---------------------------------------------------------------------------

def test_generate_checklist_contains_statute_citation():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "18 U.S.C. § 1111" in output


def test_generate_checklist_contains_statute_name():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "Murder" in output


def test_generate_checklist_met_element_shows_x():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "[x]" in output
    assert "With malice aforethought" in output


def test_generate_checklist_unmet_element_shows_empty_box():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "[ ]" in output
    assert "Unlawful killing of a human being" in output


def test_generate_checklist_met_status_label():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "Status: MET" in output
    assert "Status: NOT MET" in output


def test_generate_checklist_supporting_facts_shown():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "Suspect stated intent prior to incident" in output


def test_generate_checklist_missing_facts_shows_dash():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "Supporting facts: —" in output


def test_generate_checklist_sentencing_block_present():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "SENTENCING" in output
    assert "2A1.1" in output


def test_generate_checklist_notes_included():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "NOTES:" in output
    assert "1112" in output


def test_generate_checklist_no_elements_no_crash():
    ref = StatuteReference(jurisdiction=Jurisdiction.FEDERAL, title="18", section="2", name="Aiding")
    charge = PotentialCharge(statute=ref, severity=Severity.FELONY)
    output = generate_checklist(charge)
    assert "18 U.S.C. § 2" in output


def test_generate_checklist_severity_in_header():
    charge = _murder_charge()
    output = generate_checklist(charge)
    assert "FELONY" in output


# ---------------------------------------------------------------------------
# generate_full_checklist tests
# ---------------------------------------------------------------------------

def test_generate_full_checklist_includes_all_criminal_charges():
    analysis = IncidentAnalysis(
        incident_description="Test incident",
        potential_charges=[_murder_charge(), _assault_charge()],
        civil_parallels=[_civil_charge()],
    )
    output = generate_full_checklist(analysis)
    assert "18 U.S.C. § 1111" in output
    assert "18 U.S.C. § 113" in output


def test_generate_full_checklist_civil_excluded_from_main_body():
    analysis = IncidentAnalysis(
        incident_description="Test incident",
        potential_charges=[_murder_charge()],
        civil_parallels=[_civil_charge()],
    )
    output = generate_full_checklist(analysis)
    # Civil charge should appear only in the civil section, not as a full checklist block
    assert "CIVIL PARALLELS" in output
    # 42 U.S.C. § 1983 should appear only in the civil section note — confirm it's there
    assert "42 U.S.C. § 1983" in output
    # Should NOT have a CHARGE: line for the civil statute
    lines = output.splitlines()
    charge_lines = [l for l in lines if l.startswith("CHARGE:")]
    assert all("1983" not in l for l in charge_lines)


def test_generate_full_checklist_no_civil_parallels_no_civil_section():
    analysis = IncidentAnalysis(
        incident_description="Test incident",
        potential_charges=[_murder_charge()],
        civil_parallels=[],
    )
    output = generate_full_checklist(analysis)
    assert "CIVIL PARALLELS" not in output


def test_generate_full_checklist_only_criminal_charges_shown_as_checklists():
    analysis = IncidentAnalysis(
        incident_description="Test incident",
        potential_charges=[_murder_charge()],
        civil_parallels=[_civil_charge()],
    )
    output = generate_full_checklist(analysis)
    # Only murder has a full ELEMENTS CHECKLIST block
    assert output.count("ELEMENTS CHECKLIST") == 1


def test_generate_full_checklist_empty_analysis_no_crash():
    analysis = IncidentAnalysis(incident_description="No charges")
    output = generate_full_checklist(analysis)
    assert isinstance(output, str)


# ---------------------------------------------------------------------------
# checklist_to_dict tests
# ---------------------------------------------------------------------------

def test_checklist_to_dict_statute_field():
    charge = _murder_charge()
    d = checklist_to_dict(charge)
    assert d["statute"] == "18 U.S.C. § 1111"


def test_checklist_to_dict_elements_structure():
    charge = _murder_charge()
    d = checklist_to_dict(charge)
    assert len(d["elements"]) == 2
    assert d["elements"][0]["met"] is False
    assert d["elements"][1]["met"] is True
    assert d["elements"][1]["supporting_facts"] == "Suspect stated intent prior to incident"


def test_checklist_to_dict_sentencing_block():
    charge = _murder_charge()
    d = checklist_to_dict(charge)
    assert d["sentencing"] is not None
    assert d["sentencing"]["max_months"] is None
    assert d["sentencing"]["offense_level"] == 43


def test_checklist_to_dict_no_sentencing_is_none():
    charge = _assault_charge()
    d = checklist_to_dict(charge)
    assert d["sentencing"] is None


def test_checklist_to_dict_category_field():
    charge = _murder_charge()
    d = checklist_to_dict(charge)
    assert d["category"] == "criminal"


def test_checklist_to_dict_severity_field():
    charge = _murder_charge()
    d = checklist_to_dict(charge)
    assert d["severity"] == "felony"


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    test_generate_checklist_contains_statute_citation()
    test_generate_checklist_contains_statute_name()
    test_generate_checklist_met_element_shows_x()
    test_generate_checklist_unmet_element_shows_empty_box()
    test_generate_checklist_met_status_label()
    test_generate_checklist_supporting_facts_shown()
    test_generate_checklist_missing_facts_shows_dash()
    test_generate_checklist_sentencing_block_present()
    test_generate_checklist_notes_included()
    test_generate_checklist_no_elements_no_crash()
    test_generate_checklist_severity_in_header()
    test_generate_full_checklist_includes_all_criminal_charges()
    test_generate_full_checklist_civil_excluded_from_main_body()
    test_generate_full_checklist_no_civil_parallels_no_civil_section()
    test_generate_full_checklist_only_criminal_charges_shown_as_checklists()
    test_generate_full_checklist_empty_analysis_no_crash()
    test_checklist_to_dict_statute_field()
    test_checklist_to_dict_elements_structure()
    test_checklist_to_dict_sentencing_block()
    test_checklist_to_dict_no_sentencing_is_none()
    test_checklist_to_dict_category_field()
    test_checklist_to_dict_severity_field()
    print("All checklist tests passed!")
