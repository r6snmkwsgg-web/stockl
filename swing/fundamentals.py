"""Company financial statements from the SEC's EDGAR database (free, no key).

Every US-listed company files its numbers with the SEC. EDGAR exposes them as
"company facts": one JSON file per company with every reported value of every
line item (revenue, net income, cash flow ...) and, crucially, the date each
value was FILED. That lets us compute what an investor could have known on any
past date (point-in-time), which is what makes an honest backtest possible.

Data flow:
  download_all()  -> data/fundamentals/<TICKER>.json  (compact: only the tags we use)
  pit_frame()     -> a daily DataFrame of trailing-twelve-month figures, aligned to
                     the price calendar, each value appearing only from its filing date.
"""
from __future__ import annotations

import json
import time
from datetime import date, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import requests

FUND_DIR = Path(__file__).resolve().parent.parent / "data" / "fundamentals"
# The SEC asks automated clients to identify themselves in the User-Agent.
UA = "stockl research (personal project) jimmt7610@gmail.com"

# Line items we use, with the alternative tag names companies use for them.
FLOW_TAGS = {
    "revenue": ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax",
                "SalesRevenueNet", "RevenueFromContractWithCustomerIncludingAssessedTax",
                "RevenuesNetOfInterestExpense", "TotalRevenuesAndOtherIncome"],
    "net_income": ["NetIncomeLoss", "NetIncomeLossAvailableToCommonStockholdersBasic", "ProfitLoss"],
    "op_income": ["OperatingIncomeLoss"],
    "ocf": ["NetCashProvidedByUsedInOperatingActivities",
            "NetCashProvidedByUsedInOperatingActivitiesContinuingOperations"],
    "capex": ["PaymentsToAcquirePropertyPlantAndEquipment", "PaymentsToAcquireProductiveAssets",
              "PaymentsToAcquirePropertyPlantAndEquipmentAndIntangibleAssets"],
}
INSTANT_TAGS = {
    "equity": ["StockholdersEquity",
               "StockholdersEquityIncludingPortionAttributableToNoncontrollingInterest"],
    "cash": ["CashAndCashEquivalentsAtCarryingValue",
             "CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents"],
    "debt_lt": ["LongTermDebtNoncurrent", "LongTermDebt", "LongTermDebtAndCapitalLeaseObligations"],
    "debt_st": ["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings"],
}
# Companies that moved to a new SEC registrant number: the new number only
# carries recent filings, so we also pull the old number's history.
EXTRA_CIKS = {"XOM": [34088], "APA": [6769], "BLK": [1364742], "DIS": [1001039]}
DEI_SHARES = "EntityCommonStockSharesOutstanding"
SHARE_TAGS_INSTANT = ["CommonStockSharesOutstanding"]
SHARE_TAGS_FLOW = ["WeightedAverageNumberOfDilutedSharesOutstanding", "WeightedAverageNumberOfSharesOutstandingBasic"]
ALL_TAGS = sorted({t for v in FLOW_TAGS.values() for t in v} | {t for v in INSTANT_TAGS.values() for t in v}
                  | set(SHARE_TAGS_INSTANT) | set(SHARE_TAGS_FLOW))


# --------------------------------------------------------------------------- download
def cik_map() -> dict[str, int]:
    FUND_DIR.mkdir(parents=True, exist_ok=True)
    f = FUND_DIR / "company_tickers.json"
    if not f.exists() or (time.time() - f.stat().st_mtime) > 7 * 86400:
        r = requests.get("https://www.sec.gov/files/company_tickers.json",
                         headers={"User-Agent": UA}, timeout=60)
        r.raise_for_status()
        f.write_text(r.text)
    d = json.loads(f.read_text())
    return {v["ticker"].upper(): int(v["cik_str"]) for v in d.values()}


def fetch_facts(cik: int) -> dict | None:
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik:010d}.json"
    for attempt in range(4):
        try:
            r = requests.get(url, headers={"User-Agent": UA}, timeout=60)
            if r.status_code == 200:
                return r.json()
            if r.status_code == 404:
                return None
        except requests.RequestException:
            pass
        time.sleep(2 * (attempt + 1))
    return None


