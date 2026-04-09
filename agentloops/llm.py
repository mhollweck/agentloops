"""LLM client abstraction — supports Anthropic, OpenAI, and custom providers.

AgentLoops uses an LLM for reflection, rule generation, and convention evolution.
This module provides a unified interface so users can bring any LLM provider.

Supported providers:
- "anthropic" (default): Uses the Anthropic SDK (Claude models)
- "openai": Uses the OpenAI SDK (GPT models)
- Custom: Pass any callable that takes a prompt string and returns a string
"""

from __future__ import annotations

import json
from typing import Any, Callable, Protocol


class LLMCallable(Protocol):
    """Protocol for custom LLM functions."""

    def __call__(self, prompt: str) -> str: ...


def create_llm_client(
    provider: str = "anthropic",
    model: str | None = None,
    api_key: str | None = None,
    custom_fn: LLMCallable | None = None,
) -> Callable[[str], dict[str, Any]]:
    """Create an LLM client function that takes a prompt and returns parsed JSON.

    Args:
        provider: "anthropic", "openai", or "custom".
        model: Model name. Defaults to provider's best model.
        api_key: API key. Falls back to env vars (ANTHROPIC_API_KEY, OPENAI_API_KEY).
        custom_fn: Custom function(prompt) -> str for provider="custom".

    Returns:
        A function that takes a prompt string and returns a parsed JSON dict.
    """
    if provider == "custom" and custom_fn:
        return _wrap_custom(custom_fn)
    elif provider == "openai":
        return _create_openai_client(model or "gpt-4o", api_key)
    else:
        # Default: Anthropic
        return _create_anthropic_client(model or "claude-sonnet-4-6", api_key)


def _create_anthropic_client(
    model: str, api_key: str | None
) -> Callable[[str], dict[str, Any]]:
    """Create an Anthropic-backed LLM client."""

    def call_llm(prompt: str) -> dict[str, Any]:
        import anthropic

        client = anthropic.Anthropic(api_key=api_key)
        message = client.messages.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = ""
        for block in message.content:
            if hasattr(block, "text"):
                text += block.text

        return _parse_json_response(text)

    return call_llm


def _create_openai_client(
    model: str, api_key: str | None
) -> Callable[[str], dict[str, Any]]:
    """Create an OpenAI-backed LLM client."""

    def call_llm(prompt: str) -> dict[str, Any]:
        import openai

        client = openai.OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.choices[0].message.content or ""
        return _parse_json_response(text)

    return call_llm


def _wrap_custom(fn: LLMCallable) -> Callable[[str], dict[str, Any]]:
    """Wrap a custom LLM function to return parsed JSON."""

    def call_llm(prompt: str) -> dict[str, Any]:
        text = fn(prompt)
        return _parse_json_response(text)

    return call_llm


def _parse_json_response(text: str) -> dict[str, Any]:
    """Parse JSON from LLM response, handling markdown fences."""
    text = text.strip()
    if text.startswith("```"):
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
        if text.endswith("```"):
            text = text[:-3].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"_raw": text}
