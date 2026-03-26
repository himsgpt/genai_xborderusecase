"""
Core Analysis Engine — The innovation core of the product.

Runs 4 analysis steps per payment:
1. Fee Attribution (deterministic)   — break down total cost into components
2. Flow Reconstruction (heuristic)   — infer payment route + intermediaries
3. Leakage Detection (deterministic) — compare to corridor baseline
4. Optimization (rule-based)         — generate actionable recommendations

Works without LLM. LLM enhances explanations when available.
"""
import time
from typing import Optional
from datetime import datetime

from .corridor_data import CORRIDORS, get_mid_market_rate  # sibling import within domain.services


def analyze_payment(
    corridor: str,
    amount_sent: float,
    currency_sent: str,
    amount_received: float,
    currency_received: str,
    initiated_at: datetime,
    settled_at: Optional[datetime],
    psp: str = "stripe",
    live_mid_rate: Optional[float] = None,
    stripe_fee_details: Optional[list] = None,
    stripe_exchange_rate: Optional[float] = None,
) -> dict:
    """
    Analyze a single cross-border payment.
    Returns fee breakdown, flow reconstruction, leakage, and recommendations.

    Enhanced mode (with Stripe data):
      - live_mid_rate:         ECB mid-market rate from Frankfurter API
      - stripe_fee_details:    Real fee breakdown from Stripe Balance Transaction
      - stripe_exchange_rate:  Actual FX rate Stripe applied
    """
    start = time.time()

    corridor_info = CORRIDORS.get(corridor)
    if not corridor_info:
        return {"error": f"Unsupported corridor: {corridor}"}

    # ── Step 1: Fee Attribution ──────────────────────────────────────────
    mid_rate = live_mid_rate or get_mid_market_rate(currency_sent, currency_received, initiated_at)
    expected_amount = amount_sent * mid_rate
    actual_rate = amount_received / amount_sent if amount_sent else 0

    # Total cost in received currency, then convert to sent currency
    total_cost_received = expected_amount - amount_received
    total_fees = total_cost_received / mid_rate if mid_rate else 0
    total_cost_pct = (total_fees / amount_sent * 100) if amount_sent else 0

    # --- REAL Stripe fee data (when available) ---
    if stripe_fee_details:
        platform_fee = sum(
            fd["amount"] for fd in stripe_fee_details
            if fd.get("type") in ("stripe_fee", "application_fee", "payment_method_passthrough_fee")
        )
        # FX spread = difference between mid-market and Stripe's exchange rate
        if stripe_exchange_rate and mid_rate:
            fx_spread_pct_val = abs(mid_rate - stripe_exchange_rate) / mid_rate
            fx_spread_cost = amount_sent * fx_spread_pct_val
        else:
            fx_spread_cost = max(0, total_fees - platform_fee)
        intermediary_fee = max(0, total_fees - platform_fee - fx_spread_cost)
        data_source = "stripe_live"
        confidence = 0.95
    else:
        # --- Heuristic attribution (no Stripe data) ---
        platform_fee = amount_sent * corridor_info["typical_platform_fee_pct"]
        intermediary_fee = corridor_info["typical_intermediary_fee"]
        fx_spread_cost = max(0, total_fees - platform_fee - intermediary_fee)

        if total_fees < (platform_fee + intermediary_fee):
            if platform_fee + intermediary_fee > 0:
                ratio = total_fees / (platform_fee + intermediary_fee)
                platform_fee *= ratio
                intermediary_fee *= ratio
            fx_spread_cost = 0
        data_source = "heuristic"
        confidence = 0.78

    # ── Step 2: Flow Reconstruction ──────────────────────────────────────
    settlement_days = 0
    if settled_at and initiated_at:
        delta = settled_at - initiated_at
        settlement_days = max(0, delta.days)

    flow = _reconstruct_flow(
        corridor, corridor_info, amount_sent, settlement_days, psp,
        platform_fee, intermediary_fee, fx_spread_cost,
    )

    # ── Step 3: Leakage Detection ────────────────────────────────────────
    baseline_cost = amount_sent * (corridor_info["typical_total_cost_pct"] / 100)
    leakage = max(0, total_fees - baseline_cost)
    leakage_pct = max(0, total_cost_pct - corridor_info["typical_total_cost_pct"])

    # ── Step 4: Recommendations ──────────────────────────────────────────
    fx_spread_pct = (fx_spread_cost / amount_sent * 100) if amount_sent else 0
    recommendations = _generate_recommendations(
        corridor, corridor_info, total_cost_pct, fx_spread_pct,
        intermediary_fee, settlement_days, amount_sent,
    )

    # ── Explanation ──────────────────────────────────────────────────────
    explanation = _generate_explanation(
        corridor, amount_sent, currency_sent, amount_received, currency_received,
        mid_rate, actual_rate, total_fees, total_cost_pct,
        platform_fee, intermediary_fee, fx_spread_cost,
        flow, leakage, psp,
    )

    duration_ms = int((time.time() - start) * 1000)

    return {
        "expected_amount": round(expected_amount, 2),
        "mid_market_rate": round(mid_rate, 6),
        "actual_rate": round(actual_rate, 6),
        "platform_fee": round(platform_fee, 2),
        "intermediary_fee": round(intermediary_fee, 2),
        "fx_spread_cost": round(fx_spread_cost, 2),
        "total_fees": round(total_fees, 2),
        "total_leakage": round(leakage, 2),
        "leakage_pct": round(leakage_pct, 2),
        "reconstructed_flow": flow,
        "confidence_score": confidence,
        "explanation": explanation,
        "analysis_duration_ms": duration_ms,
        "recommendations": recommendations,
        "data_source": data_source,
        "fx_rate_source": "live" if live_mid_rate else "hardcoded",
    }


