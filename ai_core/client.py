"""
SmartClient — dual-mode LLM client with automatic fallback.

Tries Ollama (local, free) first. If Ollama is unavailable or times out,
falls back to the Claude API (cloud, paid). If neither is configured,
returns deterministic mock responses for development.

Usage:
    from ai_core.client import get_client

    client = get_client()
    response = client.complete("Summarize this text: ...")
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

import httpx
from django.conf import settings

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    text: str
    model: str
    provider: str  # "ollama", "claude", "demo"
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    cost_usd: float = 0.0
    fallback_used: bool = False
    error: str = ""


@dataclass
class SmartClient:
    """Dual-mode LLM client: Ollama → Claude API → demo fallback."""

    ollama_url: str = ""
    ollama_model: str = "qwen3:8b"
    ollama_timeout: int = 30

    claude_api_key: str = ""
    claude_model: str = "claude-sonnet-4-20250514"
    claude_timeout: int = 60
    claude_input_cost_per_m: float = 3.0
    claude_output_cost_per_m: float = 15.0

    _http: httpx.Client = field(init=False, repr=False, default=None)

    def __post_init__(self):
        self._http = httpx.Client(timeout=max(self.ollama_timeout, self.claude_timeout))

    def complete(
        self,
        prompt: str,
        system: str = "",
        temperature: float = 0.3,
        max_tokens: int = 2048,
    ) -> LLMResponse:
        if self.ollama_url:
            result = self._try_ollama(prompt, system, temperature, max_tokens)
            if not result.error:
                return result
            logger.warning("Ollama failed (%s), falling back to Claude", result.error)

        if self.claude_api_key:
            result = self._try_claude(prompt, system, temperature, max_tokens)
            if self.ollama_url:
                result.fallback_used = True
            if not result.error:
                return result
            logger.error("Claude also failed: %s", result.error)

        return self._demo_response(prompt)

    def _try_ollama(
        self, prompt: str, system: str, temperature: float, max_tokens: int
    ) -> LLMResponse:
        start = time.monotonic()
        try:
            body: dict[str, Any] = {
                "model": self.ollama_model,
                "prompt": prompt,
                "stream": False,
                "options": {"temperature": temperature, "num_predict": max_tokens},
            }
            if system:
                body["system"] = system

            resp = self._http.post(
                f"{self.ollama_url}/api/generate",
                json=body,
                timeout=self.ollama_timeout,
            )
            resp.raise_for_status()
            data = resp.json()
            elapsed = int((time.monotonic() - start) * 1000)

            return LLMResponse(
                text=data.get("response", ""),
                model=self.ollama_model,
                provider="ollama",
                input_tokens=data.get("prompt_eval_count", 0),
                output_tokens=data.get("eval_count", 0),
                latency_ms=elapsed,
                cost_usd=0.0,
            )
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return LLMResponse(
                text="",
                model=self.ollama_model,
                provider="ollama",
                latency_ms=elapsed,
                error=str(exc),
            )

    def _try_claude(
        self, prompt: str, system: str, temperature: float, max_tokens: int
    ) -> LLMResponse:
        start = time.monotonic()
        try:
            import anthropic

            client = anthropic.Anthropic(
                api_key=self.claude_api_key,
                timeout=self.claude_timeout,
            )
            messages = [{"role": "user", "content": prompt}]
            kwargs: dict[str, Any] = {
                "model": self.claude_model,
                "max_tokens": max_tokens,
                "messages": messages,
                "temperature": temperature,
            }
            if system:
                kwargs["system"] = system

            resp = client.messages.create(**kwargs)
            elapsed = int((time.monotonic() - start) * 1000)

            input_tok = resp.usage.input_tokens
            output_tok = resp.usage.output_tokens
            cost = (
                input_tok * self.claude_input_cost_per_m / 1_000_000
                + output_tok * self.claude_output_cost_per_m / 1_000_000
            )

            return LLMResponse(
                text=resp.content[0].text,
                model=self.claude_model,
                provider="claude",
                input_tokens=input_tok,
                output_tokens=output_tok,
                latency_ms=elapsed,
                cost_usd=round(cost, 6),
            )
        except Exception as exc:
            elapsed = int((time.monotonic() - start) * 1000)
            return LLMResponse(
                text="",
                model=self.claude_model,
                provider="claude",
                latency_ms=elapsed,
                error=str(exc),
            )

    def _demo_response(self, prompt: str) -> LLMResponse:
        """Deterministic mock for development without any LLM configured."""
        logger.info("No LLM configured — returning demo response")
        prompt_lower = prompt.lower()

        if "score" in prompt_lower or "lead" in prompt_lower:
            text = '{"score": 7, "label": "warm", "reason": "Demo: lead shows purchase intent"}'
        elif "summarize" in prompt_lower or "summary" in prompt_lower:
            text = "Demo summary: The text discusses key points relevant to the topic at hand."
        elif "classify" in prompt_lower or "intent" in prompt_lower:
            text = '{"intent": "purchase", "confidence": 0.85}'
        elif "email" in prompt_lower or "draft" in prompt_lower:
            text = "Subject: Follow-up\n\nHi,\n\nThank you for reaching out. [Demo response]"
        else:
            text = f"Demo response for: {prompt[:100]}"

        return LLMResponse(
            text=text,
            model="demo",
            provider="demo",
            input_tokens=len(prompt.split()),
            output_tokens=len(text.split()),
            latency_ms=1,
        )

    def close(self):
        if self._http:
            self._http.close()


_client: SmartClient | None = None


def get_client() -> SmartClient:
    """Return a singleton SmartClient configured from Django settings."""
    global _client
    if _client is None:
        cfg = getattr(settings, "AI_CONFIG", {})
        ollama = cfg.get("ollama", {})
        claude = cfg.get("claude", {})
        _client = SmartClient(
            ollama_url=ollama.get("base_url", ""),
            ollama_model=ollama.get("model", "qwen3:8b"),
            ollama_timeout=ollama.get("timeout", 30),
            claude_api_key=claude.get("api_key", ""),
            claude_model=claude.get("model", "claude-sonnet-4-20250514"),
            claude_timeout=claude.get("timeout", 60),
            claude_input_cost_per_m=claude.get("input_cost_per_m", 3.0),
            claude_output_cost_per_m=claude.get("output_cost_per_m", 15.0),
        )
    return _client
