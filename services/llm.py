"""LLM provider abstraction.

Endpoints and domain services depend ONLY on the `LLMProvider` interface and the
`get_llm()` factory — never on a concrete SDK. Switching from OpenAI to Anthropic
means adding one class and one branch in `get_llm()`, nothing else.
"""

from __future__ import annotations

import abc
import json
from typing import Any

from django.conf import settings


class LLMError(RuntimeError):
    """Raised when the provider fails or returns something we cannot parse."""


def _extract_json(text: str) -> dict[str, Any]:
    """Robustly pull a JSON object out of a model response.

    Handles the common failure modes: markdown ```json fences and leading/trailing
    prose around the object. Raises LLMError if no valid object can be recovered.
    """
    cleaned = text.strip()

    # Strip markdown fences if present.
    if cleaned.startswith("```"):
        cleaned = cleaned.split("```", 2)
        cleaned = cleaned[1] if len(cleaned) > 1 else text
        if cleaned.startswith("json"):
            cleaned = cleaned[len("json") :]
        cleaned = cleaned.strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass

    # Fall back to the substring between the first '{' and the last '}'.
    start, end = cleaned.find("{"), cleaned.rfind("}")
    if start != -1 and end != -1 and end > start:
        try:
            return json.loads(cleaned[start : end + 1])
        except json.JSONDecodeError as exc:
            raise LLMError(f"Could not parse JSON from LLM response: {exc}") from exc

    raise LLMError("LLM response contained no JSON object.")


class LLMProvider(abc.ABC):
    """Provider-agnostic chat interface used for extraction and explanation."""

    @abc.abstractmethod
    def complete_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        """Run a chat completion and return the parsed JSON object."""
        raise NotImplementedError


class OpenAILLMProvider(LLMProvider):
    """Default concrete provider, backed by the OpenAI chat completions API."""

    def __init__(self, *, api_key: str | None = None, model: str | None = None) -> None:
        from openai import OpenAI

        self._model = model or settings.OPENAI_CHAT_MODEL
        self._client = OpenAI(api_key=api_key or settings.OPENAI_API_KEY)

    def complete_json(self, system_prompt: str, user_content: str) -> dict[str, Any]:
        try:
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_content},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
        except Exception as exc:
            raise LLMError(f"OpenAI chat request failed: {exc}") from exc

        content = response.choices[0].message.content or ""
        return _extract_json(content)


def get_llm() -> LLMProvider:
    """Factory: returns the configured LLM provider."""
    provider = settings.LLM_PROVIDER.lower()
    if provider == "openai":
        return OpenAILLMProvider()
    # Plug in AnthropicLLMProvider here when needed.
    raise LLMError(f"Unknown LLM_PROVIDER: {settings.LLM_PROVIDER!r}")
