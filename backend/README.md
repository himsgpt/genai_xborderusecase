# XBorder Payment Intelligence - Backend

AI-powered cross-border payment analysis engine that **exposes hidden fees, attributes costs across intermediaries, reconstructs payment flows, and generates actionable savings recommendations**.

---

## Architecture (DDD-Lite)

```
backend/src/
|
|-- main.py                          # FastAPI app factory, lifespan, middleware, router wiring
|-- __init__.py
|
|-- api/                             # API Layer -- HTTP interface
|   |-- __init__.py
|   |-- schemas.py                   # Pydantic request/response models
|   |-- deps.py                      # Shared FastAPI dependencies (get_db, get_current_user_id)
|   |-- routes/
|       |-- auth.py                  # POST /api/auth/register, /api/auth/login
|       |-- payments.py              # GET/POST /api/payments, POST /api/payments/demo
|       |-- analysis.py              # POST /api/analysis/run, GET /api/analysis, /summary, /{id}
|       |-- recommendations.py       # GET /api/recommendations, PATCH /{id}/status
|       |-- demo.py                  # POST /api/demo/full-pipeline (one-click demo)
|       |-- stripe.py                # Stripe integration: connect, sync charges, view fees, live FX
|
|-- domain/                          # Domain Layer -- core business logic (zero framework deps)
|   |-- __init__.py
|   |-- services/
|       |-- __init__.py              # Public exports: analyze_payment, corridors, rates
|       |-- analysis.py              # Fee attribution, flow reconstruction, leakage detection
|       |-- corridor_data.py         # Payment corridor knowledge base, FX rates, benchmarks
|
|-- infrastructure/                  # Infrastructure Layer -- external concerns
|   |-- __init__.py
|   |-- config.py                    # Pydantic Settings (env vars, DB URL, JWT, LLM, Stripe config)
|   |-- auth.py                      # JWT token creation/decode, bcrypt password hashing
|   |-- fx_rates.py                  # Live FX rates from Frankfurter/ECB API (free, no key)
|   |-- stripe_client.py            # Stripe SDK wrapper -- pull charges, balance_transactions, fee_details
|   |-- database/
|       |-- __init__.py              # Re-exports: engine, Base, get_db, SessionLocal
|       |-- connection.py            # SQLAlchemy async engine, session factory
|       |-- models.py               # ORM models: UserModel, PaymentModel, AnalysisModel, RecommendationModel
|
|-- agents/                          # Agents Layer -- future AI/LLM enhancement
    |-- __init__.py                  # Placeholder: LLM-powered explanations, smart recommendations
```

### Request Flow

```
HTTP Request
  -> api/routes/*.py      (parse request, validate with Pydantic schemas)
  -> api/deps.py          (inject DB session, authenticate user via JWT)
  -> domain/services/     (run business logic: analyze_payment, corridor lookup)
  -> infrastructure/      (persist to Postgres via SQLAlchemy models)
  -> api/schemas.py       (serialize response)
HTTP Response
```

---

## Database Schema (4 Tables)

| Table | Purpose |
|-------|---------|
| **users** | Registered users. Fields: id (UUID), email, password_hash, name, company, created_at |
| **payments** | Raw payment records. Fields: id, user_id, corridor, amount_sent/received, currency_sent/received, initiated_at, settled_at, psp, status, raw_data |
| **analyses** | Analysis results per payment. Fields: id, payment_id, user_id, expected_amount, mid_market_rate, actual_rate, platform_fee, intermediary_fee, fx_spread_cost, total_fees, total_leakage, leakage_pct, reconstructed_flow, confidence_score, explanation |
| **recommendations** | Actionable savings recommendations. Fields: id, analysis_id, user_id, title, description, category, estimated_savings, estimated_savings_annual, effort, risk, implementation_steps, status |

---

## API Endpoints (15 total)

### Health & Root
| Method | Path | Business Purpose |
|--------|------|-----------------|
| GET | `/` | API info + supported corridors |
| GET | `/health` | System health check |

### Auth (`/api/auth`)
| Method | Path | Business Purpose |
|--------|------|-----------------|
| POST | `/register` | Create account (email, password, name, company) |
| POST | `/login` | Authenticate, receive JWT token |

### Payments (`/api/payments`)
| Method | Path | Business Purpose |
|--------|------|-----------------|
| GET | `/` | List user's payments |
| POST | `/` | Record a new cross-border payment |
| POST | `/demo` | Load 8 demo payments across 3 corridors |

