"""
Stripe Integration routes — connect Stripe account, sync payments, view raw fee data.

Flow:
  1. POST /api/stripe/connect    — validate API key, save connection
  2. GET  /api/stripe/status     — check if Stripe is connected
  3. POST /api/stripe/sync       — pull charges from Stripe, store as payments
  4. GET  /api/stripe/charges    — view raw Stripe charge data (for debugging/transparency)
"""
import logging
from datetime import datetime, timezone
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ...infrastructure.database import get_db, PaymentModel
from ...infrastructure.auth import get_current_user_id
from ...infrastructure.config import settings
from ...infrastructure import stripe_client

logger = logging.getLogger("xborder")
router = APIRouter(prefix="/api/stripe", tags=["stripe"])


class StripeConnectRequest(BaseModel):
    api_key: str


# ─── Connect ─────────────────────────────────────────────────────────────────

@router.post("/connect")
async def connect_stripe(req: StripeConnectRequest):
    """
    Validate a Stripe API key and connect.
    Use sk_test_* for test mode, sk_live_* for production.
    """
    if not req.api_key.startswith(("sk_test_", "sk_live_", "rk_test_", "rk_live_")):
        raise HTTPException(status_code=400, detail="Invalid Stripe key format. Must start with sk_test_ or sk_live_")

    stripe_client.configure_stripe(req.api_key)
    account = stripe_client.get_account_info()
    if not account:
        raise HTTPException(status_code=401, detail="Invalid Stripe API key — authentication failed")

    return {
        "status": "connected",
        "account": account,
        "message": f"Connected to Stripe account {account['id']} ({account.get('business_name') or 'unnamed'})",
    }


@router.get("/status")
async def stripe_status():
    """Check whether Stripe is connected and the key is valid."""
    if not stripe_client.is_configured():
        # Try from env
        if settings.stripe_secret_key:
            stripe_client.configure_stripe(settings.stripe_secret_key)
        else:
            return {"connected": False, "message": "Stripe not configured. POST /api/stripe/connect with your API key."}

    account = stripe_client.get_account_info()
    if not account:
        return {"connected": False, "message": "Stripe key invalid or expired."}

    return {"connected": True, "account": account}


# ─── Sync ─────────────────────────────────────────────────────────────────────

@router.post("/sync")
async def sync_stripe_charges(
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """
    Pull charges from Stripe and import them as payments.
    Skips charges already imported (deduplication by stripe_charge_id in raw_data).
    Each payment stores Stripe's fee_details and exchange_rate in raw_data
    for real fee attribution during analysis.
    """
    _ensure_stripe_configured()

    charges = stripe_client.list_charges(limit=limit)
    logger.info(f"Fetched {len(charges)} charges from Stripe")

    # Get existing Stripe charge IDs to avoid duplicates
    existing_refs = set()
    result = await db.execute(
        select(PaymentModel.reference).where(
            PaymentModel.user_id == user_id,
            PaymentModel.reference.like("stripe_%"),
        )
    )
    existing_refs = {r[0] for r in result.all()}

    imported = 0
    skipped = 0
    cross_border = 0

    for ch in charges:
        ref = f"stripe_{ch['stripe_charge_id']}"
        if ref in existing_refs:
            skipped += 1
            continue

        if not ch.get("paid"):
            skipped += 1
            continue

        # Determine corridor
        charge_currency = ch["currency"]
        account_currency = ch.get("account_currency", charge_currency)
        corridor = ch.get("corridor")

        if not corridor and charge_currency != account_currency:
            corridor = f"{charge_currency}_{account_currency}"

        if corridor:
            cross_border += 1

        # Map to our payment model
        currency_sent = charge_currency
        currency_received = account_currency
        amount_sent = ch["amount"]
        amount_received = ch.get("net_amount", ch["amount"])

        if ch.get("exchange_rate") and ch["exchange_rate"] != 1.0:
            amount_received = ch["amount"] * ch["exchange_rate"]

        payment = PaymentModel(
            user_id=user_id,
            reference=ref,
            corridor=corridor or f"{currency_sent}_{currency_received}",
            amount_sent=amount_sent,
            currency_sent=currency_sent,
            amount_received=round(amount_received, 2),
            currency_received=currency_received,
            initiated_at=ch["created"],
            settled_at=ch["created"],
            psp="stripe",
            status="completed" if ch["paid"] else ch["status"],
            raw_data={
                "stripe_charge_id": ch["stripe_charge_id"],
                "stripe_balance_txn_id": ch.get("stripe_balance_txn_id"),
                "exchange_rate": ch.get("exchange_rate"),
                "fee_total": ch.get("fee_total"),
                "fee_details": ch.get("fee_details", []),
                "payment_method_type": ch.get("payment_method_type"),
                "customer_id": ch.get("customer_id"),
                "description": ch.get("description"),
            },
        )
        db.add(payment)
        imported += 1

    await db.commit()
    logger.info(f"Stripe sync: {imported} imported, {skipped} skipped, {cross_border} cross-border")

    return {
        "message": f"Synced {imported} payments from Stripe ({cross_border} cross-border)",
        "imported": imported,
        "skipped": skipped,
        "cross_border": cross_border,
        "total_fetched": len(charges),
    }


# ─── Raw Data ─────────────────────────────────────────────────────────────────

@router.get("/charges")
async def list_stripe_charges(limit: int = 20):
    """
    View raw Stripe charges with fee details (for debugging/transparency).
    Shows what Stripe actually charges you.
    """
    _ensure_stripe_configured()
    charges = stripe_client.list_charges(limit=limit)
    return {
        "count": len(charges),
        "charges": charges,
    }


@router.get("/balance-transactions")
async def list_stripe_balance_txns(limit: int = 20, type_filter: str = "charge"):
    """View raw Stripe balance transactions with fee breakdowns."""
    _ensure_stripe_configured()
    txns = stripe_client.list_balance_transactions(limit=limit, type_filter=type_filter or None)
    return {
        "count": len(txns),
        "transactions": txns,
    }


# ─── FX Rate Endpoint ────────────────────────────────────────────────────────

@router.get("/fx-rate")
async def get_live_fx_rate(
    currency_from: str = "USD",
    currency_to: str = "EUR",
):
    """
    Get live mid-market FX rate from ECB (Frankfurter API).
    Compare this against Stripe's exchange_rate to see the markup.
    """
    from ...infrastructure.fx_rates import fetch_live_rate
    from ...domain.services.corridor_data import get_mid_market_rate

    live = await fetch_live_rate(currency_from.upper(), currency_to.upper())
    hardcoded = get_mid_market_rate(currency_from.upper(), currency_to.upper())

    return {
        "pair": f"{currency_from.upper()}/{currency_to.upper()}",
        "live_rate": live,
        "hardcoded_rate": hardcoded,
        "source": "Frankfurter (ECB)" if live else "hardcoded fallback",
        "note": "Compare against Stripe's exchange_rate to calculate FX spread/markup",
    }


def _ensure_stripe_configured():
    if not stripe_client.is_configured():
        if settings.stripe_secret_key:
            stripe_client.configure_stripe(settings.stripe_secret_key)
        else:
            raise HTTPException(
                status_code=400,
                detail="Stripe not configured. POST /api/stripe/connect with your API key, or set STRIPE_SECRET_KEY in .env",
            )
