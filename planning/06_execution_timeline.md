# 06 — Execution Timeline (12-Week Build to Revenue)

**Reality:** You're a solo founder with limited time and zero budget  
**Goal:** First paying customer by Week 8, 10 customers by Week 12

---

## 📅 Timeline Overview

| Phase | Weeks | Milestone | Revenue |
|-------|-------|-----------|---------|
| Validation | -2 to 0 | Customer interviews, technical spike | $0 |
| Build | 1-4 | MVP complete, local deployment working | $0 |
| Beta | 5-6 | 5 beta users, product validation | $0 |
| Launch | 6-7 | Public launch, first paid customers | $300-500 |
| Growth | 8-12 | Scale to 10 customers, refine product | $1k-3k |

**Total time to first revenue: 6-8 weeks**  
**Total time to validation: 12 weeks**

---

## 🔬 Week -2 to 0: Validation (BEFORE Building)

### Week -2: Customer Discovery

**Time Budget:** 15 hours

**Monday-Tuesday: Research (4 hours)**
- Find 100 companies on LinkedIn matching ICP
- E-commerce: $5M-$50M revenue, international sales
- SaaS: $5M-$50M revenue, global customers
- Extract CFO/Finance Lead names + LinkedIn profiles

**Wednesday-Friday: Outreach (6 hours)**
- Send 50 personalized LinkedIn DMs or emails
- Template:
  ```
  Hi [Name],
  
  I noticed [Company] works with international customers/sellers.
  
  Quick question: Do you ever discover unexpected fees in your cross-border payouts? Most companies I talk to leak 1-3% to hidden intermediary costs.
  
  I'm building a tool to expose this. Would you be open to a 15-min call to share your experience? I'll analyze one of your payouts for free and show you exactly where the money goes.
  
  [Your Name]
  Payments background, now building in fintech
  ```

**Goal: 10 responses, 5 call bookings**

**Weekend: Prep (1 hour)**
- Create interview script
- Set up Calendly for call booking

**Monday: Calls (4 hours)**
- 5 customer discovery calls (30 min each)
- Ask:
  1. How much cross-border volume monthly?
  2. How do you reconcile payments today?
  3. Ever discovered hidden fees after the fact?
  4. Would you pay $99-299/month if I save you $1k+/month?
- Take notes, record (with permission)

**Deliverable:** 
- 20+ emails in waitlist
- 3+ confirmed "yes I'd pay"
- Notes on pain points, willingness to pay

**Decision Gate:** If <3 say yes → PIVOT to different customer segment or problem

---

### Week -1: Technical Feasibility Spike

**Time Budget:** 20 hours

**Monday-Tuesday: Stripe API Research (4 hours)**
- Create Stripe test account
- Read Stripe API docs (payouts, balance transactions)
- Test OAuth flow
- Fetch sample payout data
- **Question:** Is there enough data to reconstruct flows?

**Wednesday-Thursday: Flow Reconstruction Prototype (8 hours)**
- Pick one real payout (use your own or test data)
- Manually reverse-engineer the route:
  - Get mid-market FX rate (use exchangerate-api.com)
  - Calculate expected amount
  - Compare to actual amount
  - Estimate intermediary chain
- Write Python script to automate this
- **Goal:** Can you identify 3+ intermediaries with 70%+ accuracy?

**Friday: LLM Experimentation (4 hours)**
- Install Ollama (Llama 3.1 8B)
- Write prompt for flow reconstruction
- Test with 5 sample payouts
- Check if LLM output makes sense
- **Goal:** LLM can reason about payment routes

**Weekend: MVP Scope Finalization (4 hours)**
- Review validation results
- Lock MVP features (update `02_mvp_definition.md` if needed)
- Create Trello/Notion board with tasks
- Estimate hours per task

**Deliverable:**
- Proof-of-concept script that analyzes one payout end-to-end
- LLM prompts that work
- Task breakdown for 4-week build

