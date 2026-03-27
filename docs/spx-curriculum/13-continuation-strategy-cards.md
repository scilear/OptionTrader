# Module 13 - Continuation Strategy Cards (Beyond Mean Reversion)

This module documents continuation-oriented decision branches.

Important:

- Current code templates in `src/core/trade_ideas.py` are primarily reversion-oriented.
- These cards define process and candidate families; implementation templates can be added next.

## Why continuation matters

Not every distortion should be faded. In stress and event-driven regimes, continuation can be more coherent than reversion.

Decision principle:

- choose continuation branch when distortion is strengthening with regime/event support and execution remains viable.

## Card C1 - RR Continuation (Defensive Skew Persistence)

Signal context:

- RR becomes more negative with persistence,
- worst-case confirms,
- regime/event context supports sustained downside premium.

What it expresses:

- skew expansion likely persists short-term.

Candidate family (to implement/expand):

- defensive bearish defined-risk spreads aligned with persistent downside skew,
- avoid naive skew-fade until stabilization evidence appears.

Invalidation examples:

- RR stops steepening and reverts with confirmation,
- regime stress indicators cool materially,
- execution quality collapses.

## Card C2 - FLY Continuation (Convexity Stress Persistence)

Signal context:

- `fly25` remains elevated or keeps accelerating,
- worst-case confirms,
- decomposition indicates sustained wing stress.

What it expresses:

- convexity distortion likely to persist before normalization.

Candidate family (to implement/expand):

- lower-risk directional/hedged expressions that do not depend on immediate fly normalization,
- avoid large multi-leg mean-reversion structures in unstable execution windows.

Invalidation examples:

- clear convexity stabilization across adjacent buckets,
- event catalyst passes with rapid decay in distortion,
- spread regime worsens beyond viable execution.

## Card C3 - TERM Continuation (Event Premium Persistence)

Signal context:

- front-vs-back slope remains elevated through pre-event window,
- post-event decay is not yet visible,
- carry costs penalize early normalization bets.

What it expresses:

- near-term premium remains justified longer than baseline expectation.

Candidate family (to implement/expand):

- delay normalization structures until post-event confirmation,
- prefer watch/no-trade if carry + slippage dominate.

Invalidation examples:

- post-event slope normalization with persistence,
- front premium compresses with stable execution,
- new data contradicts event-persistence narrative.

## Continuation Branch Checklist

Use before selecting continuation action:

1. distortion direction is persistent,
2. worst-case confirms,
3. regime/event context supports continuation,
4. execution remains viable,
5. risk worksheet complete.

If any key item fails, downgrade to `Watch` or `No-trade`.

## Tool and Workflow Gaps for Continuation

Current gaps:

- no continuation-specific templates in trade idea engine,
- no explicit UI branch control tied to strategy menu,
- no continuation-vs-reversion outcome analytics panel.

Suggested next implementation:

1. add branch selector persistence in app and export payload,
2. add continuation template prototypes,
3. add branch performance dashboard.
