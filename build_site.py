#!/usr/bin/env python3
"""Build the Bargain Ledger: a single self-contained web page (site/index.html)
that ranks every stock in both universes by the score in swing/score.py and
explains why each one ranks where it does.

    python build_site.py                 # use data on disk
    python build_site.py --download      # refresh prices and filings first

The page embeds its data, so it works offline and can be published anywhere.
Re-run this script whenever you want fresh numbers.
"""
import argparse
import json
import re
from datetime import date
from pathlib import Path

import numpy as np
import pandas as pd

from swing import data, fundamentals
from swing.control_universe import FALLEN
from swing.score import NOT_SCORED, WEIGHTS, build_features, cross_section
from swing.universe import ALL_TICKERS, MARKET, STOCKS

OUT = Path("site/index.html")
TEMPLATE = Path(__file__).with_name("site_template.html")


def clean_name(n: str | None, ticker: str) -> str:
    if not n:
        return ticker
    n = re.sub(r"\s*/[A-Z]+/?\s*$", "", n)        # "/NEW", "/DE/"
    n = re.sub(r"\s*\((?:THE|DE|NEW)\)\s*$", "", n, flags=re.I)
    n = n.title()
    for a, b in [(" Inc.", " Inc"), (" Inc", ""), (" Corp.", ""), (" Corp", ""), (" Co.", ""), (",", ""),
                 (" Plc", ""), (" Ltd", ""), (" Holdings", " Holdings"), ("Llc", "LLC"), ("&", "&")]:
        n = n.replace(a, b)
    n = re.sub(r"\b(Ii|Iii|Iv)\b", lambda m: m.group(0).upper(), n)
    return n.strip() or ticker


def load_prices():
    prices = data.load_all(ALL_TICKERS)
    data.DATA_DIR = Path("data/control")
    for t, df in data.load_all(FALLEN).items():
        prices.setdefault(t, df)
    data.DATA_DIR = Path("data/prices")
    return prices


def pct(x, d=0):
    return None if x is None or (isinstance(x, float) and np.isnan(x)) else round(float(x) * 100, d)


def num(x, d=2):
    return None if x is None or (isinstance(x, float) and (np.isnan(x) or np.isinf(x))) else round(float(x), d)


def why(r) -> dict:
    fin = bool(r["financial"])
    dip = -r["dd52"] if pd.notna(r["dd52"]) else 0
    q = []
    if pd.notna(r["roe"]):
        q.append(f"return on equity {r['roe']:.0%}")
    if fin and pd.notna(r["net_margin"]):
        q.append(f"net margin {r['net_margin']:.0%}")
    elif pd.notna(r["fcf_margin"]):
        q.append(f"{r['fcf_margin']:.0%} of revenue turns into free cash")
    if pd.notna(r["rev_growth"]):
        q.append(f"revenue {'up' if r['rev_growth'] >= 0 else 'down'} {abs(r['rev_growth']):.0%} over the last year")
    if pd.notna(r["ret3y_vs_spy"]):
        q.append(f"3-year share price {r['ret3y_vs_spy']:+.0%} versus SPY")
    q.append("200-day trend " + ("rising" if r["sma200_rising"] else "falling"))
    v = []
    if pd.notna(r["pe"]):
        s = f"P/E {r['pe']:.1f}"
        if pd.notna(r["pe_pct_5y"]):
            s += f", cheaper than {100 * (1 - r['pe_pct_5y']):.0f}% of its own last five years"
        v.append(s)
    else:
        v.append("no P/E (not profitable over the last 12 months)")
    if fin:
        if pd.notna(r["pb"]):
            s = f"price {r['pb']:.1f}x book value"
            if pd.notna(r["pb_pct_5y"]):
                s += f", cheaper than {100 * (1 - r['pb_pct_5y']):.0f}% of its history"
            v.append(s)
    else:
        if pd.notna(r["ps_pct_5y"]):
            v.append(f"price-to-sales cheaper than {100 * (1 - r['ps_pct_5y']):.0f}% of its history")
        if pd.notna(r["fcf_yield"]):
            v.append(f"free-cash-flow yield {r['fcf_yield']:.1%}")
    if pd.notna(r["earnings_yield"]):
        v.append(f"earnings yield {r['earnings_yield']:.1%}")
    t = []
    if pd.notna(r["dd52"]):
        d = int(r["days_since_high"]) if pd.notna(r["days_since_high"]) else None
        t.append(f"{dip:.0%} below its 52-week high" + (f", set {d} trading days ago" if d is not None else "")
                 + (" (a fresh dip)" if r["fresh"] else " (an older high)"))
    if pd.notna(r["above_200"]):
        t.append(f"{r['above_200']:+.0%} versus its 200-day average")
    if pd.notna(r["rsi14"]):
        t.append(f"RSI {r['rsi14']:.0f}" + (" (over-bought)" if r["rsi14"] > 70 else ""))
    return {"quality": "; ".join(q) + ".", "value": "; ".join(v) + ".", "timing": "; ".join(t) + "."}


