"""Analysis routes — run analysis, get summary, list/detail."""
import logging
from collections import defaultdict
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, PaymentModel, AnalysisModel, RecommendationModel
from ...infrastructure.auth import get_current_user_id
from ...infrastructure.config import settings
from ...infrastructure.fx_rates import fetch_live_rate
from ...domain.services import analyze_payment
from ..schemas import AnalysisResponse, AnalysisSummary, CorridorSummary

logger = logging.getLogger("xborder")
router = APIRouter(prefix="/api/analysis", tags=["analysis"])


def _to_response(a: AnalysisModel) -> AnalysisResponse:
    return AnalysisResponse(
        id=str(a.id), payment_id=str(a.payment_id),
        expected_amount=a.expected_amount or 0, mid_market_rate=a.mid_market_rate or 0,
        actual_rate=a.actual_rate or 0, platform_fee=a.platform_fee or 0,
        intermediary_fee=a.intermediary_fee or 0, fx_spread_cost=a.fx_spread_cost or 0,
        total_fees=a.total_fees or 0, total_leakage=a.total_leakage or 0,
        leakage_pct=a.leakage_pct or 0, reconstructed_flow=a.reconstructed_flow or [],
        confidence_score=a.confidence_score or 0, explanation=a.explanation,
        analyzed_at=a.analyzed_at, analysis_duration_ms=a.analysis_duration_ms,
    )


