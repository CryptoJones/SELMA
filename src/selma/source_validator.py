"""
Validates fetch URLs against the SELMA trusted sources allowlist.

All data collection scripts must call validate_url() before fetching
any external resource. URLs that don't match a trusted source entry are
rejected, preventing malicious feeds from being ingested into training data.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Optional

import yaml

_DEFAULT_CONFIG = Path(__file__).parent.parent.parent / "configs" / "trusted_sources.yaml"


def load_sources(config_path: Path = _DEFAULT_CONFIG) -> list[dict]:
    """Load the trusted sources allowlist from YAML."""
    with open(config_path) as f:
        data = yaml.safe_load(f)
    return data.get("sources", [])


def validate_url(url: str, config_path: Path = _DEFAULT_CONFIG) -> dict:
    """Check that a URL matches a trusted source entry.

    Args:
        url: The URL about to be fetched.
        config_path: Path to trusted_sources.yaml (defaults to configs/).

    Returns:
        The matching source dict.

    Raises:
        ValueError: If the URL does not match any trusted source.
    """
    sources = load_sources(config_path)
    for source in sources:
        for pattern in source.get("url_patterns", []):
            if url.startswith(pattern):
                return source
    raise ValueError(
        f"Blocked: '{url}' does not match any entry in trusted_sources.yaml.\n"
        f"To add this source, run: python scripts/add_source.py"
    )


def get_source(source_id: str, config_path: Path = _DEFAULT_CONFIG) -> Optional[dict]:
    """Look up a source entry by its id field."""
    for source in load_sources(config_path):
        if source.get("id") == source_id:
            return source
    return None


def list_sources(
    jurisdiction: Optional[str] = None,
    source_type: Optional[str] = None,
    config_path: Path = _DEFAULT_CONFIG,
) -> list[dict]:
    """Return sources filtered by jurisdiction and/or type."""
    sources = load_sources(config_path)
    if jurisdiction:
        sources = [s for s in sources if s.get("jurisdiction") == jurisdiction]
    if source_type:
        sources = [s for s in sources if s.get("type") == source_type]
    return sources
