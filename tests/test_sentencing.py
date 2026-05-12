"""Tests for the SentencingIndex module."""

import sys
sys.path.insert(0, ".")

from src.selma.schema import (
    ChargeCategory,
    Jurisdiction,
    OffenseElement,
    PotentialCharge,
    Severity,
    StatuteReference,
)
from src.selma.sentencing import SentencingIndex


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_SMALL_USSG = {
    "1":  {"I": [0, 6],   "II": [0, 6],   "III": [0, 6], "IV": [0, 6], "V": [0, 6], "VI": [0, 6]},
    "10": {"I": [6, 12],  "II": [8, 14],  "III": [10, 16]},
    "43": {"I": [360, None]},
}


def _index_with_ussg(table: dict = None) -> SentencingIndex:
    """Return a SentencingIndex pre-loaded with the given (or default small) USSG table."""
    idx = SentencingIndex()
    idx._ussg = table if table is not None else _SMALL_USSG
    return idx


def _make_charge(jurisdiction=Jurisdiction.FEDERAL, title="18", section="1111",
                 name="Murder", severity=Severity.FELONY,
                 elements=None) -> PotentialCharge:
    ref = StatuteReference(jurisdiction=jurisdiction, title=title, section=section, name=name)
    return PotentialCharge(
        statute=ref,
        severity=severity,
        elements=elements or [],
    )


# ---------------------------------------------------------------------------
# USSG range tests
# ---------------------------------------------------------------------------

def test_ussg_range_returns_correct_min_max():
    idx = _index_with_ussg()
    result = idx.ussg_range(10, "I")
    assert result is not None
    assert result.min_months == 6
    assert result.max_months == 12
    assert result.offense_level == 10
    assert result.criminal_history_category == "I"


def test_ussg_range_level_1_ch_ii():
    idx = _index_with_ussg()
    result = idx.ussg_range(1, "II")
    assert result is not None
    assert result.min_months == 0
    assert result.max_months == 6


def test_ussg_range_life_sentence_max_months_is_none():
    idx = _index_with_ussg()
    result = idx.ussg_range(43, "I")
    assert result is not None
    assert result.max_months is None
    assert result.notes == "Life"


def test_ussg_range_missing_offense_level_returns_none():
    idx = _index_with_ussg()
    result = idx.ussg_range(99, "I")
    assert result is None


def test_ussg_range_missing_ch_returns_none():
    idx = _index_with_ussg()
    # Level 43 only has CH I in our small table
    result = idx.ussg_range(43, "VI")
    assert result is None


def test_ussg_range_no_data_loaded_returns_none():
    idx = SentencingIndex()  # nothing loaded
    result = idx.ussg_range(10, "I")
    assert result is None


# ---------------------------------------------------------------------------
# Georgia mandatory minimum tests
# ---------------------------------------------------------------------------

def test_georgia_mandatory_minimum_found():
    idx = SentencingIndex()
    idx._georgia = {
        "16-5-1": {
            "guideline_section": "17-10-2",
            "min_months": 240,
            "max_months": None,
            "notes": "Murder — life or death",
        }
    }
    result = idx.georgia_mandatory_minimum("16-5-1")
    assert result is not None
    assert result.min_months == 240
    assert result.max_months is None
    assert "Murder" in result.notes


def test_georgia_mandatory_minimum_not_found_returns_none():
    idx = SentencingIndex()
    idx._georgia = {"16-5-1": {"min_months": 240}}
    result = idx.georgia_mandatory_minimum("16-99-99")
    assert result is None


def test_georgia_mandatory_minimum_no_data_returns_none():
    idx = SentencingIndex()
    result = idx.georgia_mandatory_minimum("16-5-1")
    assert result is None


# ---------------------------------------------------------------------------
# annotate_charge tests
# ---------------------------------------------------------------------------

def test_annotate_charge_adds_sentencing_for_georgia_statute():
    idx = SentencingIndex()
    idx._georgia = {
        "16-5-1": {
            "guideline_section": "17-10-2",
            "min_months": 240,
            "max_months": None,
            "notes": "Murder",
        }
    }
    charge = _make_charge(jurisdiction=Jurisdiction.GEORGIA, title="16", section="5-1")
    result = idx.annotate_charge(charge)
    assert result is charge  # modified in place
    assert result.sentencing is not None
    assert result.sentencing.min_months == 240


def test_annotate_charge_does_not_overwrite_existing_sentencing():
    from src.selma.schema import SentencingRange
    idx = SentencingIndex()
    idx._georgia = {
        "16-5-1": {"min_months": 240, "max_months": None, "notes": "Murder"}
    }
    existing = SentencingRange(source="Manual", min_months=120)
    charge = _make_charge(jurisdiction=Jurisdiction.GEORGIA, title="16", section="5-1")
    charge.sentencing = existing
    idx.annotate_charge(charge)
    assert charge.sentencing is existing  # unchanged


def test_annotate_charge_federal_no_ussg_level_leaves_sentencing_none():
    idx = _index_with_ussg()
    charge = _make_charge()  # federal, no offense level provided
    idx.annotate_charge(charge)
    assert charge.sentencing is None


def test_annotate_charge_returns_charge():
    idx = SentencingIndex()
    charge = _make_charge()
    returned = idx.annotate_charge(charge)
    assert returned is charge


# ---------------------------------------------------------------------------
# load() tests (no filesystem needed — just verify False when files absent)
# ---------------------------------------------------------------------------

def test_load_returns_false_when_files_absent(tmp_path):
    idx = SentencingIndex(data_dir=tmp_path)
    assert idx.load() is False


def test_load_returns_true_when_ussg_file_present(tmp_path):
    import json
    ussg_path = tmp_path / "ussg_table.json"
    ussg_path.write_text(json.dumps({"1": {"I": [0, 6]}}))
    idx = SentencingIndex(data_dir=tmp_path)
    assert idx.load() is True
    assert idx._ussg == {"1": {"I": [0, 6]}}


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import tempfile, pathlib

    test_ussg_range_returns_correct_min_max()
    test_ussg_range_level_1_ch_ii()
    test_ussg_range_life_sentence_max_months_is_none()
    test_ussg_range_missing_offense_level_returns_none()
    test_ussg_range_missing_ch_returns_none()
    test_ussg_range_no_data_loaded_returns_none()
    test_georgia_mandatory_minimum_found()
    test_georgia_mandatory_minimum_not_found_returns_none()
    test_georgia_mandatory_minimum_no_data_returns_none()
    test_annotate_charge_adds_sentencing_for_georgia_statute()
    test_annotate_charge_does_not_overwrite_existing_sentencing()
    test_annotate_charge_federal_no_ussg_level_leaves_sentencing_none()
    test_annotate_charge_returns_charge()

    with tempfile.TemporaryDirectory() as d:
        test_load_returns_false_when_files_absent(pathlib.Path(d))

    with tempfile.TemporaryDirectory() as d:
        test_load_returns_true_when_ussg_file_present(pathlib.Path(d))

    print("All sentencing tests passed!")
