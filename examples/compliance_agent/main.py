"""
AgentLoops Example: Regulatory Compliance Monitoring Agent
Industry: Financial Services / RegTech
Use Case: AI compliance monitor that learns which transaction patterns are truly risky
vs noise, reducing false positive fatigue while catching real violations.
Expected ROI: $10K-50K/month in analyst time savings. False positive rates typically
drop from 95% to 20% with learning loops. One missed violation = $500K+ fine.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_compliance_")
    loops = AgentLoops("compliance-monitor", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: Regulatory Compliance Monitoring Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track compliance screening decisions.
    # Each run = one transaction or activity the agent reviewed.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking compliance screenings ---\n")

    screenings = [
        {
            "input": "Transaction: Wire transfer $49,500 from Acme LLC to offshore account "
                     "in Cayman Islands. Just under $50K reporting threshold. "
                     "Acme LLC established 2 months ago. 3rd similar transfer this week.",
            "output": "FLAGGED: Structuring pattern detected. Amount just below $50K "
                      "reporting threshold. New entity. Multiple transfers in short period. "
                      "Recommend SAR filing.",
            "outcome": "flagged",
            "metadata": {"rule_type": "structuring", "amount": 49500,
                         "regulation": "BSA/AML", "entity_age_months": 2,
                         "similar_txn_count_7d": 3, "analyst_verdict": "true_positive",
                         "fine_avoided_estimate": 250000},
        },
        {
            "input": "Transaction: ACH payment $125,000 from Johnson Manufacturing to "
                     "overseas supplier. Johnson Manufacturing is a 15-year customer. "
                     "Regular monthly payment to same supplier for 3 years.",
            "output": "FLAGGED: Large international transfer. Overseas destination.",
            "outcome": "false_positive",
            "metadata": {"rule_type": "large_international", "amount": 125000,
                         "regulation": "BSA/AML", "entity_age_months": 180,
                         "pattern": "recurring_supplier_payment",
                         "analyst_time_wasted_minutes": 20},
        },
        {
            "input": "Activity: Customer opened 4 accounts at different branches within "
                     "48 hours. Each account funded with exactly $9,000 cash. "
                     "Customer provided different phone numbers for each.",
            "output": "FLAGGED: Multi-account structuring. Cash deposits below $10K CTR "
                      "threshold across branches. Different contact info suggests intent "
                      "to avoid aggregation. High-risk pattern.",
            "outcome": "flagged",
            "metadata": {"rule_type": "multi_account_structuring", "amount": 36000,
                         "regulation": "BSA/AML", "accounts_opened": 4,
                         "analyst_verdict": "true_positive",
                         "fine_avoided_estimate": 500000},
        },
        {
            "input": "Transaction: Payroll batch $850,000 from TechCorp to 150 employees. "
                     "Monthly payroll. Same amount within 5% for last 12 months.",
            "output": "FLAGGED: Large batch transaction exceeds daily monitoring threshold.",
            "outcome": "false_positive",
            "metadata": {"rule_type": "large_batch", "amount": 850000,
                         "regulation": "BSA/AML", "pattern": "regular_payroll",
                         "entity_age_months": 60,
                         "analyst_time_wasted_minutes": 15},
        },
        {
            "input": "Transaction: Crypto exchange transfer $75,000 from personal account "
                     "to Binance. Customer is a 24-year-old student with account balance "
                     "normally under $5,000. No known income source for this amount.",
            "output": "FLAGGED: Source of funds concern. Transfer amount inconsistent "
                      "with customer profile. Crypto exchange destination adds risk. "
                      "Recommend enhanced due diligence.",
            "outcome": "flagged",
            "metadata": {"rule_type": "source_of_funds", "amount": 75000,
                         "regulation": "BSA/AML", "profile_mismatch": True,
                         "analyst_verdict": "true_positive",
                         "fine_avoided_estimate": 100000},
        },
        {
            "input": "Activity: AI-powered lending model approved a loan for a customer "
                     "in Colorado. Model uses zip code as a feature. Colorado AI Act "
                     "requires disclosure of AI use in consequential decisions. "
                     "No disclosure was provided.",
            "output": "FLAGGED: Colorado AI Act (SB 21-169) violation. AI model used in "
                      "consequential decision (lending) without required consumer notice. "
                      "Zip code feature may also create proxy discrimination risk.",
            "outcome": "flagged",
            "metadata": {"rule_type": "ai_act_compliance", "amount": 0,
                         "regulation": "colorado_ai_act",
                         "violation_type": "missing_disclosure",
                         "analyst_verdict": "true_positive",
                         "fine_avoided_estimate": 50000},
        },
        {
            "input": "Transaction: International wire $200,000 from Smith & Associates "
                     "(law firm) to escrow account in London. Labeled as real estate "
                     "closing. Smith & Associates is a 30-year client. Transaction is "
                     "consistent with their practice area.",
            "output": "FLAGGED: Large international wire to foreign account.",
            "outcome": "false_positive",
            "metadata": {"rule_type": "large_international", "amount": 200000,
                         "regulation": "BSA/AML", "entity_age_months": 360,
                         "pattern": "law_firm_escrow",
                         "analyst_time_wasted_minutes": 25},
        },
        {
            "input": "Activity: Customer attempted to send money to an entity on OFAC SDN "
                     "list. Transfer of $15,000 to 'Al-Rashid Trading Company' which "
                     "matches OFAC Specially Designated Nationals list entry.",
            "output": "BLOCKED and FLAGGED: OFAC SDN list match. Transaction blocked. "
                      "Immediate SAR filing required. Customer account frozen pending review.",
            "outcome": "flagged",
            "metadata": {"rule_type": "sanctions_screening", "amount": 15000,
                         "regulation": "OFAC", "list_match": "SDN",
                         "analyst_verdict": "true_positive",
                         "fine_avoided_estimate": 1000000},
        },
        {
            "input": "Transaction: Monthly pension payment $3,200 from RetireWell Fund "
                     "to 85-year-old beneficiary. Same amount for 7 years.",
            "output": "FLAGGED: Transaction from investment fund to individual.",
            "outcome": "false_positive",
            "metadata": {"rule_type": "fund_to_individual", "amount": 3200,
                         "regulation": "BSA/AML", "pattern": "regular_pension",
                         "entity_age_months": 84,
                         "analyst_time_wasted_minutes": 10},
        },
    ]

    true_positives = 0
    false_positives = 0
    for s in screenings:
        run = loops.track(**s)
        m = s["metadata"]
        if s["outcome"] == "flagged":
            true_positives += 1
        elif s["outcome"] == "false_positive":
            false_positives += 1
        icon = {"flagged": "FLG", "false_positive": "F/P", "cleared": "CLR"}
        fine = m.get("fine_avoided_estimate", 0)
        print(f"  [{icon.get(s['outcome'], '???'):3s}] {m['rule_type']:28s} "
              f"| ${m['amount']:>10,} | {m['regulation']:15s} "
              f"| {'$' + f'{fine:,}' if fine else 'wasted ' + str(m.get('analyst_time_wasted_minutes', 0)) + 'min'}")

    total = len(screenings)
    precision = true_positives / (true_positives + false_positives)
    print(f"\n  Precision: {precision:.0%} (target: >80%)")
    print(f"  False positive rate: {false_positives/total:.0%}")

    # -------------------------------------------------------------------
    # Phase 2: Rules to reduce false positives while keeping true positives.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF transaction is international wire AND entity is >5 years old AND "
            "same recipient for >12 months THEN auto-clear — because recurring "
            "supplier payments and law firm escrows from established entities are "
            "always false positives",
            ["Johnson Manufacturing: 15yr customer, 3yr recurring payment = false positive",
             "Smith & Associates: 30yr client, regular escrow = false positive"],
            0.92,
        ),
        (
            "IF transaction is payroll batch AND amount within 10% of trailing "
            "12-month average AND entity age > 2 years THEN auto-clear — because "
            "regular payroll from established companies is never suspicious",
            ["TechCorp: 5yr customer, consistent $850K monthly payroll = false positive"],
            0.95,
        ),
        (
            "IF transaction is pension/retirement payment AND same amount for >6 months "
            "THEN auto-clear — because recurring pension payments are definitionally "
            "not suspicious activity",
            ["RetireWell Fund: 7yr recurring $3,200 pension = false positive"],
            0.98,
        ),
        (
            "IF amount is just below reporting threshold ($10K CTR or $50K wire) AND "
            "entity is < 6 months old AND multiple similar transactions in 7 days "
            "THEN escalate as high-priority structuring — because this pattern was "
            "confirmed as true positive in 100% of cases",
            ["Acme LLC: $49.5K x3 in one week, 2-month-old entity"],
            0.95,
        ),
        (
            "IF jurisdiction is Colorado AND decision involves AI model THEN apply "
            "Colorado AI Act (SB 21-169) criteria: check for consumer disclosure, "
            "check for proxy discrimination in features — because this is a new "
            "regulation with strict penalties",
            ["Lending model in CO: missing disclosure, zip code proxy risk"],
            0.90,
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
        ("Entity age and transaction history are the strongest signals for auto-clearing. "
         "Established entities with consistent patterns should not generate alerts.",
         "derived from false positive analysis — 100% of FPs were established entities"),
        ("New regulations (Colorado AI Act, EU AI Act) require proactive monitoring rules. "
         "When a new regulation takes effect, add specific screening criteria immediately.",
         "derived from Colorado AI Act compliance flag"),
        ("OFAC/sanctions matches are always highest priority — block first, analyze second. "
         "No auto-clear rules should ever apply to sanctions screening.",
         "derived from SDN list match protocol"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are a regulatory compliance monitoring agent. Screen transactions "
            "and activities for BSA/AML, OFAC sanctions, and emerging AI regulations. "
            "Minimize false positives without missing true violations.")
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
    total_fines_avoided = sum(s["metadata"].get("fine_avoided_estimate", 0)
                              for s in screenings)
    total_time_wasted = sum(s["metadata"].get("analyst_time_wasted_minutes", 0)
                            for s in screenings)
    print(f"  Transactions screened: {total}")
    print(f"  True positives: {true_positives} | False positives: {false_positives}")
    print(f"  Precision: {precision:.0%}")
    print(f"  Fines avoided: ${total_fines_avoided:,}")
    print(f"  Analyst time wasted on FPs: {total_time_wasted} min")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"  With learned auto-clear rules, {false_positives} FPs would be eliminated")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
