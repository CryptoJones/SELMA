"""
Sentencing lookup module for SELMA.

Loads pre-processed sentencing data (output of fetch_sentencing_guidelines.py)
and provides lookups for USSG guideline ranges and Georgia mandatory minimums.
Designed to fail gracefully when data files do not yet exist.
"""

import json
from pathlib import Path
from typing import Optional

from src.selma.schema import PotentialCharge, SentencingRange


class SentencingIndex:
    """Loads and queries sentencing data from pre-processed JSON files."""

    USSG_FILE = "ussg_table.json"
    GEORGIA_FILE = "georgia_minimums.json"

    def __init__(self, data_dir: Path = Path("data/processed")):
        self.data_dir = data_dir
        self._ussg: dict = {}       # {offense_level_str: {ch_str: [min, max|null]}}
        self._georgia: dict = {}    # {statute_section: {min_months, max_months, notes, ...}}

    def load(self) -> bool:
        """Load USSG table and Georgia minimums. Returns True if any data found."""
        found = False

        ussg_path = self.data_dir / self.USSG_FILE
        if ussg_path.exists():
            with ussg_path.open() as f:
                self._ussg = json.load(f)
            found = True

        georgia_path = self.data_dir / self.GEORGIA_FILE
        if georgia_path.exists():
            with georgia_path.open() as f:
                self._georgia = json.load(f)
            found = True

        return found

    def ussg_range(self, offense_level: int, criminal_history: str = "I") -> Optional[SentencingRange]:
        """Look up USSG guideline range. Returns None if table not loaded or level not found."""
        if not self._ussg:
            return None

        row = self._ussg.get(str(offense_level))
        if row is None:
            return None

        cell = row.get(criminal_history)
        if cell is None:
            return None

        min_months, max_months = cell[0], cell[1]  # max_months may be None (life)
        return SentencingRange(
            source="USSG 2023",
            offense_level=offense_level,
            criminal_history_category=criminal_history,
            min_months=min_months,
            max_months=max_months,
            notes="Life" if max_months is None else "",
        )

    def georgia_mandatory_minimum(self, statute_section: str) -> Optional[SentencingRange]:
        """Look up Georgia mandatory minimum for a statute section. Returns None if not found."""
        if not self._georgia:
            return None

        entry = self._georgia.get(statute_section)
        if entry is None:
            return None

        return SentencingRange(
            source="Georgia State",
            guideline_section=entry.get("guideline_section", statute_section),
            min_months=entry.get("min_months"),
            max_months=entry.get("max_months"),
            notes=entry.get("notes", ""),
        )

    def annotate_charge(self, charge: PotentialCharge) -> PotentialCharge:
        """Add sentencing info to a charge if available. Returns charge (modified in place)."""
        if charge.sentencing is not None:
            return charge

        # Try Georgia lookup first for Georgia statutes, then USSG
        from src.selma.schema import Jurisdiction
        if charge.statute.jurisdiction == Jurisdiction.GEORGIA:
            section = f"{charge.statute.title}-{charge.statute.section}"
            result = self.georgia_mandatory_minimum(section)
            if result is not None:
                charge.sentencing = result
                return charge

        # Fall back to USSG if an offense level is embedded in notes or elements
        # (without a known offense level there's nothing to look up)
        return charge
