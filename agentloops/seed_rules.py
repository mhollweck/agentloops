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
    # --- Creator agent types ---
    "youtube-creator": [
        (
            "IF title is longer than 60 characters THEN shorten it to under 50 because YouTube truncates titles on mobile at ~50 chars and truncated titles kill CTR",
            0.85,
            ["YouTube mobile truncation at ~50 chars is well-documented by creators"],
        ),
        (
            "IF the first 30 seconds don't state the video's value prop THEN rewrite the intro to front-load the payoff because YouTube measures 30-second retention and that single metric determines whether the algorithm promotes the video",
            0.90,
            ["YouTube algorithm weights 30-second retention heavily for promotion"],
        ),
        (
            "IF a video gets over 10% CTR but under 40% average view duration THEN the content is underdelivering on the title's promise — rewrite the script structure, not the title",
            0.85,
            ["High CTR + low retention trains algorithm that channel clickbaits"],
        ),
        (
            "IF you have a how-to video THEN put the exact result in the thumbnail (before/after, final output) because thumbnails showing tangible outcomes get 2-3x higher CTR than text-only thumbnails",
            0.80,
            ["Outcome thumbnails outperform abstract/text-only by 2-3x"],
        ),
        (
            "IF a video has high impressions but CTR below 4% THEN change the thumbnail before changing the title because the thumbnail is 80% of the click decision",
            0.85,
            ["Thumbnail drives 80% of click decision; YouTube allows swaps without re-upload"],
        ),
        (
            "IF you're scripting a 10+ minute video THEN add a pattern interrupt every 2-3 minutes because retention graphs show drops at predictable intervals and interrupts reset attention",
            0.80,
            ["Pattern interrupts create micro-hooks that reset viewer attention"],
        ),
        (
            "IF your video answers a question THEN put the answer in the first 60 seconds and then explain why because 'answer then explain' has higher retention than 'build up to the answer'",
            0.85,
            ["Answer-first structure retains better: viewers who got the answer stay to understand"],
        ),
        (
            "IF your title contains a number THEN use an odd or specific number instead of a round one because '7 Tips' outperforms '10 Tips' and specificity signals authenticity",
            0.75,
            ["Odd/specific numbers outperform round numbers in CTR"],
        ),
    ],
    "tiktok-creator": [
        (
            "IF the first frame doesn't have text or a face THEN reshoot with on-screen text in frame 1 because TikTok decides to push a video based on the first 1 second's watch-through rate",
            0.90,
            ["TikTok algorithm decides promotion based on 1-second watch-through rate"],
        ),
        (
            "IF a trending sound has under 50K uses THEN use it within 24 hours because the algorithm boosts early adopters of rising sounds — by 500K uses the boost window is closed",
            0.80,
            ["Early adoption of rising sounds gets algorithmic boost on TikTok"],
        ),
        (
            "IF your video is getting views but low shares THEN add a 'send this to someone who...' CTA because shares are weighted 5-10x higher than likes in TikTok's ranking",
            0.85,
            ["TikTok weights shares 5-10x higher than likes; direct prompts increase share rate 30-40%"],
        ),
        (
            "IF you're posting educational content THEN keep it under 45 seconds because TikTok rewards completion rate and 45-second educational videos hit 70%+ completion vs 30% for 90-second ones",
            0.85,
            ["Completion rate is TikTok's primary metric; shorter = higher completion"],
        ),
        (
            "IF your hook starts with 'I' or 'So' THEN rewrite to start with 'You', a number, or a question because second-person hooks outperform first-person by 2x on average watch time",
            0.80,
            ["Second-person hooks ('You're doing X wrong') outperform first-person by 2x"],
        ),
        (
            "IF a video flops (under 300 views after 24h) THEN don't delete it — post a new version with a different hook because deleted videos signal instability to the algorithm",
            0.75,
            ["Deleted videos signal instability; same content with better hook often performs 10x better"],
        ),
        (
            "IF a video gets 1000+ views in the first hour THEN post a follow-up within 24 hours on the same topic because TikTok clusters related content and a hot topic compound-boosts the next video",
            0.80,
            ["TikTok clusters related content from same creator; hot topics compound-boost"],
        ),
        (
            "IF your completion rate is above 80% but followers gained is low THEN add a hook at the end referencing other content because high completion without follow CTA means no reason to follow",
            0.80,
            ["High completion without follow CTA = enjoyed but no follow reason"],
        ),
    ],
    "newsletter-writer": [
        (
            "IF your subject line is longer than 7 words THEN shorten it because 6-7 word subject lines have the highest open rates — mobile email clients truncate at 35-40 characters",
            0.85,
            ["6-7 word subject lines have highest open rates across Substack and Beehiiv"],
        ),
        (
            "IF your open rate drops below 40% THEN send a re-engagement email to inactive subscribers because a smaller engaged list outperforms a large dead one and email providers penalize low engagement",
            0.80,
            ["Email providers penalize low engagement with spam filtering"],
        ),
        (
            "IF your subject line is a statement THEN test rewriting it as an incomplete thought or question because open loops outperform declarative subjects by 15-25% on open rate",
            0.80,
            ["Open loops outperform declarative subjects by 15-25%"],
        ),
        (
            "IF you're writing a long newsletter (1000+ words) THEN add a TL;DR at the top with 3 bullet points because readers who scan and find value are more likely to read the full piece",
            0.75,
            ["TL;DR at top increases full-read rate for long newsletters"],
        ),
        (
            "IF you're publishing on Substack THEN send between Tuesday-Thursday at 7-9am in your audience's timezone because weekend sends have 20-30% lower open rates",
            0.80,
            ["Weekend newsletter sends have 20-30% lower open rates"],
        ),
        (
            "IF your click-through rate on links is below 3% THEN reduce links to 1-2 because a single clear CTA converts 3-5x better than a link roundup",
            0.80,
            ["Single CTA converts 3-5x better than multiple links"],
        ),
        (
            "IF you mention a tool or resource THEN include your honest take because newsletters that add editorial judgment have 2x higher forward rates than pure curation",
            0.75,
            ["Editorial judgment drives 2x higher forward rates"],
        ),
        (
            "IF you're growing from 0 to 1000 subscribers THEN cross-post every issue as a Note and a Twitter thread because discovery on Substack alone is nearly zero for new writers",
            0.85,
            ["External distribution is the only growth lever until recommendations kick in"],
        ),
    ],
    "social-media": [
        (
            "IF you're posting on Twitter/X THEN put the hook in the first line and leave a line break before the rest because the timeline only shows ~280 chars before 'Show more'",
            0.85,
            ["Twitter timeline shows ~280 chars before 'Show more'; first line determines expansion"],
        ),
        (
            "IF you're writing a Twitter thread THEN make each tweet standalone-valuable because 60% of thread readers drop off after tweet 2",
            0.80,
            ["60% of thread readers drop off after tweet 2"],
        ),
        (
            "IF your tweet gets 10+ replies in the first hour THEN reply to every single one within 2 hours because Twitter's algorithm heavily weights reply velocity",
            0.80,
            ["Creator-reply chains double tweet impression count"],
        ),
        (
            "IF you're posting on LinkedIn THEN start with a one-line hook followed by a line break because LinkedIn truncates at ~210 characters with 'see more'",
            0.85,
            ["LinkedIn algorithm measures 'see more' clicks as primary engagement signal"],
        ),
        (
            "IF you have a piece of long-form content THEN extract 5-8 standalone insights and post them individually over 2 weeks because atomized content outperforms link-sharing by 10x",
            0.85,
            ["Platforms suppress external links; atomized content gets 10x engagement"],
        ),
        (
            "IF your LinkedIn post includes a link THEN put the link in the first comment because LinkedIn's algorithm suppresses posts with external links by 40-50%",
            0.80,
            ["LinkedIn suppresses posts with external links by 40-50% in reach"],
        ),
        (
            "IF your Twitter following is under 5K THEN reply to 10-20 large accounts daily with substantive takes because quality replies are the #1 growth lever for small accounts",
            0.80,
            ["Quality replies to large accounts provide best growth for small accounts"],
        ),
        (
            "IF you haven't posted in over 48 hours THEN post engagement bait to restart algorithmic momentum because platforms reduce distribution to dormant accounts",
            0.70,
            ["Platforms reduce distribution to dormant accounts; quick engagement resets baseline"],
        ),
    ],
    "seo-writer": [
        (
            "IF the target keyword has informational intent THEN structure as a direct answer in the first 100 words because Google pulls featured snippets from pages that answer concisely up front",
            0.90,
            ["Answer-first structure wins position zero / featured snippets"],
        ),
        (
            "IF you're targeting a keyword with over 10K monthly searches and you have a new site THEN target the long-tail variant instead because new domains can't compete on head terms",
            0.85,
            ["Long-tail variants rank months before head terms for new domains"],
        ),
        (
            "IF the SERP shows 'People Also Ask' boxes THEN add an FAQ section using those exact questions as headings because FAQ sections frequently get pulled into PAA boxes",
            0.85,
            ["FAQ sections with PAA questions can get a second SERP listing"],
        ),
        (
            "IF your post is over 1500 words THEN add a table of contents with anchor links because Google uses jump-to sitelinks which increases SERP real estate and CTR 10-15%",
            0.80,
            ["Table of contents enables jump-to sitelinks in SERPs"],
        ),
        (
            "IF you're publishing on a new domain THEN focus first 20 posts on a single topic cluster with heavy internal linking because Google's topical authority rewards depth over breadth",
            0.85,
            ["20 interlinked posts on one topic outranks 20 posts on 20 topics"],
        ),
        (
            "IF you have an existing post ranking positions 5-15 THEN update it rather than writing a new post because updating preserves accumulated authority and typically jumps 3-5 positions",
            0.85,
            ["Updating existing URLs preserves authority; typically jumps 3-5 positions within weeks"],
        ),
        (
            "IF a competitor's #1 page has thin content THEN write a 3x more comprehensive page because content quality gaps are the easiest ranking opportunities",
            0.80,
            ["Google wants to replace thin #1 results but needs a clearly better alternative"],
        ),
        (
            "IF your meta description is auto-generated THEN write a custom one under 155 chars with keyword and benefit because custom meta descriptions improve CTR 5-10%",
            0.75,
            ["Custom meta descriptions improve CTR 5-10% over auto-generated"],
        ),
    ],
    "podcast-producer": [
        (
            "IF a clip is under 45 seconds and contains a complete thought with emotional escalation THEN prioritize it for social distribution because 30-60s clips with clear arcs outperform longer clips",
            0.85,
            ["30-60s is the sweet spot for podcast clip shareability on social"],
        ),
        (
            "IF the guest makes a counterintuitive claim THEN flag that segment as high-priority clip because contrarian statements generate the most comments and shares",
            0.85,
            ["Contrarian 'wait, what?' moments create the best social clips"],
        ),
        (
            "IF generating show notes THEN structure as: 1-sentence summary, 3-5 key takeaways, timestamped topics, guest links because this format is what Apple Podcasts and Spotify index for search",
            0.80,
            ["Structured show notes get indexed by podcast platforms for search"],
        ),
        (
            "IF the episode title contains an unknown guest's name THEN lead with the topic hook instead because unknown names reduce click-through rate",
            0.80,
            ["Topic-first titles outperform guest-name titles for non-famous guests"],
        ),
        (
            "IF audio energy drops for more than 90 seconds THEN mark for cutting because listener drop-off spikes during low-energy sections",
            0.80,
            ["Spotify data shows skip-forward within 2 minutes of energy dips"],
        ),
        (
            "IF the episode is longer than 60 minutes THEN create a 'skip to' section with 3-4 timestamps because long episodes intimidate new listeners",
            0.75,
            ["Entry points via timestamps reduce abandonment before play"],
        ),
        (
            "IF selecting an episode title THEN test: does it promise a specific transformation or revelation? because specificity signals value and creates curiosity gap",
            0.80,
            ["Specific transformation titles outperform generic interview titles"],
        ),
        (
            "IF producing clips for social with two speakers THEN always include context from the question so the clip makes sense standalone because clips starting mid-answer confuse new audiences",
            0.80,
            ["Standalone context in clips prevents confusion for new audiences"],
        ),
    ],
    # --- Founder agent types ---
    "email-outreach": [
        (
            "IF email is over 125 words THEN cut to under 100 because cold emails over 125 words see 50%+ drop in reply rate — founders skim on mobile",
            0.85,
            ["Cold emails over 125 words see 50%+ reply rate drop"],
        ),
        (
            "IF you don't have a mutual connection THEN open with a specific observation about their product because personalization referencing something only a real user would notice converts 3x better",
            0.85,
            ["Specific product observations convert 3x better than generic 'I love what you're building'"],
        ),
        (
            "IF the recipient is a founder THEN write peer-to-peer, never vendor-to-buyer because founders pattern-match sales emails instantly — 'I help companies like yours' is an auto-delete",
            0.90,
            ["Peer-to-peer framing gets replies; vendor framing gets deleted"],
        ),
        (
            "IF first email gets no reply THEN follow up exactly 3 days later with a single new data point because the 3-day follow-up has the highest conversion of any cadence",
            0.80,
            ["3-day follow-up cadence has highest reply conversion"],
        ),
        (
            "IF you're emailing about a product THEN lead with the recipient's problem, not your solution because 'I noticed [problem]' → 'I built [thing]' outperforms the reverse by 2-3x",
            0.85,
            ["Problem-first outperforms solution-first by 2-3x in reply rates"],
        ),
        (
            "IF your ask requires more than one step THEN simplify to a single yes/no question because every additional friction point halves conversion",
            0.80,
            ["Single yes/no ask converts best; multi-step asks halve conversion"],
        ),
        (
            "IF your subject line is longer than 6 words THEN shorten to 3-5 words because short subjects look like real emails, not campaigns",
            0.80,
            ["Short subject lines (3-5 words) outperform descriptive ones for cold email"],
        ),
        (
            "IF the recipient recently launched something THEN reference it and send within 48 hours because post-launch founders are most emotionally open to conversations",
            0.80,
            ["Post-launch is peak receptivity window for founder outreach"],
        ),
    ],
    "community-manager": [
        (
            "IF a new member posts an introduction THEN reply within 2 hours because early engagement in the first 24 hours is the #1 predictor of long-term retention",
            0.90,
            ["First 24-hour engagement is #1 predictor of community retention"],
        ),
        (
            "IF a post has zero replies after 4 hours THEN write a substantive reply because dead posts signal a dead community and lurkers see unanswered questions and never post",
            0.85,
            ["Unanswered posts create doom loop of declining engagement"],
        ),
        (
            "IF someone shares a win THEN amplify with a specific compliment and follow-up question because public celebration creates positive reinforcement loop",
            0.80,
            ["Public celebration drives posting frequency and attracts new members"],
        ),
        (
            "IF a thread is turning negative THEN DM the aggressor privately before posting a public warning because private DMs resolve 80% of issues without drama",
            0.85,
            ["Private moderation resolves 80% of issues; public moderation escalates conflict"],
        ),
        (
            "IF engagement drops 30%+ week-over-week THEN post a controversial-but-safe hot take to spark discussion because communities need periodic energy injections",
            0.75,
            ["Hot takes reliably reignite participation in declining communities"],
        ),
        (
            "IF someone asks a previously answered question THEN link the answer AND add one new sentence of context because 'use search' kills community warmth",
            0.80,
            ["Link + context helps asker and trains others to search without killing warmth"],
        ),
        (
            "IF someone reports a bug or complaint THEN acknowledge within 1 hour even without a fix because speed of acknowledgment matters more than speed of resolution",
            0.85,
            ["Fast acknowledgment buys goodwill; silence breeds frustration"],
        ),
        (
            "IF a Discord server has more than 5 channels with zero activity THEN archive them because empty channels make a community look dead",
            0.75,
            ["Fewer active channels beats many empty ones for new member perception"],
        ),
    ],
    "product-copywriter": [
        (
            "IF the landing page headline doesn't state a clear outcome THEN rewrite as '[Verb] [desired outcome] without [pain point]' because outcome-first headlines outperform feature-first",
            0.90,
            ["Outcome-first headlines outperform feature-first; visitors decide in 3 seconds"],
        ),
        (
            "IF the page has no social proof above the fold THEN add a metric or testimonial near the headline because social proof adjacent to headline increases conversion 15-30%",
            0.85,
            ["Social proof near headline increases conversion 15-30%"],
        ),
        (
            "IF you're writing a CTA button THEN use first-person ('Start my free trial') not second-person because first-person CTAs outperform second-person by 25-90%",
            0.85,
            ["First-person CTAs outperform second-person by 25-90% in A/B tests"],
        ),
        (
            "IF you're listing features THEN convert each to 'Feature → so you can [benefit]' format because features tell, benefits sell",
            0.80,
            ["Feature-to-benefit conversion is the fundamental copywriting transformation"],
        ),
        (
            "IF the page has more than 3 CTAs THEN reduce to 1 primary and 1 secondary max because multiple CTAs create decision paralysis",
            0.80,
            ["Every additional CTA reduces probability of action by ~15% (Hick's Law)"],
        ),
        (
            "IF testimonials are generic ('great product!') THEN replace with specific outcome testimonials ('saved 4 hours/week') because specific testimonials are trusted 3x more",
            0.80,
            ["Specific outcome testimonials trusted 3x more than vague praise"],
        ),
        (
            "IF you're writing for a technical audience THEN show the product working (code snippet, screenshot) within the first scroll because developers trust demos over descriptions",
            0.85,
            ["Working code snippet converts better than 500 words of marketing copy for devs"],
        ),
        (
            "IF the landing page doesn't address the #1 objection THEN add a FAQ section because unaddressed objections become bounce reasons",
            0.80,
            ["Top objection for indie products is 'will this actually work/be maintained?'"],
        ),
    ],
    "onboarding-agent": [
        (
            "IF a user signs up but doesn't complete the first core action within 24 hours THEN send a single email showing the fastest path to value because users who don't activate in day 1 have 60-70% chance of never returning",
            0.90,
            ["24-hour activation window is the highest-leverage moment; 60-70% churn after"],
        ),
        (
            "IF the onboarding flow has more than 3 steps before value THEN cut until first-value is reachable in under 60 seconds because every step before the 'aha moment' is a dropout point",
            0.90,
            ["Best onboarding delivers value first, then asks for setup"],
        ),
        (
            "IF the user skips the onboarding tour THEN surface contextual tooltips at moment of need instead of forcing it because forced tours have 70-80% skip rates",
            0.85,
            ["Contextual guidance at moment of need has 3x higher retention impact than tours"],
        ),
        (
            "IF a user completes their first core action THEN immediately show the result and celebrate because the gap between action and reward must be zero",
            0.85,
            ["Immediate reward locks in dopamine loop that drives habit formation"],
        ),
        (
            "IF you're asking for user info during signup THEN only ask for email and defer everything else because every additional signup field reduces conversion 10-15%",
            0.85,
            ["Every additional signup field reduces conversion 10-15%"],
        ),
        (
            "IF the product has multiple use cases THEN ask ONE question to segment and customize the first experience because generic dashboards waste the onboarding window",
            0.80,
            ["One segmentation question enables relevant first experience"],
        ),
        (
            "IF the activation milestone requires data from the user THEN pre-populate with sample data because blank-slate paralysis is the #1 onboarding killer for productivity tools",
            0.85,
            ["Pre-filled templates show what 'good' looks like and reduce cognitive load"],
        ),
        (
            "IF a user triggers an error during onboarding THEN show a recovery path, not just an error message because errors during onboarding are 5x more likely to cause permanent churn",
            0.85,
            ["Onboarding errors cause 5x more churn than errors from established users"],
        ),
    ],
    "ad-creative": [
        (
            "IF a Facebook ad has been running 7+ days with declining CTR THEN create 3 new variations because ad fatigue sets in after 7-10 days for audiences under 500K",
            0.85,
            ["Ad fatigue at 7-10 days; algorithm deprioritizes stale creatives"],
        ),
        (
            "IF your ad headline doesn't include a number or specific claim THEN add one because 'Save 4 hours/week' outperforms 'Save time' by 30-50% in CTR",
            0.85,
            ["Specificity drives clicks; specific claims outperform vague by 30-50%"],
        ),
        (
            "IF you're testing a new ad concept THEN test the hook/headline first before body copy because the headline determines 80% of engagement",
            0.85,
            ["Headline determines 80% of engagement; optimize it first"],
        ),
        (
            "IF your target audience is founders or indie hackers THEN use plain direct language because this audience is hyper-allergic to marketing-speak",
            0.80,
            ["Founders respond to specifics: what it does, how fast, what it costs"],
        ),
        (
            "IF you're spending under $50/day THEN test only 2 variables at a time because small budgets across many variations never exit the learning phase",
            0.80,
            ["Meta needs ~50 conversions per ad set per week to optimize; fragmented budget prevents this"],
        ),
        (
            "IF an ad variation outperforms others by 2x+ on CTR THEN check conversion rate first before killing losers because high-CTR ads often attract curiosity clicks that don't convert",
            0.80,
            ["Lower CTR ad with higher CVR may have better ROAS"],
        ),
        (
            "IF video ads are under-performing THEN test the first 3 seconds specifically because 65% of Facebook video viewers drop in the first 3 seconds",
            0.85,
            ["Hook frame (text overlay + first words) is the entire ad for most viewers"],
        ),
        (
            "IF a single creative drives 70%+ of conversions THEN duplicate it into a new ad set rather than scaling because scaling budget 20%+ per day resets Meta's learning phase",
            0.80,
            ["Duplication preserves optimization; budget scaling resets learning phase"],
        ),
    ],
    # --- Utility agent types ---
    "analytics-reporter": [
        (
            "IF a metric changes more than 2 standard deviations from its 30-day rolling average THEN flag as anomaly requiring investigation before reporting because reporting an anomaly as a trend misleads decision-makers",
            0.90,
            ["Always separate signal from noise before presenting"],
        ),
        (
            "IF writing an executive summary THEN lead with the single most important change and its business impact in one sentence because executives read the first sentence and skim the rest",
            0.85,
            ["The 'so what' lead — Brent Dykes, Effective Data Storytelling"],
        ),
        (
            "IF comparing time periods THEN normalize for seasonality and one-time events before drawing conclusions because raw comparisons without context produce false narratives",
            0.85,
            ["A 20% traffic drop during Christmas week is not a crisis"],
        ),
        (
            "IF a vanity metric improves but the quality metric declines THEN highlight the quality decline as primary because growth that dilutes quality signals worsening economics",
            0.85,
            ["Volume up + quality down = worsening channel economics"],
        ),
        (
            "IF presenting funnel data THEN include both absolute numbers and conversion rates because percentages without absolutes hide scale problems",
            0.80,
            ["50% conversion on 4 visitors is meaningless without raw count"],
        ),
        (
            "IF a report has more than 10 metrics THEN group into 3-4 thematic clusters with 1-sentence insight each because ungrouped metric lists cause decision paralysis",
            0.80,
            ["The reader's job is to decide, not to interpret raw numbers"],
        ),
        (
            "IF week-over-week change is under 5% for non-critical metric THEN report as 'stable' rather than exact percentage because small fluctuations are noise",
            0.75,
            ["Reporting small fluctuations as movement trains stakeholders to react to randomness"],
        ),
        (
            "IF a metric has declined 3+ consecutive periods THEN call it a trend even if each decline was small because gradual declines compound — 3% weekly = 44% quarterly",
            0.85,
            ["Gradual declines are the most dangerous; they don't trigger alarms but compound"],
        ),
    ],
    "research-agent": [
        (
            "IF a claim appears in only one source THEN label it 'single-source, unverified' and search for corroboration because single-source claims are the #1 cause of research errors",
            0.90,
            ["Triangulation across 3+ independent sources is the minimum reliability standard"],
        ),
        (
            "IF two credible sources contradict each other THEN present both positions rather than picking one because the contradiction itself is often the most valuable finding",
            0.85,
            ["Premature resolution of contradictions hides important nuance"],
        ),
        (
            "IF a source has a financial incentive related to their claim THEN note the conflict and weight lower because incentive-aligned research overstates favorable metrics by 30-60%",
            0.85,
            ["Gartner/Forrester numbers are notoriously optimistic; vendor studies even more so"],
        ),
        (
            "IF the research question is about market size THEN always specify whose estimate, methodology, and what's included because market size numbers vary 2-10x across sources",
            0.85,
            ["'$50B market' is meaningless without knowing what's counted"],
        ),
        (
            "IF synthesizing from 5+ sources THEN create a source quality matrix and weight conclusions accordingly because treating a 2019 blog post equal to a 2025 study produces garbage",
            0.80,
            ["Source quality weighting: recency, methodology, independence, expertise"],
        ),
        (
            "IF researching a competitor THEN map public actions separately from stated strategy because what companies do and say frequently diverge",
            0.80,
            ["Revealed preference beats stated preference"],
        ),
        (
            "IF the research brief asks for 'everything about X' THEN push back and ask for the decision it needs to inform because undirected research produces encyclopedias, not insights",
            0.80,
            ["Output should be shaped by the decision it supports"],
        ),
        (
            "IF more than 40% of sources are older than 18 months THEN flag that the area may have evolved significantly because fast-moving domains shift fundamentally in under a year",
            0.80,
            ["AI, crypto, regulatory domains can shift fundamentally in <1 year"],
        ),
    ],
    "personal-assistant": [
        (
            "IF an email requires more than 2 minutes to respond and is not urgent THEN move to a batch reply block because context-switching between quick and deep replies destroys focus",
            0.80,
            ["Cal Newport: batching deep replies saves 30-40 minutes per day"],
        ),
        (
            "IF a calendar invite has no agenda THEN request one before accepting because meetings without agendas run 25-40% longer and produce fewer decisions",
            0.85,
            ["No-agenda meetings are the #1 meeting quality problem"],
        ),
        (
            "IF more than 3 tasks are marked urgent THEN force-rank them because when everything is urgent nothing is — true urgency means irreversible consequences if not done today",
            0.85,
            ["Most 'urgent' tasks fail the 'irreversible if not done today' test"],
        ),
        (
            "IF a meeting is scheduled during a 2+ hour focus block THEN propose an alternative time because a 30-minute meeting in a 3-hour focus block destroys 3 hours, not 30 minutes",
            0.85,
            ["Protecting deep work blocks is the highest-ROI calendar intervention"],
        ),
        (
            "IF composing a daily brief THEN structure as: top 3 priorities, calendar with prep notes, awaiting response, FYI items because separating action from FYI prevents important tasks getting buried",
            0.80,
            ["3 priorities max forces real prioritization"],
        ),
        (
            "IF a task has been on the list 5+ business days without progress THEN surface it and ask: do it, delegate it, schedule it, or delete it because stale tasks create ambient anxiety",
            0.80,
            ["David Allen GTD: two-minute rule only works if you also prune what doesn't get done"],
        ),
        (
            "IF an email thread goes back and forth 3+ times without resolution THEN recommend a 10-minute call because long threads indicate misalignment text can't resolve",
            0.80,
            ["3-volley rule is a common EA practice that saves hours per week"],
        ),
        (
            "IF the user has back-to-back meetings for 2+ hours THEN insert a 15-minute buffer because cognitive depletion degrades decision quality",
            0.75,
            ["Microsoft brain-scan research showed stress accumulation without meeting breaks"],
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
