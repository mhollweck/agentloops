# Industry Use Cases

AgentLoops applies to any domain where AI agents run repeatedly and outcomes are measurable. This guide covers 10 verticals with specific problems, metrics, example rules, and ROI estimates.

---

## 1. Sales / AI SDR

**Market:** $2B+ and growing. AI SDR tools (11x, Artisan, Relevance AI) raised $200M+ in 2024-2025.

**The problem:** AI SDRs have 50-70% churn within 6 months. The core issue: agents send the same templated outreach regardless of what's working. A cold email that books meetings in fintech gets sent to healthcare prospects. Response rates decay as prospects learn to ignore AI-generated patterns.

**How learning loops solve it:**
- Track every outreach with its outcome (reply, meeting booked, ignored, unsubscribed)
- Reflect on patterns: which subject lines, personalization approaches, and email lengths work for which industries
- Generate rules that segment by prospect persona, industry, and seniority
- Evolve conventions as market conditions change (what worked in Q1 may not work in Q3)

**Key metrics to track:**
- Reply rate per outreach type
- Meeting booking rate
- Time-to-response
- Unsubscribe/opt-out rate (negative signal)

**Example rules that would evolve:**
```
IF prospect is VP-level THEN keep email under 75 words -- 3x higher reply rate
IF prospect's company raised funding in last 90 days THEN reference the round -- 2.5x replies
IF industry is healthcare THEN avoid urgency language -- reduces opt-outs by 60%
IF previous email got no reply THEN wait 5+ days before follow-up -- 40% better than 2-day cadence
IF subject line is a question THEN expect 28% higher open rate
```

**ROI estimate:** A sales team running 10,000 outreach emails/month at a 2% reply rate. A 50% improvement in reply rate (2% to 3%) means 100 more replies/month. At a 20% meeting-to-close rate and $50K ACV, that's $1M incremental pipeline per month.

**Example:** [`examples/sales_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/sales_agent)

---

## 2. Customer Service

**Market:** $15B customer service AI market. Klarna's AI assistant handles 2/3 of customer chats, saving $40M/year.

**The problem:** Support agents give generic responses. A refund request from a loyal 5-year customer gets the same scripted reply as a first-time buyer. Resolution rates plateau because agents never learn which approaches actually resolve issues faster.

**How learning loops solve it:**
- Track every support interaction with its resolution outcome (resolved, escalated, churned)
- Reflect on which response strategies work for different issue categories
- Build rules that adapt tone, solution approach, and escalation timing by customer segment
- Evolve conventions about when to offer compensation vs. when to explain policy

**Key metrics to track:**
- First-contact resolution rate (FCR)
- Average resolution time
- Customer satisfaction score (CSAT)
- Escalation rate
- Repeat contact rate within 7 days

**Example rules that would evolve:**
```
IF issue is billing dispute AND customer tenure > 2 years THEN lead with empathy + immediate credit -- 85% FCR
IF customer mentions "cancel" THEN offer retention discount before explaining policy -- saves 35% of at-risk accounts
IF issue requires technical steps THEN provide numbered instructions with screenshots -- 50% fewer follow-ups
IF CSAT drops below 3.5 on a response pattern THEN flag for human review
IF customer has contacted 3+ times about same issue THEN escalate immediately -- repeat contacts cost 4x
```

**ROI estimate:** A company handling 100K support tickets/month at $7/ticket average cost. Improving FCR from 65% to 80% eliminates 15,000 repeat contacts/month = $105K/month saved. Plus CSAT improvements reduce churn.

**Example:** [`examples/support_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/support_agent)

---

## 3. Insurance

**Market:** Insurance AI grew 325% YoY in claims processing. $5.5B market by 2027.

**The problem:** Fraud detection models have fixed rules that fraudsters learn to evade. Legitimate claims get delayed by overly aggressive screening. The false positive rate wastes adjuster time, while new fraud patterns slip through because the system only updates quarterly.

**How learning loops solve it:**
- Track every claim assessment with its final outcome (approved, denied, fraud confirmed)
- Reflect on patterns that distinguish legitimate claims from fraudulent ones
- Generate rules that adapt to emerging fraud patterns in real-time
- Forget outdated fraud indicators as schemes evolve

**Key metrics to track:**
- Fraud detection rate (true positive rate)
- False positive rate
- Average processing time per claim
- Adjuster override rate (agent was wrong)
- Dollar value of fraud caught vs. missed

