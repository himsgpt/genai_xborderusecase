"""Test Stripe sync + analysis with real charges and live FX rates."""
import httpx
import json
import sys
import os

if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE = "http://localhost:8000"
SEP = "=" * 70


def main():
    c = httpx.Client(base_url=BASE, timeout=30)

    print(f"\n{SEP}")
    print("  Stripe Integration Test -- Real Charges + Live FX")
    print(SEP)

    # Step 1: Get auth via demo pipeline
    print("\n[1/5] Getting auth token via demo pipeline...")
    r = c.post("/api/demo/full-pipeline")
    assert r.status_code == 200, f"Demo failed: {r.text}"
    data = r.json()
    token = data["auth"]["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"  [OK] Token received")
    print(f"  FX rate source: {data.get('fx_rate_source', 'unknown')}")
    print(f"  Demo summary: {data['summary']['headline']}")

    # Step 2: Check Stripe status
    print("\n[2/5] Checking Stripe connection...")
    r = c.get("/api/stripe/status")
    status = r.json()
    print(f"  Connected: {status['connected']}")
    if status.get("account"):
        acct = status["account"]
        print(f"  Account: {acct['id']} | Country: {acct['country']} | Currency: {acct['default_currency']}")

    # Step 3: Sync Stripe charges
    print("\n[3/5] Syncing Stripe charges...")
    r = c.post("/api/stripe/sync?limit=50", headers=headers)
    assert r.status_code == 200, f"Sync failed: {r.text}"
    sync = r.json()
    print(f"  [OK] {sync['message']}")
    print(f"  Imported: {sync['imported']} | Skipped: {sync['skipped']} | Cross-border: {sync['cross_border']}")

    # Step 4: View raw Stripe data
    print("\n[4/5] Viewing raw Stripe charges (fee transparency)...")
    r = c.get("/api/stripe/charges?limit=6")
    charges = r.json()
    print(f"  {charges['count']} charges from Stripe:")
    for ch in charges.get("charges", []):
        cur = ch["currency"]
        amt = ch["amount"]
        fx = ch.get("exchange_rate") or "N/A"
        fee = ch.get("fee_total", 0)
        fees_desc = " + ".join(
            f"{fd['type']}=${fd['amount']:.2f}"
            for fd in ch.get("fee_details", [])
        ) or "none"
        print(f"    {ch['stripe_charge_id'][:20]}... | {cur} {amt:>10,.0f} | FX={fx} | Fee=${fee:.2f} ({fees_desc})")

    # Step 5: Live FX comparison
    print("\n[5/5] Comparing Stripe FX vs ECB mid-market rates...")
    for pair in [("EUR", "USD"), ("GBP", "USD")]:
        r = c.get("/api/stripe/fx-rate", params={"currency_from": pair[0], "currency_to": pair[1]})
        fx = r.json()
        ecb = fx.get("live_rate")
        print(f"  {fx['pair']}: ECB mid-market = {ecb}")

    # Find a cross-border charge for comparison
    for ch in charges.get("charges", []):
        if ch.get("exchange_rate") and ch["exchange_rate"] != 1.0:
            stripe_rate = ch["exchange_rate"]
            cur_from = ch["currency"]
            cur_to = ch["account_currency"]
            r = c.get("/api/stripe/fx-rate", params={"currency_from": cur_from, "currency_to": cur_to})
            ecb_rate = r.json().get("live_rate")
            if ecb_rate:
                spread = abs(ecb_rate - stripe_rate) / ecb_rate * 100
                markup_per_1000 = abs(ecb_rate - stripe_rate) * 1000
                print(f"\n  --- FX Spread Analysis ---")
                print(f"  {cur_from.upper()}->{cur_to.upper()}")
                print(f"  Stripe rate:  {stripe_rate}")
                print(f"  ECB rate:     {ecb_rate}")
                print(f"  Spread:       {spread:.3f}%")
                print(f"  Markup per $1,000: ${markup_per_1000:.2f}")
            break

    print(f"\n{SEP}")
    print("  ALL STRIPE INTEGRATION TESTS PASSED!")
    print(SEP)
    print(f"\n  API Docs: {BASE}/docs")
    print(f"  Stripe charges: GET {BASE}/api/stripe/charges")
    print(f"  Live FX rates: GET {BASE}/api/stripe/fx-rate?currency_from=USD&currency_to=EUR")
    print()


if __name__ == "__main__":
    try:
        main()
    except httpx.ConnectError:
        print(f"\n[FAIL] Cannot connect to {BASE}")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n[FAIL] {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
