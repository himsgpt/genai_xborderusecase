# 07 — Cost & Revenue Model

**Reality Check:** Bootstrapped, no external funding, must be profitable from Day 1 of revenue  
**Goal:** Break-even by Month 2, $10k MRR by Month 12

---

## 💰 Startup Costs (One-Time)

### Absolutely Required

| Item | Cost | When | Note |
|------|------|------|------|
| Domain name (.com) | $12 | Week 0 | Via Namecheap/Cloudflare |
| **Total Minimum** | **$12** | | |

### Optional (Recommended but Not Required)

| Item | Cost | When | Note |
|------|------|------|------|
| Terms/Privacy templates | $50 | Week 4 | Termly.io or TermsFeed |
| Logo design | $25 | Week 4 | Fiverr |
| Stock photos | $0 | Week 4 | Unsplash (free) |
| **Total Recommended** | **$87** | | |

**Decision:** Start with $12. Add others only if you get first customer.

---

## 📊 Monthly Operating Costs

### Development Phase (Week 1-5)

**Before any customers:**

| Service | Cost | Note |
|---------|------|------|
| Local development | $0 | Docker on your laptop |
| Ollama (LLM) | $0 | Local inference |
| Git/GitHub | $0 | Public repo |
| **Total** | **$0/month** | |

**You can build entire MVP with zero monthly costs.**

---

### Production Phase (Week 6+)

#### Infrastructure

| Service | Free Tier | Paid (if exceed) | Note |
|---------|-----------|------------------|------|
| **Railway** (backend + PostgreSQL) | - | $5-10/month | Starter plan, includes DB |
| **Vercel** (frontend) | ✓ Unlimited | $0 | Hobby tier |
| **Database backup** | Included | - | Railway handles this |
| **Subtotal Infrastructure** | | **$5-10/month** | |

#### Services

| Service | Free Tier | Paid (if exceed) | Note |
|---------|-----------|------------------|------|
| **OpenAI (GPT-4o-mini)** | - | $0.15 per 1M input tokens | ~$0.0015 per analysis |
| **Resend (email)** | 3,000 emails/month | $20/month for 50k | Free tier covers 100 customers |
| **Sentry (errors)** | 5,000 errors/month | $26/month | Free tier sufficient for MVP |
| **LangSmith (LLM traces)** | 5,000 traces/month | $39/month | Free tier = 5k analyses/month |
| **Subtotal Services** | | **$5-50/month** | Scales with usage |

#### Total Operating Costs by Phase

| Phase | Customers | Analyses/Month | Monthly Cost | Note |
|-------|-----------|----------------|--------------|------|
| **Launch (Week 6-8)** | 0-5 | <1,000 | **$10-15** | Mostly free tiers |
| **Early Growth (Month 2-3)** | 5-10 | 1,000-3,000 | **$15-30** | Still under free limits |
| **Validation (Month 4-6)** | 10-30 | 3,000-10,000 | **$30-100** | May hit some paid tiers |
| **Scale (Month 7-12)** | 30-100 | 10,000-50,000 | **$100-300** | LLM costs dominate |

**Key insight: Costs scale with revenue. You're never at risk of runaway bills.**

---

## 💵 Cost Per Analysis (Unit Economics)

### Breakdown

**Per analysis cost:**
- **LLM (GPT-4o-mini):** $0.0015
  - Flow Reconstruction: ~1,500 input + 500 output tokens = $0.0005
  - Optimization: ~2,000 input + 1,000 output tokens = $0.0009
  - Total: $0.0014 (round to $0.0015)
- **Database write:** $0.0001 (negligible)
- **Compute (Railway):** $0.0002 (amortized)
- **Total:** ~$0.002 per analysis

**For free tier users (Ollama):**
- **LLM:** $0 (local inference)
- **Total:** ~$0.0003 per analysis (just DB + compute)

### Monthly Cost by Customer

**Assumptions:**
- Average customer analyzes 100 transactions/month
- 80% of analyses use cached results (re-analysis not needed)
- Effective: 20 new analyses/month per customer

**Cost per customer per month:**
- 20 analyses × $0.002 = **$0.04/month**

**For 100 customers:**
- 2,000 analyses/month × $0.002 = **$4/month in LLM costs**

**Gross margin:**
- Revenue per customer: $100-300/month
- Cost per customer: $0.04/month
- **Gross margin: 99.97%** (effectively 100%)

**This is a software business with near-zero marginal costs. Beautiful.**

---

## 📈 Revenue Model

### Pricing Tiers (Final, After Validation)

**Tier 1: Starter** — $99/month
- Up to $250k monthly payment volume
- 3 corridors (USD→EUR, USD→INR, USD→GBP)
- Monthly analysis
- Email reports
- **Target customers:** 50-60% of base

