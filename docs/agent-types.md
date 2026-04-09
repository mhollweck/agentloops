# Pre-Seeded Agent Types

AgentLoops ships with pre-seeded intelligence for common agent types. When you specify an `agent_type`, your agent starts with proven conventions and rules from the global learning network — no cold start.

```python
loops = AgentLoops("my-sales-bot", agent_type="sales-sdr", api_key="al_xxx")

# Your agent immediately has access to global conventions like:
# → "CTOs respond 4.2x more to technical depth than ROI-first emails"
# → "Follow-ups on Tuesday/Wednesday 9-11am book 2.3x more meetings"
# → "Mentioning prospect's recent GitHub/LinkedIn activity doubles reply rate"
```

## Available Agent Types

### `sales-sdr` — Sales Development / Outreach

**What it learns:** Which outreach patterns book meetings, optimal follow-up timing, personalization strategies by persona, subject line patterns, call-to-action effectiveness.

**Starter rules (seeded from global network):**
- IF target is C-suite THEN lead with strategic insight, not product features
- IF no reply after 3 touches THEN switch channel (email → LinkedIn → phone)
- IF prospect engaged with content THEN reference specific piece in outreach
- IF industry is regulated THEN lead with compliance/security positioning

**Key metrics tracked:** Reply rate, meeting booked rate, pipeline generated, time-to-reply.

**Target customers:** AI SDR platforms (11x, Artisan, Relevance AI), sales teams using Clay/Instantly/Salesforge, any company with automated outbound.

---

### `customer-support` — Ticket Resolution

**What it learns:** Which response patterns resolve tickets fastest, escalation triggers, tone calibration by issue type, self-service deflection opportunities.

**Starter rules:**
- IF ticket mentions "cancel" THEN lead with empathy + immediate value, not troubleshooting
- IF customer is enterprise tier THEN name their account manager in first response
- IF issue is password/SSO THEN skip troubleshooting, go straight to reset
- IF same customer, 3rd ticket in 7 days THEN proactive escalation to success team

**Key metrics tracked:** First contact resolution (FCR), resolution time, CSAT, escalation rate.

**Target customers:** SaaS companies, Intercom/Zendesk users, fintech support teams, any company building AI support bots.

---

### `help-desk` — Hospitality & Service Desk

**What it learns:** Guest preference patterns, upsell timing and conversion, escalation thresholds, seasonal demand patterns, VIP handling conventions.

**Starter rules:**
- IF guest booked suite AND requested late checkout THEN offer spa upsell (3x conversion)
- IF repeat guest THEN reference previous stay preferences without asking
- IF complaint about noise THEN immediate room change offer, don't troubleshoot
- IF check-in after 10pm THEN skip upsell, prioritize speed

**Key metrics tracked:** Guest satisfaction, upsell conversion rate, resolution time, repeat booking rate.

**Target customers:** Hotel chains, airlines, travel platforms, SaaS help desks, any service with repeat customers.

---

### `content-creator` — Content Strategy & Creation

**What it learns:** Which hooks drive engagement, optimal posting times, format effectiveness (video vs text vs carousel), topic resonance patterns.

**Starter rules:**
- IF platform is TikTok THEN hook must land in first 2 seconds
- IF topic is tutorial THEN "before/after" format outperforms "how to"
- IF posting on weekend THEN personal/behind-the-scenes outperforms educational
- IF engagement drops 2 days in a row THEN switch content pillar

**Key metrics tracked:** Views, engagement rate, follower growth, save/share ratio.

**Target customers:** Creator economy tools, marketing teams, social media agencies, content automation platforms.

---

### `code-generator` — Code Generation & Review

**What it learns:** Which code patterns produce fewer bugs, language-specific conventions, review feedback patterns, test coverage correlations.

**Starter rules:**
- IF generating async code THEN always include error handling and timeouts
- IF PR has >500 lines THEN flag for split before review
- IF test coverage drops below 80% THEN block merge and suggest specific tests
- IF same function modified 3x in a week THEN suggest refactor

**Key metrics tracked:** Bug rate, review iterations, build pass rate, time-to-merge.

**Target customers:** Dev tools companies, coding assistants (Cursor, Cody, Codegen), CI/CD platforms, engineering teams.

---

### `recruiting` — Candidate Screening & Outreach

**What it learns:** Which outreach messages get responses, screening criteria that predict success, interview scheduling optimization, offer acceptance patterns.