**Decision Gate:** If you can't prove technical feasibility → SIMPLIFY MVP or PIVOT

---

## 🏗️ Week 1-4: Build MVP

### Week 1: Foundation

**Time Budget:** 30 hours

**Day 1-2: Project Setup (8 hours)**
- Create Git repo
- Set up Docker Compose (PostgreSQL, backend, frontend)
- Initialize FastAPI backend skeleton
- Initialize React + Vite frontend skeleton
- Create `.env` files
- Run `docker-compose up` successfully
- **Milestone:** All services start without errors

**Day 3-4: Database & Auth (10 hours)**
- Write Alembic migrations (users, payments, analyses, recommendations tables)
- Implement user registration (email + password)
- Implement login (JWT tokens)
- Add password reset (email via Resend)
- Test auth flow end-to-end
- **Milestone:** Can sign up, log in, get JWT token

**Day 5: Stripe OAuth (6 hours)**
- Implement Stripe OAuth flow (FastAPI endpoint)
- Frontend: "Connect Stripe" button
- Store access token (encrypted)
- Test with Stripe test account
- **Milestone:** Can connect Stripe account, token stored

**Weekend: Frontend Basics (6 hours)**
- Dashboard layout (header, sidebar, main content)
- Landing page (hero, value prop, CTA)
- Sign up / Log in forms
- Basic styling (Tailwind CSS)
- **Milestone:** UI looks decent, not ugly

---

### Week 2: Core Analysis Engine

**Time Budget:** 35 hours

**Day 1: Payment Fetching (6 hours)**
- API endpoint: Fetch payouts from Stripe
- Filter cross-border transactions (currency_sent ≠ currency_received)
- Store in database (payments table)
- Schedule daily sync (cron job or manual for MVP)
- **Milestone:** Payments from Stripe appear in database

**Day 2-3: Agent Setup (12 hours)**
- Install LangGraph
- Create state machine (PaymentAnalysisState)
- Implement Flow Reconstruction Agent
  - Load corridor knowledge from JSON
  - LLM prompt (Ollama for dev)
  - Parse JSON output
- Test with 5 sample payments
- **Milestone:** Agent reconstructs flows with 70%+ confidence

**Day 4: Fee Attribution Logic (8 hours)**
- Implement fee calculation (deterministic, no LLM)
- Get FX rate from API (exchangerate-api.com)
- Calculate expected vs actual
- Attribute to sources (platform, FX, intermediary)
- Store in analyses table
- **Milestone:** Fee breakdown is accurate (±10%)

**Day 5: Leakage Detection (5 hours)**
- Implement baseline comparison
- Flag anomalies (>10% variance)
- Categorize leakage types
- Store leakage_items in database
- **Milestone:** Can identify what's excessive

**Weekend: Optimization Agent (4 hours)**
- Hardcode alternative routes (USD→EUR: Wise, Revolut, etc.)
- LLM prompt for recommendations
- Generate 3-5 recommendations per payment
- Store in recommendations table
- **Milestone:** Recommendations are specific and actionable

---

### Week 3: Frontend Dashboard

**Time Budget:** 30 hours

**Day 1-2: Dashboard Summary (10 hours)**
- Summary cards component (total sent, received, leakage, savings)
- Fetch from backend API (`GET /api/analyses/summary`)
- Display with nice formatting ($ amounts, % leakage)
- Loading states, error handling
- **Milestone:** Dashboard shows high-level stats

**Day 3: Transaction List (6 hours)**
- Table component (corridor, amount, date, leakage)
- Pagination (50 per page)
- Filters (corridor, date range)
- Click row → navigate to detail view
- **Milestone:** Can browse all analyzed payments

**Day 4: Transaction Detail View (8 hours)**
- Flow visualization (simple: boxes + arrows)
- Fee breakdown (pie chart or bar chart)
- Leakage explanation (plain English)
- Cost comparison (expected vs actual)
- **Milestone:** User understands what happened to their money

