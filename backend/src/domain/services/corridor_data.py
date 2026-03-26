"""
Corridor Knowledge Base — Static data about payment corridors.

This is proprietary data that makes the product valuable.
Contains: typical costs, routes, intermediaries, alternatives.
In production, this becomes a database table updated from multiple sources.
"""

CORRIDORS = {
    "USD_EUR": {
        "currency_from": "USD",
        "currency_to": "EUR",
        "typical_total_cost_pct": 1.50,
        "typical_fx_spread_pct": 0.80,
        "typical_platform_fee_pct": 0.0025,  # 0.25% (Stripe standard)
        "typical_intermediary_fee": 15.0,     # $15 flat (SEPA/SWIFT)
        "typical_settlement_days": 2,
        "typical_routes": [
            {
                "name": "SEPA via Correspondent",
                "typical_days": 2,
                "hops": [
                    {"entity": "Stripe", "type": "PSP", "description": "Payment processor — charges 0.25% platform fee"},
                    {"entity": "Citi Correspondent Bank", "type": "intermediary", "description": "USD->EUR nostro/vostro — flat fee ~$15"},
                    {"entity": "SEPA Network", "type": "network", "description": "European payment clearing rail"},
                    {"entity": "Receiving Bank", "type": "fx", "description": "Final FX conversion — applies spread on mid-market rate"},
                ]
            },
            {
                "name": "SWIFT Direct",
                "typical_days": 3,
                "hops": [
                    {"entity": "Stripe", "type": "PSP", "description": "Payment processor"},
                    {"entity": "SWIFT Network", "type": "intermediary", "description": "International wire — $15-30 per transaction"},
                    {"entity": "Receiving Bank", "type": "fx", "description": "Applies FX markup of 0.5-2%"},
                ]
            },
        ],
        "alternatives": [
            {
                "name": "Wise Business",
                "type": "fx_platform",
                "cost_pct": 0.43,
                "settlement_days": 1,
                "effort": "medium",
                "steps": [
                    "Create Wise Business account at wise.com/business (30 min)",
                    "Complete business verification — upload docs (1-2 day wait)",
                    "Add EUR balance as payout destination",
                    "Test with one small payment ($100) to verify",
                    "Monitor for 2 weeks, then migrate all EUR payouts",
                ],
            },
            {
                "name": "Revolut Business",
                "type": "fx_platform",
                "cost_pct": 0.50,
                "settlement_days": 1,
                "effort": "medium",
                "steps": [
                    "Sign up for Revolut Business",
                    "Complete verification",
                    "Use inter-bank rate for EUR conversion",
                    "Set up scheduled EUR payouts",
                ],
            },
        ],
    },
    "USD_INR": {
        "currency_from": "USD",
        "currency_to": "INR",
        "typical_total_cost_pct": 2.00,
        "typical_fx_spread_pct": 1.20,
        "typical_platform_fee_pct": 0.003,  # 0.3%
        "typical_intermediary_fee": 25.0,
        "typical_settlement_days": 3,
        "typical_routes": [
            {
                "name": "SWIFT via Correspondent",
                "typical_days": 3,
                "hops": [
                    {"entity": "Stripe", "type": "PSP", "description": "Payment processor — 0.3% cross-border fee"},
                    {"entity": "JPMorgan Correspondent", "type": "intermediary", "description": "USD nostro bank — $20-30 processing fee"},
                    {"entity": "SWIFT Network", "type": "network", "description": "International wire transfer"},
                    {"entity": "HDFC/SBI India", "type": "fx", "description": "Indian receiving bank — applies FX spread 0.5-2%"},
                ]
            },
        ],
        "alternatives": [
            {
                "name": "Wise Business",
                "type": "fx_platform",
                "cost_pct": 0.61,
                "settlement_days": 1,
                "effort": "medium",
                "steps": [
                    "Create Wise Business account (30 min)",
                    "Add INR recipient with IFSC code",
                    "Test with small amount ($100)",
                    "Compare received amount vs current route",
                    "Migrate if savings confirmed",
                ],
            },
        ],
    },
    "USD_GBP": {
        "currency_from": "USD",
        "currency_to": "GBP",
        "typical_total_cost_pct": 1.30,
        "typical_fx_spread_pct": 0.70,
        "typical_platform_fee_pct": 0.0025,
        "typical_intermediary_fee": 12.0,
        "typical_settlement_days": 2,
        "typical_routes": [
            {
                "name": "Faster Payments via Correspondent",
                "typical_days": 1,
                "hops": [
                    {"entity": "Stripe", "type": "PSP", "description": "Payment processor — 0.25% fee"},
                    {"entity": "Barclays Correspondent", "type": "intermediary", "description": "UK correspondent bank — ~$12 flat"},
                    {"entity": "Faster Payments", "type": "network", "description": "UK instant payment rail"},
                    {"entity": "Receiving Bank", "type": "fx", "description": "Final FX conversion"},
                ]
            },
            {
                "name": "SWIFT to UK",
                "typical_days": 3,
                "hops": [
                    {"entity": "Stripe", "type": "PSP", "description": "Payment processor"},
                    {"entity": "SWIFT Network", "type": "intermediary", "description": "International wire — $15-20"},
                    {"entity": "Receiving Bank", "type": "fx", "description": "Applies FX spread"},
                ]
            },
        ],
        "alternatives": [
            {
                "name": "Wise Business",
                "type": "fx_platform",
                "cost_pct": 0.37,
                "settlement_days": 1,
                "effort": "medium",
                "steps": [
                    "Create Wise Business account (30 min)",
                    "Add GBP recipient with sort code + account number",
                    "Test with small amount",
                    "Compare rates vs current route",
                    "Migrate GBP payouts",
                ],
            },
        ],
    },
}


# FX Rates — hardcoded for demo, replace with live API in production
FX_RATES = {
    "USD_EUR": 0.9210,
    "USD_INR": 83.50,
    "USD_GBP": 0.7930,
    "EUR_USD": 1.0858,
    "INR_USD": 0.01198,
    "GBP_USD": 1.2610,
}


def get_mid_market_rate(currency_from: str, currency_to: str, date=None) -> float:
    """
    Get mid-market FX rate from hardcoded data (sync fallback).
    For live rates, use get_live_mid_market_rate() in routes.
    """
    key = f"{currency_from}_{currency_to}"
    rate = FX_RATES.get(key)
    if rate:
        return rate
    reverse_key = f"{currency_to}_{currency_from}"
    reverse_rate = FX_RATES.get(reverse_key)
    if reverse_rate:
        return 1.0 / reverse_rate
    return 1.0


async def get_live_mid_market_rate(currency_from: str, currency_to: str, on_date=None) -> float:
    """
    Get mid-market FX rate from live Frankfurter API (ECB data).
    Falls back to hardcoded if API is unavailable.
    """
    from ...infrastructure.fx_rates import fetch_live_rate

    live_rate = await fetch_live_rate(currency_from, currency_to, on_date)
    if live_rate is not None:
        return live_rate
    return get_mid_market_rate(currency_from, currency_to, on_date)


def get_corridor_info(corridor_code: str) -> dict:
    return CORRIDORS.get(corridor_code, {})


def get_supported_corridors() -> list:
    return [
        {
            "code": code,
            "from": info["currency_from"],
            "to": info["currency_to"],
            "typical_cost_pct": info["typical_total_cost_pct"],
        }
        for code, info in CORRIDORS.items()
    ]
