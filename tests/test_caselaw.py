"""Tests for src/selma/caselaw.py and scripts/data_collection/fetch_caselaw.py."""

import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, ".")

from src.selma.caselaw import CaseLawIndex
from src.selma.schema import (
    CaseLawReference,
    ChargeCategory,
    Jurisdiction,
    PotentialCharge,
    StatuteReference,
)
from scripts.data_collection.fetch_caselaw import parse_result, statute_to_slug


# ---------------------------------------------------------------------------
# fetch_caselaw helpers
# ---------------------------------------------------------------------------

def test_statute_to_slug():
    assert statute_to_slug("18 U.S.C. § 1111") == "18_u_s_c_1111"


def test_statute_to_slug_ocga():
    slug = statute_to_slug("O.C.G.A. § 16-5-1")
    assert " " not in slug
    assert "§" not in slug


def test_parse_result_basic():
    raw = {
        "case_name": "United States v. Smith",
        "citation": ["12 F.3d 345"],
        "court": "9th Cir.",
        "date_filed": "2001-06-15",
        "snippet": "Murder requires malice aforethought.",
        "absolute_url": "/opinion/12345/",
    }
    ref = parse_result(raw, "18 U.S.C. § 1111")
    assert ref.case_name == "United States v. Smith"
    assert ref.citation == "12 F.3d 345"
    assert ref.court == "9th Cir."
    assert ref.year == 2001
    assert ref.holding == "Murder requires malice aforethought."
    assert ref.statute_interpreted == "18 U.S.C. § 1111"
    assert ref.url.startswith("https://www.courtlistener.com")


def test_parse_result_missing_fields():
    raw = {}
    ref = parse_result(raw, "18 U.S.C. § 1112")
    assert isinstance(ref, CaseLawReference)
    assert ref.statute_interpreted == "18 U.S.C. § 1112"
    assert ref.year == 0


def test_parse_result_absolute_url_already_full():
    raw = {
        "case_name": "Doe v. Roe",
        "citation": [],
        "court": "SDNY",
        "date_filed": "2010-01-01",
        "snippet": "",
        "absolute_url": "https://www.courtlistener.com/opinion/999/",
    }
    ref = parse_result(raw, "18 U.S.C. § 1111")
    assert ref.url == "https://www.courtlistener.com/opinion/999/"


# ---------------------------------------------------------------------------
# CaseLawIndex
# ---------------------------------------------------------------------------

def _write_caselaw_file(data_dir: Path, statute: str, records: list[dict]):
    """Helper to write a fake caselaw JSON file."""
    import re
    slug = re.sub(r"[\s§\.\(\)]+", "_", statute)
    slug = re.sub(r"_+", "_", slug).strip("_").lower()
    path = data_dir / f"caselaw_{slug}.json"
    with open(path, "w") as f:
        json.dump(records, f)


SAMPLE_RECORDS = [
    {
        "case_name": "US v. Alpha",
        "citation": "100 F.3d 1",
        "court": "5th Cir.",
        "year": 1999,
        "holding": "Requires malice.",
        "statute_interpreted": "18 U.S.C. § 1111",
        "url": "https://www.courtlistener.com/opinion/1/",
    },
    {
        "case_name": "US v. Beta",
        "citation": "101 F.3d 2",
        "court": "9th Cir.",
        "year": 2000,
        "holding": "Premeditation element.",
        "statute_interpreted": "18 U.S.C. § 1111",
        "url": "https://www.courtlistener.com/opinion/2/",
    },
]


def test_load_returns_count():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        _write_caselaw_file(data_dir, "18 U.S.C. § 1111", SAMPLE_RECORDS)
        index = CaseLawIndex(data_dir=data_dir)
        count = index.load()
        assert count == 2


def test_lookup_by_citation():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        _write_caselaw_file(data_dir, "18 U.S.C. § 1111", SAMPLE_RECORDS)
        index = CaseLawIndex(data_dir=data_dir)
        index.load()
        results = index.lookup("18 U.S.C. § 1111")
        assert len(results) == 2
        assert results[0].case_name == "US v. Alpha"


def test_lookup_respects_limit():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        _write_caselaw_file(data_dir, "18 U.S.C. § 1111", SAMPLE_RECORDS)
        index = CaseLawIndex(data_dir=data_dir)
        index.load()
        results = index.lookup("18 U.S.C. § 1111", limit=1)
        assert len(results) == 1


def test_lookup_unknown_statute_returns_empty():
    with tempfile.TemporaryDirectory() as tmpdir:
        index = CaseLawIndex(data_dir=Path(tmpdir))
        index.load()
        assert index.lookup("18 U.S.C. § 9999") == []


def test_annotate_charge():
    with tempfile.TemporaryDirectory() as tmpdir:
        data_dir = Path(tmpdir)
        _write_caselaw_file(data_dir, "18 U.S.C. § 1111", SAMPLE_RECORDS)
        index = CaseLawIndex(data_dir=data_dir)
        index.load()

        statute = StatuteReference(
            jurisdiction=Jurisdiction.FEDERAL,
            title="18",
            section="1111",
            name="Murder",
        )
        charge = PotentialCharge(statute=statute)
        result = index.annotate_charge(charge)
        assert result is charge  # modified in place
        assert len(charge.case_law) > 0
        assert charge.case_law[0].case_name == "US v. Alpha"


def test_annotate_charge_no_match():
    with tempfile.TemporaryDirectory() as tmpdir:
        index = CaseLawIndex(data_dir=Path(tmpdir))
        index.load()

        statute = StatuteReference(
            jurisdiction=Jurisdiction.FEDERAL,
            title="18",
            section="9999",
            name="Unknown",
        )
        charge = PotentialCharge(statute=statute)
        result = index.annotate_charge(charge)
        assert result is charge
        assert charge.case_law == []


if __name__ == "__main__":
    test_statute_to_slug()
    test_statute_to_slug_ocga()
    test_parse_result_basic()
    test_parse_result_missing_fields()
    test_parse_result_absolute_url_already_full()
    test_load_returns_count()
    test_lookup_by_citation()
    test_lookup_respects_limit()
    test_lookup_unknown_statute_returns_empty()
    test_annotate_charge()
    test_annotate_charge_no_match()
    print("All caselaw tests passed!")
