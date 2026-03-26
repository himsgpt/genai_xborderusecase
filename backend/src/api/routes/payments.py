"""Payment routes — CRUD + demo data loading."""
import logging
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, PaymentModel
from ...infrastructure.auth import get_current_user_id
from ...domain.services import DEMO_PAYMENTS
from ..schemas import PaymentCreate, PaymentResponse

logger = logging.getLogger("xborder")
router = APIRouter(prefix="/api/payments", tags=["payments"])


def _to_response(p: PaymentModel) -> PaymentResponse:
    return PaymentResponse(
        id=str(p.id), reference=p.reference, corridor=p.corridor,
        amount_sent=p.amount_sent, currency_sent=p.currency_sent,
        amount_received=p.amount_received, currency_received=p.currency_received,
        initiated_at=p.initiated_at, settled_at=p.settled_at,
        psp=p.psp, status=p.status, created_at=p.created_at,
    )


@router.get("", response_model=list[PaymentResponse])
async def list_payments(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """List all payments for the authenticated user."""
    result = await db.execute(
        select(PaymentModel).where(PaymentModel.user_id == user_id).order_by(PaymentModel.initiated_at.desc())
    )
    return [_to_response(p) for p in result.scalars().all()]


@router.post("", response_model=PaymentResponse, status_code=201)
async def create_payment(data: PaymentCreate, db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Add a payment record manually."""
    payment = PaymentModel(
        user_id=user_id, reference=data.reference, corridor=data.corridor,
        amount_sent=data.amount_sent, currency_sent=data.currency_sent,
        amount_received=data.amount_received, currency_received=data.currency_received,
        initiated_at=data.initiated_at, settled_at=data.settled_at,
        psp=data.psp, status="completed",
    )
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return _to_response(payment)


@router.post("/demo")
async def load_demo_payments(db: AsyncSession = Depends(get_db), user_id: str = Depends(get_current_user_id)):
    """Load 8 realistic demo payments across 3 corridors."""
    existing = await db.execute(
        select(func.count(PaymentModel.id)).where(PaymentModel.user_id == user_id).where(PaymentModel.reference.like("po_demo_%"))
    )
    count = existing.scalar()
    if count and count > 0:
        return {"message": f"Demo data already loaded ({count} payments)."}

    for demo in DEMO_PAYMENTS:
        db.add(PaymentModel(
            user_id=user_id, reference=demo["reference"], corridor=demo["corridor"],
            amount_sent=demo["amount_sent"], currency_sent=demo["currency_sent"],
            amount_received=demo["amount_received"], currency_received=demo["currency_received"],
            initiated_at=datetime.fromisoformat(demo["initiated_at"].replace("Z", "+00:00")),
            settled_at=datetime.fromisoformat(demo["settled_at"].replace("Z", "+00:00")) if demo.get("settled_at") else None,
            psp=demo.get("psp", "stripe"), status="completed",
        ))
    await db.commit()
    logger.info(f"Loaded {len(DEMO_PAYMENTS)} demo payments for user {user_id}")
    return {"message": f"Loaded {len(DEMO_PAYMENTS)} demo payments", "payments_created": len(DEMO_PAYMENTS)}
