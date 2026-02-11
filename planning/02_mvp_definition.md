# 02 — MVP Definition & Scope Lock

**Status:** ⚠️ Only read after validation complete  
**Prerequisites:** Customer interviews done, technical feasibility proven, innovation validated

---

## 🎯 MVP Philosophy

### What MVP Means Here

**NOT:**
- ❌ "Build everything but poorly"
- ❌ "Launch with bugs and fix later"
- ❌ "Minimal features customers will tolerate"

**YES:**
- ✅ **Minimum** = Smallest feature set that proves value
- ✅ **Viable** = Customers will pay for it
- ✅ **Product** = Solves real problem end-to-end

### MVP Success Definition

**You have a viable MVP when:**
1. Customer connects their Stripe account
2. Within 5 minutes, sees $X leakage identified
3. Gets 3-5 actionable recommendations
4. Can export report to share with team
5. Pays $99-$299/month gladly

**If any step takes >5 minutes or feels painful: NOT MVP-READY.**

---

## 🧱 Core User Journey (Lock This)

### Step 1: Onboarding (5 minutes)

**User actions:**
1. Sign up with email
2. Connect Stripe account (OAuth)
3. Select date range (last 3 months default)
4. Click "Analyze Payments"

**System actions:**
1. Fetch all cross-border payouts via Stripe API
2. Identify supported corridors (USD→EUR, USD→INR, USD→GBP)
3. Queue analysis jobs
4. Show "Analyzing... estimated 2 minutes"

**Output:**
- Dashboard with summary stats visible
- "Analysis complete" notification

**Success metric:** 90% complete onboarding without support.

### Step 2: Discovery (First Value Moment)

**User sees:**

**Dashboard Summary Card:**
```
💸 Total Sent (3 months): $485,000
💰 Total Received: $469,150
📉 Total Leakage: $15,850 (3.27%)
🎯 Potential Savings: $6,340/year
```

**Top Leakage Sources:**
1. USD→EUR corridor: $8,200 (FX spread: 1.8%)
2. USD→INR corridor: $4,500 (Intermediary fees: $45/txn)
3. USD→GBP corridor: $3,150 (Weekend timing delays)

**Immediate reaction:**
> "Holy shit, we're losing $16k and had no idea."

**Success metric:** 80% of users say "This found something I didn't know."

### Step 3: Deep Dive (Flow Forensics)

**User clicks on specific transaction:**

**Transaction Detail View:**
```
Transaction: payout_1234xyz
Date: Jan 15, 2026
Sent: $10,000 USD → Received: €9,156 EUR
Expected: €9,280 EUR (mid-market rate)
Variance: €124 EUR ($135 USD)

🔍 Reconstructed Flow:
Stripe → Citi Correspondent Bank → SWIFT Network → Deutsche Bank → Merchant
  ↓          ↓                        ↓               ↓
 $10k    -$25 (0.25%)              -$15           -$40 (FX spread 1.2%)
                                   (SWIFT fee)

💡 What Happened:
• Stripe charged $25 (standard 0.25% platform fee)
• SWIFT network charged $15 (corridor fee)
• Deutsche Bank applied 1.2% FX spread (vs 0.3% mid-market rate)
• Total unnecessary cost: ~$80 (could have saved with alternative route)

🚀 Recommendation:
Use Wise Business for this corridor → Expected savings: $75/transaction
• Wise charges 0.43% all-in (vs your 1.35%)
• Settlement time: 1 day (vs 3 days)
• Annual savings (50 txns): $3,750
```

**User reaction:**
> "Now I understand exactly where money is going. I can present this to my CEO."

**Success metric:** 70% of users click into at least 3 transaction details.

### Step 4: Take Action (Optimization)

**User navigates to "Recommendations" tab:**

**Recommendation #1:**
```
💡 Switch USD→EUR corridor to Wise Business
Potential savings: $3,750/year
Effort: Medium (1-day setup)
Risk: Low (Wise is reputable, regulated)

How to implement:
1. Create Wise Business account (30 min)
2. Verify business (1-2 days)
3. Update payout settings in Stripe
4. Test with small transaction
5. Monitor for 1 month, then scale

[Export Implementation Guide] [Mark as In Progress] [Dismiss]
```

