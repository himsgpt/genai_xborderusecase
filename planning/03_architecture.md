# 03 — Technical Architecture

**Prerequisites:** MVP scope locked, innovation validated  
**Purpose:** Define HOW to build the system with minimal cost, maximum speed

---

## 🎯 Architecture Principles (Non-Negotiable)

### 1. **Local-First Development**
- Entire system runs on your laptop (Docker Compose)
- No cloud dependencies during development
- Deploy only when ready for beta users
- **Why:** $0 cost until revenue

### 2. **Domain-Driven Design**
- Clean separation: Domain → Application → Infrastructure → API
- Business logic independent of frameworks
- Easy to test, refactor, extend
- **Why:** Maintainability for solo founder

### 3. **Agent-First Architecture**
- AI agents are first-class citizens, not afterthoughts
- Clear orchestration layer
- Observable, debuggable, cost-controlled
- **Why:** This is what makes you innovative

### 4. **Data Minimalism**
- Store only what's necessary
- No PII unless required
- Anonymize/hash where possible
- **Why:** GDPR compliance, security

### 5. **Cost-Conscious Infra**
- Use free tiers aggressively
- Ollama for dev, GPT-4o-mini for prod
- Pay per use, not reserved instances
- **Why:** Runway preservation

---

## 🧱 System Architecture (High-Level)

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                             │
│  React + Vite + Tailwind CSS (Vercel - $0 free tier)       │
│  - Dashboard UI                                             │
│  - Auth flows                                               │
│  - Transaction detail views                                 │
│  - Recommendation UI                                        │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │ HTTPS / REST API
                 │
┌────────────────┴────────────────────────────────────────────┐
│                      API Layer                               │
│  FastAPI (Python 3.11+)                                     │
│  - REST endpoints                                           │
│  - JWT authentication                                       │
│  - Request validation (Pydantic)                            │
│  - Rate limiting                                            │
└────────────────┬────────────────────────────────────────────┘
                 │
                 │
