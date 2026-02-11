"""
Database — SQLAlchemy models + async connection.
Single file for MVP. Can split into models/, repos/ for DDD later.
"""
import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Column, String, Float, DateTime, Boolean, Integer, Text, ForeignKey, JSON,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase

from .config import settings

# ---------------------------------------------------------------------------
# Engine + Session
# ---------------------------------------------------------------------------
engine = create_async_engine(
    settings.database_url,
    echo=(settings.environment == "development"),
    pool_size=5,
    max_overflow=10,
)

AsyncSessionLocal = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)


class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

class UserModel(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(255))
    company = Column(String(255))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class PaymentModel(Base):
    __tablename__ = "payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    reference = Column(String(255))  # External ID (Stripe payout ID, etc.)
    corridor = Column(String(20), nullable=False, index=True)  # e.g. "USD_EUR"
    amount_sent = Column(Float, nullable=False)
    currency_sent = Column(String(3), nullable=False)
    amount_received = Column(Float, nullable=False)
    currency_received = Column(String(3), nullable=False)
    initiated_at = Column(DateTime(timezone=True), nullable=False)
    settled_at = Column(DateTime(timezone=True))
    psp = Column(String(50), default="stripe")
    status = Column(String(50), default="completed")
    raw_data = Column(JSON, default=dict)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("payments.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Expected vs actual
    expected_amount = Column(Float)
    mid_market_rate = Column(Float)
    actual_rate = Column(Float)

    # Fee breakdown (in sent currency, e.g. USD)
    platform_fee = Column(Float, default=0)
    intermediary_fee = Column(Float, default=0)
    fx_spread_cost = Column(Float, default=0)
    total_fees = Column(Float, default=0)

    # Leakage
    total_leakage = Column(Float, default=0)
    leakage_pct = Column(Float, default=0)

    # Flow reconstruction
    reconstructed_flow = Column(JSON, default=list)
    confidence_score = Column(Float, default=0.78)
    explanation = Column(Text)

    # Meta
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    analysis_duration_ms = Column(Integer)


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(
        UUID(as_uuid=True),
        ForeignKey("analyses.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(50))  # route_switch, batching, timing, fx_optimization
    estimated_savings = Column(Float, default=0)
    estimated_savings_annual = Column(Float, default=0)
    effort = Column(String(20))  # low, medium, high
    risk = Column(String(20))    # low, medium, high
    implementation_steps = Column(JSON, default=list)
    status = Column(String(50), default="pending")  # pending, in_progress, implemented, dismissed
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


# ---------------------------------------------------------------------------
# DB Dependency
# ---------------------------------------------------------------------------

async def get_db():
    """FastAPI dependency — yields an async session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
