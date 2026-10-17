"""
Pre-built AI tasks that use SmartClient and log to AIRequest.

Each function calls the LLM, logs the result, and returns the parsed output.
Add your own tasks following this pattern.
"""

from __future__ import annotations

import json
import logging

from .client import LLMResponse, get_client
from .models import AIRequest

logger = logging.getLogger(__name__)


def _log(task: str, prompt: str, resp: LLMResponse) -> AIRequest:
    return AIRequest.objects.create(
        task=task,
        provider=resp.provider,
        model=resp.model,
        prompt_preview=prompt[:200],
        input_tokens=resp.input_tokens,
        output_tokens=resp.output_tokens,
        latency_ms=resp.latency_ms,
        cost_usd=resp.cost_usd,
        fallback_used=resp.fallback_used,
        error=resp.error,
    )


def score_lead(name: str, industry: str, message: str) -> dict:
    """Score a lead 1-10 with a label and reason."""
    prompt = (
        f"Score this lead from 1 to 10. Return JSON: "
        f'{{"score": <int>, "label": "<hot|warm|cold>", "reason": "<one sentence>"}}\n\n'
        f"Name: {name}\nIndustry: {industry}\nMessage: {message}"
    )
    system = "You are a lead scoring assistant. Return only valid JSON, no extra text."

    client = get_client()
    resp = client.complete(prompt, system=system, temperature=0.2)
    _log("score_lead", prompt, resp)

    try:
        return json.loads(resp.text)
    except json.JSONDecodeError:
        return {"score": 5, "label": "warm", "reason": resp.text[:200]}


def summarize_text(text: str, max_sentences: int = 3) -> str:
    """Summarize text into a concise paragraph."""
    prompt = f"Summarize the following text in {max_sentences} sentences or fewer:\n\n{text}"
    system = "You are a concise summarizer. Return only the summary, no preamble."

    client = get_client()
    resp = client.complete(prompt, system=system, temperature=0.3)
    _log("summarize_text", prompt, resp)
    return resp.text


def classify_intent(text: str) -> dict:
    """Classify user intent from a message."""
    prompt = (
        f"Classify the intent of this message. Return JSON: "
        f'{{"intent": "<purchase|support|info|complaint|other>", "confidence": <0.0-1.0>}}\n\n'
        f"Message: {text}"
    )
    system = "You are an intent classifier. Return only valid JSON."

    client = get_client()
    resp = client.complete(prompt, system=system, temperature=0.1)
    _log("classify_intent", prompt, resp)

    try:
        return json.loads(resp.text)
    except json.JSONDecodeError:
        return {"intent": "other", "confidence": 0.5}


def draft_email(context: str, tone: str = "professional") -> str:
    """Draft an email reply based on context."""
    prompt = f"Draft a {tone} email reply based on this context:\n\n{context}"
    system = f"You write {tone} business emails. Include a subject line. Be concise."

    client = get_client()
    resp = client.complete(prompt, system=system, temperature=0.5, max_tokens=1024)
    _log("draft_email", prompt, resp)
    return resp.text
