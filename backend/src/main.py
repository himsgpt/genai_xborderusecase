"""
Cross-Border Payment Intelligence Platform — FastAPI Application
All routes in one file for MVP speed. Refactor into routers later.
"""
import logging
from datetime import datetime, timezone
from contextlib import asynccontextmanager
from collections import defaultdict

import traceback
from fastapi import FastAPI, Depends, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .database import engine, Base, AsyncSessionLocal, get_db
from .database import UserModel, PaymentModel, AnalysisModel, RecommendationModel
from .schemas import (
    UserRegister, UserLogin, TokenResponse, UserResponse,
    PaymentCreate, PaymentResponse,
    AnalysisResponse, AnalysisSummary, CorridorSummary,
    RecommendationResponse, RecommendationUpdate,
)
from .auth import hash_password, verify_password, create_token, get_current_user_id
from .analysis import analyze_payment, DEMO_PAYMENTS
from .corridor_data import get_supported_corridors

# ─── Logging ─────────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO if settings.environment == "production" else logging.DEBUG,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("xborder")


# ─── Lifespan ────────────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"Starting XBorder Payment Intelligence [{settings.environment}]")
    logger.info(f"LLM provider: {settings.llm_provider}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables created / verified")
    yield
    logger.info("Shutting down")
    await engine.dispose()


# ─── App ─────────────────────────────────────────────────────────────────────

app = FastAPI(
    title="XBorder Payment Intelligence API",
    description="AI-powered cross-border payment analysis — expose hidden fees, optimize routes",
    version="0.1.0",
    lifespan=lifespan,
)

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}:\n{traceback.format_exc()}")
    return JSONResponse(status_code=500, content={"detail": str(exc)})


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ═══════════════════════════════════════════════════════════════════════════════
# HEALTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "XBorder Payment Intelligence",
        "version": "0.1.0",
        "environment": settings.environment,
        "llm_provider": settings.llm_provider,
    }


@app.get("/")
async def root():
    return {
        "message": "XBorder Payment Intelligence API",
        "docs": "/docs",
        "health": "/health",
        "corridors": get_supported_corridors(),
    }