# ─────────────────────────────────────────────────────────────────────────────
# Internal helpers
# ─────────────────────────────────────────────────────────────────────────────

def _reconstruct_flow(
    corridor, corridor_info, amount, settlement_days, psp,
    platform_fee, intermediary_fee, fx_spread_cost,
):
    """Pick most likely route and build flow diagram with fee attribution."""
    routes = corridor_info.get("typical_routes", [])
    if not routes:
        return []

    # Pick route closest to actual settlement time
    best_route = routes[0]
    for route in routes:
        if abs(route.get("typical_days", 3) - settlement_days) < \
           abs(best_route.get("typical_days", 3) - settlement_days):
            best_route = route

    flow = []
    for i, hop in enumerate(best_route.get("hops", [])):
        fee = 0.0
        if hop["type"] == "PSP":
            fee = round(platform_fee, 2)
        elif hop["type"] == "intermediary":
            fee = round(intermediary_fee, 2)
        elif hop["type"] == "fx":
            fee = round(fx_spread_cost, 2)

        flow.append({
            "sequence": i + 1,
            "entity": hop["entity"],
            "type": hop["type"],
            "fee_usd": fee,
            "description": hop.get("description", ""),
        })

    return flow


def _generate_recommendations(
    corridor, corridor_info, actual_cost_pct, fx_spread_pct,
    intermediary_fee, settlement_days, amount_sent,
):
    """Generate actionable recommendations based on analysis results."""
    recs = []
    alternatives = corridor_info.get("alternatives", [])
    corridor_label = corridor.replace("_", "→")

    # ── Rec: FX / Route Optimization ──
    if fx_spread_pct > corridor_info["typical_fx_spread_pct"] * 100 * 0.8:
        # FX spread is high-ish — suggest alternative
        for alt in alternatives:
            if alt["type"] == "fx_platform":
                per_txn_savings = max(0, (fx_spread_pct / 100 - alt["cost_pct"] / 100)) * amount_sent
                annual_savings = per_txn_savings * 12
                if annual_savings < 50:
                    continue
                recs.append({
                    "title": f"Switch {corridor_label} payments to {alt['name']}",
                    "description": (
                        f"{alt['name']} charges {alt['cost_pct']}% all-in for {corridor_label}, "
                        f"vs your effective {fx_spread_pct:.1f}% FX spread alone. "
                        f"Estimated savings: ${per_txn_savings:,.0f} per transaction, "
                        f"${annual_savings:,.0f}/year."
                    ),
                    "category": "route_switch",
                    "estimated_savings": round(per_txn_savings, 2),
                    "estimated_savings_annual": round(annual_savings, 2),
                    "effort": alt.get("effort", "medium"),
                    "risk": "low",
                    "implementation_steps": alt.get("steps", []),
                })
                break  # Only suggest best alternative

    # ── Rec: Batching ──
    if intermediary_fee > 15:
        savings_per_txn = intermediary_fee * 0.8
        annual_savings = savings_per_txn * 12
        recs.append({
            "title": f"Batch {corridor_label} payments weekly instead of daily",
            "description": (
                f"You pay ${intermediary_fee:,.0f}/transaction in intermediary fees. "
                f"Batching 5 daily payments into 1 weekly batch reduces fees by ~80%. "
                f"Savings: ${savings_per_txn:,.0f}/batch, ${annual_savings:,.0f}/year."
            ),
            "category": "batching",
            "estimated_savings": round(savings_per_txn, 2),
            "estimated_savings_annual": round(annual_savings, 2),
            "effort": "low",
            "risk": "medium",
            "implementation_steps": [
                "Survey recipients: confirm weekly payouts are acceptable",
                "Update payout schedule in PSP settings to weekly",
                "Notify all recipients of new schedule",
                "Monitor for complaints in first month",
                "Revert if >10% complain",
            ],
        })

    # ── Rec: Timing ──
    typical_days = corridor_info.get("typical_settlement_days", 2)
    if settlement_days > typical_days + 1:
        delay_days = settlement_days - typical_days
        opportunity_cost = amount_sent * 0.05 * (delay_days / 365)
        annual = opportunity_cost * 12
        if annual > 20:
            recs.append({
                "title": f"Optimize payment timing for {corridor_label}",
                "description": (
                    f"Payments settle in {settlement_days} days vs typical {typical_days}. "
                    f"Initiating on Tue–Thu avoids weekend/holiday delays. "
                    f"Opportunity cost of delay: ${opportunity_cost:,.0f}/transaction."
                ),
                "category": "timing",
                "estimated_savings": round(opportunity_cost, 2),
                "estimated_savings_annual": round(annual, 2),
                "effort": "low",
                "risk": "low",
                "implementation_steps": [
                    "Schedule payouts for Tuesday–Thursday only",
                    "Avoid bank holidays in both origin and destination countries",
                    "Use PSP scheduling feature to automate",
                    "Monitor settlement times for improvement",
                ],
            })

    return recs


