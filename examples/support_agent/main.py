"""
AgentLoops Example: Customer Service Agent
Industry: SaaS / Enterprise Support
Use Case: AI support agent that learns resolution patterns per customer segment and issue type.
Expected ROI: Push first-contact resolution from 60% to 85%. Klarna saved $40M/year with AI
support — learning loops prevent the drift that causes re-escalation and customer churn.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_support_")
    loops = AgentLoops("support-agent", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: Customer Service Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track realistic support ticket interactions.
    # Each run is a ticket the agent handled, with its resolution outcome.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking support ticket runs ---\n")

    tickets = [
        {
            "input": "Ticket #4821: Enterprise customer (Acme Corp, $50K ARR) reports "
                     "'Unable to log in via SSO. Error: SAML assertion expired.' "
                     "Customer tier: Enterprise. Previous tickets: 3 SSO issues this month.",
            "output": "Checked SAML config — customer's IdP clock was 6 minutes ahead "
                      "of our server. Guided them to sync NTP on their IdP server. "
                      "Verified login worked after fix.",
            "outcome": "resolved",
            "metadata": {"category": "sso", "tier": "enterprise", "csat_score": 5,
                         "resolution_minutes": 12, "first_contact": True},
        },
        {
            "input": "Ticket #4822: Free tier user says 'I forgot my password and the "
                     "reset email never arrives.' Email: user@gmail.com",
            "output": "Triggered password reset. Email was in spam folder. "
                      "Advised customer to check spam and whitelist noreply@ourapp.com.",
            "outcome": "resolved",
            "metadata": {"category": "password_reset", "tier": "free", "csat_score": 4,
                         "resolution_minutes": 3, "first_contact": True},
        },
        {
            "input": "Ticket #4823: Enterprise customer (GlobalBank, $200K ARR) reports "
                     "'SSO login works but user is assigned wrong role after SAML assertion. "
                     "Expected admin, got viewer.' Using Okta as IdP.",
            "output": "Suggested checking attribute mapping in Okta. Provided our "
                      "expected SAML attribute names. Customer says mapping looks correct.",
            "outcome": "escalated",
            "metadata": {"category": "sso", "tier": "enterprise", "csat_score": 3,
                         "resolution_minutes": 45, "first_contact": False},
        },
        {
            "input": "Ticket #4824: Pro tier customer says 'API returns 429 Too Many "
                     "Requests but I'm well under my rate limit of 1000/min.'",
            "output": "Checked rate limiter — customer was hitting per-endpoint limits "
                      "(100/min on /search), not the global limit. Explained the "
                      "per-endpoint limits and suggested batching.",
            "outcome": "resolved",
            "metadata": {"category": "api_rate_limit", "tier": "pro", "csat_score": 5,
                         "resolution_minutes": 8, "first_contact": True},
        },
        {
            "input": "Ticket #4825: Enterprise customer (MegaCorp, $120K ARR) reports "
                     "'Users can log in via SSO but session expires after 5 minutes instead "
                     "of our configured 8 hours.' Using Azure AD.",
            "output": "Checked session config — our side shows 8h session length. "
                      "Suggested it might be Azure AD conditional access policy overriding "
                      "session length. Customer confirmed that was the issue.",
            "outcome": "resolved",
            "metadata": {"category": "sso", "tier": "enterprise", "csat_score": 5,
                         "resolution_minutes": 20, "first_contact": True},
        },
        {
            "input": "Ticket #4826: Free tier user says 'I can't upload files larger "
                     "than 5MB. Your docs say 10MB limit.'",
            "output": "Free tier limit is 5MB. Pro tier is 10MB. Docs were showing "
                      "Pro limits on the free tier page. Fixed the docs, apologized, "
                      "offered 7-day Pro trial.",
            "outcome": "resolved",
            "metadata": {"category": "upload_limit", "tier": "free", "csat_score": 4,
                         "resolution_minutes": 5, "first_contact": True},
        },
        {
            "input": "Ticket #4827: Enterprise customer (TechStartup, $30K ARR) reports "
                     "'SCIM provisioning creates duplicate users when syncing from Okta. "
                     "We now have 200 duplicate accounts.'",
            "output": "Attempted to deduplicate via API. Script merged 50 accounts "
                      "but 150 had conflicting data. Need engineering team to write "
                      "a migration script.",
            "outcome": "escalated",
            "metadata": {"category": "scim", "tier": "enterprise", "csat_score": 2,
                         "resolution_minutes": 90, "first_contact": False},
        },
        {
            "input": "Ticket #4828: Pro customer says 'Webhook deliveries stopped "
                     "working 2 hours ago. No errors in our logs.'",
            "output": "Checked webhook delivery logs — customer's endpoint started "
                      "returning 503. Their server was down. Notified customer and "
                      "offered to replay failed webhooks once server is back.",
            "outcome": "resolved",
            "metadata": {"category": "webhooks", "tier": "pro", "csat_score": 5,
                         "resolution_minutes": 10, "first_contact": True},
        },
        {
            "input": "Ticket #4829: Enterprise customer reopens Ticket #4823 (GlobalBank). "
                     "'Engineering fixed the SAML mapping but now ALL users get admin role "
                     "instead of their correct roles.'",
            "output": "Reviewed SAML config again. Found that the role attribute was "
                      "mapped to a hardcoded value instead of the group claim. Provided "
                      "correct Okta expression: appuser.groups.",
            "outcome": "reopened",
            "metadata": {"category": "sso", "tier": "enterprise", "csat_score": 2,
                         "resolution_minutes": 60, "first_contact": False,
                         "original_ticket": "4823"},
        },
    ]

    resolved = 0
    total = 0
    for t in tickets:
        run = loops.track(**t)
        total += 1
        if t["outcome"] == "resolved":
            resolved += 1
        icon = {"resolved": "OK", "escalated": "ESC", "reopened": "RE"}
        print(f"  [{icon.get(t['outcome'], '??'):3s}] #{t['input'][8:12]} "
              f"| {t['metadata']['category']:18s} | {t['metadata']['tier']:10s} "
              f"| CSAT {t['metadata']['csat_score']}/5")

    print(f"\n  Resolution rate: {resolved}/{total} ({resolved/total:.0%})")

    # -------------------------------------------------------------------
    # Phase 2: Rules learned from ticket patterns.
    # The agent discovers that SSO issues for enterprise need different
    # handling than generic password resets.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF customer is enterprise AND issue mentions SSO/SAML AND uses Okta "
            "THEN check attribute mapping first, not clock sync — because 2/3 "
            "Okta SSO escalations were caused by attribute mapping errors",
            ["Ticket #4823 escalated due to wrong attribute mapping",
             "Ticket #4829 reopened — same root cause"],
            0.85,
        ),
        (
            "IF customer is enterprise AND issue is SCIM provisioning THEN "
            "escalate to engineering immediately — because SCIM dedup requires "
            "migration scripts that support agents cannot write",
            ["Ticket #4827 took 90 min and still required engineering"],
            0.90,
        ),
        (
            "IF issue is password reset AND tier is free THEN check spam folder "
            "first — because 80% of password reset issues are spam filter problems",
            ["Ticket #4822 resolved in 3 min by checking spam"],
            0.75,
        ),
        (
            "IF issue is API rate limit AND customer mentions global limit THEN "
            "explain per-endpoint limits — because customers confuse global vs "
            "per-endpoint rate limits 90% of the time",
            ["Ticket #4824 resolved by explaining per-endpoint limits"],
            0.80,
        ),
    ]

    for text, evidence, confidence in rules:
        loops.rules.add_rule(text=text, evidence=evidence, confidence=confidence)
        print(f"  Rule ({confidence:.0%}): {text[:75]}...")

    # -------------------------------------------------------------------
    # Phase 3: Conventions — higher-level support behaviors.
    # -------------------------------------------------------------------
    print("\n--- Phase 3: Adding conventions ---\n")

    conventions = [
        ("For enterprise SSO tickets, always ask for the IdP vendor (Okta, Azure AD, "
         "OneLogin) in the first response — different IdPs have different failure modes.",
         "derived from SSO ticket patterns"),
        ("Never attempt bulk data operations (dedup, migration) via the support agent — "
         "escalate to engineering with a clear description of the data state.",
         "derived from SCIM escalation"),
        ("Always check previous tickets for the same customer before responding — "
         "reopened tickets destroy CSAT scores.",
         "derived from GlobalBank reopened ticket pattern"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt — the agent gets smarter.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base_prompt = (
        "You are a customer support agent for a SaaS platform. Resolve tickets "
        "efficiently. Prioritize enterprise customers. Always be empathetic."
    )
    enhanced = loops.enhance_prompt(base_prompt)
    # Show just the rules section for brevity
    lines = enhanced.split("\n")
    for line in lines:
        if line.strip():
            print(f"  {line}")

    # -------------------------------------------------------------------
    # Phase 5: Forgetting stale patterns.
    # -------------------------------------------------------------------
    print("\n--- Phase 5: Memory pruning ---\n")

    pruned = loops.forget(strategy="hybrid", max_age_days=21)
    print(f"  Rules pruned: {len(pruned['rules_pruned'])}")
    print(f"  Conventions pruned: {len(pruned['conventions_pruned'])}")

    # -------------------------------------------------------------------
    # Phase 6: Improvement tracking.
    # -------------------------------------------------------------------
    print("\n--- Phase 6: Improvement metrics ---\n")

    active_rules = loops.rules.active()
    print(f"  Active rules: {len(active_rules)}")
    print(f"  Total runs tracked: {total}")
    print(f"  First-contact resolution: {resolved}/{total} ({resolved/total:.0%})")
    print(f"  Average CSAT: {sum(t['metadata']['csat_score'] for t in tickets)/len(tickets):.1f}/5")

    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
