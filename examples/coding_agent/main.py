"""
AgentLoops Example: AI Code Assistant
Industry: Developer Tools
Use Case: AI coding agent that learns project-specific patterns and reduces code review rejections.
Expected ROI: 45% of developers are frustrated with "almost right" AI code suggestions. Learning
loops reduce revision cycles from 2.3 to 0.8 per PR, saving 30+ min per developer per day.
"""

import tempfile

from agentloops import AgentLoops


def main():
    storage_dir = tempfile.mkdtemp(prefix="agentloops_coding_")
    loops = AgentLoops("code-assistant", storage_path=storage_dir)

    print("=" * 70)
    print("AgentLoops Example: AI Code Assistant")
    print("=" * 70)

    # -------------------------------------------------------------------
    # Phase 1: Track code generation runs with review outcomes.
    # Each run = a code generation request and the PR review result.
    # -------------------------------------------------------------------
    print("\n--- Phase 1: Tracking code generation runs ---\n")

    code_runs = [
        {
            "input": "Add a new user preferences API endpoint. Project uses Express.js, "
                     "TypeScript, Prisma ORM, Zod validation. Follow existing patterns.",
            "output": "Generated POST /api/preferences endpoint with Prisma query, "
                      "Zod schema validation, proper error handling, and tests.",
            "outcome": "merged",
            "metadata": {"project": "web-api", "language": "typescript",
                         "framework": "express", "orm": "prisma",
                         "review_comments": 0, "revisions": 0},
        },
        {
            "input": "Add global state management for the shopping cart feature. "
                     "Project uses React, TypeScript.",
            "output": "Generated Redux store with cart slice, actions, reducers, "
                      "and connected components using useSelector/useDispatch.",
            "outcome": "rejected",
            "metadata": {"project": "ecommerce-frontend", "language": "typescript",
                         "framework": "react", "state_mgmt": "zustand",
                         "review_comments": 3,
                         "rejection_reason": "Project uses Zustand, not Redux. "
                         "Generated code uses wrong state management library.",
                         "revisions": 0},
        },
        {
            "input": "Write a database migration to add a 'last_login' column to users table. "
                     "Project uses Django, PostgreSQL.",
            "output": "Generated Django migration with AddField for last_login as "
                      "DateTimeField(null=True). Included data migration to backfill "
                      "from auth_log table.",
            "outcome": "needs_revision",
            "metadata": {"project": "django-backend", "language": "python",
                         "framework": "django", "review_comments": 1,
                         "revision_reason": "Backfill migration should be separate "
                         "from schema migration per our convention.",
                         "revisions": 1},
        },
        {
            "input": "Create a React component for displaying user avatar with "
                     "fallback initials. Project uses React, Tailwind CSS.",
            "output": "Generated Avatar component using styled-components with "
                      "fallback to initials when image fails to load.",
            "outcome": "needs_revision",
            "metadata": {"project": "ecommerce-frontend", "language": "typescript",
                         "framework": "react", "review_comments": 2,
                         "revision_reason": "Project uses Tailwind CSS, not "
                         "styled-components. Also missing dark mode variant.",
                         "revisions": 1},
        },
        {
            "input": "Add error tracking middleware for all API routes. "
                     "Project uses Express.js, TypeScript.",
            "output": "Generated Express error middleware that catches all errors, "
                      "logs to Sentry, returns consistent error response shape, "
                      "and includes request ID for tracing.",
            "outcome": "merged",
            "metadata": {"project": "web-api", "language": "typescript",
                         "framework": "express", "review_comments": 0,
                         "revisions": 0},
        },
        {
            "input": "Write unit tests for the payment processing service. "
                     "Project uses NestJS, Jest, TypeScript.",
            "output": "Generated Jest tests with mocked Stripe SDK, testing happy path, "
                      "card declined, network error, and idempotency key scenarios. "
                      "Used describe/it blocks with proper setup/teardown.",
            "outcome": "merged",
            "metadata": {"project": "payment-service", "language": "typescript",
                         "framework": "nestjs", "test_framework": "jest",
                         "review_comments": 0, "revisions": 0},
        },
        {
            "input": "Add a caching layer for the product catalog endpoint. "
                     "Project uses FastAPI, Python, Redis.",
            "output": "Generated Redis caching decorator with TTL, cache invalidation "
                      "on product updates, and cache-aside pattern. Used aioredis "
                      "for async compatibility.",
            "outcome": "needs_revision",
            "metadata": {"project": "catalog-api", "language": "python",
                         "framework": "fastapi", "review_comments": 1,
                         "revision_reason": "Project uses redis-py with async support "
                         "(redis.asyncio), not aioredis which is deprecated.",
                         "revisions": 1},
        },
        {
            "input": "Implement WebSocket connection for real-time notifications. "
                     "Project uses React, Zustand, TypeScript.",
            "output": "Generated WebSocket hook using native WebSocket API, Zustand "
                      "store for notification state, reconnection logic with "
                      "exponential backoff, and React context provider.",
            "outcome": "merged",
            "metadata": {"project": "ecommerce-frontend", "language": "typescript",
                         "framework": "react", "state_mgmt": "zustand",
                         "review_comments": 1, "revisions": 0,
                         "comment": "Nice — correct use of Zustand this time"},
        },
    ]

    for r in code_runs:
        run = loops.track(**r)
        icon = {"merged": "MRG", "rejected": "REJ", "needs_revision": "REV"}
        m = r["metadata"]
        print(f"  [{icon.get(r['outcome'], '???'):3s}] {m['project']:22s} "
              f"| {m['framework']:8s} | comments: {m['review_comments']} "
              f"| {r['outcome']}")

    # -------------------------------------------------------------------
    # Phase 2: Rules from code review patterns.
    # -------------------------------------------------------------------
    print("\n--- Phase 2: Adding learned rules ---\n")

    rules = [
        (
            "IF project is ecommerce-frontend THEN use Zustand for state management, "
            "never Redux — because PR was rejected for using Redux when the project "
            "standardized on Zustand",
            ["ecommerce-frontend cart feature rejected for using Redux",
             "WebSocket notification merged using Zustand correctly"],
            0.95,
        ),
        (
            "IF project uses React with Tailwind CSS THEN never use styled-components "
            "or CSS modules — because Avatar component was revised for using "
            "styled-components instead of Tailwind utility classes",
            ["Avatar PR required revision to switch from styled-components to Tailwind"],
            0.90,
        ),
        (
            "IF generating Django migrations THEN always separate schema changes from "
            "data migrations into two migration files — because combined migrations "
            "violate the project convention and get sent back",
            ["last_login migration revised for combining schema + data migration"],
            0.85,
        ),
        (
            "IF project uses FastAPI with Redis THEN use redis.asyncio (redis-py), "
            "not aioredis — because aioredis is deprecated and merged into redis-py",
            ["catalog-api caching revision due to deprecated aioredis"],
            0.88,
        ),
        (
            "IF generating React components THEN always include dark mode Tailwind "
            "variants (dark:) — because missing dark mode caused a revision on "
            "the Avatar component",
            ["Avatar component missing dark: variants"],
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
        ("Before generating code, check the project's package.json or requirements.txt "
         "for the actual libraries in use. Never assume the standard library choice.",
         "derived from Redux/Zustand and aioredis/redis-py mismatches"),
        ("Always generate code that matches the project's existing patterns exactly — "
         "check 2-3 similar files before writing new code.",
         "derived from styling and ORM pattern mismatches"),
        ("Separate concerns in migrations: one migration per schema change, "
         "data migrations in their own files.",
         "derived from Django migration review feedback"),
    ]

    for text, source in conventions:
        loops.conventions.add(text=text, source=source)
        print(f"  Convention: {text[:70]}...")

    # -------------------------------------------------------------------
    # Phase 4: Enhanced prompt.
    # -------------------------------------------------------------------
    print("\n--- Phase 4: Enhanced prompt ---\n")

    base = ("You are an AI code assistant. Generate production-quality code that "
            "follows project conventions. Your code should pass review on the first try.")
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
    merged = sum(1 for r in code_runs if r["outcome"] == "merged")
    rejected = sum(1 for r in code_runs if r["outcome"] == "rejected")
    revised = sum(1 for r in code_runs if r["outcome"] == "needs_revision")
    total = len(code_runs)
    print(f"  PRs tracked: {total}")
    print(f"  Merged: {merged} ({merged/total:.0%}) | "
          f"Revised: {revised} ({revised/total:.0%}) | "
          f"Rejected: {rejected} ({rejected/total:.0%})")
    print(f"  First-try merge rate: {merged/total:.0%}")
    print(f"  Active rules: {len(loops.rules.active())}")
    print(f"  Most common issue: wrong library/framework choice")
    print(f"\n  Storage: {storage_dir}")
    print("=" * 70)


if __name__ == "__main__":
    main()