# ═══════════════════════════════════════════════════════════════════════════════
# AUTH
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/auth/register", response_model=TokenResponse)
async def register(data: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user account."""
    # Check duplicate
    existing = await db.execute(select(UserModel).where(UserModel.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = UserModel(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
        company=data.company,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)

    token = create_token(str(user.id))
    logger.info(f"User registered: {user.email}")
    return TokenResponse(
        access_token=token, user_id=str(user.id), email=user.email,
    )


@app.post("/api/auth/login", response_model=TokenResponse)
async def login(data: UserLogin, db: AsyncSession = Depends(get_db)):
    """Login and get JWT token."""
    result = await db.execute(select(UserModel).where(UserModel.email == data.email))
    user = result.scalar_one_or_none()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid email or password")

    token = create_token(str(user.id))
    logger.info(f"User logged in: {user.email}")
    return TokenResponse(
        access_token=token, user_id=str(user.id), email=user.email,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# PAYMENTS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/payments", response_model=list[PaymentResponse])
async def list_payments(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all payments for the authenticated user."""
    result = await db.execute(
        select(PaymentModel)
        .where(PaymentModel.user_id == user_id)
        .order_by(PaymentModel.initiated_at.desc())
    )
    payments = result.scalars().all()
    return [_payment_to_response(p) for p in payments]


@app.post("/api/payments", response_model=PaymentResponse, status_code=201)
async def create_payment(
    data: PaymentCreate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Add a payment record manually."""
    payment = PaymentModel(
        user_id=user_id,
        reference=data.reference,
        corridor=data.corridor,
        amount_sent=data.amount_sent,
        currency_sent=data.currency_sent,
        amount_received=data.amount_received,
        currency_received=data.currency_received,
        initiated_at=data.initiated_at,
        settled_at=data.settled_at,
        psp=data.psp,
        status="completed",
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return _payment_to_response(payment)


@app.post("/api/payments/demo")
async def load_demo_payments(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Load 8 realistic demo payments across 3 corridors.
    Includes payments with varying levels of cost/leakage.
    """
    # Check if demo data already loaded
    existing = await db.execute(
        select(func.count(PaymentModel.id))
        .where(PaymentModel.user_id == user_id)
        .where(PaymentModel.reference.like("po_demo_%"))
    )
    count = existing.scalar()
    if count and count > 0:
        return {"message": f"Demo data already loaded ({count} payments). Use /api/analysis/run-all to analyze."}

    created = []
    for demo in DEMO_PAYMENTS:
        payment = PaymentModel(
            user_id=user_id,
            reference=demo["reference"],
            corridor=demo["corridor"],
            amount_sent=demo["amount_sent"],
            currency_sent=demo["currency_sent"],
            amount_received=demo["amount_received"],
            currency_received=demo["currency_received"],
            initiated_at=datetime.fromisoformat(demo["initiated_at"].replace("Z", "+00:00")),
            settled_at=datetime.fromisoformat(demo["settled_at"].replace("Z", "+00:00")) if demo.get("settled_at") else None,
            psp=demo.get("psp", "stripe"),
            status="completed",
        )
        db.add(payment)
        created.append(demo["reference"])

    await db.commit()
    logger.info(f"Loaded {len(created)} demo payments for user {user_id}")
    return {
        "message": f"Loaded {len(created)} demo payments across 3 corridors (USD→EUR, USD→INR, USD→GBP)",
        "payments_created": len(created),
        "total_sent_usd": sum(d["amount_sent"] for d in DEMO_PAYMENTS),
        "next_step": "POST /api/analysis/run-all to analyze all payments",
    }


# ═══════════════════════════════════════════════════════════════════════════════
# ANALYSIS
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/analysis/run-all")
async def run_analysis_all(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Run analysis on ALL unanalyzed payments for this user.
    Returns summary of findings.
    """
    # Get payments without analysis
    analyzed_ids_q = select(AnalysisModel.payment_id).where(AnalysisModel.user_id == user_id)
    result = await db.execute(
        select(PaymentModel)
        .where(PaymentModel.user_id == user_id)
        .where(PaymentModel.id.notin_(analyzed_ids_q))
    )
    payments = result.scalars().all()

    if not payments:
        return {"message": "All payments already analyzed. GET /api/analysis/summary for results."}

    analyzed_count = 0
    recs_count = 0

    for payment in payments:
        # Run analysis engine
        result = analyze_payment(
            corridor=payment.corridor,
            amount_sent=payment.amount_sent,
            currency_sent=payment.currency_sent,
            amount_received=payment.amount_received,
            currency_received=payment.currency_received,
            initiated_at=payment.initiated_at,
            settled_at=payment.settled_at,
            psp=payment.psp,
        )

        if "error" in result:
            logger.warning(f"Skipping payment {payment.id}: {result['error']}")
            continue

        # Store analysis
        analysis = AnalysisModel(
            payment_id=payment.id,
            user_id=user_id,
            expected_amount=result["expected_amount"],
            mid_market_rate=result["mid_market_rate"],
            actual_rate=result["actual_rate"],
            platform_fee=result["platform_fee"],
            intermediary_fee=result["intermediary_fee"],
            fx_spread_cost=result["fx_spread_cost"],
            total_fees=result["total_fees"],
            total_leakage=result["total_leakage"],
            leakage_pct=result["leakage_pct"],
            reconstructed_flow=result["reconstructed_flow"],
            confidence_score=result["confidence_score"],
            explanation=result["explanation"],
            analysis_duration_ms=result["analysis_duration_ms"],
        )
        db.add(analysis)
        await db.flush()  # Get analysis.id
        analyzed_count += 1

        # Store recommendations
        for rec in result.get("recommendations", []):
            recommendation = RecommendationModel(
                analysis_id=analysis.id,
                user_id=user_id,
                title=rec["title"],
                description=rec["description"],
                category=rec["category"],
                estimated_savings=rec["estimated_savings"],
                estimated_savings_annual=rec["estimated_savings_annual"],
                effort=rec["effort"],
                risk=rec["risk"],
                implementation_steps=rec["implementation_steps"],
                status="pending",
            )
            db.add(recommendation)
            recs_count += 1

    await db.commit()
    logger.info(f"Analyzed {analyzed_count} payments, generated {recs_count} recommendations")

    return {
        "message": f"Analysis complete! {analyzed_count} payments analyzed, {recs_count} recommendations generated.",
        "payments_analyzed": analyzed_count,
        "recommendations_generated": recs_count,
        "next_steps": [
            "GET /api/analysis/summary — see total leakage & savings potential",
            "GET /api/analysis — see all analysis details",
            "GET /api/recommendations — see actionable recommendations",
        ],
    }


@app.get("/api/analysis/summary", response_model=AnalysisSummary)
async def get_analysis_summary(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Aggregated analysis summary — the money shot.
    Shows total leakage, savings potential, corridor breakdown.
    """
    # Fetch all analyses with payment data
    result = await db.execute(
        select(AnalysisModel, PaymentModel)
        .join(PaymentModel, AnalysisModel.payment_id == PaymentModel.id)
        .where(AnalysisModel.user_id == user_id)
    )
    rows = result.all()

    if not rows:
        raise HTTPException(status_code=404, detail="No analyses found. Run POST /api/analysis/run-all first.")

    total_sent = 0.0
    total_fees = 0.0
    total_leakage = 0.0
    corridor_data = defaultdict(lambda: {
        "payments": 0, "total_sent": 0, "total_fees": 0, "total_leakage": 0,
    })

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
    annual_savings = total_leakage * 12  # Rough annualization

    # Build corridor summaries
    corridor_summaries = []
    for code, cd in corridor_data.items():
        avg_pct = (cd["total_fees"] / cd["total_sent"] * 100) if cd["total_sent"] else 0
        top_issue = "FX spread above benchmark" if cd["total_leakage"] > 0 else "Within normal range"
        corridor_summaries.append(CorridorSummary(
            corridor=code.replace("_", "→"),
            payments=cd["payments"],
            total_sent=round(cd["total_sent"], 2),
            total_fees=round(cd["total_fees"], 2),
            total_leakage=round(cd["total_leakage"], 2),
            avg_cost_pct=round(avg_pct, 2),
            top_issue=top_issue,
        ))

    # Top recommendations
    rec_result = await db.execute(
        select(RecommendationModel)
        .where(RecommendationModel.user_id == user_id)
        .where(RecommendationModel.status == "pending")
        .order_by(RecommendationModel.estimated_savings_annual.desc())
        .limit(5)
    )
    top_recs = [
        {"title": r.title, "annual_savings": r.estimated_savings_annual, "effort": r.effort}
        for r in rec_result.scalars().all()
    ]

    headline = (
        f"You're leaking ${total_leakage:,.0f} on {len(rows)} payments. "
        f"Annualized: ${annual_savings:,.0f}/year in potential savings."
    )

    return AnalysisSummary(
        total_payments_analyzed=len(rows),
        total_sent_usd=round(total_sent, 2),
        total_fees_usd=round(total_fees, 2),
        total_leakage_usd=round(total_leakage, 2),
        avg_cost_pct=round(avg_cost_pct, 2),
        potential_annual_savings_usd=round(annual_savings, 2),
        headline=headline,
        corridors=corridor_summaries,
        top_recommendations=top_recs,
    )


@app.get("/api/analysis", response_model=list[AnalysisResponse])
async def list_analyses(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all analyses for this user."""
    result = await db.execute(
        select(AnalysisModel)
        .where(AnalysisModel.user_id == user_id)
        .order_by(AnalysisModel.analyzed_at.desc())
    )
    analyses = result.scalars().all()
    return [_analysis_to_response(a) for a in analyses]


@app.get("/api/analysis/{analysis_id}", response_model=AnalysisResponse)
async def get_analysis_detail(
    analysis_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get detailed analysis for a specific payment."""
    result = await db.execute(
        select(AnalysisModel)
        .where(AnalysisModel.id == analysis_id)
        .where(AnalysisModel.user_id == user_id)
    )
    analysis = result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    return _analysis_to_response(analysis)


# ═══════════════════════════════════════════════════════════════════════════════
# RECOMMENDATIONS
# ═══════════════════════════════════════════════════════════════════════════════

@app.get("/api/recommendations", response_model=list[RecommendationResponse])
async def list_recommendations(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all recommendations, ordered by potential savings."""
    result = await db.execute(
        select(RecommendationModel)
        .where(RecommendationModel.user_id == user_id)
        .order_by(RecommendationModel.estimated_savings_annual.desc())
    )
    recs = result.scalars().all()
    return [_rec_to_response(r) for r in recs]


@app.patch("/api/recommendations/{rec_id}")
async def update_recommendation_status(
    rec_id: str,
    data: RecommendationUpdate,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update recommendation status (pending → in_progress → implemented | dismissed)."""
    result = await db.execute(
        select(RecommendationModel)
        .where(RecommendationModel.id == rec_id)
        .where(RecommendationModel.user_id == user_id)
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    valid_statuses = {"pending", "in_progress", "implemented", "dismissed"}
    if data.status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    rec.status = data.status
    await db.commit()
    return {"message": f"Recommendation updated to '{data.status}'", "id": rec_id}


# ═══════════════════════════════════════════════════════════════════════════════
# DEMO — One-click full pipeline
# ═══════════════════════════════════════════════════════════════════════════════

@app.post("/api/demo/full-pipeline")
async def demo_full_pipeline(db: AsyncSession = Depends(get_db)):
    """
    One-click demo: Create user → Load payments → Analyze → Return summary.
    No auth required. Perfect for testing.
    """
    # Create or get demo user
    demo_email = "demo@xborder.ai"
    result = await db.execute(select(UserModel).where(UserModel.email == demo_email))
    user = result.scalar_one_or_none()

    if not user:
        user = UserModel(
            email=demo_email,
            password_hash=hash_password("demo123"),
            name="Demo User",
            company="Demo Corp",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    user_id = str(user.id)

    # Clean existing demo data for fresh run
    await db.execute(
        RecommendationModel.__table__.delete().where(RecommendationModel.user_id == user.id)
    )
    await db.execute(
        AnalysisModel.__table__.delete().where(AnalysisModel.user_id == user.id)
    )
    await db.execute(
        PaymentModel.__table__.delete().where(PaymentModel.user_id == user.id)
    )
    await db.commit()

    # Load demo payments
    for demo in DEMO_PAYMENTS:
        payment = PaymentModel(
            user_id=user.id,
            reference=demo["reference"],
            corridor=demo["corridor"],
            amount_sent=demo["amount_sent"],
            currency_sent=demo["currency_sent"],
            amount_received=demo["amount_received"],
            currency_received=demo["currency_received"],
            initiated_at=datetime.fromisoformat(demo["initiated_at"].replace("Z", "+00:00")),
            settled_at=datetime.fromisoformat(demo["settled_at"].replace("Z", "+00:00")) if demo.get("settled_at") else None,
            psp=demo.get("psp", "stripe"),
            status="completed",
        )
        db.add(payment)
    await db.commit()

    # Run analysis on all payments
    payments_result = await db.execute(
        select(PaymentModel).where(PaymentModel.user_id == user.id)
    )
    payments = payments_result.scalars().all()

    total_leakage = 0.0
    total_fees = 0.0
    total_sent = 0.0
    all_recs = []

    for payment in payments:
        result = analyze_payment(
            corridor=payment.corridor,
            amount_sent=payment.amount_sent,
            currency_sent=payment.currency_sent,
            amount_received=payment.amount_received,
            currency_received=payment.currency_received,
            initiated_at=payment.initiated_at,
            settled_at=payment.settled_at,
            psp=payment.psp,
        )

        if "error" in result:
            continue

        analysis = AnalysisModel(
            payment_id=payment.id,
            user_id=user.id,
            expected_amount=result["expected_amount"],
            mid_market_rate=result["mid_market_rate"],
            actual_rate=result["actual_rate"],
            platform_fee=result["platform_fee"],
            intermediary_fee=result["intermediary_fee"],
            fx_spread_cost=result["fx_spread_cost"],
            total_fees=result["total_fees"],
            total_leakage=result["total_leakage"],
            leakage_pct=result["leakage_pct"],
            reconstructed_flow=result["reconstructed_flow"],
            confidence_score=result["confidence_score"],
            explanation=result["explanation"],
            analysis_duration_ms=result["analysis_duration_ms"],
        )
        db.add(analysis)
        await db.flush()

        total_leakage += result["total_leakage"]
        total_fees += result["total_fees"]
        total_sent += payment.amount_sent

        for rec in result.get("recommendations", []):
            recommendation = RecommendationModel(
                analysis_id=analysis.id,
                user_id=user.id,
                title=rec["title"],
                description=rec["description"],
                category=rec["category"],
                estimated_savings=rec["estimated_savings"],
                estimated_savings_annual=rec["estimated_savings_annual"],
                effort=rec["effort"],
                risk=rec["risk"],
                implementation_steps=rec["implementation_steps"],
                status="pending",
            )
            db.add(recommendation)
            all_recs.append(rec)

    await db.commit()

    # Build response
    token = create_token(user_id)
    annual_savings = total_leakage * 12

    return {
        "status": "success",
        "message": "Full demo pipeline complete!",
        "auth": {
            "token": token,
            "user_id": user_id,
            "email": demo_email,
            "tip": "Use this token in Authorization: Bearer <token> header for other endpoints",
        },
        "summary": {
            "payments_analyzed": len(payments),
            "total_sent_usd": round(total_sent, 2),
            "total_fees_usd": round(total_fees, 2),
            "total_leakage_usd": round(total_leakage, 2),
            "avg_cost_pct": round(total_fees / total_sent * 100, 2) if total_sent else 0,
            "potential_annual_savings_usd": round(annual_savings, 2),
            "headline": f"💸 Found ${total_leakage:,.0f} in hidden costs across {len(payments)} payments. That's ${annual_savings:,.0f}/year you're losing!",
        },
        "recommendations_count": len(all_recs),
        "top_recommendations": sorted(all_recs, key=lambda r: r["estimated_savings_annual"], reverse=True)[:3],
        "next_steps": [
            "GET /api/analysis/summary — detailed breakdown by corridor",
            "GET /api/analysis — see individual payment analyses",
            "GET /api/recommendations — all actionable recommendations",
            f"Use token: Bearer {token[:20]}...",
        ],
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Helpers — model → response conversion
# ═══════════════════════════════════════════════════════════════════════════════

def _payment_to_response(p: PaymentModel) -> PaymentResponse:
    return PaymentResponse(
        id=str(p.id),
        reference=p.reference,
        corridor=p.corridor,
        amount_sent=p.amount_sent,
        currency_sent=p.currency_sent,
        amount_received=p.amount_received,
        currency_received=p.currency_received,
        initiated_at=p.initiated_at,
        settled_at=p.settled_at,
        psp=p.psp,
        status=p.status,
        created_at=p.created_at,
    )


def _analysis_to_response(a: AnalysisModel) -> AnalysisResponse:
    return AnalysisResponse(
        id=str(a.id),
        payment_id=str(a.payment_id),
        expected_amount=a.expected_amount or 0,
        mid_market_rate=a.mid_market_rate or 0,
        actual_rate=a.actual_rate or 0,
        platform_fee=a.platform_fee or 0,
        intermediary_fee=a.intermediary_fee or 0,
        fx_spread_cost=a.fx_spread_cost or 0,
        total_fees=a.total_fees or 0,
        total_leakage=a.total_leakage or 0,
        leakage_pct=a.leakage_pct or 0,
        reconstructed_flow=a.reconstructed_flow or [],
        confidence_score=a.confidence_score or 0,
        explanation=a.explanation,
        analyzed_at=a.analyzed_at,
        analysis_duration_ms=a.analysis_duration_ms,
    )


def _rec_to_response(r: RecommendationModel) -> RecommendationResponse:
    return RecommendationResponse(
        id=str(r.id),
        analysis_id=str(r.analysis_id),
        title=r.title,
        description=r.description,
        category=r.category or "",
        estimated_savings=r.estimated_savings or 0,
        estimated_savings_annual=r.estimated_savings_annual or 0,
        effort=r.effort or "medium",
        risk=r.risk or "low",
        implementation_steps=r.implementation_steps or [],
        status=r.status or "pending",
        created_at=r.created_at,
    )


# ─── Run ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.environment == "development",
    )