**Recommendation #2:**
```
💡 Batch USD→INR payments weekly instead of daily
Potential savings: $2,100/year
Effort: Low (change payout schedule)
Risk: None (just timing shift)

Why this works:
• You're paying $45/transaction intermediary fee
• You send 5 small INR payouts daily
• Batching reduces from 150 txns/month to 30
• Fee savings: $5,400/year
• Trade-off: Sellers wait 1-7 days longer (survey them)

[Export Batch Schedule] [Mark as Implemented] [Dismiss]
```

**Success metric:** 50% of users export at least 1 recommendation.

### Step 5: Ongoing Monitoring

**User returns monthly:**

**Dashboard shows:**
```
📊 This Month vs Last Month
Leakage: $1,200 → $680 (43% reduction) ✅
Savings captured: $520 (from Wise switch)
New issues detected: 1 (EUR payments now routing differently)

🔔 Alerts:
• New corridor detected: USD→MXN (analyze now?)
• USD→EUR cost increased 15% this week (investigate?)
```

**Success metric:** 60% monthly active users (return at least once/month).

---

## 🎨 MVP Feature List (What's IN)

### 1. User Management (Basic)
- Email/password signup
- Email verification
- Password reset
- Profile settings (name, company)
- **OUT:** SSO, 2FA, team management (later)

### 2. Stripe Integration
- OAuth connection to Stripe
- Read-only access (no writes)
- Fetch payouts, transfers, balance transactions
- Automatic sync (daily)
- **OUT:** Multi-account, webhook real-time sync (later)

### 3. Payment Analysis Engine
- Identify cross-border transactions (corridors)
- Filter supported corridors (USD→EUR, USD→INR, USD→GBP only)
- Calculate expected vs actual amounts
- Attribute fees (platform, FX, intermediary estimates)
- **OUT:** Real-time analysis, predictive models (later)

### 4. Flow Reconstruction (AI Agent)
- LLM-powered intermediary identification
- Use transaction metadata + corridor knowledge
- Estimate fee breakdown
- Explain in plain English
- **OUT:** Multi-model consensus, confidence scores (later)

### 5. Leakage Detection
- Compare actual fees vs expected baseline
- Flag anomalies (>10% variance)
- Categorize by source (FX, intermediary, timing)
- Calculate total leakage over period
- **OUT:** Anomaly prediction, root cause drill-down (later)

### 6. Recommendations Engine
- Rule-based alternative route suggestions
- Show savings estimate, effort, risk
- Provide implementation guides (text)
- Track recommendation status (pending, in progress, implemented, dismissed)
- **OUT:** ML-powered recommendations, automated execution (later)

### 7. Dashboard UI
- Summary metrics (total sent, received, leakage, savings)
- Transaction list (filterable by corridor, date, amount)
- Transaction detail view (flow visualization, cost breakdown)
- Recommendations list
- Monthly reports (exportable PDF)
- **OUT:** Custom dashboards, advanced filters, data exports (later)

### 8. Reporting
- Monthly leakage report (email)
- Savings summary
- Top leakage sources
- Recommendation recap
- **OUT:** Custom reports, scheduled reports, Slack/email alerts (later)

---

## ❌ What's Explicitly OUT (No Scope Creep)

### Infrastructure Features
- ❌ Multi-PSP support (Adyen, Wise, banks) → v1.1
- ❌ Multi-currency wallets → never (not our focus)
- ❌ Payment execution → v1.2 (after proving advisory works)
- ❌ Real-time webhooks → v1.1
- ❌ Mobile app → v2.0

### Analysis Features
- ❌ Predictive analytics (forecast future costs) → v1.3
- ❌ Anomaly alerts (real-time) → v1.2
- ❌ Corridor benchmarking (compare to peers) → v1.3
- ❌ Treasury forecasting → v2.0
- ❌ All corridors (>100) → gradual rollout post-v1

### User Features
- ❌ Team collaboration (shared dashboards) → v1.2
- ❌ Role-based access control → v1.2
- ❌ SSO (SAML, OAuth) → v2.0
- ❌ Custom integrations (API access) → v2.0
- ❌ White-label / reseller → never

