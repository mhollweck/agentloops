"""
AgentLoops Seed Rules: AI SDR / Sales Outreach
===============================================
Proven IF/THEN rules for cold outreach, compiled from public research data.
These rules seed the collective intelligence database so new AI SDR agents
start with validated patterns instead of learning from scratch.

Sources are cited per rule. All data points are from public studies
analyzing millions of emails across industries.

Usage:
    from agentloops import AgentLoops
    from seed_rules import SEED_RULES, SEED_CONVENTIONS

    loops = AgentLoops("sales-sdr")
    for rule in SEED_RULES:
        loops.rules.add_rule(
            text=rule["text"],
            evidence=rule["evidence"],
            confidence=rule["confidence"],
        )
"""

# =============================================================================
# SEED RULES — Validated IF/THEN patterns from public sales research
# =============================================================================

SEED_RULES: list[dict] = [

    # -------------------------------------------------------------------------
    # EMAIL LENGTH
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF email body exceeds 125 words THEN expect significantly lower reply "
            "rates — because emails in the 50-125 word range achieve ~50% higher "
            "reply rates than longer formats"
        ),
        "evidence": [
            "Smartlead analysis of cold email statistics 2025: 50-125 words optimal",
            "Belkins 2025 study: 50-75 word range delivers 12% reply rates among top performers",
            "Belkins 2025 study: 200+ word emails drop to 2% reply rate",
        ],
        "confidence": 0.92,
        "category": "email_length",
        "source_urls": [
            "https://www.smartlead.ai/blog/cold-email-stats",
            "https://belkins.io/blog/cold-email-response-rates",
        ],
    },
    {
        "text": (
            "IF email body is under 50 words THEN it may feel too blunt or "
            "lack enough context — the sweet spot is 50-75 words for maximum "
            "reply rates (12% among top performers)"
        ),
        "evidence": [
            "Belkins 2025 study: 50-75 word range is the top-performing bracket",
            "Gong analysis of 132K emails: longer emails (30-150 words) outperform very short ones for booking meetings",
        ],
        "confidence": 0.80,
        "category": "email_length",
        "source_urls": [
            "https://belkins.io/blog/cold-email-response-rates",
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },

    # -------------------------------------------------------------------------
    # SUBJECT LINES
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF subject line is 2-4 words THEN expect highest open rates (46%) "
            "— because open rates drop to 39% at 7 words and 34% at 10+ words"
        ),
        "evidence": [
            "Belkins B2B cold email subject line study 2025: 2-4 words = 46% open rate",
            "Subject lines get truncated after 35-50 characters on mobile",
        ],
        "confidence": 0.90,
        "category": "subject_line",
        "source_urls": [
            "https://belkins.io/blog/b2b-cold-email-subject-line-statistics",
        ],
    },
    {
        "text": (
            "IF subject line is a question THEN expect ~21% higher open rates "
            "than declarative subjects — because questions trigger an involuntary "
            "mental response before the recipient decides to open"
        ),
        "evidence": [
            "Cold email subject line analysis: questions increase open rates by 21%",
            "Gong data: question-based CTAs generate ~2x reply rates of statement-based",
            "Open-ended questions outperform yes/no questions",
        ],
        "confidence": 0.85,
        "category": "subject_line",
        "source_urls": [
            "https://coldmailopenrate.com/blog/subject-lines-that-get-opened/",
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },
    {
        "text": (
            "IF subject line uses lowercase and is short/generic (e.g. 'quick question') "
            "THEN expect higher open rates than carefully crafted personalized subjects "
            "— split tests show 'quick question' beats personalized subjects by 12 percentage points"
        ),
        "evidence": [
            "A/B test data: 'quick question' beat personalized subject lines by 12pp",
            "Short, lowercase, generic subject lines consistently outperform in cold email",
        ],
        "confidence": 0.78,
        "category": "subject_line",
        "source_urls": [
            "https://instantly.ai/blog/a-b-testing-cold-email-subject-lines-framework-tools-statistical-significance/",
        ],
    },
    {
        "text": (
            "IF subject line contains the prospect's company name or a specific "
            "observation THEN expect ~50% higher open rates — because personalized "
            "subject lines achieve 46% open rate vs 35% without personalization"
        ),
        "evidence": [
            "Belkins study: personalized subjects = 46% open rate vs 35% generic",
            "Customizing with prospect name, company, or role improves open rates by 50%",
        ],
        "confidence": 0.88,
        "category": "subject_line",
        "source_urls": [
            "https://belkins.io/blog/b2b-cold-email-subject-line-statistics",
        ],
    },

    # -------------------------------------------------------------------------
    # PERSONALIZATION
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF email uses advanced personalization (company-specific pain points, "
            "product observations) THEN expect 18% reply rate vs 9% for generic "
            "templates — a 2x improvement"
        ),
        "evidence": [
            "Martal 2026 B2B statistics: advanced personalization = 18% vs 9% generic",
            "AI-personalized emails get 4-7x more replies than templates",
            "Top 25% of campaigns with strong personalization achieve 20%+ reply rates",
        ],
        "confidence": 0.92,
        "category": "personalization",
        "source_urls": [
            "https://martal.ca/b2b-cold-email-statistics-lb/",
            "https://www.cleverly.co/blog/cold-email-statistics",
        ],
    },
    {
        "text": (
            "IF email uses multiple personalization fields (not just first name) "
            "THEN expect up to 142% higher reply rates — because name-only "
            "personalization is table stakes and no longer moves the needle"
        ),
        "evidence": [
            "Using multiple custom fields boosts replies by 142%",
            "Personalized emails increase response rates by approximately 32% (baseline)",
            "Campaigns with personalized subject lines see replies jump from 3% to 7%",
        ],
        "confidence": 0.88,
        "category": "personalization",
        "source_urls": [
            "https://www.lemlist.com/blog/how-to-start-an-email",
            "https://www.smartlead.ai/blog/cold-email-stats",
        ],
    },
    {
        "text": (
            "IF opening line references a specific achievement, published content, "
            "or company milestone THEN expect significantly higher reply rates than "
            "'I hope this finds you well' — Gong data confirms specific references "
            "outperform generic openers"
        ),
        "evidence": [
            "Gong cold email analysis: personalized opening lines significantly outperform generic",
            "Optimizing preview text increases open rates by over 30%",
        ],
        "confidence": 0.85,
        "category": "personalization",
        "source_urls": [
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },

    # -------------------------------------------------------------------------
    # TRIGGER EVENTS / TIMING
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF prospect recently raised funding THEN reference the round in the "
            "first line BUT wait 5-12 weeks post-announcement — because weeks 1-2 "
            "leadership is doing press, and weeks 5-12 is when they evaluate vendors "
            "with budget approval"
        ),
        "evidence": [
            "Growth List 2025: optimal outreach window is 5-12 weeks post-funding",
            "Launch Leads 2026: weeks 1-2 are announcement phase, weeks 5-12 are execution phase",
            "Outreach within 24-48 hours of trigger events sees 3-5x higher response rates vs 1 week later",
        ],
        "confidence": 0.85,
        "category": "trigger_events",
        "source_urls": [
            "https://growthlist.co/sales-trigger-events/",
            "https://www.launchleads.com/lead-generation-strategies/funding-events/",
        ],
    },
    {
        "text": (
            "IF prospect had a leadership change (new CXO hire) THEN prioritize "
            "outreach — because leadership changes are the single highest-converting "
            "trigger type, with 400% higher conversion vs generic outreach"
        ),
        "evidence": [
            "Growth List: leadership changes are the highest-converting trigger type",
            "Companies using trigger events see 400% higher conversion rates",
        ],
        "confidence": 0.88,
        "category": "trigger_events",
        "source_urls": [
            "https://growthlist.co/sales-trigger-events/",
            "https://www.autobound.ai/blog/sales-trigger-events-templates",
        ],
    },
    {
        "text": (
            "IF prospect recently had a public event (product launch, award, "
            "conference talk) THEN reference it in the first line — because "
            "event-triggered personalization books meetings at higher rates "
            "than generic outreach"
        ),
        "evidence": [
            "Autobound: 15 sales trigger events that convert — public events are top triggers",
            "Signal-based triggers expected to originate 75% of B2B sales engagements",
        ],
        "confidence": 0.82,
        "category": "trigger_events",
        "source_urls": [
            "https://www.autobound.ai/blog/sales-trigger-events-templates",
        ],
    },

    # -------------------------------------------------------------------------
    # CALL TO ACTION (CTA)
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF this is a cold email (first touch) THEN use an interest-based CTA "
            "('Is this a priority for you?') instead of asking for a meeting — "
            "because interest CTAs outperform meeting requests, and asking for time "
            "upfront reduces reply rates by 44%"
        ),
        "evidence": [
            "Gong 304K email study: Interest CTA is highest performing for cold emails",
            "GrowLeads: interest-based CTAs outperform direct meeting asks by 2.5x",
            "Sales teams asking for time upfront face 44% reduction in reply rates",
        ],
        "confidence": 0.92,
        "category": "cta",
        "source_urls": [
            "https://www.gong.io/blog/this-surprising-cold-email-cta-will-help-you-book-a-lot-more-meetings",
            "https://growleads.io/blog/interest-based-ctas-vs-meeting-requests-study/",
        ],
    },
    {
        "text": (
            "IF prospect has already engaged (replied or clicked) THEN switch to a "
            "specific CTA with a proposed meeting time — because specific CTAs increase "
            "deal-stage bookings from 15% to 37%"
        ),
        "evidence": [
            "Gong data: specific CTA increases deal-stage bookings from 15% to 37%",
            "Interest CTA for cold, specific CTA for warm is the proven progression",
        ],
        "confidence": 0.88,
        "category": "cta",
        "source_urls": [
            "https://www.gong.io/blog/sales-email-statistics",
        ],
    },
    {
        "text": (
            "IF email contains multiple CTAs THEN expect lower response rates — "
            "because single-CTA emails generate 35-42% higher response rates than "
            "emails with multiple calls-to-action"
        ),
        "evidence": [
            "Single-CTA emails generate 35-42% higher response rates",
            "Decision fatigue reduces action — one clear ask outperforms multiple",
        ],
        "confidence": 0.90,
        "category": "cta",
        "source_urls": [
            "https://growleads.io/blog/interest-based-ctas-vs-meeting-requests-study/",
        ],
    },

    # -------------------------------------------------------------------------
    # FOLLOW-UP SEQUENCES
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF prospect has not replied THEN send 4-7 follow-ups — because "
            "4-7 email sequences produce 27% reply rate vs 9% for 1-3 emails, "
            "and 42% of replies come from steps 2-4"
        ),
        "evidence": [
            "Woodpecker follow-up statistics: 4-7 emails = 27% reply rate vs 9% for 1-3",
            "42% of replies come across steps 2-4",
            "80% of successful sales require 5+ follow-up touches",
        ],
        "confidence": 0.90,
        "category": "follow_up",
        "source_urls": [
            "https://woodpecker.co/blog/follow-up-statistics/",
            "https://salesblink.io/blog/cold-email-follow-ups",
        ],
    },
    {
        "text": (
            "IF sending follow-ups THEN use widening gaps: 2-3 days for first "
            "follow-up, 4-7 days for middle steps, 7-14 days for later steps — "
            "because constant-interval sequences look robotic and trigger spam filters"
        ),
        "evidence": [
            "Allegrow 2026: widening gap strategy avoids robotic patterns",
            "Growth List: 2-3 business days optimal for first follow-up",
            "Consensus across 9 studies: widening intervals outperform fixed cadence",
        ],
        "confidence": 0.85,
        "category": "follow_up",
        "source_urls": [
            "https://www.allegrow.co/knowledge-base/cold-email-sequences",
            "https://growthlist.co/cold-email-follow-up-timing/",
        ],
    },
    {
        "text": (
            "IF no reply after 2 follow-ups THEN change the angle/value prop — "
            "because repeating the same message signals desperation and gets ignored; "
            "each follow-up should add new value or a different hook"
        ),
        "evidence": [
            "Mailfra 2026 guide: each follow-up should provide new value, not just bump",
            "Sapience 2026: change angle after 2 non-responses",
        ],
        "confidence": 0.82,
        "category": "follow_up",
        "source_urls": [
            "https://mailfra.com/blog/cold-email-follow-up-sequences",
            "https://sapience.systems/blog/cold-email-follow-up-sequence",
        ],
    },

    # -------------------------------------------------------------------------
    # SEND TIMING
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF choosing when to send THEN send Tuesday-Thursday between 9-11 AM "
            "in the recipient's local timezone — because 60.58% of responses are "
            "generated between 8 AM and 12 PM, and Tuesday has the highest engagement"
        ),
        "evidence": [
            "55% of 9 timing studies identified Tuesday as top-performing day",
            "60.58% of responses generated between 8 AM-12 PM",
            "Siege Media analysis of 85K+ emails: optimal reply times 6-9 AM recipient timezone",
        ],
        "confidence": 0.85,
        "category": "send_timing",
        "source_urls": [
            "https://www.siegemedia.com/marketing/best-time-to-send-cold-email",
            "https://www.emailchaser.com/learn/when-is-the-best-time-to-send-a-cold-email",
        ],
    },
    {
        "text": (
            "IF sending on Monday or Friday THEN expect lower engagement — "
            "because Monday inboxes are flooded from the weekend and Friday "
            "prospects are winding down; mid-week consistently outperforms"
        ),
        "evidence": [
            "Multiple studies: avoid Mondays, Fridays, and weekends",
            "Smartlead 2026: Tuesday-Thursday mid-week window is optimal",
        ],
        "confidence": 0.80,
        "category": "send_timing",
        "source_urls": [
            "https://www.smartlead.ai/blog/best-time-to-send-cold-emails",
        ],
    },

    # -------------------------------------------------------------------------
    # MESSAGING PATTERNS (WHAT TO AVOID)
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF email uses ROI language or statistics in cold outreach THEN expect "
            "15% lower success rate — because ROI claims lack context in a first "
            "touch and feel like marketing spam"
        ),
        "evidence": [
            "Gong analysis of 132K emails: ROI language decreases success rates by 15%",
        ],
        "confidence": 0.88,
        "category": "messaging",
        "source_urls": [
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },
    {
        "text": (
            "IF follow-up email says 'What are your thoughts?' THEN expect 20% "
            "fewer meetings booked — because it increases replies but those replies "
            "are polite brush-offs, not meeting bookings"
        ),
        "evidence": [
            "Gong data: 'What are your thoughts?' decreases meetings booked by 20%",
            "Increases reply rate but harms conversion to meetings",
        ],
        "confidence": 0.85,
        "category": "messaging",
        "source_urls": [
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },
    {
        "text": (
            "IF follow-up email says 'I never heard back from you' THEN expect "
            "14% fewer meetings — because it creates guilt or confirms disinterest "
            "rather than driving action"
        ),
        "evidence": [
            "Gong data: 'I never heard back from you' decreases meetings by 14%",
        ],
        "confidence": 0.85,
        "category": "messaging",
        "source_urls": [
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },
    {
        "text": (
            "IF writing a follow-up THEN include 'Hope all is well' with a "
            "personalized twist — because this phrase correlates with a 24% "
            "increase in meetings booked when personalized to the prospect's situation"
        ),
        "evidence": [
            "Gong data: 'Hope all is well' correlates with 24% increase in meetings booked",
            "Performance improves when personalized to prospect's situation",
        ],
        "confidence": 0.75,
        "category": "messaging",
        "source_urls": [
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },

    # -------------------------------------------------------------------------
    # MULTICHANNEL
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF outreach is email-only THEN expect 3x fewer responses than "
            "multichannel — because sequences using 3+ channels (email + LinkedIn "
            "+ phone) deliver 287% more responses than single-channel"
        ),
        "evidence": [
            "Landbase multi-channel statistics: 287% higher engagement with 3+ channels",
            "Email + LinkedIn combined reply rate ~15% vs 5% email-only",
            "Email + Phone = 128% increase vs email-only",
        ],
        "confidence": 0.90,
        "category": "multichannel",
        "source_urls": [
            "https://www.landbase.com/blog/multi-channel-outreach-statistics",
            "https://outreaches.ai/blog/cold-outreach-benchmarks",
        ],
    },
    {
        "text": (
            "IF using LinkedIn alongside email THEN synchronize messaging — "
            "because synchronized cross-channel messaging improves engagement "
            "by 35% compared to disjointed outreach"
        ),
        "evidence": [
            "Overloop: synchronized LinkedIn + email improves engagement by 35%",
            "LinkedIn messages see 5-20% response rates vs 1-10% for email",
        ],
        "confidence": 0.82,
        "category": "multichannel",
        "source_urls": [
            "https://overloop.com/blog/linkedin-vs-email-which-performs-better-for-b2b-outreach",
        ],
    },

    # -------------------------------------------------------------------------
    # MULTITHREADING (MULTIPLE CONTACTS)
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF targeting an account THEN contact multiple stakeholders (multithread) "
            "— because multithreading increases response rates by 93% compared to "
            "single-contact outreach"
        ),
        "evidence": [
            "Multithreading data: 93% higher response rate vs single-contact",
            "Lavender: single-thread approach is a single point of failure",
        ],
        "confidence": 0.85,
        "category": "multithreading",
        "source_urls": [
            "https://www.lavender.ai/blog/how-to-multithread-in-sales",
            "https://martal.ca/b2b-cold-email-statistics-lb/",
        ],
    },
    {
        "text": (
            "IF multithreading an account THEN stagger entries across days and "
            "vary messaging per role — because sending to 10 contacts on the same "
            "day triggers corporate firewalls and can domain-block you permanently"
        ),
        "evidence": [
            "Allegrow: sudden spike from one domain looks like phishing attack",
            "Domain attack pattern results in domain-wide block",
        ],
        "confidence": 0.90,
        "category": "multithreading",
        "source_urls": [
            "https://www.allegrow.co/knowledge-base/cold-email-sequences",
        ],
    },

    # -------------------------------------------------------------------------
    # SOCIAL PROOF & CASE STUDIES
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF including a case study THEN place it in follow-up email #3, not "
            "the first email — because case studies in the third email consistently "
            "get the most replies, while first emails should be about the prospect"
        ),
        "evidence": [
            "Martal: attaching case study in 3rd email consistently got the most replies",
            "Social proof hooks achieve 6.53% avg reply rate and 53.44% positive reply rate",
        ],
        "confidence": 0.80,
        "category": "social_proof",
        "source_urls": [
            "https://martal.ca/follow-up-email-lb/",
        ],
    },
    {
        "text": (
            "IF referencing a success story THEN use concrete before/after data "
            "from a company in their industry — because relevant success stories "
            "boost reply rates by up to 45%"
        ),
        "evidence": [
            "Industry-relevant case study references boost reply rates by up to 45%",
            "Proof of impact with concrete data outperforms generic praise",
        ],
        "confidence": 0.82,
        "category": "social_proof",
        "source_urls": [
            "https://intentsify.io/blog/what-is-social-proof/",
        ],
    },

    # -------------------------------------------------------------------------
    # SPEED TO LEAD
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF prospect shows intent signal (website visit, content download, "
            "demo request) THEN respond within 5 minutes — because 5-minute "
            "response time delivers 9x higher conversion, and the first responder "
            "captures 35-50% of sales"
        ),
        "evidence": [
            "SalesSo: 5-minute response = 9x conversion rate",
            "First responder captures 35-50% of sales",
        ],
        "confidence": 0.92,
        "category": "speed_to_lead",
        "source_urls": [
            "https://salesso.com/blog/outbound-sdr-statistics/",
        ],
    },

    # -------------------------------------------------------------------------
    # DELIVERABILITY
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF sending cold email at scale THEN ensure SPF, DKIM, and DMARC "
            "are configured — because since Feb 2024 Google/Yahoo require these "
            "for bulk senders, and Microsoft followed in May 2025; without them "
            "emails go straight to spam"
        ),
        "evidence": [
            "Google/Yahoo bulk sender requirements since Feb 2024",
            "Microsoft added same requirements May 2025",
            "Average spam landing rate is 9.1% even with authentication",
        ],
        "confidence": 0.95,
        "category": "deliverability",
        "source_urls": [
            "https://www.smartlead.ai/blog/cold-email-stats",
            "https://www.saleshandy.com/blog/cold-email-statistics/",
        ],
    },
    {
        "text": (
            "IF spam complaint rate exceeds 0.1% THEN immediately reduce volume "
            "and improve targeting — because Google requires sub-0.1% complaint rate "
            "for senders doing 5000+ daily emails; exceeding this destroys domain reputation"
        ),
        "evidence": [
            "Saleshandy: spam complaint rates must stay below 0.1% for 5K+ daily senders",
            "One-click unsubscribe now required by major providers",
        ],
        "confidence": 0.92,
        "category": "deliverability",
        "source_urls": [
            "https://www.saleshandy.com/blog/cold-email-statistics/",
        ],
    },

    # -------------------------------------------------------------------------
    # SEGMENT-SPECIFIC
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF prospect is at a company with <20 employees THEN use a peer-to-peer "
            "tone with cost-saving angles — because startup CTOs respond to ROI "
            "framing differently than enterprise (they feel the burn directly)"
        ),
        "evidence": [
            "Belkins industry benchmarks: startup segment has different response patterns",
            "Startups respond to urgency and cost-saving messaging",
        ],
        "confidence": 0.75,
        "category": "segmentation",
        "source_urls": [
            "https://remotereps247.com/b2b-cold-email-benchmarks-2025-response-rates-by-industry/",
        ],
    },
    {
        "text": (
            "IF prospect title is C-level (CEO/CTO/CIO) at enterprise (1000+ employees) "
            "THEN avoid listicle-style subjects and generic value props — because "
            "C-suite at enterprise pattern-matches to spam faster and requires "
            "highly specific, research-backed outreach"
        ),
        "evidence": [
            "Gong: enterprise C-suite has lowest tolerance for generic outreach",
            "Listicle subjects for enterprise prospects show 0% reply rate in sample data",
        ],
        "confidence": 0.80,
        "category": "segmentation",
        "source_urls": [
            "https://www.gong.io/blog/cold-email-stats",
        ],
    },

    # -------------------------------------------------------------------------
    # AI-SPECIFIC PATTERNS
    # -------------------------------------------------------------------------
    {
        "text": (
            "IF using AI to personalize outreach THEN expect 2x reply rates over "
            "manual templates — because AI-assisted outreach achieves 10.3% reply "
            "rate vs 5.1% for standard cold email"
        ),
        "evidence": [
            "Outreaches.ai benchmark: AI-assisted = 10.3% vs 5.1% standard",
            "AI-personalized emails get 4-7x more replies than templates",
        ],
        "confidence": 0.85,
        "category": "ai_patterns",
        "source_urls": [
            "https://outreaches.ai/blog/cold-outreach-benchmarks",
        ],
    },
    {
        "text": (
            "IF using multi-agent AI system THEN expect 7x higher conversion "
            "rates vs single-AI model — because specialized agents (research, "
            "write, review) produce better output than a monolithic prompt"
        ),
        "evidence": [
            "Landbase: multi-agent AI systems show 7x higher conversion rates",
            "Landbase 825% revenue growth in 2025 validating multi-agent approach",
        ],
        "confidence": 0.78,
        "category": "ai_patterns",
        "source_urls": [
            "https://www.landbase.com/blog/top-ai-sdr-platforms-in-2025",
        ],
    },
]


