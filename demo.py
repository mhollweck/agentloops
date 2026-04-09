#!/usr/bin/env python3
"""
AgentLoops Live Demo — See self-learning in action.

This demo runs a simulated sales agent through 3 learning cycles,
showing how rules emerge, prompts improve, and performance correlates.

Two modes:
  1. MOCK MODE (default): No API key needed, simulates LLM responses
  2. LIVE MODE: Set ANTHROPIC_API_KEY to use real Claude reflection

Usage:
    python demo.py              # Mock mode — instant, no API key
    python demo.py --live       # Live mode — uses Claude for reflection
"""

from __future__ import annotations

import json
import sys
import tempfile

from agentloops import AgentLoops


# ---------------------------------------------------------------------------
# Mock LLM responses for testing without an API key
# ---------------------------------------------------------------------------

MOCK_REFLECTION_RESPONSES = [
    # Cycle 1: After first batch of emails
    {
        "critique": (
            "Clear pattern: personalized, technical observations convert VP Engineering "
            "prospects at a high rate (3/3 booked). Listicle-style subjects consistently "
            "fail with enterprise contacts (0/2, one unsubscribe). Startup outreach with "
            "ROI framing shows promise but sample size is small."
        ),
        "suggested_rules": [
            "IF prospect is VP Engineering THEN lead with a specific technical observation about their product — because 3/3 VP Eng meetings booked with this approach",
            "IF subject style is listicle AND prospect is enterprise THEN avoid — because 0/2 success rate plus one unsubscribe",
            "IF prospect recently had a public event THEN reference it in the first line — because personalized event references booked meetings",
        ],
        "confidence_scores": {
            "IF prospect is VP Engineering THEN lead with a specific technical observation about their product — because 3/3 VP Eng meetings booked with this approach": 0.92,
            "IF subject style is listicle AND prospect is enterprise THEN avoid — because 0/2 success rate plus one unsubscribe": 0.85,
            "IF prospect recently had a public event THEN reference it in the first line — because personalized event references booked meetings": 0.70,
        },
        "rules_to_reconsider": [],
    },
    # Cycle 2: After applying rules and seeing improvement
    {
        "critique": (
            "Rules from cycle 1 are working. VP Engineering approach is now 5/5. "
            "New pattern emerging: mentioning a mutual connection or shared experience "
            "increases reply rate across all segments. The startup segment needs more data "
            "but the case-study approach seems solid for <50 person companies."
        ),
        "suggested_rules": [
            "IF you can find a mutual connection THEN mention it in the first sentence — because shared context doubled reply rates in cycle 2",
            "IF prospect company has <50 employees THEN lead with ROI numbers from similar-stage companies — because startups respond to concrete savings more than features",
        ],
        "confidence_scores": {
            "IF you can find a mutual connection THEN mention it in the first sentence — because shared context doubled reply rates in cycle 2": 0.78,
            "IF prospect company has <50 employees THEN lead with ROI numbers from similar-stage companies — because startups respond to concrete savings more than features": 0.65,
        },
        "rules_to_reconsider": [],
    },
    # Cycle 3: Convention evolution
    {
        "critique": (
            "System is mature. 5 active rules, all validated. Booking rate improved from "
            "50% to 75% over 3 cycles. The VP Engineering rule and anti-listicle rule are "
            "the highest-impact learnings. Ready to codify these into conventions."
        ),
        "suggested_rules": [],
        "confidence_scores": {},
        "rules_to_reconsider": [],
    },
]

MOCK_EVOLUTION_RESPONSE = {
    "new_conventions": [
        {
            "text": "Always research the prospect's product and reference something specific — generic outreach fails consistently with technical leaders.",
            "source": "derived from VP Engineering rule (0.92 confidence, validated across 5 runs)",
        },
        {
            "text": "Never use listicle or content-marketing-style subjects for enterprise prospects — they pattern match to spam.",
            "source": "derived from anti-listicle rule (0.85 confidence, 0/2 success rate)",
        },
    ],
    "contradictions": [],
    "to_remove": [],
    "to_merge": [],
}

MOCK_RULE_GEN_RESPONSE = {
    "rules": [
        {
            "text": "IF prospect is in financial services THEN avoid casual tone — because the CIO at Wells Fargo unsubscribed after informal approach",
            "confidence": 0.72,
            "evidence": ["Robert Kim unsubscribed — too casual for financial services"],
        },
    ],
}

_mock_call_count = 0


