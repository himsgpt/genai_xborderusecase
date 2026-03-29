"""
Analysis Agent — LLM-powered payment intelligence.

Takes deterministic analysis results and enriches them with:
1. Contextual, narrative explanation (not template strings)
2. Dynamic, data-driven recommendations (not threshold-based constants)
3. Risk flags and anomaly detection
4. Market-aware insights

The core analysis engine (domain/services/analysis.py) runs first — it always works.
This agent ENHANCES results when an LLM is available.
"""
import json
import logging
from typing import Optional

from .llm_client import call_llm

logger = logging.getLogger("xborder.agents")

ANALYSIS_SYSTEM_PROMPT = """You are a cross-border payment cost optimization expert. You analyze real payment data to find hidden fees, FX spread markups, and cost-saving opportunities.

Your analysis is data-driven and specific — never generic. You always reference actual numbers from the payment data.

IMPORTANT GUIDELINES:
- Compare the actual effective rate to the ECB mid-market rate
- Calculate the REAL FX markup percentage
- Identify which fee component is the biggest cost driver
- Provide specific, actionable recommendations with dollar amounts
- Consider the PSP being used and suggest alternatives with specific cost comparisons
- Flag any anomalies (unusual fees, slow settlement, etc.)
- Be direct and business-focused, not academic

Return ONLY valid JSON with this exact structure (no markdown, no code fences):
{
    "explanation": "A 3-5 paragraph analysis in plain English. Explain what happened to this payment, where money was lost, and what's unusual. Use actual numbers.",
    "recommendations": [
        {
            "title": "Specific action item",
            "description": "Why this helps, with numbers. Compare current cost to alternative cost.",
            "category": "route_switch|batching|timing|negotiation|fx_strategy",
            "estimated_savings": 0.00,
            "estimated_savings_annual": 0.00,
            "effort": "low|medium|high",
            "risk": "low|medium|high",
            "implementation_steps": ["Step 1", "Step 2"]
        }
    ],
    "risk_flags": ["Any concerns about this payment pattern"],
    "key_insight": "One-sentence summary of the most important finding"
}"""

BATCH_SYSTEM_PROMPT = """You are a cross-border payment portfolio analyst. You analyze MULTIPLE payments together to find cross-cutting patterns, corridor-level insights, and portfolio-wide optimization strategies.

Focus on:
- Patterns across payments (same corridor, same PSP issues)
- Volume-based negotiation opportunities
- Portfolio-level cost reduction strategies
- Diversification recommendations (don't over-rely on one PSP/route)

Return ONLY valid JSON (no markdown, no code fences):
{
    "portfolio_summary": "2-3 paragraph overview of the payment portfolio health",
    "recommendations": [
        {
            "title": "Portfolio-level recommendation",
            "description": "Why and how, with aggregated numbers",
            "category": "route_switch|batching|timing|negotiation|fx_strategy|portfolio",
            "estimated_savings": 0.00,
            "estimated_savings_annual": 0.00,
            "effort": "low|medium|high",
            "risk": "low|medium|high",
            "implementation_steps": ["Step 1", "Step 2"]
        }
    ],
    "risk_flags": ["Portfolio-level concerns"],
    "key_insight": "Most important finding across all payments"
}"""


