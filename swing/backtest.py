"""Day-by-day portfolio simulation.

How a day is processed (in this order, so we never use information we would
not have had at the time):

  1. Open positions are checked against today's prices: stops, the +2R
     partial-profit target, and any exit that was decided at yesterday's close.
  2. Candidates found at YESTERDAY's close (setups) are checked: if today's
     high goes above yesterday's high, we buy (rule 4).
  3. At today's close, we look for new setups for tomorrow, and flag open
     positions that must be sold at tomorrow's open (close below the 20 EMA,
     or the 10-day time stop).

Prices used:
  * Entry: the higher of yesterday's high and today's open (a buy-stop order;
    if the stock gaps above the trigger we pay the open).
  * Stop hit: the stop price, or today's open if the stock gapped below it.
  * +2R partial: the target price, or today's open if it gapped above it.
  * "Sell at next open" exits: tomorrow's open price.
No commissions are charged. See config.slippage_pct for a simple cost model.

The Config also has "variant" switches (stop_mode, exit_rule, target_pct,
setup_mode, entry_mode ...). Their defaults reproduce the original rules
exactly; research_variants.py uses them to test rule changes.
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import strategy as S
from .indicators import add_indicators
from .strategy import add_signals, market_ok


@dataclass
class Config:
    name: str = "A"
    start_cash: float = 10_000.0
    risk_pct: float = 0.01              # risk per trade, as a fraction of equity
    max_positions: int = 5
    max_total_risk_pct: float = 0.06    # max open risk across all positions
    max_position_pct: float | None = None   # e.g. 0.40 = at most 40% of equity in one stock
    use_market_filter: bool = True
    slippage_pct: float = 0.0           # per side, e.g. 0.001 = 0.1%
    min_size_fraction: float = 0.5      # skip if cash only covers < 50% of the intended size
    start: str = "2010-01-01"
    end: str | None = None
    # ---- variant switches (defaults = the original rules) ----
    setup_mode: str = "pullback"        # "pullback" (rules as given) or "mean_reversion"
    entry_mode: str = "breakout"        # "breakout" = buy above prior high; "open" = buy next open
    stop_mode: str = "closer"           # "closer" (rule 5), "atr" (2xATR only), "pullback" (low only)
    atr_mult: float = 2.0
    max_stop_pct: float = 0.08
    partial_R: float | None = 2.0       # sell half at +NR and move stop to breakeven; None = off
    exit_rule: str = "ema_close"        # "ema_close" (rule 7), "ema_after_partial", "trail_low5",
                                        # "close_above_sma5" (mean reversion), "none"
    target_pct: float | None = None     # sell everything when the high reaches entry*(1+x)
    time_stop_days: int | None = 10     # rule 7: exit if not +1R after N days (None = off)
    time_stop_min_R: float = 1.0
    max_hold_days: int | None = None    # hard exit at the open after N days (None = off)


@dataclass
class Position:
    ticker: str
    entry_date: pd.Timestamp
    entry: float
    stop: float
    init_stop: float
    shares: int
    init_shares: int
    risk_per_share: float
    days_held: int = 0
    partial_done: bool = False
    exit_pending: str | None = None
    realized: float = 0.0
    fills: list = field(default_factory=list)   # (date, shares, price, reason)

    @property
    def init_risk_dollars(self):
        return self.init_shares * self.risk_per_share


def prepare(prices: dict[str, pd.DataFrame], market: str = "SPY"):
    """Add indicators + signals to every stock, aligned to SPY's calendar."""
    spy = add_indicators(prices[market])
    spy["market_ok"] = market_ok(spy)
    calendar = spy.index
    stocks = {}
    for t, df in prices.items():
        if t == market:
            continue
        d = add_signals(add_indicators(df))
        d = d.reindex(calendar)          # missing days (before IPO) become NaN
        for c in ("setup", "setup_mr"):
            d[c] = d[c].fillna(False).astype(bool)
        d["close_ff"] = d["Close"].ffill()   # last known close, used only to value open positions
        stocks[t] = d
    return spy, stocks, calendar