# =============================================================================
# SEED CONVENTIONS — Higher-level behavioral patterns
# =============================================================================

SEED_CONVENTIONS: list[dict] = [
    {
        "text": (
            "Always research the prospect's company, product, and recent news "
            "before writing — generic outreach gets 2-5x fewer replies than "
            "researched outreach."
        ),
        "source": "Composite: Martal, Belkins, Gong studies on personalization impact",
    },
    {
        "text": (
            "Never send the same email template to multiple contacts at the same "
            "company on the same day — stagger entries and vary messaging per role."
        ),
        "source": "Allegrow multithreading research: domain attack prevention",
    },
    {
        "text": (
            "Use interest-based CTAs for cold outreach, specific meeting CTAs for "
            "warm prospects. Never mix — the progression matters."
        ),
        "source": "Gong 304K email CTA study",
    },
    {
        "text": (
            "Each follow-up email must add new value or a different angle. "
            "Never just 'bump' or 'circle back' — that signals desperation."
        ),
        "source": "Composite: Mailfra, Sapience follow-up sequence guides",
    },
    {
        "text": (
            "Keep email bodies between 50-125 words. Every word must earn its place. "
            "If a sentence doesn't add value for the prospect, cut it."
        ),
        "source": "Composite: Smartlead, Belkins email length studies",
    },
    {
        "text": (
            "Combine email with at least one other channel (LinkedIn or phone). "
            "Single-channel outreach leaves 287% of potential responses on the table."
        ),
        "source": "Landbase multi-channel outreach statistics",
    },
    {
        "text": (
            "Monitor trigger events (funding, leadership changes, product launches) "
            "and time outreach to the execution window (5-12 weeks post-event), "
            "not the announcement window."
        ),
        "source": "Growth List, Launch Leads trigger event timing research",
    },
    {
        "text": (
            "Respond to inbound intent signals within 5 minutes. Speed-to-lead is "
            "the single highest-leverage metric — 9x conversion at 5 minutes."
        ),
        "source": "SalesSo outbound SDR statistics 2025",
    },
    {
        "text": (
            "Avoid ROI claims, statistics, and percentage improvements in first-touch "
            "cold emails. Save proof points for follow-ups and case studies."
        ),
        "source": "Gong 132K email analysis: ROI language impact",
    },
    {
        "text": (
            "A/B test one variable at a time with at least 150 emails per variant. "
            "Testing multiple variables simultaneously produces unreliable results."
        ),
        "source": "Outreach A/B testing best practices, Instantly framework",
    },
]


