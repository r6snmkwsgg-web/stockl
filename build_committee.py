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

from swing import news as newsmod
from swing.fundamentals import FLOW_TAGS, _pick, load as load_facts

TEMPLATE = Path("committee_template.html")
OUT = Path("site/committee.html")
STANDALONE = Path("site/ledger_committee.html")
TOP_N = 400   # all eligible stocks; the committee, not the score, does the choosing
PRICE_DIRS = ["data/prices", "data/control", "data/prices_mid", "data/prices_small", "data/prices_spec"]


def main():
    html = Path("site/index.html").read_text()
    payload = json.loads(re.search(r"const DATA = (\{.*?\});\nconst S = DATA.stocks", html, re.S).group(1))
    el = [s for s in payload["stocks"] if s["eligible"]][:TOP_N]
    # moonshot pool for the Extreme profile: liquid small companies that fail the Ledger's profit rules but have a real,
    # growing revenue line (pre-profit growth companies) or are in the speculative list
    num = lambda v: isinstance(v, (int, float))
    def spec_ok(s):
        if s["universe"] not in ("spec", "small") or s["eligible"]:
            return False
        if s.get("reason") not in ("price under $10", "losing money", "negative free cash flow", "less than 3 years of price history"):
            return False
        if not (num(s.get("price")) and s["price"] >= 2 and num(s.get("mcap")) and s["mcap"] >= 5e7):
            return False
        growing = (num(s.get("rev_growth")) and s["rev_growth"] > 15) or (num(s.get("revenue_ttm")) and s["revenue_ttm"] > 2e7)
        funded = (num(s.get("runway_years")) and s["runway_years"] >= 1) or (num(s.get("net_income_ttm")) and s["net_income_ttm"] > 0)
        return bool(growing and funded)
    moon = [dict(s, moonshot=True) for s in payload["stocks"] if spec_ok(s)]
    el = el + moon
    keep = ["ticker", "name", "sector", "universe", "rank", "score", "quality", "value", "timing", "verdict", "price", "mcap", "moonshot", "eligible", "reason",
            "share_growth_1y", "runway_years", "cash", "net_income_ttm",
            "dip", "fresh", "days_since_high", "above_200", "pe", "pe_pct_5y", "ps", "fcf_yield", "earnings_yield", "roe",
            "net_margin", "fcf_margin", "rev_growth", "ni_growth", "debt_to_equity", "ret1y", "ret3y_vs_spy", "vol60", "flags", "financial", "spark", "revenue_ttm", "net_income_ttm"]
    stocks = [{k: s.get(k) for k in keep} for s in el]
    for s in stocks:
        s["spark"] = [v for v in s["spark"][::4]] if s.get("spark") else []   # ~13 points, enough for a mini line
        t = s["ticker"]
        # price trend: month-end closes over the last year, as % change from a year ago
        for d in PRICE_DIRS:
            f = Path(d) / f"{t}.csv.gz"
            if f.exists():
                px = pd.read_csv(f, parse_dates=["Date"], index_col="Date")["Close"]
                break
        else:
            px = None
        if px is not None and len(px) > 260:
            last = px.iloc[-260:]
            me = last.groupby([last.index.year, last.index.month]).last()
            base = float(me.iloc[0])
            s["path"] = [round((float(v) / base - 1) * 100) for v in me.iloc[1:]]
        else:
            s["path"] = []
        # business trend: the last six quarters of revenue and profit from the filings
        facts = load_facts(t)
        s["q_rev"], s["q_ni"] = [], []
        if facts:
            for key, item in [("q_rev", "revenue"), ("q_ni", "net_income")]:
                q = _pick(facts["tags"], FLOW_TAGS[item], "flow")
                if len(q):
                    q = q[q["end"] <= pd.Timestamp(payload["as_of"]).date()].tail(6)
                    s[key] = [round(float(v) / 1e9, 2) for v in q["val"]]
        # official events and headlines
        n = newsmod.load(t) or {}
        s["events"] = [f"{e['date']}: {e['what']}" for e in n.get("events", [])][:6]
        s["headlines"] = [f"{h['date']}: {h['title']}" for h in n.get("headlines", [])][:5]
        s["last_report"] = (n.get("last_report") or {}).get("filed")
        s["next_report"] = n.get("next_report_est")

    # historical distribution of a top-10 basket held a year, and of SPY, from the point-in-time test
    p = pd.read_csv("results/score_picks.csv", parse_dates=["date"])
    top = p[p["rank"] <= 10].groupby("date").agg(basket=("fwd252", "mean"), spy=("spy252", "first"))
    qs = [0.10, 0.25, 0.50, 0.75, 0.90]
    dist = {"quantiles": qs, "basket": [float(top.basket.quantile(q)) for q in qs], "spy": [float(top.spy.quantile(q)) for q in qs],
            "beat": float((top.basket > top.spy).mean()), "lose": float((top.basket < 0).mean()), "n": int(len(top)),
            "worst": float(top.basket.min()), "best": float(top.basket.max())}
    bt = payload.get("backtest") or {}
    # risk tiers: what each one is, and what its own point-in-time backtest measured
    TIERS = [
        {"id": "calm", "name": "Calm", "universes": ["top100"], "vol_cap": 30, "index": 70, "npos": 4,
         "blurb": "Today's largest companies only, none that moves more than 30% a year, most of the money in the index fund."},
        {"id": "moderate", "name": "Moderate", "universes": ["top100"], "vol_cap": 45, "index": 50, "npos": 6,
         "blurb": "Today's largest companies, up to 45% volatility, half in the index fund."},
        {"id": "high", "name": "High", "universes": ["top100", "mid"], "vol_cap": 60, "index": 30, "npos": 8,
         "blurb": "Large and mid-sized companies (S&P 400), up to 60% volatility, less in the index fund."},
        {"id": "extreme", "name": "Extreme", "universes": ["small", "spec"], "vol_cap": 999, "index": 0, "npos": 8,
         "blurb": "Small and micro caps only, including companies that are not yet profitable, no volatility limit, no index fund unless you add it. The seats switch to growth jobs: revenue acceleration, cash runway, dilution, catalysts. Big winners and total wipe-outs live here."},
    ]
    for tier in TIERS:
        f = Path(f"results/tier_{tier['id']}.json")
        if f.exists():
            j = json.loads(f.read_text())
            tier["record"] = {"basket_cagr": j["portfolio"]["cagr"], "spy_cagr": j["portfolio"]["spy_cagr"], "max_dd": j["portfolio"]["max_dd"],
                              "spy_max_dd": j["portfolio"]["spy_max_dd"], "beat_spy": j["top10"]["beat_spy_12m"], "lost_20": j["top10"]["lost_20pct_12m"],
                              "avg_12m": j["top10"]["avg_12m"], "worst_year": min(v["avg_12m"] for v in j["by_year"].values()),
                              "best_year": max(v["avg_12m"] for v in j["by_year"].values()), "n_dates": j["rebalance_dates"]}
        else:
            tier["record"] = None
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

    # ---- monthly total-return history since end-2019 for the stress test (SPY + every candidate)
    def monthly(t, d):
        f = Path(d) / f"{t}.csv.gz"
        if not f.exists():
            return None
        px = pd.read_csv(f, parse_dates=["Date"], index_col="Date")
        col = px["AdjClose"] if "AdjClose" in px.columns else px["Close"]
        col = col[col.index >= "2019-12-01"]
        if not len(col):
            return None
        m = col.groupby([col.index.year, col.index.month]).last()
        return m
    spy_m = monthly("SPY", "data/prices")
    months = [f"{y}-{mo:02d}" for (y, mo) in spy_m.index]
    hist = {"months": months, "SPY": [round(float(v), 3) for v in spy_m]}
    for s in stocks:
        t = s["ticker"]
        m = None
        for d in PRICE_DIRS:
            m = monthly(t, d)
            if m is not None:
                break
        if m is None:
            hist[t] = [None] * len(months); continue
        series = [None] * len(months)
        for (y, mo), v in m.items():
            key = f"{y}-{mo:02d}"
            if key in months:
                series[months.index(key)] = round(float(v), 3)
        hist[t] = series
        # per-name stress figures for the seats: 2022 and worst rolling 12 months since 2020
        vals = pd.Series(series, dtype="float64")
        def ret(a, b):
            if a in months and b in months:
                x, y = vals[months.index(a)], vals[months.index(b)]
                if pd.notna(x) and pd.notna(y) and x > 0:
                    return round((y / x - 1) * 100)
            return None
        s["r2022"] = ret("2021-12", "2022-12")
        s["covid"] = ret("2020-01", "2020-03")
        r12 = (vals / vals.shift(12) - 1).dropna()
        s["worst12"] = round(float(r12.min()) * 100) if len(r12) and pd.notna(r12.min()) else None

    # ---- base rates: what small and speculative stocks actually did, year by year, since 2020
    base = {}
    for tier_name, pool in [("small", [x for x in stocks if x["universe"] in ("small", "spec")]), ("large", [x for x in stocks if x["universe"] == "top100"])]:
        n2 = n3 = nhalf = tot = 0
        for x in pool:
            ser = pd.Series(hist.get(x["ticker"], []), dtype="float64")
            r12 = (ser / ser.shift(12) - 1).dropna()
            tot += len(r12); n2 += int((r12 >= 1.0).sum()); n3 += int((r12 >= 2.0).sum()); nhalf += int((r12 <= -0.5).sum())
        if tot:
            base[tier_name] = {"n": tot, "doubled": n2 / tot, "tripled": n3 / tot, "halved": nhalf / tot}
    macro_base = base

    # ---- macro backdrop for the Macro Strategist
    def stats(t, d="data/macro"):
        px = pd.read_csv(Path(d) / f"{t}.csv.gz", parse_dates=["Date"], index_col="Date")["Close"]
        last = float(px.iloc[-1])
        return {"last": round(last, 2), "r3m": round((last / float(px.iloc[-64]) - 1) * 100, 1), "r12m": round((last / float(px.iloc[-253]) - 1) * 100, 1),
                "vs200": round((last / float(px.rolling(200).mean().iloc[-1]) - 1) * 100, 1), "r1m": round((last / float(px.iloc[-22]) - 1) * 100, 1),
                "hi52_dd": round((last / float(px.iloc[-252:].max()) - 1) * 100, 1)}
    tnx = pd.read_csv("data/macro/^TNX.csv.gz", parse_dates=["Date"], index_col="Date")["Close"]
    vix = pd.read_csv("data/macro/^VIX.csv.gz", parse_dates=["Date"], index_col="Date")["Close"]
    sec_names = {"XLK": "Technology", "XLF": "Financials", "XLV": "Health care", "XLE": "Energy", "XLB": "Materials", "XLI": "Industrials",
                 "XLY": "Consumer discretionary", "XLP": "Consumer staples", "XLU": "Utilities", "XLRE": "Real estate", "XLC": "Communication"}
    macro = {
        "spy": stats("SPY", "data/prices"),
        "ten_year": {"last": round(float(tnx.iloc[-1]), 2), "a_year_ago": round(float(tnx.iloc[-253]), 2), "three_months_ago": round(float(tnx.iloc[-64]), 2)},
        "vix": {"last": round(float(vix.iloc[-1]), 1), "avg_1y": round(float(vix.iloc[-252:].mean()), 1)},
        "sectors": [{"etf": e, "name": n, **stats(e)} for e, n in sec_names.items()],
        "breadth": round(100 * sum(1 for x in stocks if isinstance(x.get("above_200"), (int, float)) and x["above_200"] > 0) / max(1, len(stocks))),
        "fresh_dips": round(100 * sum(1 for x in stocks if x.get("fresh")) / max(1, len(stocks))),
    }
    # SPY's own recent volatility, so the page can put the index share on the same footing
    spy_px = pd.read_csv("data/prices/SPY.csv.gz", parse_dates=["Date"], index_col="Date")["Close"]
    spy_vol = float(np.log(spy_px).diff().rolling(60).std().iloc[-1] * np.sqrt(252) * 100)
    data = {"as_of": payload["as_of"], "market": {**payload["market"], "spy_vol": round(spy_vol, 1)}, "stocks": stocks, "sectors": sectors,
            "hist": hist, "macro": macro, "tiers": TIERS, "base_rates": macro_base,
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
