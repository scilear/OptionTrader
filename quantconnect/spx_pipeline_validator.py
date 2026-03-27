from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date, datetime, timedelta
import math
from typing import Iterable

try:
    from AlgorithmImports import *  # type: ignore
except ImportError:  # pragma: no cover
    class QCAlgorithm:
        pass

    class Resolution:
        MINUTE = "Minute"

    class OptionRight:
        Call = "Call"
        Put = "Put"


@dataclass
class ContractQuote:
    symbol: object
    expiry: date
    strike: float
    right: str
    bid: float
    ask: float
    open_interest: int


@dataclass
class IvPoint:
    expiry: date
    delta_bucket: str
    iv_mid: float | None
    iv_bid: float | None
    iv_ask: float | None
    quality_score: float


@dataclass
class StrategyLeg:
    symbol: object
    quantity: int
    right: str
    expiry: date
    strike: float
    entry_price: float


@dataclass
class VirtualTrade:
    trade_id: int
    alert_type: str
    expiry_bucket: str
    entered_at: datetime
    regime_label: str
    zscore_mid: float
    zscore_worst: float
    tradability_score: float
    legs: list[StrategyLeg]
    entry_value: float


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def _bs_price(
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    vol: float,
    right: str,
) -> float:
    if t_years <= 0 or vol <= 0:
        intrinsic = max(0.0, spot - strike) if right == "C" else max(0.0, strike - spot)
        return intrinsic

    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    d2 = d1 - vol_sqrt
    disc = math.exp(-rate * t_years)

    if right == "C":
        return disc * (fwd * _norm_cdf(d1) - strike * _norm_cdf(d2))
    return disc * (strike * _norm_cdf(-d2) - fwd * _norm_cdf(-d1))


def _bs_delta(
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    vol: float,
    right: str,
) -> float:
    if t_years <= 0 or vol <= 0:
        return 0.0

    fwd = spot * math.exp((rate - div) * t_years)
    vol_sqrt = vol * math.sqrt(t_years)
    d1 = (math.log(fwd / strike) + 0.5 * vol * vol * t_years) / vol_sqrt
    if right == "C":
        return math.exp(-div * t_years) * _norm_cdf(d1)
    return math.exp(-div * t_years) * (_norm_cdf(d1) - 1.0)


def _solve_iv(
    price: float,
    spot: float,
    strike: float,
    rate: float,
    div: float,
    t_years: float,
    right: str,
    vol_low: float = 1e-4,
    vol_high: float = 5.0,
    tol: float = 1e-6,
    max_iter: int = 100,
) -> float | None:
    if price <= 0 or t_years <= 0 or spot <= 0 or strike <= 0:
        return None

    intrinsic = max(0.0, spot - strike) if right == "C" else max(0.0, strike - spot)
    if price < intrinsic:
        return None

    low_price = _bs_price(spot, strike, rate, div, t_years, vol_low, right)
    high_price = _bs_price(spot, strike, rate, div, t_years, vol_high, right)
    if price < low_price or price > high_price:
        return None

    low = vol_low
    high = vol_high
    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        mid_price = _bs_price(spot, strike, rate, div, t_years, mid, right)
        if abs(mid_price - price) < tol:
            return mid
        if mid_price > price:
            high = mid
        else:
            low = mid
    return 0.5 * (low + high)


def _forward(spot: float, rate: float, div: float, t_years: float) -> float:
    return spot * math.exp((rate - div) * t_years)


def _bucket_days(dte: int, buckets: Iterable[int]) -> int:
    return min(buckets, key=lambda b: abs(dte - b))