def _mock_anthropic_create(**kwargs):
    """Mock the Anthropic API to return pre-built learning responses."""
    global _mock_call_count

    # Determine which response to return based on call order
    prompt = kwargs.get("messages", [{}])[0].get("content", "")

    if "convention evolution" in prompt.lower() or "Review the current conventions" in prompt:
        response_data = MOCK_EVOLUTION_RESPONSE
    elif "rule generation" in prompt.lower() or "discover IF/THEN" in prompt:
        response_data = MOCK_RULE_GEN_RESPONSE
    else:
        # Reflection prompt — cycle through responses
        idx = min(_mock_call_count, len(MOCK_REFLECTION_RESPONSES) - 1)
        response_data = MOCK_REFLECTION_RESPONSES[idx]
        _mock_call_count += 1

    # Build a mock response object matching Anthropic SDK structure
    class MockBlock:
        def __init__(self, text):
            self.text = text

    class MockMessage:
        def __init__(self, text):
            self.content = [MockBlock(text)]

    return MockMessage(json.dumps(response_data))


# ---------------------------------------------------------------------------
# Email data for 3 learning cycles
# ---------------------------------------------------------------------------

CYCLE_1_EMAILS = [
    {"input": "Prospect: Sarah Chen, VP Engineering at Stripe (2000 emp). Book demo for API monitoring.",
     "output": "Subject: 'Quick question about Stripe API reliability'\nBody: Hi Sarah, I noticed Stripe processes billions of API calls. We helped Plaid reduce errors by 40%...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "question"}},
    {"input": "Prospect: Jake Miller, CTO at 15-person fintech. Book demo for API monitoring.",
     "output": "Subject: 'How we saved Series A startups $50K in downtime'\nBody: Hey Jake, saw you just raised your Series A...",
     "outcome": "replied", "metadata": {"segment": "startup", "subject_style": "case_study"}},
    {"input": "Prospect: Lisa Park, Director of Platform at Shopify. Book demo for API monitoring.",
     "output": "Subject: '5 API monitoring tools compared'\nBody: Hi Lisa, I put together a comparison...",
     "outcome": "no_reply", "metadata": {"segment": "enterprise", "subject_style": "listicle"}},
    {"input": "Prospect: Tom Wright, VP Engineering at Datadog. Book demo for API monitoring.",
     "output": "Subject: 'Question about Datadog internal monitoring'\nBody: Hi Tom, curious — do you use your own product internally?",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "question"}},
    {"input": "Prospect: Amy Liu, Head of Eng at 50-person SaaS. Book demo for API monitoring.",
     "output": "Subject: 'Congrats on the Product Hunt launch!'\nBody: Hey Amy, saw your PH launch yesterday...",
     "outcome": "meeting_booked", "metadata": {"segment": "smb", "subject_style": "personalized_event"}},
    {"input": "Prospect: Robert Kim, CIO at Wells Fargo. Book demo for API monitoring.",
     "output": "Subject: '3 trends in financial API monitoring'\nBody: Dear Robert, Financial services are seeing 300% increase...",
     "outcome": "unsubscribed", "metadata": {"segment": "enterprise", "subject_style": "listicle"}},
    {"input": "Prospect: Nina Patel, VP Engineering at Notion. Book demo for API monitoring.",
     "output": "Subject: 'Noticed something about Notion public API'\nBody: Hi Nina, I was building with your API and noticed p99 spikes...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
    {"input": "Prospect: David Brown, CTO at 8-person startup. Book demo for API monitoring.",
     "output": "Subject: 'API monitoring best practices for early stage'\nBody: Hi David, Most pre-seed teams skip monitoring...",
     "outcome": "no_reply", "metadata": {"segment": "startup", "subject_style": "advice"}},
]

# Cycle 2: After learning rules, agent adjusts approach
CYCLE_2_EMAILS = [
    {"input": "Prospect: Maya Singh, VP Engineering at Cloudflare. Book demo for API monitoring.",
     "output": "Subject: 'Noticed your Workers API latency dropped 12% last month'\nBody: Hi Maya, I run synthetic monitors on major APIs...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
    {"input": "Prospect: Chris Lee, VP Engineering at Twilio. Book demo for API monitoring.",
     "output": "Subject: 'Your Programmable Voice API had 3 incidents this quarter'\nBody: Hi Chris, as someone who monitors APIs professionally...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
    {"input": "Prospect: Rachel Green, CTO at 30-person SaaS. Book demo for API monitoring.",
     "output": "Subject: 'How a similar-stage company saved $40K on downtime'\nBody: Hey Rachel, a team your size reduced P0 incidents by 60%...",
     "outcome": "replied", "metadata": {"segment": "smb", "subject_style": "case_study"}},
    {"input": "Prospect: James Wu, VP Engineering at Figma. Book demo for API monitoring.",
     "output": "Subject: 'Your real-time collab API is impressively fast — one question'\nBody: Hi James, I tested your API round-trip...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
]

# Cycle 3: Further refinement
CYCLE_3_EMAILS = [
    {"input": "Prospect: Elena Vasquez, VP Engineering at Square. Book demo for API monitoring.",
     "output": "Subject: 'Your payment API handles Black Friday better than most — noticed one gap'\nBody: Hi Elena, during BFCM I tracked...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
    {"input": "Prospect: Kevin Park, CTO at 25-person fintech. Book demo for API monitoring.",
     "output": "Subject: 'How a 20-person team cut API incidents 70%'\nBody: Hey Kevin, I know from our Series A portfolio that at your stage...",
     "outcome": "meeting_booked", "metadata": {"segment": "startup", "subject_style": "case_study"}},
    {"input": "Prospect: Lisa Chen, VP Engineering at Plaid. Book demo for API monitoring.",
     "output": "Subject: 'Your Bank Connection API error rate spiked Tuesday — saw why'\nBody: Hi Lisa, I was testing integrations and caught...",
     "outcome": "meeting_booked", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
    {"input": "Prospect: Andre Brown, Director of Infra at Coinbase. Book demo for API monitoring.",
     "output": "Subject: 'Noticed your Trading API p99 is 3x better than competitors'\nBody: Hi Andre, I benchmark exchange APIs weekly...",
     "outcome": "replied", "metadata": {"segment": "enterprise", "subject_style": "observation"}},
]


def _success(outcome: str) -> bool:
    return outcome in ("meeting_booked", "replied")


def _print_section(title: str):
    print(f"\n{'=' * 70}")
    print(f"  {title}")
    print(f"{'=' * 70}\n")


def _print_stats(emails: list[dict]):
    total = len(emails)
    wins = sum(1 for e in emails if _success(e["outcome"]))
    print(f"  Results: {wins}/{total} positive outcomes ({wins/total:.0%} success rate)")
    by_style = {}
    for e in emails:
        style = e["metadata"]["subject_style"]
        by_style.setdefault(style, {"total": 0, "wins": 0})
        by_style[style]["total"] += 1
        if _success(e["outcome"]):
            by_style[style]["wins"] += 1
    for style, stats in sorted(by_style.items()):
        print(f"    {style:25s} {stats['wins']}/{stats['total']}")


def _install_mocks(loops):
    """Patch _call_llm on all LLM-using components to avoid needing anthropic installed."""
    global _mock_call_count
    _mock_call_count = 0

    def mock_call_llm(prompt: str) -> dict:
        global _mock_call_count

        if "convention evolution" in prompt.lower() or "Review the current conventions" in prompt:
            return MOCK_EVOLUTION_RESPONSE
        elif "rule generation" in prompt.lower() or "discover IF/THEN" in prompt:
            return MOCK_RULE_GEN_RESPONSE
        else:
            idx = min(_mock_call_count, len(MOCK_REFLECTION_RESPONSES) - 1)
            response = MOCK_REFLECTION_RESPONSES[idx]
            _mock_call_count += 1
            return response

    loops._reflector._call_llm = mock_call_llm
    loops._rule_engine._call_llm = mock_call_llm
    loops._convention_store._call_llm = mock_call_llm


def run_demo(live_mode: bool = False):
    global _mock_call_count
    _mock_call_count = 0

    storage_dir = tempfile.mkdtemp(prefix="agentloops_demo_")

    _print_section("AgentLoops Live Demo — Self-Learning in Action")
    print(f"  Mode: {'LIVE (using Claude API)' if live_mode else 'MOCK (no API key needed)'}")
    print(f"  Storage: {storage_dir}")

    # Don't pass agent_type here — we'll show seed rules loading later
    loops = AgentLoops(
        "sales-sdr",
        storage_path=storage_dir,
        auto_learn=False,  # We'll trigger learning manually to show each step
    )

    if not live_mode:
        _install_mocks(loops)

    # -----------------------------------------------------------------------
    # CYCLE 1: Baseline — no learning, raw performance
    # -----------------------------------------------------------------------
    _print_section("CYCLE 1: Baseline — No Rules Yet")

    base_prompt = (
        "You are an AI SDR. Write cold outreach emails to book demos for our "
        "API monitoring product. Be concise, specific, and relevant."
    )
    print(f"  Base prompt: {base_prompt[:80]}...")
    print(f"  Enhanced prompt is IDENTICAL (no rules yet)\n")

    assert loops.enhance_prompt(base_prompt) == base_prompt, "Should be unchanged with no rules"

    for e in CYCLE_1_EMAILS:
        run = loops.track(**e)
        icon = "✓" if _success(e["outcome"]) else "✗"
        print(f"  {icon} {e['outcome']:20s} | {e['metadata']['segment']:10s} | {e['metadata']['subject_style']}")

    _print_stats(CYCLE_1_EMAILS)

    # -----------------------------------------------------------------------
    # LEARNING STEP 1: Reflect on cycle 1
    # -----------------------------------------------------------------------
    _print_section("LEARNING: Reflecting on Cycle 1...")

    reflection = loops.reflect(last_n=8)

    print(f"  Critique: {reflection.critique[:200]}...")
    print(f"\n  Suggested rules ({len(reflection.suggested_rules)}):")
    for rule_text in reflection.suggested_rules:
        print(f"    → {rule_text[:90]}...")

    # Generate rules from the reflection
    new_rules = loops.rules.generate_rules()

    print(f"\n  Rules generated: {len(new_rules)}")
    for rule in new_rules:
        print(f"    [{rule.confidence:.0%}] {rule.text[:80]}...")

    # Also manually add the reflection's suggested rules (in production, reflect() -> generate_rules() handles this)
    for rule_text in reflection.suggested_rules:
        conf = reflection.confidence_scores.get(rule_text, 0.6)
        loops.rules.add_rule(text=rule_text, confidence=conf)

    # -----------------------------------------------------------------------
    # CYCLE 2: Agent applies learned rules
    # -----------------------------------------------------------------------
    _print_section("CYCLE 2: Applying Learned Rules")

    enhanced = loops.enhance_prompt(base_prompt)
    print("  Enhanced prompt now includes:\n")
    # Show just the rules section
    for line in enhanced.split("\n"):
        if line.startswith("- IF") or line.startswith("## "):
            print(f"    {line}")
    print()

    for e in CYCLE_2_EMAILS:
        run = loops.track(**e)
        icon = "✓" if _success(e["outcome"]) else "✗"
        print(f"  {icon} {e['outcome']:20s} | {e['metadata']['segment']:10s} | {e['metadata']['subject_style']}")

    _print_stats(CYCLE_2_EMAILS)

    # -----------------------------------------------------------------------
    # LEARNING STEP 2: Reflect on cycle 2
    # -----------------------------------------------------------------------
    _print_section("LEARNING: Reflecting on Cycle 2...")

    reflection2 = loops.reflect(last_n=4)

    print(f"  Critique: {reflection2.critique[:200]}...")
    if reflection2.suggested_rules:
        print(f"\n  New rules suggested ({len(reflection2.suggested_rules)}):")
        for rule_text in reflection2.suggested_rules:
            conf = reflection2.confidence_scores.get(rule_text, 0.6)
            loops.rules.add_rule(text=rule_text, confidence=conf)
            print(f"    → [{conf:.0%}] {rule_text[:80]}...")

    # -----------------------------------------------------------------------
    # CYCLE 3: Further refinement
    # -----------------------------------------------------------------------
    _print_section("CYCLE 3: Refined Agent")

    enhanced = loops.enhance_prompt(base_prompt)
    rule_count = enhanced.count("- IF")
    print(f"  Active rules in prompt: {rule_count}\n")

    for e in CYCLE_3_EMAILS:
        run = loops.track(**e)
        icon = "✓" if _success(e["outcome"]) else "✗"
        print(f"  {icon} {e['outcome']:20s} | {e['metadata']['segment']:10s} | {e['metadata']['subject_style']}")

    _print_stats(CYCLE_3_EMAILS)

    # -----------------------------------------------------------------------
    # CONVENTION EVOLUTION: Promote rules to conventions
    # -----------------------------------------------------------------------
    _print_section("EVOLVING: Promoting Rules to Conventions...")

    changes = loops.conventions.evolve()

    if changes.get("new"):
        print(f"  New conventions ({len(changes['new'])}):")
        for conv in changes["new"]:
            print(f"    ★ {conv['text'][:80]}...")
    if changes.get("contradictions"):
        print(f"  Contradictions found: {len(changes['contradictions'])}")
    if changes.get("merged"):
        print(f"  Merged conventions: {len(changes['merged'])}")

    # -----------------------------------------------------------------------
    # FORGETTING: Prune stale patterns
    # -----------------------------------------------------------------------
    _print_section("FORGETTING: Pruning Stale Patterns...")

    pruned = loops.forget(strategy="hybrid", max_age_days=21)
    print(f"  Rules pruned: {len(pruned['rules_pruned'])}")
    print(f"  Conventions pruned: {len(pruned['conventions_pruned'])}")
    print("  (All entries are fresh — in production, stale low-confidence rules get cleaned up)")

    # -----------------------------------------------------------------------
    # PERFORMANCE SUMMARY
    # -----------------------------------------------------------------------
    _print_section("PERFORMANCE IMPROVEMENT")

    c1_rate = sum(1 for e in CYCLE_1_EMAILS if _success(e["outcome"])) / len(CYCLE_1_EMAILS)
    c2_rate = sum(1 for e in CYCLE_2_EMAILS if _success(e["outcome"])) / len(CYCLE_2_EMAILS)
    c3_rate = sum(1 for e in CYCLE_3_EMAILS if _success(e["outcome"])) / len(CYCLE_3_EMAILS)

    print(f"  Cycle 1 (no learning):  {c1_rate:.0%} success rate")
    print(f"  Cycle 2 (after rules):  {c2_rate:.0%} success rate")
    print(f"  Cycle 3 (refined):      {c3_rate:.0%} success rate")
    print(f"\n  Improvement: {c1_rate:.0%} → {c3_rate:.0%} ({(c3_rate-c1_rate)/c1_rate:+.0%} relative)")

    # Show improvement curve
    curve = loops.tracker.improvement_curve(metric="success_rate", window_days=1)
    if curve:
        print(f"\n  Improvement curve data points: {len(curve)}")

    # -----------------------------------------------------------------------
    # FINAL STATE
    # -----------------------------------------------------------------------
    _print_section("FINAL AGENT STATE")

    final_prompt = loops.enhance_prompt(base_prompt)
    print("  Full enhanced prompt:\n")
    for line in final_prompt.split("\n"):
        print(f"    {line}")

    print(f"\n  Total runs tracked: {len(loops.tracker.get_runs())}")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"  Active conventions: {len(loops.conventions.get_conventions())}")
    print(f"  Reflections: {len(loops._storage.get_reflections())}")

    # -----------------------------------------------------------------------
    # HOW TO USE IN PRODUCTION
    # -----------------------------------------------------------------------
    _print_section("HOW TO USE IN PRODUCTION")

    print("""  # 1. Install
  pip install agentloops

  # 2. Initialize (5 seconds)
  from agentloops import AgentLoops
  loops = AgentLoops("my-agent", agent_type="sales-sdr")

  # 3. Track every run
  loops.track(input=task, output=result, outcome="meeting_booked")

  # 4. Enhance your prompt (includes learned rules automatically)
  prompt = loops.enhance_prompt(base_system_prompt)

  # 5. Reflection + rule generation (call periodically or let auto_learn handle it)
  #    With auto_learn=True (default), this happens automatically after every 10 runs.
  #    Or call manually:
  reflection = loops.reflect(last_n=10)
  new_rules = loops.rules.generate_rules()
  changes = loops.conventions.evolve()

  # 6. Scheduling: Run learning on a schedule
  #    Option A: Cron job
  #    0 2 * * * cd /app && python -c "from agentloops import AgentLoops; \\
  #        l = AgentLoops('my-agent'); l.reflect(); l.rules.generate_rules(); \\
  #        l.conventions.evolve(); l.forget()"
  #
  #    Option B: In your agent's main loop
  #    loops = AgentLoops("my-agent", auto_learn=True, reflection_threshold=10)
  #    # Learning triggers automatically after every 10 runs
  #
  #    Option C: Background worker (e.g., Celery, APScheduler)
  #    @scheduler.scheduled_job('cron', hour=2)
  #    def nightly_learning():
  #        loops = AgentLoops("my-agent")
  #        loops.reflect(last_n=50)
  #        loops.rules.generate_rules()
  #        loops.conventions.evolve()
  #        loops.forget(strategy="hybrid")
""")

    print(f"  Demo storage directory: {storage_dir}")
    print(f"  Inspect the learned data:")
    print(f"    cat {storage_dir}/sales-sdr/rules.json | python -m json.tool")
    print(f"    cat {storage_dir}/sales-sdr/conventions.json | python -m json.tool")
    print(f"    wc -l {storage_dir}/sales-sdr/runs.jsonl")
    print()


if __name__ == "__main__":
    live = "--live" in sys.argv
    run_demo(live_mode=live)
