"""The scoring formula: "strong company, cheap price, sensible timing".

For every stock and every day we compute a set of features, then score each
stock against the others on the same day (percentile ranks, 0 = worst,
100 = best). Three groups:

  QUALITY  (70%)  Is this a good business?     return on equity, free-cash-flow
                                               margin, revenue growth, 3-year
                                               share-price record vs SPY, rising
                                               200-day trend.
  VALUE    (20%)  Is the price low?            P/E and P/S versus the stock's OWN
                                               5-year history (is it cheaper than
                                               it usually is?), earnings yield and
                                               free-cash-flow yield versus peers.
  TIMING   (10%)  Is now a sensible moment?    size of the pull-back from the
                                               52-week high (a sale), whether the
                                               high was recent, and whether the
                                               price is still near its 200-day
                                               average (not a collapsing stock).

Red flags are shown on the site but do not change the score. Some conditions
make a stock ineligible altogether (losing money, stale data, too illiquid).

Why these weights: the first version (35/40/25 with flag penalties) was tested
point-in-time on 2012-2025 and its top picks did WORSE than the average stock.
Only the quality component ranked future returns in both halves of the data;
cheapness and dip-depth ranked them backwards. See results/score_backtest_v1.md
and RESEARCH_SCORE.md. The weights above follow that evidence.

Financial companies (banks, insurers, exchanges) are scored on earnings,
book value and return on equity instead of cash flow, which is meaningless
for a bank.

There is no formula that "finds the perfect stock". This one is transparent
so you can see WHY a stock ranks where it does, and it is backtested
(backtest_score.py) so you know how often its top picks actually beat SPY.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from .data import load_events
from .fundamentals import pit_frame
from .indicators import add_indicators
from .universe import FINANCIAL, SECTORS

WEIGHTS = {"quality": 0.70, "value": 0.20, "timing": 0.10}
FLAG_PENALTY = 0          # flags are shown, not scored (the record says penalising them hurt)
MIN_PRICE = 10.0
MIN_AVG_VOLUME = 500_000
STALE_DAYS = 135          # no new filing for this long = data is stale


# --------------------------------------------------------------------------- features
NOT_SCORED = {"BRK-B": "Berkshire's reported profit swings with the market value of its investments, "
                       "so earnings-based measures are meaningless for it."}


def features(ticker: str, px: pd.DataFrame, calendar: pd.DatetimeIndex, spy: pd.Series) -> pd.DataFrame | None:
    """Daily feature table for one stock (fundamentals are point-in-time)."""
    if ticker in NOT_SCORED:
        return None
    f = pit_frame(ticker, calendar)
    if f is None:
        return None
    d = add_indicators(px).reindex(calendar)
    c = d["Close"]
    # Prices are split-adjusted. For the $10 and volume rules we need what actually traded:
    # real price = adjusted price x every split that came AFTER that day.
    fac = pd.Series(1.0, index=calendar)
    for sd, ratio in load_events(ticker).get("splits", []):
        fac[calendar < pd.Timestamp(sd)] *= ratio
    out = pd.DataFrame(index=calendar)
    out["price_real"] = c * fac
    out["avgvol_real"] = d["avgvol50"] / fac
    out["ticker"] = ticker
    out["sector"] = SECTORS.get(ticker, "Other")
    out["financial"] = ticker in FINANCIAL
    out["close"] = c
    out["avgvol50"] = d["avgvol50"]
    out["mcap"] = c * f["shares"]
    ni, rev, fcf, eq = f["net_income_ttm"], f["revenue_ttm"], f["fcf_ttm"], f["equity"]
    out["revenue_ttm"], out["net_income_ttm"], out["fcf_ttm"] = rev, ni, fcf
    out["op_income_ttm"] = f["op_income_ttm"]
    out["ni_pos_quarters"] = f["ni_pos_quarters"]
    # "Core" profit: net income, but never more than after-tax operating profit.
    # Guards against one-off windfalls (e.g. a gain on an investment) making a
    # stock look cheap on P/E. Financial companies have no operating income line.
    core = ni.where(f["op_income_ttm"].isna() | (ticker in FINANCIAL),
                    pd.concat([ni, f["op_income_ttm"] * 0.79], axis=1).min(axis=1))
    out["core_income_ttm"] = core
    out["windfall"] = (ni > 1.5 * f["op_income_ttm"] * 0.79) & f["op_income_ttm"].notna() & (ticker not in FINANCIAL)
    out["equity"], out["debt"], out["cash"] = eq, f["debt"], f["cash"]
    out["pe"] = (out["mcap"] / core).where(core > 0)
    out["pe_reported"] = (out["mcap"] / ni).where(ni > 0)
    out["ps"] = (out["mcap"] / rev).where(rev > 0)
    out["pb"] = (out["mcap"] / eq).where(eq > 0)
    out["earnings_yield"] = core / out["mcap"]
    out["fcf_yield"] = fcf / out["mcap"]
    out["roe"] = (ni / eq).where(eq > 0)
    out["net_margin"] = (ni / rev).where(rev > 0)
    out["fcf_margin"] = (fcf / rev).where(rev > 0)
    out["rev_growth"] = (rev / f["revenue_ttm_1y"] - 1).where(f["revenue_ttm_1y"] > 0)
    out["ni_growth"] = (ni / f["net_income_ttm_1y"] - 1).where(f["net_income_ttm_1y"] > 0)
    out["debt_to_equity"] = (f["debt"] / eq).where(eq > 0)
    # valuation versus the stock's own last 5 years (percentile: 0.10 = cheaper than 90% of its history)
    out["pe_pct_5y"] = out["pe"].rolling(1260, min_periods=504).rank(pct=True)
    out["ps_pct_5y"] = out["ps"].rolling(1260, min_periods=504).rank(pct=True)
    out["pb_pct_5y"] = out["pb"].rolling(1260, min_periods=504).rank(pct=True)
    # price behaviour
    out["dd52"] = c / d["hi52"] - 1
    out["fresh"] = d["High"].rolling(60).max() >= d["hi52"] * 0.999
    out["days_since_high"] = d["days_since_high"]
    out["above_200"] = c / d["sma200"] - 1
    out["sma200_rising"] = d["sma200"] > d["sma200"].shift(126)
    out["ret3y_vs_spy"] = (c / c.shift(756) - 1) - (spy / spy.shift(756) - 1)
    out["ret1y"] = c / c.shift(252) - 1
    out["ret20"] = c / c.shift(20) - 1
    out["rsi14"] = d["rsi14"]
    out["vol60"] = np.log(c).diff().rolling(60).std() * np.sqrt(252)
    # staleness: days since the trailing net income last changed (a new filing)
    changed = ni.ne(ni.shift(1)) & ni.notna()
    last_change = pd.Series(np.where(changed, np.arange(len(calendar)), np.nan), index=calendar).ffill()
    out["days_since_filing"] = np.arange(len(calendar)) - last_change
    return out


def _pct(s: pd.Series) -> pd.Series:
    """Percentile rank across stocks, 0..100 (NaN stays NaN)."""
    return s.rank(pct=True) * 100


def _clip100(s):
    return s.clip(0, 100)


# --------------------------------------------------------------------------- scoring
def score_day(rows: pd.DataFrame) -> pd.DataFrame:
    """Score every stock on one day. `rows` has one row per ticker."""
    r = rows.copy()
    fin = r["financial"].astype(bool)

    # eligibility (hard filters)
    ok = ((r["net_income_ttm"] > 0) & (r["revenue_ttm"] > 0) & r["mcap"].notna()
          & (r["price_real"] > MIN_PRICE) & (r["avgvol_real"] > MIN_AVG_VOLUME)
          & (r["days_since_filing"] <= STALE_DAYS)
          & (fin | (r["fcf_ttm"] > 0)))
    r["eligible"] = ok.fillna(False)

    # --- quality
    profit_metric = r["net_margin"].where(fin, r["fcf_margin"])
    q_parts = pd.concat([
        _pct(r["roe"].clip(-1, 1)),
        _pct(profit_metric.clip(-1, 1)),
        _pct(r["rev_growth"].clip(-0.5, 1.0)),
        _pct(r["ret3y_vs_spy"].clip(-2, 5)),
        r["sma200_rising"].astype(float) * 100,
    ], axis=1)
    r["quality"] = _clip100(q_parts.mean(axis=1, skipna=True)
                            - np.where((~fin) & (r["debt_to_equity"] > 2), 15, 0))

    # --- value
    own_pe = (1 - r["pe_pct_5y"]) * 100
    own_ps = (1 - r["ps_pct_5y"]) * 100
    own_pb = (1 - r["pb_pct_5y"]) * 100
    cash_metric = _pct(r["fcf_yield"].clip(-0.3, 0.3)).where(~fin, _pct((1 / r["pb"]).clip(0, 3)))
    v_parts = pd.concat([
        own_pe, own_ps.where(~fin, own_pb),
        _pct(r["earnings_yield"].clip(-0.3, 0.3)),
        cash_metric,
    ], axis=1)
    r["value"] = _clip100(v_parts.mean(axis=1, skipna=True))

    # --- timing
    dip = (-r["dd52"] / 0.30).clip(0, 1) * 100 + r["fresh"].astype(float) * 15
    trend = np.where(r["above_200"] >= 0, 100, 100 + r["above_200"] * 500)
    trend = pd.Series(trend, index=r.index).clip(0, 100)
    rsi_pen = np.where(r["rsi14"] > 70, 20, 0)
    r["timing"] = _clip100(0.6 * dip.clip(0, 100) + 0.4 * trend - rsi_pen)

    # --- red flags
    flags = {
        "losing money (last 12 months)": r["net_income_ttm"] <= 0,
        "one big loss quarter": (r["net_income_ttm"] <= 0) & (r["ni_pos_quarters"] >= 3),
        "profit boosted by one-off gains": r["windfall"],
        "negative free cash flow": (~fin) & (r["fcf_ttm"] <= 0),
        "revenue shrinking >10%": r["rev_growth"] < -0.10,
        "profit shrinking >25%": r["ni_growth"] < -0.25,
        "heavy debt (debt > 2x equity)": (~fin) & (r["debt_to_equity"] > 2),
        "very volatile (>60%/yr)": r["vol60"] > 0.60,
        ">20% below 200-day average": r["above_200"] < -0.20,
        "expensive (P/E > 50)": r["pe"] > 50,
        "priced above its 5-year norm (P/E top 20%)": r["pe_pct_5y"] > 0.80,
        "stale filings": r["days_since_filing"] > STALE_DAYS,
        "thin trading (<500k shares/day)": r["avgvol_real"] < MIN_AVG_VOLUME,
        "short price history (<3 years)": r["ret3y_vs_spy"].isna(),
    }
    flag_df = pd.DataFrame({k: v.fillna(False).astype(bool) for k, v in flags.items()})
    r["flags"] = flag_df.apply(lambda row: [k for k, v in row.items() if v], axis=1)
    r["n_flags"] = flag_df.sum(axis=1)

    r["score"] = _clip100(WEIGHTS["quality"] * r["quality"] + WEIGHTS["value"] * r["value"]
                          + WEIGHTS["timing"] * r["timing"] - FLAG_PENALTY * r["n_flags"])
    r["eligible"] &= r["score"].notna()
    r.loc[~r["eligible"], "score"] = np.nan
    return r


def build_features(prices: dict, tickers, calendar: pd.DatetimeIndex, spy: pd.Series, verbose=False) -> dict:
    feats = {}
    for t in tickers:
        if t not in prices:
            continue
        f = features(t, prices[t], calendar, spy)
        if f is not None:
            feats[t] = f
        elif verbose:
            print("no fundamentals:", t)
    return feats


def cross_section(feats: dict, date) -> pd.DataFrame:
    rows = []
    for t, f in feats.items():
        if date in f.index:
            rows.append(f.loc[date])
    if not rows:
        return pd.DataFrame()
    return score_day(pd.DataFrame(rows).set_index("ticker", drop=False))