def compact(facts: dict) -> dict:
    """Keep only the tags we use, and only the fields we need."""
    out = {"tags": {}, "shares": []}
    gaap = facts.get("facts", {}).get("us-gaap", {})
    for tag in ALL_TAGS:
        if tag not in gaap:
            continue
        units = gaap[tag]["units"]
        vals = units.get("USD") or units.get("shares") or next(iter(units.values()))
        out["tags"][tag] = [
            {"s": v.get("start"), "e": v["end"], "v": v["val"], "f": v["filed"], "form": v.get("form")}
            for v in vals if v.get("form") in ("10-K", "10-Q", "10-K/A", "10-Q/A", "20-F", "40-F")
        ]
    dei = facts.get("facts", {}).get("dei", {})
    if DEI_SHARES in dei:
        out["shares"] = [{"e": v["end"], "v": v["val"], "f": v["filed"]}
                         for v in dei[DEI_SHARES]["units"]["shares"]]
    return out


def download_all(tickers, pause: float = 0.15, verbose: bool = True) -> dict[str, str]:
    FUND_DIR.mkdir(parents=True, exist_ok=True)
    m = cik_map()
    status = {}
    for i, t in enumerate(tickers, 1):
        cik = m.get(t.upper()) or m.get(t.upper().replace("-", ""))
        if cik is None:
            status[t] = "no CIK"
        else:
            facts = fetch_facts(cik)
            if facts is None:
                status[t] = "no facts"
            else:
                c = compact(facts)
                for old in EXTRA_CIKS.get(t.upper(), []):
                    older = fetch_facts(old)
                    if older:
                        oc = compact(older)
                        for tag, rows in oc["tags"].items():
                            c["tags"].setdefault(tag, [])
                            seen = {(r["s"], r["e"], r["f"]) for r in c["tags"][tag]}
                            c["tags"][tag] += [r for r in rows if (r["s"], r["e"], r["f"]) not in seen]
                        seen = {(r["e"], r["f"]) for r in c["shares"]}
                        c["shares"] += [r for r in oc["shares"] if (r["e"], r["f"]) not in seen]
                c["cik"] = cik
                c["name"] = facts.get("entityName")
                (FUND_DIR / f"{t}.json").write_text(json.dumps(c, separators=(",", ":")))
                status[t] = f"ok ({len(c['tags'])} tags)"
        if verbose:
            print(f"[{i:3d}/{len(tickers)}] {t:6s} {status[t]}")
        time.sleep(pause)
    return status


def load(ticker: str) -> dict | None:
    f = FUND_DIR / f"{ticker}.json"
    return json.loads(f.read_text()) if f.exists() else None


# --------------------------------------------------------------------------- parsing
def _d(s: str) -> date:
    return date.fromisoformat(s)


def quarterly(facts: list[dict]) -> pd.DataFrame:
    """Turn reported values into one value per fiscal QUARTER.

    Companies report some items per quarter (3-month periods) and others
    year-to-date (3, 6, 9, 12 months from the fiscal year start). For the
    latter we subtract consecutive year-to-date values. Returns columns
    end, val, filed (the date the value became public).
    """
    rows = [r for r in facts if r["s"] and r["e"] and r["v"] is not None]
    direct, ytd = [], {}
    for r in rows:
        s, e = _d(r["s"]), _d(r["e"])
        days = (e - s).days
        if 70 <= days <= 125:                    # a quarter (12 to 17 weeks)
            direct.append((e, float(r["v"]), _d(r["f"])))
        elif 150 <= days <= 380:                 # year-to-date
            ytd.setdefault(s, []).append((e, float(r["v"]), _d(r["f"])))
    out = {}
    for e, v, f in direct:                       # prefer the earliest filing of a period
        if e not in out or f < out[e][1]:
            out[e] = (v, f)
    # derive missing quarters from year-to-date differences
    by_start = {}
    for r in rows:
        s, e = _d(r["s"]), _d(r["e"])
        if 70 <= (e - s).days <= 380:
            by_start.setdefault(s, {})
            if e not in by_start[s] or _d(r["f"]) < by_start[s][e][1]:
                by_start[s][e] = (float(r["v"]), _d(r["f"]))
    for s, ends in by_start.items():
        seq = sorted(ends.items())
        prev_end, prev_val = s - timedelta(days=1), 0.0
        for e, (v, f) in seq:
            gap = (e - prev_end).days
            if e not in out and 70 <= gap <= 125:
                out[e] = (v - prev_val, f)
            prev_end, prev_val = e, v
    if not out:
        return pd.DataFrame(columns=["end", "val", "filed"])
    df = pd.DataFrame([(e, v, f) for e, (v, f) in out.items()], columns=["end", "val", "filed"])
    return df.sort_values("end").reset_index(drop=True)


