"""
LLM Client — Async wrapper for calling Groq / OpenAI / Ollama.
Groq is the primary provider (fast + free tier).
Falls back gracefully if unconfigured or unavailable.
"""
import httpx
import logging
from typing import Optional

from ..infrastructure.config import settings

logger = logging.getLogger("xborder.agents")

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
OPENAI_API_URL = "https://api.openai.com/v1/chat/completions"


async def call_llm(
    system_prompt: str,
    user_prompt: str,
    max_tokens: int = 2000,
    temperature: float = 0.3,
) -> Optional[str]:
    """
    Call the configured LLM. Returns raw text response or None on failure.
    Provider priority: groq > openai > ollama > None (product still works)
    """
    if settings.groq_api_key:
        return await _call_api(
            url=GROQ_API_URL,
            api_key=settings.groq_api_key,
            model=settings.groq_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            provider="groq",
        )

    if settings.openai_api_key:
        return await _call_api(
            url=OPENAI_API_URL,
            api_key=settings.openai_api_key,
            model=settings.openai_model,
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            max_tokens=max_tokens,
            temperature=temperature,
            provider="openai",
        )

    logger.debug("No LLM provider configured — skipping AI enhancement")
    return None


async def _call_api(
    url: str,
    api_key: str,
    model: str,
    system_prompt: str,
    user_prompt: str,
    max_tokens: int,
    temperature: float,
    provider: str,
) -> Optional[str]:
    """Generic OpenAI-compatible API call (works for Groq and OpenAI)."""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                url,
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt},
                    ],
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            content = data["choices"][0]["message"]["content"]
            logger.info(f"LLM call OK ({provider}/{model}): {len(content)} chars")
            return content

    except httpx.TimeoutException:
        logger.warning(f"LLM call timed out ({provider})")
        return None
    except httpx.HTTPStatusError as e:
        logger.warning(f"LLM API error ({provider}): {e.response.status_code} - {e.response.text[:200]}")
        return None
    except Exception as e:
        logger.warning(f"LLM call failed ({provider}): {e}")
        return None
