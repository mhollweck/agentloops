"""
AgentLoops Example: AI SDR / Sales Outreach
Industry: B2B SaaS Sales
Use Case: Cold email agent that learns which messaging converts for each prospect segment.
Expected ROI: 2-3x improvement in meeting booking rate within 30 days. Companies like 11x.ai
lose customers because their AI SDRs don't learn — this fixes the core retention problem.
"""

import os
import tempfile

from agentloops import AgentLoops


def main():
    # -------------------------------------------------------------------
    # Setup: Create an AgentLoops instance for our sales outreach agent.
    # We use a temp directory so this example is self-contained.
    # In production, you'd use the default ".agentloops" in your project.
    # -------------------------------------------------------------------
    storage_dir = tempfile.mkdtemp(prefix="agentloops_sales_")
    loops = AgentLoops("sales-sdr", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: AI SDR / Sales Outreach")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track cold email runs with realistic outcomes.
    # The agent sends outreach emails and we log what happened.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking cold email runs ---\n")

    email_runs = [
        {
            "input": "Prospect: Sarah Chen, VP Engineering at Stripe (2000 employees). "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: 'Quick question about Stripe's API reliability'\n"
                      "Body: Hi Sarah, I noticed Stripe processes billions of API calls. "
                      "We helped Plaid reduce API errors by 40%...",
            "outcome": "meeting_booked",
            "metadata": {"segment": "enterprise", "title": "VP Engineering",
                         "subject_style": "question", "company_size": 2000},
        },
        {
            "input": "Prospect: Jake Miller, CTO at a 15-person fintech startup. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: 'How we saved Series A startups $50K in downtime'\n"
                      "Body: Hey Jake, saw you just raised your Series A. "
                      "Most CTOs at your stage don't have monitoring until it's too late...",
            "outcome": "replied",
            "metadata": {"segment": "startup", "title": "CTO",
                         "subject_style": "case_study", "company_size": 15},
        },
        {
            "input": "Prospect: Lisa Park, Director of Platform at Shopify. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: '5 API monitoring tools compared'\n"
                      "Body: Hi Lisa, I put together a comparison of the top 5 API "
                      "monitoring solutions for platform teams...",
            "outcome": "no_reply",
            "metadata": {"segment": "enterprise", "title": "Director",
                         "subject_style": "listicle", "company_size": 5000},
        },
        {
            "input": "Prospect: Tom Wright, VP Engineering at Datadog. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: 'Question about Datadog's internal monitoring'\n"
                      "Body: Hi Tom, curious — do you use your own product internally "
                      "for API monitoring, or something separate?",
            "outcome": "meeting_booked",
            "metadata": {"segment": "enterprise", "title": "VP Engineering",
                         "subject_style": "question", "company_size": 3000},
        },
        {
            "input": "Prospect: Amy Liu, Head of Engineering at a 50-person B2B SaaS. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: 'Congrats on the Product Hunt launch!'\n"
                      "Body: Hey Amy, saw your PH launch yesterday — impressive traction. "
                      "When we were at that stage, API monitoring saved us from...",
            "outcome": "meeting_booked",
            "metadata": {"segment": "smb", "title": "Head of Engineering",
                         "subject_style": "personalized_event", "company_size": 50},
        },
        {
            "input": "Prospect: Robert Kim, CIO at Wells Fargo. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: '3 trends in financial API monitoring'\n"
                      "Body: Dear Robert, Financial services companies are seeing a 300% "
                      "increase in API call volume...",
            "outcome": "unsubscribed",
            "metadata": {"segment": "enterprise", "title": "CIO",
                         "subject_style": "listicle", "company_size": 50000},
        },
        {
            "input": "Prospect: Nina Patel, VP Engineering at Notion. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: 'Noticed something about Notion's public API'\n"
                      "Body: Hi Nina, I was building an integration with Notion's API "
                      "and noticed the p99 latency spikes around 2pm EST...",
            "outcome": "meeting_booked",
            "metadata": {"segment": "enterprise", "title": "VP Engineering",
                         "subject_style": "observation", "company_size": 1500},
        },
        {
            "input": "Prospect: David Brown, CTO at 8-person pre-seed startup. "
                     "Goal: Book a demo for our API monitoring tool.",
            "output": "Subject: 'API monitoring best practices for early stage'\n"
                      "Body: Hi David, Most pre-seed teams skip monitoring. "
                      "Here's why that's actually fine until Series A...",
            "outcome": "no_reply",
            "metadata": {"segment": "startup", "title": "CTO",
                         "subject_style": "advice", "company_size": 8},
        },
    ]

    for run_data in email_runs:
        run = loops.track(**run_data)
        status = "OK" if run_data["outcome"] in ("meeting_booked", "replied") else "MISS"
        print(f"  [{status}] {run_data['outcome']:20s} | {run_data['metadata']['segment']:10s} "
              f"| {run_data['metadata']['subject_style']}")

    # -------------------------------------------------------------------
    # Phase 2: Add rules manually (simulating what reflect() would produce).
    # In production, you'd call loops.reflect() which uses Claude to
    # analyze the runs and suggest these rules automatically.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules_to_add = [
        (
            "IF prospect is VP Engineering THEN lead with a specific technical "
            "observation about their product — because 3/3 VP Eng prospects booked "
            "meetings when we showed we used their product",
            ["run with Sarah Chen booked", "run with Tom Wright booked",
             "run with Nina Patel booked"],
            0.90,
        ),
        (
            "IF prospect is at an enterprise company AND subject style is listicle "
            "THEN avoid — because 0/2 listicle subjects got replies from enterprise "
            "prospects, and one unsubscribed",
            ["Lisa Park no_reply with listicle", "Robert Kim unsubscribed with listicle"],
            0.85,
        ),
        (
            "IF prospect is at a startup with <20 employees THEN use case study "
            "subject with ROI numbers — because Jake Miller replied to the Series A "
            "cost-saving angle",
            ["Jake Miller replied to case study approach"],
            0.60,
        ),
        (
            "IF prospect recently had a public event (launch, funding, award) THEN "
            "reference it in the first line — because Amy Liu booked after a "
            "personalized Product Hunt reference",
            ["Amy Liu meeting_booked after PH reference"],
            0.75,
        ),
    ]

    for text, evidence, confidence in rules_to_add:
        rule = loops.rules.add_rule(text=text, evidence=evidence, confidence=confidence)
        print(f"  Rule added (confidence {confidence:.0%}): {text[:80]}...")

    # -------------------------------------------------------------------
    # Phase 3: Add conventions (behavioral patterns the agent should follow).
    # Conventions are higher-level than rules — they shape overall behavior.
    # -------------------------------------------------------------------
    print("\n--- Phase 3: Adding conventions ---\n")

    conventions_to_add = [
        ("Always research the prospect's product before writing — generic outreach "
         "gets ignored by technical leaders.", "derived from VP Eng success pattern"),
        ("Never use listicle-style subjects for enterprise prospects — they pattern "
         "match to spam.", "derived from listicle failure pattern"),
        ("Follow up within 3 days if no reply, but only once. Two follow-ups "
         "without reply means move on.", "sales best practice"),
    ]

    for text, source in conventions_to_add:
        conv = loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhance a prompt with learned rules and conventions.
    # This is the magic — your agent's system prompt automatically includes
    # everything it has learned, so it gets smarter every day.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base_prompt = (
        "You are an AI SDR. Write cold outreach emails to book demos for our "
        "API monitoring product. Be concise, specific, and relevant."
    )
    enhanced = loops.enhance_prompt(base_prompt)
    print(enhanced)

    # -------------------------------------------------------------------
    # Phase 5: Forget stale rules.
    # In production, rules older than 21 days with low confidence get pruned.
    # This keeps the agent's memory fresh and prevents outdated patterns.
    # -------------------------------------------------------------------
    print("\n--- Phase 5: Memory pruning ---\n")

    # Since these rules were just created, nothing will be pruned.
    # In production, this runs daily to clean out stale patterns.
    pruned = loops.forget(strategy="hybrid", max_age_days=21)
    print(f"  Rules pruned: {len(pruned['rules_pruned'])}")
    print(f"  Conventions pruned: {len(pruned['conventions_pruned'])}")
    print("  (Nothing pruned — all entries are fresh. In production, stale rules")
    print("   with low confidence get automatically cleaned up after 21 days.)")

    # -------------------------------------------------------------------
    # Phase 6: Show the correlation — how rules affect outcomes.
    # This proves the ROI: rules that improve booking rates stay,
    # rules that don't get pruned.
    # -------------------------------------------------------------------
    print("\n--- Phase 6: Performance correlation ---\n")

    active_rules = loops.rules.active()
    print(f"  Active rules: {len(active_rules)}")
    for rule in active_rules:
        print(f"    [{rule.confidence:.0%}] {rule.text[:70]}...")

    # -------------------------------------------------------------------
    # Production usage: Call loops.reflect() after each batch of emails.
    # The LLM analyzes outcomes and generates rules automatically.
    #
    # Example (requires ANTHROPIC_API_KEY):
    #   reflection = loops.reflect(last_n=10)
    #   print(reflection.critique)
    #   new_rules = loops.rules.generate_rules()
    #   changes = loops.conventions.evolve()
    # -------------------------------------------------------------------
    print("\n--- Production Usage ---\n")
    print("  To enable automatic learning (requires ANTHROPIC_API_KEY):")
    print("    reflection = loops.reflect(last_n=10)")
    print("    new_rules = loops.rules.generate_rules()")
    print("    changes = loops.conventions.evolve()")
    print(f"\n  Storage directory: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
