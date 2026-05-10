#!/usr/bin/env python3
"""
Fetch Georgia O.C.G.A. Title 16 (Crimes and Offenses) from law.onecle.com.

Note: The official Georgia code is copyrighted and published through LexisNexis.
This script uses law.onecle.com as a freely available (though potentially dated) source.
For production use, verify against the official O.C.G.A. at
https://www.lexisnexis.com/hottopics/gacode/
"""

import json
import re
import time
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

BASE_URL = "https://law.onecle.com/georgia/title-16"
RAW_DIR = Path("data/raw/georgia")
OUTPUT_DIR = Path("data/processed")

HEADERS = {
    "User-Agent": "SELMA-DataCollector/0.1 (Academic Research; Apache 2.0)"
}

# O.C.G.A. Title 16 chapters
CHAPTERS = {
    "1": "General Provisions",
    "2": "Criminal Liability",
    "3": "Defenses to Criminal Prosecutions",
    "4": "Criminal Attempt, Conspiracy, and Solicitation",
    "5": "Crimes Against the Person",
    "6": "Sexual Offenses",
    "7": "Damage to and Intrusion Upon Property",
    "8": "Offenses Involving Theft",
    "9": "Forgery and Fraudulent Practices",
    "10": "Offenses Against Public Administration",
    "11": "Offenses Against Public Order and Safety",
    "12": "Offenses Against Public Health and Morals",
    "13": "Controlled Substances",
    "14": "Racketeer Influenced and Corrupt Organizations",
    "15": "Street Gang Terrorism and Prevention",
    "16": "Civil Forfeiture",
    "17": "Payday Lending",
}


def fetch_chapter_sections(chapter_num: str) -> list[dict]:
    """Fetch the list of sections for a given chapter."""
    url = f"{BASE_URL}/chapter-{chapter_num}/index.html"
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException as e:
        print(f"  Warning: Could not fetch chapter {chapter_num}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    sections = []

    for link in soup.find_all("a", href=True):
        href = link["href"]
        text = link.get_text(strip=True)
        # Match section links like "/georgia/title-16/16-1-1.html"
        if re.search(r"16-\d+-\d+", href):
            section_match = re.search(r"(16-\d+-\d+[\.\d]*)", href.replace(".html", ""))
            if section_match:
                section_num = section_match.group(1)
                if href.startswith("/"):
                    full_url = f"https://law.onecle.com{href}"
                elif href.startswith("http"):
                    full_url = href
                else:
                    full_url = f"{BASE_URL}/{href}"
                sections.append({
                    "section": section_num,
                    "title": text,
                    "url": full_url,
                })

    return sections


def fetch_section_text(url: str) -> str:
    """Fetch the full text of a specific section."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except requests.RequestException:
        return ""

    soup = BeautifulSoup(resp.text, "html.parser")

    # onecle.com uses div.col-sm-12 for the main content
    content = soup.select_one("div.col-sm-12")
    if not content:
        # Fallback selectors
        for selector in ["div.section-text", "div#content", "div.container"]:
            content = soup.select_one(selector)
            if content:
                break

    if content:
        # Remove nav, script, style elements
        for tag in content.find_all(["script", "style", "nav", "footer"]):
            tag.decompose()
        text = content.get_text(separator="\n", strip=True)
        # Clean: remove section navigation lists at the end
        # Cut at "Last modified:" or "Section:" lines if they're just navigation
        lines = text.split("\n")
        clean_lines = []
        for line in lines:
            if line.startswith("Section:") or line.startswith("Last modified:"):
                break
            if re.match(r"^16-\d+-\d+$", line.strip()):
                continue  # Skip bare section number links
            if line.strip() in ("Next", "Previous"):
                continue
            clean_lines.append(line)
        text = "\n".join(clean_lines)
    else:
        paragraphs = soup.find_all("p")
        text = "\n".join(p.get_text(strip=True) for p in paragraphs)

    return text


def fetch_all_georgia_statutes() -> dict:
    """Fetch all sections from O.C.G.A. Title 16."""
    statutes = {}

    for chapter_num, chapter_name in tqdm(CHAPTERS.items(), desc="Chapters"):
        print(f"\nChapter {chapter_num}: {chapter_name}")
        sections = fetch_chapter_sections(chapter_num)
        print(f"  Found {len(sections)} sections")

        for section_info in tqdm(sections, desc=f"  Ch.{chapter_num}", leave=False):
            section_num = section_info["section"]
            text = fetch_section_text(section_info["url"])

            if text and len(text) > 50:  # Filter out empty/trivial pages
                statutes[section_num] = {
                    "section": section_num,
                    "chapter": chapter_num,
                    "chapter_name": chapter_name,
                    "title": section_info["title"],
                    "text": text[:5000],
                    "citation": f"O.C.G.A. § {section_num}",
                    "jurisdiction": "georgia",
                    "source": section_info["url"],
                    "source_note": "law.onecle.com (may not be current)",
                }

            # Be polite to the server
            time.sleep(0.3)

    return statutes


def save_statutes(statutes: dict):
    """Save parsed statutes to JSON."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / "georgia_statutes.json"
    with open(output_path, "w") as f:
        json.dump(statutes, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(statutes)} Georgia statutes to {output_path}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("SELMA — Fetching Georgia O.C.G.A. Title 16")
    print("=" * 60)
    print("Source: law.onecle.com (free but may be dated)")
    print("Note: Verify against official LexisNexis source for production use")
    print()

    statutes = fetch_all_georgia_statutes()
    save_statutes(statutes)

    print(f"\nDone! {len(statutes)} sections processed.")


if __name__ == "__main__":
    main()
