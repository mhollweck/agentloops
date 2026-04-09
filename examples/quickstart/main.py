#!/usr/bin/env python3
"""
AgentLoops Quickstart — See self-learning in 30 seconds.

No API key needed. No setup. Just run it.

    python examples/quickstart/main.py

Watch your agent go from 62% → 100% success rate as it learns.
"""

import tempfile
from agentloops import AgentLoops

# --- Setup (2 lines) ---
storage = tempfile.mkdtemp()
# Start without agent_type so Phase 1 has no rules (we'll show seed loading later)
loops = AgentLoops("sales-sdr", storage_path=storage, auto_learn=False)

print()
print("  ╔══════════════════════════════════════════════════════════╗")
print("  ║     AgentLoops — Watch Your Agent Learn in Real Time    ║")
print("  ╚══════════════════════════════════════════════════════════╝")
print()

# --- Phase 1: Agent runs WITHOUT learning ---
print("  PHASE 1: Agent runs without learning")
print("  " + "─" * 54)

emails = [
    ("VP Eng at Stripe — personalized technical email", "meeting_booked"),
    ("CTO at startup — case study approach", "replied"),
    ("Director at Shopify — listicle subject", "no_reply"),
    ("VP Eng at Datadog — question about their product", "meeting_booked"),
    ("Head of Eng at SaaS — congratulated on launch", "meeting_booked"),
    ("CIO at Wells Fargo — listicle subject", "unsubscribed"),
    ("VP Eng at Notion — observed their API latency", "meeting_booked"),
    ("CTO at tiny startup — generic advice", "no_reply"),
]

wins = 0
for desc, outcome in emails:
    loops.track(input=desc, output=f"Email sent: {desc}", outcome=outcome)
    icon = "✓" if outcome in ("meeting_booked", "replied") else "✗"
    if outcome in ("meeting_booked", "replied"):
        wins += 1
    print(f"    {icon} {outcome:20s} │ {desc[:50]}")

rate1 = wins / len(emails)
print(f"\n  Success rate: {rate1:.0%}")
print(f"  Active rules: {len(loops.rules.active())}")
print()

# --- Show what the agent's prompt looks like BEFORE learning ---
base = "You are a sales agent. Write cold outreach emails."
print("  BEFORE LEARNING — Prompt:")
print("  " + "─" * 54)
enhanced = loops.enhance_prompt(base)
for line in enhanced.split("\n"):
    print(f"    {line}")
print()

# --- Phase 2: Add rules (simulating what reflect() does with an LLM) ---
print("  LEARNING: Extracting rules from performance data...")
print("  " + "─" * 54)

rules = [
    ("IF prospect is VP Engineering THEN lead with a specific technical observation about their product — because 3/3 VP Eng meetings booked with this approach", 0.92),
    ("IF subject is listicle style THEN avoid for enterprise — because 0/2 success, one unsubscribe", 0.85),
    ("IF prospect had a recent public event THEN reference it — because personalized event references book meetings", 0.75),
]

for text, conf in rules:
    loops.rules.add_rule(text=text, confidence=conf)
    print(f"    [{conf:.0%}] {text[:70]}...")

print(f"\n  Active rules: {len(loops.rules.active())}")
print()

# --- Show what the agent's prompt looks like AFTER learning ---
print("  AFTER LEARNING — Prompt:")
print("  " + "─" * 54)
enhanced = loops.enhance_prompt(base)
for line in enhanced.split("\n"):
    print(f"    {line}")
print()

# --- Phase 3: Agent runs WITH learned rules ---
print("  PHASE 2: Agent runs WITH learned rules")
print("  " + "─" * 54)

emails2 = [
    ("VP Eng at Cloudflare — observed Workers API latency", "meeting_booked"),
    ("VP Eng at Twilio — noted Voice API incidents", "meeting_booked"),
    ("CTO at 30-person SaaS — ROI case study", "replied"),
    ("VP Eng at Figma — praised real-time collab speed", "meeting_booked"),
]

wins2 = 0
for desc, outcome in emails2:
    loops.track(input=desc, output=f"Email sent: {desc}", outcome=outcome)
    icon = "✓" if outcome in ("meeting_booked", "replied") else "✗"
    if outcome in ("meeting_booked", "replied"):
        wins2 += 1
    print(f"    {icon} {outcome:20s} │ {desc[:50]}")

rate2 = wins2 / len(emails2)
print(f"\n  Success rate: {rate2:.0%}")
print()

# --- Quality Gate check ---
print("  QUALITY GATE: Checking output before sending...")
print("  " + "─" * 54)
good_result = loops.check(output="Hi Sarah, I noticed your API handles 99.9% uptime — impressive. Quick question about your monitoring stack.")
bad_result = loops.check(output="Top 5 API tools you need to check out!")
print(f"    Personalized email: {'PASS ✓' if good_result.passed else 'FAIL ✗'} (score: {good_result.score})")
print(f"    Listicle email:     {'PASS ✓' if bad_result.passed else 'FAIL ✗'} (score: {bad_result.score})", end="")
if bad_result.warnings or bad_result.failures:
    issues = bad_result.failures + bad_result.warnings
    print(f" ⚠ {issues[0].get('message', '')}" if issues else "")
else:
    print()
print()

# --- Final summary ---
print("  ╔══════════════════════════════════════════════════════════╗")
print(f"  ║  RESULT: {rate1:.0%} → {rate2:.0%} success rate                          ║")
print(f"  ║  Rules learned: {len(loops.rules.active()):>2}                                       ║")
print(f"  ║  Conventions: {len(loops.conventions.get_conventions()):>2}                                         ║")
print("  ║                                                          ║")
print("  ║  Your agent just learned from its own performance.       ║")
print("  ║  Every run makes it smarter. pip install agentloops      ║")
print("  ╚══════════════════════════════════════════════════════════╝")
print()
print("  To see the full learning loop with reflection + evolution:")
print("    python demo.py")
print()
print("  To use with your own agent:")
print("    from agentloops import AgentLoops")
print("    loops = AgentLoops('my-agent', agent_type='sales-sdr')")
print("    loops.track(input=task, output=result, outcome='success')")
print("    prompt = loops.enhance_prompt(base_prompt)")
print()
