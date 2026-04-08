"""
AgentLoops Example: Legal Document Review Agent
Industry: Legal Tech / Contract Management
Use Case: AI contract reviewer that learns clause variations by jurisdiction and reduces
missed issues by propagating attorney corrections.
Expected ROI: Every attorney correction the agent fails to learn from costs $500+ in
billable hours on the next occurrence. One missed clause = $1M+ liability. Learning
loops reduce missed issues from 15% to 2%.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_legal_")
    loops = AgentLoops("contract-reviewer", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: Legal Document Review Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track contract review decisions.
    # Each run = one contract the agent reviewed with the outcome.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking contract reviews ---\n")

    reviews = [
        {
            "input": "Contract: SaaS License Agreement. Counterparty: Acme Corp. "
                     "Jurisdiction: Delaware. Key clauses: 2-year term, auto-renewal, "
                     "mutual indemnification, 12-month limitation of liability cap, "
                     "standard IP ownership clause.",
            "output": "APPROVED with notes. Standard SaaS agreement. All clauses within "
                      "acceptable ranges. Limitation of liability cap at 12 months of fees "
                      "is standard. Recommend signing.",
            "outcome": "approved",
            "metadata": {"contract_type": "saas_license", "jurisdiction": "delaware",
                         "counterparty_size": "enterprise", "value": 240000,
                         "review_time_minutes": 15},
        },
        {
            "input": "Contract: Employment Agreement. Counterparty: Jane Smith (new hire). "
                     "Jurisdiction: California. Key clauses: 2-year non-compete, "
                     "IP assignment covering personal projects, at-will employment.",
            "output": "APPROVED. Standard employment agreement. Non-compete and IP "
                      "assignment clauses present. At-will clause included.",
            "outcome": "attorney_correction",
            "metadata": {"contract_type": "employment", "jurisdiction": "california",
                         "correction": "Non-compete clauses are unenforceable in California "
                         "(Business and Professions Code Section 16600). Must remove the "
                         "non-compete clause entirely. Also, the IP assignment clause "
                         "covering personal projects may violate California Labor Code "
                         "Section 2870. Needs narrowing.",
                         "review_time_minutes": 10},
        },
        {
            "input": "Contract: NDA (Mutual). Counterparty: TechStartup Inc. "
                     "Jurisdiction: New York. Key clauses: 3-year confidentiality period, "
                     "residual knowledge exception, standard exclusions.",
            "output": "APPROVED. Standard mutual NDA. 3-year period is reasonable. "
                      "Residual knowledge clause present — flagging for review but "
                      "acceptable for mutual NDA.",
            "outcome": "approved",
            "metadata": {"contract_type": "nda", "jurisdiction": "new_york",
                         "value": 0, "review_time_minutes": 5},
        },
        {
            "input": "Contract: SaaS License Agreement. Counterparty: GlobalBank. "
                     "Jurisdiction: Texas. Key clauses: 5-year term, unilateral "
                     "indemnification (us only), unlimited liability for data breaches, "
                     "non-compete restricting similar products for 3 years after term.",
            "output": "FLAGGED. Three high-risk clauses: (1) Unilateral indemnification, "
                      "(2) Unlimited liability for data breaches — should be capped, "
                      "(3) 3-year non-compete on similar products is overly broad.",
            "outcome": "flagged",
            "metadata": {"contract_type": "saas_license", "jurisdiction": "texas",
                         "counterparty_size": "enterprise", "value": 1200000,
                         "flags": ["unilateral_indemnification", "unlimited_liability",
                                   "broad_non_compete"],
                         "review_time_minutes": 35},
        },
        {
            "input": "Contract: Employment Agreement. Counterparty: Tom Chen (new hire). "
                     "Jurisdiction: Texas. Key clauses: 1-year non-compete within 50-mile "
                     "radius, IP assignment, at-will with 2-week notice.",
            "output": "FLAGGED. Non-compete clause needs review — Texas has specific "
                      "enforceability requirements. Must verify ancillary to an otherwise "
                      "enforceable agreement and reasonable in scope.",
            "outcome": "approved",
            "metadata": {"contract_type": "employment", "jurisdiction": "texas",
                         "review_time_minutes": 12,
                         "attorney_note": "Good catch flagging the non-compete. Texas "
                         "non-competes are enforceable if reasonable, and 1-year/50-mile "
                         "is within range. Approved as-is."},
        },
        {
            "input": "Contract: Data Processing Agreement (DPA). Counterparty: CloudCo. "
                     "Jurisdiction: EU (GDPR). Key clauses: Standard contractual clauses, "
                     "data retention 5 years, sub-processor notification 30 days, "
                     "audit rights annual.",
            "output": "APPROVED. GDPR-compliant DPA. Standard contractual clauses "
                      "included. 5-year retention seems long but within allowable range. "
                      "Sub-processor notification at 30 days is acceptable.",
            "outcome": "attorney_correction",
            "metadata": {"contract_type": "dpa", "jurisdiction": "eu_gdpr",
                         "correction": "5-year data retention is NOT automatically "
                         "acceptable under GDPR. Must be justified by specific legal basis. "
                         "Need to add a retention schedule tied to processing purposes. "
                         "Also, audit rights should include right to use independent "
                         "third-party auditor, not just annual self-reporting.",
                         "review_time_minutes": 20},
        },
        {
            "input": "Contract: Consulting Agreement. Counterparty: Smith Consulting LLC. "
                     "Jurisdiction: California. Key clauses: Work-for-hire IP assignment, "
                     "non-solicitation 1 year, confidentiality perpetual, net-30 payment.",
            "output": "FLAGGED. California non-solicitation clause may be unenforceable "
                      "under recent case law (AMN Healthcare v. Aya Healthcare, 2022). "
                      "Recommend replacing with a non-interference clause instead. "
                      "Perpetual confidentiality is aggressive — recommend 5-year limit.",
            "outcome": "approved",
            "metadata": {"contract_type": "consulting", "jurisdiction": "california",
                         "value": 180000, "review_time_minutes": 18,
                         "attorney_note": "Excellent analysis of the non-solicitation "
                         "issue under AMN Healthcare. Approved with suggested edits."},
        },
        {
            "input": "Contract: Software License (perpetual). Counterparty: MedTech Inc. "
                     "Jurisdiction: Massachusetts. Key clauses: Perpetual license, "
                     "source code escrow, 3x annual fees limitation of liability, "
                     "HIPAA BAA incorporated by reference.",
            "output": "APPROVED. Perpetual license with source code escrow is standard "
                      "for enterprise. 3x fees liability cap is generous but acceptable. "
                      "HIPAA BAA included by reference.",
            "outcome": "missed_issue",
            "metadata": {"contract_type": "software_license", "jurisdiction": "massachusetts",
                         "value": 500000, "review_time_minutes": 22,
                         "missed": "BAA 'incorporated by reference' is not sufficient — "
                         "the full BAA must be attached as an exhibit and independently "
                         "executed. Reference-only BAAs have been challenged in enforcement "
                         "actions. This is a compliance risk for a healthcare client."},
        },
    ]

    for r in reviews:
        run = loops.track(**r)
        icon = {"approved": "APR", "flagged": "FLG",
                "attorney_correction": "COR", "missed_issue": "MIS"}
        m = r["metadata"]
        print(f"  [{icon.get(r['outcome'], '???'):3s}] {m['contract_type']:20s} "
              f"| {m['jurisdiction']:12s} | {r['outcome']}")

    # -------------------------------------------------------------------
    # Phase 2: Rules from attorney corrections and missed issues.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF jurisdiction is California AND clause type is non-compete THEN "
            "flag as unenforceable and recommend removal — because California "
            "Business and Professions Code Section 16600 voids non-competes",
            ["Employment agreement approved with non-compete in CA — attorney corrected",
             "Consulting agreement correctly flagged non-solicitation under AMN Healthcare"],
            0.98,
        ),
        (
            "IF jurisdiction is California AND clause is IP assignment covering "
            "personal projects THEN flag for narrowing — because California Labor "
            "Code Section 2870 protects employee inventions made on own time",
            ["Employment agreement IP clause too broad — attorney corrected"],
            0.90,
        ),
        (
            "IF contract references HIPAA BAA 'by reference' only THEN flag — "
            "BAA must be attached as exhibit and independently executed, not just "
            "referenced. Reference-only BAAs are compliance risks.",
            ["MedTech license missed: BAA by reference is insufficient"],
            0.95,
        ),
        (
            "IF jurisdiction is EU/GDPR AND data retention period > 3 years THEN "
            "require specific legal basis justification and retention schedule — "
            "because GDPR does not permit blanket long-term retention",
            ["DPA with 5-year retention approved — attorney corrected"],
            0.88,
        ),
        (
            "IF jurisdiction is Texas AND clause type is non-compete THEN "
            "verify it is ancillary to an enforceable agreement and reasonable "
            "in scope — Texas enforces non-competes unlike California",
            ["Texas employment non-compete correctly flagged for review, approved"],
            0.80,
        ),
    ]

    for text, evidence, confidence in rules:
        loops.rules.add_rule(text=text, evidence=evidence, confidence=confidence)
        print(f"  Rule ({confidence:.0%}): {text[:75]}...")

    # -------------------------------------------------------------------
    # Phase 3: Conventions.
    # -------------------------------------------------------------------
    print("\n--- Phase 3: Adding conventions ---\n")

    conventions = [
        ("Jurisdiction determines enforceability. Always check state-specific law "
         "before approving restrictive covenants (non-compete, non-solicitation). "
         "California, Oklahoma, North Dakota, and Colorado have specific restrictions.",
         "derived from CA non-compete correction"),
        ("HIPAA BAAs must be independently executed documents, not incorporated "
         "by reference. This is a hard requirement with no exceptions.",
         "derived from MedTech missed issue"),
        ("Every attorney correction must become a rule. A correction that doesn't "
         "propagate to future reviews is wasted billable hours.",
         "operational policy"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are a contract review agent for a corporate legal team. "
            "Review contracts for risk, flag problematic clauses, and ensure "
            "jurisdictional compliance. Every missed issue is a potential liability.")
    enhanced = loops.enhance_prompt(base)
    for line in enhanced.split("\n"):
        if line.strip():
            print(f"  {line}")

    # -------------------------------------------------------------------
    # Phase 5: Summary.
    # -------------------------------------------------------------------
    print("\n--- Phase 5: Memory pruning ---\n")
    pruned = loops.forget(strategy="hybrid", max_age_days=21)
    print(f"  Pruned: {len(pruned['rules_pruned'])} rules, "
          f"{len(pruned['conventions_pruned'])} conventions")

    print(f"\n--- Summary ---\n")
    approved = sum(1 for r in reviews if r["outcome"] == "approved")
    flagged = sum(1 for r in reviews if r["outcome"] == "flagged")
    corrections = sum(1 for r in reviews if r["outcome"] == "attorney_correction")
    missed = sum(1 for r in reviews if r["outcome"] == "missed_issue")
    total = len(reviews)
    print(f"  Contracts reviewed: {total}")
    print(f"  Approved: {approved} | Flagged: {flagged} | "
          f"Corrected: {corrections} | Missed: {missed}")
    print(f"  Error rate: {(corrections + missed)/total:.0%} (target: <5%)")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"  Critical learning: CA non-competes unenforceable, HIPAA BAAs need execution")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
