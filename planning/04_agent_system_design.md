# 04 — Agent System Design (The Innovation Core)

**Prerequisites:** Architecture locked  
**Purpose:** Define exact agent behavior, prompts, and coordination logic

---

## 🎯 Why This Matters

**This is your moat.**

If your agents are just "call API, show data" → commodity.

If your agents **reason, infer, explain, prescribe** → innovation.

**Quality bar:**
- Agent output must be **more insightful** than what customers can figure out manually
- Recommendations must be **specific enough to act on** without external research
- Explanations must be **clear to non-technical finance people**

---

## 🤖 Agent Orchestration (State Machine)

### State Flow

```
Payment Data Ingested
    ↓
[Flow Reconstruction Agent]
    ├─ Identifies intermediaries
    ├─ Estimates route path
    └─ Confidence: 70-90%
    ↓
[Fee Attribution Agent]
    ├─ Calculates expected costs
    ├─ Attributes variance to sources
    └─ Breakdown: Platform, FX, Intermediary
    ↓
[Leakage Detection Agent]
    ├─ Compares to corridor baseline
    ├─ Flags anomalies
    └─ Categorizes leakage types
    ↓
[Optimization Agent]
    ├─ Queries alternative routes
    ├─ Simulates savings
    └─ Generates recommendations
    ↓
Results Stored & Displayed
```

### Orchestration Code (LangGraph)

```python
from langgraph.graph import StateGraph, END
from typing import TypedDict, Annotated
import operator

class PaymentAnalysisState(TypedDict):
    # Input
    payment_id: str
    user_id: str
    payment_data: dict  # Stripe payout object
    
    # Extracted fields
    corridor: str
    amount_sent: float
    currency_sent: str
    amount_received: float
    currency_received: str
    initiated_at: str
    settled_at: str
    
    # Agent outputs (accumulated)
    flow: dict | None
    fees: dict | None
    leakage: dict | None
    recommendations: Annotated[list[dict], operator.add]  # Accumulate
    
    # Metadata
    confidence: float
    errors: Annotated[list[str], operator.add]  # Accumulate
    agent_costs: dict  # Track LLM costs per agent

# Build workflow
workflow = StateGraph(PaymentAnalysisState)

# Add nodes (agents)
workflow.add_node("extract_data", extract_payment_data)
workflow.add_node("reconstruct_flow", flow_reconstruction_agent)
workflow.add_node("attribute_fees", fee_attribution_agent)
workflow.add_node("detect_leakage", leakage_detection_agent)
workflow.add_node("optimize", optimization_agent)
workflow.add_node("save_results", save_to_database)

# Define edges
workflow.set_entry_point("extract_data")
workflow.add_edge("extract_data", "reconstruct_flow")
workflow.add_edge("reconstruct_flow", "attribute_fees")
workflow.add_edge("attribute_fees", "detect_leakage")
workflow.add_edge("detect_leakage", "optimize")
workflow.add_edge("optimize", "save_results")
workflow.add_edge("save_results", END)

# Compile
app = workflow.compile()

# Execute
result = await app.ainvoke({
    "payment_id": "pay_123",
    "user_id": "user_456",
    "payment_data": stripe_payout_object,
    "recommendations": [],
    "errors": [],
    "agent_costs": {}
})
```

---

## 🔍 Agent 1: Flow Reconstruction Agent

### Purpose
Reverse-engineer the payment route by inferring intermediaries from available data.

### Why This Is Hard (And Valuable)
- Stripe doesn't expose routing details
- Intermediaries are dynamic (change based on volume, time, regulations)
- Must use domain knowledge + heuristics + LLM reasoning

### Inputs
```python
{
    "corridor": "USD_EUR",
    "amount_sent": 10000.00,
    "currency_sent": "USD",
    "amount_received": 9156.00,
    "currency_received": "EUR",
    "initiated_at": "2026-01-15T10:30:00Z",
    "settled_at": "2026-01-18T14:22:00Z",
    "settlement_days": 3,
    "stripe_payout_id": "po_1234xyz"
}
```

### Knowledge Base (Pre-loaded)

