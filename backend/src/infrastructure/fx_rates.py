"""
Live FX Rate Client — Frankfurter API (ECB mid-market rates).

Free, no API key required, unlimited requests.
Provides the mid-market baseline we compare Stripe's exchange_rate against.
"""
import logging
import time
from datetime import datetime, date
from typing import Optional

import httpx

logger = logging.getLogger("xborder.fx")

FRANKFURTER_BASE = "https://api.frankfurter.dev/v1"

_rate_cache: dict[str, tuple[float, float]] = {}
CACHE_TTL_SECONDS = 3600  # 1 hour


async def fetch_live_rate(
    currency_from: str,
    currency_to: str,
    on_date: Optional[date] = None,
) -> Optional[float]:
    """
    Fetch mid-market FX rate from Frankfurter (ECB data).
    Returns None if API is unreachable (caller should fallback).
    """
    cache_key = f"{currency_from}_{currency_to}_{on_date or 'latest'}"
    cached = _rate_cache.get(cache_key)
    if cached:
        rate, ts = cached
        if time.time() - ts < CACHE_TTL_SECONDS:
            return rate

    endpoint = f"{FRANKFURTER_BASE}/{on_date.isoformat() if on_date else 'latest'}"
    params = {"base": currency_from.upper(), "symbols": currency_to.upper()}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()

        rate = data.get("rates", {}).get(currency_to.upper())
        if rate:
            _rate_cache[cache_key] = (rate, time.time())
            logger.info(f"Live FX rate {currency_from}->{currency_to}: {rate} (date={data.get('date')})")
            return float(rate)

        logger.warning(f"No rate returned for {currency_from}->{currency_to}")
        return None

    except Exception as e:
        logger.warning(f"Frankfurter API error for {currency_from}->{currency_to}: {e}")
        return None


async def fetch_rates_batch(
    base_currency: str,
    target_currencies: list[str],
    on_date: Optional[date] = None,
) -> dict[str, float]:
    """Fetch multiple rates in a single API call."""
    symbols = ",".join(c.upper() for c in target_currencies)
    endpoint = f"{FRANKFURTER_BASE}/{on_date.isoformat() if on_date else 'latest'}"
    params = {"base": base_currency.upper(), "symbols": symbols}

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(endpoint, params=params)
            resp.raise_for_status()
            data = resp.json()

        rates = data.get("rates", {})
        now = time.time()
        for cur, rate in rates.items():
            cache_key = f"{base_currency}_{cur}_{on_date or 'latest'}"
            _rate_cache[cache_key] = (float(rate), now)

        logger.info(f"Batch FX rates from {base_currency}: {rates}")
        return {k: float(v) for k, v in rates.items()}

    except Exception as e:
        logger.warning(f"Frankfurter batch API error: {e}")
        return {}


def clear_cache():
    _rate_cache.clear()
