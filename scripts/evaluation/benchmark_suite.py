#!/usr/bin/env python3
"""
SELMA Benchmark Suite.

Standardized test scenarios for evaluating criminal law analysis capability.
"""

BENCHMARK_SCENARIOS = [
    {
        "id": "federal_001",
        "category": "violent_crime",
        "description": "Two individuals enter a federally-insured bank. One brandishes a firearm "
                       "and demands money from the teller while the other stands guard at the door. "
                       "They flee with $50,000 in cash.",
        "expected_statutes": ["18 U.S.C. § 2113", "18 U.S.C. § 924(c)"],
        "expected_charges": ["Bank Robbery", "Use of Firearm During Crime of Violence"],
        "jurisdiction": "federal",
    },
    {
        "id": "federal_002",
        "category": "fraud",
        "description": "A company executive systematically overstates revenue figures in SEC filings "
                       "over a three-year period, inflating the stock price. Investors lose $2M when "
                       "the fraud is discovered.",
        "expected_statutes": ["18 U.S.C. § 1348", "18 U.S.C. § 1341", "18 U.S.C. § 1343"],
        "expected_charges": ["Securities Fraud", "Mail Fraud", "Wire Fraud"],
        "jurisdiction": "federal",
    },
    {
        "id": "georgia_001",
        "category": "violent_crime",
        "description": "During a verbal altercation at a bar in Atlanta, GA, Person A strikes "
                       "Person B in the head with a pool cue, causing a laceration requiring "
                       "12 stitches. Person B loses consciousness briefly.",
        "expected_statutes": ["O.C.G.A. § 16-5-24", "O.C.G.A. § 16-5-21"],
        "expected_charges": ["Aggravated Assault", "Aggravated Battery"],
        "jurisdiction": "georgia",
    },
    {
        "id": "georgia_002",
        "category": "property_crime",
        "description": "A person enters an occupied dwelling in Savannah, GA at 2 AM through "
                       "an unlocked window. They take a laptop, jewelry, and a handgun. The "
                       "homeowner wakes up and sees them leaving.",
        "expected_statutes": ["O.C.G.A. § 16-7-1", "O.C.G.A. § 16-8-12"],
        "expected_charges": ["Burglary", "Theft by Taking"],
        "jurisdiction": "georgia",
    },
    {
        "id": "mixed_001",
        "category": "drug_offense",
        "description": "Federal agents observe a person in Fulton County, GA receiving a package "
                       "containing 500 grams of methamphetamine shipped via USPS from California. "
                       "The person is found with $10,000 in cash and a digital scale.",
        "expected_statutes": [
            "21 U.S.C. § 841",
            "18 U.S.C. § 1952",
            "O.C.G.A. § 16-13-30",
        ],
        "expected_charges": [
            "Possession with Intent to Distribute",
            "Travel Act Violation",
            "Trafficking in Methamphetamine",
        ],
        "jurisdiction": "both",
    },
]


def get_benchmark_scenarios(
    category: str = None,
    jurisdiction: str = None,
) -> list[dict]:
    """Get benchmark scenarios, optionally filtered."""
    scenarios = BENCHMARK_SCENARIOS

    if category:
        scenarios = [s for s in scenarios if s["category"] == category]
    if jurisdiction:
        scenarios = [s for s in scenarios if s["jurisdiction"] == jurisdiction or s["jurisdiction"] == "both"]

    return scenarios


if __name__ == "__main__":
    import json
    print(json.dumps(BENCHMARK_SCENARIOS, indent=2))
