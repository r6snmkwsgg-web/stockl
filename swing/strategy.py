"""The trading rules, turned into True/False columns.

Nothing in here looks at the account or other stocks. It only answers, for one
stock on one day: "does this day pass the stock filter?" and "is this a setup?"
The portfolio-level rules (market filter, position limits, sizing) live in
backtest.py.
"""
from __future__ import annotations

import pandas as pd

# ---- Rule 2: stock filter ---------------------------------------------------
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500_000
NEAR_HIGH_PCT = 0.25      # within 25% of the 52-week high
ABOVE_LOW_PCT = 0.30      # at least 30% above the 52-week low

# ---- Rule 3: setup ----------------------------------------------------------
PULLBACK_MIN_DAYS = 3
PULLBACK_MAX_DAYS = 8
EMA_TOUCH_PCT = 0.01      # the low must come within 1% of the 20-day EMA
RSI_LOW, RSI_HIGH = 40, 60

# ---- Rule 5: stop -----------------------------------------------------------
ATR_STOP_MULT = 2.0
MAX_STOP_PCT = 0.08       # skip the trade if the stop is more than 8% away
STOP_BUFFER = 0.001       # "just below" the pullback low = 0.1% below it

# ---- Rule 7: exits ----------------------------------------------------------
PARTIAL_TARGET_R = 2.0    # sell half at +2R
TIME_STOP_DAYS = 10       # after 10 trading days ...
TIME_STOP_MIN_R = 1.0     # ... the trade must be at least +1R, or we exit

# ---- Rule 1: market filter --------------------------------------------------
MARKET_SMA = 200


def stock_filter(d: pd.DataFrame) -> pd.Series:
    """Rule 2. True on days when the stock is in a healthy long-term uptrend."""
    c = d["Close"]
    return (
        (c > d["sma50"]) & (c > d["sma150"]) & (c > d["sma200"])
        & (d["sma200"] > d["sma200_20ago"])
        & (c >= d["hi52"] * (1 - NEAR_HIGH_PCT))
        & (c >= d["lo52"] * (1 + ABOVE_LOW_PCT))
        & (d["avgvol50"] > MIN_AVG_VOLUME)
        & (c > MIN_PRICE)
    )


def setup(d: pd.DataFrame) -> pd.Series:
    """Rule 3. True on days when the stock has pulled back to its 20-day EMA."""
    c, low, e20 = d["Close"], d["Low"], d["ema20"]
    return (
        d["days_since_high"].between(PULLBACK_MIN_DAYS, PULLBACK_MAX_DAYS)
        & (c < d["swing_high"])                       # it really is a pullback
        & (low <= e20 * (1 + EMA_TOUCH_PCT))          # low came within 1% of the EMA
        & (c >= e20 * (1 - EMA_TOUCH_PCT))            # but did not close well below it
        & (e20 > d["sma50"])                          # 20 EMA still above 50 SMA
        & d["rsi14"].between(RSI_LOW, RSI_HIGH)
    )


def market_ok(spy: pd.DataFrame) -> pd.Series:
    """Rule 1. True when SPY closed above its 200-day simple moving average."""
    return spy["Close"] > spy["Close"].rolling(MARKET_SMA, min_periods=MARKET_SMA).mean()


def add_signals(d: pd.DataFrame) -> pd.DataFrame:
    d = d.copy()
    d["filter_ok"] = stock_filter(d)
    d["setup"] = d["filter_ok"] & setup(d)
    return d


def plan_trade(entry: float, pullback_low: float, atr14: float):
    """Rules 5. Given an entry price, return (stop, risk_per_share) or None.

    The stop is the CLOSER of: just below the pullback low, or 2 x ATR below
    entry. If that stop is more than 8% below the entry, the trade is skipped.
    """
    stop_low = pullback_low * (1 - STOP_BUFFER)
    stop_atr = entry - ATR_STOP_MULT * atr14
    stop = max(stop_low, stop_atr)
    if stop >= entry:
        return None
    risk = entry - stop
    if risk / entry > MAX_STOP_PCT:
        return None
    return stop, risk
