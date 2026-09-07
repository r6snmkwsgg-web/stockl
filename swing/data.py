"""Download and load daily price data.

Two sources are supported:

* stooq.com  - the source the project was originally asked to use. It works
               from a normal home computer, but from some cloud/data-center
               networks stooq answers "Access denied", so it cannot be relied on.
* Yahoo Finance's public chart endpoint - no API key needed. This is the
               fallback and is what the results in the report were built from.

Prices from both sources are split-adjusted (a 4-for-1 split does not show up
as a 75% crash) but NOT dividend-adjusted. That is what we want: the $10 price
filter and the stop distances should use real traded prices.

Each ticker is saved as data/prices/<TICKER>.csv.gz (gzip-compressed CSV) with columns
Date,Open,High,Low,Close,Volume.
"""
from __future__ import annotations

import io
import json
import time
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import requests

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "prices"
EVENTS_DIR = Path(__file__).resolve().parent.parent / "data" / "events"   # splits and dividends
START = "2010-01-01"
# Keep this short: Yahoo answers "429 Too Many Requests" to long browser-style
# user-agent strings sent from scripts, but accepts a plain one.
UA = "Mozilla/5.0"
COLS = ["Open", "High", "Low", "Close", "Volume"]
OPT_COLS = ["AdjClose"]          # split- AND dividend-adjusted close (total-return basis)


def _clean(df: pd.DataFrame) -> pd.DataFrame:
    df = df[COLS + [c for c in OPT_COLS if c in df.columns]].astype(float)
    df = df[~df.index.duplicated(keep="last")].sort_index()
    df = df.dropna(subset=["Close"])
    df = df[(df["Volume"] >= 0) & (df["Close"] > 0)]
    df.index.name = "Date"
    return df


def fetch_stooq(ticker: str, start: str = START) -> pd.DataFrame | None:
    """Try stooq's CSV export. Returns None if stooq refuses or sends HTML."""
    sym = ticker.replace("-", ".").lower() + ".us"
    url = (f"https://stooq.com/q/d/l/?s={sym}&i=d"
           f"&d1={start.replace('-', '')}&d2={datetime.now().strftime('%Y%m%d')}")
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
    except requests.RequestException:
        return None
    text = r.text.strip()
    if r.status_code != 200 or not text.startswith("Date,"):
        return None
    df = pd.read_csv(io.StringIO(text), parse_dates=["Date"], index_col="Date")
    return _clean(df)


def fetch_yahoo(ticker: str, start: str = START) -> pd.DataFrame | None:
    """Yahoo Finance chart endpoint (no key needed)."""
    p1 = int(datetime.strptime(start, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())
    p2 = int(time.time()) + 86400
    url = (f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
           f"?period1={p1}&period2={p2}&interval=1d&events=div,splits")
    for attempt in range(5):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=30)
            if r.status_code == 200:
                break
            if r.status_code == 429:          # rate limited: back off hard
                time.sleep(15 * (attempt + 1))
                continue
        except requests.RequestException:
            pass
        time.sleep(3 * (attempt + 1))
    else:
        return None
    js = r.json()
    res = js.get("chart", {}).get("result")
    if not res:
        return None
    res = res[0]
    ts = res.get("timestamp")
    if not ts:
        return None
    q = res["indicators"]["quote"][0]
    cols = {"Open": q["open"], "High": q["high"], "Low": q["low"], "Close": q["close"], "Volume": q["volume"]}
    adj = res["indicators"].get("adjclose")
    if adj and adj[0].get("adjclose"):
        cols["AdjClose"] = adj[0]["adjclose"]
    df = pd.DataFrame(cols, index=pd.to_datetime(ts, unit="s", utc=True).tz_convert("America/New_York").normalize().tz_localize(None))
    # splits and dividends: needed to put SEC share counts on the same basis as adjusted prices
    ev = res.get("events", {})
    splits = sorted((str(pd.to_datetime(v["date"], unit="s", utc=True).tz_convert("America/New_York").date()),
                     float(v["numerator"]) / float(v["denominator"]))
                    for v in ev.get("splits", {}).values() if float(v.get("denominator", 0)) > 0)
    divs = sorted((str(pd.to_datetime(v["date"], unit="s", utc=True).tz_convert("America/New_York").date()), float(v["amount"]))
                  for v in ev.get("dividends", {}).values())
    EVENTS_DIR.mkdir(parents=True, exist_ok=True)
    (EVENTS_DIR / f"{ticker}.json").write_text(json.dumps({"splits": splits, "dividends": divs}))
    return _clean(df)


def download_all(tickers, source: str = "auto", pause: float = 1.5, verbose: bool = True):
    """Download every ticker and save CSVs. Returns a dict ticker -> source used."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    used = {}
    for i, t in enumerate(tickers, 1):
        df = None
        if source in ("auto", "stooq"):
            df = fetch_stooq(t)
            if df is not None and len(df):
                used[t] = "stooq"
        if df is None and source in ("auto", "yahoo"):
            df = fetch_yahoo(t)
            if df is not None and len(df):
                used[t] = "yahoo"
        if df is None or not len(df):
            used[t] = "FAILED"
            if verbose:
                print(f"[{i:3d}/{len(tickers)}] {t:6s} FAILED")
            continue
        df.to_csv(DATA_DIR / f"{t}.csv.gz", float_format="%.4f")
        if verbose:
            print(f"[{i:3d}/{len(tickers)}] {t:6s} {used[t]:6s} {len(df):5d} rows "
                  f"{df.index[0].date()} -> {df.index[-1].date()}")
        time.sleep(pause)
    return used


def load(ticker: str) -> pd.DataFrame:
    return pd.read_csv(DATA_DIR / f"{ticker}.csv.gz", parse_dates=["Date"], index_col="Date")


def load_events(ticker: str) -> dict:
    """{"splits": [(date, ratio), ...], "dividends": [(date, amount), ...]} (empty if unknown)."""
    f = EVENTS_DIR / f"{ticker}.json"
    return json.loads(f.read_text()) if f.exists() else {"splits": [], "dividends": []}


def load_all(tickers) -> dict[str, pd.DataFrame]:
    out = {}
    for t in tickers:
        f = DATA_DIR / f"{t}.csv.gz"
        if f.exists():
            out[t] = load(t)
    return out
