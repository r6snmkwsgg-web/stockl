"""Technical indicators, written to be easy to read.

All functions take a price DataFrame with columns Open, High, Low, Close, Volume
and return a new DataFrame with extra indicator columns added.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

TRADING_DAYS_PER_YEAR = 252


def sma(series: pd.Series, n: int) -> pd.Series:
    """Simple moving average: the plain average of the last n values."""
    return series.rolling(n, min_periods=n).mean()


def ema(series: pd.Series, n: int) -> pd.Series:
    """Exponential moving average: like an average, but recent days count more."""
    return series.ewm(span=n, adjust=False, min_periods=n).mean()


def rsi(close: pd.Series, n: int = 14) -> pd.Series:
    """Relative Strength Index (Wilder's version, 0-100).

    Above 70 usually means 'stretched up', below 30 'stretched down'.
    40-60 means the stock is resting, neither overbought nor oversold.
    """
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    avg_loss = loss.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out = 100 - 100 / (1 + rs)
    return out.fillna(100).where(avg_loss.notna())


def atr(df: pd.DataFrame, n: int = 14) -> pd.Series:
    """Average True Range: how much the stock typically moves in a day (in $)."""
    prev_close = df["Close"].shift(1)
    tr = pd.concat([
        df["High"] - df["Low"],
        (df["High"] - prev_close).abs(),
        (df["Low"] - prev_close).abs(),
    ], axis=1).max(axis=1)
    return tr.ewm(alpha=1 / n, adjust=False, min_periods=n).mean()


def add_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """Add every indicator the strategy needs."""
    d = df.copy()
    c = d["Close"]
    d["sma50"] = sma(c, 50)
    d["sma150"] = sma(c, 150)
    d["sma200"] = sma(c, 200)
    d["sma200_20ago"] = d["sma200"].shift(20)
    d["ema20"] = ema(c, 20)
    d["rsi14"] = rsi(c, 14)
    d["rsi2"] = rsi(c, 2)                      # very short-term "oversold" gauge
    d["sma5"] = sma(c, 5)
    d["low5"] = d["Low"].rolling(5, min_periods=5).min()   # for a trailing stop
    d["atr14"] = atr(d, 14)
    d["hi52"] = d["High"].rolling(TRADING_DAYS_PER_YEAR, min_periods=TRADING_DAYS_PER_YEAR).max()
    d["lo52"] = d["Low"].rolling(TRADING_DAYS_PER_YEAR, min_periods=TRADING_DAYS_PER_YEAR).min()
    d["avgvol50"] = d["Volume"].rolling(50, min_periods=50).mean()
    d["ret126"] = c / c.shift(126) - 1          # 6-month return, used to rank candidates

    # Pullback bookkeeping: how many days since the highest high of the last 15
    # days, and the lowest low since that high (the "pullback low").
    win = 15
    hi = d["High"].to_numpy()
    lo = d["Low"].to_numpy()
    n = len(d)
    days_since = np.full(n, np.nan)
    swing_high = np.full(n, np.nan)
    pull_low = np.full(n, np.nan)
    for i in range(win - 1, n):
        seg = hi[i - win + 1:i + 1]
        j = int(np.argmax(seg))           # position of the swing high inside the window
        k = win - 1 - j                   # days since that swing high (0 = today)
        days_since[i] = k
        swing_high[i] = seg[j]
        pull_low[i] = lo[i - k:i + 1].min() if k > 0 else lo[i]
    d["days_since_high"] = days_since
    d["swing_high"] = swing_high
    d["pullback_low"] = pull_low
    return d