async def enhance_single_analysis(
    corridor: str,
    amount_sent: float,
    currency_sent: str,
    amount_received: float,
    currency_received: str,
    mid_rate: float,
    actual_rate: float,
    total_fees: float,
    total_cost_pct: float,
    platform_fee: float,
    intermediary_fee: float,
    fx_spread_cost: float,
    leakage: float,
    leakage_pct: float,
    psp: str,
    settlement_days: int,
    flow: list,
    data_source: str,
    corridor_info: dict,
) -> Optional[dict]:
    """Enhance a single payment analysis with LLM intelligence."""

    expected = amount_sent * mid_rate
    fx_markup_pct = abs(mid_rate - actual_rate) / mid_rate * 100 if mid_rate else 0

    user_prompt = f"""Analyze this cross-border payment:

PAYMENT:
- Corridor: {corridor.replace('_', ' → ')}
- Amount sent: {currency_sent} {amount_sent:,.2f}
- Amount received: {currency_received} {amount_received:,.2f}
- Expected at mid-market: {currency_received} {expected:,.2f}
- Shortfall: {currency_received} {expected - amount_received:,.2f}
- PSP: {psp}
- Settlement time: {settlement_days} days

FX RATES:
- ECB mid-market rate: {mid_rate:.6f}
- Effective rate applied: {actual_rate:.6f}
- FX markup: {fx_markup_pct:.3f}%

FEE BREAKDOWN ({data_source}):
- Platform fee ({psp}): ${platform_fee:,.2f} ({platform_fee/amount_sent*100:.2f}%)
- Intermediary/correspondent: ${intermediary_fee:,.2f}
- FX spread cost: ${fx_spread_cost:,.2f} ({fx_spread_cost/amount_sent*100:.2f}%)
- TOTAL: ${total_fees:,.2f} ({total_cost_pct:.2f}% of sent)

CORRIDOR BENCHMARKS:
- Typical total cost: {corridor_info.get('typical_total_cost_pct', 0):.1f}%
- Typical FX spread: {corridor_info.get('typical_fx_spread_pct', 0):.1f}%
- Typical settlement: {corridor_info.get('typical_settlement_days', 0)} days
- Leakage (above baseline): ${leakage:,.2f} ({leakage_pct:.2f}%)

AVAILABLE ALTERNATIVES:
{json.dumps(corridor_info.get('alternatives', []), indent=2)}

PAYMENT ROUTE:
{json.dumps(flow, indent=2)}
"""

    response = await call_llm(ANALYSIS_SYSTEM_PROMPT, user_prompt)
    return _parse_json_response(response) if response else None


async def enhance_batch_analysis(analyses: list[dict]) -> Optional[dict]:
    """Analyze multiple payments together for portfolio-level insights."""
    if not analyses:
        return None

    summary_lines = []
    total_sent = 0
    total_fees = 0
    total_leakage = 0
    corridors = {}

    for a in analyses:
        total_sent += a.get("amount_sent", 0)
        total_fees += a.get("total_fees", 0)
        total_leakage += a.get("leakage", 0)
        c = a.get("corridor", "unknown")
        if c not in corridors:
            corridors[c] = {"count": 0, "total_sent": 0, "total_fees": 0, "total_leakage": 0, "psps": set()}
        corridors[c]["count"] += 1
        corridors[c]["total_sent"] += a.get("amount_sent", 0)
        corridors[c]["total_fees"] += a.get("total_fees", 0)
        corridors[c]["total_leakage"] += a.get("leakage", 0)
        corridors[c]["psps"].add(a.get("psp", "unknown"))

    # Convert sets to lists for JSON
    corridor_summary = {}
    for c, data in corridors.items():
        corridor_summary[c] = {**data, "psps": list(data["psps"])}

    user_prompt = f"""Analyze this payment portfolio:

PORTFOLIO OVERVIEW:
- Total payments: {len(analyses)}
- Total sent: ${total_sent:,.2f}
- Total fees: ${total_fees:,.2f} ({total_fees/total_sent*100:.2f}%)
- Total leakage: ${total_leakage:,.2f}
- Projected annual leakage: ${total_leakage * 12:,.2f}

BY CORRIDOR:
{json.dumps(corridor_summary, indent=2)}

INDIVIDUAL PAYMENTS:
"""
    for a in analyses:
        user_prompt += (
            f"  - {a.get('corridor','?')}: ${a.get('amount_sent',0):,.0f} via {a.get('psp','?')}, "
            f"fees ${a.get('total_fees',0):,.2f} ({a.get('total_cost_pct',0):.1f}%), "
            f"leakage ${a.get('leakage',0):,.2f}\n"
        )

    response = await call_llm(BATCH_SYSTEM_PROMPT, user_prompt)
    return _parse_json_response(response) if response else None


def _parse_json_response(response: str) -> Optional[dict]:
    """Parse LLM response as JSON, handling markdown code fences."""
    try:
        cleaned = response.strip()

        if cleaned.startswith("```"):
            first_newline = cleaned.index("\n")
            cleaned = cleaned[first_newline + 1:]
            if "```" in cleaned:
                cleaned = cleaned[:cleaned.rindex("```")]

        return json.loads(cleaned.strip())
    except (json.JSONDecodeError, ValueError) as e:
        logger.warning(f"Failed to parse LLM JSON: {e}")
        return {
            "explanation": response,
            "recommendations": [],
            "risk_flags": [],
            "key_insight": "AI analysis available but could not be structured",
        }
