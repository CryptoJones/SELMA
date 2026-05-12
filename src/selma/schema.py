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
    """Criminal charge severity classification. Not applicable to civil matters."""
    INFRACTION = "infraction"
    MISDEMEANOR = "misdemeanor"
    FELONY = "felony"


class ChargeCategory(Enum):
    """Whether a charge is criminal or civil.

    Criminal charges are always the primary focus. Civil statutes are included
    only to flag parallel liability — they are NOT charges an officer can bring.
    """
    CRIMINAL = "criminal"
    CIVIL = "civil"


@dataclass
class StatuteReference:
    """Reference to a specific statute (criminal or civil)."""
    jurisdiction: Jurisdiction
    title: str           # e.g., "18" for 18 U.S.C., "42" for 42 U.S.C., "16" for O.C.G.A. Title 16
    section: str         # e.g., "1111", "1983"
    subsection: str = "" # e.g., "(a)(1)"
    name: str = ""       # e.g., "Murder", "Civil Rights — Color of Law"
    full_citation: str = ""

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
class SentencingRange:
    """Guideline sentencing range for a charge."""
    source: str                          # e.g., "USSG 2023", "Georgia State"
    guideline_section: str = ""          # e.g., "2A1.1" (USSG) or "17-10-2" (GA)
    offense_level: Optional[int] = None  # USSG offense level (1–43)
    criminal_history_category: str = "I" # I–VI for USSG
    min_months: Optional[int] = None
    max_months: Optional[int] = None
    notes: str = ""                      # e.g., "life if CH III+", mandatory minimums


@dataclass
class CaseLawReference:
    """A court decision relevant to a specific statute."""
    case_name: str                  # e.g., "Miranda v. Arizona"
    citation: str                   # e.g., "384 U.S. 436"
    court: str                      # e.g., "U.S. Supreme Court", "11th Cir."
    year: int
    holding: str                    # One-sentence summary of the holding
    statute_interpreted: str = ""   # Statute citation this case interprets
    url: str = ""                   # CourtListener or official source URL


@dataclass
class MergerAnalysis:
    """Whether this charge merges with others or is separately punishable."""
    separately_punishable: bool = True
    merges_with: list[str] = field(default_factory=list)  # statute citations
    lesser_included_of: str = ""    # citation of the greater offense, if any
    double_jeopardy_bar: bool = False
    notes: str = ""


@dataclass
class PotentialCharge:
    """A potential charge (criminal) or civil parallel identified from an incident."""
    statute: StatuteReference
    category: ChargeCategory = ChargeCategory.CRIMINAL
    severity: Optional[Severity] = None  # None for civil matters
    degree: str = ""                     # e.g., "first degree", "aggravated"
    elements: list[OffenseElement] = field(default_factory=list)
    confidence: float = 0.0
    reasoning: str = ""
    lesser_included: list[str] = field(default_factory=list)
    notes: str = ""
    sentencing: Optional[SentencingRange] = None
    case_law: list[CaseLawReference] = field(default_factory=list)
    merger: Optional[MergerAnalysis] = None


@dataclass
class StateComparison:
    """How the same incident would be charged in a different jurisdiction."""
    jurisdiction: Jurisdiction
    charges: list[PotentialCharge] = field(default_factory=list)
    key_differences: str = ""
    notes: str = ""


@dataclass
class IncidentAnalysis:
    """Complete analysis of an incident for potential criminal violations and civil parallels."""
    incident_description: str
    # Criminal charges — primary focus; what the officer may pursue
    potential_charges: list[PotentialCharge] = field(default_factory=list)
    # Civil parallels — secondary; flagged for awareness, NOT actionable by the officer
    civil_parallels: list[PotentialCharge] = field(default_factory=list)
    # How this incident would be charged under other jurisdictions' law
    state_comparisons: list[StateComparison] = field(default_factory=list)
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