def _generate_explanation(
    corridor, amount_sent, currency_sent, amount_received, currency_received,
    mid_rate, actual_rate, total_fees, total_cost_pct,
    platform_fee, intermediary_fee, fx_spread_cost,
    flow, leakage, psp,
):
    """Generate human-readable analysis explanation."""
    corridor_label = corridor.replace("_", "→")
    expected_received = amount_sent * mid_rate

    lines = [
        f"=== Payment Analysis: {corridor_label} ===",
        "",
        f"You sent {currency_sent} {amount_sent:,.2f} and received {currency_received} {amount_received:,.2f}.",
        f"At the mid-market rate ({mid_rate:.4f}), you should have received "
        f"{currency_received} {expected_received:,.2f}.",
        "",
        f"--- Cost Breakdown ---",
        f"  Platform fee ({psp}):  ${platform_fee:,.2f}",
        f"  Intermediary fees:     ${intermediary_fee:,.2f}",
        f"  FX spread:             ${fx_spread_cost:,.2f}",
        f"  ────────────────────────────",
        f"  Total fees:            ${total_fees:,.2f} ({total_cost_pct:.2f}%)",
        "",
        f"--- Payment Route ---",
    ]

    for hop in flow:
        fee_str = f" — ${hop['fee_usd']:,.2f}" if hop['fee_usd'] > 0.01 else ""
        lines.append(f"  {hop['sequence']}. {hop['entity']} ({hop['type']}){fee_str}")

    lines.append("")

    if leakage > 0.01:
        lines.append(
            f"⚠️  EXCESSIVE COST: ${leakage:,.2f} above corridor baseline. "
            f"This payment cost more than typical for {corridor_label}."
        )
    else:
        lines.append(
            f"✅  Cost is within normal range for {corridor_label}."
        )

    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────────
# Demo Data
# ─────────────────────────────────────────────────────────────────────────────

DEMO_PAYMENTS = [
    {
        "reference": "po_demo_001",
        "corridor": "USD_EUR",
        "amount_sent": 10000.00,
        "currency_sent": "USD",
        "amount_received": 8980.00,
        "currency_received": "EUR",
        "initiated_at": "2026-01-15T10:30:00Z",
        "settled_at": "2026-01-18T14:22:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_002",
        "corridor": "USD_EUR",
        "amount_sent": 5000.00,
        "currency_sent": "USD",
        "amount_received": 4530.00,
        "currency_received": "EUR",
        "initiated_at": "2026-01-20T09:00:00Z",
        "settled_at": "2026-01-22T11:15:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_003",
        "corridor": "USD_INR",
        "amount_sent": 8000.00,
        "currency_sent": "USD",
        "amount_received": 644000.00,
        "currency_received": "INR",
        "initiated_at": "2026-01-10T08:00:00Z",
        "settled_at": "2026-01-13T16:30:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_004",
        "corridor": "USD_INR",
        "amount_sent": 3000.00,
        "currency_sent": "USD",
        "amount_received": 243000.00,
        "currency_received": "INR",
        "initiated_at": "2026-01-25T12:00:00Z",
        "settled_at": "2026-01-28T10:45:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_005",
        "corridor": "USD_GBP",
        "amount_sent": 15000.00,
        "currency_sent": "USD",
        "amount_received": 11550.00,
        "currency_received": "GBP",
        "initiated_at": "2026-02-01T14:00:00Z",
        "settled_at": "2026-02-03T09:30:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_006",
        "corridor": "USD_GBP",
        "amount_sent": 7000.00,
        "currency_sent": "USD",
        "amount_received": 5480.00,
        "currency_received": "GBP",
        "initiated_at": "2026-02-05T11:00:00Z",
        "settled_at": "2026-02-06T15:20:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_007",
        "corridor": "USD_EUR",
        "amount_sent": 20000.00,
        "currency_sent": "USD",
        "amount_received": 17900.00,
        "currency_received": "EUR",
        "initiated_at": "2026-02-07T10:00:00Z",
        "settled_at": "2026-02-10T13:45:00Z",
        "psp": "stripe",
    },
    {
        "reference": "po_demo_008",
        "corridor": "USD_INR",
        "amount_sent": 12000.00,
        "currency_sent": "USD",
        "amount_received": 966000.00,
        "currency_received": "INR",
        "initiated_at": "2026-02-03T09:00:00Z",
        "settled_at": "2026-02-07T17:00:00Z",
        "psp": "stripe",
    },
]
