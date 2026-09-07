#!/usr/bin/env python3
"""Swing trading the best businesses: the 'buy the dip, sell the bounce' rule
(RSI(2) below 10 in an uptrend, buy next open, sell at the next close above the
5-day average or after 10 days, 2xATR stop) applied ONLY to stocks whose
quality score is in the top 30% on the day. About 40-90 trades a year.
Run with no costs and with 0.1% slippage per side, split into two halves.
"""
from dataclasses import replace
from pathlib import Path

import numpy as np
import pandas as pd

from swing import data
from swing.backtest import Config, prepare, run
from swing.control_universe import FALLEN
from swing.metrics import summarize
from swing.score import build_features, cross_section
from swing.universe import ALL_TICKERS, MARKET

prices = data.load_all(ALL_TICKERS)
data.DATA_DIR = Path("data/control")
for t, df in data.load_all(FALLEN).items():
    prices.setdefault(t, df)
data.DATA_DIR = Path("data/prices")
cal = prices[MARKET].index
spy_close = prices[MARKET]["Close"]
feats = build_features(prices, [t for t in prices if t != MARKET], cal, spy_close)

# quality rank on every trading day (cross-sectional), then a daily boolean "top 30%"
print("scoring every day ...")
# quality is computed cross-sectionally in score_day; do it once per month-end to keep it fast, then forward-fill
month_ends = cal[cal.to_series().groupby([cal.year, cal.month]).cumcount(ascending=False) == 0]
qual = {}
for d in month_ends:
    cs = cross_section(feats, d)
    if len(cs):
        qual[d] = cs["quality"].where(cs["eligible"])
qual = pd.DataFrame(qual).T.reindex(cal).ffill()
top = qual.ge(qual.quantile(0.70, axis=1), axis=0)

spy, stocks, calendar = prepare(prices, MARKET)
for t, d in stocks.items():
    d["setup_mr"] = d["setup_mr"] & top[t].reindex(calendar).fillna(False) if t in top.columns else False
prepared = (spy, stocks, calendar)

base = Config(name="swing_quality", start_cash=10_000, risk_pct=0.01, max_positions=5, setup_mode="mean_reversion",
              entry_mode="open", stop_mode="atr", exit_rule="close_above_sma5", partial_R=None, time_stop_days=None,
              max_hold_days=10, start="2013-01-01")
rows = []
for name, kw in [("no costs", {}), ("0.1% per side", dict(slippage_pct=0.001)),
                 ("2013-18, costs", dict(slippage_pct=0.001, end="2018-12-31")), ("2019-26, costs", dict(slippage_pct=0.001, start="2019-01-01"))]:
    cfg = replace(base, **kw)
    trades, eq = run(prices, cfg, MARKET, prepared=prepared)
    s = summarize(trades, eq, cfg.start_cash)
    spy_seg = spy_close.loc[eq.index[0]:eq.index[-1]]
    spy_cagr = (spy_seg.iloc[-1] / spy_seg.iloc[0]) ** (1 / s["years"]) - 1
    rows.append(dict(run=name, trades=s["n_trades"], per_year=round(s["trades_per_year"], 1), win=s["win_rate"], avg_pct=trades["pct"].mean(),
                     exp_R=s["expectancy_R"], days=s["avg_days_held"], cagr=s["cagr"], spy_cagr=spy_cagr, maxdd=s["max_drawdown"]))
df = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(df.to_string(index=False, float_format=lambda x: f"{x:+.2%}" if abs(x) < 5 else f"{x:.1f}"))
md = ["| Run | trades | per year | win rate | avg % per trade | expectancy (R) | days held | CAGR | SPY CAGR (price) | max drawdown |", "|---|---|---|---|---|---|---|---|---|---|"]
for r in df.itertuples():
    md.append(f"| {r.run} | {r.trades} | {r.per_year} | {r.win:.0%} | {r.avg_pct:+.2%} | {r.exp_R:+.2f} | {r.days:.1f} | {r.cagr:+.1%} | {r.spy_cagr:+.1%} | {r.maxdd:.0%} |")
Path("results/swing_quality.md").write_text("# Swing trading the top-quality names: buy the dip, sell the bounce\n\n" + "\n".join(md) + "\n")
print("wrote results/swing_quality.md")