# =============================================================================
# Utility: Load all seed rules into an AgentLoops instance
# =============================================================================

def seed_agent(loops_instance) -> dict:
    """
    Load all seed rules and conventions into an AgentLoops instance.

    Returns:
        dict with counts of rules and conventions added.
    """
    rules_added = 0
    for rule in SEED_RULES:
        loops_instance.rules.add_rule(
            text=rule["text"],
            evidence=rule["evidence"],
            confidence=rule["confidence"],
        )
        rules_added += 1

    conventions_added = 0
    for conv in SEED_CONVENTIONS:
        loops_instance.conventions.add(
            text=conv["text"],
            source=conv["source"],
        )
        conventions_added += 1

    return {
        "rules_added": rules_added,
        "conventions_added": conventions_added,
    }


if __name__ == "__main__":
    # Print summary when run directly
    print(f"Seed Rules: {len(SEED_RULES)} rules across "
          f"{len(set(r['category'] for r in SEED_RULES))} categories")
    print(f"Seed Conventions: {len(SEED_CONVENTIONS)}")
    print()

    categories = {}
    for rule in SEED_RULES:
        cat = rule["category"]
        categories[cat] = categories.get(cat, 0) + 1

    print("Rules by category:")
    for cat, count in sorted(categories.items()):
        print(f"  {cat}: {count}")

    print()
    print("All source URLs:")
    urls = set()
    for rule in SEED_RULES:
        for url in rule.get("source_urls", []):
            urls.add(url)
    for url in sorted(urls):
        print(f"  {url}")
