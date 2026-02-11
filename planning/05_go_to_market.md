# 05 — Go-to-Market Strategy (No-Budget Customer Acquisition)

**Prerequisites:** MVP scope locked, value prop validated  
**Reality Check:** You have $0 marketing budget, no network, no warm intros

---

## 🎯 GTM Philosophy (Bootstrapped Reality)

### What Doesn't Work for Solo Founders

❌ **Paid ads** — Burn money fast, need optimization expertise  
❌ **Cold outbound at scale** — Need SDR, CRM, follow-up systems  
❌ **Enterprise sales** — 6-12 month cycles, need sales team  
❌ **"Build and they will come"** — No one finds you organically  
❌ **Conference sponsorships** — $5k-$50k, ROI unclear

### What Works (Proven for Bootstrap)

✅ **Hyper-targeted direct outreach** — 1-on-1, personal, value-first  
✅ **Public building + content** — Build credibility, attract inbound  
✅ **Community participation** — Be useful where customers already gather  
✅ **Freemium funnel** — Free tool → Paid upgrade  
✅ **Referral loops** — First 10 customers bring next 20

**Constraint = Creativity.** Use it.

---

## 🎯 Target Customer Profile (Lock This)

### Primary ICP (Ideal Customer Profile)

**Company:**
- E-commerce or SaaS with international customers/sellers
- $5M-$50M annual revenue
- $100k-$1M monthly cross-border payment volume
- 10-100 employees

**Decision Maker:**
- Title: CFO, Finance Lead, Controller, Operations Lead
- Pain: Spending 10+ hours/month on payment reconciliation
- Authority: Can approve <$500/month tools without board approval
- Budget: Has money for tools that save money

**Current Setup:**
- Using Stripe (or similar PSP) for payouts
- No treasury management system (too expensive)
- Reconciling in spreadsheets (Google Sheets, Excel)
- Aware of leakage but doesn't know how to fix it

**Psychographic:**
- Frustrated with lack of visibility
- Open to new tools if ROI is clear
- Willing to test (not risk-averse)
- Wants to look smart to CEO ("I saved $50k this year")

### Secondary ICP (Lower Priority)

- Marketplaces (Etsy-like, Upwork-like)
- Payment companies (fintech startups)
- SMB exporters (physical goods)

**Why lower priority:**
- Different payment patterns
- May need custom integrations
- Longer sales cycles

---

## 📅 GTM Timeline (12 Weeks to 10 Customers)

### Week 1-2: Pre-Launch Validation

**Goal:** Confirm ICP, build waitlist

**Activities:**
1. **LinkedIn research** (10 hours)
   - Find 100 companies matching ICP
   - Identify decision makers (CFO, Finance Lead)
   - Note their pain points from posts/comments

2. **Direct outreach** (50 DMs/emails)
   - Personalized message (not spam)
   - Offer: "I'll analyze your Stripe payouts for free and show you hidden costs (no tool yet, manual analysis)"
   - Goal: 10 responses, 5 calls

3. **Customer discovery calls** (5-10 calls)
   - Ask: What's your current cross-border payment volume?
   - Ask: How much time do you spend reconciling?
   - Ask: Have you discovered unexpected fees?
   - Ask: Would you pay $99-$299/month if I could save you $1k+/month?
   - **Goal: Validate willingness to pay, collect 20 emails for beta**

**Success Criteria:**
- 20 beta waitlist signups
- 3+ say "yes I'd pay if you prove savings"
- Refined ICP based on feedback

### Week 3-4: MVP Build

(Building, no GTM activities. See architecture docs.)

### Week 5: Soft Launch (Beta Testing)

**Goal:** 5 beta users actively using product

**Activities:**
1. **Email waitlist** (20 people)
   - "Beta is live. First 10 users get lifetime 50% discount."
   - Urgency: Close beta in 7 days

2. **Personal onboarding** (1 hour per user)
   - Zoom call to walk through setup
   - Help connect Stripe
   - Explain first analysis results
   - Get feedback live

3. **Daily check-ins** (10 min per user)
   - DM: "How's it going? Any issues?"
   - Fix bugs immediately
   - Ask for screenshots of results