┌────────────────┴────────────────────────────────────────────┐
│                  Application Layer                           │
│  - Use cases (Analyze Payment, Generate Recommendations)    │
│  - Orchestration logic                                      │
│  - Agent coordination                                       │
└────────────────┬────────────────────────────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼──────┐ ┌──▼──────┐ ┌─▼─────────────────────────────────┐
│  Domain   │ │ Agents  │ │    Infrastructure                 │
│  Layer    │ │ Layer   │ │                                   │
│           │ │         │ │  - Database (PostgreSQL)          │
│ Entities: │ │ Agents: │ │  - External APIs (Stripe)         │
│ - User    │ │ - Flow  │ │  - LLM (OpenAI / Ollama)          │
│ - Payment │ │   Recon │ │  - Cache (Redis)                  │
│ - Flow    │ │ - Cost  │ │  - Email (SendGrid)               │
│ - Fee     │ │   Attr  │ │  - Storage (Local / S3)           │
│ - Recom   │ │ - Optim │ │                                   │
│           │ │         │ │                                   │
│ Services: │ │ Coordin:│ │                                   │
│ - Payment │ │ - Lang  │ │                                   │
│   Analyzer│ │   Graph │ │                                   │
│ - Leakage │ │         │ │                                   │
│   Detector│ │         │ │                                   │
└───────────┘ └─────────┘ └───────────────────────────────────┘
```

---

## 📦 Tech Stack (Locked)

### Backend

**Framework:** FastAPI (Python 3.11+)
- **Why:** Fast, modern, async, excellent docs, Pydantic validation
- **Alternatives considered:** Django (too heavy), Flask (too minimal), Node (wrong language)

**Database:** PostgreSQL 15+
- **Why:** JSONB for flexible storage, mature, free tier available
- **Alternatives considered:** MySQL (less flexible), MongoDB (overkill), SQLite (not production-ready)

**ORM:** SQLAlchemy 2.0
- **Why:** Mature, type hints, async support
- **Alternatives considered:** Raw SQL (too much boilerplate), Django ORM (framework lock-in)

**Agent Framework:** LangGraph
- **Why:** State machines for complex flows, LangSmith observability, active development
- **Alternatives considered:** CrewAI (less mature), AutoGen (too research-y), custom (too much work)

**LLM (Development):** Ollama (Llama 3.1 8B)
- **Why:** $0 cost, runs locally, good enough for development
- **Alternatives:** None that are free

**LLM (Production):** OpenAI GPT-4o-mini
- **Why:** $0.15/1M input tokens, fast, reliable, good reasoning
- **Alternatives considered:** GPT-4o (too expensive), Claude (rate limits), Gemini (less reliable)

**Task Queue:** Redis + Celery (if needed)
- **Why:** Async processing for long-running analysis jobs
- **Alternatives:** Background threads (not scalable), RQ (less features)
- **Decision:** Start without queue, add if analysis >30 seconds

**Caching:** Redis (if needed)
- **Why:** Fast lookups for corridor data, fee rate cards
- **Decision:** Start without, add if performance issue

### Frontend

**Framework:** React 18 + Vite
- **Why:** Fast dev experience, modern, component-based
- **Alternatives considered:** Next.js (overkill for MVP), Vue (less ecosystem), Svelte (too niche)

**Styling:** Tailwind CSS
- **Why:** Rapid UI development, no custom CSS, responsive built-in
- **Alternatives considered:** Material-UI (heavy), Bootstrap (dated), CSS-in-JS (complexity)

**Charts:** Recharts
- **Why:** React-native, simple API, good-looking defaults
- **Alternatives considered:** Chart.js (not React-native), D3 (too complex), Victory (less active)

**State Management:** Zustand
- **Why:** Minimal boilerplate, TypeScript support, small bundle
- **Alternatives considered:** Redux (overkill), Context API (too manual), Jotai (too new)

**HTTP Client:** Axios
- **Why:** Interceptors for auth, error handling, timeout management
- **Alternatives considered:** Fetch (too manual), SWR (opinionated)

### Infrastructure

**Containerization:** Docker + Docker Compose
- **Why:** Consistent dev/prod environments, easy dependencies
- **Alternatives:** None viable for solo dev

**Backend Hosting:** Railway
- **Why:** $5/month, PostgreSQL included, auto-deploy from Git, no DevOps
- **Alternatives considered:** AWS (complex), Heroku ($$$), DigitalOcean (requires setup), Fly.io (less polished)

**Frontend Hosting:** Vercel
- **Why:** $0 for hobby tier, auto-deploy, edge network, no config
- **Alternatives considered:** Netlify (similar), AWS S3 (manual), Railway (frontend not their strength)

**Database (Production):** Railway PostgreSQL
- **Why:** Included with backend hosting, managed backups, connection pooling
- **Alternatives:** Neon ($0 tier), Supabase (overkill), self-hosted (no time)

**Email:** Resend
- **Why:** $0 for 3k emails/month, modern API, good deliverability
- **Alternatives:** SendGrid (complex pricing), Mailgun (dated), AWS SES (requires verification)

**Monitoring:** Sentry (errors) + LangSmith (LLM observability)
- **Why:** Sentry = $0 for 5k errors/month, LangSmith = $0 for 5k traces/month
- **Alternatives:** Rollbar, Datadog (too expensive for MVP)

**Analytics:** Plausible (if needed)
- **Why:** Privacy-friendly, simple, cheap
- **Decision:** Start without, add if needed for funnel optimization

---

## 🗂️ Database Schema (Core Tables)

### Users Table
```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    name VARCHAR(255),
    company VARCHAR(255),
    stripe_account_id VARCHAR(255) UNIQUE, -- Stripe Connect account ID
    stripe_access_token TEXT, -- Encrypted
    stripe_refresh_token TEXT, -- Encrypted
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    last_login_at TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_stripe_account ON users(stripe_account_id);
```

### Payments Table
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    stripe_payout_id VARCHAR(255) UNIQUE NOT NULL,
    corridor VARCHAR(20) NOT NULL, -- e.g., "USD_EUR"
    amount_sent DECIMAL(15, 2) NOT NULL,
    currency_sent VARCHAR(3) NOT NULL,
    amount_received DECIMAL(15, 2) NOT NULL,
    currency_received VARCHAR(3) NOT NULL,
    initiated_at TIMESTAMP NOT NULL,
    settled_at TIMESTAMP,
    status VARCHAR(50), -- pending, paid, failed
    raw_data JSONB, -- Full Stripe payout object
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_payments_user ON payments(user_id);
CREATE INDEX idx_payments_corridor ON payments(corridor);
CREATE INDEX idx_payments_initiated ON payments(initiated_at DESC);
```

