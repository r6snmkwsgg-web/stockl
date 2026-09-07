#!/usr/bin/env python3
"""How good is the score, honestly? A point-in-time test of its rankings.

On the first trading day of every quarter from 2012 to 2025 we score every
stock using only what was public that day (prices up to that day, financial
statements by their filing date), take the 10 highest-scoring eligible stocks,
and record what they did until the next rebalance and over the next 12 months
versus SPY and versus the average eligible stock. Returns are TOTAL returns
(dividends reinvested) for the stocks and for SPY alike.

Statistics: the quarterly windows do not overlap, so the quarterly edge gets a
t-statistic and a bootstrap range; 12-month windows overlap four-fold, so the
12-month figures are also given for January dates only (non-overlapping).

Universe = today's top 100 PLUS the 91 fallen/lagging stocks, so the formula
is judged on companies that went wrong as well as ones that went right.
Survivorship bias is reduced, not removed (bankrupt companies are missing).

Outputs: results/score_backtest.md / .json and results/score_picks.csv
"""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

from swing import data
from swing import score as S
from swing.control_universe import FALLEN
from swing.score import build_features, cross_section
from swing.universe import ALL_TICKERS, MARKET, STOCKS
from swing.universe_extra import MID, SMALL

OUT = Path("results")
TOP_N = 10
COST_PER_QUARTER = 0.002      # 0.1% to buy + 0.1% to sell, once a quarter


TIER = {}


