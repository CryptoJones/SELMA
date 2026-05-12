#!/usr/bin/env python3
"""
Fetch court opinions from CourtListener that cite specific statutes.

Usage:
    python scripts/data_collection/fetch_caselaw.py --statute "18 U.S.C. § 1111" --limit 20
    python scripts/data_collection/fetch_caselaw.py --statute "O.C.G.A. § 16-5-1" --limit 10
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.selma.schema import CaseLawReference
from src.selma.source_validator import validate_url

_API_BASE = "https://www.courtlistener.com/api/rest/v4/opinions/"
OUTPUT_DIR = Path("data/processed")


def statute_to_slug(statute: str) -> str:
    """Convert a statute citation to a safe filename slug."""
    slug = re.sub(r"[\s§\.\(\)]+", "_", statute)
    slug = re.sub(r"_+", "_", slug).strip("_").lower()
    return slug


def fetch_opinions(statute: str, limit: int) -> list[dict]:
    """Fetch opinions from CourtListener that cite the given statute."""
    url = _API_BASE
    params = {
        "q": statute,
        "type": "o",
        "order_by": "score desc",
        "page_size": limit,
    }
    full_url = url + "?" + "&".join(f"{k}={v}" for k, v in params.items())
    # Validate against the base URL (params don't affect trust)
    validate_url(url)

    headers = {"Accept": "application/json"}
    api_key = os.environ.get("COURTLISTENER_API_KEY")
    if api_key:
        headers["Authorization"] = f"Token {api_key}"

    print(f"Fetching opinions for: {statute!r} (limit={limit})")
    response = requests.get(url, params=params, headers=headers, timeout=30)
    response.raise_for_status()
    return response.json().get("results", [])


def parse_result(result: dict, statute: str) -> CaseLawReference:
    """Parse a CourtListener opinion result into a CaseLawReference."""
    date_filed = result.get("date_filed", "") or ""
    year = 0
    if date_filed and len(date_filed) >= 4:
        try:
            year = int(date_filed[:4])
        except ValueError:
            year = 0

    absolute_url = result.get("absolute_url", "")
    if absolute_url and not absolute_url.startswith("http"):
        absolute_url = "https://www.courtlistener.com" + absolute_url

    citation_list = result.get("citation", [])
    if isinstance(citation_list, list) and citation_list:
        citation = citation_list[0]
    elif isinstance(citation_list, str):
        citation = citation_list
    else:
        citation = result.get("id", "")

    return CaseLawReference(
        case_name=result.get("case_name", "Unknown"),
        citation=str(citation),
        court=result.get("court", ""),
        year=year,
        holding=result.get("snippet", ""),
        statute_interpreted=statute,
        url=absolute_url,
    )


def save_results(cases: list[CaseLawReference], statute: str):
    """Save parsed CaseLawReferences to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = statute_to_slug(statute)
    output_path = OUTPUT_DIR / f"caselaw_{slug}.json"

    records = [
        {
            "case_name": c.case_name,
            "citation": c.citation,
            "court": c.court,
            "year": c.year,
            "holding": c.holding,
            "statute_interpreted": c.statute_interpreted,
            "url": c.url,
        }
        for c in cases
    ]

    with open(output_path, "w") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(records)} cases to {output_path}")
    return output_path


def main():
    parser = argparse.ArgumentParser(description="Fetch case law from CourtListener")
    parser.add_argument("--statute", required=True, help='Statute citation, e.g. "18 U.S.C. § 1111"')
    parser.add_argument("--limit", type=int, default=20, help="Max results to fetch (default: 20)")
    args = parser.parse_args()

    results = fetch_opinions(args.statute, args.limit)
    print(f"Retrieved {len(results)} results")

    cases = [parse_result(r, args.statute) for r in results]
    save_results(cases, args.statute)
    print("Done.")


if __name__ == "__main__":
    main()
