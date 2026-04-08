"""
AgentLoops Example: E-Commerce Product Recommendation Agent
Industry: E-Commerce / Retail
Use Case: AI recommendation engine that learns seasonal patterns, cross-sell opportunities,
and which recommendations lead to returns (negative signal).
Expected ROI: Direct ROI measurable in conversion lift. Typical: 15-35% increase in
average order value. Learning loops prevent stale recommendations (e.g., pushing winter
coats in April) that erode customer trust.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_ecommerce_")
    loops = AgentLoops("product-recommender", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: E-Commerce Product Recommendation Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track product recommendation outcomes.
    # Each run = one recommendation the agent served + what happened.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking recommendation outcomes ---\n")

    recommendations = [
        {
            "input": "Customer: C-1001. Just purchased: Nike Air Zoom Pegasus 40 "
                     "(running shoes, $130). Profile: runner, 28F, past purchases include "
                     "running shorts and sports bra. Season: March.",
            "output": "Recommended: (1) Garmin Forerunner 55 ($200), "
                      "(2) Nathan hydration vest ($35), (3) Body Glide anti-chafe ($10)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "active_runner", "month": "march",
                         "purchased_item": "Body Glide anti-chafe",
                         "rec_category": "running_accessories",
                         "aov_impact": 10, "click_position": 3},
        },
        {
            "input": "Customer: C-1002. Just purchased: MacBook Pro 16\" M3 ($2499). "
                     "Profile: software developer, 35M. Season: March.",
            "output": "Recommended: (1) Magic Mouse ($99), (2) USB-C hub ($45), "
                      "(3) Laptop stand ($60)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "tech_professional", "month": "march",
                         "purchased_item": "USB-C hub",
                         "rec_category": "tech_accessories",
                         "aov_impact": 45, "click_position": 2},
        },
        {
            "input": "Customer: C-1003. Just purchased: Running shoes (Nike Pegasus). "
                     "Profile: new customer, no history. Season: March.",
            "output": "Recommended: (1) Winter running jacket ($180), "
                      "(2) Wool running socks ($25), (3) Ice cleats ($30)",
            "outcome": "cart_abandoned",
            "metadata": {"customer_segment": "new_runner", "month": "march",
                         "rec_category": "winter_running",
                         "aov_impact": 0, "abandon_reason": "seasonal_mismatch"},
        },
        {
            "input": "Customer: C-1004. Just purchased: Yoga mat ($35). "
                     "Profile: 32F, bought running shoes 2 months ago. Season: March.",
            "output": "Recommended: (1) GU energy gels 24-pack ($30), "
                      "(2) Foam roller ($25), (3) Yoga blocks set ($15)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "cross_sport", "month": "march",
                         "purchased_items": ["Foam roller", "Yoga blocks set"],
                         "rec_category": "recovery_yoga",
                         "aov_impact": 40, "click_position": 2},
        },
        {
            "input": "Customer: C-1005. Browsing: Men's dress shirts. "
                     "Profile: 40M, corporate buyer, past purchases: suits, ties. "
                     "Season: April.",
            "output": "Recommended: (1) Matching silk tie ($65), "
                      "(2) Cufflinks set ($45), (3) Leather belt ($80)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "corporate", "month": "april",
                         "purchased_item": "Matching silk tie",
                         "rec_category": "formal_accessories",
                         "aov_impact": 65, "click_position": 1},
        },
        {
            "input": "Customer: C-1001 (returning). Purchased running shoes in March. "
                     "Now browsing in April. Profile: runner, 28F. Season: April.",
            "output": "Recommended: (1) Spring running shorts ($55), "
                      "(2) Nuun electrolyte tablets ($25), "
                      "(3) Running sunglasses ($120)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "active_runner", "month": "april",
                         "purchased_item": "Nuun electrolyte tablets",
                         "rec_category": "nutrition",
                         "aov_impact": 25, "click_position": 2,
                         "returning_customer": True},
        },
        {
            "input": "Customer: C-1006. Just purchased: Instant Pot ($90). "
                     "Profile: new customer. Season: April.",
            "output": "Recommended: (1) Instant Pot cookbook ($20), "
                      "(2) Extra sealing ring set ($12), (3) Steamer basket ($15)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "home_cook", "month": "april",
                         "purchased_item": "Instant Pot cookbook",
                         "rec_category": "complementary_product",
                         "aov_impact": 20, "click_position": 1},
        },
        {
            "input": "Customer: C-1007. Just purchased: iPhone 15 Pro ($1199). "
                     "Profile: 25M, past purchases: AirPods, Apple Watch. Season: April.",
            "output": "Recommended: (1) Spigen case ($15), "
                      "(2) Screen protector 3-pack ($12), (3) MagSafe charger ($39)",
            "outcome": "purchased",
            "metadata": {"customer_segment": "apple_ecosystem", "month": "april",
                         "purchased_items": ["Spigen case", "Screen protector 3-pack",
                                              "MagSafe charger"],
                         "rec_category": "phone_accessories",
                         "aov_impact": 66, "click_position": 1},
        },
        {
            "input": "Customer: C-1008. Just purchased: Running shoes (Hoka Clifton 9). "
                     "Profile: 45M, casual jogger. Season: April.",
            "output": "Recommended: (1) Garmin Fenix 7X ($800), "
                      "(2) Carbon fiber insoles ($60), (3) Compression socks ($35)",
            "outcome": "returned",
            "metadata": {"customer_segment": "casual_jogger", "month": "april",
                         "purchased_item": "Carbon fiber insoles",
                         "returned_item": "Carbon fiber insoles",
                         "return_reason": "Too advanced for casual jogging — "
                         "customer felt upsold on a product they didn't need",
                         "rec_category": "running_performance",
                         "aov_impact": -60},
        },
    ]

    for r in recommendations:
        run = loops.track(**r)
        m = r["metadata"]
        icon = {"purchased": "BUY", "clicked": "CLK",
                "cart_abandoned": "ABN", "returned": "RET"}
        aov = m["aov_impact"]
        print(f"  [{icon.get(r['outcome'], '???'):3s}] {m.get('customer_segment', 'unknown'):18s} "
              f"| {m['rec_category']:22s} | AOV: ${aov:>+4d} | {r['outcome']}")

    # -------------------------------------------------------------------
    # Phase 2: Rules from recommendation outcomes.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF customer bought running shoes in March THEN suggest nutrition/hydration "
            "products in April, NOT winter gear — because winter running recs in March "
            "caused cart abandonment, but April nutrition recs converted",
            ["C-1003 abandoned cart: winter jacket rec in March",
             "C-1001 purchased: electrolyte tablets in April"],
            0.92,
        ),
        (
            "IF customer segment is casual jogger THEN recommend entry-level accessories "
            "(<$40), NOT performance gear — because carbon fiber insoles were returned "
            "by a casual jogger who felt upsold",
            ["C-1008 returned carbon fiber insoles: 'too advanced for casual jogging'"],
            0.85,
        ),
        (
            "IF customer is in apple ecosystem (prior Apple purchases) AND just bought "
            "iPhone THEN recommend full accessory bundle — because Apple ecosystem "
            "customers buy 3+ accessories at once (C-1007 bought all 3 recs)",
            ["C-1007 purchased all 3 recommended items: case + protector + charger"],
            0.88,
        ),
        (
            "IF customer bought a kitchen appliance THEN recommend complementary "
            "consumables (cookbooks, replacement parts) in position 1 — because "
            "Instant Pot cookbook was clicked in position 1 immediately",
            ["C-1006 purchased cookbook from position 1"],
            0.80,
        ),
        (
            "IF recommendation leads to a return THEN deactivate that recommendation "
            "pattern for the customer segment — because returns destroy margin and "
            "customer trust simultaneously",
            ["C-1008 return: negative AOV impact of -$60"],
            0.95,
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
        ("Season-aware recommendations are mandatory. Never recommend winter products "
         "in spring or summer. Check the current month before generating any recs.",
         "derived from winter-jacket-in-March cart abandonment"),
        ("Match recommendation price tier to customer's purchase history. Casual "
         "buyers get sub-$40 recs. Performance buyers get premium recs.",
         "derived from casual jogger return"),
        ("Returns are the strongest negative signal. A returned recommendation "
         "should immediately suppress that pattern for the segment.",
         "derived from insole return analysis"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are a product recommendation engine. Suggest 3 relevant products "
            "after each purchase. Maximize add-to-cart rate while minimizing returns. "
            "Consider customer history, season, and price sensitivity.")
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
    purchased = sum(1 for r in recommendations if r["outcome"] == "purchased")
    returned = sum(1 for r in recommendations if r["outcome"] == "returned")
    abandoned = sum(1 for r in recommendations if r["outcome"] == "cart_abandoned")
    total = len(recommendations)
    total_aov = sum(r["metadata"]["aov_impact"] for r in recommendations)
    print(f"  Recommendations served: {total}")
    print(f"  Purchased: {purchased} ({purchased/total:.0%}) | "
          f"Abandoned: {abandoned} | Returned: {returned}")
    print(f"  Net AOV impact: ${total_aov:,}")
    print(f"  Avg AOV per successful rec: ${total_aov/purchased:.0f}")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