**Example rules that would evolve:**
```
IF claim amount is 2-5x historical average for this policy type THEN flag for review -- catches 70% of padding fraud
IF claim filed within 60 days of policy increase THEN escalate -- 4x fraud likelihood
IF medical claim AND provider is out-of-network AND amount > $10K THEN verify provider credentials
IF auto claim AND three prior claims in 12 months THEN adjuster review required
IF claim documentation is unusually complete for claim type THEN check for staged fraud -- counterintuitive but 3x fraud rate
```

**ROI estimate:** An insurer processing $500M in claims annually with a 5% fraud rate ($25M). Improving detection from 60% to 75% catches an additional $3.75M in fraud per year. Reducing false positives by 30% saves 2,000 adjuster hours/year.

**Example:** [`examples/insurance_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/insurance_agent)

---

## 4. Developer Tools

**Market:** $12B developer tools market. GitHub Copilot alone does $100M+ ARR.

**The problem:** Code generation tools have a 45% frustration rate among developers. The agent suggests code that compiles but doesn't match the project's patterns, conventions, or architecture. Developers waste time fixing AI-generated code that doesn't match their style.

**How learning loops solve it:**
- Track every code suggestion with its outcome (accepted, modified, rejected)
- Reflect on which patterns match the developer's style and which don't
- Generate rules about the codebase's conventions (naming, error handling, architecture)
- Evolve as the codebase changes and new patterns emerge

**Key metrics to track:**
- Suggestion acceptance rate
- Edit distance (how much the developer modified the suggestion)
- Build success after accepting suggestion
- Test pass rate
- Time saved vs. time spent fixing

**Example rules that would evolve:**
```
IF generating TypeScript THEN always use explicit return types -- 90% acceptance rate vs. 60% without
IF error handling THEN use Result<T, E> pattern, not try/catch -- matches codebase convention
IF generating tests THEN use describe/it blocks with AAA pattern -- team standard
IF function > 20 lines THEN split into smaller functions -- developer always refactors these
IF import statement THEN use absolute paths from @/ alias -- project convention
```

**ROI estimate:** A 50-person engineering team spending 20% of time on code review and fixes. Improving suggestion quality from 55% to 75% acceptance rate saves 2 hours/developer/week = 5,200 hours/year. At $150K average salary, that's $375K/year in recovered productivity.

**Example:** [`examples/coding_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/coding_agent)

---

## 5. Legal

**Market:** $1.1B legal AI market. Contract review errors can cost $1M+ per miss. Harvey AI raised $186M.

**The problem:** Contract review agents miss nuanced clauses because they treat every contract the same. An indemnification clause that's standard in SaaS agreements is a red flag in construction contracts. The cost of a miss is catastrophic -- one missed liability clause can exceed $1M.

**How learning loops solve it:**
- Track every clause flagged/missed with senior attorney validation
- Reflect on which clause patterns are risky by contract type and jurisdiction
- Generate rules specific to practice areas, client risk profiles, and jurisdictions
- Evolve as case law changes and new regulatory requirements emerge

**Key metrics to track:**
- Clause detection recall (% of risky clauses caught)
- Precision (% of flagged clauses that were actually risky)
- Attorney override rate
- Review time per contract
- Dollar exposure of missed clauses

**Example rules that would evolve:**
```
IF contract type is SaaS AND indemnification clause lacks mutual limitation THEN flag -- 95% of attorneys want this flagged
IF jurisdiction is California AND non-compete clause present THEN auto-flag as unenforceable
IF limitation of liability < 12 months of fees THEN flag as below market standard
IF auto-renewal clause AND notice period < 60 days THEN flag -- clients miss these and get locked in
IF governing law differs from client's jurisdiction THEN highlight dispute resolution costs
```

**ROI estimate:** A firm reviewing 500 contracts/month, each taking 4 attorney hours at $500/hr ($1M/month). Improving recall from 85% to 95% prevents an average of 2 missed high-risk clauses/month at $500K potential exposure each = $1M risk reduction/month. Reducing review time by 30% saves $300K/month.