def load_prices(tiers=("top100", "fallen")):
    prices = data.load_all(ALL_TICKERS)
    for t in prices:
        TIER[t] = "top100"
    for tier, lst, d in [("fallen", FALLEN, "data/control"), ("mid", MID, "data/prices_mid"), ("small", SMALL, "data/prices_small")]:
        if tier not in tiers:
            continue
        data.DATA_DIR = Path(d)
        for t, df in data.load_all(lst).items():
            if t not in prices:
                prices[t] = df
                TIER[t] = tier
    data.DATA_DIR = Path("data/prices")
    return prices


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--quality", type=float, help="weight (e.g. 0.35 to test the first version)")
    ap.add_argument("--value", type=float)
    ap.add_argument("--timing", type=float)
    ap.add_argument("--flag-penalty", type=float)
    ap.add_argument("--tag", default="", help="suffix for the output files, e.g. _v1")
    ap.add_argument("--tiers", default="top100,fallen", help="comma list of universes: top100,fallen,mid,small")
    ap.add_argument("--vol-cap", type=float, default=None, help="only stocks with 60-day volatility at or below this (percent)")
    args = ap.parse_args()
    if args.quality is not None:
        S.WEIGHTS.update({"quality": args.quality, "value": args.value, "timing": args.timing})
    if args.flag_penalty is not None:
        S.FLAG_PENALTY = args.flag_penalty
    print(f"weights {S.WEIGHTS}, flag penalty {S.FLAG_PENALTY}")
    tag = args.tag
    prices = load_prices(tuple(args.tiers.split(",")))
    vol_cap = args.vol_cap
    cal = prices[MARKET].index
    spy = prices[MARKET]["Close"]
    tickers = [t for t in prices if t != MARKET]
    print(f"building features for {len(tickers)} stocks ...")
    feats = build_features(prices, tickers, cal, spy)
    print(f"{len(feats)} with fundamentals")
    def tr(t):   # total-return price: split- and dividend-adjusted close where available
        d = prices[t]
        return (d["AdjClose"] if "AdjClose" in d.columns else d["Close"]).reindex(cal)
    closes = pd.DataFrame({t: tr(t) for t in feats})
    spy = tr(MARKET)
    pos = {d: i for i, d in enumerate(cal)}

    # rebalance dates: first trading day of Jan/Apr/Jul/Oct
    q_starts = cal.to_series().groupby([cal.year, cal.quarter]).first()
    dates = [d for d in q_starts if pd.Timestamp("2012-01-01") <= d and pos[d] + 252 < len(cal)]
    nxt = {d: (dates[k + 1] if k + 1 < len(dates) else cal[pos[d] + 63]) for k, d in enumerate(dates)}

    picks = []
    for d in dates:
        cs = cross_section(feats, d)
        el = cs[cs["eligible"]]
        if vol_cap is not None:
            el = el[el["vol60"] <= vol_cap / 100]
        el = el.sort_values("score", ascending=False)
        if len(el) < 20:
            continue
        el = el.copy()
        el["rank"] = np.arange(1, len(el) + 1)
        el["quintile"] = pd.qcut(el["rank"], 5, labels=[1, 2, 3, 4, 5]).astype(int)
        i, j = pos[d], pos[nxt[d]]
        for t, row in el.iterrows():
            c0 = closes[t].iloc[i]
            f63 = closes[t].iloc[j] / c0 - 1              # until the next rebalance
            f252 = closes[t].iloc[i + 252] / c0 - 1
            s63 = spy.iloc[j] / spy.iloc[i] - 1
            s252 = spy.iloc[i + 252] / spy.iloc[i] - 1
            picks.append(dict(date=d, ticker=t, universe=TIER.get(t, "fallen"),
                              score=row["score"], quality=row["quality"], value=row["value"],
                              timing=row["timing"], n_flags=row["n_flags"], rank=row["rank"],
                              quintile=row["quintile"], n_eligible=len(el),
                              fwd63=f63, fwd252=f252, spy63=s63, spy252=s252,
                              x63=f63 - s63, x252=f252 - s252))
    p = pd.DataFrame(picks).dropna(subset=["fwd252", "fwd63"])
    # excess over the AVERAGE eligible stock on the same date (removes the universe's own drift)
    p["e63"] = p["fwd63"] - p.groupby("date")["fwd63"].transform("mean")
    p["e252"] = p["fwd252"] - p.groupby("date")["fwd252"].transform("mean")
    p.to_csv(OUT / f"score_picks{tag}.csv", index=False)
    top = p[p["rank"] <= TOP_N]
    bottom = p[p["rank"] > p["n_eligible"] - TOP_N]

    def stats(g):
        return dict(n=int(len(g)), avg_12m=float(g.fwd252.mean()), median_12m=float(g.fwd252.median()),
                    avg_vs_spy_12m=float(g.x252.mean()), beat_spy_12m=float((g.x252 > 0).mean()),
                    avg_vs_eligible_12m=float(g.e252.mean()), beat_eligible_12m=float((g.e252 > 0).mean()),
                    avg_3m=float(g.fwd63.mean()), avg_vs_spy_3m=float(g.x63.mean()),
                    beat_spy_3m=float((g.x63 > 0).mean()), lost_20pct_12m=float((g.fwd252 < -0.2).mean()))

    def edge(series):
        """Mean, t-statistic and a 90% bootstrap range for a series of per-date excess returns."""
        x = np.asarray(series, dtype=float)
        n = len(x)
        rng = np.random.default_rng(7)
        boots = [rng.choice(x, size=n, replace=True).mean() for _ in range(4000)]
        return dict(n=int(n), mean=float(x.mean()), t=float(x.mean() / (x.std(ddof=1) / np.sqrt(n))) if n > 1 else 0.0,
                    ci90=[float(np.percentile(boots, 5)), float(np.percentile(boots, 95))],
                    share_positive=float((x > 0).mean()))

    res = {
        "rebalance_dates": len(dates), "first": str(dates[0].date()), "last": str(dates[-1].date()),
        "top10": stats(top), "bottom10": stats(bottom), "all_eligible": stats(p),
        "top10_top100_only": stats(top[top.universe == "top100"]),
        "top10_fallen_only": stats(top[top.universe == "fallen"]),
        "top10_share_from_fallen": float((top.universe == "fallen").mean()),
        "quintiles": {int(k): stats(g) for k, g in p.groupby("quintile")},
        "by_year": {int(k): stats(g) for k, g in top.groupby(top.date.dt.year)},
        "spy_avg_12m": float(p.groupby("date").spy252.first().mean()),
    }
    # the "undervalued on a dip" screen: strong business, cheap vs its own norm, well off its high
    rb = p[(p.quality >= 60) & (p.value >= 60) & (p.timing >= 60)]
    res["rebound"] = dict(stats(rb), per_date=float(rb.groupby("date").size().mean()) if len(rb) else 0.0,
                          dates_with_any=int(rb.date.nunique()),
                          top100=stats(rb[rb.universe == "top-100"]) if len(rb) else None,
                          fallen=stats(rb[rb.universe == "fallen"]) if len(rb) else None)
    # quarterly (non-overlapping) edge of the top-10 basket, per date
    byd = top.groupby("date").agg(port=("fwd63", "mean"), spy=("spy63", "first"), elig=("e63", "mean"))
    jan = top[top.date.dt.month == 1]
    res["edge"] = {
        "quarter_vs_spy": edge(byd["port"] - byd["spy"]),
        "quarter_vs_eligible": edge(byd["elig"]),
        "jan_only_12m_vs_spy": edge(jan.groupby("date").x252.mean()),
        "jan_only_12m_vs_eligible": edge(jan.groupby("date").e252.mean()),
        "jan_only_beat_spy_12m": float((jan.x252 > 0).mean()),
    }
    # a quarterly-rebalanced top-10 portfolio, compounded, with costs, vs SPY
    q = byd[["port", "spy"]].copy()
    q["port_net"] = q["port"] - COST_PER_QUARTER
    eq = (1 + q["port_net"]).cumprod()
    eq_spy = (1 + q["spy"]).cumprod()
    # label each point with the END of its holding quarter and start the curve at $1
    q_end = [nxt[d] for d in q.index]
    yrs = len(q) / 4
    res["portfolio"] = dict(
        quarters=int(len(q)), cagr=float(eq.iloc[-1] ** (1 / yrs) - 1), spy_cagr=float(eq_spy.iloc[-1] ** (1 / yrs) - 1),
        total=float(eq.iloc[-1] - 1), spy_total=float(eq_spy.iloc[-1] - 1),
        max_dd=float((eq / eq.cummax() - 1).min()), spy_max_dd=float((eq_spy / eq_spy.cummax() - 1).min()),
        quarters_beat_spy=float((q["port_net"] > q["spy"]).mean()),
        curve=[(str(q.index[0].date()), 1.0, 1.0)]
              + [(str(d.date()), round(float(a), 4), round(float(b), 4)) for d, a, b in zip(q_end, eq, eq_spy)],
    )
    res["weights"] = dict(S.WEIGHTS)
    res["tiers"] = args.tiers
    res["vol_cap"] = vol_cap
    res["flag_penalty"] = S.FLAG_PENALTY
    (OUT / f"score_backtest{tag}.json").write_text(json.dumps(res, indent=1))

    L = []
    L.append(f"# Score backtest: {len(dates)} quarterly rebalances, {dates[0].date()} to {dates[-1].date()}\n")
    L.append("| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |")
    L.append("|---|---|---|---|---|---|---|---|---|---|")
    for name, key in [("Top 10 by score", "top10"), ("Top 10, from today's top-100", "top10_top100_only"),
                      ("Top 10, from the fallen group", "top10_fallen_only"), ("Bottom 10 by score", "bottom10"),
                      ("Every eligible stock (average)", "all_eligible")]:
        s = res[key]
        L.append(f"| {name} | {s['n']} | {s['avg_12m']:+.1%} | {s['median_12m']:+.1%} | {s['avg_vs_spy_12m']:+.1%} | "
                 f"{s['beat_spy_12m']:.0%} | {s['avg_vs_eligible_12m']:+.1%} | {s['avg_3m']:+.1%} | {s['beat_spy_3m']:.0%} | {s['lost_20pct_12m']:.0%} |")
    L.append(f"\nSPY itself averaged {res['spy_avg_12m']:+.1%} (total return) over the same 12-month windows.\n")
    e = res["edge"]
    L.append("## Is the edge real? (top-10 basket, per rebalance date)\n")
    L.append("| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |")
    L.append("|---|---|---|---|---|---|")
    for name, k in [("Quarter vs SPY (non-overlapping)", "quarter_vs_spy"), ("Quarter vs average eligible stock", "quarter_vs_eligible"),
                    ("12-mo vs SPY, January dates only", "jan_only_12m_vs_spy"), ("12-mo vs average eligible, January only", "jan_only_12m_vs_eligible")]:
        v = e[k]
        L.append(f"| {name} | {v['n']} | {v['mean']:+.2%} | {v['t']:.2f} | {v['ci90'][0]:+.2%} to {v['ci90'][1]:+.2%} | {v['share_positive']:.0%} |")
    L.append("\nA t-stat below about 2 means the edge cannot be told apart from luck with this much data.\n")
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
    r_ = res["rebound"]
    L.append("## The 'undervalued on a dip' screen (quality, value and timing all >= 60)\n")
    L.append(f"{r_['n']} stock-quarters, about {r_['per_date']:.1f} names per date on {r_['dates_with_any']} of {len(dates)} dates: "
             f"avg 12-mo {r_['avg_12m']:+.1%}, median {r_['median_12m']:+.1%}, vs SPY {r_['avg_vs_spy_12m']:+.1%}, beat SPY {r_['beat_spy_12m']:.0%}, "
             f"vs average stock {r_['avg_vs_eligible_12m']:+.1%}, lost >20% {r_['lost_20pct_12m']:.0%}.")
    if r_["top100"] and r_["top100"]["n"]:
        L.append(f"From today's largest: {r_['top100']['n']} picks, vs SPY {r_['top100']['avg_vs_spy_12m']:+.1%}, beat {r_['top100']['beat_spy_12m']:.0%}. "
                 f"From the fallen group: {r_['fallen']['n']} picks, vs SPY {r_['fallen']['avg_vs_spy_12m']:+.1%}, beat {r_['fallen']['beat_spy_12m']:.0%}.\n")
    pf = res["portfolio"]
    L.append(f"\n## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter\n")
    L.append(f"* CAGR {pf['cagr']:+.1%} vs SPY {pf['spy_cagr']:+.1%}; total {pf['total']:+.0%} vs {pf['spy_total']:+.0%}")
    L.append(f"* Max drawdown {pf['max_dd']:.0%} vs SPY {pf['spy_max_dd']:.0%} (quarterly granularity)")
    L.append(f"* Beat SPY in {pf['quarters_beat_spy']:.0%} of quarters; {pf['quarters']} quarters")
    L.insert(1, f"Weights: quality {S.WEIGHTS['quality']:.0%}, value {S.WEIGHTS['value']:.0%}, timing {S.WEIGHTS['timing']:.0%}; "
                f"flag penalty {S.FLAG_PENALTY:g} points per flag.\n")
    (OUT / f"score_backtest{tag}.md").write_text("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
