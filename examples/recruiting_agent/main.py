"""
AgentLoops Example: AI Recruiter / HR Screening Agent
Industry: Human Resources / Talent Acquisition
Use Case: AI candidate screener that learns hiring manager preferences and reduces override rates.
Expected ROI: 40% manager override rate means the agent isn't learning real preferences.
Learning loops cut override rate to <10%, saving 15+ hours/week per recruiter on
misaligned candidate screening.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_recruiting_")
    loops = AgentLoops("recruiter-agent", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: AI Recruiter / HR Screening Agent")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track candidate screening decisions and manager overrides.
    # Each run = one candidate the agent screened for a role.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking candidate screenings ---\n")

    screenings = [
        {
            "input": "Role: Senior Backend Engineer. Hiring Manager: Alice Chen. "
                     "Candidate: Sam Torres. Resume: 6 years Python, Django, AWS. "
                     "Stanford CS degree. No open-source contributions. "
                     "Currently at Oracle.",
            "output": "RECOMMEND: ADVANCE. Strong technical background, top school, "
                      "6 years relevant experience. Meets all listed requirements.",
            "outcome": "override_by_manager",
            "metadata": {"role": "senior_backend", "hiring_manager": "alice_chen",
                         "manager_note": "I need people who build in public. "
                         "No OSS contributions is a dealbreaker for my team culture.",
                         "candidate_oss": False, "candidate_yoe": 6},
        },
        {
            "input": "Role: Senior Backend Engineer. Hiring Manager: Alice Chen. "
                     "Candidate: Priya Sharma. Resume: 4 years Python, FastAPI, GCP. "
                     "Bootcamp grad. 200+ GitHub stars on a FastAPI middleware library. "
                     "Currently freelancing.",
            "output": "RECOMMEND: ADVANCE. Active open-source contributor despite "
                      "shorter experience. FastAPI expertise aligns well.",
            "outcome": "advanced",
            "metadata": {"role": "senior_backend", "hiring_manager": "alice_chen",
                         "candidate_oss": True, "candidate_github_stars": 200,
                         "candidate_yoe": 4},
        },
        {
            "input": "Role: Product Manager. Hiring Manager: Bob Kim. "
                     "Candidate: Jordan Lee. Resume: 3 years PM at Google, MBA from "
                     "Wharton, launched 2 products with 1M+ users. No startup experience.",
            "output": "RECOMMEND: ADVANCE. Strong PM background, top MBA, "
                      "proven product launches at scale.",
            "outcome": "advanced",
            "metadata": {"role": "product_manager", "hiring_manager": "bob_kim",
                         "candidate_yoe": 3, "has_startup_exp": False},
        },
        {
            "input": "Role: Frontend Engineer. Hiring Manager: Carol Davis. "
                     "Candidate: Alex Rivera. Resume: 5 years React, TypeScript, "
                     "Next.js. Made 3 conference talks. Currently at Vercel. "
                     "Portfolio shows 8 polished side projects.",
            "output": "RECOMMEND: ADVANCE. Excellent frontend skills, industry talks "
                      "show thought leadership, portfolio demonstrates initiative.",
            "outcome": "advanced",
            "metadata": {"role": "frontend_engineer", "hiring_manager": "carol_davis",
                         "candidate_yoe": 5, "side_projects": 8,
                         "conference_talks": 3},
        },
        {
            "input": "Role: Senior Backend Engineer. Hiring Manager: Alice Chen. "
                     "Candidate: Mike Johnson. Resume: 8 years Java, Spring Boot, AWS. "
                     "MIT degree. Led team of 5 at Amazon. No Python, no open-source.",
            "output": "RECOMMEND: ADVANCE. Very senior, led teams, MIT education, "
                      "8 years backend. Java/Spring translatable to Python.",
            "outcome": "override_by_manager",
            "metadata": {"role": "senior_backend", "hiring_manager": "alice_chen",
                         "manager_note": "Java-to-Python transitions rarely work well "
                         "at the senior level. And again — no open-source is a no-go.",
                         "candidate_oss": False, "candidate_yoe": 8},
        },
        {
            "input": "Role: Product Manager. Hiring Manager: Bob Kim. "
                     "Candidate: Sarah Park. Resume: 2 years PM at a Series B startup, "
                     "previously software engineer for 3 years. No MBA. "
                     "Shipped v1 of a product that hit $2M ARR.",
            "output": "RECOMMEND: REJECT. Only 2 years PM experience, no MBA.",
            "outcome": "override_by_manager",
            "metadata": {"role": "product_manager", "hiring_manager": "bob_kim",
                         "manager_note": "I don't care about MBAs. She shipped a $2M "
                         "product at a startup — that's worth more than 5 years at Google. "
                         "Advance her immediately.",
                         "candidate_yoe": 2, "has_startup_exp": True,
                         "shipped_product_arr": 2000000},
        },
        {
            "input": "Role: Senior Backend Engineer. Hiring Manager: Alice Chen. "
                     "Candidate: Li Wei. Resume: 5 years Go, Rust, Kubernetes. "
                     "Maintains a popular Kubernetes operator (1.2K GitHub stars). "
                     "Self-taught, no degree. Currently at Cloudflare.",
            "output": "RECOMMEND: ADVANCE. Strong open-source presence, systems "
                      "programming expertise, no degree but proven by contributions.",
            "outcome": "advanced",
            "metadata": {"role": "senior_backend", "hiring_manager": "alice_chen",
                         "candidate_oss": True, "candidate_github_stars": 1200,
                         "candidate_yoe": 5, "has_degree": False},
        },
        {
            "input": "Role: Frontend Engineer. Hiring Manager: Carol Davis. "
                     "Candidate: Emma Wilson. Resume: 7 years Angular, JavaScript. "
                     "No React experience. No side projects. Currently at Deloitte.",
            "output": "RECOMMEND: REJECT. No React experience (required for role). "
                      "Angular skills not directly transferable. No side projects.",
            "outcome": "rejected",
            "metadata": {"role": "frontend_engineer", "hiring_manager": "carol_davis",
                         "candidate_yoe": 7, "side_projects": 0,
                         "has_react": False},
        },
    ]

    overrides = 0
    total = 0
    for s in screenings:
        run = loops.track(**s)
        total += 1
        if s["outcome"] == "override_by_manager":
            overrides += 1
        icon = {"advanced": "ADV", "rejected": "REJ",
                "override_by_manager": "OVR", "hired": "HIR"}
        m = s["metadata"]
        print(f"  [{icon.get(s['outcome'], '???'):3s}] {m['role']:22s} "
              f"| mgr: {m['hiring_manager']:12s} | {s['outcome']}")

    print(f"\n  Override rate: {overrides}/{total} ({overrides/total:.0%})")

    # -------------------------------------------------------------------
    # Phase 2: Rules learned from manager overrides.
    # The agent discovers what managers ACTUALLY care about vs stated criteria.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF hiring manager is Alice Chen THEN weight open-source contributions "
            "2x over education or YOE — because Alice overrode 2 candidates with "
            "strong resumes but no OSS, and advanced candidates with less experience "
            "but active GitHub profiles",
            ["Sam Torres overridden: 6yr exp, Stanford, no OSS",
             "Mike Johnson overridden: 8yr exp, MIT, no OSS",
             "Priya Sharma advanced: 4yr exp, bootcamp, 200 GitHub stars",
             "Li Wei advanced: 5yr exp, no degree, 1.2K GitHub stars"],
            0.95,
        ),
        (
            "IF hiring manager is Bob Kim AND candidate has shipped a revenue-generating "
            "product at a startup THEN advance regardless of YOE or education — because "
            "Bob overrode a rejection of a 2yr PM who shipped $2M ARR product, noting "
            "'that's worth more than 5 years at Google'",
            ["Sarah Park overridden: 2yr PM, no MBA, but $2M ARR product"],
            0.80,
        ),
        (
            "IF role is Senior Backend AND candidate's primary language differs from "
            "team's stack AND candidate has no OSS in the target language THEN reject "
            "— because Alice noted 'Java-to-Python transitions rarely work at senior level'",
            ["Mike Johnson overridden: Java dev for Python role"],
            0.70,
        ),
        (
            "IF role is Frontend Engineer AND candidate has no React experience THEN "
            "reject — because React is non-negotiable for the frontend team",
            ["Emma Wilson rejected: 7yr Angular, no React"],
            0.85,
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
        ("Manager preferences trump stated job requirements. Track overrides per "
         "manager and update screening criteria accordingly.",
         "derived from 37.5% override rate analysis"),
        ("Open-source contributions are the strongest signal for some managers — "
         "always check GitHub profile before screening.",
         "derived from Alice Chen's consistent OSS preference"),
        ("Startup shipping experience (revenue, users) outweighs credentials (MBA, "
         "FAANG tenure) for Bob Kim's PM roles.",
         "derived from Bob Kim's Sarah Park override"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are a candidate screening agent. Evaluate resumes against role "
            "requirements and recommend advance or reject. Be thorough and fair.")
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
    advanced = sum(1 for s in screenings if s["outcome"] == "advanced")
    rejected_count = sum(1 for s in screenings if s["outcome"] == "rejected")
    print(f"  Candidates screened: {total}")
    print(f"  Advanced: {advanced} | Rejected: {rejected_count} | Overridden: {overrides}")
    print(f"  Override rate: {overrides/total:.0%} (target: <10%)")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"  Key insight: Alice cares about OSS, Bob cares about shipping")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
