"""Tests for SELMA data schemas."""

import sys
sys.path.insert(0, ".")

from src.selma.schema import (
    Jurisdiction,
    Severity,
    ChargeCategory,
    StatuteReference,
    OffenseElement,
    PotentialCharge,
    IncidentAnalysis,
    TrainingExample,
)


def test_statute_reference_federal():
    ref = StatuteReference(
        jurisdiction=Jurisdiction.FEDERAL,
        title="18",
        section="1111",
        name="Murder",
    )
    assert ref.full_citation == "18 U.S.C. § 1111"


def test_statute_reference_georgia():
    ref = StatuteReference(
        jurisdiction=Jurisdiction.GEORGIA,
        title="16",
        section="5-1",
        name="Murder",
    )
    assert ref.full_citation == "O.C.G.A. § 16-5-1"


def test_statute_reference_with_subsection():
    ref = StatuteReference(
        jurisdiction=Jurisdiction.FEDERAL,
        title="18",
        section="1111",
        subsection="(a)",
        name="Murder - First Degree",
    )
    assert ref.full_citation == "18 U.S.C. § 1111(a)"


def test_training_example_chat_format():
    example = TrainingExample(
        instruction="Analyze the incident.",
        input_text="A person stole a car.",
        output_text="Potential violation of theft statutes.",
        jurisdiction=Jurisdiction.FEDERAL,
        statutes_referenced=["18 U.S.C. § 2312"],
    )
    messages = example.to_chat_format()
    assert len(messages) == 3
    assert messages[0]["role"] == "system"
    assert messages[1]["role"] == "user"
    assert messages[2]["role"] == "assistant"


def test_training_example_to_dict():
    example = TrainingExample(
        instruction="Analyze.",
        input_text="Incident.",
        output_text="Analysis.",
        jurisdiction=Jurisdiction.GEORGIA,
    )
    d = example.to_dict()
    assert "messages" in d
    assert d["jurisdiction"] == "georgia"


def test_incident_analysis():
    analysis = IncidentAnalysis(
        incident_description="Test incident",
        potential_charges=[],
        additional_info_needed=["Witness statements"],
    )
    assert analysis.incident_description == "Test incident"
    assert len(analysis.additional_info_needed) == 1


def test_criminal_charge_defaults_to_criminal_category():
    ref = StatuteReference(jurisdiction=Jurisdiction.FEDERAL, title="18", section="1111", name="Murder")
    charge = PotentialCharge(statute=ref, severity=Severity.FELONY)
    assert charge.category == ChargeCategory.CRIMINAL


def test_civil_charge_has_no_severity():
    ref = StatuteReference(jurisdiction=Jurisdiction.FEDERAL, title="42", section="1983",
                           name="Civil Rights — Color of Law")
    charge = PotentialCharge(statute=ref, category=ChargeCategory.CIVIL)
    assert charge.severity is None
    assert charge.category == ChargeCategory.CIVIL


def test_civil_statute_citation_format():
    ref = StatuteReference(jurisdiction=Jurisdiction.FEDERAL, title="42", section="1983")
    assert ref.full_citation == "42 U.S.C. § 1983"


def test_incident_analysis_separates_criminal_and_civil():
    criminal_ref = StatuteReference(jurisdiction=Jurisdiction.FEDERAL, title="18", section="2")
    civil_ref = StatuteReference(jurisdiction=Jurisdiction.FEDERAL, title="42", section="1983")

    criminal = PotentialCharge(statute=criminal_ref, severity=Severity.FELONY)
    civil = PotentialCharge(statute=civil_ref, category=ChargeCategory.CIVIL)

    analysis = IncidentAnalysis(
        incident_description="Test incident",
        potential_charges=[criminal],
        civil_parallels=[civil],
    )
    assert len(analysis.potential_charges) == 1
    assert len(analysis.civil_parallels) == 1
    assert analysis.potential_charges[0].category == ChargeCategory.CRIMINAL
    assert analysis.civil_parallels[0].category == ChargeCategory.CIVIL


if __name__ == "__main__":
    test_statute_reference_federal()
    test_statute_reference_georgia()
    test_statute_reference_with_subsection()
    test_training_example_chat_format()
    test_training_example_to_dict()
    test_incident_analysis()
    test_criminal_charge_defaults_to_criminal_category()
    test_civil_charge_has_no_severity()
    test_civil_statute_citation_format()
    test_incident_analysis_separates_criminal_and_civil()
    print("All tests passed!")
