"""Official events and headlines for each company, for the committee.

Two free sources:
  * SEC EDGAR "submissions": every filing a company made, with the item codes
    of its 8-K material-event reports (results, impairments, officer changes,
    acquisitions ...) and the dates of its quarterly reports, from which the
    next report date is estimated.
  * Yahoo Finance's per-ticker RSS headline feed: the last few headlines.

Saved as data/news/<TICKER>.json. Headlines are third-party text: shown to
the committee as data, never as instructions.
"""
from __future__ import annotations

import json
import re
import time
from datetime import date, timedelta
from pathlib import Path

import requests

from .fundamentals import UA, cik_map, EXTRA_CIKS

NEWS_DIR = Path(__file__).resolve().parent.parent / "data" / "news"
ITEMS = {
    "1.01": "material agreement", "1.02": "agreement terminated", "1.03": "bankruptcy", "2.01": "acquisition or disposal completed",
    "2.02": "results announced", "2.03": "new debt taken on", "2.04": "debt acceleration", "2.05": "restructuring or exit costs",
    "2.06": "impairment charge", "3.01": "listing standards notice", "3.02": "unregistered share sale", "4.01": "auditor change",
    "4.02": "restatement: past financials not reliable", "5.01": "change of control", "5.02": "officer or director change",
    "5.03": "charter or bylaw change", "5.07": "shareholder vote", "7.01": "investor disclosure", "8.01": "other event",
}
EVENT_DAYS = 120
HEADLINE_DAYS = 45
HEADLINES = 6


def _submissions(cik: int) -> dict | None:
    try:
        r = requests.get(f"https://data.sec.gov/submissions/CIK{cik:010d}.json", headers={"User-Agent": UA}, timeout=60)
        return r.json() if r.status_code == 200 else None
    except (requests.RequestException, ValueError):
        return None


def events_and_reports(cik: int, today: date) -> dict:
    d = _submissions(cik)
    if not d:
        return {"events": [], "last_report": None, "next_report_est": None}
    r = d["filings"]["recent"]
    rows = list(zip(r["form"], r["filingDate"], r.get("items", [""] * len(r["form"])), r.get("reportDate", [""] * len(r["form"]))))
    since = str(today - timedelta(days=EVENT_DAYS))
    events = []
    for form, filed, items, _ in rows:
        if form in ("8-K", "8-K/A") and filed >= since:
            names = [ITEMS[i.strip()] for i in items.split(",") if i.strip() in ITEMS and i.strip() not in ("9.01",)]
            if names:
                events.append({"date": filed, "what": ", ".join(dict.fromkeys(names))})
    reports = [(form, filed, period) for form, filed, items, period in rows if form in ("10-Q", "10-K", "20-F", "40-F")]
    last = {"form": reports[0][0], "filed": reports[0][1], "period": reports[0][2]} if reports else None
    nxt = None
    if reports:
        last_filed = date.fromisoformat(reports[0][1])
        # the same report a year earlier (350-380 days before the last one) tells us the company's rhythm
        prior = [f for f in reports if 350 <= (last_filed - date.fromisoformat(f[1])).days <= 380]
        following = None
        if prior:
            pf = date.fromisoformat(prior[0][1])
            later = sorted([date.fromisoformat(f[1]) for f in reports if date.fromisoformat(f[1]) > pf])
            following = later[0] if later else None
        est = (following + timedelta(days=365)) if following else (last_filed + timedelta(days=91))
        nxt = str(est)
    return {"events": events[:8], "last_report": last, "next_report_est": nxt}


def headlines(ticker: str, today: date) -> list[dict]:
    try:
        r = requests.get(f"https://feeds.finance.yahoo.com/rss/2.0/headline?s={ticker}&region=US&lang=en-US",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.status_code != 200:
            return []
    except requests.RequestException:
        return []
    out = []
    for it in re.findall(r"<item>(.*?)</item>", r.text, re.S):
        t = re.search(r"<title>(?:<!\[CDATA\[)?(.*?)(?:\]\]>)?</title>", it, re.S)
        dt = re.search(r"<pubDate>(.*?)</pubDate>", it)
        if not t:
            continue
        when = None
        if dt:
            m = re.search(r"(\d{1,2}) (\w{3}) (\d{4})", dt.group(1))
            if m:
                try:
                    when = date(int(m.group(3)), ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"].index(m.group(2)) + 1, int(m.group(1)))
                except ValueError:
                    when = None
        if when and (today - when).days > HEADLINE_DAYS:
            continue
        title = re.sub(r"\s+", " ", t.group(1)).strip()[:140]
        out.append({"date": str(when) if when else "", "title": title})
    return out[:HEADLINES]


def download_all(tickers, pause: float = 0.25, verbose: bool = True) -> dict[str, str]:
    NEWS_DIR.mkdir(parents=True, exist_ok=True)
    m = cik_map()
    today = date.today()
    status = {}
    for i, t in enumerate(tickers, 1):
        cik = m.get(t.upper()) or m.get(t.upper().replace("-", ""))
        rec = {"asof": str(today), "events": [], "last_report": None, "next_report_est": None, "headlines": []}
        if cik:
            rec.update(events_and_reports(cik, today))
            if not rec["last_report"]:
                for old in EXTRA_CIKS.get(t.upper(), []):
                    rec.update(events_and_reports(old, today))
                    if rec["last_report"]:
                        break
        rec["headlines"] = headlines(t, today)
        (NEWS_DIR / f"{t}.json").write_text(json.dumps(rec, separators=(",", ":")))
        status[t] = f"{len(rec['events'])} events, {len(rec['headlines'])} headlines, next report ~{rec['next_report_est']}"
        if verbose:
            print(f"[{i:3d}/{len(tickers)}] {t:6s} {status[t]}")
        time.sleep(pause)
    return status


def load(ticker: str) -> dict | None:
    f = NEWS_DIR / f"{ticker}.json"
    return json.loads(f.read_text()) if f.exists() else None