def ttm(q: pd.DataFrame) -> pd.DataFrame:
    """Trailing-twelve-month sums: the last four quarters, if they are consecutive."""
    rows = []
    ends = list(q["end"])
    for i in range(3, len(q)):
        span = (ends[i] - ends[i - 3]).days
        if 240 <= span <= 300:                   # four consecutive quarters
            rows.append((ends[i], q["val"].iloc[i - 3:i + 1].sum(), q["filed"].iloc[i - 3:i + 1].max()))
    return pd.DataFrame(rows, columns=["end", "val", "filed"])


def instant(facts: list[dict]) -> pd.DataFrame:
    out = {}
    for r in facts:
        if r["s"] is None and r["v"] is not None:
            e, f = _d(r["e"]), _d(r["f"])
            if e not in out or f < out[e][1]:
                out[e] = (float(r["v"]), f)
    df = pd.DataFrame([(e, v, f) for e, (v, f) in out.items()], columns=["end", "val", "filed"])
    return df.sort_values("end").reset_index(drop=True)


def shares_series(sh: list[dict]) -> pd.DataFrame:
    """Shares outstanding from the filing cover page. Companies with several
    share classes report each class separately in the same filing: sum them."""
    by_filing = {}
    for r in sh:
        f = _d(r["f"])
        by_filing.setdefault(f, []).append((r["e"], float(r["v"])))
    rows = []
    for f, items in by_filing.items():
        # the latest cover date within the filing; sum all classes reported at that date
        latest = max(e for e, _ in items)
        rows.append((_d(latest), sum(v for e, v in items if e == latest), f))
    df = pd.DataFrame(rows, columns=["end", "val", "filed"])
    return df.sort_values("filed").reset_index(drop=True)


def _pick(tags: dict, candidates: list[str], kind: str) -> pd.DataFrame:
    """Combine the candidate tags for one line item.

    Companies change which tag they file a line item under (e.g. "Revenues"
    then "RevenueFromContractWithCustomer..."). The tag with the best recent
    coverage is the backbone; periods it lacks are filled from the others, so
    a tag switch in 2018 does not erase the years before it.
    """
    series = []
    for i, tag in enumerate(candidates):
        if tag not in tags:
            continue
        if kind == "flow_last":
            rows = [r for r in tags[tag] if r["s"] and r["e"] and 70 <= (_d(r["e"]) - _d(r["s"])).days <= 125]
            df = pd.DataFrame([(_d(r["e"]), float(r["v"]), _d(r["f"])) for r in rows],
                              columns=["end", "val", "filed"]).sort_values("end").drop_duplicates("end", keep="last")
        elif kind == "flow":
            df = quarterly(tags[tag])
        else:
            df = instant(tags[tag])
        if len(df):
            recent = df[df["end"] >= (date.today() - timedelta(days=5 * 365))]
            series.append(((len(recent), -i), df))
    if not series:
        return pd.DataFrame(columns=["end", "val", "filed"])
    series.sort(key=lambda x: x[0], reverse=True)
    out = series[0][1].copy()
    have = set(out["end"])
    for _, df in series[1:]:
        extra = df[~df["end"].isin(have)]
        if len(extra):
            out = pd.concat([out, extra])
            have |= set(extra["end"])
    return out.sort_values("end").reset_index(drop=True)