class SpxPipelineValidatorAlgorithm(QCAlgorithm):
    """
    QuantConnect validation harness for the repo's SPX surface pipeline.

    It uses QC option quotes to rebuild the RR/Fly/term metrics on scheduled
    snapshots, then opens virtual trades using pessimistic bid/ask entry logic.
    """

    def initialize(self) -> None:
        start_year = int(self.get_parameter("start_year") or 2023)
        start_month = int(self.get_parameter("start_month") or 1)
        start_day = int(self.get_parameter("start_day") or 1)
        end_year = int(self.get_parameter("end_year") or 2024)
        end_month = int(self.get_parameter("end_month") or 12)
        end_day = int(self.get_parameter("end_day") or 31)
        self.set_start_date(start_year, start_month, start_day)
        self.set_end_date(end_year, end_month, end_day)
        self.set_cash(1_000_000)

        self.bucket_days = [21, 30, 45]
        self.dte_min = 14
        self.dte_max = 60
        self.spread_gate_pct = float(self.get_parameter("spread_gate_pct") or 0.15)
        self.z_threshold = float(self.get_parameter("z_threshold") or 2.0)
        self.exit_z_threshold = float(self.get_parameter("exit_z_threshold") or 0.50)
        self.persistence_required = int(self.get_parameter("persistence_required") or 2)
        self.z_window_observations = int(self.get_parameter("z_window_observations") or 180)
        self.min_open_interest = int(self.get_parameter("min_open_interest") or 100)
        self.max_hold_days = int(self.get_parameter("max_hold_days") or 10)
        self.max_open_trades = int(self.get_parameter("max_open_trades") or 3)
        self.use_weeklys = (self.get_parameter("use_weeklys") or "true").lower() == "true"
        self.research_mode = (self.get_parameter("research_mode") or "signal_scan").lower()
        self.alert_filter = (self.get_parameter("alert_filter") or "ALL").upper()
        self.bucket_filter = (self.get_parameter("bucket_filter") or "ALL").upper()
        self.eval_frequency_minutes = int(self.get_parameter("eval_frequency_minutes") or 60)
        self.max_candidate_days = int(self.get_parameter("max_candidate_days") or 10)
        self.max_validation_snapshots = int(self.get_parameter("max_validation_snapshots") or 50)
        self.trade_validation_days = self._parse_date_set(self.get_parameter("trade_validation_days") or "")
        self.run_trade_validation = self.research_mode in {"trade_validation", "full"}
        self.run_virtual_trades = self.research_mode == "full"

        self.trade_counter = 0
        self.metric_history: dict[tuple[str, str], deque[float]] = defaultdict(
            lambda: deque(maxlen=self.z_window_observations)
        )
        self.current_metrics: dict[str, dict] = {}
        self.current_alerts: list[dict] = []
        self.open_trades: dict[int, VirtualTrade] = {}
        self.closed_trades: list[dict] = []
        self.signal_mid_passed = 0
        self.signal_worst_passed = 0
        self.signal_tradable = 0
        self.trades_opened = 0
        self.trades_skipped = 0
        self.signal_log: list[dict] = []
        self.candidate_days: dict[date, dict] = {}
        self.evaluations_run = 0
        self.validation_snapshots_run = 0

        self.index = self.add_index("SPX", Resolution.MINUTE).symbol
        if self.use_weeklys:
            self.option = self.add_index_option(self.index, "SPXW", Resolution.MINUTE)
        else:
            self.option = self.add_index_option(self.index, Resolution.MINUTE)

        self.option.set_filter(self._option_filter)

        for hour, minute in self._evaluation_times():
            self.schedule.on(
                self.date_rules.every_day(self.index),
                self.time_rules.at(hour, minute),
                self._scheduled_evaluate,
            )
        self.schedule.on(
            self.date_rules.every_day(self.index),
            self.time_rules.at(15, 55),
            self._scheduled_report,
        )
        self.debug(
            "CONFIG "
            f"research_mode={self.research_mode} "
            f"alert_filter={self.alert_filter} "
            f"bucket_filter={self.bucket_filter} "
            f"eval_frequency_minutes={self.eval_frequency_minutes}"
        )

    def _parse_date_set(self, raw: str) -> set[date]:
        dates: set[date] = set()
        for token in raw.split(","):
            token = token.strip()
            if not token:
                continue
            try:
                dates.add(datetime.strptime(token, "%Y-%m-%d").date())
            except ValueError:
                pass
        return dates

    def _evaluation_times(self) -> list[tuple[int, int]]:
        if self.eval_frequency_minutes <= 60:
            return [(10, 0), (11, 0), (12, 0), (13, 0), (14, 0), (15, 0), (15, 30)]
        if self.eval_frequency_minutes <= 120:
            return [(10, 0), (12, 0), (14, 0), (15, 30)]
        return [(10, 0), (13, 0), (15, 30)]

    def _option_filter(self, universe):
        universe = universe.include_weeklys() if self.use_weeklys else universe
        return universe.expiration(self.dte_min, self.dte_max).strikes(-120, 120)

    def on_data(self, slice: Slice) -> None:
        self._last_slice = slice

    def _scheduled_evaluate(self) -> None:
        if not hasattr(self, "_last_slice"):
            return
        if not self._should_evaluate_now():
            return

        chain = self._get_current_chain(self._last_slice)
        if chain is None:
            return

        spot = float(self.securities[self.index].price)
        if spot <= 0:
            return

        quotes = self._extract_quotes(chain)
        if not quotes:
            return

        metrics = self._compute_surface_metrics(quotes, spot)
        if not metrics:
            return

        self.evaluations_run += 1
        self.current_metrics = {m["expiry_bucket"]: m for m in metrics}
        self.current_alerts = self._compute_alerts(metrics, quotes, spot)

        if self.run_virtual_trades:
            self._manage_open_trades(quotes)
            self._open_new_trades(quotes, spot)

    def _should_evaluate_now(self) -> bool:
        current_day = self.time.date()
        if self.run_trade_validation:
            if self.trade_validation_days:
                if current_day not in self.trade_validation_days:
                    return False
            else:
                if current_day not in self.candidate_days and len(self.candidate_days) >= self.max_candidate_days:
                    return False
        if self.run_trade_validation and self.validation_snapshots_run >= self.max_validation_snapshots:
            return False
        return True

    def _get_current_chain(self, slice: Slice):
        for symbol, chain in slice.option_chains.items():
            if symbol == self.option.symbol:
                return chain
        return None

    def _extract_quotes(self, chain) -> list[ContractQuote]:
        quotes: list[ContractQuote] = []
        now_date = self.time.date()
        for contract in chain:
            bid = float(contract.bid_price)
            ask = float(contract.ask_price)
            if bid < 0 or ask < 0 or bid > ask:
                continue

            dte = (contract.expiry.date() - now_date).days
            if dte < self.dte_min or dte > self.dte_max:
                continue

            if bid == 0 and ask == 0:
                continue

            right = "C" if contract.right == OptionRight.Call else "P"
            quotes.append(
                ContractQuote(
                    symbol=contract.symbol,
                    expiry=contract.expiry.date(),
                    strike=float(contract.strike),
                    right=right,
                    bid=bid,
                    ask=ask,
                    open_interest=int(contract.open_interest),
                )
            )
        return quotes

    def _compute_iv_points(self, quotes: list[ContractQuote], spot: float) -> list[IvPoint]:
        points: list[IvPoint] = []
        rate = 0.0
        div = 0.0

        by_expiry: dict[date, list[ContractQuote]] = defaultdict(list)
        for quote in quotes:
            by_expiry[quote.expiry].append(quote)

        for expiry, exp_quotes in by_expiry.items():
            t_years = max((expiry - self.time.date()).days, 0) / 365.0
            if t_years <= 0:
                continue

            rows = []
            for quote in exp_quotes:
                mid = 0.5 * (quote.bid + quote.ask) if quote.bid + quote.ask > 0 else 0.0
                iv_mid = _solve_iv(mid, spot, quote.strike, rate, div, t_years, quote.right) if mid > 0 else None
                iv_bid = _solve_iv(quote.bid, spot, quote.strike, rate, div, t_years, quote.right) if quote.bid > 0 else None
                iv_ask = _solve_iv(quote.ask, spot, quote.strike, rate, div, t_years, quote.right) if quote.ask > 0 else None
                if iv_mid is None:
                    continue

                quality = 1.0
                if mid > 0 and (quote.ask - quote.bid) / mid > self.spread_gate_pct:
                    quality = 0.0

                delta = _bs_delta(spot, quote.strike, rate, div, t_years, iv_mid, quote.right)
                rows.append(
                    {
                        "strike": quote.strike,
                        "right": quote.right,
                        "iv_mid": iv_mid,
                        "iv_bid": iv_bid,
                        "iv_ask": iv_ask,
                        "delta": delta,
                        "quality": quality,
                    }
                )

            if not rows:
                continue

            fwd = _forward(spot, rate, div, t_years)
            atm_row = min(rows, key=lambda row: abs(row["strike"] - fwd))
            points.append(
                IvPoint(
                    expiry=expiry,
                    delta_bucket="ATM",
                    iv_mid=atm_row["iv_mid"],
                    iv_bid=atm_row["iv_bid"],
                    iv_ask=atm_row["iv_ask"],
                    quality_score=atm_row["quality"],
                )
            )

            for target, bucket, right in [
                (0.25, "+0.25C", "C"),
                (-0.25, "-0.25P", "P"),
                (0.10, "+0.10C", "C"),
                (-0.10, "-0.10P", "P"),
            ]:
                candidates = [row for row in rows if row["right"] == right]
                if not candidates:
                    continue
                selected = min(candidates, key=lambda row: abs(row["delta"] - target))
                points.append(
                    IvPoint(
                        expiry=expiry,
                        delta_bucket=bucket,
                        iv_mid=selected["iv_mid"],
                        iv_bid=selected["iv_bid"],
                        iv_ask=selected["iv_ask"],
                        quality_score=selected["quality"],
                    )
                )
        return points

    def _compute_surface_metrics(self, quotes: list[ContractQuote], spot: float) -> list[dict]:
        iv_points = self._compute_iv_points(quotes, spot)
        if not iv_points:
            return []

        rows = []
        for point in iv_points:
            rows.append(
                {
                    "expiry": point.expiry,
                    "bucket": point.delta_bucket,
                    "iv_mid": point.iv_mid,
                    "iv_bid": point.iv_bid,
                    "iv_ask": point.iv_ask,
                    "quality": point.quality_score,
                }
            )

        by_expiry: dict[date, list[dict]] = defaultdict(list)
        for row in rows:
            by_expiry[row["expiry"]].append(row)

        candidates: dict[str, tuple[int, dict]] = {}
        for expiry, exp_rows in by_expiry.items():
            dte = (expiry - self.time.date()).days
            if dte <= 0:
                continue

            bucket_days = _bucket_days(dte, self.bucket_days)
            row_map = {row["bucket"]: row for row in exp_rows}
            atm = row_map.get("ATM")
            c25 = row_map.get("+0.25C")
            p25 = row_map.get("-0.25P")
            c10 = row_map.get("+0.10C")
            p10 = row_map.get("-0.10P")

            quality_atm = atm["quality"] if atm else 0.0
            quality_c25 = c25["quality"] if c25 else 0.0
            quality_p25 = p25["quality"] if p25 else 0.0
            quality_c10 = c10["quality"] if c10 else 0.0
            quality_p10 = p10["quality"] if p10 else 0.0

            tier = None
            if quality_atm >= 1 and quality_c25 >= 1 and quality_p25 >= 1:
                tier = "Core"
            if tier == "Core" and quality_c10 >= 1 and quality_p10 >= 1:
                tier = "Full"

            if tier is None:
                continue

            entry = {
                "expiry_bucket": f"{bucket_days}D",
                "expiry": expiry,
                "dte": dte,
                "tier": tier,
                "atm_iv_mid": atm["iv_mid"] if atm else None,
                "rr25_mid": (c25["iv_mid"] - p25["iv_mid"]) if c25 and p25 else None,
                "rr10_mid": (c10["iv_mid"] - p10["iv_mid"]) if c10 and p10 else None,
                "fly25_mid": ((c25["iv_mid"] + p25["iv_mid"]) / 2 - atm["iv_mid"]) if c25 and p25 and atm else None,
                "fly10_mid": ((c10["iv_mid"] + p10["iv_mid"]) / 2 - atm["iv_mid"]) if c10 and p10 and atm else None,
                "atm_iv_worst": atm["iv_bid"] if atm else None,
                "rr25_worst": (c25["iv_ask"] - p25["iv_bid"]) if c25 and p25 else None,
                "rr10_worst": (c10["iv_ask"] - p10["iv_bid"]) if c10 and p10 else None,
                "fly25_worst": ((c25["iv_ask"] + p25["iv_bid"]) / 2 - atm["iv_bid"]) if c25 and p25 and atm else None,
                "fly10_worst": ((c10["iv_ask"] + p10["iv_bid"]) / 2 - atm["iv_bid"]) if c10 and p10 and atm else None,
            }

            key = f"{bucket_days}D"
            distance = abs(dte - bucket_days)
            if key not in candidates or distance < candidates[key][0]:
                candidates[key] = (distance, entry)

        selected = [entry for _, entry in candidates.values()]
        selected.sort(key=lambda row: int(row["expiry_bucket"].replace("D", "")))
        for idx, entry in enumerate(selected):
            next_entry = selected[idx + 1] if idx + 1 < len(selected) else None
            entry["term_slope_mid"] = (
                entry["atm_iv_mid"] - next_entry["atm_iv_mid"]
                if next_entry and entry["atm_iv_mid"] is not None and next_entry["atm_iv_mid"] is not None
                else None
            )
            entry["term_slope_worst"] = (
                entry["atm_iv_worst"] - next_entry["atm_iv_worst"]
                if next_entry and entry["atm_iv_worst"] is not None and next_entry["atm_iv_worst"] is not None
                else None
            )
        return selected

    def _zscore(self, key: tuple[str, str], value: float | None) -> float | None:
        if value is None:
            return None
        history = self.metric_history[key]
        if len(history) < max(self.persistence_required, 20):
            history.append(value)
            return None

        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / max(len(history) - 1, 1)
        std = math.sqrt(variance)
        history.append(value)
        if std == 0:
            return None
        return (value - mean) / std

    def _persistence_count(self, history: deque[float], threshold: float) -> int:
        if len(history) < self.persistence_required:
            return 0
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / max(len(history) - 1, 1)
        std = math.sqrt(variance)
        if std == 0:
            return 0

        count = 0
        for value in reversed(list(history)[-self.persistence_required :]):
            if abs((value - mean) / std) >= threshold:
                count += 1
            else:
                break
        return count

    def _compute_alerts(self, metrics: list[dict], quotes: list[ContractQuote], spot: float) -> list[dict]:
        alerts: list[dict] = []
        regime_label = self._infer_regime(metrics)

        for entry in metrics:
            bucket = entry["expiry_bucket"]
            tier = entry.get("tier")
            if tier is None:
                continue
            if self.bucket_filter != "ALL" and bucket != self.bucket_filter:
                continue

            for metric_name, worst_name, alert_type in [
                ("rr25_mid", "rr25_worst", "RR_EXTREME"),
                ("fly25_mid", "fly25_worst", "FLY_EXTREME"),
                ("term_slope_mid", "term_slope_worst", "TERM_KINK"),
            ]:
                if self.alert_filter != "ALL" and alert_type != self.alert_filter:
                    continue
                z_mid = self._zscore((bucket, metric_name), entry.get(metric_name))
                z_worst = self._zscore((bucket, worst_name), entry.get(worst_name))
                history = self.metric_history[(bucket, metric_name)]
                persistence = self._persistence_count(history, self.z_threshold)

                if z_mid is None:
                    continue
                if abs(z_mid) < self.z_threshold:
                    continue
                self.signal_mid_passed += 1
                if persistence < self.persistence_required:
                    continue
                if alert_type == "RR_EXTREME" and regime_label == "Stress":
                    continue

                worst_pass = z_worst is not None and abs(z_worst) >= self.z_threshold
                if worst_pass:
                    self.signal_worst_passed += 1

                tradable = self._is_alert_tradable(
                    {
                        "alert_type": alert_type,
                        "expiry": entry["expiry"],
                        "expiry_bucket": bucket,
                        "tier": tier,
                        "regime_label": regime_label,
                        "zscore_mid": z_mid,
                        "zscore_worst": z_worst if z_worst is not None else float("nan"),
                        "persistence": persistence,
                        "tradability_score": self._tradability_score(bucket),
                    },
                    quotes,
                    spot,
                )
                if tradable:
                    self.signal_tradable += 1

                self._record_signal(
                    {
                        "ts": self.time,
                        "alert_type": alert_type,
                        "expiry_bucket": bucket,
                        "regime_label": regime_label,
                        "zscore_mid": z_mid,
                        "zscore_worst": z_worst,
                        "persistence": persistence,
                        "worst_pass": worst_pass,
                        "tradable": tradable,
                    }
                )

                if not worst_pass:
                    continue

                alert = {
                    "alert_type": alert_type,
                    "expiry_bucket": bucket,
                    "expiry": entry["expiry"],
                    "tier": tier,
                    "regime_label": regime_label,
                    "zscore_mid": z_mid,
                    "zscore_worst": z_worst,
                    "persistence": persistence,
                    "tradability_score": self._tradability_score(bucket),
                    "tradable": tradable,
                }
                alerts.append(alert)
                if self.run_trade_validation:
                    self.validation_snapshots_run += 1
        return alerts

    def _record_signal(self, signal: dict) -> None:
        self.signal_log.append(signal)
        day = signal["ts"].date()
        stats = self.candidate_days.setdefault(
            day,
            {"count": 0, "max_abs_z": 0.0, "worst_pass_count": 0, "tradable_count": 0},
        )
        stats["count"] += 1
        stats["max_abs_z"] = max(stats["max_abs_z"], abs(signal["zscore_mid"]))
        if signal["worst_pass"]:
            stats["worst_pass_count"] += 1
        if signal["tradable"]:
            stats["tradable_count"] += 1

    def _is_alert_tradable(self, alert: dict, quotes: list[ContractQuote], spot: float) -> bool:
        if alert["tradability_score"] <= 0:
            return False
        return bool(self._select_trade_legs(alert, quotes, spot))

    def _infer_regime(self, metrics: list[dict]) -> str:
        atm_values = [row["atm_iv_mid"] for row in metrics if row.get("atm_iv_mid") is not None]
        if not atm_values:
            return "Neutral"
        avg_atm = sum(atm_values) / len(atm_values)
        if avg_atm >= 0.30:
            return "Stress"
        if avg_atm <= 0.18:
            return "Calm"
        return "Transition"

    def _tradability_score(self, bucket: str) -> float:
        metric = self.current_metrics.get(bucket)
        if not metric:
            return 0.0
        expiry = metric["expiry"]
        chain = self._get_current_chain(self._last_slice)
        if chain is None:
            return 0.0

        spreads = []
        for contract in chain:
            if contract.expiry.date() != expiry:
                continue
            bid = float(contract.bid_price)
            ask = float(contract.ask_price)
            mid = 0.5 * (bid + ask) if bid + ask > 0 else 0.0
            if mid <= 0:
                continue
            spreads.append((ask - bid) / mid)

        if not spreads:
            return 0.0
        good = sum(1 for spread in spreads if spread <= self.spread_gate_pct)
        return good / len(spreads)

    def _open_new_trades(self, quotes: list[ContractQuote], spot: float) -> None:
        if len(self.open_trades) >= self.max_open_trades:
            return

        occupied_buckets = {trade.expiry_bucket for trade in self.open_trades.values()}
        for alert in self.current_alerts:
            if alert["expiry_bucket"] in occupied_buckets:
                continue
            if not alert.get("tradable", False):
                self.trades_skipped += 1
                continue

            legs = self._select_trade_legs(alert, quotes, spot)
            if not legs:
                self.trades_skipped += 1
                continue

            entry_value = sum(leg.quantity * leg.entry_price for leg in legs)
            self.trade_counter += 1
            trade = VirtualTrade(
                trade_id=self.trade_counter,
                alert_type=alert["alert_type"],
                expiry_bucket=alert["expiry_bucket"],
                entered_at=self.time,
                regime_label=alert["regime_label"],
                zscore_mid=alert["zscore_mid"],
                zscore_worst=alert["zscore_worst"],
                tradability_score=alert["tradability_score"],
                legs=legs,
                entry_value=entry_value,
            )
            self.open_trades[trade.trade_id] = trade
            self.trades_opened += 1
            self.log(
                f"ENTER trade_id={trade.trade_id} alert={trade.alert_type} bucket={trade.expiry_bucket} "
                f"entry={entry_value:.2f} regime={trade.regime_label} z={trade.zscore_worst:.2f}"
            )

    def _select_trade_legs(self, alert: dict, quotes: list[ContractQuote], spot: float) -> list[StrategyLeg]:
        if alert["alert_type"] == "RR_EXTREME":
            expiry = alert["expiry"]
            short_put = self._select_contract(quotes, expiry, "P", -0.25, spot)
            long_put = self._select_contract(quotes, expiry, "P", -0.10, spot)
            if not short_put or not long_put:
                return []
            return self._build_legs(
                [
                    (short_put, -1),
                    (long_put, 1),
                ]
            )

        if alert["alert_type"] == "FLY_EXTREME":
            expiry = alert["expiry"]
            wing_put = self._select_contract(quotes, expiry, "P", -0.25, spot)
            body_put = self._select_contract(quotes, expiry, "P", -0.50, spot)
            tail_put = self._select_contract(quotes, expiry, "P", -0.10, spot)
            if not wing_put or not body_put or not tail_put:
                return []
            return self._build_legs(
                [
                    (wing_put, 1),
                    (body_put, -2),
                    (tail_put, 1),
                ]
            )

        if alert["alert_type"] == "TERM_KINK":
            front_expiry, back_expiry = self._calendar_expiries(quotes, alert["expiry_bucket"])
            if front_expiry is None or back_expiry is None:
                return []
            front_call = self._select_contract(quotes, front_expiry, "C", 0.50, spot)
            back_call = self._select_contract(quotes, back_expiry, "C", 0.50, spot)
            if not front_call or not back_call:
                return []
            if abs(front_call.strike - back_call.strike) > 5:
                common = self._select_common_strike_calendar(quotes, front_expiry, back_expiry, spot)
                if not common:
                    return []
                front_call, back_call = common
            return self._build_legs(
                [
                    (front_call, -1),
                    (back_call, 1),
                ]
            )

        return []

    def _build_legs(self, spec: list[tuple[ContractQuote, int]]) -> list[StrategyLeg]:
        legs: list[StrategyLeg] = []
        for quote, qty in spec:
            if quote.open_interest < self.min_open_interest:
                return []
            price = quote.ask if qty > 0 else quote.bid
            mid = 0.5 * (quote.bid + quote.ask) if quote.bid + quote.ask > 0 else 0.0
            if price <= 0 or mid <= 0:
                return []
            if (quote.ask - quote.bid) / mid > self.spread_gate_pct:
                return []
            legs.append(
                StrategyLeg(
                    symbol=quote.symbol,
                    quantity=qty,
                    right=quote.right,
                    expiry=quote.expiry,
                    strike=quote.strike,
                    entry_price=price,
                )
            )
        return legs

    def _calendar_expiries(self, quotes: list[ContractQuote], bucket: str) -> tuple[date | None, date | None]:
        bucket_days = int(bucket.replace("D", ""))
        expiries = sorted({quote.expiry for quote in quotes})
        front = None
        back = None
        for expiry in expiries:
            dte = (expiry - self.time.date()).days
            if self.dte_min <= dte <= min(bucket_days, 30):
                front = expiry if front is None or abs(dte - bucket_days) < abs((front - self.time.date()).days - bucket_days) else front
            if max(bucket_days, 30) <= dte <= self.dte_max:
                back = expiry if back is None or dte < (back - self.time.date()).days else back
        return front, back

    def _select_common_strike_calendar(
        self,
        quotes: list[ContractQuote],
        front_expiry: date,
        back_expiry: date,
        spot: float,
    ) -> tuple[ContractQuote, ContractQuote] | None:
        front_calls = [quote for quote in quotes if quote.expiry == front_expiry and quote.right == "C"]
        back_calls = [quote for quote in quotes if quote.expiry == back_expiry and quote.right == "C"]
        back_by_strike = {quote.strike: quote for quote in back_calls}
        shared = [quote for quote in front_calls if quote.strike in back_by_strike]
        if not shared:
            return None
        front = min(shared, key=lambda quote: abs(quote.strike - spot))
        return front, back_by_strike[front.strike]

    def _select_contract(
        self,
        quotes: list[ContractQuote],
        expiry: date,
        right: str,
        target_delta: float,
        spot: float,
    ) -> ContractQuote | None:
        rate = 0.0
        div = 0.0
        t_years = max((expiry - self.time.date()).days, 0) / 365.0
        if t_years <= 0:
            return None

        candidates = []
        for quote in quotes:
            if quote.expiry != expiry or quote.right != right:
                continue
            mid = 0.5 * (quote.bid + quote.ask) if quote.bid + quote.ask > 0 else 0.0
            if mid <= 0:
                continue
            iv = _solve_iv(mid, spot, quote.strike, rate, div, t_years, right)
            if iv is None:
                continue
            delta = _bs_delta(spot, quote.strike, rate, div, t_years, iv, right)
            candidates.append((abs(delta - target_delta), quote))

        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _manage_open_trades(self, quotes: list[ContractQuote]) -> None:
        if not self.open_trades:
            return

        quote_map = {quote.symbol: quote for quote in quotes}
        to_close: list[int] = []

        for trade_id, trade in self.open_trades.items():
            age = self.time - trade.entered_at
            current_metric = self.current_metrics.get(trade.expiry_bucket)
            should_exit = age >= timedelta(days=self.max_hold_days)
            if current_metric is not None:
                metric_name = {
                    "RR_EXTREME": "rr25_mid",
                    "FLY_EXTREME": "fly25_mid",
                    "TERM_KINK": "term_slope_mid",
                }[trade.alert_type]
                z_now = self._latest_zscore(trade.expiry_bucket, metric_name, current_metric.get(metric_name))
                if z_now is not None and abs(z_now) <= self.exit_z_threshold:
                    should_exit = True

            if not should_exit:
                continue

            exit_value = 0.0
            missing_quote = False
            for leg in trade.legs:
                quote = quote_map.get(leg.symbol)
                if quote is None:
                    missing_quote = True
                    break
                exit_price = quote.bid if leg.quantity > 0 else quote.ask
                if exit_price <= 0:
                    missing_quote = True
                    break
                exit_value += -leg.quantity * exit_price

            if missing_quote:
                continue

            pnl = exit_value + trade.entry_value
            self.closed_trades.append(
                {
                    "trade_id": trade.trade_id,
                    "alert_type": trade.alert_type,
                    "expiry_bucket": trade.expiry_bucket,
                    "entry_time": trade.entered_at,
                    "exit_time": self.time,
                    "entry_value": trade.entry_value,
                    "exit_value": exit_value,
                    "pnl": pnl,
                    "days_held": age.days,
                }
            )
            self.log(
                f"EXIT trade_id={trade.trade_id} alert={trade.alert_type} bucket={trade.expiry_bucket} "
                f"pnl={pnl:.2f} held_days={age.days}"
            )
            to_close.append(trade_id)

        for trade_id in to_close:
            self.open_trades.pop(trade_id, None)

    def _latest_zscore(self, bucket: str, metric_name: str, current_value: float | None) -> float | None:
        if current_value is None:
            return None
        history = self.metric_history[(bucket, metric_name)]
        if len(history) < 20:
            return None
        mean = sum(history) / len(history)
        variance = sum((x - mean) ** 2 for x in history) / max(len(history) - 1, 1)
        std = math.sqrt(variance)
        if std == 0:
            return None
        return (current_value - mean) / std

    def _scheduled_report(self) -> None:
        worst_pass_rate = self.signal_worst_passed / self.signal_mid_passed if self.signal_mid_passed else 0.0
        tradable_rate = self.signal_tradable / self.signal_worst_passed if self.signal_worst_passed else 0.0
        conversion_rate = self.trades_opened / self.signal_mid_passed if self.signal_mid_passed else 0.0
        closed = len(self.closed_trades)
        avg_pnl = sum(trade["pnl"] for trade in self.closed_trades) / closed if closed else 0.0
        self.plot("Validator", "SignalsMidPassed", self.signal_mid_passed)
        self.plot("Validator", "SignalsWorstPassed", self.signal_worst_passed)
        self.plot("Validator", "SignalsTradable", self.signal_tradable)
        self.plot("Validator", "WorstPassRate", worst_pass_rate)
        self.plot("Validator", "TradableRate", tradable_rate)
        self.plot("Validator", "ConversionRate", conversion_rate)
        self.plot("Validator", "OpenTrades", len(self.open_trades))
        self.plot("Validator", "ClosedTrades", closed)
        self.plot("Validator", "AvgPnL", avg_pnl)

    def on_end_of_algorithm(self) -> None:
        worst_pass_rate = self.signal_worst_passed / self.signal_mid_passed if self.signal_mid_passed else 0.0
        tradable_rate = self.signal_tradable / self.signal_worst_passed if self.signal_worst_passed else 0.0
        conversion_rate = self.trades_opened / self.signal_mid_passed if self.signal_mid_passed else 0.0
        closed = len(self.closed_trades)
        avg_pnl = sum(trade["pnl"] for trade in self.closed_trades) / closed if closed else 0.0
        winners = sum(1 for trade in self.closed_trades if trade["pnl"] > 0)
        win_rate = winners / closed if closed else 0.0
        top_days = sorted(
            self.candidate_days.items(),
            key=lambda item: (item[1]["tradable_count"], item[1]["max_abs_z"], item[1]["count"]),
            reverse=True,
        )[: min(5, len(self.candidate_days))]
        if top_days:
            self.log(
                "CANDIDATE_DAYS " +
                ",".join(
                    f"{day.isoformat()}|tradable={stats['tradable_count']}|worst={stats['worst_pass_count']}|maxz={stats['max_abs_z']:.2f}"
                    for day, stats in top_days
                )
            )
        self.log(
            "SUMMARY "
            f"mode={self.research_mode} "
            f"signals_mid_passed={self.signal_mid_passed} "
            f"signals_worst_passed={self.signal_worst_passed} "
            f"signals_tradable={self.signal_tradable} "
            f"worst_pass_rate={worst_pass_rate:.2%} "
            f"tradable_rate={tradable_rate:.2%} "
            f"conversion_rate={conversion_rate:.2%} "
            f"open_trades={len(self.open_trades)} "
            f"closed_trades={closed} "
            f"trades_opened={self.trades_opened} "
            f"win_rate={win_rate:.2%} "
            f"avg_pnl={avg_pnl:.2f} "
            f"skipped={self.trades_skipped} "
            f"evaluations={self.evaluations_run} "
            f"validation_snapshots={self.validation_snapshots_run}"
        )