### Analysis (`/api/analysis`)
| Method | Path | Business Purpose |
|--------|------|-----------------|
| POST | `/run` | **Core value** -- analyze all payments: fee attribution, flow reconstruction, leakage detection |
| GET | `/summary` | Aggregate intelligence: total leakage, corridor breakdown, annual savings projection |
| GET | `/` | List all individual analysis results |
| GET | `/{id}` | Detailed single analysis with full fee breakdown |

### Recommendations (`/api/recommendations`)
| Method | Path | Business Purpose |
|--------|------|-----------------|
| GET | `/` | List actionable cost-saving recommendations |
| PATCH | `/{id}/status` | Accept/reject/implement a recommendation |

### Stripe Integration (`/api/stripe`)
| Method | Path | Business Purpose |
|--------|------|-----------------|
| POST | `/connect` | Connect Stripe account with API key (test or live) |
| GET | `/status` | Check if Stripe is connected |
| POST | `/sync` | **Import real charges** from Stripe with fee_details + exchange_rate |
| GET | `/charges` | View raw Stripe charges with fee breakdowns (transparency) |
| GET | `/balance-transactions` | View raw Stripe balance transactions |
| GET | `/fx-rate?currency_from=USD&currency_to=EUR` | Get live mid-market FX rate from ECB |

### Demo (`/api/demo`)
| Method | Path | Business Purpose |
|--------|------|-----------------|
| POST | `/full-pipeline` | **One-click demo**: creates user, loads payments, runs analysis, returns complete results |

---

## Live Integrations

### Live FX Rates (Frankfurter / ECB)
- **Free, no API key needed**, unlimited requests
- ECB mid-market rates updated daily at 16:00 CET
- Used automatically when `FX_RATE_SOURCE=live` (default)
- Provides the baseline to detect FX spread/markup in Stripe's rates
- Endpoint: `GET /api/stripe/fx-rate?currency_from=USD&currency_to=EUR`

### Stripe Integration
- Connect your Stripe account via API key (test mode: `sk_test_*`)
- Pulls **real charges** with expanded `balance_transaction`
- Extracts **fee_details**: exact Stripe processing fee, FX fee, tax
- Extracts **exchange_rate**: the actual FX rate Stripe applied
- Compares against ECB mid-market to calculate **real FX spread**
- Confidence score jumps from 78% (heuristic) to **95%** (real data)

**How it works:**
```
Your Stripe Account
  -> GET /v1/charges (with expanded balance_transaction)
  -> fee_details: [{type: "stripe_fee", amount: 2.90}, ...]
  -> exchange_rate: 0.8430 (Stripe's rate)
  
ECB Mid-Market Rate: 0.8471

FX Spread = |0.8471 - 0.8430| / 0.8471 = 0.48%
On $10,000 = $48 hidden cost from FX markup alone
```

---

## Setup & Run

### Prerequisites
- Docker Desktop (for PostgreSQL)
- Python 3.10+ (Anaconda or venv)

### 1. Start PostgreSQL
```bash
cd xborder_settlement
docker-compose up -d postgres

docker start xborder_postgres; Start-Sleep -Seconds 5; docker ps
```

### 2. Create & activate virtual environment
```bash
cd backend

# Using venv (Windows with Anaconda)
C:\Users\HIMANSHU\anaconda3\python.exe -m venv venv
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Environment variables
The `.env` file in the project root contains all config:
```
DATABASE_URL=postgresql+asyncpg://xborder:xborder123@localhost:5432/xborder
JWT_SECRET=your-secret-key
ENVIRONMENT=development
LLM_PROVIDER=none

# FX Rates: "live" (Frankfurter/ECB, default) or "hardcoded"
FX_RATE_SOURCE=live

# Stripe (optional — enables real payment data import)
# Get from: https://dashboard.stripe.com/test/apikeys
STRIPE_SECRET_KEY=sk_test_your_key_here
```

### 4. Run the backend
```bash
d:\Tech\GenAI\xborder_settlement\backend\venv\Scripts\python.exe -m uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload

uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

### 5. Test everything

live fx rate 
```bash
d:\Tech\GenAI\xborder_settlement\backend\venv\Scripts\python.exe -c "import httpx; r = httpx.get('http://localhost:8000/api/stripe/fx-rate', params={'currency_from': 'USD', 'currency_to': 'EUR'}); print(r.json())"

```

Live FX rates are working. The ECB mid-market rate for USD/EUR is 0.8471 today (vs our hardcoded 0.921). Now let me test all three corridors and the demo pipeline with live rates:
```bash
d:\Tech\GenAI\xborder_settlement\backend\venv\Scripts\python.exe -c "import httpx; c = httpx.Client(base_url='http://localhost:8000', timeout=30); pairs = [('USD','EUR'),('USD','INR'),('USD','GBP')]; [print(c.get('/api/stripe/fx-rate', params={'currency_from':f,'currency_to':t}).json()) for f,t in pairs]"
```