### Enterprise Features
- ❌ Audit logs → v2.0
- ❌ Compliance certifications (SOC2, etc) → v2.0
- ❌ SLA guarantees → v2.0
- ❌ Dedicated support → after $50k MRR

**Rule:** If it's not on the IN list, it's OUT. No exceptions during MVP.

---

## 🧪 MVP Validation Criteria

### Before Launch (Internal)

**Technical:**
- [ ] All 3 corridors analyze successfully (USD→EUR, USD→INR, USD→GBP)
- [ ] Fee attribution accuracy >70% (vs known ground truth)
- [ ] Average analysis time <2 minutes per 100 transactions
- [ ] Dashboard loads in <3 seconds
- [ ] Mobile responsive (works on tablet)

**Product:**
- [ ] Onboarding takes <5 minutes (internal testing)
- [ ] Value visible within 5 minutes of connecting Stripe
- [ ] At least 3 recommendations generated for test account
- [ ] Recommendations are actionable (not vague)
- [ ] Leakage calculation matches manual spreadsheet (±5%)

**Business:**
- [ ] Stripe OAuth works reliably
- [ ] No PII stored unnecessarily (GDPR-ready)
- [ ] Terms of Service + Privacy Policy published
- [ ] Pricing page live
- [ ] Payment processing setup (Stripe Checkout)

### After Launch (Beta Users)

**Week 1-2: 10 Beta Users**
- [ ] 8/10 complete onboarding without support
- [ ] 7/10 say "This found leakage I didn't know about"
- [ ] 5/10 export at least 1 recommendation
- [ ] 3/10 say "I would pay for this"
- [ ] 0 critical bugs

**Week 3-4: Paid Conversion**
- [ ] 3/10 beta users convert to paid ($99-$299/month)
- [ ] 2/3 paid users implement at least 1 recommendation
- [ ] 1/3 paid users report measurable savings within 30 days
- [ ] <1 support ticket per user per month
- [ ] Churn = 0 (too early to churn)

**Month 2-3: Product-Market Fit Signals**
- [ ] 10 paying customers
- [ ] $2k-$3k MRR
- [ ] NPS >40
- [ ] 1-2 customer testimonials with $ savings quoted
- [ ] 80% say "I'd be disappointed if this went away"
- [ ] 2-3 referrals from existing customers

**If any criteria fail: Fix before scaling.**

---

## 🏗️ Build Phases (4-Week Plan)

### Week 1: Foundation
**Goal:** Database + Auth + Stripe integration working locally

**Tasks:**
- Set up project structure (backend, frontend, db)
- Docker Compose for local dev
- User schema + auth (JWT)
- Stripe OAuth flow
- Fetch payouts from Stripe API
- Store in PostgreSQL
- Basic API endpoints (health, auth, stripe-connect)

**Success:** Can connect Stripe, fetch payouts, see raw data in database.

### Week 2: Analysis Engine
**Goal:** Agent system analyzes transactions and calculates leakage

**Tasks:**
- Corridor identification (USD→EUR, etc)
- Fee attribution logic (platform, FX, intermediary estimates)
- LangGraph agent setup (flow reconstruction)
- LLM prompts for intermediary identification
- Leakage calculation (expected vs actual)
- Store analysis results in database

**Success:** Input a payout → Get back fee breakdown + leakage amount.

### Week 3: Recommendations + Dashboard
**Goal:** Frontend shows analysis + recommendations

**Tasks:**
- React dashboard setup (Vite + Tailwind)
- Summary metrics component
- Transaction list + detail view
- Flow visualization (simple diagram)
- Recommendations engine (rule-based)
- Recommendations UI
- Monthly report generation (PDF)

**Success:** Full user journey works (onboarding → analysis → recommendations).

### Week 4: Polish + Deploy
**Goal:** Production-ready, deployed, accepting beta users

**Tasks:**
- Error handling + loading states
- Mobile responsive CSS
- Email notifications (analysis complete)
- Landing page (marketing site)
- Terms of Service + Privacy Policy
- Deploy to Railway (backend) + Vercel (frontend)
- Monitoring (Sentry, logs)
- Beta user onboarding flow

**Success:** Beta users can sign up, connect Stripe, see results. No major bugs.

---

## 💰 MVP Pricing Model

### Pricing Tiers (Test with Beta Users)

