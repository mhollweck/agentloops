# Contributing to AgentLoops

Thanks for your interest in contributing!

## Setup

```bash
git clone https://github.com/mhollweck/agentloops.git
cd agentloops
uv sync
```

## Running Tests

```bash
pytest
```

To run with coverage:

```bash
pytest --cov=agentloops
```

## Submitting Changes

1. Fork the repo and create a feature branch.
2. Make your changes.
3. Run `pytest` and make sure all tests pass.
4. Open a PR with a clear description of what changed and why.

## Code Style

- Standard Python conventions (PEP 8).
- Type hints are welcome and encouraged.
- Keep functions focused and well-named.
- Add tests for new functionality.

## Questions?

Open an issue if something is unclear. We're happy to help.
