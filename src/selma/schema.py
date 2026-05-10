"""
Data schemas for SELMA training data.

Defines the structure for incident descriptions, statute references,
charge classifications, and training examples.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Jurisdiction(Enum):
    """Legal jurisdiction."""
    FEDERAL = "federal"
    GEORGIA = "georgia"


class Severity(Enum):
    """Charge severity classification."""
    INFRACTION = "infraction"
    MISDEMEANOR = "misdemeanor"
    FELONY = "felony"


@dataclass
class StatuteReference:
    """Reference to a specific criminal statute."""
    jurisdiction: Jurisdiction
    title: str           # e.g., "18" for federal, "16" for Georgia
    section: str         # e.g., "1111" for 18 U.S.C. § 1111
    subsection: str = "" # e.g., "(a)(1)"
    name: str = ""       # e.g., "Murder"
    full_citation: str = ""  # e.g., "18 U.S.C. § 1111(a)"

    def __post_init__(self):
        if not self.full_citation:
            if self.jurisdiction == Jurisdiction.FEDERAL:
                sub = self.subsection if self.subsection else ""
                self.full_citation = f"{self.title} U.S.C. § {self.section}{sub}"
            elif self.jurisdiction == Jurisdiction.GEORGIA:
                sub = self.subsection if self.subsection else ""
                self.full_citation = f"O.C.G.A. § {self.title}-{self.section}{sub}"


@dataclass
class OffenseElement:
    """An element that must be proven for a criminal offense."""
    description: str
    element_type: str = "essential"  # essential, circumstantial, jurisdictional
    met_by_facts: bool = False
    supporting_facts: str = ""


@dataclass
class PotentialCharge:
    """A potential criminal charge identified from an incident."""
    statute: StatuteReference
    severity: Severity
    degree: str = ""                    # e.g., "first degree", "aggravated"
    elements: list[OffenseElement] = field(default_factory=list)
    confidence: float = 0.0            # 0.0 to 1.0
    reasoning: str = ""
    lesser_included: list[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class IncidentAnalysis:
    """Complete analysis of an incident for potential criminal violations."""
    incident_description: str
    potential_charges: list[PotentialCharge] = field(default_factory=list)
    jurisdictional_notes: str = ""
    additional_info_needed: list[str] = field(default_factory=list)
    summary: str = ""


@dataclass
class TrainingExample:
    """A single training example for SELMA fine-tuning."""
    instruction: str           # System prompt / task description
    input_text: str            # Incident description
    output_text: str           # Expected analysis
    jurisdiction: Optional[Jurisdiction] = None
    statutes_referenced: list[str] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)

    def to_chat_format(self) -> list[dict]:
        """Convert to chat message format for training."""
        messages = [
            {"role": "system", "content": self.instruction},
            {"role": "user", "content": self.input_text},
            {"role": "assistant", "content": self.output_text},
        ]
        return messages

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "messages": self.to_chat_format(),
            "jurisdiction": self.jurisdiction.value if self.jurisdiction else None,
            "statutes_referenced": self.statutes_referenced,
            "metadata": self.metadata,
        }