**Tier 1: Starter**
- **Price:** $99/month
- **Limits:** Up to $250k monthly payment volume
- **Features:**
  - All 3 corridors
  - Monthly analysis
  - Recommendations
  - Email reports
- **Target:** Small e-commerce ($1M-$5M revenue)

**Tier 2: Growth**
- **Price:** $299/month
- **Limits:** Up to $1M monthly payment volume
- **Features:**
  - Everything in Starter
  - Weekly analysis
  - Priority support
  - Quarterly savings review call
- **Target:** Mid-size SaaS/marketplaces ($5M-$20M revenue)

**Tier 3: Scale**
- **Price:** $699/month
- **Limits:** Up to $5M monthly payment volume
- **Features:**
  - Everything in Growth
  - Daily analysis
  - Custom corridors
  - Dedicated Slack channel
- **Target:** Large e-commerce ($20M-$50M revenue)

### Alternative: Performance-Based Pricing

**Model:** 20% of identified savings (monthly cap)

**How it works:**
1. First month free (prove value)
2. Month 2+: We identify $X savings
3. Customer pays 20% of $X (max $999/month)
4. As savings increase, revenue increases

**Pros:**
- Perfect alignment with customer value
- Easy "yes" decision (no risk)
- Upside if we're really good

**Cons:**
- Variable revenue (harder to forecast)
- Requires tracking implementation (did they act on recommendations?)
- Attribution disputes (did savings come from us?)

**Decision:** Test both models with 5 beta users each. Pick winner based on:
- Conversion rate
- Customer satisfaction
- Revenue per customer
- Sales cycle length

---

## 📊 Success Metrics (Lock These)

### North Star Metric
**$ Savings Identified per Customer per Month**

Target: $1,000+ (10x ROI on $99 plan)

### Supporting Metrics

**Acquisition:**
- Signups per week: 5+ (Month 1-2), 20+ (Month 3+)
- Beta → Paid conversion: 30%+
- Landing page → Signup: 5%+

**Activation:**
- Stripe connected: 80%+
- First analysis complete: 90%+
- Leakage visible: 100% (product must deliver)

**Engagement:**
- WAU: 60%+ (weekly active users)
- Recommendations viewed: 70%+
- Recommendations exported: 40%+

**Revenue:**
- MRR growth: 20%+ month-over-month
- ARPU: $150+ (blended average)
- Churn: <5% monthly

**Value:**
- Savings identified: $1,000+ per customer per month
- Savings captured: 30%+ of identified (customers act on recommendations)
- ROI: 10x+ (savings / cost)

---

## 🚨 Risk Mitigation

### Risk 1: Stripe API Limitations

**Risk:** Stripe doesn't expose enough data to reconstruct flows

**Mitigation:**
- Validate during technical feasibility spike (Week -1)
- If insufficient, pivot to Wise API (more transparent)
- Fallback: Use bank statement CSV uploads (manual)

### Risk 2: Customers Don't Act on Recommendations

**Risk:** Insights are interesting but not actionable

**Mitigation:**
- Provide step-by-step implementation guides
- Offer "concierge onboarding" for first 10 customers (do it with them)
- Track implementation rate as key metric
- If <20% implement, add execution capability (v1.1)

### Risk 3: Savings Are Overstated

**Risk:** We claim $10k savings, customer only saves $2k

**Mitigation:**
- Conservative estimates (always round down)
- Show "potential" vs "guaranteed" savings
- Track actual savings post-implementation
- Refund policy if we overstate by >30%

### Risk 4: Competitors Clone Fast

**Risk:** Stripe launches this feature in 6 months

**Mitigation:**
- Build data moat (multi-PSP, more corridors)
- Focus on SMB market (Stripe serves enterprises)
- Add execution capabilities (Stripe won't do this)
- Patent flow reconstruction algorithm

---

## ✅ MVP Scope Locked

**This is the contract.**

If you're tempted to add features during build:
1. Write it down in "v1.1 backlog"
2. Ask: "Will customers pay without this?"
3. If yes: Don't build it
4. If no: You scoped MVP wrong, pivot

**Scope creep kills MVPs. Ship fast, learn, iterate.**

**Next:** `03_architecture.md` → How to build this.
