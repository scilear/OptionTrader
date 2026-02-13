from __future__ import annotations


def evaluate_quote(
    bid: float | None,
    ask: float | None,
    allow_zero_bid: bool,
    spread_gate_pct: float,
) -> tuple[bool, dict]:
    flags: dict[str, bool] = {}

    if bid is None or ask is None:
        flags["missing"] = True
        return False, flags

    if bid > ask:
        flags["crossed"] = True
        return False, flags

    if bid <= 0 and not allow_zero_bid:
        flags["zero_bid"] = True
        return False, flags

    mid = (bid + ask) / 2 if bid + ask > 0 else 0.0
    if mid > 0:
        spread = (ask - bid) / mid
        if spread > spread_gate_pct:
            flags["wide_spread"] = True

    return True, flags