### Analyses Table
```sql
CREATE TABLE analyses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    payment_id UUID NOT NULL REFERENCES payments(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Expected values
    expected_amount DECIMAL(15, 2),
    expected_fx_rate DECIMAL(10, 6),
    
    -- Actual values
    actual_fx_rate DECIMAL(10, 6),
    
    -- Fee breakdown
    platform_fee DECIMAL(15, 2),
    intermediary_fee DECIMAL(15, 2),
    fx_spread DECIMAL(15, 2),
    other_fees DECIMAL(15, 2),
    
    -- Leakage
    total_leakage DECIMAL(15, 2),
    leakage_percentage DECIMAL(5, 2),
    
    -- Flow reconstruction
    reconstructed_flow JSONB, -- Agent output: [{hop: "Stripe", fee: 25}, ...]
    confidence_score DECIMAL(3, 2), -- 0.0 to 1.0
    
    -- Metadata
    analyzed_at TIMESTAMP DEFAULT NOW(),
    analysis_duration_ms INTEGER,
    llm_model VARCHAR(100)
);

CREATE INDEX idx_analyses_payment ON analyses(payment_id);
CREATE INDEX idx_analyses_user ON analyses(user_id);
```

### Recommendations Table
```sql
CREATE TABLE recommendations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analyses(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    
    -- Recommendation content
    title VARCHAR(255) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50), -- route_switch, batching, timing, fx_optimization
    
    -- Value proposition
    estimated_savings DECIMAL(15, 2),
    estimated_savings_annual DECIMAL(15, 2),
    effort VARCHAR(20), -- low, medium, high
    risk VARCHAR(20), -- low, medium, high
    
    -- Implementation
    implementation_guide TEXT,
    
    -- Tracking
    status VARCHAR(50) DEFAULT 'pending', -- pending, in_progress, implemented, dismissed
    implemented_at TIMESTAMP,
    actual_savings DECIMAL(15, 2),
    
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_recommendations_user ON recommendations(user_id);
CREATE INDEX idx_recommendations_status ON recommendations(status);
```

### Corridors Reference Table (Static Data)
```sql
CREATE TABLE corridors (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    code VARCHAR(20) UNIQUE NOT NULL, -- "USD_EUR"
    currency_from VARCHAR(3) NOT NULL,
    currency_to VARCHAR(3) NOT NULL,
    
    -- Typical characteristics (updated periodically)
    typical_fee_percentage DECIMAL(5, 4),
    typical_flat_fee DECIMAL(10, 2),
    typical_settlement_days INTEGER,
    
    -- Rate card data (public sources)
    rate_cards JSONB, -- [{provider: "Stripe", fee: 0.25}, ...]
    
    supported BOOLEAN DEFAULT true,
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_corridors_code ON corridors(code);
```

---

## 🤖 Agent Architecture (The Innovation Core)

### Agent Orchestration (LangGraph State Machine)

