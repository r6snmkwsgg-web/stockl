#!/usr/bin/env python3
"""Research: buying structurally strong stocks after a big dip.

"Structurally strong" (using only data known on the day):
  * the stock's 3-year return beat SPY's 3-year return, and
  * its 200-day moving average is higher than it was 6 months ago.
"Big dip": the close is at least X% below its 52-week high (X = 10..30).
"Fresh": the 52-week high was set within the last 60 trading days.

We look at each stock the FIRST day it crosses the dip threshold (then wait
60 trading days before counting the same stock again) and measure what
happened next over 5, 20, 60, 120 and 250 trading days, versus SPY and versus
the same stocks on ordinary days. No fundamentals are used: this is
"cheap relative to its own trend", not "undervalued" in the earnings sense.

The same test is run on two universes:
  * the 100 largest stocks TODAY (today's winners: survivorship bias), and
  * a control group of ~95 once-large or once-popular stocks that later
    lagged or crashed (swing/control_universe.py).
If the effect is real it should show up in both. If it only shows up in the
winners, it is hindsight.
"""
from pathlib import Path

import pandas as pd

from swing import data
from swing.control_universe import FALLEN
from swing.universe import ALL_TICKERS, MARKET, STOCKS

OUT = Path("results")
HORIZONS = [5, 20, 60, 120, 250]
COOLDOWN = 60
THRESHOLDS = [0.10, 0.15, 0.20, 0.25, 0.30]


def forward(close: pd.Series, h: int) -> pd.Series:
    return close.shift(-h) / close - 1


def worst_path(low: pd.Series, close: pd.Series, h: int) -> pd.Series:
    """Worst further fall (lowest low in the next h days) relative to today's close."""
    fwd_low = low[::-1].rolling(h, min_periods=1).min()[::-1].shift(-1)
    return fwd_low / close - 1


def features(d: pd.DataFrame, spy: pd.Series, ticker: str) -> pd.DataFrame:
    """Per-stock table: strong flag, drawdown from 52-week high, forward returns."""
    d = d.reindex(spy.index)
    c = d["Close"]
    f = pd.DataFrame(index=spy.index)
    f["ticker"] = ticker
    f["close"] = c
    sma200 = c.rolling(200).mean()
    f["ret3y"] = c / c.shift(756) - 1
    f["sma200_rising"] = sma200 > sma200.shift(126)
    f["strong"] = (f["ret3y"] > (spy / spy.shift(756) - 1)) & f["sma200_rising"]
    hi252 = d["High"].rolling(252).max()
    f["hi252"] = hi252
    f["dd"] = c / hi252 - 1
    f["fresh"] = d["High"].rolling(60).max() >= hi252 * 0.999
    for h in HORIZONS:
        f[f"r{h}"] = forward(c, h)
        f[f"spy{h}"] = forward(spy, h)
        f[f"x{h}"] = f[f"r{h}"] - f[f"spy{h}"]
    f["worst60"] = worst_path(d["Low"], c, 60)
    return f


def build(prices: dict, tickers, spy: pd.Series) -> pd.DataFrame:
    f = pd.concat([features(prices[t], spy, t) for t in tickers if t in prices])
    return f[f.index >= "2011-01-01"]


def events(f: pd.DataFrame, thr: float, fresh: bool) -> pd.DataFrame:
    """First day each stock crosses the dip threshold, with a cooldown."""
    out = []
    for t, g in f.groupby("ticker"):
        cond = g["strong"] & (g["dd"] <= -thr)
        if fresh:
            cond &= g["fresh"]
        last = None
        for k, (date, ok) in enumerate(cond.items()):
            if ok and (last is None or (k - last) >= COOLDOWN):
                out.append(g.iloc[k])
                last = k
    return pd.DataFrame(out)


