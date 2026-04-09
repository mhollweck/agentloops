"""Pre-seeded starter rules for each agent type.

When an agent is initialized with an agent_type, it gets starter rules
from the Collective Intelligence pool — proven patterns from real agents.

Everyone contributes anonymized learnings. You pay for freshness:
  - Free ($0):       3 agent types, static snapshot (bundled with release)
  - Pro ($99/mo):    Unlimited types, live global rules (updated daily)
  - Team ($249/mo):  Shared namespace across org's agents
  - Enterprise:      Live rules + benchmarking + dedicated support

The more agents on the network, the smarter ALL agents become.
This is the Waze model: free map is great, live traffic data is what you pay for.
"""

from __future__ import annotations

from agentloops.models import Rule

# Each entry: (rule_text, confidence, evidence)
SEED_RULES: dict[str, list[tuple[str, float, list[str]]]] = {
    "sales-sdr": [
        (
            "IF prospect is VP/C-level THEN lead with a specific observation about their product — because senior leaders ignore generic outreach but respond to demonstrated knowledge",
            0.85,
            ["Industry best practice: personalized outreach converts 3x higher for enterprise"],
        ),
        (
            "IF subject line is a listicle or content-marketing style THEN avoid for enterprise prospects — because enterprise contacts pattern-match these to spam",
            0.80,
            ["Consistent pattern across sales teams: listicle subjects underperform for B2B enterprise"],
        ),
        (
            "IF prospect had a recent public event (funding, launch, award) THEN reference it in the first line — because timely personalization signals effort and relevance",
            0.75,
            ["Event-triggered outreach converts 2-4x higher than cold generic"],
        ),
        (
            "IF email has no clear CTA THEN add a specific ask (15-min call, async demo link) — because emails without CTAs get read but not acted on",
            0.70,
            ["Single clear CTA outperforms multiple options by 2x"],
        ),
    ],
    "customer-support": [
        (
            "IF customer expresses frustration THEN acknowledge the emotion before solving the problem — because jumping to solutions without acknowledgment escalates 40% of cases",
            0.90,
            ["Support industry standard: empathy-first reduces escalation rates"],
        ),
        (
            "IF issue has been reported 3+ times by the same customer THEN escalate to tier 2 — because repeated issues signal a systemic problem, not a one-off",
            0.85,
            ["Repeat contacts are the #1 driver of churn in SaaS"],
        ),
        (
            "IF resolution requires more than 2 back-and-forth messages THEN offer a call or screen share — because long async threads frustrate customers and reduce CSAT",
            0.75,
            ["CSAT drops 15 points after the 3rd message exchange on the same issue"],
        ),
        (
            "IF the customer asks 'is this a known issue' THEN check status page and recent tickets before responding — because saying 'no' when it IS known destroys trust",
            0.80,
            ["Known-issue misidentification is the top driver of negative reviews"],
        ),
    ],
    "help-desk": [
        (
            "IF guest has stayed before THEN reference their previous visit and preferences — because returning guests who feel remembered tip 23% more and leave better reviews",
            0.85,
            ["Hospitality industry: recognition drives loyalty more than discounts"],
        ),
        (
            "IF request involves a room change or upgrade THEN check availability before promising — because promising then failing is worse than saying 'let me check'",
            0.80,
            ["Unmet promises are the #1 negative review trigger in hospitality"],
        ),
        (
            "IF guest mentions a special occasion THEN flag for amenity delivery (champagne, card, etc.) — because surprise recognition converts one-time guests to repeat customers",
            0.75,
            ["Special occasion recognition drives 3x repeat booking rate"],
        ),
    ],
    "content-creator": [
        (
            "IF posting a hook/intro THEN front-load the value proposition in the first 3 seconds — because 65% of viewers decide to stay or leave within 3 seconds",
            0.90,
            ["YouTube/TikTok analytics: retention cliff at 3 seconds is universal"],
        ),
        (
            "IF content includes a tutorial THEN show the end result first — because 'here's what we're building' increases completion rate by 40%",
            0.85,
            ["Consistent pattern: outcome-first tutorials retain better"],
        ),
        (
            "IF topic has been covered before THEN find a unique angle or newer data — because rehashed content gets penalized by algorithms and audiences",
            0.75,
            ["Duplicate content detection is active on all major platforms"],
        ),
        (
            "IF posting time conflicts with peak hours for the target audience THEN reschedule — because posting during audience peak hours increases reach 2-3x",
            0.70,
            ["Platform analytics: time-of-day is the #2 factor after content quality"],
        ),
    ],
    "code-generator": [
        (
            "IF generating code that handles user input THEN always validate and sanitize — because unvalidated input is the root cause of OWASP Top 10 vulnerabilities",
            0.95,
            ["Security: input validation prevents injection, XSS, and path traversal"],
        ),
        (
            "IF the project has existing patterns (naming, error handling, testing) THEN follow them — because consistency matters more than theoretical best practices",
            0.90,
            ["Code review data: style inconsistency is the #1 friction point in PRs"],
        ),
        (
            "IF generating a function longer than 50 lines THEN consider breaking it up — because long functions are 3x more likely to contain bugs",
            0.75,
            ["Static analysis: cyclomatic complexity correlates with defect density"],
        ),
        (
            "IF adding error handling THEN be specific about which errors to catch — because broad try/except hides bugs and makes debugging harder",
            0.80,
            ["Debugging time doubles with overly broad exception handlers"],
        ),
    ],
    "recruiting": [
        (
            "IF candidate has <2 years experience THEN focus on projects and learning trajectory over credentials — because early-career signal is in output, not pedigree",
            0.80,
            ["Hiring data: project portfolio predicts junior performance better than resume"],
        ),
        (
            "IF outreach to passive candidate THEN lead with the specific challenge they'd solve, not company perks — because top engineers care about problems, not ping pong tables",
            0.85,
            ["Recruiting benchmarks: problem-first outreach gets 3x response rate"],
        ),
        (
            "IF candidate asks about compensation THEN provide the range early — because withholding range wastes everyone's time and creates negative candidate experience",
            0.90,
            ["Transparency laws plus candidate data: early range sharing increases conversion 25%"],
        ),
    ],
    "legal-review": [
        (
            "IF reviewing a contract clause with ambiguous language THEN flag it as HIGH risk — because ambiguous clauses are the #1 source of contract disputes",
            0.90,
            ["Legal data: 67% of contract disputes stem from ambiguous language"],
        ),
        (
            "IF jurisdiction differs from the company's home jurisdiction THEN highlight potential conflicts — because cross-jurisdiction clauses often have unenforceable terms",
            0.85,
            ["Cross-border legal: enforceability varies dramatically by jurisdiction"],
        ),
        (
            "IF contract contains an auto-renewal clause THEN flag with notice period — because missed cancellation windows are the most common contract gotcha",
            0.80,
            ["Auto-renewal clauses are the #1 surprise cost for businesses"],
        ),
    ],
    "insurance-claims": [
        (
            "IF claim amount is >3x the average for this claim type THEN flag for manual review — because high-value outliers have 5x the fraud rate",
            0.90,
            ["Insurance fraud data: outlier amounts are the strongest fraud signal"],
        ),
        (
            "IF claimant has filed 3+ claims in 12 months THEN flag as high-frequency pattern — because repeat filers have 8x the fraud rate of single-claim filers",
            0.85,
            ["Claims frequency is the #2 fraud predictor after amount"],
        ),
        (
            "IF claim was filed within 48 hours of policy activation THEN flag for review — because early-filing is a common fraud pattern across all insurance types",
            0.80,
            ["Immediate-filing claims have 4x the investigation rate"],
        ),
    ],
    "devops-incident": [
        (
            "IF alert fires during a deployment window THEN check if the deploy caused it before escalating — because 60% of incidents correlate with recent deploys",
            0.90,
            ["SRE data: deployment correlation is the fastest path to root cause"],
        ),
        (
            "IF the same alert fired 3+ times this week THEN investigate the root cause, not just the symptom — because flapping alerts indicate a systemic issue",
            0.85,
            ["Flapping alerts waste 4x the engineering time of one-off alerts"],
        ),
        (
            "IF incident affects <5% of traffic THEN confirm scope before paging on-call — because false urgent escalations cause alert fatigue and burnout",
            0.75,
            ["Alert fatigue is the #1 reason SREs leave: reduce noise, not latency"],
        ),
    ],
    "ecommerce-rec": [
        (
            "IF user viewed a product 3+ times without purchasing THEN recommend similar alternatives at different price points — because repeat viewing signals interest blocked by price or feature mismatch",
            0.85,
            ["E-commerce: multi-view no-buy is the strongest intent signal without conversion"],
        ),
        (
            "IF recommending during a seasonal period THEN weight recent purchase patterns heavily — because seasonal preferences shift quickly and historical data lags",
            0.80,
            ["Seasonal rec accuracy: recency-weighted models outperform by 30%"],
        ),
        (
            "IF user has high return rate THEN prioritize well-reviewed items with detailed sizing — because reducing returns is worth more than increasing order value",
            0.75,
            ["Return cost is 3-5x the margin on the item: preventing returns > driving sales"],
        ),
    ],
}


def get_seed_rules(agent_type: str) -> list[Rule]:
    """Get pre-seeded starter rules for an agent type.

    Args:
        agent_type: The type of agent (e.g., "sales-sdr", "customer-support").

    Returns:
        List of Rule objects with starter intelligence. Empty list if unknown type.
    """
    seeds = SEED_RULES.get(agent_type, [])
    return [
        Rule(
            text=text,
            confidence=confidence,
            evidence=evidence,
            evidence_count=len(evidence),
        )
        for text, confidence, evidence in seeds
    ]


def list_agent_types() -> list[str]:
    """Return all available pre-seeded agent types."""
    return sorted(SEED_RULES.keys())
