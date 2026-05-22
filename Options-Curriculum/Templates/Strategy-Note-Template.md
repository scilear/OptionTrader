---
title: "{{strategy-name}}"
tags:
  - strategy
  - {{strategy-type}}
aliases:
  - {{alternate-name}}
status: "{{status}}"
strategy-type: "{{income | set-and-forget | 0DTE | long-term}}"
legs: "{{number-of-legs}}"
max-profit: "{{max-profit-description-or-formula}}"
max-loss: "{{max-loss-description-or-formula}}"
breakeven: "{{breakeven-price-or-formula}}"
ideal-IV-rank: "{{IV-rank-range-e.g.-30-50}}"
ideal-DTE: "{{days-to-expiration-range-e.g.-7-21}}"
related:
  - "[[{{related-concept-1}}]]"
  - "[[{{related-concept-2}}]]"
  - "[[{{related-strategy}}]]"
created: <% tp.date.now("YYYY-MM-DD") %>
modified: <% tp.date.now("YYYY-MM-DD") %>
---

> [!warning]
> This strategy involves financial risk. Always validate entry conditions, manage position sizing, and establish hard stop-losses before execution. Paper trade before deploying real capital.

## Structure

Describe the option legs that make up this strategy. Include:
- **Leg 1**: {{leg-type}} {{description}}
  - Strike: {{strike-specification}}
  - Qty: {{quantity}}
  - Side: {{buy/sell}}

- **Leg 2**: {{leg-type}} {{description}}
  - Strike: {{strike-specification}}
  - Qty: {{quantity}}
  - Side: {{buy/sell}}

*(Add more legs as needed)*

Include a simple payoff diagram description or ASCII chart:
```
{{payoff-diagram}}
```

## Entry Conditions

List the specific conditions that signal this strategy should be initiated:

- **Market Condition 1**: {{description}} (e.g., IV rank above 60%)
- **Market Condition 2**: {{description}}
- **Technical Condition 1**: {{description}}
- **Underlying Price**: {{price-range-or-condition}}
- **Time Condition**: {{DTE-requirement}} days to expiration

> [!tip]
> Use a checklist before entry: confirm all conditions are met, validate market liquidity, and check bid/ask spreads on all legs.

## Management Rules

Outline how to manage the position once entered:

1. **Profit Taking**: {{describe-when-to-take-profits}}
   - Partial profit at: {{profit-target-1}}
   - Close at: {{profit-target-2}}

2. **Loss Management**: {{describe-loss-limits}}
   - Hard stop at: {{max-loss-percentage-or-amount}}
   - Review at: {{secondary-loss-level}}

3. **Monitoring Frequency**: {{daily | weekly | as-needed}}

4. **Greeks Targets**: {{describe-target-Greeks-during-hold}}
   - Delta: {{target-range}}
   - Gamma: {{target-range}}
   - Theta: {{target-range}}

## Exit Rules

Define all scenarios that warrant exiting the position:

- **Profit Exit**: Close when {{profit-condition}}
- **Stop Loss Exit**: Close when {{loss-condition}}
- **Time-Based Exit**: Close {{days-before-expiration}} DTE or if {{other-condition}}
- **Technical Exit**: Close if {{technical-condition-breaks}}
- **Fundamental Exit**: Close if {{macro-event-or-earnings}}

## Risk Profile

Summarize the risk characteristics:

| Aspect | Description |
|--------|-------------|
| **Max Risk** | {{max-loss-amount-or-percentage}} |
| **Risk/Reward Ratio** | {{ratio-e.g.-1:2}} |
| **Probability of Profit** | {{estimated-POP-percentage}} |
| **Theta Decay** | {{positive/negative}} — {{explanation}} |
| **Vega Exposure** | {{long/short/neutral}} — {{explanation}} |
| **Gamma Exposure** | {{long/short/neutral}} — {{explanation}} |

## Adjustments

Describe how to adjust the position if the market moves against you:

- **If Underlying Up**: {{adjustment-action}}
- **If Underlying Down**: {{adjustment-action}}
- **If IV Spikes**: {{adjustment-action}}
- **If IV Crushes**: {{adjustment-action}}

*Example: "Roll the short call up and out 5 days if underlying rallies 5% above entry."*

## Chart

Insert a marked-up chart showing:
- Entry zone (shaded region)
- Stop-loss level (red line)
- Profit-taking targets (green lines)
- Current price action relative to entry

*Placeholder for image: [Insert chart image here]*

## Links

- Related concepts: `[[{{concept-1}}]]`, `[[{{concept-2}}]]`
- Comparative strategies: `[[{{strategy-A}}]]`, `[[{{strategy-B}}]]`
- Risk management: `[[{{position-sizing}}]]`, `[[{{stop-losses}}]]`
- Historical playbooks: `[[{{playbook-example}}]]`