def plan_stop(cfg: Config, entry: float, pullback_low: float, atr14: float):
    """Return (stop, risk_per_share) or None if the stop would be too far away."""
    stop_low = pullback_low * (1 - S.STOP_BUFFER)
    stop_atr = entry - cfg.atr_mult * atr14
    if cfg.stop_mode == "closer":
        stop = max(stop_low, stop_atr)
    elif cfg.stop_mode == "atr":
        stop = stop_atr
    elif cfg.stop_mode == "pullback":
        stop = stop_low
    else:
        raise ValueError(cfg.stop_mode)
    if not (stop < entry):
        return None
    risk = entry - stop
    if risk / entry > cfg.max_stop_pct:
        return None
    return stop, risk


def run(prices: dict[str, pd.DataFrame], cfg: Config, market: str = "SPY",
        prepared=None):
    spy, stocks, calendar = prepared if prepared is not None else prepare(prices, market)
    start = pd.Timestamp(cfg.start)
    end = pd.Timestamp(cfg.end) if cfg.end else calendar[-1]
    days = calendar[(calendar >= start) & (calendar <= end)]

    # Pull everything into numpy for speed.
    cols = ["Open", "High", "Low", "Close", "close_ff", "ema20", "sma5", "low5", "atr14",
            "pullback_low", "ret126", "rsi2"]
    arr = {t: {c: d[c].to_numpy(dtype=float) for c in cols} for t, d in stocks.items()}
    setup_col = "setup" if cfg.setup_mode == "pullback" else "setup_mr"
    for t, d in stocks.items():
        arr[t]["setup"] = d[setup_col].to_numpy(dtype=bool)
    mkt_ok = spy["market_ok"].to_numpy(dtype=bool)
    pos_of = {dt: i for i, dt in enumerate(calendar)}
    slip = cfg.slippage_pct

    cash = cfg.start_cash
    positions: dict[str, Position] = {}
    closed: list[dict] = []
    equity_rows = []
    candidates: list[tuple[str, int]] = []     # (ticker, signal day index) found at yesterday's close

    def equity_at(i):
        return cash + sum(p.shares * arr[p.ticker]["close_ff"][i] for p in positions.values())

    def close_out(p: Position, date, shares, price, reason):
        nonlocal cash
        price = price * (1 - slip)
        cash += shares * price
        p.realized += shares * (price - p.entry)
        p.shares -= shares
        p.fills.append((date, shares, price, reason))
        if p.shares == 0:
            r = p.realized / p.init_risk_dollars
            closed.append(dict(
                version=cfg.name, ticker=p.ticker, entry_date=p.entry_date, exit_date=date,
                entry=p.entry, init_stop=p.init_stop, shares=p.init_shares,
                risk_dollars=p.init_risk_dollars, pnl=p.realized, R=r,
                pct=p.realized / (p.init_shares * p.entry),
                days_held=p.days_held, partial_taken=p.partial_done,
                exit_reason=reason,
            ))
            del positions[p.ticker]

    def rank_key(c):
        t, j = c
        if cfg.setup_mode == "mean_reversion":
            return np.nan_to_num(arr[t]["rsi2"][j], nan=99)          # most oversold first
        return -np.nan_to_num(arr[t]["ret126"][j], nan=-9)           # strongest first

    for date in days:
        i = pos_of[date]
        eq_open = equity_at(i - 1) if i > 0 else cash

        # ---- 1. manage open positions with today's prices -------------------
        for t in list(positions):
            p = positions[t]
            a = arr[t]
            o, h, l = a["Open"][i], a["High"][i], a["Low"][i]
            if np.isnan(o):
                continue
            p.days_held += 1
            if p.exit_pending:
                close_out(p, date, p.shares, o, p.exit_pending)
                continue
            # stop first (conservative: if both stop and target hit, assume stop)
            if o <= p.stop:
                close_out(p, date, p.shares, o, "stop_gap"); continue
            if l <= p.stop:
                close_out(p, date, p.shares, p.stop, "stop" if not p.partial_done else "breakeven_stop")
                continue
            if cfg.target_pct is not None:
                tgt = p.entry * (1 + cfg.target_pct)
                if h >= tgt:
                    close_out(p, date, p.shares, max(o, tgt), f"target_{cfg.target_pct:.0%}"); continue
            if cfg.partial_R is not None and not p.partial_done:
                target = p.entry + cfg.partial_R * p.risk_per_share
                if h >= target:
                    fill = max(o, target)
                    half = p.shares // 2
                    if half == 0:
                        close_out(p, date, p.shares, fill, "target_R_all"); continue
                    close_out(p, date, half, fill, "target_R_half")
                    p.partial_done = True
                    p.stop = p.entry                       # move stop to breakeven

        # ---- 2. entries from yesterday's candidates --------------------------
        if candidates:
            candidates.sort(key=rank_key)
            for t, j in candidates:
                if t in positions or len(positions) >= cfg.max_positions:
                    continue
                a = arr[t]
                o, h = a["Open"][i], a["High"][i]
                if np.isnan(o):
                    continue
                if cfg.entry_mode == "breakout":
                    trig = a["High"][j]
                    if h <= trig:
                        continue                           # did not trade above yesterday's high
                    entry = max(o, trig) * (1 + slip)
                else:
                    entry = o * (1 + slip)                 # buy at the open
                if np.isnan(a["pullback_low"][j]) or np.isnan(a["atr14"][j]):
                    continue
                plan = plan_stop(cfg, entry, a["pullback_low"][j], a["atr14"][j])
                if plan is None:
                    continue
                stop, rps = plan
                shares = math.floor(eq_open * cfg.risk_pct / rps)
                if cfg.max_position_pct:
                    shares = min(shares, math.floor(eq_open * cfg.max_position_pct / entry))
                intended = shares
                shares = min(shares, math.floor(cash / entry))      # no margin: cash only
                if shares <= 0 or shares < intended * cfg.min_size_fraction:
                    continue
                open_risk = sum(max(0.0, q.entry - q.stop) * q.shares for q in positions.values())
                if open_risk + shares * rps > cfg.max_total_risk_pct * eq_open + 1e-9:
                    continue
                cash -= shares * entry
                positions[t] = Position(t, date, entry, stop, stop, shares, shares, rps)
            candidates = []

        # ---- 3. close-of-day decisions ---------------------------------------
        for p in positions.values():
            a = arr[p.ticker]
            c = a["Close"][i]
            if np.isnan(c) or p.exit_pending:
                continue
            rule = cfg.exit_rule
            if rule == "ema_close" and c < a["ema20"][i]:
                p.exit_pending = "close_below_ema20"
            elif rule == "ema_after_partial" and p.partial_done and c < a["ema20"][i]:
                p.exit_pending = "close_below_ema20"
            elif rule == "trail_low5":
                # raise the stop to the lowest low of the last 5 days (never lower it)
                p.stop = max(p.stop, a["low5"][i])
            elif rule == "close_above_sma5" and c > a["sma5"][i]:
                p.exit_pending = "close_above_sma5"
            if p.exit_pending:
                continue
            if (cfg.time_stop_days is not None and p.days_held >= cfg.time_stop_days
                    and not p.partial_done and c < p.entry + cfg.time_stop_min_R * p.risk_per_share):
                p.exit_pending = "time_stop"
            elif cfg.max_hold_days is not None and p.days_held >= cfg.max_hold_days:
                p.exit_pending = "max_hold"

        if (not cfg.use_market_filter) or mkt_ok[i]:
            for t, a in arr.items():
                if a["setup"][i] and t not in positions:
                    candidates.append((t, i))

        equity_rows.append((date, equity_at(i), cash, len(positions)))

    # Close anything still open at the last price so the final equity is realized.
    last = pos_of[days[-1]]
    for t in list(positions):
        close_out(positions[t], days[-1], positions[t].shares, arr[t]["Close"][last], "end_of_test")

    equity = pd.DataFrame(equity_rows, columns=["date", "equity", "cash", "n_pos"]).set_index("date")
    trades = pd.DataFrame(closed)
    return trades, equity
