"""Recommendation routes — list and update status."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, RecommendationModel
from ...infrastructure.auth import get_current_user_id
from ..schemas import RecommendationResponse, RecommendationUpdate

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


def _to_response(r: RecommendationModel) -> RecommendationResponse:
    return RecommendationResponse(
        id=str(r.id), analysis_id=str(r.analysis_id), title=r.title,
        description=r.description, category=r.category or "",
        estimated_savings=r.estimated_savings or 0,
        estimated_savings_annual=r.estimated_savings_annual or 0,
        effort=r.effort or "medium", risk=r.risk or "low",
        implementation_steps=r.implementation_steps or [],
        status=r.status or "pending", created_at=r.created_at,
    )


@router.get("", response_model=list[RecommendationResponse])
async def list_recommendations(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """List all recommendations, ordered by potential savings."""
    result = await db.execute(
        select(RecommendationModel).where(RecommendationModel.user_id == user_id)
        .order_by(RecommendationModel.estimated_savings_annual.desc())
    )
    return [_to_response(r) for r in result.scalars().all()]


@router.patch("/{rec_id}")
async def update_recommendation_status(rec_id: str, data: RecommendationUpdate,
                                        db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Update recommendation status (pending -> in_progress -> implemented | dismissed)."""
    result = await db.execute(
        select(RecommendationModel).where(RecommendationModel.id == rec_id).where(RecommendationModel.user_id == user_id)
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    valid = {"pending", "in_progress", "implemented", "dismissed"}
    if data.status not in valid:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid}")
    rec.status = data.status
    await db.commit()
    return {"message": f"Recommendation updated to '{data.status}'", "id": rec_id}