**Day 5: Recommendations UI (6 hours)**
- Recommendations list (cards)
- Show savings, effort, risk
- "Export Guide" button (download TXT)
- Mark as "In Progress" / "Implemented" / "Dismissed"
- **Milestone:** User can act on recommendations

---

### Week 4: Polish & Deploy

**Time Budget:** 25 hours

**Day 1: Error Handling & UX (6 hours)**
- Add loading spinners
- Error messages (user-friendly)
- Empty states ("No payments yet. Connect Stripe to start.")
- Toast notifications (success, error)
- **Milestone:** No blank screens or crashes

**Day 2: Email Notifications (4 hours)**
- Set up Resend API
- "Analysis complete" email
- Weekly leakage report email
- Templates in HTML
- **Milestone:** Users get notified

**Day 3: Landing Page (6 hours)**
- Hero section (headline, subheadline, CTA)
- How It Works (3 steps)
- Testimonials (use beta users if available)
- Pricing table
- FAQ section
- **Milestone:** Landing page is compelling

**Day 4: Deploy to Production (5 hours)**
- Push code to GitHub
- Connect Railway (backend + PostgreSQL)
- Connect Vercel (frontend)
- Set environment variables
- Run migrations
- Test end-to-end in production
- **Milestone:** Live URL works

**Day 5: Beta User Prep (4 hours)**
- Write onboarding email
- Create quick start guide (PDF or Notion doc)
- Set up feedback form (Typeform or Google Forms)
- Prepare 5 beta user invitations
- **Milestone:** Ready to invite beta users

---

## 🧪 Week 5: Beta Testing

**Time Budget:** 20 hours

**Monday: Invite Beta Users (2 hours)**
- Email 20 waitlist contacts
- "Beta is live! First 10 get lifetime 50% off."
- Include signup link + onboarding guide
- **Goal: 10 signups**

**Tuesday-Thursday: Onboarding Calls (10 hours)**
- Schedule 1-hour Zoom with each beta user
- Walk through:
  1. Sign up
  2. Connect Stripe
  3. Wait for analysis
  4. Review dashboard
  5. Explain one recommendation in detail
- Take notes on confusion points
- **Goal: 5 users fully onboarded**

**Friday: Bug Fixing (4 hours)**
- Monitor Sentry for errors
- Fix critical bugs immediately
- Deploy fixes same day
- **Goal: No showstoppers**

**Weekend: Feedback Synthesis (4 hours)**
- Review feedback form responses
- Categorize feedback (bugs, features, UX)
- Prioritize what to fix before launch
- Update product roadmap
- **Goal: Clear list of pre-launch fixes**

---

## 🚀 Week 6: Public Launch

**Time Budget:** 25 hours

**Monday: Pre-Launch Fixes (6 hours)**
- Fix top 3 UX issues from beta
- Add pricing page
- Add Terms of Service + Privacy Policy (use Termly.io templates)
- Test payment flow (Stripe Checkout)
- **Milestone:** Product is launch-ready

**Tuesday: Launch Day (8 hours)**

**8am: Indie Hackers Post**
- Publish launch post (see GTM doc for template)
- Respond to every comment within 1 hour

**10am: Reddit Posts**
- Post in r/ecommerce, r/SaaS, r/Entrepreneur
- Engage with comments

**12pm: Twitter Thread**
- Publish 10-tweet thread
- Pin to profile

**2pm: Email Waitlist**
- "We're live! Sign up now for 30-day free trial."

**Rest of day:**
- Monitor signups
- Respond to questions
- Fix any critical bugs

**Wednesday-Friday: Launch Follow-Up (8 hours)**
- Engage with comments on all platforms
- DM people who showed interest
- Onboard new signups (send welcome email)
- Monitor analytics (signups, Stripe connections, analyses)

