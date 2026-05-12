#!/usr/bin/env python3
"""
Add a new trusted data source to SELMA's allowlist.

Usage:
    python scripts/add_source.py \\
        --id california_leginfo \\
        --name "California Penal Code (leginfo.legislature.ca.gov)" \\
        --jurisdiction california \\
        --type statute \\
        --url-pattern "https://leginfo.legislature.ca.gov/" \\
        --format html \\
        --license public_domain

    python scripts/add_source.py --list
    python scripts/add_source.py --list --jurisdiction georgia
"""

import argparse
import sys
from pathlib import Path

import yaml

CONFIGS_DIR = Path(__file__).parent.parent / "configs"
TRUSTED_SOURCES = CONFIGS_DIR / "trusted_sources.yaml"

VALID_TYPES = {"statute", "civil_statute", "caselaw", "dataset"}
VALID_FORMATS = {"uslm_xml", "html", "csv", "jsonl", "json", "pdf"}
VALID_LICENSES = {"public_domain", "fair_use", "open", "cc_by", "cc_by_sa", "cc0", "proprietary"}


def load_config() -> dict:
    with open(TRUSTED_SOURCES) as f:
        return yaml.safe_load(f) or {}


def save_config(data: dict):
    with open(TRUSTED_SOURCES, "w") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)


def list_sources(jurisdiction: str = None):
    data = load_config()
    sources = data.get("sources", [])
    if jurisdiction:
        sources = [s for s in sources if s.get("jurisdiction") == jurisdiction]
    if not sources:
        print("No sources found.")
        return
    print(f"{'ID':<30} {'Jurisdiction':<14} {'Type':<10} {'Name'}")
    print("-" * 80)
    for s in sources:
        print(f"{s['id']:<30} {s['jurisdiction']:<14} {s['type']:<10} {s['name']}")


def add_source(args: argparse.Namespace):
    data = load_config()
    sources = data.get("sources", [])

    # Check for duplicate id
    existing_ids = {s["id"] for s in sources}
    if args.id in existing_ids:
        print(f"Error: A source with id '{args.id}' already exists.", file=sys.stderr)
        print("Use --list to see existing sources.", file=sys.stderr)
        sys.exit(1)

    # Validate URL patterns are proper prefixes (must start with https://)
    patterns = args.url_pattern
    for p in patterns:
        if not p.startswith("https://"):
            print(f"Error: url-pattern must start with 'https://': {p}", file=sys.stderr)
            sys.exit(1)

    new_source: dict = {
        "id": args.id,
        "name": args.name,
        "jurisdiction": args.jurisdiction,
        "type": args.type,
        "url_patterns": patterns,
        "format": args.format,
        "license": args.license,
    }
    if args.discovery_url:
        new_source["discovery_url"] = args.discovery_url
    if args.discovery_regex:
        new_source["discovery_regex"] = args.discovery_regex
    if args.note:
        new_source["note"] = args.note

    sources.append(new_source)
    data["sources"] = sources
    save_config(data)

    print(f"Added source '{args.id}' to {TRUSTED_SOURCES}")
    print()
    print("Next steps:")
    print("  1. Review the entry in configs/trusted_sources.yaml")
    print("  2. Commit the change: git add configs/trusted_sources.yaml && git commit")
    print("     (Git history is the audit trail for source additions.)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Add a trusted data source to SELMA's allowlist.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command")

    # list
    ls = sub.add_parser("list", help="List current trusted sources")
    ls.add_argument("--jurisdiction", help="Filter by jurisdiction (e.g. 'georgia')")

    # add (default if no subcommand)
    parser.add_argument("--id", help="Unique source identifier (snake_case)")
    parser.add_argument("--name", help="Human-readable source name")
    parser.add_argument("--jurisdiction", help="Jurisdiction (e.g. 'federal', 'georgia', 'california')")
    parser.add_argument(
        "--type", choices=sorted(VALID_TYPES), help="Source type"
    )
    parser.add_argument(
        "--url-pattern",
        dest="url_pattern",
        action="append",
        metavar="URL_PREFIX",
        help="Trusted URL prefix (https:// required). Repeat for multiple patterns.",
    )
    parser.add_argument(
        "--format", choices=sorted(VALID_FORMATS), help="Data format"
    )
    parser.add_argument(
        "--license", choices=sorted(VALID_LICENSES), help="Source license"
    )
    parser.add_argument("--discovery-url", help="(optional) Page to scrape for current download URL")
    parser.add_argument("--discovery-regex", help="(optional) Regex to extract download URL from discovery page")
    parser.add_argument("--note", help="(optional) Caveats or verification guidance")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()

    if args.command == "list":
        list_sources(getattr(args, "jurisdiction", None))
        return

    # Adding a source — all fields required
    required = ["id", "name", "jurisdiction", "type", "url_pattern", "format", "license"]
    missing = [f"--{f.replace('_', '-')}" for f in required if not getattr(args, f, None)]
    if missing:
        parser.error(f"The following arguments are required: {', '.join(missing)}")

    add_source(args)


if __name__ == "__main__":
    main()
