"""
Pydantic schemas — API request/response models.
Kept in the API layer because they define the HTTP contract.
"""
from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


# ---- Auth ----

class UserRegister(BaseModel):
    email: str
    password: str
    name: Optional[str] = None
    company: Optional[str] = None


class UserLogin(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class UserResponse(BaseModel):
    id: str
    email: str
    name: Optional[str] = None
    company: Optional[str] = None
    model_config = ConfigDict(from_attributes=True)


# ---- Payments ----

class PaymentCreate(BaseModel):
    reference: Optional[str] = None
    corridor: str
    amount_sent: float
    currency_sent: str
    amount_received: float
    currency_received: str
    initiated_at: datetime
    settled_at: Optional[datetime] = None
    psp: str = "stripe"


class PaymentResponse(BaseModel):
    id: str
    reference: Optional[str] = None
    corridor: str
    amount_sent: float
    currency_sent: str
    amount_received: float
    currency_received: str
    initiated_at: datetime
    settled_at: Optional[datetime] = None
    psp: str
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


# ---- Analysis ----

class AnalysisResponse(BaseModel):
    id: str
    payment_id: str
    expected_amount: float
    mid_market_rate: float
    actual_rate: float
    platform_fee: float
    intermediary_fee: float
    fx_spread_cost: float
    total_fees: float
    total_leakage: float
    leakage_pct: float
    reconstructed_flow: list
    confidence_score: float
    explanation: Optional[str] = None
    analyzed_at: datetime
    analysis_duration_ms: Optional[int] = None
    model_config = ConfigDict(from_attributes=True)


class CorridorSummary(BaseModel):
    corridor: str
    payments: int
    total_sent: float
    total_fees: float
    total_leakage: float
    avg_cost_pct: float
    top_issue: str


class AnalysisSummary(BaseModel):
    total_payments_analyzed: int
    total_sent_usd: float
    total_fees_usd: float
    total_leakage_usd: float
    avg_cost_pct: float
    potential_annual_savings_usd: float
    headline: str
    corridors: List[CorridorSummary]
    top_recommendations: list


# ---- Recommendations ----

class RecommendationResponse(BaseModel):
    id: str
    analysis_id: str
    title: str
    description: Optional[str] = None
    category: str
    estimated_savings: float
    estimated_savings_annual: float
    effort: str
    risk: str
    implementation_steps: list
    status: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)


class RecommendationUpdate(BaseModel):
    status: str  # pending | in_progress | implemented | dismissed
