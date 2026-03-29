"""Demo route — one-click full pipeline for testing."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, UserModel, PaymentModel, AnalysisModel, RecommendationModel
from ...infrastructure.auth import hash_password, create_token
from ...infrastructure.config import settings
from ...infrastructure.fx_rates import fetch_live_rate, fetch_rates_batch
from ...domain.services import analyze_payment
from ...domain.services.corridor_data import CORRIDORS
from ...agents.analysis_agent import enhance_single_analysis, enhance_batch_analysis

logger = logging.getLogger("xborder")
router = APIRouter(prefix="/api/demo", tags=["demo"])

DEMO_PAYMENT_TEMPLATES = [
    {"ref": "demo_001", "corridor": "USD_EUR", "sent": 10000, "psp": "stripe",  "spread_pct": 2.5,  "init": "2026-01-15T10:30:00Z", "settle": "2026-01-18T14:22:00Z"},
    {"ref": "demo_002", "corridor": "USD_EUR", "sent": 5000,  "psp": "wise",    "spread_pct": 0.8,  "init": "2026-01-20T09:00:00Z", "settle": "2026-01-22T11:15:00Z"},
    {"ref": "demo_003", "corridor": "USD_INR", "sent": 8000,  "psp": "stripe",  "spread_pct": 3.2,  "init": "2026-01-10T08:00:00Z", "settle": "2026-01-13T16:30:00Z"},
    {"ref": "demo_004", "corridor": "USD_INR", "sent": 3000,  "psp": "paypal",  "spread_pct": 4.5,  "init": "2026-01-25T12:00:00Z", "settle": "2026-01-28T10:45:00Z"},
    {"ref": "demo_005", "corridor": "USD_GBP", "sent": 15000, "psp": "stripe",  "spread_pct": 1.9,  "init": "2026-02-01T14:00:00Z", "settle": "2026-02-03T09:30:00Z"},
    {"ref": "demo_006", "corridor": "USD_GBP", "sent": 7000,  "psp": "bank_direct", "spread_pct": 3.8, "init": "2026-02-05T11:00:00Z", "settle": "2026-02-08T15:20:00Z"},
    {"ref": "demo_007", "corridor": "USD_EUR", "sent": 20000, "psp": "stripe",  "spread_pct": 2.1,  "init": "2026-02-07T10:00:00Z", "settle": "2026-02-10T13:45:00Z"},
    {"ref": "demo_008", "corridor": "USD_INR", "sent": 12000, "psp": "stripe",  "spread_pct": 3.5,  "init": "2026-02-03T09:00:00Z", "settle": "2026-02-07T17:00:00Z"},
]


@router.post("/full-pipeline")
async def demo_full_pipeline(db: AsyncSession = Depends(get_db)):
    """One-click demo: Create user -> Load payments -> Analyze -> Return summary. No auth required."""
    demo_email = "demo@xborder.ai"
    result = await db.execute(select(UserModel).where(UserModel.email == demo_email))
    user = result.scalar_one_or_none()
    if not user:
        user = UserModel(email=demo_email, password_hash=hash_password("demo123"), name="Demo User", company="Demo Corp")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    user_id = str(user.id)

    await db.execute(RecommendationModel.__table__.delete().where(RecommendationModel.user_id == user.id))
    await db.execute(AnalysisModel.__table__.delete().where(AnalysisModel.user_id == user.id))
    await db.execute(PaymentModel.__table__.delete().where(PaymentModel.user_id == user.id))
    await db.commit()

    # Fetch live FX rates so demo amounts are realistic
    live_rates = await fetch_rates_batch("USD", ["EUR", "INR", "GBP"])
    corridor_rates = {
        "USD_EUR": live_rates.get("EUR", 0.85),
        "USD_INR": live_rates.get("INR", 83.5),
        "USD_GBP": live_rates.get("GBP", 0.74),
    }

    for tmpl in DEMO_PAYMENT_TEMPLATES:
        mid_rate = corridor_rates.get(tmpl["corridor"], 1.0)
        spread = tmpl["spread_pct"] / 100.0
        effective_rate = mid_rate * (1 - spread)
        received = round(tmpl["sent"] * effective_rate, 2)
        cur_from, cur_to = tmpl["corridor"].split("_")

        db.add(PaymentModel(
            user_id=user.id, reference=tmpl["ref"], corridor=tmpl["corridor"],
            amount_sent=tmpl["sent"], currency_sent=cur_from,
            amount_received=received, currency_received=cur_to,
            initiated_at=datetime.fromisoformat(tmpl["init"].replace("Z", "+00:00")),
            settled_at=datetime.fromisoformat(tmpl["settle"].replace("Z", "+00:00")),
            psp=tmpl["psp"], status="completed",
        ))
    await db.commit()

    # Run analysis
    payments_result = await db.execute(select(PaymentModel).where(PaymentModel.user_id == user.id))
    payments = payments_result.scalars().all()

    total_leakage = total_fees = total_sent = 0.0
    all_recs = []
    seen_rec_titles = set()
    use_live_fx = settings.fx_rate_source == "live"

    batch_analysis_data = []
    ai_enhanced = False

    for payment in payments:
        live_rate = None
        if use_live_fx:
            live_rate = await fetch_live_rate(payment.currency_sent, payment.currency_received)

        result = analyze_payment(
            corridor=payment.corridor, amount_sent=payment.amount_sent,
            currency_sent=payment.currency_sent, amount_received=payment.amount_received,
            currency_received=payment.currency_received, initiated_at=payment.initiated_at,
            settled_at=payment.settled_at, psp=payment.psp,
            live_mid_rate=live_rate,
        )
        if "error" in result:
            continue

        corridor_info = CORRIDORS.get(payment.corridor, {})
        settlement_days = 0
        if payment.settled_at and payment.initiated_at:
            settlement_days = max(0, (payment.settled_at - payment.initiated_at).days)

        # LLM enhancement per payment
        llm_result = await enhance_single_analysis(
            corridor=payment.corridor, amount_sent=payment.amount_sent,
            currency_sent=payment.currency_sent, amount_received=payment.amount_received,
            currency_received=payment.currency_received, mid_rate=result["mid_market_rate"],
            actual_rate=result["actual_rate"], total_fees=result["total_fees"],
            total_cost_pct=(result["total_fees"] / payment.amount_sent * 100) if payment.amount_sent else 0,
            platform_fee=result["platform_fee"], intermediary_fee=result["intermediary_fee"],
            fx_spread_cost=result["fx_spread_cost"], leakage=result["total_leakage"],
            leakage_pct=result["leakage_pct"], psp=payment.psp,
            settlement_days=settlement_days, flow=result["reconstructed_flow"],
            data_source=result.get("data_source", "heuristic"), corridor_info=corridor_info,
        )

        explanation = result["explanation"]
        recs_to_use = result.get("recommendations", [])
        if llm_result:
            ai_enhanced = True
            if llm_result.get("explanation"):
                explanation = llm_result["explanation"]
            if llm_result.get("recommendations"):
                recs_to_use = llm_result["recommendations"]
            if llm_result.get("key_insight"):
                explanation += f"\n\n💡 Key Insight: {llm_result['key_insight']}"

        analysis = AnalysisModel(
            payment_id=payment.id, user_id=user.id,
            expected_amount=result["expected_amount"], mid_market_rate=result["mid_market_rate"],
            actual_rate=result["actual_rate"], platform_fee=result["platform_fee"],
            intermediary_fee=result["intermediary_fee"], fx_spread_cost=result["fx_spread_cost"],
            total_fees=result["total_fees"], total_leakage=result["total_leakage"],
            leakage_pct=result["leakage_pct"], reconstructed_flow=result["reconstructed_flow"],
            confidence_score=result["confidence_score"], explanation=explanation,
            analysis_duration_ms=result["analysis_duration_ms"],
        )
        db.add(analysis)
        await db.flush()
        total_leakage += result["total_leakage"]
        total_fees += result["total_fees"]
        total_sent += payment.amount_sent

        batch_analysis_data.append({
            "corridor": payment.corridor, "amount_sent": payment.amount_sent,
            "total_fees": result["total_fees"], "leakage": result["total_leakage"],
            "total_cost_pct": (result["total_fees"] / payment.amount_sent * 100) if payment.amount_sent else 0,
            "psp": payment.psp,
        })

        for rec in recs_to_use:
            title = rec.get("title", "Recommendation")
            if title not in seen_rec_titles:
                db.add(RecommendationModel(
                    analysis_id=analysis.id, user_id=user.id,
                    title=title,
                    description=rec.get("description", ""),
                    category=rec.get("category", "general"),
                    estimated_savings=rec.get("estimated_savings", 0),
                    estimated_savings_annual=rec.get("estimated_savings_annual", 0),
                    effort=rec.get("effort", "medium"),
                    risk=rec.get("risk", "low"),
                    implementation_steps=rec.get("implementation_steps", []),
                    status="pending",
                ))
                seen_rec_titles.add(title)
                all_recs.append(rec)

    # Portfolio-level LLM analysis
    batch_result = await enhance_batch_analysis(batch_analysis_data)
    if batch_result and batch_result.get("recommendations"):
        ai_enhanced = True
        for rec in batch_result["recommendations"]:
            title = rec.get("title", "Portfolio Recommendation")
            if title not in seen_rec_titles:
                db.add(RecommendationModel(
                    analysis_id=analysis.id, user_id=user.id,
                    title=title,
                    description=rec.get("description", ""),
                    category=rec.get("category", "portfolio"),
                    estimated_savings=rec.get("estimated_savings", 0),
                    estimated_savings_annual=rec.get("estimated_savings_annual", 0),
                    effort=rec.get("effort", "medium"),
                    risk=rec.get("risk", "low"),
                    implementation_steps=rec.get("implementation_steps", []),
                    status="pending",
                ))
                seen_rec_titles.add(title)
                all_recs.append(rec)

    await db.commit()

    token = create_token(user_id)
    annual_savings = total_leakage * 12
    fx_source = "live (ECB/Frankfurter)" if use_live_fx else "hardcoded"

    headline = f"Found ${total_leakage:,.0f} in hidden costs across {len(payments)} payments. That's ${annual_savings:,.0f}/year!"
    if batch_result and batch_result.get("key_insight"):
        headline += f" — {batch_result['key_insight']}"

    return {
        "status": "success",
        "message": "Full demo pipeline complete!",
        "auth": {"token": token, "user_id": user_id, "email": demo_email},
        "summary": {
            "payments_analyzed": len(payments), "total_sent_usd": round(total_sent, 2),
            "total_fees_usd": round(total_fees, 2), "total_leakage_usd": round(total_leakage, 2),
            "avg_cost_pct": round(total_fees / total_sent * 100, 2) if total_sent else 0,
            "potential_annual_savings_usd": round(annual_savings, 2),
            "headline": headline,
        },
        "fx_rate_source": fx_source,
        "ai_enhanced": ai_enhanced,
        "recommendations_count": len(all_recs),
        "top_recommendations": sorted(
            all_recs, key=lambda r: r.get("estimated_savings_annual", 0), reverse=True,
        )[:5],
    }