@router.post("/run-all")
@router.post("/run")
async def run_analysis_all(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Run analysis on ALL unanalyzed payments for this user."""
    analyzed_ids_q = select(AnalysisModel.payment_id).where(AnalysisModel.user_id == user_id)
    result = await db.execute(
        select(PaymentModel).where(PaymentModel.user_id == user_id).where(PaymentModel.id.notin_(analyzed_ids_q))
    )
    payments = result.scalars().all()
    if not payments:
        return {"message": "All payments already analyzed."}

    analyzed_count = 0
    recs_count = 0
    use_live_fx = settings.fx_rate_source == "live"

    for payment in payments:
        # Fetch live mid-market rate if enabled
        live_rate = None
        if use_live_fx:
            live_rate = await fetch_live_rate(payment.currency_sent, payment.currency_received)

        # Extract Stripe fee details from raw_data if available
        stripe_fees = None
        stripe_fx_rate = None
        if payment.raw_data and isinstance(payment.raw_data, dict):
            stripe_fees = payment.raw_data.get("fee_details")
            stripe_fx_rate = payment.raw_data.get("exchange_rate")

        result = analyze_payment(
            corridor=payment.corridor, amount_sent=payment.amount_sent,
            currency_sent=payment.currency_sent, amount_received=payment.amount_received,
            currency_received=payment.currency_received, initiated_at=payment.initiated_at,
            settled_at=payment.settled_at, psp=payment.psp,
            live_mid_rate=live_rate,
            stripe_fee_details=stripe_fees,
            stripe_exchange_rate=stripe_fx_rate,
        )
        if "error" in result:
            logger.warning(f"Skipping payment {payment.id}: {result['error']}")
            continue

        analysis = AnalysisModel(
            payment_id=payment.id, user_id=user_id,
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
        analyzed_count += 1

        for rec in result.get("recommendations", []):
            db.add(RecommendationModel(
                analysis_id=analysis.id, user_id=user_id,
                title=rec["title"], description=rec["description"], category=rec["category"],
                estimated_savings=rec["estimated_savings"], estimated_savings_annual=rec["estimated_savings_annual"],
                effort=rec["effort"], risk=rec["risk"], implementation_steps=rec["implementation_steps"],
                status="pending",
            ))
            recs_count += 1

    await db.commit()

    # Build summary for response
    total_sent = sum(p.amount_sent for p in payments)
    total_leakage = 0
    total_fees_sum = 0
    # Re-query analyses we just created
    result = await db.execute(
        select(AnalysisModel).where(AnalysisModel.user_id == user_id)
    )
    for a in result.scalars().all():
        total_leakage += (a.total_leakage or 0)
        total_fees_sum += (a.total_fees or 0)

    fx_source = "live (ECB/Frankfurter)" if use_live_fx else "hardcoded"
    logger.info(f"Analyzed {analyzed_count} payments (FX: {fx_source}), generated {recs_count} recommendations")

    return {
        "message": f"Analysis complete! {analyzed_count} payments analyzed, {recs_count} recommendations generated.",
        "analyzed": analyzed_count,
        "recommendations_generated": recs_count,
        "fx_rate_source": fx_source,
        "summary": {
            "total_leakage": round(total_leakage, 2),
            "total_fees": round(total_fees_sum, 2),
        },
    }


@router.get("/summary", response_model=AnalysisSummary)
async def get_analysis_summary(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Aggregated analysis summary — total leakage, savings potential, corridor breakdown."""
    result = await db.execute(
        select(AnalysisModel, PaymentModel).join(PaymentModel, AnalysisModel.payment_id == PaymentModel.id)
        .where(AnalysisModel.user_id == user_id)
    )
    rows = result.all()
    if not rows:
        raise HTTPException(status_code=404, detail="No analyses found. Run POST /api/analysis/run-all first.")

    total_sent = total_fees = total_leakage = 0.0
    corridor_data = defaultdict(lambda: {"payments": 0, "total_sent": 0, "total_fees": 0, "total_leakage": 0})
    for analysis, payment in rows:
        total_sent += payment.amount_sent
        total_fees += analysis.total_fees
        total_leakage += analysis.total_leakage
        cd = corridor_data[payment.corridor]
        cd["payments"] += 1
        cd["total_sent"] += payment.amount_sent
        cd["total_fees"] += analysis.total_fees
        cd["total_leakage"] += analysis.total_leakage

    avg_cost_pct = (total_fees / total_sent * 100) if total_sent else 0
    annual_savings = total_leakage * 12

    corridor_summaries = [
        CorridorSummary(
            corridor=code.replace("_", "->"), payments=cd["payments"],
            total_sent=round(cd["total_sent"], 2), total_fees=round(cd["total_fees"], 2),
            total_leakage=round(cd["total_leakage"], 2),
            avg_cost_pct=round((cd["total_fees"] / cd["total_sent"] * 100) if cd["total_sent"] else 0, 2),
            top_issue="FX spread above benchmark" if cd["total_leakage"] > 0 else "Within normal range",
        )
        for code, cd in corridor_data.items()
    ]

    rec_result = await db.execute(
        select(RecommendationModel).where(RecommendationModel.user_id == user_id)
        .where(RecommendationModel.status == "pending")
        .order_by(RecommendationModel.estimated_savings_annual.desc()).limit(5)
    )
    top_recs = [{"title": r.title, "annual_savings": r.estimated_savings_annual, "effort": r.effort}
                for r in rec_result.scalars().all()]

    return AnalysisSummary(
        total_payments_analyzed=len(rows), total_sent_usd=round(total_sent, 2),
        total_fees_usd=round(total_fees, 2), total_leakage_usd=round(total_leakage, 2),
        avg_cost_pct=round(avg_cost_pct, 2), potential_annual_savings_usd=round(annual_savings, 2),
        headline=f"You're leaking ${total_leakage:,.0f} on {len(rows)} payments. Annualized: ${annual_savings:,.0f}/year in potential savings.",
        corridors=corridor_summaries, top_recommendations=top_recs,
    )


@router.get("", response_model=list[AnalysisResponse])
async def list_analyses(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """List all analyses for this user."""
    result = await db.execute(
        select(AnalysisModel).where(AnalysisModel.user_id == user_id).order_by(AnalysisModel.analyzed_at.desc())
    )
    return [_to_response(a) for a in result.scalars().all()]


@router.get("/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_detail(analysis_id: str, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Get detailed analysis for a specific payment."""
    result = await db.execute(
        select(AnalysisModel).where(AnalysisModel.id == analysis_id).where(AnalysisModel.user_id == user_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _to_response(analysis)