MAX_AGE_DAYS = 400   # a figure with no newer filing for this long is treated as unknown


def _to_daily(df: pd.DataFrame, calendar: pd.DatetimeIndex, col: str) -> pd.Series:
    """Point-in-time daily series: each value appears from the day it was filed
    and expires if the company stops reporting that line item."""
    if not len(df):
        return pd.Series(np.nan, index=calendar, name=col)
    s = df.sort_values("filed").drop_duplicates("filed", keep="last")
    filed = pd.to_datetime(s["filed"])
    ser = pd.Series(s["val"].to_numpy(), index=filed)
    ser = ser[~ser.index.duplicated(keep="last")].sort_index()
    stamp = pd.Series(ser.index, index=ser.index)
    full = calendar.union(ser.index)
    vals = ser.reindex(full).ffill().reindex(calendar)
    last_filed = stamp.reindex(full).ffill().reindex(calendar)
    age = (calendar - pd.DatetimeIndex(last_filed)).days
    return vals.where(pd.Series(age, index=calendar) <= MAX_AGE_DAYS).rename(col)


def pit_frame(ticker: str, calendar: pd.DatetimeIndex) -> pd.DataFrame | None:
    """Daily point-in-time fundamentals for one company."""
    data = load(ticker)
    if data is None:
        return None
    tags = data["tags"]
    cols = {}
    for name, cands in FLOW_TAGS.items():
        q = _pick(tags, cands, "flow")
        t = ttm(q) if len(q) else q
        cols[name + "_ttm"] = _to_daily(t, calendar, name + "_ttm")
        # the same figure one year earlier (for growth), also point-in-time
        if len(t) >= 5:
            lag = t.copy()
            lag["val"] = t["val"].shift(4)
            lag = lag.dropna()
            cols[name + "_ttm_1y"] = _to_daily(lag, calendar, name + "_ttm_1y")
        else:
            cols[name + "_ttm_1y"] = pd.Series(np.nan, index=calendar)
    for name, cands in INSTANT_TAGS.items():
        cols[name] = _to_daily(_pick(tags, cands, "instant"), calendar, name)
    sh = shares_series(data["shares"])
    if not len(sh) or (date.today() - sh["filed"].max()).days > 400:
        # no usable cover-page count (e.g. Alphabet): fall back to the balance sheet,
        # then to the diluted share count used for earnings per share
        alt = _pick(tags, SHARE_TAGS_INSTANT, "instant")
        if not len(alt) or (date.today() - alt["filed"].max()).days > 400:
            q = _pick(tags, SHARE_TAGS_FLOW, "flow_last")
            alt = q
        if len(alt):
            sh = alt
    cols["shares"] = _to_daily(sh, calendar, "shares")
    # how many of the last four quarters were profitable (spots one-off loss quarters)
    q_ni = _pick(tags, FLOW_TAGS["net_income"], "flow")
    if len(q_ni) >= 4:
        pos = q_ni.copy()
        pos["val"] = (q_ni["val"] > 0).astype(float).rolling(4).sum()
        pos["filed"] = q_ni["filed"].rolling(4).max() if False else q_ni["filed"]
        cols["ni_pos_quarters"] = _to_daily(pos.dropna(), calendar, "ni_pos_quarters")
    else:
        cols["ni_pos_quarters"] = pd.Series(np.nan, index=calendar)
    f = pd.DataFrame(cols)
    f["debt"] = f["debt_lt"].fillna(0) + f["debt_st"].fillna(0)
    f["fcf_ttm"] = f["ocf_ttm"] - f["capex_ttm"].fillna(0)
    f["fcf_ttm_1y"] = f["ocf_ttm_1y"] - f["capex_ttm_1y"].fillna(0)
    return f