**Tier 2: Growth** — $299/month
- Up to $1M monthly payment volume
- All corridors
- Weekly analysis
- Priority support (24h response)
- **Target customers:** 30-35% of base

**Tier 3: Scale** — $699/month
- Up to $5M monthly payment volume
- Daily analysis
- Dedicated Slack channel
- Quarterly review call
- **Target customers:** 10-15% of base

**Average Revenue Per User (ARPU):** $180/month (blended)

---

## 💸 Customer Acquisition Cost (CAC)

### Organic Channels (Free)

**Cost:** $0 cash, but time investment

**Time investment per customer (first 50 customers):**
- Content creation: 2 hours/week = $0
- Community engagement: 30 min/day = $0
- Direct outreach: 10 prospects/customer = 2 hours = $0

**True CAC (time-adjusted):**
- If you value your time at $50/hour: ~$100 per customer
- But in cash: **$0**

**As you scale (>50 customers):**
- Inbound increases (content compounds)
- Referrals kick in (20% of customers refer 1 person)
- CAC drops to $0-50 per customer

---

## 🎯 Lifetime Value (LTV)

### Assumptions

**Retention:**
- Month 1-3 churn: 10% (high, product still improving)
- Month 4-6 churn: 5% (stabilizing)
- Month 7+ churn: 3% (sticky, product-market fit)

**Average customer lifespan:** 24 months (conservative)

**LTV calculation:**
- ARPU: $180/month
- Lifespan: 24 months
- **LTV: $4,320**

**LTV:CAC ratio:**
- $4,320 LTV / $0 CAC = **Infinite** (in practice, 40:1+ if you value time)

**Payback period:** 0 months (customers are profitable from Day 1)

**This is a dream business model.**

---

## 📊 Revenue Projections (Conservative)

### Month-by-Month Breakdown

| Month | New Customers | Total Customers | Churn | Net Customers | ARPU | MRR | Growth |
|-------|---------------|-----------------|-------|---------------|------|-----|--------|
| 1 | 3 | 3 | 0 | 3 | $120 | $360 | - |
| 2 | 5 | 8 | 0 | 8 | $150 | $1,200 | 233% |
| 3 | 7 | 15 | 1 | 14 | $160 | $2,240 | 87% |
| 4 | 10 | 24 | 1 | 23 | $170 | $3,910 | 75% |
| 5 | 12 | 35 | 2 | 33 | $175 | $5,775 | 48% |
| 6 | 15 | 48 | 2 | 46 | $180 | $8,280 | 43% |
| 7 | 18 | 64 | 2 | 62 | $185 | $11,470 | 39% |
| 8 | 20 | 82 | 3 | 79 | $190 | $15,010 | 31% |
| 9 | 22 | 101 | 3 | 98 | $195 | $19,110 | 27% |
| 10 | 25 | 123 | 4 | 119 | $200 | $23,800 | 25% |
| 11 | 27 | 146 | 5 | 141 | $205 | $28,905 | 21% |
| 12 | 30 | 171 | 5 | 166 | $210 | $34,860 | 21% |

### Assumptions Behind Projections

**Customer Acquisition:**
- Month 1-3: Manual outreach, beta conversion (slow)
- Month 4-6: Content starts working, inbound increases
- Month 7-9: Referrals kick in, word-of-mouth
- Month 10-12: Repeatable channels, predictable growth

**ARPU Growth:**
- Month 1-3: Heavy discounts for early customers (50% off)
- Month 4-6: Discounts reduce, customers upgrade tiers
- Month 7-12: New customers pay full price, upsells to higher tiers

**Churn:**
- Starts high (10%) as you figure out product-market fit
- Drops to 3-5% once you nail onboarding and value delivery
- Below 3% is world-class for SMB SaaS

---

## 💰 Profitability Analysis

### Revenue vs Costs (Month 12)

**Revenue:**
- MRR: $34,860
- Annualized: $418,320

**Costs:**
- Infrastructure: $50/month
- LLM (166 customers × 20 analyses × $0.002): $66/month
- Email: $20/month (over free tier)
- Tools/SaaS: $50/month (monitoring, productivity)
- **Total Operating Costs: $186/month**

**Gross Profit:**
- $34,860 - $186 = **$34,674/month**
- **Gross margin: 99.5%**

**Net Profit (after paying yourself):**
- Assume you pay yourself $5,000/month (modest salary)
- $34,674 - $5,000 = **$29,674/month**
- **Net margin: 85%**

**Annual Net Profit (Year 1):**
- ~$300k+ (ramp from $0 to $29k/month)

**This is why software businesses are incredible.**

---

## 🚀 Break-Even Analysis

### When Do You Break Even?

**Monthly operating costs:** $10-30 (before paying yourself)

**Revenue needed to cover costs:** $30/month

**Break-even:** 1 customer at $99/month = **Month 1, Week 7**