**Example:** [`examples/legal_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/legal_agent)

---

## 6. Healthcare

**Market:** Healthcare AI projected at $45B by 2030. BCG research shows clinical decision support improves outcomes by 10-30%.

**The problem:** Clinical decision support systems give the same recommendations regardless of patient context. Drug interaction alerts fire so frequently (alert fatigue) that clinicians override 90%+ of them. The system doesn't learn which alerts are valuable and which are noise.

**How learning loops solve it:**
- Track every recommendation with clinician action (accepted, modified, overridden)
- Reflect on which alert types are acted on vs. ignored
- Generate rules that adjust alert sensitivity by context (patient history, department, clinician)
- Evolve as treatment guidelines change and new evidence emerges

**Key metrics to track:**
- Alert acceptance rate by category
- Override rate (and whether overrides led to adverse events)
- Time-to-decision
- Patient outcome correlation (30-day readmission, complications)
- Clinician satisfaction score

**Example rules that would evolve:**
```
IF drug interaction alert AND both drugs are chronic medications AND patient has been on combination > 6 months THEN suppress alert -- 98% override rate, zero adverse events
IF patient age > 75 AND new medication THEN flag renal dosing check -- 40% of adverse events in this cohort
IF diagnosis is sepsis AND lactate > 2 THEN prioritize antibiotic recommendation to top of alert queue
IF clinician has overridden alert type 5+ times THEN reduce alert priority for that clinician
IF patient has 3+ comorbidities THEN use conservative dosing recommendations
```

**ROI estimate:** A hospital system generating 50,000 alerts/month with a 92% override rate. Reducing unnecessary alerts by 50% (from alert fatigue research) saves 500 clinician hours/month. Improving the quality of remaining alerts to catch 2 additional adverse drug events/month at $50K average cost = $100K/month avoided harm plus reduced malpractice exposure.

**Example:** See [healthcare patterns in concepts](concepts.md)

---

## 7. Education

**Market:** EdTech AI market at $4B, growing 36% CAGR. Adaptive learning platforms like Khan Academy's Khanmigo show 15% improvement in learning outcomes.

**The problem:** AI tutors use one-size-fits-all explanations. A visual learner gets the same text-heavy explanation as a kinesthetic learner. The system doesn't adapt to individual learning patterns, misconception types, or optimal difficulty levels.

**How learning loops solve it:**
- Track every tutoring interaction with learning outcome (quiz score, time-on-task, help requests)
- Reflect on which explanation styles work for different student profiles
- Generate rules for difficulty adjustment, hint sequencing, and example selection
- Evolve as curriculum changes and new pedagogical research emerges

**Key metrics to track:**
- Quiz score improvement (pre/post)
- Time to mastery per concept
- Help request frequency
- Student engagement (session length, return rate)
- Misconception recurrence rate

**Example rules that would evolve:**
```
IF student fails same concept 3 times THEN switch from abstract to concrete examples -- 60% faster mastery
IF student solves quickly AND skips hints THEN increase difficulty by 2 levels -- maintains engagement
IF topic is fractions AND student age < 12 THEN use visual (pizza/pie) metaphors first -- 2x comprehension
IF student asks "why" questions THEN give conceptual explanation before procedural -- higher retention
IF session length > 45 minutes THEN suggest a break with a motivational message -- prevents frustration spiraling
```

**ROI estimate:** A tutoring platform with 100K students. Improving learning outcomes by 15% (matching Khanmigo benchmarks) increases student retention by 20%. At $30/month subscription, 20K additional retained students = $600K/month incremental revenue. Plus: measurable learning gains drive word-of-mouth growth.

**Example:** See [education patterns in concepts](concepts.md)

---

## 8. DevOps / SRE

**Market:** AIOps market at $12B by 2026. PagerDuty, Datadog, and Splunk investing heavily in AI-driven incident response.

**The problem:** Incident response agents treat every alert the same. A CPU spike on a test server gets the same urgency as production database latency. Runbooks are static. Mean time to resolution (MTTR) stays flat because the system doesn't learn from past incidents.

**How learning loops solve it:**
- Track every incident response with its resolution outcome and MTTR
- Reflect on which diagnostic steps actually led to resolution vs. wasted time
- Generate rules for alert prioritization, runbook selection, and escalation timing
- Evolve as infrastructure changes and new failure patterns emerge

**Key metrics to track:**
- Mean time to resolution (MTTR)
- Mean time to detection (MTTD)
- False alarm rate
- Correct first-action rate (did the first diagnostic step help?)
- Escalation accuracy (should it have been escalated sooner/later?)

**Example rules that would evolve:**
```
IF alert is CPU > 90% AND service is stateless AND duration < 5 min THEN auto-scale before paging -- 80% self-resolve
IF database latency spike AND recent deployment in last 2 hours THEN check deployment diff first -- root cause 65% of the time
IF memory leak pattern detected AND service is Java THEN trigger heap dump immediately -- saves 30 min vs. waiting
IF incident involves payment service THEN page on-call AND notify finance within 5 min -- compliance requirement
IF same alert fires 3+ times in 24 hours THEN create a follow-up ticket for permanent fix -- reduces recurrence by 70%
```

**ROI estimate:** A company with 500 incidents/month and 45-minute average MTTR. Reducing MTTR by 30% (to 31 minutes) saves 116 engineer-hours/month. At $200K salary, that's $13K/month. More importantly: reducing customer-facing incidents by 20% through better auto-remediation prevents $200K+/month in SLA penalties and churn.

**Example:** [`examples/devops_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/devops_agent)