**Success Criteria:**
- 5 users connected Stripe
- 5 analyses completed successfully
- 3+ users say "This is useful"
- 0 major bugs

### Week 6: Public Launch

**Goal:** 50 signups, 3 paying customers

**Activities:**

**1. Indie Hackers Launch Post**

**Title:** "I built an AI tool that found $15k in hidden fees in my Stripe payouts"

**Post structure:**
```markdown
## The Problem
I'm a SaaS founder. Last month I sent $485k in international payouts via Stripe.
I received $469k. $16k disappeared.

I had no idea where the money went. Stripe dashboard just shows "total fees."

## What I Built
An AI agent system that:
- Reconstructs your payment route (which banks, intermediaries touched your money)
- Breaks down fees (platform, FX spread, intermediary fees)
- Recommends cheaper routes

I used it on 3 months of my own payments. Found $15,850 in leakage.
Switched to Wise for EUR payouts → now saving $500/month.

## How It Works
1. Connect your Stripe account (OAuth, read-only)
2. AI analyzes your cross-border payouts
3. See exactly where money goes
4. Get recommendations to save 20-40%

## Lessons from Building
- Used LangGraph for agent orchestration
- GPT-4o-mini costs $0.0015 per analysis (stupid cheap)
- Hardest part: reverse-engineering routes from limited data
- Built in 4 weeks solo

## Try It
Free for first 30 days: [link]

Looking for feedback from anyone doing >$100k/month cross-border.

## Ask Me Anything
Happy to answer questions about the build or cross-border payment optimization.
```

**Expected results:**
- 500-1,000 views
- 30-50 signups
- 5-10 comments with feedback

**2. Reddit Posts (3 subreddits)**

**r/ecommerce:**
"I analyzed 500 Stripe payouts and found the average e-commerce store is leaking 2.3% to hidden fees. Here's the breakdown."

**r/SaaS:**
"Built an AI tool to audit cross-border payment costs. Saved myself $6k/year. Free analysis if you want to try."

**r/Entrepreneur:**
"PSA: If you're sending international payments via Stripe, you're probably overpaying 20-40%. Here's how to check."