**When can you pay yourself?**
- Need: $5,000 MRR to pay yourself $5k/month (no savings yet)
- Timeline: **Month 5-6** (33 customers)

**When are you comfortable?**
- Need: $10,000 MRR (pay yourself $8k, save $2k)
- Timeline: **Month 7** (62 customers)

---

## 📉 Downside Scenario (What If It Goes Poorly?)

### Pessimistic Case

**Assumptions:**
- Acquisition is 50% slower than projected
- Churn is 2x higher (10% steady state)
- ARPU is 20% lower ($140 average)

**Month 12 Results:**
- Customers: 80 (vs 166 in base case)
- ARPU: $140 (vs $210)
- MRR: $11,200 (vs $34,860)
- Costs: $100/month
- Net profit (after $5k salary): **$6,100/month**

**Still profitable. Still a business.**

**Worst case: You're making $70k+ per year as a solo founder within 12 months.**

---

## 📈 Upside Scenario (What If It Goes Well?)

### Optimistic Case

**Assumptions:**
- Content goes viral (1-2 posts hit front page of HN/Reddit)
- Word-of-mouth is strong (30% referral rate)
- You nail product-market fit by Month 6
- Enterprise customers start signing up ($1,500-$3,000/month)

**Month 12 Results:**
- Customers: 250
- ARPU: $280 (more enterprise mix)
- MRR: $70,000
- Costs: $300/month
- Net profit (after $10k salary): **$59,700/month**

**Annual net profit: $500k+**

**At this point, you hire 2-3 people and scale to $1M ARR in Year 2.**

---

## 🎯 Financial Decision Framework

### When to Spend Money

**DO NOT spend on:**
- ❌ Paid ads (until you have $50k+ MRR and proven CAC)
- ❌ Fancy tools (use free tiers aggressively)
- ❌ Office space (work from home)
- ❌ Conferences (unless speaking for free)
- ❌ Certifications (SOC2, etc) until customers demand it

**DO spend on:**
- ✅ Domain name ($12 — required)
- ✅ Legal templates ($50 — protects you)
- ✅ Infrastructure ($10-30/month — required to run)
- ✅ Coffee with customers ($20 — invaluable insights)

### When to Hire

**First hire: Customer Success (at $5k MRR)**
- Part-time contractor (10-20 hours/week)
- $20-30/hour = $800-2,400/month
- Handles: Onboarding, support, success calls
- **You focus on:** Product, content, growth

**Second hire: Developer (at $15k MRR)**
- Full-time contractor or junior dev
- $4k-6k/month
- Handles: Feature development, bug fixes
- **You focus on:** Strategy, sales, hiring

**Third hire: Content/Marketing (at $30k MRR)**
- Full-time contractor
- $3k-5k/month
- Handles: Blog posts, SEO, social media
- **You focus on:** Product vision, key partnerships

**Don't hire before these milestones. Solo is faster and leaner.**

---

## 💎 Key Financial Takeaways

### Why This Business Model Works

1. **Near-zero marginal costs** — Each new customer costs $0.04/month to serve
2. **Zero CAC** — Organic growth via content + community
3. **High ARPU** — $180/month average, some pay $699
4. **Sticky product** — Once customers see savings, they don't churn
5. **Fast payback** — Customers profitable from Day 1
6. **Scalable** — Can grow to 1,000 customers without adding infrastructure

### Risks to Watch

1. **LLM costs spike** — If OpenAI raises prices 10x (unlikely), your margin drops from 99% to 90% (still great)
2. **Stripe changes API** — If Stripe restricts data access (possible), pivot to Wise/other PSPs
3. **Competitor with more capital** — If Stripe/Wise builds this feature (possible in 12-18 months), you'll have a head start and loyal customers
4. **Customer concentration** — If top 10 customers = 50% revenue and they churn, you're in trouble (diversify)

**Mitigation:** Build data moat (more PSPs, more corridors, proprietary insights), focus on SMB market (big players ignore), move fast.

---

## ✅ Financial Health Checklist

### Monthly Review (Track These)

- [ ] MRR growth rate: 20%+ month-over-month (first 6 months)
- [ ] Churn rate: <5% monthly (target <3% by Month 6)
- [ ] ARPU: Increasing over time (upsells working)
- [ ] CAC: Still $0 or low (organic channels working)
- [ ] Gross margin: >95% (costs under control)
- [ ] Runway: 6+ months (if not profitable yet)

### Red Flags (Action Needed)

- 🚨 MRR growth <10% for 2 months straight → GTM broken, fix acquisition
- 🚨 Churn >10% sustained → Product not sticky, talk to churned users
- 🚨 ARPU declining → Downmarket death spiral, focus on higher-value customers
- 🚨 Costs >30% of revenue → Efficiency issue, optimize infrastructure

---

**Next:** `08_risk_mitigation.md` → What could go wrong and how to prevent it
