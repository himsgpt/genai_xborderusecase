"""
SQLAlchemy ORM models — 4 tables for the payment intelligence platform.

users -> payments -> analyses -> recommendations
"""
import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Float, Integer, Text, DateTime, JSON, ForeignKey, Index,
)
from sqlalchemy.dialects.postgresql import UUID

from .connection import Base


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
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    reference = Column(String(255))
    corridor = Column(String(20), nullable=False, index=True)
    amount_sent = Column(Float, nullable=False)
    currency_sent = Column(String(3), nullable=False)
    amount_received = Column(Float, nullable=False)
    currency_received = Column(String(3), nullable=False)
    initiated_at = Column(DateTime(timezone=True), nullable=False)
    settled_at = Column(DateTime(timezone=True))
    psp = Column(String(50))
    status = Column(String(50))
    raw_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))


class AnalysisModel(Base):
    __tablename__ = "analyses"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    payment_id = Column(UUID(as_uuid=True), ForeignKey("payments.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    expected_amount = Column(Float)
    mid_market_rate = Column(Float)
    actual_rate = Column(Float)
    platform_fee = Column(Float)
    intermediary_fee = Column(Float)
    fx_spread_cost = Column(Float)
    total_fees = Column(Float)
    total_leakage = Column(Float)
    leakage_pct = Column(Float)
    reconstructed_flow = Column(JSON)
    confidence_score = Column(Float)
    explanation = Column(Text)
    analyzed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    analysis_duration_ms = Column(Integer)


class RecommendationModel(Base):
    __tablename__ = "recommendations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    analysis_id = Column(UUID(as_uuid=True), ForeignKey("analyses.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    description = Column(Text)
    category = Column(String(50))
    estimated_savings = Column(Float)
    estimated_savings_annual = Column(Float)
    effort = Column(String(20))
    risk = Column(String(20))
    implementation_steps = Column(JSON)
    status = Column(String(50))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
