"""
End-to-end test script for XBorder Payment Intelligence API.
Run: python test_e2e.py
"""
import httpx
import json
import sys
import os

# Fix Windows console encoding
if sys.platform == "win32":
    os.environ.setdefault("PYTHONIOENCODING", "utf-8")
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE = "http://localhost:8000"
SEPARATOR = "=" * 70


def main():
    print(f"\n{SEPARATOR}")
    print("  XBorder Payment Intelligence -- End-to-End Test")
    print(SEPARATOR)

    client = httpx.Client(base_url=BASE, timeout=30)

    # -- 1. Health Check -------------------------------------------------------
    print("\n[1/7] Health check...")
    r = client.get("/health")
    assert r.status_code == 200, f"Health check failed: {r.text}"
    print(f"  [OK] API is healthy: {r.json()['service']}")

    # -- 2. Full Demo Pipeline (one-click) -------------------------------------
    print("\n[2/7] Running full demo pipeline (create user + payments + analysis)...")
    r = client.post("/api/demo/full-pipeline")
    assert r.status_code == 200, f"Demo pipeline failed: {r.text}"
    demo = r.json()
    token = demo["auth"]["token"]
    headers = {"Authorization": f"Bearer {token}"}

    print(f"  [OK] {demo['message']}")
    print(f"  Payments analyzed: {demo['summary']['payments_analyzed']}")
    print(f"  Total sent: ${demo['summary']['total_sent_usd']:,.2f}")
    print(f"  Total fees: ${demo['summary']['total_fees_usd']:,.2f} ({demo['summary']['avg_cost_pct']:.2f}%)")
    print(f"  Total leakage: ${demo['summary']['total_leakage_usd']:,.2f}")
    print(f"  Annual savings potential: ${demo['summary']['potential_annual_savings_usd']:,.2f}")
    print(f"  Recommendations: {demo['recommendations_count']}")

    # -- 3. Get Analysis Summary -----------------------------------------------
    print("\n[3/7] Getting analysis summary...")
    r = client.get("/api/analysis/summary", headers=headers)
    assert r.status_code == 200, f"Summary failed: {r.text}"
    summary = r.json()

    print(f"\n  {summary['headline']}")
    print(f"\n  Corridor Breakdown:")
    for c in summary["corridors"]:
        print(f"    {c['corridor']:>10}: {c['payments']} payments | "
              f"${c['total_sent']:>10,.2f} sent | "
              f"${c['total_leakage']:>8,.2f} leakage | "
              f"{c['avg_cost_pct']:.2f}% avg cost")

    # -- 4. List All Analyses --------------------------------------------------
    print("\n[4/7] Listing all analyses...")
    r = client.get("/api/analysis", headers=headers)
    assert r.status_code == 200, f"List analyses failed: {r.text}"
    analyses = r.json()
    print(f"  [OK] {len(analyses)} analyses found")

    # Show one detailed analysis
    if analyses:
        a = analyses[0]
        print(f"\n  --- Sample Analysis (Payment {a['payment_id'][:8]}...) ---")
        print(f"  Expected amount: {a['expected_amount']:,.2f}")
        print(f"  Mid-market rate: {a['mid_market_rate']:.4f}")
        print(f"  Platform fee:    ${a['platform_fee']:,.2f}")
        print(f"  Intermediary:    ${a['intermediary_fee']:,.2f}")
        print(f"  FX spread:       ${a['fx_spread_cost']:,.2f}")
        print(f"  Total fees:      ${a['total_fees']:,.2f}")
        print(f"  Leakage:         ${a['total_leakage']:,.2f} ({a['leakage_pct']:.2f}%)")
        print(f"  Confidence:      {a['confidence_score']:.0%}")

        if a["reconstructed_flow"]:
            print(f"\n  Payment Route:")
            for hop in a["reconstructed_flow"]:
                fee_str = f" -- ${hop['fee_usd']:,.2f}" if hop['fee_usd'] > 0.01 else ""
                print(f"    {hop['sequence']}. {hop['entity']} ({hop['type']}){fee_str}")

    # -- 5. List Recommendations -----------------------------------------------
    print("\n[5/7] Listing recommendations...")
    r = client.get("/api/recommendations", headers=headers)
    assert r.status_code == 200, f"List recommendations failed: {r.text}"
    recs = r.json()
    print(f"  [OK] {len(recs)} recommendations found\n")

    for i, rec in enumerate(recs[:5], 1):
        print(f"  [{i}] {rec['title']}")
        print(f"      Savings: ${rec['estimated_savings_annual']:,.0f}/year | Effort: {rec['effort']} | Risk: {rec['risk']}")
        if rec.get("implementation_steps"):
            print(f"      Steps: {rec['implementation_steps'][0]}")
        print()

    # -- 6. Test Auth Flow -----------------------------------------------------
    print("[6/7] Testing auth flow (register + login)...")
    import time
    test_email = f"test_{int(time.time())}@example.com"

    r = client.post("/api/auth/register", json={
        "email": test_email,
        "password": "testpass123",
        "name": "Test User",
        "company": "Test Corp",
    })
    assert r.status_code == 200, f"Register failed: {r.text}"
    print(f"  [OK] Registered: {test_email}")

    r = client.post("/api/auth/login", json={
        "email": test_email,
        "password": "testpass123",
    })
    assert r.status_code == 200, f"Login failed: {r.text}"
    print(f"  [OK] Login successful, token received")

    # -- 7. Test Payment CRUD --------------------------------------------------
    print("\n[7/7] Testing payment CRUD...")
    auth_headers = {"Authorization": f"Bearer {r.json()['access_token']}"}

    r = client.post("/api/payments", headers=auth_headers, json={
        "corridor": "USD_EUR",
        "amount_sent": 25000,
        "currency_sent": "USD",
        "amount_received": 22100,
        "currency_received": "EUR",
        "initiated_at": "2026-02-09T10:00:00Z",
        "settled_at": "2026-02-12T14:00:00Z",
        "psp": "stripe",
    })
    assert r.status_code == 201, f"Create payment failed: {r.text}"
    print(f"  [OK] Payment created: $25,000 USD -> EUR")

    r = client.get("/api/payments", headers=auth_headers)
    assert r.status_code == 200, f"List payments failed: {r.text}"
    print(f"  [OK] Payments listed: {len(r.json())} found")

    # -- DONE ------------------------------------------------------------------
    print(f"\n{SEPARATOR}")
    print("  ALL TESTS PASSED -- End-to-end pipeline works!")
    print(SEPARATOR)
    print(f"\n  API docs: {BASE}/docs")
    print(f"  Health:   {BASE}/health")
    print(f"  Demo:     POST {BASE}/api/demo/full-pipeline")
    print(f"\n  Try the interactive docs at {BASE}/docs to explore all endpoints.\n")


if __name__ == "__main__":
    try:
        main()
    except httpx.ConnectError:
        print(f"\n[FAIL] Cannot connect to {BASE}")
        print("   Make sure the backend is running: uvicorn src.main:app --reload")
        sys.exit(1)
    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[FAIL] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