def table(ev: pd.DataFrame, label: str) -> dict:
    row = {"case": label, "events": len(ev)}
    if not len(ev):
        return row
    for h in HORIZONS:
        row[f"avg {h}d"] = ev[f"r{h}"].mean()
        row[f"median {h}d"] = ev[f"r{h}"].median()
        row[f"vs SPY {h}d"] = ev[f"x{h}"].mean()
        row[f"beat SPY {h}d"] = (ev[f"x{h}"] > 0).mean()
    row["median worst fall next 60d"] = ev["worst60"].median()
    row["fell 10%+ more within 60d"] = (ev["worst60"] <= -0.10).mean()
    row["distinct months"] = ev.index.to_period("M").nunique()
    return row


def study(prices: dict, tickers, spy: pd.Series, tag: str) -> pd.DataFrame:
    f = build(prices, tickers, spy)
    rows = [table(f[f["strong"] & (f["dd"] > -0.05)], "control: strong stock, within 5% of its high (all days)"),
            table(f[f["strong"]], "control: strong stock, any day")]
    for thr in THRESHOLDS:
        for fresh in [False, True]:
            ev = events(f, thr, fresh)
            ev.to_csv(OUT / "dips" / f"{tag.split('/')[0].replace(' ', '_')}_events_{int(thr * 100)}pct_{'fresh' if fresh else 'any'}.csv")
            rows.append(table(ev, f"strong stock, {thr:.0%} below 52w high{', high set <60d ago' if fresh else ''}"))
    ev = events(f, 0.20, False)
    rows.append(table(ev[ev.index <= "2018-12-31"], "20% dip, 2011-2018 only"))
    rows.append(table(ev[ev.index >= "2019-01-01"], "20% dip, 2019-2026 only"))
    rows.append(table(ev[~ev.index.year.isin([2020, 2022])], "20% dip, excluding 2020 and 2022"))
    df = pd.DataFrame(rows)
    df.insert(0, "universe", tag)
    return df


def to_md(df: pd.DataFrame) -> str:
    cols = ["events", "avg 20d", "avg 60d", "avg 250d", "median 60d", "median 250d",
            "vs SPY 20d", "vs SPY 60d", "vs SPY 250d", "beat SPY 60d", "beat SPY 250d",
            "median worst fall next 60d", "fell 10%+ more within 60d", "distinct months"]
    md = ["| Universe | Case | " + " | ".join(cols) + " |", "|---|---|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r.get(c)
            if v is None or v != v:
                cells.append("")
            elif c in ("events", "distinct months"):
                cells.append(f"{v:.0f}")
            elif "beat" in c or "fell" in c:
                cells.append(f"{v:.0%}")
            else:
                cells.append(f"{v:+.1%}")
        md.append(f"| {r['universe']} | {r['case']} | " + " | ".join(cells) + " |")
    return "\n".join(md) + "\n"


def main():
    (OUT / "dips").mkdir(exist_ok=True)
    prices = data.load_all(ALL_TICKERS)
    spy = prices[MARKET]["Close"]
    frames = [study(prices, STOCKS, spy, "top-100 today")]

    control_dir = Path("data/control")
    if control_dir.exists() and any(control_dir.iterdir()):
        data.DATA_DIR = control_dir
        cprices = data.load_all(FALLEN)
        data.DATA_DIR = Path("data/prices")
        print(f"control universe: {len(cprices)} tickers loaded")
        frames.append(study(cprices, list(cprices), spy, "fallen/lagging control"))

    df = pd.concat(frames, ignore_index=True)
    df.to_csv(OUT / "dips_summary.csv", index=False)
    (OUT / "dips_summary.md").write_text(to_md(df))
    pd.set_option("display.width", 250)
    show = ["universe", "case", "events", "avg 60d", "avg 250d", "median 250d", "vs SPY 60d", "vs SPY 250d",
            "beat SPY 250d", "fell 10%+ more within 60d"]
    print(df[show].to_string(index=False, float_format=lambda x: f"{x:+.1%}"))
    print("Wrote results/dips_summary.md")


if __name__ == "__main__":
    main()