All three corridors returning live ECB rates. Now let me reset the DB and run the full demo pipeline with live rates:
```bash
docker exec xborder_postgres psql -U xborder -d xborder -c "DELETE FROM recommendations; DELETE FROM analyses; DELETE FROM payments; DELETE FROM users;"
```

python test_e2e.py: This runs 7 E2E tests: health check, demo pipeline, analysis summary, analysis list, recommendations, auth flow, and payment CRUD.

All 7 tests pass with live FX rates. Notice the key difference -- with live ECB rates (91.08 INR/USD today vs hardcoded 83.50), the analysis now correctly detects $2,195 in leakage on the USD->INR corridor and $26,343/year in potential savings. The negative fees on EUR and GBP corridors mean our demo data amounts are actually better than current mid-market (which makes sense -- the demo data was crafted with old rates).

### 6. Interactive API docs
Open: http://localhost:8000/docs

---

## Frontend

The frontend is a React + Vite + Tailwind CSS application at `frontend/`.

### Run frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

### Frontend pages
- **Login** -- Authentication with demo mode (one-click, no signup)
- **Dashboard** -- Stats cards, corridor charts, leakage distribution, corridor breakdown table
- **Payments** -- List/add payments, load demo data, trigger analysis
- **Analysis** -- Fee attribution charts, expandable analysis cards with flow reconstruction
- **Recommendations** -- Actionable savings cards with accept/reject/implement workflow

---

## Dependencies

### Required
- **FastAPI + Uvicorn** -- async web framework
- **SQLAlchemy + asyncpg** -- async PostgreSQL ORM
- **Pydantic + pydantic-settings** -- validation & config
- **bcrypt + PyJWT** -- authentication
- **httpx** -- async HTTP client (Frankfurter FX rates)
- **PostgreSQL 15** -- database (via Docker)

### Integrations (optional but powerful)
- **stripe** (Python SDK) -- connect Stripe account, pull real charges + fee breakdowns. Set `STRIPE_SECRET_KEY` in .env
- **Frankfurter/ECB** -- live mid-market FX rates (free, no key, enabled by default)
- **LLM Provider** (none by default) -- set `LLM_PROVIDER=openai|groq|ollama` for AI-enhanced explanations

---

## Business Value

The core analysis engine (`domain/services/analysis.py`) provides:
1. **Fee Attribution** -- breaks down total cost into platform fee, intermediary fee, and FX spread
2. **Payment Flow Reconstruction** -- infers the chain of intermediaries (PSP -> Correspondent Bank -> SWIFT -> Local Bank)
3. **Leakage Detection** -- compares actual costs against corridor benchmarks to find overcharges
4. **Actionable Recommendations** -- generates specific cost-saving suggestions with annual savings estimates

Demo results (8 payments, 3 corridors):
- Total fees detected: ~$2,229
- Money leakage: ~$959
- Annual savings potential: ~$11,511
- Recommendations generated: 3

---

## Next Steps

### Done
- [x] Live FX rates from ECB via Frankfurter API (free, no key)
- [x] Stripe integration -- connect, sync charges, real fee_details + exchange_rate
- [x] Analysis engine uses live rates + real Stripe fees when available
- [x] Confidence: 78% (heuristic) -> 95% (real Stripe data)

### Immediate (Week 1-2)
1. **Test with real Stripe account** -- Use `sk_test_*` key, create test charges, sync + analyze
2. **CSV/Excel Upload** -- Bulk import payments from bank exports (for non-Stripe sources)
3. **LLM Agent Integration** -- Add GPT-4o-mini explanations via the `agents/` layer
4. **More Corridors** -- Add EUR->GBP, GBP->INR, USD->MXN, etc.
5. **Historical FX Rates** -- Use Frankfurter date-specific rates for past payments

### Short-term (Week 3-4)
6. **Multi-PSP Support** -- PayPal, Wise, Payoneer API integrations
7. **User Dashboard Customization** -- Save preferred corridors, alert thresholds
8. **Email Alerts** -- Notify when leakage exceeds threshold
9. **Historical Trending** -- Track cost reduction over time
10. **PDF Report Generation** -- Exportable analysis reports

### Revenue Path
11. **Freemium Model** -- Free: 5 payments/month. Paid: unlimited + LLM + PDF reports
12. **API Access** -- Charge for programmatic analysis (per-payment pricing)
13. **White-label** -- Offer the engine to fintech platforms and payment aggregators