**Corridor Characteristics Database:**
```python
CORRIDOR_KNOWLEDGE = {
    "USD_EUR": {
        "typical_routes": [
            {
                "route": "Stripe → Citi → SEPA → Local Bank",
                "probability": 0.6,
                "typical_duration_days": 2,
                "typical_intermediaries": ["Stripe", "Citi Correspondent", "SEPA", "Receiving Bank"]
            },
            {
                "route": "Stripe → SWIFT → Local Bank",
                "probability": 0.3,
                "typical_duration_days": 3,
                "typical_intermediaries": ["Stripe", "SWIFT Network", "Receiving Bank"]
            },
            {
                "route": "Stripe → Direct SEPA",
                "probability": 0.1,
                "typical_duration_days": 1,
                "typical_intermediaries": ["Stripe", "SEPA", "Receiving Bank"]
            }
        ],
        "typical_fx_spread": 0.012,  # 1.2%
        "typical_platform_fee": 0.0025,  # 0.25%
        "typical_intermediary_fee_usd": 15
    },
    # ... other corridors
}
```

### Agent Logic

```python
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser

async def flow_reconstruction_agent(state: PaymentAnalysisState) -> dict:
    """
    Reconstruct payment flow using LLM reasoning + domain knowledge.
    """
    
    # Load corridor knowledge
    corridor_info = CORRIDOR_KNOWLEDGE.get(state["corridor"])
    if not corridor_info:
        return {
            "flow": None,
            "errors": [f"Unsupported corridor: {state['corridor']}"],
            "confidence": 0.0
        }
    
    # Build context for LLM
    context = f"""
    Corridor: {state['corridor']}
    Amount sent: {state['amount_sent']} {state['currency_sent']}
    Amount received: {state['amount_received']} {state['currency_received']}
    Settlement time: {state['settlement_days']} days
    
    Typical routes for this corridor:
    {json.dumps(corridor_info['typical_routes'], indent=2)}
    """
    
    # LLM prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", FLOW_RECONSTRUCTION_SYSTEM_PROMPT),
        ("user", context)
    ])
    
    # Execute
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    chain = prompt | llm | JsonOutputParser()
    
    try:
        result = await chain.ainvoke({})
        
        return {
            "flow": result,
            "confidence": result.get("confidence", 0.7),
            "agent_costs": {
                "flow_reconstruction": calculate_cost(result)
            }
        }
    
    except Exception as e:
        return {
            "flow": None,
            "errors": [f"Flow reconstruction failed: {str(e)}"],
            "confidence": 0.0
        }
```

### System Prompt

```python
FLOW_RECONSTRUCTION_SYSTEM_PROMPT = """
You are an expert in cross-border payment routing and banking intermediaries.

Your task: Given a cross-border payment's basic details and typical routing patterns for that corridor, reconstruct the most likely payment flow.

Guidelines:
1. Payment flows typically go through 3-5 hops (PSP → Intermediary(ies) → Destination Bank)
2. Use settlement time as a clue (faster = fewer hops, direct routing)
3. Use amount delta to estimate total fees, then distribute across intermediaries
4. SWIFT routes take 2-4 days, SEPA routes take 1-2 days
5. Larger amounts often get routed differently than smaller amounts
6. Be probabilistic: Output confidence score (0.0-1.0) based on how certain you are

Output strict JSON format:
{
  "hops": [
    {
      "sequence": 1,
      "entity": "Stripe",
      "entity_type": "PSP",
      "estimated_fee_usd": 25.00,
      "estimated_fee_pct": 0.25,
      "confidence": 0.95,
      "reasoning": "Stripe charges standard 0.25% platform fee for payouts"
    },
    {
      "sequence": 2,
      "entity": "Citi Correspondent Bank",
      "entity_type": "correspondent_bank",
      "estimated_fee_usd": 20.00,
      "estimated_fee_pct": 0.0,
      "confidence": 0.75,
      "reasoning": "3-day settlement suggests correspondent bank involved; Citi is common for USD→EUR"
    },
    ...
  ],
  "total_estimated_fees_usd": 85.00,
  "route_description": "Stripe → Citi Correspondent → SEPA → Deutsche Bank",
  "confidence": 0.78,
  "alternative_routes": ["Direct SEPA (less likely due to 3-day settlement)"]
}

Be specific but acknowledge uncertainty. If multiple routes are equally likely, pick the most probable and mention alternatives.
"""
```

### Example Output