```python
from langgraph.graph import StateGraph

class PaymentAnalysisState(TypedDict):
    payment_id: str
    user_id: str
    raw_payment_data: dict
    corridor: str
    amount_sent: float
    amount_received: float
    
    # Outputs from agents
    reconstructed_flow: list[dict] | None
    fee_breakdown: dict | None
    leakage_amount: float | None
    recommendations: list[dict] | None
    
    # Metadata
    confidence: float
    errors: list[str]

workflow = StateGraph(PaymentAnalysisState)

# Agent nodes
workflow.add_node("flow_reconstruction", flow_reconstruction_agent)
workflow.add_node("fee_attribution", fee_attribution_agent)
workflow.add_node("leakage_detection", leakage_detection_agent)
workflow.add_node("optimization", optimization_agent)

# Edges
workflow.set_entry_point("flow_reconstruction")
workflow.add_edge("flow_reconstruction", "fee_attribution")
workflow.add_edge("fee_attribution", "leakage_detection")
workflow.add_edge("leakage_detection", "optimization")
workflow.add_edge("optimization", END)

app = workflow.compile()
```

### Agent 1: Flow Reconstruction Agent

**Purpose:** Identify intermediaries in payment route

**Inputs:**
- Payment metadata (Stripe payout object)
- Corridor (USD→EUR)
- Amount sent, amount received
- Timing data

**Process:**
1. Load corridor knowledge (typical routes for USD→EUR)
2. Use LLM to reason about likely intermediaries
3. Estimate hops based on amount deltas

**Prompt Template:**
```
You are a payment routing expert. Analyze this cross-border payment:

Corridor: {corridor}
Sent: {amount_sent} {currency_sent}
Received: {amount_received} {currency_received}
Initiated: {initiated_at}
Settled: {settled_at}

Based on industry knowledge:
1. What intermediaries likely handled this payment?
2. What is the typical route for this corridor?
3. List each hop with estimated fee.

Output JSON:
{
  "hops": [
    {"entity": "Stripe", "type": "PSP", "fee_usd": 25, "confidence": 0.9},
    {"entity": "Citi Correspondent", "type": "Bank", "fee_usd": 15, "confidence": 0.7},
    ...
  ],
  "total_estimated_fees": 85,
  "confidence_score": 0.75
}
```

**Output:**
```python
{
    "hops": [
        {"entity": "Stripe", "type": "PSP", "fee_usd": 25, "confidence": 0.9},
        {"entity": "SWIFT Network", "type": "Network", "fee_usd": 15, "confidence": 0.8},
        {"entity": "Receiving Bank", "type": "Bank", "fee_usd": 40, "confidence": 0.7}
    ],
    "total_estimated_fees": 80,
    "confidence_score": 0.78
}
```

### Agent 2: Fee Attribution Agent

**Purpose:** Break down total cost into components

**Inputs:**
- Flow reconstruction output
- Corridor rate cards (from database)
- Actual amount deltas

**Process:**
1. Calculate expected FX using mid-market rate
2. Attribute difference between expected and actual to FX spread
3. Allocate remaining variance to intermediary fees
4. Cross-check with known rate cards

**Logic:**
```python
def attribute_fees(payment, flow):
    # Get mid-market FX rate
    mid_rate = get_fx_rate(payment.currency_sent, payment.currency_received, payment.initiated_at)
    expected_amount = payment.amount_sent * mid_rate
    
    # Calculate FX spread
    actual_rate = payment.amount_received / payment.amount_sent
    fx_spread = (mid_rate - actual_rate) * payment.amount_sent
    
    # Calculate total fees
    total_fees = expected_amount - payment.amount_received
    intermediary_fees = total_fees - fx_spread
    
    # Breakdown by hop
    for hop in flow['hops']:
        if hop['type'] == 'PSP':
            hop['fee_actual'] = get_psp_fee(hop['entity'], payment.amount_sent)
        elif hop['type'] == 'Bank':
            hop['fee_actual'] = estimate_bank_fee(hop['entity'], payment.corridor)
    
    return {
        "platform_fee": flow['hops'][0]['fee_actual'],
        "intermediary_fees": intermediary_fees,
        "fx_spread": fx_spread,
        "total_fees": total_fees
    }
```

