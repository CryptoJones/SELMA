"""
CaseLawIndex — load and query CourtListener case law data for SELMA.

Case law JSON files are written by scripts/data_collection/fetch_caselaw.py.
"""

from __future__ import annotations

import json
from pathlib import Path

from src.selma.schema import CaseLawReference, PotentialCharge


class CaseLawIndex:
    """In-memory index of CaseLawReferences loaded from processed JSON files."""

    def __init__(self, data_dir: Path = Path("data/processed")):
        self._data_dir = data_dir
        # Maps statute_interpreted → list of CaseLawReference
        self._index: dict[str, list[CaseLawReference]] = {}

    def load(self) -> int:
        """Load all caselaw JSON files from data_dir. Returns count of cases loaded."""
        total = 0
        for path in self._data_dir.glob("caselaw_*.json"):
            try:
                with open(path) as f:
                    records = json.load(f)
                for rec in records:
                    case = CaseLawReference(
                        case_name=rec.get("case_name", ""),
                        citation=rec.get("citation", ""),
                        court=rec.get("court", ""),
                        year=rec.get("year", 0),
                        holding=rec.get("holding", ""),
                        statute_interpreted=rec.get("statute_interpreted", ""),
                        url=rec.get("url", ""),
                    )
                    key = case.statute_interpreted
                    if key not in self._index:
                        self._index[key] = []
                    self._index[key].append(case)
                    total += 1
            except Exception as e:
                print(f"Warning: failed to load {path}: {e}")
        return total

    def lookup(self, statute_citation: str, limit: int = 3) -> list[CaseLawReference]:
        """Return up to `limit` cases interpreting the given statute citation."""
        cases = self._index.get(statute_citation, [])
        return cases[:limit]

    def annotate_charge(self, charge: PotentialCharge) -> PotentialCharge:
        """Attach relevant case law to a charge. Returns charge (modified in place)."""
        citation = charge.statute.full_citation
        matches = self.lookup(citation)
        if matches:
            charge.case_law = list(matches)
        return charge
