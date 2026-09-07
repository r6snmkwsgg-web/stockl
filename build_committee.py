#!/usr/bin/env python3
"""Build the Ledger Committee page (site/committee.html): a panel of AI analysts
that deliberate, on the page, over the Bargain Ledger's numbers to propose a
portfolio for whoever fills in the brief.

Reads the data already embedded in site/index.html (run build_site.py first)
and results/score_picks.csv for the historical distribution.
"""
import json
import re
from pathlib import Path

import numpy as np
import pandas as pd

TEMPLATE = Path("committee_template.html")
OUT = Path("site/committee.html")
STANDALONE = Path("site/ledger_committee.html")
TOP_N = 400   # all eligible stocks; the committee, not the score, does the choosing


def main():
    html = Path("site/index.html").read_text()
    payload = json.loads(re.search(r"const DATA = (\{.*?\});\nconst S = DATA.stocks", html, re.S).group(1))
    el = [s for s in payload["stocks"] if s["eligible"]][:TOP_N]
    keep = ["ticker", "name", "sector", "universe", "rank", "score", "quality", "value", "timing", "verdict", "price", "mcap",
            "dip", "fresh", "days_since_high", "above_200", "pe", "pe_pct_5y", "ps", "fcf_yield", "earnings_yield", "roe",
            "net_margin", "fcf_margin", "rev_growth", "ni_growth", "debt_to_equity", "ret1y", "ret3y_vs_spy", "vol60", "flags", "financial", "spark", "revenue_ttm", "net_income_ttm"]
    stocks = [{k: s.get(k) for k in keep} for s in el]
    for s in stocks:
        s["spark"] = [v for v in s["spark"][::4]] if s.get("spark") else []   # ~13 points, enough for a mini line

    # historical distribution of a top-10 basket held a year, and of SPY, from the point-in-time test
    p = pd.read_csv("results/score_picks.csv", parse_dates=["date"])
    top = p[p["rank"] <= 10].groupby("date").agg(basket=("fwd252", "mean"), spy=("spy252", "first"))
    qs = [0.10, 0.25, 0.50, 0.75, 0.90]
    dist = {"quantiles": qs, "basket": [float(top.basket.quantile(q)) for q in qs], "spy": [float(top.spy.quantile(q)) for q in qs],
            "beat": float((top.basket > top.spy).mean()), "lose": float((top.basket < 0).mean()), "n": int(len(top)),
            "worst": float(top.basket.min()), "best": float(top.basket.max())}
    bt = payload.get("backtest") or {}
    record = {
        "per_pick_beat_spy": bt.get("top10", {}).get("beat_spy_12m"),
        "per_pick_vs_spy": bt.get("top10", {}).get("avg_vs_spy_12m"),
        "per_pick_vs_avg": bt.get("top10", {}).get("avg_vs_eligible_12m"),
        "basket_cagr": bt.get("portfolio", {}).get("cagr"), "spy_cagr": bt.get("portfolio", {}).get("spy_cagr"),
        "basket_maxdd": bt.get("portfolio", {}).get("max_dd"), "spy_maxdd": bt.get("portfolio", {}).get("spy_max_dd"),
        "quarters_beat": bt.get("portfolio", {}).get("quarters_beat_spy"),
        "edge_vs_avg": bt.get("edge", {}).get("quarter_vs_eligible"),
        "fallen_beat": bt.get("top10_fallen_only", {}).get("beat_spy_12m"),
        "first": bt.get("first"), "last": bt.get("last"),
    }
    sectors = sorted({s["sector"] for s in stocks})
    data = {"as_of": payload["as_of"], "market": payload["market"], "stocks": stocks, "sectors": sectors,
            "dist": dist, "record": record, "counts": payload["counts"]}
    js = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    page = TEMPLATE.read_text().replace("__DATA__", js)
    assert all(ord(c) < 128 for c in page), "page must be ASCII-only"
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(page)
    head, body = page.split("\n", 1)
    STANDALONE.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">' + head + "</head><body>" + body + "</body></html>")
    print(f"{len(stocks)} candidates, as of {data['as_of']}; wrote {OUT} and {STANDALONE} ({OUT.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
