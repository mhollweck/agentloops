"""
AgentLoops Example: Insurance Claims Processing Agent
Industry: Property & Casualty Insurance
Use Case: AI claims processor that learns fraud patterns and evolves review criteria.
Expected ROI: One missed fraud claim = $100K+ loss. Learning agents catch evolving fraud
patterns that static rule engines miss. Reduces false positive rate from 30% to 8%,
saving adjusters 100+ hours/month in manual review.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_insurance_")
    loops = AgentLoops("claims-processor", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: Insurance Claims Processing Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track claims processing decisions.
    # Each run = one claim the agent reviewed and decided on.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking claims processing ---\n")

    claims = [
        {
            "input": "Claim #C-9201: Auto collision. Claimant: John Rivera. "
                     "Amount: $4,200. Body shop: Mike's Auto (est. 2019, 142 claims "
                     "processed). Single vehicle, hit guardrail on I-95. "
                     "Police report filed. Photos show front-end damage consistent "
                     "with impact speed.",
            "output": "APPROVED. Damage consistent with reported incident. Body shop "
                      "has good history. Police report confirms. Standard collision claim.",
            "outcome": "approved",
            "metadata": {"amount": 4200, "type": "auto_collision",
                         "body_shop_age_years": 5, "body_shop_claims": 142,
                         "has_police_report": True, "review_time_minutes": 3},
        },
        {
            "input": "Claim #C-9202: Auto collision. Claimant: Sandra Wells. "
                     "Amount: $18,500. Body shop: QuickFix Auto (est. 2024, 8 claims). "
                     "Rear-end collision at intersection. No police report. "
                     "3 other claims from same body shop in last 14 days.",
            "output": "FLAGGED FOR REVIEW. High amount + new body shop + cluster of "
                      "recent claims from same shop + no police report. Possible "
                      "staged accident ring.",
            "outcome": "flagged_fraud",
            "metadata": {"amount": 18500, "type": "auto_collision",
                         "body_shop_age_years": 0.5, "body_shop_claims": 8,
                         "has_police_report": False, "cluster_claims_30d": 3,
                         "review_time_minutes": 15},
        },
        {
            "input": "Claim #C-9203: Water damage. Claimant: Maria Gonzalez. "
                     "Amount: $32,000. Burst pipe in basement. Home built 1985. "
                     "Plumber confirms pipe corrosion. Photos show extensive water damage "
                     "to finished basement. Policy includes water damage rider.",
            "output": "APPROVED. Legitimate water damage claim. Pipe age consistent "
                      "with home age. Plumber report corroborates. Coverage confirmed.",
            "outcome": "approved",
            "metadata": {"amount": 32000, "type": "water_damage",
                         "home_age_years": 41, "has_expert_report": True,
                         "review_time_minutes": 8},
        },
        {
            "input": "Claim #C-9204: Auto theft. Claimant: Derek Chang. "
                     "Amount: $45,000. 2023 BMW M4 reported stolen from driveway. "
                     "Police report filed 3 days after alleged theft. No security "
                     "camera footage. Claimant has 2 prior theft claims in 5 years.",
            "output": "FLAGGED FOR REVIEW. Delayed police report + no footage + "
                      "2 prior theft claims is a significant fraud indicator pattern.",
            "outcome": "flagged_fraud",
            "metadata": {"amount": 45000, "type": "auto_theft",
                         "prior_claims_5y": 2, "police_report_delay_days": 3,
                         "has_footage": False, "review_time_minutes": 20},
        },
        {
            "input": "Claim #C-9205: Auto collision. Claimant: Ashley Park. "
                     "Amount: $6,800. Body shop: QuickFix Auto (same as C-9202). "
                     "T-bone collision at parking lot. No police report. "
                     "4th claim from QuickFix in 21 days.",
            "output": "FLAGGED FOR REVIEW. Same body shop as C-9202 flagged claim. "
                      "This is the 4th claim from QuickFix Auto in 21 days. "
                      "Escalating to SIU for pattern investigation.",
            "outcome": "flagged_fraud",
            "metadata": {"amount": 6800, "type": "auto_collision",
                         "body_shop_age_years": 0.5, "body_shop_claims": 12,
                         "has_police_report": False, "cluster_claims_30d": 4,
                         "review_time_minutes": 5, "related_claim": "C-9202"},
        },
        {
            "input": "Claim #C-9206: Homeowner fire. Claimant: Robert Zhang. "
                     "Amount: $125,000. Kitchen fire from grease. Fire department "
                     "report confirms accidental origin. Smoke damage to 3 rooms. "
                     "Policy current, no prior claims.",
            "output": "APPROVED with adjustor review. Amount exceeds auto-approve "
                      "threshold. Fire department confirms accidental. Clean history. "
                      "Recommend standard adjustor visit.",
            "outcome": "approved",
            "metadata": {"amount": 125000, "type": "fire", "prior_claims_5y": 0,
                         "has_expert_report": True, "review_time_minutes": 12},
        },
        {
            "input": "Claim #C-9207: Auto collision. Claimant: James Wilson. "
                     "Amount: $3,100. Fender bender in grocery store parking lot. "
                     "Other driver's insurance confirmed. Photos match. "
                     "Body shop: Reliable Auto (est. 2001, 2,400 claims).",
            "output": "APPROVED. Low amount, established body shop, other party "
                      "confirmed, photos consistent. Straightforward claim.",
            "outcome": "approved",
            "metadata": {"amount": 3100, "type": "auto_collision",
                         "body_shop_age_years": 25, "body_shop_claims": 2400,
                         "has_police_report": False, "review_time_minutes": 2},
        },
        {
            "input": "Claim #C-9208: Auto collision. Claimant: Patricia Lee. "
                     "Amount: $11,200. Body shop: ABC Auto (est. 2023, 22 claims). "
                     "Multi-car accident on highway. Police report filed. "
                     "2 claims from ABC Auto in last 30 days.",
            "output": "APPROVED. Despite newer body shop, police report confirms "
                      "multi-car accident. Amount reasonable for reported damage. "
                      "2 claims in 30 days is within normal range for busy shop.",
            "outcome": "disputed",
            "metadata": {"amount": 11200, "type": "auto_collision",
                         "body_shop_age_years": 3, "body_shop_claims": 22,
                         "has_police_report": True, "cluster_claims_30d": 2,
                         "review_time_minutes": 10, "dispute_reason": "SIU found "
                         "body shop inflated repair estimate by $4,000"},
        },
    ]

    for c in claims:
        run = loops.track(**c)
        icon = {"approved": "APR", "flagged_fraud": "FLG",
                "disputed": "DIS", "reopened": "REO"}
        print(f"  [{icon.get(c['outcome'], '???'):3s}] {c['input'][7:14]} "
              f"| ${c['metadata']['amount']:>8,} | {c['metadata']['type']:15s} "
              f"| {c['outcome']}")

    # -------------------------------------------------------------------
    # Phase 2: Fraud detection rules.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned fraud rules ---\n")

    rules = [
        (
            "IF claim amount > $10K AND body shop is less than 2 years old AND "
            "3+ claims from that shop in 30 days THEN escalate to SIU — because "
            "QuickFix Auto pattern showed organized fraud ring with staged accidents",
            ["C-9202 flagged: $18.5K, shop 0.5yr old, 3 claims in 14 days",
             "C-9205 flagged: same shop, 4th claim in 21 days"],
            0.95,
        ),
        (
            "IF claim is auto theft AND prior theft claims >= 2 AND police report "
            "delayed > 48 hours THEN flag for SIU investigation — because repeat "
            "theft claimants with delayed reporting are 8x more likely to be fraudulent",
            ["C-9204: 2 prior thefts, 3-day delayed report"],
            0.85,
        ),
        (
            "IF body shop is newer than 3 years AND claim is approved THEN verify "
            "repair estimate against market rates — because C-9208 was approved but "
            "SIU found $4K inflation on a $11.2K claim (36% overcharge)",
            ["C-9208 disputed after estimate inflation discovered"],
            0.80,
        ),
        (
            "IF claim amount > $100K AND has fire department report confirming "
            "accidental AND no prior claims THEN approve with standard adjustor "
            "visit — no need for SIU escalation on legitimate high-value claims",
            ["C-9206 approved smoothly with fire dept confirmation"],
            0.75,
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
        ("Track body shop claim frequency as a first-class signal. Cluster analysis "
         "catches organized fraud rings that individual claim review misses.",
         "derived from QuickFix Auto fraud pattern"),
        ("Police reports reduce fraud probability significantly but do not eliminate "
         "it — verify repair estimates independently even when police report exists.",
         "derived from C-9208 disputed claim"),
        ("Auto-approve threshold is $50K for claims with expert reports and clean "
         "history. Above that, always require human adjustor review.",
         "operational policy"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are an insurance claims processing agent. Review claims for "
            "legitimacy, detect potential fraud, and make approve/flag decisions. "
            "Prioritize accuracy — missed fraud costs $100K+, false positives "
            "waste adjuster time.")
    enhanced = loops.enhance_prompt(base)
    for line in enhanced.split("\n"):
        if line.strip():
            print(f"  {line}")

    # -------------------------------------------------------------------
    # Phase 5: Forget + summary.
    # -------------------------------------------------------------------
    print("\n--- Phase 5: Memory pruning ---\n")
    pruned = loops.forget(strategy="hybrid", max_age_days=21)
    print(f"  Pruned: {len(pruned['rules_pruned'])} rules, "
          f"{len(pruned['conventions_pruned'])} conventions")

    print(f"\n--- Summary ---\n")
    total_claims = len(claims)
    approved = sum(1 for c in claims if c["outcome"] == "approved")
    flagged = sum(1 for c in claims if c["outcome"] == "flagged_fraud")
    disputed = sum(1 for c in claims if c["outcome"] == "disputed")
    total_amount = sum(c["metadata"]["amount"] for c in claims)
    flagged_amount = sum(c["metadata"]["amount"] for c in claims
                         if c["outcome"] == "flagged_fraud")
    print(f"  Claims processed: {total_claims}")
    print(f"  Approved: {approved} | Flagged: {flagged} | Disputed: {disputed}")
    print(f"  Total claim value: ${total_amount:,}")
    print(f"  Flagged claim value: ${flagged_amount:,} (fraud exposure avoided)")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
