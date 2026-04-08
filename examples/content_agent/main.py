"""
AgentLoops Example: Content Creator / Marketing Agent
Industry: Creator Economy / Digital Marketing
Use Case: AI content agent that learns which hooks, formats, and topics drive engagement.
Expected ROI: 2-5x engagement improvement within 4 weeks. Creators running AI content
pipelines need agents that learn what resonates — not just generate content blindly.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_content_")
    loops = AgentLoops("content-agent", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: Content Creator / Marketing Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track social media post performance.
    # Each run = one post the agent wrote, with real engagement metrics.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking content performance ---\n")

    posts = [
        {
            "input": "Write a TikTok script about Claude Code for developers. "
                     "Target audience: indie devs and solopreneurs.",
            "output": "Hook: 'I replaced my entire engineering team with one CLI tool.'\n"
                      "Body: Shows building a full-stack app in 10 minutes with Claude Code. "
                      "Ends with 'The craziest part? It costs $20/month.'",
            "outcome": "success",  # Use success/failure based on threshold
            "metadata": {"views": 245000, "engagement_rate": 8.2, "shares": 3400,
                         "saves": 12000, "hook_type": "bold_claim",
                         "topic": "ai_tools", "platform": "tiktok",
                         "posted_hour": 9},
        },
        {
            "input": "Write a TikTok script about 5 AI tools for productivity.",
            "output": "Hook: '5 AI tools that will 10x your productivity'\n"
                      "Body: Lists ChatGPT, Claude, Cursor, v0, Midjourney with "
                      "one-sentence descriptions of each.",
            "outcome": "failure",
            "metadata": {"views": 12000, "engagement_rate": 1.1, "shares": 50,
                         "saves": 200, "hook_type": "listicle",
                         "topic": "ai_tools", "platform": "tiktok",
                         "posted_hour": 14},
        },
        {
            "input": "Write a TikTok about quitting FAANG to go solo with AI.",
            "output": "Hook: 'I left my $400K job because AI made me unemployable... "
                      "at a company.'\n"
                      "Body: Talks about how AI enables solo builders to compete with "
                      "teams of 10. Shows revenue dashboard.",
            "outcome": "success",
            "metadata": {"views": 890000, "engagement_rate": 12.5, "shares": 15000,
                         "saves": 45000, "hook_type": "curiosity_gap",
                         "topic": "career", "platform": "tiktok",
                         "posted_hour": 8},
        },
        {
            "input": "Write a YouTube thumbnail text and title about building an app "
                     "with AI in one day.",
            "output": "Title: 'I Built a $10K/Month App in 24 Hours (with AI)'\n"
                      "Thumbnail text: '$10K/mo app' with shocked face + code on screen",
            "outcome": "success",
            "metadata": {"views": 56000, "engagement_rate": 6.8, "shares": 800,
                         "saves": 2200, "hook_type": "outcome_reveal",
                         "topic": "ai_tools", "platform": "youtube",
                         "posted_hour": 10},
        },
        {
            "input": "Write a TikTok about the best AI coding assistant.",
            "output": "Hook: 'Stop using Copilot. Here's what I switched to.'\n"
                      "Body: Compares Copilot, Cursor, Claude Code. Shows real code "
                      "generation side by side. Conclusion: Claude Code wins.",
            "outcome": "success",
            "metadata": {"views": 320000, "engagement_rate": 9.1, "shares": 5600,
                         "saves": 18000, "hook_type": "contrarian",
                         "topic": "ai_tools", "platform": "tiktok",
                         "posted_hour": 8},
        },
        {
            "input": "Write a Substack post about AI agent architecture.",
            "output": "Title: 'How I Built a Self-Learning Agent System'\n"
                      "Body: 2000-word technical deep dive on reflection loops, "
                      "rule engines, and convention stores.",
            "outcome": "success",
            "metadata": {"views": 4500, "engagement_rate": 15.0, "shares": 600,
                         "saves": 900, "hook_type": "technical_deep_dive",
                         "topic": "ai_tools", "platform": "substack",
                         "posted_hour": 7},
        },
        {
            "input": "Write a TikTok tutorial on setting up a Next.js project.",
            "output": "Hook: 'How to set up Next.js in 2024'\n"
                      "Body: Step-by-step tutorial. npx create-next-app, folder structure, "
                      "basic routing. Very educational, no personality.",
            "outcome": "failure",
            "metadata": {"views": 8000, "engagement_rate": 0.8, "shares": 20,
                         "saves": 150, "hook_type": "tutorial",
                         "topic": "web_dev", "platform": "tiktok",
                         "posted_hour": 15},
        },
        {
            "input": "Write a TikTok about what happened when AI wrote my app's code.",
            "output": "Hook: 'AI wrote 100% of my app's code. Here's what happened "
                      "after 10,000 users.'\n"
                      "Body: Story format — launched app, bugs appeared, AI fixed them, "
                      "revenue grew. Punchline: 'Zero human-written lines of code.'",
            "outcome": "success",
            "metadata": {"views": 510000, "engagement_rate": 10.3, "shares": 8900,
                         "saves": 28000, "hook_type": "story_outcome",
                         "topic": "ai_tools", "platform": "tiktok",
                         "posted_hour": 9},
        },
    ]

    for p in posts:
        run = loops.track(**p)
        m = p["metadata"]
        status = "HIT" if p["outcome"] == "success" else "MISS"
        print(f"  [{status}] {m['views']:>8,} views | {m['engagement_rate']:5.1f}% eng "
              f"| {m['hook_type']:20s} | {m['platform']}")

    # -------------------------------------------------------------------
    # Phase 2: Rules discovered from performance data.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF topic is AI tools THEN use curiosity gap or bold claim hook, "
            "NOT listicle — because AI tool listicles averaged 1.1% engagement "
            "vs 9.2% for curiosity gap hooks",
            ["listicle post got 12K views vs 245K for bold claim",
             "curiosity gap got 890K views"],
            0.92,
        ),
        (
            "IF platform is TikTok THEN post between 8-9am EST — because "
            "morning posts averaged 340K views vs 10K for afternoon posts",
            ["8am posts: 890K, 320K, 510K views", "2pm post: 12K views",
             "3pm post: 8K views"],
            0.88,
        ),
        (
            "IF content is tutorial/educational THEN wrap it in a story, "
            "never pure how-to — because pure tutorials got 0.8% engagement "
            "vs 10.3% for story-wrapped technical content",
            ["Next.js tutorial: 8K views", "AI wrote my code story: 510K views"],
            0.85,
        ),
        (
            "IF hook uses 'Stop using X' contrarian format THEN expect high "
            "saves and shares — because contrarian hooks had 3x the save rate "
            "of other formats",
            ["Copilot contrarian: 18K saves, 5.6K shares"],
            0.70,
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
        ("AI-only content. Never make generic productivity or tutorial content — "
         "the audience follows for AI insights, not basic how-tos.",
         "derived from engagement analysis"),
        ("Every TikTok hook must create a gap between what the viewer expects and "
         "what actually happened. 'How to X' hooks are dead.",
         "derived from hook performance comparison"),
        ("Post TikToks at 8-9am EST. YouTube uploads at 10am EST. "
         "Substack at 7am EST.",
         "derived from time-of-day analysis"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are a content creation agent for an AI/tech creator. "
            "Write engaging social media scripts that drive views and saves.")
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
    successes = sum(1 for p in posts if p["outcome"] == "success")
    print(f"  Posts tracked: {len(posts)}")
    print(f"  Success rate: {successes}/{len(posts)} ({successes/len(posts):.0%})")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"  Avg views (success): {sum(p['metadata']['views'] for p in posts if p['outcome']=='success') / successes:,.0f}")
    print(f"  Avg views (failure): {sum(p['metadata']['views'] for p in posts if p['outcome']=='failure') / (len(posts)-successes):,.0f}")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
