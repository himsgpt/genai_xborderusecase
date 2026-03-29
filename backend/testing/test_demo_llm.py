"""Quick test: run demo pipeline and check LLM enhancement."""
import httpx
import asyncio
import json
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

async def main():
    async with httpx.AsyncClient(timeout=120) as c:
        print("Running demo pipeline (with LLM)...")
        r = await c.post("http://localhost:8000/api/demo/full-pipeline")
        d = r.json()

        print(f"\nStatus: {d.get('status')}")
        print(f"AI Enhanced: {d.get('ai_enhanced')}")
        print(f"FX Source: {d.get('fx_rate_source')}")

        s = d.get("summary", {})
        print(f"\n--- Summary ---")
        print(f"Payments analyzed: {s.get('payments_analyzed')}")
        print(f"Total sent: ${s.get('total_sent_usd', 0):,.2f}")
        print(f"Total fees: ${s.get('total_fees_usd', 0):,.2f}")
        print(f"Total leakage: ${s.get('total_leakage_usd', 0):,.2f}")
        print(f"Avg cost: {s.get('avg_cost_pct', 0):.2f}%")
        print(f"Annual savings: ${s.get('potential_annual_savings_usd', 0):,.2f}")
        print(f"Headline: {s.get('headline', '')}")

        print(f"\n--- Recommendations ({d.get('recommendations_count', 0)}) ---")
        for rec in d.get("top_recommendations", []):
            title = rec.get("title", "?")
            cat = rec.get("category", "?")
            savings = rec.get("estimated_savings_annual", 0)
            print(f"  [{cat}] {title}: ${savings:,.0f}/yr")

        token = d["auth"]["token"]
        headers = {"Authorization": f"Bearer {token}"}

        print("\n--- Dashboard Summary ---")
        r2 = await c.get("http://localhost:8000/api/analysis/summary", headers=headers)
        if r2.status_code == 200:
            summary = r2.json()
            print(f"total_payments_analyzed: {summary.get('total_payments_analyzed')}")
            print(f"total_fees_usd: {summary.get('total_fees_usd')}")
            print(f"total_leakage_usd: {summary.get('total_leakage_usd')}")
            print(f"potential_annual_savings_usd: {summary.get('potential_annual_savings_usd')}")
        else:
            print(f"Summary failed: {r2.status_code}")

        print("\n--- Analysis Explanations (first 2) ---")
        r3 = await c.get("http://localhost:8000/api/analysis", headers=headers)
        if r3.status_code == 200:
            analyses = r3.json()
            for a in analyses[:2]:
                expl = a.get("explanation", "")
                print(f"\nPayment {a['payment_id'][:8]}... ({a.get('leakage_pct', 0):.2f}% leakage):")
                print(expl[:600] + ("..." if len(expl) > 600 else ""))
        else:
            print(f"Analyses failed: {r3.status_code}")

asyncio.run(main())
