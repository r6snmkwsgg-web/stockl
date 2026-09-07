#!/usr/bin/env python3
"""How good is the score, honestly? A point-in-time test of its rankings.

On the first trading day of every quarter from 2012 to 2025 we score every
stock using only what was public that day (prices up to that day, financial
statements by their filing date), take the 10 highest-scoring eligible stocks,
and record what they did over the next 3 and 12 months versus SPY and versus
the average eligible stock.

Universe = today's top 100 PLUS the 91 fallen/lagging stocks, so the formula
is judged on companies that went wrong as well as ones that went right.
Survivorship bias is reduced, not removed (bankrupt companies are missing).

Outputs: results/score_backtest.md / .json and results/score_picks.csv
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd

from swing import data
from swing.control_universe import FALLEN
from swing.score import build_features, cross_section
from swing.universe import ALL_TICKERS, MARKET, STOCKS

OUT = Path("results")
TOP_N = 10
COST_PER_QUARTER = 0.002      # 0.1% to buy + 0.1% to sell, once a quarter


def load_prices():
    prices = data.load_all(ALL_TICKERS)
    data.DATA_DIR = Path("data/control")
    for t, df in data.load_all(FALLEN).items():
        prices.setdefault(t, df)
    data.DATA_DIR = Path("data/prices")
    return prices


def main():
    prices = load_prices()
    cal = prices[MARKET].index
    spy = prices[MARKET]["Close"]
    tickers = [t for t in prices if t != MARKET]
    print(f"building features for {len(tickers)} stocks ...")
    feats = build_features(prices, tickers, cal, spy)
    print(f"{len(feats)} with fundamentals")
    closes = pd.DataFrame({t: prices[t]["Close"].reindex(cal) for t in feats})
    pos = {d: i for i, d in enumerate(cal)}

    # rebalance dates: first trading day of Jan/Apr/Jul/Oct
    q_starts = cal.to_series().groupby([cal.year, cal.quarter]).first()
    dates = [d for d in q_starts if pd.Timestamp("2012-01-01") <= d and pos[d] + 252 < len(cal)]

    picks = []
    for d in dates:
        cs = cross_section(feats, d)
        el = cs[cs["eligible"]].sort_values("score", ascending=False)
        if len(el) < 20:
            continue
        el = el.copy()
        el["rank"] = np.arange(1, len(el) + 1)
        el["quintile"] = pd.qcut(el["rank"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
        i = pos[d]
        for t, row in el.iterrows():
            c0 = closes[t].iloc[i]
            f63 = closes[t].iloc[i + 63] / c0 - 1
            f252 = closes[t].iloc[i + 252] / c0 - 1
            s63 = spy.iloc[i + 63] / spy.iloc[i] - 1
            s252 = spy.iloc[i + 252] / spy.iloc[i] - 1
            picks.append(dict(date=d, ticker=t, universe="top-100" if t in STOCKS else "fallen",
                              score=row["score"], quality=row["quality"], value=row["value"],
                              timing=row["timing"], n_flags=row["n_flags"], rank=row["rank"],
                              quintile=row["quintile"], n_eligible=len(el),
                              fwd63=f63, fwd252=f252, spy63=s63, spy252=s252,
                              x63=f63 - s63, x252=f252 - s252))
    p = pd.DataFrame(picks).dropna(subset=["fwd252"])
    p.to_csv(OUT / "score_picks.csv", index=False)
    top = p[p["rank"] <= TOP_N]
    bottom = p[p["rank"] > p["n_eligible"] - TOP_N]

    def stats(g):
        return dict(n=int(len(g)), avg_12m=float(g.fwd252.mean()), median_12m=float(g.fwd252.median()),
                    avg_vs_spy_12m=float(g.x252.mean()), beat_spy_12m=float((g.x252 > 0).mean()),
                    avg_3m=float(g.fwd63.mean()), avg_vs_spy_3m=float(g.x63.mean()),
                    beat_spy_3m=float((g.x63 > 0).mean()), lost_20pct_12m=float((g.fwd252 < -0.2).mean()))

    res = {
        "rebalance_dates": len(dates), "first": str(dates[0].date()), "last": str(dates[-1].date()),
        "top10": stats(top), "bottom10": stats(bottom), "all_eligible": stats(p),
        "top10_top100_only": stats(top[top.universe == "top-100"]),
        "top10_fallen_only": stats(top[top.universe == "fallen"]),
        "top10_share_from_fallen": float((top.universe == "fallen").mean()),
        "quintiles": {int(k): stats(g) for k, g in p.groupby("quintile")},
        "by_year": {int(k): stats(g) for k, g in top.groupby(top.date.dt.year)},
        "spy_avg_12m": float(p.groupby("date").spy252.first().mean()),
    }
    # a quarterly-rebalanced top-10 portfolio, compounded, with costs, vs SPY
    q = top.groupby("date").agg(port=("fwd63", "mean"), spy=("spy63", "first"))
    q["port_net"] = q["port"] - COST_PER_QUARTER
    eq = (1 + q["port_net"]).cumprod()
    eq_spy = (1 + q["spy"]).cumprod()
    yrs = len(q) / 4
    res["portfolio"] = dict(
        quarters=int(len(q)), cagr=float(eq.iloc[-1] ** (1 / yrs) - 1), spy_cagr=float(eq_spy.iloc[-1] ** (1 / yrs) - 1),
        total=float(eq.iloc[-1] - 1), spy_total=float(eq_spy.iloc[-1] - 1),
        max_dd=float((eq / eq.cummax() - 1).min()), spy_max_dd=float((eq_spy / eq_spy.cummax() - 1).min()),
        quarters_beat_spy=float((q["port_net"] > q["spy"]).mean()),
        curve=[(str(d.date()), round(float(a), 4), round(float(b), 4)) for d, a, b in zip(q.index, eq, eq_spy)],
    )
    (OUT / "score_backtest.json").write_text(json.dumps(res, indent=1))

    L = []
    L.append(f"# Score backtest: {len(dates)} quarterly rebalances, {dates[0].date()} to {dates[-1].date()}\n")
    L.append("| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |")
    L.append("|---|---|---|---|---|---|---|---|---|")
    for name, key in [("Top 10 by score", "top10"), ("Top 10, from today's top-100", "top10_top100_only"),
                      ("Top 10, from the fallen group", "top10_fallen_only"), ("Bottom 10 by score", "bottom10"),
                      ("Every eligible stock (average)", "all_eligible")]:
        s = res[key]
        L.append(f"| {name} | {s['n']} | {s['avg_12m']:+.1%} | {s['median_12m']:+.1%} | {s['avg_vs_spy_12m']:+.1%} | "
                 f"{s['beat_spy_12m']:.0%} | {s['avg_3m']:+.1%} | {s['beat_spy_3m']:.0%} | {s['lost_20pct_12m']:.0%} |")
    L.append(f"\nSPY itself averaged {res['spy_avg_12m']:+.1%} over the same 12-month windows.\n")
    L.append("## By score quintile (1 = best fifth, 5 = worst fifth)\n")
    L.append("| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |")
    L.append("|---|---|---|---|---|")
    for k, s in res["quintiles"].items():
        L.append(f"| {k} | {s['n']} | {s['avg_12m']:+.1%} | {s['avg_vs_spy_12m']:+.1%} | {s['beat_spy_12m']:.0%} |")
    L.append("\n## Top 10, by year of purchase\n")
    L.append("| Year | picks | avg 12-mo | avg vs SPY | beat SPY |")
    L.append("|---|---|---|---|---|")
    for k, s in res["by_year"].items():
        L.append(f"| {k} | {s['n']} | {s['avg_12m']:+.1%} | {s['avg_vs_spy_12m']:+.1%} | {s['beat_spy_12m']:.0%} |")
    pf = res["portfolio"]
    L.append(f"\n## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter\n")
    L.append(f"* CAGR {pf['cagr']:+.1%} vs SPY {pf['spy_cagr']:+.1%}; total {pf['total']:+.0%} vs {pf['spy_total']:+.0%}")
    L.append(f"* Max drawdown {pf['max_dd']:.0%} vs SPY {pf['spy_max_dd']:.0%} (quarterly granularity)")
    L.append(f"* Beat SPY in {pf['quarters_beat_spy']:.0%} of quarters; {pf['quarters']} quarters")
    (OUT / "score_backtest.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