```json
{
  "hops": [
    {
      "sequence": 1,
      "entity": "Stripe",
      "entity_type": "PSP",
      "estimated_fee_usd": 25.00,
      "estimated_fee_pct": 0.25,
      "confidence": 0.95,
      "reasoning": "Stripe charges 0.25% for cross-border payouts per their pricing page"
    },
    {
      "sequence": 2,
      "entity": "SWIFT Network",
      "entity_type": "payment_network",
      "estimated_fee_usd": 15.00,
      "estimated_fee_pct": 0.0,
      "confidence": 0.80,
      "reasoning": "3-day settlement and amount size suggest SWIFT routing; typical SWIFT fee is $10-20"
    },
    {
      "sequence": 3,
      "entity": "Receiving Bank (likely Deutsche Bank)",
      "entity_type": "receiving_bank",
      "estimated_fee_usd": 40.00,
      "estimated_fee_pct": 0.0,
      "confidence": 0.70,
      "reasoning": "Remainder of fee delta attributed to receiving bank FX spread (1.2% applied)"
    }
  ],
  "total_estimated_fees_usd": 80.00,
  "route_description": "Stripe → SWIFT Network → Receiving Bank",
  "confidence": 0.78,
  "alternative_routes": [
    "Stripe → Citi Correspondent → SEPA (less likely, would be 2-day settlement)"
  ]
}
```

---

## 💰 Agent 2: Fee Attribution Agent

### Purpose
Calculate expected costs and attribute actual costs to specific sources.

### Why This Is Valuable
- Customers see "total fee: $80" but don't know breakdown
- You show "Stripe: $25, SWIFT: $15, Bank FX: $40"
- Enables targeted optimization

### Inputs
```python
{
    "payment_data": {...},  # Original payment
    "flow": {...}  # From previous agent
}
```

### Logic (Deterministic, No LLM)

```python
async def fee_attribution_agent(state: PaymentAnalysisState) -> dict:
    """
    Calculate expected vs actual costs, attribute to sources.
    """
    
    # Get mid-market FX rate (use external API or DB)
    mid_rate = await get_fx_rate(
        state["currency_sent"],
        state["currency_received"],
        state["initiated_at"]
    )
    
    # Expected amount if zero fees + mid-market rate
    expected_amount = state["amount_sent"] * mid_rate
    
    # Actual amount received
    actual_amount = state["amount_received"]
    
    # Total cost (fees + FX spread)
    total_cost_usd = (expected_amount - actual_amount) / mid_rate
    
    # Breakdown
    fees = {
        "expected_amount": round(expected_amount, 2),
        "actual_amount": round(actual_amount, 2),
        "mid_market_fx_rate": round(mid_rate, 6),
        "actual_fx_rate": round(actual_amount / state["amount_sent"], 6),
        
        # Fee components
        "platform_fee_usd": None,
        "intermediary_fees_usd": None,
        "fx_spread_usd": None,
        "total_fees_usd": round(total_cost_usd, 2),
        
        # Percentages
        "total_cost_pct": round((total_cost_usd / state["amount_sent"]) * 100, 2)
    }
    
    # Attribute to sources using flow reconstruction
    if state["flow"] and state["flow"]["hops"]:
        # Platform fee (first hop, usually)
        platform_hop = next((h for h in state["flow"]["hops"] if h["entity_type"] == "PSP"), None)
        if platform_hop:
            fees["platform_fee_usd"] = platform_hop["estimated_fee_usd"]
        
        # Intermediary fees (sum of all non-PSP, non-FX hops)
        intermediary_hops = [h for h in state["flow"]["hops"] if h["entity_type"] in ["correspondent_bank", "payment_network"]]
        fees["intermediary_fees_usd"] = sum(h["estimated_fee_usd"] for h in intermediary_hops)
        
        # FX spread (remainder)
        fees["fx_spread_usd"] = total_cost_usd - (fees["platform_fee_usd"] or 0) - (fees["intermediary_fees_usd"] or 0)
        fees["fx_spread_pct"] = round((fees["fx_spread_usd"] / state["amount_sent"]) * 100, 2)
    
    return {"fees": fees}
```

### External Data: FX Rates