**Starter rules:**
- IF candidate is passive (employed) THEN lead with growth opportunity, not job description
- IF role is engineering THEN mention tech stack and team culture in first message
- IF candidate responded but didn't schedule THEN follow up within 24h with specific time slots
- IF candidate source is referral THEN fast-track screening (2x higher conversion)

**Key metrics tracked:** Response rate, screen-to-interview conversion, time-to-fill, offer acceptance rate.

**Target customers:** HR tech platforms, recruiting agencies, ATS providers, companies building AI recruiters.

---

### `legal-review` — Contract & Document Review

**What it learns:** Which clauses flag real risks vs noise, jurisdiction-specific patterns, negotiation leverage points, false-positive reduction.

**Starter rules:**
- IF indemnification clause is uncapped THEN always flag (high risk regardless of deal size)
- IF governing law differs from company jurisdiction THEN flag with specific implications
- IF contract value < $50K THEN reduce scrutiny on standard terms (focus on non-standard)
- IF same counterparty, 2nd contract THEN reference prior negotiated terms

**Key metrics tracked:** Review time, false-positive rate, risk items caught, negotiation success rate.

**Target customers:** Legal tech companies, contract management platforms, in-house legal teams, law firms.

---

### `insurance-claims` — Claims Processing & Fraud Detection

**What it learns:** Fraud indicator patterns, processing efficiency rules, audit preparation conventions, seasonal claim patterns.

**Starter rules:**
- IF multiple claims from same body shop within 30 days THEN flag for fraud review
- IF claim amount is 5-10% below investigation threshold THEN flag (common fraud tactic)
- IF claimant has policy < 90 days AND total loss THEN escalate
- IF weather event in region THEN batch-process similar claims with expedited rules

**Key metrics tracked:** Fraud detection rate, false-positive rate, processing time, audit pass rate.

**Target customers:** Insurtech companies, claims management platforms, insurance carriers.

---

### `devops-incident` — Incident Response & SRE

**What it learns:** Which alerts need which runbooks, escalation timing, root cause patterns, post-mortem insights.

**Starter rules:**
- IF alert is CPU > 90% AND duration < 5 min THEN auto-resolve (transient spike)
- IF same service, 3rd alert in 1 hour THEN escalate to on-call immediately
- IF incident during deploy window THEN check rollback first before investigating
- IF P1 incident AND no acknowledgment in 10 min THEN page secondary on-call

**Key metrics tracked:** MTTR, false-alert rate, escalation accuracy, incident recurrence rate.

**Target customers:** Platform engineering teams, SRE teams, observability companies, PagerDuty/Opsgenie users.

---

### `ecommerce-rec` — Product Recommendations & Personalization

**What it learns:** Purchase prediction patterns, cross-sell timing, personalization rules, seasonal adjustments, return risk indicators.

**Starter rules:**
- IF customer bought running shoes THEN recommend socks/insoles within 3 days (not shoes)
- IF customer browsed 3x without purchase THEN offer exists intent discount
- IF cart value > $200 THEN show free shipping threshold (don't discount)
- IF product has >15% return rate THEN add size guide prominently

**Key metrics tracked:** Conversion rate, average order value, return rate, customer lifetime value.

**Target customers:** E-commerce platforms, Shopify apps, recommendation engine companies, retail tech.

---

## How Global Learning Works

When you use a pre-seeded agent type with a Pro or Enterprise plan, your agent benefits from — and contributes to — the collective intelligence of all agents of that type on AgentLoops.

**What gets shared (anonymized):**
- Behavioral rules that improved outcomes (e.g., "leading with empathy resolves billing tickets 60% faster")
- Anti-patterns that hurt outcomes (e.g., "technical jargon in support replies increases escalation 2x")
- Convention effectiveness scores (which rules actually work across many agents)

**What NEVER gets shared:**
- Your actual inputs, outputs, or conversations
- Customer-specific data or PII
- Your custom rules or proprietary prompts
- Any data that could identify your business or customers

Think of it like Waze: every driver's route data makes traffic predictions better for everyone, but nobody sees your specific trips.

## Creating Custom Agent Types

You can define your own agent type for internal use:

```python
loops = AgentLoops(
    "my-unique-agent",
    agent_type="custom:invoice-processor",
    api_key="al_xxx"
)
```

Custom types don't participate in global learning — they're private to your organization. You can seed them with your own starter rules:

```python
loops.rules.add_rule(
    pattern="IF invoice currency differs from PO currency THEN flag for review",
    confidence=0.95,
    source="manual"
)
```