**Weekend: Retrospective (3 hours)**
- Review launch metrics (signups, traffic, engagement)
- What worked? What didn't?
- Plan content for Week 7-12

---

## 💰 Week 7-8: First Paid Customers

**Time Budget:** 20 hours

**Goal: 3 paying customers**

**Week 7:**

**Monday-Tuesday: Beta User Conversion (4 hours)**
- Email beta users (trial ending)
- Offer: 50% lifetime discount if paid this week
- Personalized follow-up (call if needed)
- **Goal: 3/5 convert = $150-300 MRR**

**Wednesday-Friday: Trial User Nurture (8 hours)**
- Email Day 7 trial users: "Here's what you've found so far"
- Jump on call with high-intent users (offered via email)
- Ask: "What's stopping you from paying?"
- Address objections
- **Goal: 2 more paid = $200 MRR**

**Week 8:**

**Monday-Friday: Outreach to New Prospects (8 hours)**
- Find 25 companies matching ICP
- Personalized cold email:
  ```
  Hi [Name],
  
  I saw [Company] processes international payments.
  
  I recently analyzed 500+ Stripe payouts and found the average company leaks 2.3% to hidden fees (FX spread, intermediaries, etc.).
  
  I built a tool that exposes this. Would you be open to a free analysis? Takes 5 minutes to connect Stripe, you'll see exactly where your money goes.
  
  [Link]
  
  [Your Name]
  ```
- Follow up with interested prospects
- **Goal: 5 more signups, 1-2 paid**

---

## 📈 Week 9-12: Scale to 10 Customers

**Time Budget:** 15 hours/week

**Activities (Every Week):**

**Monday: Content Creation (4 hours)**
- Write 1 article (1,000-1,500 words)
- Topics: payment optimization, hidden fees, case studies
- Publish on blog + Medium + LinkedIn

**Tuesday-Thursday: Community Engagement (6 hours)**
- 30 min/day on Indie Hackers, Reddit, Twitter
- Answer payment-related questions
- Share insights from your data
- Plug your tool naturally (not spammy)

**Friday: Metrics Review + Outreach (3 hours)**
- Review weekly metrics (MRR, signups, churn, engagement)
- Identify what's working (double down)
- Identify what's not (stop or fix)
- Outreach to 10 new prospects (personalized)

**Weekend: Product Iteration (2 hours)**
- Fix 1-2 bugs reported by users
- Ship 1 small UX improvement
- Test new feature idea (if time)

**Goal by Week 12:**
- 10 paying customers ($1k-3k MRR)
- 50+ trial users
- 1-2 customer testimonials with $ savings
- Clear understanding of what drives conversions

---

## 🎯 Success Metrics by Week

| Week | Milestone | MRR | Customers |
|------|-----------|-----|-----------|
| 1-4 | MVP built | $0 | 0 |
| 5 | Beta live | $0 | 5 beta |
| 6 | Public launch | $0 | 50 signups |
| 7 | First paid | $300 | 3 |
| 8 | Validate conversion | $500 | 5 |
| 9 | Repeatable GTM | $1,000 | 7 |
| 10 | Content working | $1,500 | 8 |
| 11 | Referrals kicking in | $2,000 | 9 |
| 12 | Validated | $3,000 | 10 |

**If behind by Week 10: Re-evaluate GTM strategy, not product.**

---

## 🚨 Weekly Discipline (Non-Negotiable)

### Daily Habits

**Morning (1 hour):**
- Check Sentry for errors (fix critical bugs)
- Respond to customer emails/DMs (within 24 hours)
- Monitor signups (onboard new users)

**Evening (30 min):**
- Engage in communities (Reddit, Indie Hackers, Twitter)
- Track metrics in spreadsheet (signups, MRR, churn)

### Weekly Habits

**Monday:**
- Plan week's priorities (write 3 goals)
- Block time for content creation (4 hours)