**Use Free API:**
```python
import httpx

async def get_fx_rate(from_currency: str, to_currency: str, date: str) -> float:
    """
    Get mid-market FX rate from free API (e.g., exchangerate-api.com)
    """
    # Use date for historical rates
    date_str = date[:10]  # YYYY-MM-DD
    
    url = f"https://api.exchangerate-api.com/v4/historical/{from_currency}/{date_str}"
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        return data["rates"][to_currency]
```

**Fallback:** Store daily rates in database if API unreliable.

---

## 🚨 Agent 3: Leakage Detection Agent

### Purpose
Identify what's excessive/unusual compared to corridor baseline.

### Why This Is Valuable
- Customers don't know what "normal" is
- You benchmark against typical corridor costs
- Flag specific issues ("Your FX spread is 2x typical")

### Inputs
```python
{
    "payment_data": {...},
    "fees": {...}  # From previous agent
}
```

### Logic

```python
async def leakage_detection_agent(state: PaymentAnalysisState) -> dict:
    """
    Compare actual costs to corridor baseline, flag anomalies.
    """
    
    # Load corridor baseline
    corridor_info = CORRIDOR_KNOWLEDGE.get(state["corridor"])
    if not corridor_info:
        return {"leakage": None, "errors": [f"No baseline for {state['corridor']}"]}
    
    leakage_items = []
    total_leakage = 0.0
    
    fees = state["fees"]
    
    # Check 1: FX spread excessive?
    expected_fx_spread_usd = state["amount_sent"] * corridor_info["typical_fx_spread"]
    if fees["fx_spread_usd"] > expected_fx_spread_usd * 1.1:  # 10% tolerance
        leakage_amount = fees["fx_spread_usd"] - expected_fx_spread_usd
        leakage_items.append({
            "type": "fx_spread",
            "amount_usd": round(leakage_amount, 2),
            "severity": "high" if leakage_amount > 50 else "medium",
            "explanation": f"FX spread of {fees['fx_spread_pct']}% exceeds typical {corridor_info['typical_fx_spread']*100:.2f}% for this corridor by {leakage_amount:.2f} USD",
            "recommendation_hint": "Consider using FX platform with tighter spreads (e.g., Wise, Revolut)"
        })
        total_leakage += leakage_amount
    
    # Check 2: Intermediary fees excessive?
    expected_intermediary_fee = corridor_info["typical_intermediary_fee_usd"]
    if fees["intermediary_fees_usd"] and fees["intermediary_fees_usd"] > expected_intermediary_fee * 1.2:
        leakage_amount = fees["intermediary_fees_usd"] - expected_intermediary_fee
        leakage_items.append({
            "type": "intermediary_fees",
            "amount_usd": round(leakage_amount, 2),
            "severity": "medium",
            "explanation": f"Intermediary fees of ${fees['intermediary_fees_usd']:.2f} exceed typical ${expected_intermediary_fee:.2f} by ${leakage_amount:.2f}",
            "recommendation_hint": "Route optimization may reduce intermediaries"
        })
        total_leakage += leakage_amount
    
    # Check 3: Settlement delay cost?
    expected_settlement_days = corridor_info["typical_routes"][0]["typical_duration_days"]
    if state["settlement_days"] > expected_settlement_days:
        # Estimate opportunity cost (assuming 5% annual cost of capital)
        delay_days = state["settlement_days"] - expected_settlement_days
        opportunity_cost = state["amount_sent"] * 0.05 * (delay_days / 365)
        if opportunity_cost > 5:  # Only flag if >$5
            leakage_items.append({
                "type": "settlement_delay",
                "amount_usd": round(opportunity_cost, 2),
                "severity": "low",
                "explanation": f"Settlement took {state['settlement_days']} days vs typical {expected_settlement_days} days, costing ~${opportunity_cost:.2f} in delayed access to funds",
                "recommendation_hint": "Consider faster rails (e.g., direct SEPA, RTP)"
            })
            total_leakage += opportunity_cost
    
    return {
        "leakage": {
            "total_leakage_usd": round(total_leakage, 2),
            "total_leakage_pct": round((total_leakage / state["amount_sent"]) * 100, 2),
            "leakage_items": leakage_items,
            "baseline_cost_usd": round(
                state["amount_sent"] * corridor_info["typical_fx_spread"] +
                state["amount_sent"] * corridor_info["typical_platform_fee"] +
                corridor_info["typical_intermediary_fee_usd"],
                2
            )
        }
    }
```

---

## 🎯 Agent 4: Optimization Agent

