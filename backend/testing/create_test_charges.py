"""Create test charges on Stripe in multiple currencies to test cross-border analysis."""
import stripe
import sys
import os

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

stripe.api_key = os.environ.get("STRIPE_SECRET_KEY", "")

test_charges = [
    {"amount": 1000000, "currency": "usd", "desc": "US domestic payment $10,000"},
    {"amount": 500000, "currency": "usd", "desc": "US domestic payment $5,000"},
    {"amount": 800000, "currency": "eur", "desc": "Cross-border EUR payment E8,000"},
    {"amount": 300000, "currency": "gbp", "desc": "Cross-border GBP payment L3,000"},
    {"amount": 1500000, "currency": "eur", "desc": "Cross-border EUR payment E15,000"},
    {"amount": 200000, "currency": "gbp", "desc": "Cross-border GBP payment L2,000"},
]

print("=" * 60)
print("  Creating Stripe Test Charges")
print("=" * 60)

created = []
for tc in test_charges:
    try:
        ch = stripe.Charge.create(
            amount=tc["amount"],
            currency=tc["currency"],
            source="tok_visa",
            description=tc["desc"],
            expand=["balance_transaction"],
        )
        bt = ch.balance_transaction
        fx_rate = getattr(bt, "exchange_rate", None) if bt else None
        fee = bt.fee / 100.0 if bt else 0
        fee_types = [fd.type for fd in bt.fee_details] if bt and bt.fee_details else []

        cur = tc["currency"].upper()
        amt = tc["amount"] / 100
        print(f"  OK: {ch.id}")
        print(f"      {cur} {amt:,.0f} | Stripe fee: ${fee:.2f} | FX rate: {fx_rate}")
        print(f"      Fee types: {fee_types}")
        created.append(ch.id)
    except Exception as e:
        print(f"  FAIL: {tc['desc']}: {e}")

print(f"\n  Created {len(created)} / {len(test_charges)} test charges")
print("=" * 60)