---

## 9. E-Commerce

**Market:** AI in e-commerce at $8B by 2026. Personalized recommendations drive 35% of Amazon's revenue.

**The problem:** Recommendation agents optimize for clicks, not for purchases or customer satisfaction. They recommend what everyone buys, not what this specific customer wants. Return rates stay high because the agent doesn't learn which recommendations lead to kept purchases vs. returns.

**How learning loops solve it:**
- Track every recommendation with its full funnel outcome (impression, click, purchase, return)
- Reflect on which recommendation strategies drive purchases that stick (low return rate)
- Generate rules for personalization by customer segment, season, and purchase history
- Evolve as inventory, trends, and customer preferences shift

**Key metrics to track:**
- Click-through rate (CTR)
- Conversion rate (click to purchase)
- Return rate per recommendation type
- Average order value (AOV) lift
- Customer lifetime value (CLV) impact

**Example rules that would evolve:**
```
IF customer has returned 2+ items in category THEN deprioritize that category -- reduces returns by 40%
IF cart value > $100 AND customer is price-sensitive segment THEN show free shipping threshold -- 25% AOV increase
IF browsing session > 10 minutes without add-to-cart THEN show "popular right now" social proof
IF customer purchased gift card last December THEN show gift options starting November -- 3x conversion
IF product has > 15% return rate THEN show size guide/comparison prominently -- reduces returns by 25%
```

**ROI estimate:** An e-commerce site with $10M monthly GMV. Improving conversion by 0.5% (from 3% to 3.5%) adds $500K/month in revenue. Reducing return rate by 3 percentage points (from 12% to 9%) saves $300K/month in reverse logistics. Net: $800K/month incremental value.

**Example:** [`examples/ecommerce_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/ecommerce_agent)

---

## 10. Compliance

**Market:** RegTech at $12B by 2027. Financial institutions spend $270B/year on compliance globally.

**The problem:** Compliance monitoring agents generate massive false positive rates (90%+ in AML). Analysts spend most of their time clearing false alerts instead of investigating real issues. Meanwhile, sophisticated violations slip through because the rules are too blunt.

**How learning loops solve it:**
- Track every alert with its disposition (true positive, false positive, escalated, regulatory action)
- Reflect on which alert patterns are noise vs. signal
- Generate rules that reduce false positives while maintaining or improving detection
- Evolve as regulations change and new evasion techniques appear

**Key metrics to track:**
- False positive rate
- True positive rate (detection rate)
- Alert-to-SAR (Suspicious Activity Report) ratio
- Analyst investigation time per alert
- Regulatory exam findings

**Example rules that would evolve:**
```
IF transaction is international wire AND amount < $3K AND counterparty is known supplier THEN auto-clear -- 95% false positive rate, zero true positives historically
IF customer is PEP AND transaction pattern changes suddenly THEN escalate regardless of amount
IF structuring pattern detected AND customer is cash-intensive business THEN human review -- 40% true positive rate
IF alert type is "round dollar amount" AND customer is payroll company THEN suppress -- inherently round transactions
IF new regulation published THEN flag all transactions in affected category for 30 days until patterns establish
```

**ROI estimate:** A bank processing 10,000 compliance alerts/month at $50/alert investigation cost ($500K/month). Reducing false positives by 40% saves $200K/month in analyst time. Improving true positive rate by 15% catches an additional $2M+/year in suspicious activity, avoiding regulatory fines of $10M+ (average BSA/AML penalty).

**Example:** [`examples/compliance_agent/`](https://github.com/mhollweck/agentloops/tree/main/examples/compliance_agent)

---

## Cross-Vertical Patterns

Regardless of industry, the same learning loop patterns emerge:

1. **Track everything.** The more granular your outcome data, the better the rules.
2. **Reflect weekly at minimum.** Daily if you have high volume (1000+ runs/day).
3. **Let rules evolve, don't hardcode.** The system will discover patterns you wouldn't write manually.
4. **Use selective forgetting aggressively in fast-moving domains.** Sales, e-commerce, and compliance rules go stale fastest.
5. **Correlate rules with outcomes.** Use `tracker.correlate()` to prove a rule is helping before promoting it to a convention.
6. **Human-in-the-loop for high-stakes domains.** In healthcare, legal, and compliance, use quality gates to flag violations for human review rather than auto-applying.

The ROI scales with volume. If your agent runs 10 times, learning loops are nice-to-have. If it runs 10,000 times, they're table stakes.
