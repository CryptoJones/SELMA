"""
Statute index and lookup for SELMA.

Provides efficient search and retrieval of criminal statutes
from the processed statute database.
"""

import json
import os
from pathlib import Path
from typing import Optional


class StatuteIndex:
    """Index of criminal statutes for lookup and search."""

    def __init__(self, data_dir: str = "data/processed"):
        self.data_dir = Path(data_dir)
        self.federal_statutes: dict = {}
        self.georgia_statutes: dict = {}
        self._loaded = False

    def load(self):
        """Load statute data from processed files."""
        federal_path = self.data_dir / "federal_statutes.json"
        georgia_path = self.data_dir / "georgia_statutes.json"

        if federal_path.exists():
            with open(federal_path) as f:
                self.federal_statutes = json.load(f)

        if georgia_path.exists():
            with open(georgia_path) as f:
                self.georgia_statutes = json.load(f)

        self._loaded = True

    def lookup(self, jurisdiction: str, section: str) -> Optional[dict]:
        """Look up a specific statute by jurisdiction and section number."""
        if not self._loaded:
            self.load()

        if jurisdiction.lower() == "federal":
            return self.federal_statutes.get(section)
        elif jurisdiction.lower() == "georgia":
            return self.georgia_statutes.get(section)
        return None

    def search(self, query: str, jurisdiction: Optional[str] = None) -> list[dict]:
        """Search statutes by keyword in title or text."""
        if not self._loaded:
            self.load()

        results = []
        query_lower = query.lower()

        sources = []
        if jurisdiction is None or jurisdiction.lower() == "federal":
            sources.append(("federal", self.federal_statutes))
        if jurisdiction is None or jurisdiction.lower() == "georgia":
            sources.append(("georgia", self.georgia_statutes))

        for jur, statutes in sources:
            for section, data in statutes.items():
                title = data.get("title", "").lower()
                text = data.get("text", "").lower()
                if query_lower in title or query_lower in text:
                    results.append({
                        "jurisdiction": jur,
                        "section": section,
                        **data,
                    })

        return results

    def get_all_sections(self, jurisdiction: str) -> list[str]:
        """Get all section numbers for a jurisdiction."""
        if not self._loaded:
            self.load()

        if jurisdiction.lower() == "federal":
            return sorted(self.federal_statutes.keys())
        elif jurisdiction.lower() == "georgia":
            return sorted(self.georgia_statutes.keys())
        return []

    def get_elements(self, jurisdiction: str, section: str) -> list[str]:
        """Get the elements of an offense for a specific statute."""
        statute = self.lookup(jurisdiction, section)
        if statute:
            return statute.get("elements", [])
        return []

    def stats(self) -> dict:
        """Return statistics about the loaded index."""
        if not self._loaded:
            self.load()
        return {
            "federal_count": len(self.federal_statutes),
            "georgia_count": len(self.georgia_statutes),
            "total": len(self.federal_statutes) + len(self.georgia_statutes),
        }
