# 08 — Risk Mitigation & Contingency Planning

**Reality:** 90% of startups fail. You need to think like a pessimist, plan like an optimist.  
**Goal:** Identify every way this could fail, and have a plan B for each.

---

## 🎯 Risk Framework

### Risk Categories

1. **Market Risk** — No one wants this
2. **Technical Risk** — Can't build it or it doesn't work
3. **Competitive Risk** — Someone else does it better/cheaper
4. **Execution Risk** — You run out of time/money/motivation
5. **External Risk** — Things outside your control (regulations, API changes)

**For each risk:**
- **Probability:** Low / Medium / High
- **Impact:** Low / Medium / High / Fatal
- **Mitigation:** What you do to prevent it
- **Contingency:** What you do if it happens anyway

---

## 🚨 Critical Risks (Could Kill the Business)

### Risk 1: No One Wants This (Market Risk)

**Probability:** Medium (30%)  
**Impact:** Fatal

**Symptoms:**
- <20% trial → paid conversion after 3 months
- Customer feedback: "Interesting but not urgent"
- Most churned users say "didn't use it enough to justify cost"

**Why This Happens:**
- Problem isn't painful enough (leakage is <$100/month for most)
- Recommendations aren't actionable (customers can't implement)
- Value is one-time (they get insights once, then churn)

**Mitigation (Before Launch):**
- ✅ Interview 20+ customers, get 10+ to say "I'd pay for this"
- ✅ Manual proof-of-concept (show savings before building product)
- ✅ Lock willingness-to-pay at >$99/month (not $10/month)

**Contingency (If It Happens):**
1. **Week 8-10:** If 0 paying customers, STOP. Conduct 10 exit interviews.
2. **Pivot options:**
   - **Pivot A:** Different customer segment (enterprises vs SMBs?)
   - **Pivot B:** Different value prop (execution vs advisory?)
   - **Pivot C:** Different problem (treasury forecasting vs cost optimization?)
3. **Test new hypothesis in 2 weeks.** If still no traction → shut down, move to next idea.

**Decision Rule:** If <3 paid customers by Week 10 despite 100+ signups → fundamental market problem, not execution.

---

### Risk 2: Can't Reconstruct Payment Flows (Technical Risk)

**Probability:** Medium (25%)  
**Impact:** High (product is useless without this)

**Symptoms:**
- Agent confidence scores <50%
- Flow reconstructions wildly inaccurate
- Customers say "this doesn't match what actually happened"

**Why This Happens:**
- Stripe API doesn't expose enough data
- Too many variables (routes change dynamically)
- LLM hallucinates intermediaries

