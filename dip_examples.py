#!/usr/bin/env python3
"""Every 20%+ dip a few well-known "it always comes back" stocks ever had,
and what happened after each one. Writes results/dip_examples.md.

    python dip_examples.py MU PLTR MSTR SNDK
"""
import sys
from pathlib import Path

import numpy as np
import pandas as pd

from swing import data

TICKERS = sys.argv[1:] or ["MU", "PLTR", "MSTR", "SNDK"]


def load_any(t):
    for d in ["data/prices", "data/control"]:
        f = Path(d) / f"{t}.csv.gz"
        if f.exists():
            return pd.read_csv(f, parse_dates=["Date"], index_col="Date")
    data.DATA_DIR = Path("data/control")
    data.download_all([t], source="yahoo", verbose=False)
    return data.load(t)


def dips(df, thr=0.20, cooldown=60):
    c, h = df["Close"], df["High"]
    hi252 = h.rolling(252, min_periods=120).max()
    dd = c / hi252 - 1
    out, last = [], -10**9
    for i in range(len(df)):
        if dd.iloc[i] <= -thr and i - last >= cooldown:
            last = i
            futlow = df["Low"].iloc[i:i + 251].min()
            regained = bool((h.iloc[i + 1:i + 251] >= hi252.iloc[i]).any())
            finished = i + 250 < len(c)
            out.append(dict(date=str(df.index[i].date()), dip=dd.iloc[i], worst_after=futlow / c.iloc[i] - 1,
                            ret_60d=c.iloc[min(i + 60, len(c) - 1)] / c.iloc[i] - 1,
                            ret_12m=(c.iloc[i + 250] / c.iloc[i] - 1) if finished else np.nan,
                            regained="yes" if regained else ("no" if finished else "not yet")))
    return pd.DataFrame(out)


lines = ["# Every 20%+ dip, and what came next\n",
         "For each stock: the first day it closed 20% or more below its 52-week high (then a 60-trading-day gap "
         "before counting the next one), the worst further fall within a year, the return 60 days and 12 months later, "
         "and whether it got back to the old high within a year.\n"]
for t in TICKERS:
    df = load_any(t)
    ev = dips(df)
    done = ev[ev.regained.isin(["yes", "no"])]
    lines.append(f"\n## {t}: {len(ev)} dips since {df.index[0].date()}; regained the old high within a year in "
                 f"{int((done.regained == 'yes').sum())} of {len(done)} finished cases\n")
    lines.append("| date | dip | worst further fall | 60 days later | 12 months later | back to the old high? |")
    lines.append("|---|---|---|---|---|---|")
    for r in ev.itertuples():
        r12 = "n/a yet" if np.isnan(r.ret_12m) else f"{r.ret_12m:+.0%}"
        lines.append(f"| {r.date} | {r.dip:+.0%} | {r.worst_after:+.0%} | {r.ret_60d:+.0%} | {r12} | {r.regained} |")
    print(lines[-len(ev) - 3])
Path("results/dip_examples.md").write_text("\n".join(lines) + "\n")
print("wrote results/dip_examples.md")