### Agent 3: Leakage Detection Agent

**Purpose:** Identify what's unusual/excessive

**Inputs:**
- Fee breakdown
- Historical baseline for corridor (from database)

**Process:**
1. Compare actual fees to corridor baseline
2. Flag anomalies (>10% variance)
3. Categorize leakage type (FX, intermediary, timing)

**Logic:**
```python
def detect_leakage(payment, fees, corridor_baseline):
    leakage = []
    
    # FX spread leakage
    if fees['fx_spread_pct'] > corridor_baseline['typical_fx_spread'] * 1.1:
        leakage.append({
            "type": "fx_spread",
            "amount": fees['fx_spread'] - (payment.amount_sent * corridor_baseline['typical_fx_spread']),
            "reason": f"FX spread {fees['fx_spread_pct']:.2%} exceeds typical {corridor_baseline['typical_fx_spread']:.2%}"
        })
    
    # Intermediary fee leakage
    if fees['intermediary_fees'] > corridor_baseline['typical_intermediary_fee'] * 1.2:
        leakage.append({
            "type": "intermediary",
            "amount": fees['intermediary_fees'] - corridor_baseline['typical_intermediary_fee'],
            "reason": "Excessive intermediary fees (route optimization needed)"
        })
    
    return {
        "total_leakage": sum(l['amount'] for l in leakage),
        "leakage_items": leakage
    }
```

### Agent 4: Optimization Agent

**Purpose:** Generate actionable recommendations

**Inputs:**
- Leakage detection output
- Corridor alternatives (from database)
- Customer payment patterns

**Process:**
1. Query alternative routes for corridor
2. Simulate cost for each alternative
3. Rank by savings potential
4. Generate implementation guide

**Prompt Template:**
```
You are a payment optimization consultant. Based on this analysis:

Current route: {current_route}
Total cost: {total_cost}
Leakage: {leakage_amount}

Alternative routes available:
{alternative_routes}

Generate 3 recommendations:
1. Highest savings (cheapest route)
2. Fastest route (if different)
3. Low-effort optimization (batching, timing, etc)

For each recommendation:
- Title (one sentence)
- Description (why this works)
- Estimated savings ($ annual)
- Effort (low/medium/high)
- Risk (low/medium/high)
- Implementation steps (3-5 bullet points)

Output JSON format.
```

**Output:**
```python
{
    "recommendations": [
        {
            "title": "Switch USD→EUR payments to Wise Business",
            "description": "Wise charges 0.43% all-in vs your current 1.35%",
            "estimated_savings_annual": 3750,
            "effort": "medium",
            "risk": "low",
            "implementation_guide": "1. Create Wise Business account...\n2. Verify business...\n..."
        },
        ...
    ]
}
```

---

## 🔐 Security Architecture

### Authentication Flow

**User Registration:**
1. User submits email + password
2. Backend hashes password (bcrypt, cost 12)
3. Store in database
4. Send verification email (Resend)
5. User clicks link → account activated

**User Login:**
1. User submits email + password
2. Backend validates password hash
3. Generate JWT token (HS256, 24h expiry)
4. Return token + refresh token (7d expiry)
5. Frontend stores in localStorage (or httpOnly cookie)

**Stripe OAuth Flow:**
1. User clicks "Connect Stripe"
2. Frontend redirects to Stripe OAuth URL
3. User authorizes access
4. Stripe redirects back with auth code
5. Backend exchanges code for access token + refresh token
6. Encrypt tokens (Fernet) before storing
7. Store user <-> Stripe account mapping

**Token Management:**
- Access token: 24h expiry (short-lived)
- Refresh token: 7d expiry (rotate on use)
- Stripe tokens: Encrypted at rest (Fernet key in env var)

### Data Protection

