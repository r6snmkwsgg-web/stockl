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
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import strategy as S
from .indicators import add_indicators
from .strategy import add_signals, market_ok, plan_trade


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
        d["setup"] = d["setup"].fillna(False).astype(bool)
        d["close_ff"] = d["Close"].ffill()   # last known close, used only to value open positions
        stocks[t] = d
    return spy, stocks, calendar


def run(prices: dict[str, pd.DataFrame], cfg: Config, market: str = "SPY",
        prepared=None):
    spy, stocks, calendar = prepared if prepared is not None else prepare(prices, market)
    start = pd.Timestamp(cfg.start)
    end = pd.Timestamp(cfg.end) if cfg.end else calendar[-1]
    days = calendar[(calendar >= start) & (calendar <= end)]

    # Pull everything into numpy for speed.
    cols = ["Open", "High", "Low", "Close", "close_ff", "ema20", "atr14", "pullback_low", "ret126"]
    arr = {t: {c: d[c].to_numpy(dtype=float) for c in cols} for t, d in stocks.items()}
    for t, d in stocks.items():
        arr[t]["setup"] = d["setup"].to_numpy(dtype=bool)
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
                days_held=p.days_held, partial_taken=p.partial_done,
                exit_reason=reason,
            ))
            del positions[p.ticker]

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
            if not p.partial_done:
                target = p.entry + S.PARTIAL_TARGET_R * p.risk_per_share
                if h >= target:
                    fill = max(o, target)
                    half = p.shares // 2
                    if half == 0:
                        close_out(p, date, p.shares, fill, "target_2R_all"); continue
                    close_out(p, date, half, fill, "target_2R_half")
                    p.partial_done = True
                    p.stop = p.entry                       # move stop to breakeven

        # ---- 2. entries from yesterday's candidates --------------------------
        if candidates:
            candidates.sort(key=lambda c: -np.nan_to_num(arr[c[0]]["ret126"][c[1]], nan=-9))
            for t, j in candidates:
                if t in positions or len(positions) >= cfg.max_positions:
                    continue
                a = arr[t]
                o, h = a["Open"][i], a["High"][i]
                trig = a["High"][j]
                if np.isnan(o) or h <= trig:
                    continue                               # did not trade above yesterday's high
                entry = max(o, trig) * (1 + slip)
                if np.isnan(a["pullback_low"][j]) or np.isnan(a["atr14"][j]):
                    continue
                plan = plan_trade(entry, a["pullback_low"][j], a["atr14"][j])
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
            if c < a["ema20"][i]:
                p.exit_pending = "close_below_ema20"
            elif (p.days_held >= S.TIME_STOP_DAYS and not p.partial_done
                  and c < p.entry + S.TIME_STOP_MIN_R * p.risk_per_share):
                p.exit_pending = "time_stop_10d"

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