**Friday:**
- Review metrics (what worked, what didn't)
- Celebrate wins (even small ones)
- Plan next week

**Sunday:**
- Rest (no work)
- Recharge

**Burnout kills solo projects. Pace yourself.**

---

## 🛠️ Tools & Setup

### Development Tools (Free)

- **Code Editor:** VS Code
- **Version Control:** Git + GitHub
- **Local Environment:** Docker Desktop
- **API Testing:** Postman or Bruno
- **Database Client:** DBeaver or pgAdmin

### Monitoring (Free Tiers)

- **Errors:** Sentry (5k errors/month free)
- **LLM Observability:** LangSmith (5k traces/month free)
- **Uptime:** UptimeRobot (50 monitors free)
- **Analytics:** Plausible (self-hosted) or Google Analytics

### Productivity

- **Task Management:** Notion or Trello
- **Time Tracking:** Toggl (optional, helps see where time goes)
- **Calendar:** Calendly (for customer calls)
- **Email:** Gmail + Streak CRM (free tier)

### Cost Summary

| Tool | Cost |
|------|------|
| Domain (.com) | $12/year |
| Railway (backend + DB) | $5-10/month |
| Vercel (frontend) | $0 (hobby tier) |
| OpenAI (GPT-4o-mini) | $5-20/month (depends on volume) |
| Resend (email) | $0 (3k emails/month free) |
| **Total** | **$10-30/month** |

**Break-even: 1 customer at $99/month**

---

## ⚠️ Common Pitfalls (Avoid These)

### Week 1-4 (Build)

❌ **Perfectionism** — Ship at 80%, iterate based on feedback  
❌ **Scope creep** — Stick to MVP list, no new features  
❌ **Over-engineering** — No microservices, no Kubernetes, keep it simple

### Week 5-6 (Launch)

❌ **Launching without validation** — If beta users don't love it, don't launch  
❌ **Ignoring feedback** — Beta feedback is gold, act on it immediately  
❌ **One-channel launch** — Launch on 3-5 channels simultaneously for momentum

### Week 7-12 (Growth)

❌ **Not talking to customers** — Every churned user is a lesson, call them  
❌ **Building in isolation** — Engage in communities, build in public  
❌ **Giving up too early** — 12 weeks is fast, some take 6 months to get to 10 customers

---

## ✅ Decision Gates (Stop and Evaluate)

### After Week 0 (Validation)

**If <3 prospects say "yes I'd pay" → STOP**

Options:
- Pivot customer segment
- Adjust value prop
- Simplify problem scope

### After Week 4 (MVP Complete)

**If you can't analyze a payment end-to-end in <5 min → STOP**

Options:
- Simplify MVP (cut features)
- Fix critical tech issue
- Get help (hire contractor for 1 week)

### After Week 8 (First Paid)

**If 0 paying customers → STOP**

Options:
- Re-validate willingness to pay
- Adjust pricing (lower or performance-based)
- Pivot problem (maybe payments isn't it)

### After Week 12 (Validation)

**If <5 paying customers OR >10% churn → EVALUATE**

Options:
- Product-market fit not there yet (keep iterating)
- GTM not working (try different channels)
- Pivot to adjacent problem

**If 10+ customers + <5% churn + 60%+ say "I'd be disappointed if this disappeared" → YOU HAVE PMF. SCALE.**

---

## 🏆 What Success Looks Like

### Week 12 Snapshot

**Product:**
- MVP works reliably (>95% uptime)
- Average analysis time <2 min
- Customers understand results without hand-holding

**Business:**
- 10 paying customers ($1k-3k MRR)
- <5% monthly churn
- 2-3 testimonials with $ savings

**Founder:**
- Clear understanding of what drives conversions
- Repeatable customer acquisition (content + community)
- Confident to scale to 50 customers

**Next Phase:** Double down on what works, hire first contractor for support/content.

---

**Next:** `07_cost_and_revenue_model.md` → Detailed financial projections