**Encryption:**
- Passwords: bcrypt (cost 12)
- Stripe tokens: Fernet symmetric encryption
- Database: TLS in transit, encryption at rest (Railway default)
- API: HTTPS only, HSTS headers

**PII Handling:**
- Store only: email, name, company (minimal)
- Do NOT store: payment card details (Stripe handles), SSNs, addresses
- Anonymize: Payment data uses Stripe IDs, no merchant customer PII

**GDPR Compliance (MVP-level):**
- Privacy policy published
- Terms of service published
- Data deletion: Cascade deletes on user deletion
- Data export: API endpoint for user data (future)

---

## 🚀 Deployment Architecture

### Development Environment (Local)

**Docker Compose Stack:**
```yaml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: xborder_dev
      POSTGRES_USER: dev
      POSTGRES_PASSWORD: dev123
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  backend:
    build: ./backend
    command: uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
    volumes:
      - ./backend:/app
    ports:
      - "8000:8000"
    environment:
      DATABASE_URL: postgresql://dev:dev123@postgres:5432/xborder_dev
      JWT_SECRET: dev-secret-key
      STRIPE_CLIENT_ID: ${STRIPE_CLIENT_ID}
      STRIPE_CLIENT_SECRET: ${STRIPE_CLIENT_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      OLLAMA_BASE_URL: http://host.docker.internal:11434
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    command: npm run dev
    volumes:
      - ./frontend:/app
    ports:
      - "5173:5173"
    environment:
      VITE_API_URL: http://localhost:8000

volumes:
  postgres_data:
```

**Local Setup Commands:**
```bash
# Start all services
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head

# View logs
docker-compose logs -f backend

# Stop all services
docker-compose down
```

### Production Environment

**Backend (Railway):**
- Dockerfile deployed via GitHub integration
- PostgreSQL addon included
- Environment variables in Railway dashboard
- Auto-deploy on `main` branch push
- Health check endpoint: `GET /health`

**Frontend (Vercel):**
- Vite build deployed via GitHub integration
- Environment variable: `VITE_API_URL` = Railway backend URL
- Auto-deploy on `main` branch push
- Edge network (global CDN)

**Database Migrations:**
- Alembic for schema changes
- Run migrations manually after deploy:
  ```bash
  railway run alembic upgrade head
  ```

**Cost Estimate (Production):**
| Service | Cost |
|---------|------|
| Railway (backend + DB) | $5-10/month (starter tier) |
| Vercel (frontend) | $0 (hobby tier) |
| OpenAI (GPT-4o-mini) | $5-50/month (depends on volume) |
| Resend (email) | $0 (free tier 3k/month) |
| Sentry (monitoring) | $0 (free tier) |
| **Total** | **$10-60/month** |

---

## 📊 Observability & Monitoring

### Error Tracking (Sentry)

**Backend:**
```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=os.getenv("SENTRY_DSN"),
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,  # 10% of requests
    environment="production"
)
```

**Frontend:**
```typescript
import * as Sentry from "@sentry/react";

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 0.1,
});
```

### LLM Observability (LangSmith)

**LangGraph Integration:**
```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["LANGCHAIN_PROJECT"] = "xborder-prod"

# All LangGraph executions auto-traced
```

**Metrics to Track:**
- Latency per agent (ms)
- Token usage per analysis
- Cost per analysis ($)
- Error rate per agent
- Confidence scores distribution

### Application Metrics

**Key Metrics (Log to Database):**
```python
@dataclass
class AnalysisMetrics:
    payment_id: str
    total_duration_ms: int
    llm_duration_ms: int
    database_duration_ms: int
    llm_tokens_used: int
    llm_cost_usd: float
    confidence_score: float
    error: str | None
```

**Dashboard (Future):**
- Average analysis time
- Success rate (% without errors)
- Cost per analysis
- User engagement (analyses per user per week)

---

## 🧪 Testing Strategy

### Unit Tests (Critical Paths Only)

**What to test:**
- Domain logic (fee calculation, leakage detection)
- Agent output parsing
- API endpoint validation

