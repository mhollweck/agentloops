# Changelog

## [0.1.0] - 2026-04-09

### Added
- Core AgentLoops class with track(), reflect(), enhance_prompt(), forget(), check()
- 7 self-learning mechanisms: Reflector, RuleEngine, ConventionStore, Forgetter, Tracker, QualityGates, SpikeResponse
- Quality Gates (mechanism #7) -- pre-flight validation with built-in, rule-based, and custom checks
- Multi-outcome system: OutcomeConfig and MetricDef for binary, categorical, numeric, duration, and multi-metric outcomes
- Multi-LLM support: Anthropic (default), OpenAI, and custom LLM callables via `llm_provider` and `llm_fn`
- 10 pre-seeded agent types with starter IF/THEN rules (sales-sdr, customer-support, help-desk, content-creator, code-generator, recruiting, legal-review, insurance-claims, devops-incident, ecommerce-rec)
- Framework adapters: LangChain (`AgentLoopsCallback`) and CrewAI (`AgentLoopsCrewCallback`) drop-in callbacks
- Supabase cloud storage backend with Row Level Security and multi-tenant isolation
- FastAPI server (`server/app.py`) with 15 REST endpoints, JWT + API key authentication
- Next.js dashboard (`dashboard/`) with agent monitoring, learning curves, and quality gate views
- Live demo script (`demo.py`) for showcasing the full learning loop
- File-based storage backend with pluggable BaseStorage interface
- 10 industry examples (sales, support, content, insurance, coding, recruiting, legal, devops, ecommerce, compliance)
- Full documentation: quickstart, concepts, architecture, API reference, integrations, verticals
- 175 tests with full coverage
