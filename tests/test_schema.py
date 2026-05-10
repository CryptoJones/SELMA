"""Tests for SELMA data schemas."""

import sys
sys.path.insert(0, ".")

from src.selma.schema import (
    Jurisdiction,
    Severity,
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


if __name__ == "__main__":
    test_statute_reference_federal()
    test_statute_reference_georgia()
    test_statute_reference_with_subsection()
    test_training_example_chat_format()
    test_training_example_to_dict()
    test_incident_analysis()
    print("All tests passed!")
