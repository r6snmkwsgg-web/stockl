#!/usr/bin/env python3
"""Point out structurally strong stocks that are in a big dip right now.

Usage:
    python scan_dips.py                  # download fresh data first
    python scan_dips.py --no-download    # use data on disk
    python scan_dips.py --min-dip 0.15   # at least 15% below the 52-week high

"Structurally strong" here is judged from price only (no fundamentals):
  * 3-year return better than SPY's 3-year return, and
  * 200-day moving average higher than it was 6 months ago.
"Big dip": close at least --min-dip below the 52-week high (default 20%).

This is a research tool, not advice. See RESEARCH_DIPS.md for what happened
after such dips in the past, and why the numbers are probably too rosy.
"""
import argparse
from pathlib import Path

import pandas as pd

from swing import data
from swing.control_universe import FALLEN
from swing.universe import ALL_TICKERS, MARKET, STOCKS

ap = argparse.ArgumentParser()
ap.add_argument("--min-dip", type=float, default=0.20)
ap.add_argument("--no-download", action="store_true")
ap.add_argument("--include-control", action="store_true", help="also scan the fallen/lagging control list")
args = ap.parse_args()

if not args.no_download:
    print("Downloading fresh prices ...")
    data.download_all(ALL_TICKERS, source="auto", verbose=False)

prices = data.load_all(ALL_TICKERS)
if args.include_control and Path("data/control").exists():
    data.DATA_DIR = Path("data/control")
    prices.update(data.load_all(FALLEN))
spy = prices[MARKET]["Close"]
spy3y = spy.iloc[-1] / spy.iloc[-757] - 1

rows = []
for t, d in prices.items():
    if t == MARKET or len(d) < 760:
        continue
    c = d["Close"]
    sma200 = c.rolling(200).mean()
    hi252 = d["High"].rolling(252).max()
    ret3y = c.iloc[-1] / c.iloc[-757] - 1
    rising = sma200.iloc[-1] > sma200.iloc[-127]
    dd = c.iloc[-1] / hi252.iloc[-1] - 1
    days_since_high = 251 - int(d["High"].iloc[-252:].to_numpy().argmax())
    if ret3y > spy3y and rising and dd <= -args.min_dip:
        rows.append(dict(ticker=t, close=c.iloc[-1], high52=hi252.iloc[-1], dip=dd,
                         days_since_high=days_since_high, ret3y=ret3y, spy3y=spy3y,
                         vs_sma200=c.iloc[-1] / sma200.iloc[-1] - 1,
                         ret20=c.iloc[-1] / c.iloc[-21] - 1))

print(f"Data as of the close on {spy.index[-1].date()}. SPY 3-year return {spy3y:+.0%}.")
if not rows:
    print(f"No structurally strong stock is {args.min_dip:.0%}+ below its 52-week high right now.")
else:
    df = pd.DataFrame(rows).sort_values("dip")
    print(f"{len(df)} structurally strong stock(s) at least {args.min_dip:.0%} below their 52-week high:\n")
    for _, r in df.iterrows():
        print(f"{r.ticker:6s} close {r.close:9.2f} | {r.dip:+.0%} from 52w high {r.high52:.2f} "
              f"({r.days_since_high} trading days ago) | 3-yr return {r.ret3y:+.0%} vs SPY {r.spy3y:+.0%} "
              f"| {r.vs_sma200:+.0%} vs 200-day avg | last 20 days {r.ret20:+.0%}")
    print("\nWhat happened historically after such dips is in RESEARCH_DIPS.md. Check the news and the\n"
          "earnings before assuming the dip is temporary: the control group shows many were not.")