**Strategy:**
- Lead with value (teach, don't pitch)
- Offer free analysis in comments
- Link to landing page in bio
- Engage with every comment

**Expected results per post:**
- 100-500 upvotes (if hits front page)
- 10-20 signups each
- Some negative feedback (ignore trolls)

**3. Twitter/X Thread**

**Hook:** "I sent $485k internationally last quarter. Only $469k arrived. Here's where $16k went (and how I stopped the leakage) 🧵"

**Thread structure (10 tweets):**
1. Hook + problem
2. Why cross-border payments are opaque
3. Visual breakdown of my payment flow
4. Hidden fee #1: FX spread
5. Hidden fee #2: Intermediary banks
6. Hidden fee #3: Timing costs
7. What I did to fix it (switched routes)
8. Result: $500/month saved
9. I built a tool to automate this analysis
10. CTA: Free for 30 days if you're also bleeding money on payments

**Expected results:**
- 50-100 signups (if picks up engagement)
- 1-2 retweets from fintech influencers (if lucky)

**4. Product Hunt Launch (Optional)**

**Only if you have time.** PH is hit-or-miss for B2B SaaS.

**If you do it:**
- Launch on Tuesday or Wednesday
- Have 5 friends upvote immediately
- Respond to every comment within 1 hour
- Goal: Top 10 for the day

**Realistic expectation:**
- 50-100 upvotes
- 30-50 signups
- Brief traffic spike, then drops

### Week 7-8: Convert Beta to Paid

**Goal:** 3 paying customers ($297-$897 MRR)

**Activities:**

**1. Beta users conversion**
- Email: "Your 30 days are ending. You've saved $X based on our recommendations. Continue for $99/month?"
- Offer: 50% lifetime discount if they pay now
- Follow-up call: "What would make this a no-brainer yes?"

**Target: 3/5 beta users convert = 60% conversion rate**

**2. Free trial optimization**
- Add "Estimated annual savings: $X,XXX" to dashboard (make ROI obvious)
- Email Day 7: "You've identified $X in leakage so far. Implement one recommendation to test."
- Email Day 21: "Final week of trial. Here's your total savings potential: $X,XXX/year"

**Target: 10% trial → paid conversion = 3 paid from 30 trials**

### Week 9-12: Scale to 10 Customers

**Goal:** 10 paying customers ($1k-$3k MRR)

**Activities:**

**1. Content Marketing (2 articles/week)**

**Article ideas:**
- "The hidden costs of cross-border e-commerce payments (and how to eliminate them)"
- "I compared Stripe vs Wise vs Payoneer for international payouts. Here's the real cost."
- "Case study: How [Customer X] saved $1,200/month on payment fees"
- "The payment route optimization playbook for SaaS companies"

**Publish on:**
- Your blog (with SEO)
- Medium (tag: payments, fintech, entrepreneurship)
- LinkedIn (long-form post)

**Expected results per article:**
- 200-500 reads
- 2-5 signups
- Builds authority over time

**2. Community Building**

**Where to be:**
- Indie Hackers (respond to payment questions, plug your tool naturally)
- Reddit r/ecommerce, r/SaaS (weekly participation)
- Twitter fintech community (engage with CFOs, finance people)

**How:**
- Answer questions with genuine value
- Share insights from your data (aggregate, anonymized)
- Don't spam, link only when relevant

**Time investment:** 30 min/day

**Expected results:**
- 1-2 signups/week from being helpful
- Brand awareness builds

**3. Referral Program**

**Incentive:**
- Give $50 credit for each referral that converts to paid
- Referrer gets 1 month free for every 2 referrals

**How to launch:**
- Add "Refer & Earn" section to dashboard
- Email existing customers with unique referral link
- Track via UTM params

**Expected results:**
- 20% of customers refer someone (2/10)
- 50% of referrals convert (1 new customer)

**4. Case Studies (Social Proof)**

**Goal:** 3 customer case studies with $ savings

**Format:**
- Company name (with permission)
- Problem: "We were losing $X/month to hidden fees"
- Solution: "Used [Your Tool] to identify and fix leakage"
- Result: "$Y saved in 3 months"
- Quote from CFO

**Use case studies in:**
- Landing page (testimonials section)
- Sales emails
- Social proof in outreach

---

## 💬 Messaging & Positioning

### One-Liner (Elevator Pitch)

**"We help e-commerce and SaaS companies save $10k-$100k/year on cross-border payments by exposing hidden fees and prescribing cheaper routes."**

### Value Proposition (Landing Page Hero)

**Headline:** "Stop Leaking Money on International Payments"

**Subheadline:** "AI-powered payment analysis that finds hidden fees, explains where your money goes, and recommends routes that save 20-40%."

**CTA:** "Analyze Your Payments Free"

### Problem-Solution Framing

**Problem (Resonate):**
> "You send $100k internationally. $96.5k arrives. Where did $3.5k go? Your PSP won't tell you. Your bank won't tell you. You write it off as 'payment fees.'"

**Solution (Position):**
> "We reverse-engineer your payment flows using AI, break down costs to the dollar, and tell you exactly how to pay less next time."

### Competitive Positioning

**You are NOT:**
- A payment processor (not competing with Stripe)
- An FX platform (not competing with Wise)
- A treasury system (not competing with Kyriba)

**You ARE:**
- Payment operations intelligence for SMBs
- The "Datadog for payment costs"
- An invisible CFO agent watching every transaction

**Tagline:** "Stripe for payment cost optimization"

---

## 📈 Pricing & Packaging (Test With Market)

### Proposed Pricing (Validate in Beta)

**Tier 1: Starter** — $99/month
- Up to $250k monthly volume
- 3 corridors (USD→EUR, USD→INR, USD→GBP)
- Monthly analysis
- Email reports
- **Target:** Small e-commerce ($1M-$5M revenue)

**Tier 2: Growth** — $299/month
- Up to $1M monthly volume
- All corridors
- Weekly analysis
- Priority support
- **Target:** Mid-size SaaS ($5M-$20M revenue)

**Tier 3: Scale** — $699/month
- Up to $5M monthly volume
- Daily analysis
- Dedicated Slack channel
- Quarterly savings review call
- **Target:** Large e-commerce ($20M-$50M revenue)

**Free Tier (Lead Magnet):**
- One-time analysis (last 30 days)
- See total leakage identified
- Get 1 recommendation
- Upgrade to track over time + get all recommendations

### Alternative: Performance Pricing (Test)

**Model:** 15% of identified savings (capped at $999/month)

**How it works:**
1. Month 1: Free analysis
2. Month 2+: We identify $X savings → charge 15% of $X
3. Customer only pays if we find savings

**Pros:**
- No-risk for customer
- Aligns incentives perfectly
- Customers love "pay for performance"

**Cons:**
- Variable revenue (harder to forecast)
- Attribution complexity (did they actually implement?)
- Lower LTV if you're really good (find savings once, then what?)

**Decision:** Test both models with first 10 customers. Pick winner.

---

## 🎯 First 10 Customers Playbook

### Month 1: Customers 1-3

**Source:** Direct outreach from Week 1-2 validation

**Strategy:**
- Personal onboarding (1 hour Zoom)
- Weekly check-ins
- "Concierge" implementation help (guide them through route switch)
- Ask for testimonial if they save money

**Goal:** Prove value, get case studies

### Month 2: Customers 4-7

**Source:** Indie Hackers + Reddit launch

**Strategy:**
- Self-serve onboarding (but monitor closely)
- Automated email sequence (Day 1, 7, 14, 21, 28)
- Jump on call if they seem confused
- Ask for referrals

**Goal:** Validate self-serve onboarding

### Month 3: Customers 8-10

**Source:** Content + referrals + word-of-mouth

**Strategy:**
- Fully self-serve
- Only engage if they ask
- Collect feedback for v1.1 features
- Optimize funnel based on drop-off points

**Goal:** Prove repeatable acquisition

---

## 🚨 Red Flags (Pivot Signals)

### If you see these in first 3 months, STOP and reassess:

❌ **<20% trial → paid conversion**
- Problem: Product isn't valuable enough or pricing is wrong
- Fix: Talk to churned trials, understand objections

❌ **Customers don't implement recommendations**
- Problem: Recommendations aren't actionable or savings aren't worth effort
- Fix: Add execution capability or simplify recommendations

❌ **Churn >10% monthly**
- Problem: Product isn't sticky, value is one-time
- Fix: Add ongoing monitoring, alerts, recurring value

❌ **Can't get to 10 customers in 3 months**
- Problem: Market doesn't care or GTM is broken
- Fix: Re-validate ICP, try different channels

---

## 🏆 Success Metrics (Track Weekly)

### Acquisition
- Signups/week: 10+ (Month 1-2), 20+ (Month 3+)
- Trial → Paid conversion: 10%+
- CAC (Customer Acquisition Cost): $0 (all organic)

### Engagement
- % users who connect Stripe: 80%+
- % users who view recommendations: 70%+
- % users who export report: 40%+

### Revenue
- MRR: $300 (Month 1), $1k (Month 2), $3k (Month 3)
- ARPU: $150-$300
- Churn: <5% monthly

### Value Delivery
- Avg savings identified per customer: $1,000+/month
- % customers who implement ≥1 recommendation: 30%+
- NPS: 40+

---

## ✅ GTM Checklist (Before Launch)

### Pre-Launch (Week 1-4)
- [ ] 20+ email addresses in beta waitlist
- [ ] 5+ customer validation calls completed
- [ ] ICP confirmed (revenue, payment volume, pain point)
- [ ] Pricing tested with 5 prospects (3+ say yes)

### Launch Assets (Week 5)
- [ ] Landing page with clear value prop
- [ ] Free trial signup flow working
- [ ] Email sequences written (trial nurture)
- [ ] 3 customer case studies (or testimonials)

### Launch Day (Week 6)
- [ ] Indie Hackers post published
- [ ] Reddit posts in 3 subreddits
- [ ] Twitter thread posted
- [ ] Email waitlist (launch announcement)

### Post-Launch (Week 7-12)
- [ ] Publishing 2 content pieces/week
- [ ] Active in communities (30 min/day)
- [ ] Weekly outreach to 10 prospects (personalized)
- [ ] Monitoring metrics dashboard daily

---

**Next:** `06_execution_timeline.md` → Week-by-week build + launch plan
