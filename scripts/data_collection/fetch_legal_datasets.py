#!/usr/bin/env python3
"""
Fetch legal NLP datasets from HuggingFace for SELMA training.

Downloads and processes:
- ALEA US Courts NOS/Cause classification (491K examples)
- LegalBench legal reasoning tasks (91.8K examples)
- CaseHOLD legal holding classification (585K examples)
"""

import json
from pathlib import Path

from datasets import load_dataset
from tqdm import tqdm

OUTPUT_DIR = Path("data/raw")


def fetch_alea_courts():
    """Fetch ALEA US Courts NOS/Cause classification dataset."""
    print("\n" + "=" * 60)
    print("Fetching ALEA US Courts NOS/Cause dataset...")
    print("=" * 60)

    try:
        ds = load_dataset("alea-institute/alea-legal-benchmark-uscourts-nos-cause")
        output_path = OUTPUT_DIR / "alea_courts.jsonl"

        count = 0
        with open(output_path, "w") as f:
            for split in ds:
                for example in tqdm(ds[split], desc=f"Processing {split}"):
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    count += 1

        print(f"Saved {count} examples to {output_path}")
    except Exception as e:
        print(f"Warning: Could not fetch ALEA dataset: {e}")
        print("You may need to accept the dataset license on HuggingFace first.")


LEGALBENCH_TASKS = [
    "abercrombie", "canada_tax_court_outcomes", "contract_nli_confidentiality_of_agreement",
    "contract_nli_explicit_identification", "contract_nli_inclusion_of_verbatim_text",
    "contract_nli_limited_use", "contract_nli_no_licensing", "contract_nli_notice_on_compelled_disclosure",
    "contract_nli_permissible_acqui_of_similar_info", "contract_nli_permissible_copy",
    "contract_nli_permissible_development_of_similar_info", "contract_nli_permissible_post_agreement_possession",
    "contract_nli_return_of_confidential_info", "contract_nli_sharing_with_employees",
    "contract_nli_sharing_with_third_parties", "contract_nli_survival_of_obligations",
    "contract_nli_use_of_pe_in_agreements", "corporate_lobbying", "cuad_anti_assignment",
    "cuad_audit_rights", "cuad_cap_on_liability", "cuad_change_of_control",
    "cuad_competitive_restriction_exception", "cuad_covenant_not_to_sue",
    "cuad_effective_date", "cuad_governing_law", "cuad_insurance", "cuad_ip_ownership_assignment",
    "cuad_irrevocable_or_perpetual_license", "cuad_joint_ip_ownership", "cuad_license_grant",
    "cuad_liquidated_damages", "cuad_minimum_commitment", "cuad_most_favored_nation",
    "cuad_mutual_non_dispatch", "cuad_non_compete", "cuad_non_disparagement",
    "cuad_non_solicitation", "cuad_no_solicit_of_customers", "cuad_no_solicit_of_employees",
    "cuad_notice_period_to_terminate_renewal", "cuad_post_termination_services",
    "cuad_price_restrictions", "cuad_renewal_term", "cuad_revenue_profit_sharing",
    "cuad_rofr_rofo_rofn", "cuad_source_code_escrow", "cuad_termination_for_convenience",
    "cuad_third_party_beneficiary", "cuad_uncapped_liability", "cuad_unlimited_all_you_can_eat_license",
    "cuad_volume_restriction", "cuad_warranty_duration", "definition_classification",
    "diversity_1", "diversity_2", "diversity_3", "diversity_4", "diversity_5", "diversity_6",
    "function_of_decision_section", "hearsay", "insurance_policy_interpretation",
    "international_citizenship_questions", "jcrew_blocker", "legal_reasoning_causality",
    "maud_ability_to_consummate_concept_is_subject_to_mae_carveouts",
    "oral_argument_question_purpose", "overruling", "personal_jurisdiction",
    "privacy_policy_entailment", "privacy_policy_qa", "proa", "rule_qa",
    "sara_entailment", "sara_numeric", "scalr", "secured_transactions_purchase_money_security_interest",
    "spell_out", "ssla_companies_and_funds", "ssla_elements", "ssla_types_of_debt",
    "statutory_reasoning_assessment", "supply_chain_disclosure_best_practice_accountability",
    "supply_chain_disclosure_best_practice_auditing",
    "supply_chain_disclosure_best_practice_certification",
    "supply_chain_disclosure_best_practice_training",
    "supply_chain_disclosure_best_practice_verification",
    "telemarketing_sales_rule", "textualism_tool_dictionaries", "textualism_tool_plain",
    "ucc_v_common_law", "unfair_tos",
]


def fetch_legalbench():
    """Fetch LegalBench reasoning tasks (all available subsets)."""
    print("\n" + "=" * 60)
    print("Fetching LegalBench dataset (all subsets)...")
    print("=" * 60)

    output_path = OUTPUT_DIR / "legalbench.jsonl"
    total = 0

    with open(output_path, "w") as f:
        for task in LEGALBENCH_TASKS:
            try:
                ds = load_dataset("nguha/legalbench", task, trust_remote_code=True)
                for split in ds:
                    for example in ds[split]:
                        row = dict(example)
                        row["task"] = task
                        f.write(json.dumps(row, ensure_ascii=False) + "\n")
                        total += 1
                print(f"  {task}: OK")
            except Exception as e:
                print(f"  {task}: skipped ({e})")

    print(f"Saved {total} LegalBench examples to {output_path}")


def fetch_casehold():
    """Fetch CaseHOLD legal holding classification dataset via parquet."""
    print("\n" + "=" * 60)
    print("Fetching CaseHOLD dataset...")
    print("=" * 60)

    # casehold/casehold uses a deprecated loading script; load from CSV directly
    csv_splits = {
        "train": "hf://datasets/casehold/casehold/data/all/train.csv",
        "validation": "hf://datasets/casehold/casehold/data/all/val.csv",
        "test": "hf://datasets/casehold/casehold/data/all/test.csv",
    }

    try:
        ds = load_dataset("csv", data_files=csv_splits)
        output_path = OUTPUT_DIR / "casehold.jsonl"

        count = 0
        with open(output_path, "w") as f:
            for split in ds:
                for example in tqdm(ds[split], desc=f"Processing {split}"):
                    f.write(json.dumps(example, ensure_ascii=False) + "\n")
                    count += 1

        print(f"Saved {count} CaseHOLD examples to {output_path}")
    except Exception as e:
        print(f"Warning: Could not fetch CaseHOLD dataset: {e}")


def main():
    """Main entry point."""
    print("=" * 60)
    print("SELMA — Fetching Legal NLP Datasets from HuggingFace")
    print("=" * 60)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    fetch_alea_courts()
    fetch_legalbench()
    fetch_casehold()

    print("\nDone! Check data/raw/ for downloaded datasets.")


if __name__ == "__main__":
    main()