**Mitigation (Before Building):**
- ✅ Technical feasibility spike (Week -1) proves you can do this
- ✅ Test on 50+ real payouts, validate accuracy >70%
- ✅ Build confidence calibration (don't show results if <70% confidence)

**Contingency (If Accuracy Is Low):**
1. **Option A: Simplify scope**
   - Only support corridors where you CAN reconstruct (e.g., USD→EUR via SEPA)
   - Drop corridors with too many variables (USD→INR)
2. **Option B: Partner with PSPs**
   - Get official data from Wise, Revolut (more transparent than Stripe)
   - Position as "Official Wise Optimization Tool"
3. **Option C: Move to advisory model**
   - Don't try to reconstruct flows (too hard)
   - Focus on benchmarking: "You paid $X, typical is $Y, here's why"

**Decision Rule:** If accuracy <60% after 2 weeks of tuning → pivot to Option B or C.

---

### Risk 3: Stripe Adds This Feature (Competitive Risk)

**Probability:** Medium (40% within 18 months)  
**Impact:** High (kills growth, not existing customers)

**Why This Happens:**
- Stripe sees you getting traction
- They have data advantage (see all flows)
- They add "Payment Cost Insights" to dashboard (free for users)

**Mitigation (Build Moat Now):**
- ✅ **Multi-PSP support** (Wise, Payoneer, banks) — Stripe can't do this
- ✅ **Proprietary data** — Build routing database from customer data (Stripe doesn't have cross-PSP view)
- ✅ **Execution capability** — Auto-route payments (Stripe won't do this, conflicts with their revenue)
- ✅ **SMB focus** — Stripe serves enterprises, you serve indie hackers (different go-to-market)

**Contingency (If Stripe Launches):**
1. **Immediate response (Week 1):**
   - Blog post: "Why Stripe's Cost Insights Still Leaves Money on the Table"
   - Show what they DON'T do (cross-PSP optimization, execution, SMB support)
2. **Differentiate (Month 1-3):**
   - Launch multi-PSP support (now a requirement, not nice-to-have)
   - Add execution (auto-route to cheapest provider)
   - Focus on "Stripe Tax for payment costs" positioning (complementary, not competitive)
3. **Worst case:**
   - If customers churn to Stripe's free feature → you've validated the market
   - Pivot to enterprise treasury analytics (Stripe doesn't serve)
   - Or partner with Stripe (become official optimization layer)

**Decision Rule:** If Stripe launches and you lose >20% of customers in 3 months → pivot to multi-PSP or enterprise.

---

### Risk 4: Can't Get to 10 Customers in 3 Months (Execution Risk)

**Probability:** Medium (35%)  
**Impact:** High (invalidates business model, demoralizes founder)

**Why This Happens:**
- GTM strategy doesn't work (wrong channels)
- Product is too complex (onboarding sucks)
- Market is smaller than expected (not enough $5M-$50M e-commerce companies)

**Mitigation (Validate GTM Early):**
- ✅ Get 3 paid customers by Week 8 (proves willingness to pay)
- ✅ If 0 by Week 8 → STOP, don't keep building
- ✅ Track leading indicators (signups/week, trial → paid %, engagement)

**Contingency (If Growth Stalls):**

**Scenario A: Good Signups, Poor Conversion**
- Problem: Product or pricing
- Fix: Talk to 10 non-converters, find objection pattern
- Test: Lower price, add guarantee, improve onboarding

**Scenario B: No Signups, Good Conversion**
- Problem: GTM channels not working
- Fix: Try 3 new channels (paid ads, partnerships, outbound sales)
- Test: 2 weeks per channel, measure CAC

**Scenario C: No Signups, No Conversion**
- Problem: Fundamental market issue
- Fix: Pivot or shut down

**Decision Rule:** 
- Week 8: If <3 paid customers → intensive diagnosis (2 weeks)
- Week 10: If still <5 customers → pivot or shut down

---

## ⚠️ High-Impact Risks (Painful but Survivable)

### Risk 5: High Churn (Product Risk)

**Probability:** High (50% — most SaaS has churn issues early)  
**Impact:** Medium (slows growth, but fixable)

**Symptoms:**
- >10% monthly churn
- Customers cancel after 1-2 months
- Exit reason: "Didn't use it enough"

**Why This Happens:**
- Value is one-time (get insights, implement, done)
- No ongoing engagement (monthly analysis isn't frequent enough)
- No workflow integration (they forget to check)

**Mitigation:**
- ✅ Build ongoing value:
  - Real-time alerts ("USD→EUR cost spiked 20% this week")
  - New leakage detection (monthly scan for new issues)
  - Corridor benchmarking ("You're in top 10% for cost efficiency")
- ✅ Increase engagement:
  - Weekly email digest ("This week: $X leakage detected")
  - Slack integration (alerts go where they work)
  - Gamification ("You've saved $10k YTD 🎉")

**Contingency (If Churn Stays High):**
1. **Month 3-4:** Exit interviews with every churned customer
2. **Identify pattern** (price, value, usage, competition?)
3. **Ship fix within 2 weeks** (e.g., real-time alerts if "not enough ongoing value")
4. **Re-engage churned customers** ("We fixed [issue], come back for 50% off")

**Decision Rule:** If churn >10% after 6 months → product-market fit not there, major pivot needed.

---

### Risk 6: Acquisition Cost Explodes (GTM Risk)

**Probability:** Low (20%)  
**Impact:** Medium (slows growth, but pivot-able)

**Why This Happens:**
- Organic channels saturate (content stops working)
- Referrals slow (customers aren't referring)
- Need paid ads but don't know how

**Mitigation:**
- ✅ Build multiple channels early (not just content)
- ✅ Referral program (incentivize word-of-mouth)
- ✅ Community presence (Indie Hackers, Reddit) as flywheel

**Contingency:**
1. **Try paid ads (carefully)**
   - Budget: $500/month test
   - Channel: LinkedIn Ads (CFO targeting)
   - Metric: CAC <$300 (LTV $4,320 = 14:1 ratio, acceptable)
   - Decision: If CAC >$500 after $1,500 spend → ads don't work, stop
2. **Partner with complementary tools**
   - Integrate with accounting software (QuickBooks, Xero)
   - Co-marketing with Stripe, Wise (hard but high upside)
   - Affiliate program (accountants refer clients, get 20% commission)
3. **Outbound sales**
   - Hire SDR at $30k/year + commission
   - Cold email 100 prospects/week
   - Target: 2-3 customers/month = $600 MRR = $7.2k/year (ROI positive)

**Decision Rule:** If CAC >$500 and no pivot working → focus on retention (keep existing customers happy, grow slowly).

---

### Risk 7: Key Infrastructure Failure (Technical Risk)

**Probability:** Low (15%)  
**Impact:** Medium (lose customers if downtime >24 hours)

**Scenarios:**
- **Railway goes down** (unlikely but possible)
- **Stripe API rate limits** (if you abuse it)
- **OpenAI bans account** (if you violate ToS)
- **Database corruption** (if no backups)

**Mitigation:**
- ✅ Automated backups (Railway does daily, verify restore works)
- ✅ API rate limiting (don't exceed Stripe limits)
- ✅ OpenAI compliance (follow usage policies)
- ✅ Monitoring (Sentry, UptimeRobot) to detect issues fast

**Contingency:**
1. **Railway failure:**
   - Migrate to Render or Fly.io (1 day, have script ready)
   - Keep Docker images pushed to Docker Hub (backup)
2. **Stripe API rate limit:**
   - Implement exponential backoff
   - Batch requests (fetch 100 payouts at once, not 1 at a time)
3. **OpenAI ban:**
   - Switch to Anthropic Claude (LangChain makes this easy)
   - Or Azure OpenAI (enterprise, more stable)
4. **Database corruption:**
   - Restore from backup (test restore monthly)
   - If backup failed: Manual data re-ingestion from Stripe

**Decision Rule:** Have disaster recovery playbook documented (1 page), test once per quarter.

---

## 🌍 External Risks (Low Probability, High Impact)

### Risk 8: Regulatory Change (Compliance Risk)

**Probability:** Low (10%)  
**Impact:** High (could require months of work)

**Scenarios:**
- **GDPR enforcement** — EU requires explicit consent for payment data processing
- **PCI DSS** — Card data regulations change (unlikely to affect you, you don't touch cards)
- **Financial licensing** — Regulators decide payment analytics requires money transmitter license (very unlikely)

**Mitigation:**
- ✅ GDPR compliance from Day 1 (privacy policy, data deletion, minimal PII)
- ✅ Don't store sensitive data (no card numbers, no bank account details, just Stripe IDs)
- ✅ Consult lawyer at $10k MRR (one-time, $500-1000 for review)

**Contingency:**
- If GDPR violation: Fix within 30 days (add consent flows, update policy)
- If licensing required: Partner with licensed entity or pivot to non-regulated advisory

**Decision Rule:** Monitor regulatory changes quarterly. If major change, address within 60 days or pivot.

---

### Risk 9: Economic Recession (Market Risk)

**Probability:** Medium (30% in next 2 years)  
**Impact:** Medium (customers cut budgets, but your product saves money)

**Why This Could Help You:**
- Recessions → companies focus on cost-cutting
- Your product literally saves money → more valuable in downturn
- "CFO tools" are recession-resistant

**But Could Hurt:**
- SMBs go out of business (lose customers)
- Payment volumes drop (less leakage to find)
- Customers delay "nice-to-have" tools

**Mitigation:**
- ✅ Position as "recession-proof investment" (saves 10x cost)
- ✅ Offer performance pricing (pay only if we save you money)
- ✅ Target profitable companies (not VC-backed burning cash)

**Contingency:**
- If recession hits: Double down on ROI messaging ("Every dollar counts now")
- Launch "CFO Dashboard" (broader cost analytics, not just payments)
- Target enterprise (better budgets in downturn)

---

## 🎯 Risk Monitoring Dashboard

### Weekly Review (Every Friday)

**Market Health:**
- [ ] Signups this week: ___
- [ ] Trial → Paid conversion: ___%
- [ ] Churn this week: ___%
- [ ] NPS score (if >10 customers): ___

**Technical Health:**
- [ ] Uptime this week: ___%
- [ ] Agent accuracy (sample 10 analyses): ___%
- [ ] Sentry errors: ___
- [ ] LangSmith cost per analysis: $___

**Competitive Intel:**
- [ ] New competitors discovered: ___
- [ ] Stripe product updates: (check changelog)
- [ ] Customer feedback mentioning competitors: ___

**Financial Health:**
- [ ] MRR: $___
- [ ] Monthly burn: $___
- [ ] Months of runway (if pre-revenue): ___

**Red flags (immediate action if any are true):**
- 🚨 0 signups for 2 weeks straight
- 🚨 3+ customer churns in 1 week
- 🚨 Downtime >4 hours
- 🚨 Competitor launches similar product

---

## 🛡️ Founder Risk (Most Overlooked)

### Risk 10: Burnout (Execution Risk)

**Probability:** High (60% of solo founders burn out within 6 months)  
**Impact:** Fatal (if you quit, business dies)

**Why This Happens:**
- Working 80-hour weeks unsustainably
- No progress for weeks (demoralizing)
- Isolation (no co-founder, no team)
- Financial stress (no revenue, savings draining)

**Mitigation:**
- ✅ Set boundaries (no work Sundays, 8-hour sleep minimum)
- ✅ Track wins (celebrate every signup, every customer)
- ✅ Community (join founder groups, don't work alone)
- ✅ Revenue milestones (break-even = psychological relief)

**Contingency:**
- **If you feel burned out (Week 8-10 especially):**
  1. Take 3-day break (seriously, no laptop)
  2. Reassess: Do you still believe in this?
  3. If yes: Simplify scope, cut features, ship faster
  4. If no: Shut down gracefully, move to next idea
- **Find accountability partner** (another founder, weekly check-ins)
- **Therapy/coaching** (if you can afford it, worth it)

**Decision Rule:** If you dread opening your laptop 3 days in a row → something is wrong, pause and diagnose.

---

## ✅ Risk Mitigation Checklist

### Before Launch (Week 0-5)

- [ ] Validated willingness to pay (10+ confirmed "yes")
- [ ] Technical feasibility proven (70%+ accuracy)
- [ ] Disaster recovery plan documented
- [ ] Privacy policy + Terms of Service published
- [ ] Monitoring set up (Sentry, UptimeRobot)

### After Launch (Week 6-12)

- [ ] Customer exit interviews (every churned user)
- [ ] Weekly risk dashboard review
- [ ] Monthly competitor analysis
- [ ] Quarterly regulatory check
- [ ] Backup restore tested

### Continuous (Ongoing)

- [ ] Talk to customers weekly (don't build in isolation)
- [ ] Track leading indicators (not just MRR)
- [ ] Keep expenses <30% of revenue
- [ ] Have 6+ months runway always
- [ ] Take care of yourself (burnout kills more startups than competition)

---

## 🎯 Final Word on Risk

**Every startup is risky.** Yours is less risky than most because:
- ✅ Low startup costs ($12)
- ✅ Near-zero marginal costs (software)
- ✅ Fast validation (8 weeks to first revenue)
- ✅ Pivot-able (payment analytics → treasury → procurement)

**But risk is still real.** Most startups fail not because the idea was bad, but because:
- Founders ran out of money
- Founders ran out of energy
- Founders didn't adapt fast enough

**Your advantage:** You're paranoid. You're planning for failure. That's why you'll succeed.

---

**Next:** `09_README.md` → Guide to all planning documents