### Purpose
Generate actionable recommendations to reduce costs.

### Why This Is Valuable
- Not just "you're overpaying" but "do this to fix it"
- Specific, implementable, with ROI estimates

### Inputs
```python
{
    "payment_data": {...},
    "fees": {...},
    "leakage": {...}
}
```

### Logic (LLM-Powered)

```python
async def optimization_agent(state: PaymentAnalysisState) -> dict:
    """
    Generate 3-5 actionable recommendations.
    """
    
    # Build context
    leakage_summary = "\n".join([
        f"- {item['type']}: ${item['amount_usd']} ({item['explanation']})"
        for item in state["leakage"]["leakage_items"]
    ])
    
    # Load alternative routes from DB
    alternatives = await get_alternative_routes(state["corridor"])
    alternatives_text = json.dumps(alternatives, indent=2)
    
    context = f"""
    Payment Analysis Summary:
    - Corridor: {state['corridor']}
    - Amount sent: ${state['amount_sent']} {state['currency_sent']}
    - Total cost: ${state['fees']['total_fees_usd']} ({state['fees']['total_cost_pct']}%)
    - Total leakage identified: ${state['leakage']['total_leakage_usd']}
    
    Leakage breakdown:
    {leakage_summary}
    
    Alternative routes available for this corridor:
    {alternatives_text}
    
    Customer's payment pattern (if available):
    - Frequency: {await estimate_frequency(state['user_id'], state['corridor'])}
    - Average amount: ${await estimate_avg_amount(state['user_id'], state['corridor'])}
    """
    
    # LLM prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", OPTIMIZATION_SYSTEM_PROMPT),
        ("user", context)
    ])
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)  # Slight creativity
    chain = prompt | llm | JsonOutputParser()
    
    result = await chain.ainvoke({})
    
    return {
        "recommendations": result.get("recommendations", [])
    }
```

### System Prompt

```python
OPTIMIZATION_SYSTEM_PROMPT = """
You are a payment optimization consultant specializing in cross-border payments cost reduction.

Your task: Generate 3-5 specific, actionable recommendations to reduce payment costs, based on identified leakage.

Guidelines:
1. Each recommendation must be SPECIFIC (not "optimize FX" but "switch to Wise Business for USD→EUR")
2. Include realistic savings estimates (be conservative)
3. Assess effort (low/medium/high) and risk (low/medium/high)
4. Provide step-by-step implementation guide (3-5 steps)
5. Prioritize by ROI (savings / effort)
6. Consider customer's payment pattern (frequent small vs infrequent large)

Output strict JSON:
{
  "recommendations": [
    {
      "priority": 1,
      "title": "Switch USD→EUR corridor to Wise Business",
      "category": "route_optimization",
      "description": "Wise offers 0.43% all-in cost for USD→EUR vs your current 1.35%, saving 0.92% per transaction.",
      "estimated_savings_per_transaction_usd": 92.00,
      "estimated_annual_savings_usd": 4600.00,
      "effort": "medium",
      "effort_explanation": "Requires Wise Business account setup (1-2 days) and updating payout settings in Stripe",
      "risk": "low",
      "risk_explanation": "Wise is regulated, reliable, and widely used. No downside beyond setup time.",
      "implementation_steps": [
        "Create Wise Business account at wise.com/business",
        "Complete business verification (upload docs, 1-2 day wait)",
        "Add Wise EUR balance as payout destination in Stripe dashboard",
        "Test with one small payout ($100) to verify routing",
        "Monitor for 2 weeks, then migrate all EUR payouts"
      ],
      "timeframe_to_implement": "1 week",
      "break_even_transactions": 1,
      "resources": [
        "https://wise.com/business/pricing",
        "https://stripe.com/docs/payouts"
      ]
    },
    {
      "priority": 2,
      "title": "Batch weekly instead of daily to reduce intermediary fees",
      "category": "batching",
      "description": "You're paying $15 per transaction in intermediary fees. Batching 5 daily payments into 1 weekly payment reduces fees by 80%.",
      "estimated_savings_per_month_usd": 240.00,
      "estimated_annual_savings_usd": 2880.00,
      "effort": "low",
      "effort_explanation": "Just change payout schedule in Stripe (5 minutes)",
      "risk": "medium",
      "risk_explanation": "Recipients wait longer for funds (up to 7 days). Survey them first to ensure acceptable.",
      "implementation_steps": [
        "Survey recipients: ask if weekly payouts (vs daily) are acceptable",
        "If 80%+ agree, update Stripe payout schedule to weekly",
        "Notify all recipients of new schedule",
        "Monitor for complaints in first month",
        "Revert if more than 10% complain"
      ],
      "timeframe_to_implement": "2 weeks (including survey)",
      "break_even_transactions": 0,
      "caveats": ["Delays recipient access to funds", "May affect recipient satisfaction"]
    },
    ...
  ]
}

Focus on HIGH ROI, LOW EFFORT recommendations first. Be realistic about implementation challenges.
"""
```

