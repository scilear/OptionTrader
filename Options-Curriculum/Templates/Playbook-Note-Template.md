---
title: "{{playbook-name}}"
tags:
  - playbook
  - {{playbook-type}}
aliases:
  - {{alternate-name}}
status: "{{status}}"
related:
  - "[[{{related-playbook-1}}]]"
  - "[[{{related-strategy-1}}]]"
  - "[[{{related-concept-1}}]]"
created: <% tp.date.now("YYYY-MM-DD") %>
modified: <% tp.date.now("YYYY-MM-DD") %>
---

> [!warning]
> This playbook requires strict adherence to entry and exit rules. {{Risk-specific-warning}}. Always validate market conditions and maintain position sizing discipline before deploying this playbook.

## When to Use This Playbook

Describe the specific market environment and triggers that make this playbook applicable:

**Best Used When**:
- {{Market-Condition-1}}: {{explanation}} (e.g., "IV Rank is between 40–60%, indicating balanced premium selling")
- {{Market-Condition-2}}: {{explanation}}
- {{Technical-Condition}}: {{explanation}}

**Time Frame**: {{Optimal holding period}} (e.g., "5–14 days before expiration")

**Underlying**: {{Ticker-or-category}} (e.g., "SPX or high-IV ETFs like VXX")

**Avoid When**:
- {{Avoid-Condition-1}}
- {{Avoid-Condition-2}}

> [!tip]
> Keep a journal of when you deployed this playbook and the outcome. Over time, you'll refine your entry timing and confidence levels.

## Step-by-Step

Follow these steps in order:

### Step 1: Pre-Entry Checklist
Verify all entry criteria are met before committing capital:

- [ ] {{Criteria-1}} — {{How to validate}}
- [ ] {{Criteria-2}} — {{How to validate}}
- [ ] {{Criteria-3}} — {{How to validate}}
- [ ] {{Liquidity-Check}} — {{Min spread / volume threshold}}
- [ ] {{Position-Size-Confirmed}} — {{Max risk amount}}

### Step 2: Build the Position
Execute the trade systematically:

1. **Order 1**: {{Leg-description}} at {{limit-price-guidance}}
   - Monitor {{time-window}} for fill
   - If no fill, {{retry-or-move-on}}

2. **Order 2**: {{Leg-description}} at {{limit-price-guidance}}
   - Ensure {{pricing-condition}} before confirming

3. **Final Check**: {{Verify}} that actual Greeks match expectations

**Entry Timing**: Place orders at {{time-of-day}} (e.g., "first 30 mins of market open for tightest spreads")

### Step 3: Set Initial Stops and Targets
Immediately upon entry, establish hardwired exit rules:

- **Profit Target 1**: Close {{% or amount}} at {{profit-level}}
- **Profit Target 2**: Close {{% or amount}} at {{profit-level}}
- **Hard Stop Loss**: Exit entire position at {{loss-level}}

### Step 4: Monitor and Adjust
Actively manage the position according to the rules below.

### Step 5: Exit
Execute exit per the ruleset in **Management Rules**.

## Entry Criteria Table

Use this table to systematically verify entry conditions before deploying:

| Criterion | Pass | Value | Notes |
|-----------|------|-------|-------|
| {{Criterion-1}} (e.g., IV Rank) | [ ] | {{Expected-value}} | {{Details}} |
| {{Criterion-2}} (e.g., Theta Decay) | [ ] | {{Expected-value}} | {{Details}} |
| {{Criterion-3}} (e.g., Bid/Ask Spread) | [ ] | {{Expected-value}} | {{Details}} |
| {{Criterion-4}} (e.g., DTE Range) | [ ] | {{Expected-value}} | {{Details}} |
| **Overall Entry Readiness** | All [ ] ✓ | — | Proceed only if all boxes checked |

## Management Rules

### Daily Checks
Perform these checks {{Frequency}}:

- **Greeks Monitor**: {{How to read/interpret}} Theta, Delta, Gamma
- **Price Move**: If underlying moved {{threshold}}, {{Action}}
- **IV Change**: If IV rank changed {{threshold}}, {{Action}}

### Profit-Taking Rules
- **When P&L hits {{%}}**: {{Action}} — e.g., "Close 50% of position"
- **When P&L hits {{%}}**: {{Action}} — e.g., "Close remaining 50%"
- **Hold to {{DTE}}**: {{Action}} — e.g., "Close all, regardless of P&L"

### Loss-Management Rules
- **If loss exceeds {{%}}**: {{Forced Exit or Adjustment?}}
  - Adjustment option: {{Roll description}}
  - Stop-loss option: {{Exit description}}

### Adjustment Protocol (if applicable)
When {{Condition}}, {{Specific Adjustment}}:
- Example: "If underlying rallies 2% above entry, roll the {{leg}} to {{new-strike}}"

## What Can Go Wrong

Catalog the pitfalls and hazards of this playbook:

### Common Mistake 1: {{Mistake}}
**How It Happens**: {{Scenario}}  
**Result**: {{Consequence}}  
**Prevention**: {{Safeguard or checklist item}}

### Common Mistake 2: {{Mistake}}
**How It Happens**: {{Scenario}}  
**Result**: {{Consequence}}  
**Prevention**: {{Safeguard or checklist item}}

### Tail Risk: {{Risk}}
**Trigger**: {{What causes this}}  
**Worst Case**: {{Magnitude}}  
**Mitigation**: {{Position size limit or hedge}}

### Market Condition Risk: {{Condition}}
**Example**: {{Historical example or scenario}}  
**Impact**: {{How playbook breaks down}}  
**Lesson**: {{Takeaway}}

## Links

- **Strategies in This Playbook**: `[[{{Strategy-1}}]]`, `[[{{Strategy-2}}]]`
- **Foundational Concepts**: `[[{{Concept-A}}]]`, `[[{{Concept-B}}]]`
- **Risk Management Framework**: `[[{{Framework}}]]`
- **Related Playbooks**: `[[{{Playbook-X}}]]`
- **Historical Case Study**: `[[{{Case-Study}}]]`
