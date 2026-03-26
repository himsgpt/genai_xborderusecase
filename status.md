What's been built
1. Live FX Rates (working now)
Frankfurter API (ECB data) -- free, no API key, unlimited requests
Today's live rates: USD/EUR = 0.8471, USD/INR = 91.08, USD/GBP = 0.7423
Cached for 1 hour, falls back to hardcoded if API is down
Used automatically in analysis -- FX_RATE_SOURCE=live (default)
Test it: GET http://localhost:8000/api/stripe/fx-rate?currency_from=USD&currency_to=INR

2. Stripe Integration (ready to connect)
6 new endpoints at /api/stripe/*:
POST /connect -- validate & save your Stripe API key
GET /status -- check connection
POST /sync -- pull real charges with fee_details + exchange_rate
GET /charges -- view raw Stripe data (transparency)
GET /balance-transactions -- view raw balance transactions
GET /fx-rate -- compare live ECB rate vs Stripe rate
Stores Stripe's fee_details and exchange_rate in raw_data JSON field
Analysis engine detects and uses real Stripe data automatically
Confidence jumps from 78% (heuristic) to 95% (real Stripe data)

3. Analysis Engine Enhanced
Accepts optional live_mid_rate, stripe_fee_details, stripe_exchange_rate
With Stripe: exact platform_fee from fee_details, FX spread = ECB vs Stripe rate
Without Stripe: falls back to corridor heuristics (still works)
How Stripe fee attribution works
Stripe balance_transaction.fee_details:  - stripe_fee: $2.90 (exact processing fee)  - stripe_fx_fee: variesStripe exchange_rate: 0.8430ECB mid-market rate: 0.8471FX spread = |0.8471 - 0.8430| / 0.8471 = 0.48%On $10,000 payment = $48 hidden cost from FX markup
To test with your Stripe account:
Go to https://dashboard.stripe.com/test/apikeys
Copy your sk_test_... key
Either set STRIPE_SECRET_KEY=sk_test_... in .env, or call:
   POST http://localhost:8000/api/stripe/connect   {"api_key": "sk_test_..."}
Sync your charges: POST http://localhost:8000/api/stripe/sync
Run analysis: POST http://localhost:8000/api/analysis/run (with auth token)
The analysis will now use real Stripe fees + live ECB rates for precise fee attribution.


How It Works in the UI
Open http://localhost:5173 in your browser. Here's the flow:
1. Login Page
Click "Try Demo (No signup needed)" -- this runs the full demo pipeline with live ECB rates and drops you into the dashboard with data already loaded
Or register/login with email + password
2. Dashboard
4 stat cards: Payments Analyzed, Total Fees, Money Leakage, Annual Savings
Bar chart: Costs by corridor (USD->EUR, USD->INR, USD->GBP)
Pie chart: Leakage distribution across corridors
Table: Detailed corridor breakdown with cost percentages
3. Payments Page
"Load Demo Data" -- loads 8 demo payments
"Add Payment" -- manually add a payment (select corridor, amounts, PSP)
"Run Analysis" -- triggers analysis with live ECB FX rates on all unanalyzed payments
Lists all payments with corridor, amounts, PSP, status
4. Analysis Page
Stacked bar chart: Fee attribution across payments (Platform / Intermediary / FX Spread)
Expandable cards for each payment showing:
Fee breakdown with progress bars
Mid-market vs actual rate comparison
Reconstructed payment route (PSP -> Correspondent -> Network -> Receiving Bank)
Confidence score (78% heuristic, 95% when Stripe data is available)
5. Recommendations Page
Actionable cost-saving cards with annual savings projections
Each has Accept / Reject / Implement workflow
Shows implementation steps (e.g., "Create Wise Business account", "Test with small payment")
Stripe Integration (currently via API, UI coming next)
Right now the Stripe sync is done via API calls. The next step would be adding a Settings/Integrations page to the UI where the user can:
Enter their Stripe API key
Click "Sync Charges" to pull real payment data
See real Stripe fee breakdowns in the Analysis page
Compare Stripe's FX rate vs ECB mid-market on each payment
Next Steps
Add a Settings/Integrations page in the frontend for Stripe connect + sync
LLM-enhanced explanations -- Groq key is configured, integrate it into the agents/ layer for natural-language payment analysis
Historical FX rates -- use date-specific ECB rates for past payments instead of today's rate
Multi-PSP -- add PayPal, Wise integrations alongside Stripe