def verdict(r) -> str:
    if not r["eligible"]:
        return "Not scored"
    parts = []
    parts.append({2: "Strong business", 1: "Decent business", 0: "Weak business"}[2 if r["quality"] >= 65 else 1 if r["quality"] >= 45 else 0])
    parts.append({2: "priced well below its norm", 1: "fairly priced", 0: "priced above its norm"}[2 if r["value"] >= 65 else 1 if r["value"] >= 45 else 0])
    parts.append({2: "in a fresh pull-back", 1: "modest pull-back", 0: "no real pull-back"}[2 if r["timing"] >= 65 else 1 if r["timing"] >= 45 else 0])
    return ", ".join(parts) + "."


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--download", action="store_true", help="refresh prices and SEC filings first")
    args = ap.parse_args()
    if args.download:
        print("Downloading prices ...")
        data.download_all(ALL_TICKERS, source="auto", verbose=False)
        data.DATA_DIR = Path("data/control")
        data.download_all(FALLEN, source="yahoo", verbose=False)
        data.DATA_DIR = Path("data/prices")
        print("Downloading SEC filings ...")
        fundamentals.download_all(STOCKS + [t for t in FALLEN if t not in STOCKS], verbose=False)

    prices = load_prices()
    cal = prices[MARKET].index
    spy = prices[MARKET]["Close"]
    as_of = cal[-1]
    tickers = [t for t in prices if t != MARKET]
    feats = build_features(prices, tickers, cal, spy)
    cs = cross_section(feats, as_of)
    sma200 = spy.rolling(200).mean().iloc[-1]

    stocks = []
    for t, r in cs.iterrows():
        px = prices[t]["Close"].reindex(cal)
        last252 = px.iloc[-252:]
        sma = px.rolling(200).mean().iloc[-252:]
        idx = list(range(0, 252, 5)) + [251]
        spark = [num(last252.iloc[i], 2) for i in idx]
        spark_sma = [num(sma.iloc[i], 2) for i in idx]
        spark_dates = [str(last252.index[i].date()) for i in idx]
        fdata = fundamentals.load(t) or {}
        reason = None
        if not r["eligible"]:
            hard = [f for f in r["flags"] if f.startswith(("losing", "negative free", "stale", "thin"))]
            reason = hard[0] if hard else "missing data"
        stocks.append({
            "ticker": t, "name": clean_name(fdata.get("name"), t), "sector": r["sector"],
            "universe": "top100" if t in STOCKS else "fallen", "financial": bool(r["financial"]),
            "eligible": bool(r["eligible"]), "reason": reason, "verdict": verdict(r),
            "score": num(r["score"], 1), "quality": num(r["quality"], 0), "value": num(r["value"], 0),
            "timing": num(r["timing"], 0), "flags": list(r["flags"]), "n_flags": int(r["n_flags"]),
            "price": num(r["close"], 2), "mcap": num(r["mcap"], 0), "dip": pct(r["dd52"], 1),
            "days_since_high": None if pd.isna(r["days_since_high"]) else int(r["days_since_high"]),
            "fresh": bool(r["fresh"]) if pd.notna(r["fresh"]) else False,
            "above_200": pct(r["above_200"], 1), "pe": num(r["pe"], 1), "pe_reported": num(r["pe_reported"], 1),
            "pe_pct_5y": pct(r["pe_pct_5y"], 0), "ps": num(r["ps"], 2), "ps_pct_5y": pct(r["ps_pct_5y"], 0),
            "pb": num(r["pb"], 2), "fcf_yield": pct(r["fcf_yield"], 1), "earnings_yield": pct(r["earnings_yield"], 1),
            "roe": pct(r["roe"], 0), "net_margin": pct(r["net_margin"], 0), "fcf_margin": pct(r["fcf_margin"], 0),
            "rev_growth": pct(r["rev_growth"], 1), "ni_growth": pct(r["ni_growth"], 0),
            "debt_to_equity": num(r["debt_to_equity"], 2), "revenue_ttm": num(r["revenue_ttm"], 0),
            "net_income_ttm": num(r["net_income_ttm"], 0), "fcf_ttm": num(r["fcf_ttm"], 0),
            "ret1y": pct(r["ret1y"], 0), "ret3y_vs_spy": pct(r["ret3y_vs_spy"], 0), "vol60": pct(r["vol60"], 0),
            "rsi14": num(r["rsi14"], 0), "days_since_filing": None if pd.isna(r["days_since_filing"]) else int(r["days_since_filing"]),
            "hi52": num(last252.max(), 2), "lo52": num(last252.min(), 2),
            "spark": spark, "spark_sma": spark_sma, "spark_dates": spark_dates, "why": why(r),
        })
    stocks.sort(key=lambda s: (-(s["score"] if s["score"] is not None else -1), s["ticker"]))
    for i, s in enumerate([s for s in stocks if s["eligible"]], 1):
        s["rank"] = i

    bt_path = Path("results/score_backtest.json")
    backtest = json.loads(bt_path.read_text()) if bt_path.exists() else None
    v1_path = Path("results/score_backtest_v1.json")
    backtest_v1 = json.loads(v1_path.read_text()) if v1_path.exists() else None
    if backtest_v1:
        backtest_v1 = {k: backtest_v1[k] for k in ("top10", "bottom10", "all_eligible", "portfolio") if k in backtest_v1}
        backtest_v1["portfolio"].pop("curve", None)
    not_scored = [{"ticker": t, "reason": why_} for t, why_ in NOT_SCORED.items()]
    missing = [t for t in tickers if t not in feats and t not in NOT_SCORED]

    payload = {
        "as_of": str(as_of.date()), "built": str(date.today()),
        "market": {"spy": num(spy.iloc[-1], 2), "sma200": num(sma200, 2), "ok": bool(spy.iloc[-1] > sma200)},
        "weights": WEIGHTS, "stocks": stocks, "backtest": backtest, "backtest_v1": backtest_v1,
        "not_scored": not_scored, "missing": missing,
        "counts": {"scanned": len(stocks), "eligible": sum(s["eligible"] for s in stocks),
                   "top100": sum(s["universe"] == "top100" for s in stocks),
                   "fallen": sum(s["universe"] == "fallen" for s in stocks)},
    }
    js = json.dumps(payload, separators=(",", ":")).replace("</", "<\\/")
    html = TEMPLATE.read_text().replace("__DATA__", js)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html)
    el = [s for s in stocks if s["eligible"]]
    print(f"as of {as_of.date()}: {len(stocks)} scanned, {len(el)} eligible. Top 10:")
    for s in el[:10]:
        print(f"  {s['rank']:2d} {s['ticker']:6s} {s['score']:5.1f}  Q{s['quality']:3.0f} V{s['value']:3.0f} T{s['timing']:3.0f}  "
              f"dip {s['dip']:+.0f}%  P/E {s['pe']}  flags {s['n_flags']}  {s['verdict']}")
    print(f"wrote {OUT} ({OUT.stat().st_size / 1024:.0f} KB)")


if __name__ == "__main__":
    main()