**What NOT to test:**
- Boilerplate (CRUD operations)
- Third-party libraries
- UI components (no time for MVP)

**Example:**
```python
def test_fee_attribution():
    payment = Payment(
        amount_sent=10000,
        currency_sent="USD",
        amount_received=9156,
        currency_received="EUR"
    )
    
    fees = attribute_fees(payment)
    
    assert fees['total_fees'] > 0
    assert fees['fx_spread'] + fees['intermediary_fees'] == fees['total_fees']
    assert 0 <= fees['fx_spread_pct'] <= 5  # Sanity check
```

### Integration Tests (Smoke Tests)

**Critical flows:**
1. User signup → login → JWT issued
2. Stripe OAuth → tokens stored
3. Fetch payments from Stripe API
4. Analyze payment → store results

**Run before each deploy:**
```bash
pytest tests/integration --maxfail=1
```

### Manual Testing (MVP)

**No automated UI tests.** Too slow for solo founder.

**Checklist before launch:**
- [ ] Signup flow works
- [ ] Stripe OAuth works
- [ ] Payments fetch from Stripe
- [ ] Analysis completes without errors
- [ ] Dashboard shows results
- [ ] Recommendations display
- [ ] Mobile responsive

**Test with real Stripe test account, not mocks.**

---

## 🔄 Development Workflow

### Git Branch Strategy

**Simple trunk-based:**
- `main` branch = production
- Feature branches = short-lived (1-2 days max)
- Merge to `main` via PR (even solo, good discipline)

**Branch naming:**
- `feat/stripe-oauth`
- `fix/fee-calculation`
- `refactor/agent-prompts`

### CI/CD Pipeline (Minimal)

**GitHub Actions (`.github/workflows/deploy.yml`):**
```yaml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend
          pip install -r requirements.txt
          pytest tests/integration

  deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to Railway
        run: echo "Railway auto-deploys on push to main"
      - name: Deploy to Vercel
        run: echo "Vercel auto-deploys on push to main"
```

**Auto-deploy:**
- Railway watches `main` branch, deploys backend
- Vercel watches `main` branch, deploys frontend

---

## ✅ Architecture Decision Records (ADRs)

### ADR-001: FastAPI vs Django
**Decision:** FastAPI  
**Reason:** Async support, faster dev loop, modern type hints, Pydantic validation  
**Trade-off:** Less batteries-included than Django (no admin panel)

### ADR-002: LangGraph vs CrewAI
**Decision:** LangGraph  
**Reason:** State machine clarity, LangSmith observability, production-ready  
**Trade-off:** Slightly steeper learning curve

### ADR-003: PostgreSQL vs MongoDB
**Decision:** PostgreSQL  
**Reason:** JSONB for flexibility, relational for structured data, better tooling  
**Trade-off:** Slightly more schema management

### ADR-004: Railway vs AWS
**Decision:** Railway  
**Reason:** $5/month, zero DevOps, managed DB, auto-deploys  
**Trade-off:** Less control, vendor lock-in (acceptable for MVP)

### ADR-005: GPT-4o-mini vs Llama
**Decision:** Both (Ollama dev, GPT-4o-mini prod)  
**Reason:** $0 dev cost, production reliability  
**Trade-off:** Two codepaths to maintain (minimal)

---

## 🚦 Architecture Validation Checklist

Before building:

- [ ] All tech choices have clear rationale (not just "it's cool")
- [ ] Stack is proven (no beta/alpha software)
- [ ] Can run entire system on laptop (Docker Compose)
- [ ] Production cost <$50/month until revenue
- [ ] Agent architecture is testable/debuggable
- [ ] Database schema supports MVP features (no more, no less)
- [ ] Security basics covered (encryption, auth, HTTPS)
- [ ] Can deploy in <1 hour (Railway + Vercel)

**If any unchecked: Fix architecture before building.**

---

**Next:** `04_agent_system_design.md` → Detailed agent prompts and logic
