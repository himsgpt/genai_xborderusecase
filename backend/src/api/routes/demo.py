"""Demo route — one-click full pipeline for testing."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, UserModel, PaymentModel, AnalysisModel, RecommendationModel
from ...infrastructure.auth import hash_password, create_token
from ...infrastructure.config import settings
from ...infrastructure.fx_rates import fetch_live_rate
from ...domain.services import analyze_payment, DEMO_PAYMENTS

logger = logging.getLogger("xborder")
router = APIRouter(prefix="/api/demo", tags=["demo"])


@router.post("/full-pipeline")
async def demo_full_pipeline(db: AsyncSession = Depends(get_db)):
    """One-click demo: Create user -> Load payments -> Analyze -> Return summary. No auth required."""
    # Create or get demo user
    demo_email = "demo@xborder.ai"
    result = await db.execute(select(UserModel).where(UserModel.email == demo_email))
    user = result.scalar_one_or_none()
    if not user:
        user = UserModel(email=demo_email, password_hash=hash_password("demo123"), name="Demo User", company="Demo Corp")
        db.add(user)
        await db.commit()
        await db.refresh(user)

    user_id = str(user.id)

    # Clean existing demo data
    await db.execute(RecommendationModel.__table__.delete().where(RecommendationModel.user_id == user.id))
    await db.execute(AnalysisModel.__table__.delete().where(AnalysisModel.user_id == user.id))
    await db.execute(PaymentModel.__table__.delete().where(PaymentModel.user_id == user.id))
    await db.commit()

    # Load demo payments
    for demo in DEMO_PAYMENTS:
        db.add(PaymentModel(
            user_id=user.id, reference=demo["reference"], corridor=demo["corridor"],
            amount_sent=demo["amount_sent"], currency_sent=demo["currency_sent"],
            amount_received=demo["amount_received"], currency_received=demo["currency_received"],
            initiated_at=datetime.fromisoformat(demo["initiated_at"].replace("Z", "+00:00")),
            settled_at=datetime.fromisoformat(demo["settled_at"].replace("Z", "+00:00")) if demo.get("settled_at") else None,
            psp=demo.get("psp", "stripe"), status="completed",
        ))
    await db.commit()

    # Run analysis
    payments_result = await db.execute(select(PaymentModel).where(PaymentModel.user_id == user.id))
    payments = payments_result.scalars().all()

    total_leakage = total_fees = total_sent = 0.0
    all_recs = []
    use_live_fx = settings.fx_rate_source == "live"

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

        analysis = AnalysisModel(
            payment_id=payment.id, user_id=user.id,
            expected_amount=result["expected_amount"], mid_market_rate=result["mid_market_rate"],
            actual_rate=result["actual_rate"], platform_fee=result["platform_fee"],
            intermediary_fee=result["intermediary_fee"], fx_spread_cost=result["fx_spread_cost"],
            total_fees=result["total_fees"], total_leakage=result["total_leakage"],
            leakage_pct=result["leakage_pct"], reconstructed_flow=result["reconstructed_flow"],
            confidence_score=result["confidence_score"], explanation=result["explanation"],
            analysis_duration_ms=result["analysis_duration_ms"],
        )
        db.add(analysis)
        await db.flush()
        total_leakage += result["total_leakage"]
        total_fees += result["total_fees"]
        total_sent += payment.amount_sent

        for rec in result.get("recommendations", []):
            db.add(RecommendationModel(
                analysis_id=analysis.id, user_id=user.id,
                title=rec["title"], description=rec["description"], category=rec["category"],
                estimated_savings=rec["estimated_savings"], estimated_savings_annual=rec["estimated_savings_annual"],
                effort=rec["effort"], risk=rec["risk"], implementation_steps=rec["implementation_steps"],
                status="pending",
            ))
            all_recs.append(rec)
    await db.commit()

    token = create_token(user_id)
    annual_savings = total_leakage * 12
    fx_source = "live (ECB/Frankfurter)" if use_live_fx else "hardcoded"
    return {
        "status": "success",
        "message": "Full demo pipeline complete!",
        "auth": {"token": token, "user_id": user_id, "email": demo_email},
        "summary": {
            "payments_analyzed": len(payments), "total_sent_usd": round(total_sent, 2),
            "total_fees_usd": round(total_fees, 2), "total_leakage_usd": round(total_leakage, 2),
            "avg_cost_pct": round(total_fees / total_sent * 100, 2) if total_sent else 0,
            "potential_annual_savings_usd": round(annual_savings, 2),
            "headline": f"Found ${total_leakage:,.0f} in hidden costs across {len(payments)} payments. That's ${annual_savings:,.0f}/year!",
        },
        "fx_rate_source": fx_source,
        "recommendations_count": len(all_recs),
        "top_recommendations": sorted(all_recs, key=lambda r: r["estimated_savings_annual"], reverse=True)[:3],
    }
