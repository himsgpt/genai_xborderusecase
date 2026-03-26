"""
Stripe API Client — Pulls real payment data, balance transactions, and fee details.

Uses the Stripe Python SDK to:
1. List charges with expanded balance_transaction (includes fee_details, exchange_rate)
2. Map Stripe data to our payment model for analysis
3. Provide REAL fee attribution instead of heuristics

Requires: STRIPE_SECRET_KEY in .env (use sk_test_* for test mode)
"""
import logging
from datetime import datetime, timezone
from typing import Optional

import stripe

logger = logging.getLogger("xborder.stripe")


def configure_stripe(api_key: str):
    stripe.api_key = api_key
    logger.info(f"Stripe configured (key ending ...{api_key[-6:]})")


def is_configured() -> bool:
    return bool(stripe.api_key)


def get_account_info() -> Optional[dict]:
    """Verify the API key works and return account info."""
    try:
        account = stripe.Account.retrieve()
        return {
            "id": account.id,
            "business_name": getattr(account, "business_profile", {}).get("name"),
            "country": account.country,
            "default_currency": account.default_currency,
            "charges_enabled": account.charges_enabled,
            "payouts_enabled": account.payouts_enabled,
        }
    except stripe.error.AuthenticationError:
        logger.error("Invalid Stripe API key")
        return None
    except Exception as e:
        logger.error(f"Stripe account check failed: {e}")
        return None


def list_charges(
    limit: int = 100,
    created_after: Optional[datetime] = None,
    created_before: Optional[datetime] = None,
    currency: Optional[str] = None,
) -> list[dict]:
    """
    Fetch charges from Stripe with expanded balance_transaction.
    Each charge includes fee_details, exchange_rate, and net amounts.
    """
    if not is_configured():
        raise RuntimeError("Stripe not configured. Set STRIPE_SECRET_KEY in .env")

    params = {
        "limit": min(limit, 100),
        "expand": ["data.balance_transaction"],
    }
    if created_after:
        params["created"] = params.get("created", {})
        params["created"]["gte"] = int(created_after.timestamp())
    if created_before:
        params["created"] = params.get("created", {})
        params["created"]["lte"] = int(created_before.timestamp())

    try:
        charges = stripe.Charge.list(**params)
        return [_map_charge(ch) for ch in charges.auto_paging_iter()]
    except Exception as e:
        logger.error(f"Stripe list_charges failed: {e}")
        raise


def list_balance_transactions(
    limit: int = 100,
    type_filter: Optional[str] = "charge",
    currency: Optional[str] = None,
) -> list[dict]:
    """Fetch balance transactions directly for fee analysis."""
    if not is_configured():
        raise RuntimeError("Stripe not configured")

    params = {"limit": min(limit, 100)}
    if type_filter:
        params["type"] = type_filter
    if currency:
        params["currency"] = currency

    try:
        txns = stripe.BalanceTransaction.list(**params)
        return [_map_balance_transaction(bt) for bt in txns.auto_paging_iter()]
    except Exception as e:
        logger.error(f"Stripe list_balance_transactions failed: {e}")
        raise


def _map_charge(ch) -> dict:
    """Map a Stripe Charge object to our internal format."""
    bt = ch.balance_transaction if hasattr(ch.balance_transaction, "id") else None

    fee_details = []
    exchange_rate = None
    net_amount = None
    total_stripe_fee = 0

    if bt:
        exchange_rate = bt.exchange_rate
        net_amount = bt.net / 100.0
        total_stripe_fee = bt.fee / 100.0
        fee_details = [
            {
                "type": fd.type,
                "amount": fd.amount / 100.0,
                "currency": fd.currency,
                "description": fd.description,
            }
            for fd in (bt.fee_details or [])
        ]

    charge_currency = ch.currency.upper()
    account_currency = bt.currency.upper() if bt else charge_currency

    # Determine corridor
    if charge_currency != account_currency:
        corridor = f"{charge_currency}_{account_currency}"
    else:
        corridor = None

    amount_cents = ch.amount
    amount = amount_cents / 100.0

    received_amount = amount
    if exchange_rate and exchange_rate != 1.0:
        received_amount = amount * exchange_rate

    return {
        "stripe_charge_id": ch.id,
        "stripe_balance_txn_id": bt.id if bt else None,
        "amount": amount,
        "currency": charge_currency,
        "account_currency": account_currency,
        "corridor": corridor,
        "exchange_rate": exchange_rate,
        "fee_total": total_stripe_fee,
        "fee_details": fee_details,
        "net_amount": net_amount,
        "status": ch.status,
        "paid": ch.paid,
        "description": ch.description,
        "payment_method_type": ch.payment_method_details.type if ch.payment_method_details else None,
        "customer_id": ch.customer,
        "created": datetime.fromtimestamp(ch.created, tz=timezone.utc),
        "metadata": dict(ch.metadata) if ch.metadata else {},
    }


def _map_balance_transaction(bt) -> dict:
    """Map a Stripe BalanceTransaction to our internal format."""
    return {
        "id": bt.id,
        "amount": bt.amount / 100.0,
        "currency": bt.currency.upper(),
        "fee": bt.fee / 100.0,
        "fee_details": [
            {
                "type": fd.type,
                "amount": fd.amount / 100.0,
                "currency": fd.currency,
                "description": fd.description,
            }
            for fd in (bt.fee_details or [])
        ],
        "net": bt.net / 100.0,
        "exchange_rate": bt.exchange_rate,
        "type": bt.type,
        "source": bt.source,
        "created": datetime.fromtimestamp(bt.created, tz=timezone.utc),
        "status": bt.status,
    }
