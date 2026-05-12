#!/usr/bin/env python3
"""
Fetch U.S. Code Title 18 (Crimes and Criminal Procedure) from uscode.house.gov.

Downloads the official USLM XML and parses it into structured JSON for training.
"""

import json
import os
import re
import sys
import zipfile
from pathlib import Path

import requests
from lxml import etree
from tqdm import tqdm

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from src.selma.source_validator import validate_url

# Fallback URL — pinned to a known-good release. discover_latest_url() will
# try to find the current release first; this is only used if that fails.
_FALLBACK_URL = "https://uscode.house.gov/download/releasepoints/us/pl/119/88/xml_usc18@119-88.zip"
_DOWNLOAD_PAGE = "https://uscode.house.gov/download/download.shtml"

RAW_DIR = Path("data/raw/federal")
OUTPUT_DIR = Path("data/processed")

# USLM namespace
NS = {"uslm": "https://xml.house.gov/schemas/uslm/1.0"}


def discover_latest_url() -> str:
    """Discover the current Title 18 USLM XML zip URL from the House download page.

    Falls back to the hardcoded release URL if discovery fails.
    """
    try:
        resp = requests.get(_DOWNLOAD_PAGE, timeout=15)
        resp.raise_for_status()
        matches = re.findall(r'href="([^"]*xml_usc18@[^"]+\.zip)"', resp.text)
        if matches:
            url = matches[0]
            if url.startswith("http"):
                return url
            return "https://uscode.house.gov" + url
        print("Warning: Could not find Title 18 URL on download page; using fallback.")
    except Exception as e:
        print(f"Warning: URL discovery failed ({e}); using fallback URL.")
    return _FALLBACK_URL


def download_title18(url: str = None) -> Path:
    """Download Title 18 USLM XML zip file."""
    if url is None:
        url = discover_latest_url()
    validate_url(url)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = RAW_DIR / "usc18.zip"

    if zip_path.exists():
        print(f"Using cached {zip_path}")
        return zip_path

    print(f"Downloading Title 18 from {url}...")
    response = requests.get(url, stream=True, timeout=120)
    response.raise_for_status()

    total = int(response.headers.get("content-length", 0))
    with open(zip_path, "wb") as f:
        with tqdm(total=total, unit="B", unit_scale=True, desc="Downloading") as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))

    return zip_path


def extract_xml(zip_path: Path) -> Path:
    """Extract XML from the downloaded zip."""
    print(f"Extracting {zip_path}...")
    extract_dir = RAW_DIR / "xml"
    extract_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as zf:
        zf.extractall(extract_dir)

    # Find the main XML file
    xml_files = list(extract_dir.rglob("*.xml"))
    if not xml_files:
        raise FileNotFoundError("No XML files found in archive")

    print(f"Found {len(xml_files)} XML file(s)")
    return xml_files[0]


def parse_uslm_xml(xml_path: Path) -> dict:
    """Parse USLM XML into structured statute data.

    Returns a dict mapping section numbers to statute info.
    """
    print(f"Parsing {xml_path}...")
    tree = etree.parse(str(xml_path))
    root = tree.getroot()

    # Auto-detect namespace
    nsmap = root.nsmap
    ns = nsmap.get(None, "https://xml.house.gov/schemas/uslm/1.0")
    NS = {"uslm": ns}

    statutes = {}

    # Find all sections
    sections = root.findall(".//uslm:section", NS)
    if not sections:
        # Try without namespace
        sections = root.iter()
        sections = [e for e in root.iter() if e.tag.endswith("}section") or e.tag == "section"]

    print(f"Found {len(sections)} sections")

    for section in tqdm(sections, desc="Parsing sections"):
        try:
            # Extract section identifier
            identifier = section.get("identifier", "")
            if not identifier:
                # Try to get from num element
                num_elem = section.find(".//uslm:num", NS)
                if num_elem is None:
                    num_elem = next(
                        (e for e in section if e.tag.endswith("}num") or e.tag == "num"),
                        None,
                    )
                if num_elem is not None:
                    identifier = num_elem.get("value", num_elem.text or "")

            if not identifier:
                continue

            # Clean section number
            section_num = identifier.strip("/us/usc/t18/s").strip("§ ").strip()

            # Extract heading/title
            heading_elem = section.find(".//uslm:heading", NS)
            if heading_elem is None:
                heading_elem = next(
                    (e for e in section if e.tag.endswith("}heading") or e.tag == "heading"),
                    None,
                )
            heading = ""
            if heading_elem is not None:
                heading = "".join(heading_elem.itertext()).strip()

            # Extract full text
            text_parts = []
            for elem in section.iter():
                if elem.text:
                    text_parts.append(elem.text.strip())
                if elem.tail:
                    text_parts.append(elem.tail.strip())
            full_text = " ".join(filter(None, text_parts))

            if section_num and (heading or full_text):
                statutes[section_num] = {
                    "section": section_num,
                    "title": heading,
                    "text": full_text[:5000],  # Truncate very long sections
                    "citation": f"18 U.S.C. § {section_num}",
                    "jurisdiction": "federal",
                }
        except Exception as e:
            print(f"  Warning: Failed to parse section: {e}", file=sys.stderr)
            continue

    return statutes


def save_statutes(statutes: dict):
    """Save parsed statutes to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / "federal_statutes.json"

    with open(output_path, "w") as f:
        json.dump(statutes, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(statutes)} federal statutes to {output_path}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("SELMA — Fetching U.S. Code Title 18")
    print("=" * 60)

    zip_path = download_title18()
    xml_path = extract_xml(zip_path)
    statutes = parse_uslm_xml(xml_path)
    save_statutes(statutes)

    print(f"\nDone! {len(statutes)} sections processed.")
    print(f"Sample sections: {list(statutes.keys())[:10]}")


if __name__ == "__main__":
    main()
