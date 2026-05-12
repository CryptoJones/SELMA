"""Tests for the trusted-source allowlist validator."""

import sys
import tempfile
from pathlib import Path
import yaml

sys.path.insert(0, ".")

from src.selma.source_validator import validate_url, load_sources, list_sources, get_source


def _write_config(sources: list) -> Path:
    """Write a temporary trusted_sources.yaml and return its path."""
    tmp = tempfile.NamedTemporaryFile(suffix=".yaml", delete=False, mode="w")
    yaml.dump({"sources": sources}, tmp)
    tmp.flush()
    return Path(tmp.name)


SAMPLE_SOURCES = [
    {
        "id": "usc_title18",
        "name": "U.S. Code Title 18",
        "jurisdiction": "federal",
        "type": "statute",
        "url_patterns": ["https://uscode.house.gov/download/"],
        "format": "uslm_xml",
        "license": "public_domain",
    },
    {
        "id": "georgia_onecle",
        "name": "Georgia O.C.G.A. Title 16",
        "jurisdiction": "georgia",
        "type": "statute",
        "url_patterns": ["https://law.onecle.com/georgia/"],
        "format": "html",
        "license": "fair_use",
    },
]


def test_validate_url_passes_for_trusted_source():
    cfg = _write_config(SAMPLE_SOURCES)
    source = validate_url("https://uscode.house.gov/download/releasepoints/xml_usc18.zip", cfg)
    assert source["id"] == "usc_title18"


def test_validate_url_blocks_untrusted_source():
    cfg = _write_config(SAMPLE_SOURCES)
    try:
        validate_url("https://malicious-site.example.com/fake_statutes.zip", cfg)
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Blocked" in str(e)
        assert "trusted_sources.yaml" in str(e)


def test_validate_url_blocks_partial_match():
    """A URL that contains a trusted prefix as a substring but doesn't start with it is rejected."""
    cfg = _write_config(SAMPLE_SOURCES)
    try:
        validate_url("https://evil.com/redirect?url=https://uscode.house.gov/download/evil.zip", cfg)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


def test_validate_url_matches_georgia_source():
    cfg = _write_config(SAMPLE_SOURCES)
    source = validate_url("https://law.onecle.com/georgia/title-16/chapter-5/index.html", cfg)
    assert source["id"] == "georgia_onecle"


def test_get_source_by_id():
    cfg = _write_config(SAMPLE_SOURCES)
    source = get_source("usc_title18", cfg)
    assert source is not None
    assert source["name"] == "U.S. Code Title 18"


def test_get_source_missing_returns_none():
    cfg = _write_config(SAMPLE_SOURCES)
    assert get_source("nonexistent_id", cfg) is None


def test_list_sources_by_jurisdiction():
    cfg = _write_config(SAMPLE_SOURCES)
    georgia = list_sources(jurisdiction="georgia", config_path=cfg)
    assert len(georgia) == 1
    assert georgia[0]["id"] == "georgia_onecle"


def test_list_sources_by_type():
    cfg = _write_config(SAMPLE_SOURCES)
    statutes = list_sources(source_type="statute", config_path=cfg)
    assert len(statutes) == 2


if __name__ == "__main__":
    test_validate_url_passes_for_trusted_source()
    test_validate_url_blocks_untrusted_source()
    test_validate_url_blocks_partial_match()
    test_validate_url_matches_georgia_source()
    test_get_source_by_id()
    test_get_source_missing_returns_none()
    test_list_sources_by_jurisdiction()
    test_list_sources_by_type()
    print("All source validator tests passed!")