---

## 📊 Agent Cost Management

### Token Usage Tracking

```python
def calculate_llm_cost(response, model="gpt-4o-mini"):
    """
    Calculate cost based on token usage.
    """
    PRICING = {
        "gpt-4o-mini": {
            "input": 0.15 / 1_000_000,   # $0.15 per 1M input tokens
            "output": 0.60 / 1_000_000   # $0.60 per 1M output tokens
        },
        "gpt-4o": {
            "input": 2.50 / 1_000_000,
            "output": 10.00 / 1_000_000
        }
    }
    
    input_tokens = response.usage.prompt_tokens
    output_tokens = response.usage.completion_tokens
    
    cost = (
        input_tokens * PRICING[model]["input"] +
        output_tokens * PRICING[model]["output"]
    )
    
    return round(cost, 6)
```

### Cost Per Analysis Estimate

**Typical token usage per agent:**
- Flow Reconstruction: ~1,500 input + 500 output = $0.0005
- Optimization: ~2,000 input + 1,000 output = $0.0009

**Total cost per analysis: ~$0.0015**

**For 1,000 analyses/month: $1.50**

**Break-even: 1 customer at $99/month = 66,000 analyses/month capacity**

---

## 🧪 Agent Testing & Debugging

### Unit Test Example

```python
@pytest.mark.asyncio
async def test_flow_reconstruction_agent():
    """
    Test flow reconstruction with known corridor.
    """
    state = {
        "payment_id": "test_123",
        "corridor": "USD_EUR",
        "amount_sent": 10000.00,
        "amount_received": 9156.00,
        "settlement_days": 3,
        "errors": []
    }
    
    result = await flow_reconstruction_agent(state)
    
    # Assertions
    assert result["flow"] is not None
    assert len(result["flow"]["hops"]) >= 2  # At least PSP + bank
    assert result["confidence"] > 0.5
    assert result["flow"]["total_estimated_fees_usd"] > 0
```

### LangSmith Observability

**View in LangSmith dashboard:**
- Latency per agent
- Token usage per agent
- Error rates
- Confidence score distribution

**Filter low-confidence analyses:**
```python
# In production, flag analyses with confidence <0.7 for manual review
if result["confidence"] < 0.7:
    await notify_manual_review(payment_id, result)
```

---

## 🎯 Agent Performance Metrics

Track in database:

```python
class AnalysisMetrics:
    payment_id: str
    
    # Latency
    total_duration_ms: int
    flow_reconstruction_ms: int
    fee_attribution_ms: int
    leakage_detection_ms: int
    optimization_ms: int
    
    # Cost
    total_llm_cost_usd: float
    
    # Quality
    confidence_score: float
    leakage_identified_usd: float
    recommendations_count: int
    
    # Errors
    error_occurred: bool
    error_message: str | None
```

**Weekly dashboard:**
- Average analysis time: <30 seconds target
- Average cost per analysis: <$0.002 target
- Success rate: >95% target
- Average leakage identified: >$500 target

---

## ✅ Agent System Checklist

Before launch:

- [ ] All 4 agents implemented and tested
- [ ] LangGraph orchestration working end-to-end
- [ ] Corridor knowledge database populated (USD→EUR, USD→INR, USD→GBP)
- [ ] FX rate API integrated and fallback implemented
- [ ] Agent costs tracked per analysis
- [ ] LangSmith observability configured
- [ ] Confidence scores calibrated (tested on 50+ real payments)
- [ ] Recommendations are specific and actionable (reviewed by 3 finance people)

---

**Next:** `05_go_to_market.md` → How to find first customers
