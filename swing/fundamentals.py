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

from .data import load_events

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
    "debt_noncurrent": ["LongTermDebtNoncurrent"],
    "debt_total": ["LongTermDebt", "LongTermDebtAndCapitalLeaseObligations"],
    "debt_st": ["LongTermDebtCurrent", "DebtCurrent", "ShortTermBorrowings"],
}
# Companies that moved to a new SEC registrant number: the new number only
# carries recent filings, so we also pull the old number's history.
EXTRA_CIKS = {"XOM": [34088], "APA": [6769], "BLK": [1364742], "DIS": [1001039], "GOOGL": [1288776]}
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
    year-to-date (3, 6, 9, 12 months from the fiscal year start). Values
    derived by subtracting consecutive year-to-date figures are preferred
    (a directly tagged fourth quarter is occasionally mis-tagged and later
    corrected; FY minus nine months is not), with direct 3-month facts as the
    fallback. Returns columns end, val, filed (the date the value became public).
    """
    rows = [r for r in facts if r["s"] and r["e"] and r["v"] is not None]
    direct, by_start = {}, {}
    for r in rows:
        s_, e = _d(r["s"]), _d(r["e"])
        days = (e - s_).days
        if not (70 <= days <= 380):
            continue
        f = _d(r["f"])
        if 70 <= days <= 125 and (e not in direct or f < direct[e][1]):   # earliest filing = as reported
            direct[e] = (float(r["v"]), f)
        by_start.setdefault(s_, {})
        if e not in by_start[s_] or f < by_start[s_][e][1]:
            by_start[s_][e] = (float(r["v"]), f)
    derived = {}
    for s_, ends in by_start.items():
        prev_end, prev_val, prev_f = s_ - timedelta(days=1), 0.0, None
        for e, (v, f) in sorted(ends.items()):
            gap = (e - prev_end).days
            if 70 <= gap <= 125:
                filed = f if prev_f is None else max(f, prev_f)
                if e not in derived or filed < derived[e][1]:
                    derived[e] = (v - prev_val, filed)
            prev_end, prev_val, prev_f = e, v, f
    out = dict(direct)
    out.update(derived)                          # derived wins where both exist
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
        by_filing.setdefault(f, set()).add((r["e"], float(r["v"])))     # a set: the same class listed twice counts once
    rows = []
    for f, items in by_filing.items():
        # the latest cover date within the filing; sum all classes reported at that date
        latest = max(e for e, _ in items)
        total = sum(v for e, v in items if e == latest)
        if total > 0:
            rows.append((_d(latest), total, f))
    df = pd.DataFrame(rows, columns=["end", "val", "filed"])
    return df.sort_values("filed").reset_index(drop=True)


def _pick(tags: dict, candidates: list[str], kind: str) -> pd.DataFrame:
    """Combine the candidate tags for one line item, period by period.

    Companies change which tag they file a line item under. For every period
    the value from the EARLIEST filing wins (that is what an investor saw
    first); ties go to the earlier tag in the candidate list. A window of four
    quarters can therefore mix tags around a switch; the audit in
    results/fundamentals_audit.csv measures how often that matters.
    """
    frames = []
    for i, tag in enumerate(candidates):
        if tag not in tags:
            continue
        if kind == "flow_last":
            rows = [r for r in tags[tag] if r["s"] and r["e"] and 70 <= (_d(r["e"]) - _d(r["s"])).days <= 125]
            df = pd.DataFrame([(_d(r["e"]), float(r["v"]), _d(r["f"])) for r in rows], columns=["end", "val", "filed"])
        elif kind == "flow":
            df = quarterly(tags[tag])
        else:
            df = instant(tags[tag])
        if len(df):
            df = df.assign(prio=i)
            frames.append(df)
    if not frames:
        return pd.DataFrame(columns=["end", "val", "filed"])
    out = pd.concat(frames).sort_values(["end", "filed", "prio"], kind="stable").drop_duplicates("end", keep="first")
    return out[["end", "val", "filed"]].reset_index(drop=True)


MAX_AGE_DAYS = 400   # a figure with no newer filing for this long is treated as unknown


def _to_daily(df: pd.DataFrame, calendar: pd.DatetimeIndex, col: str) -> pd.Series:
    """Point-in-time daily series: on each day, the value for the LATEST period
    among filings made on or before that day; expires if the company stops
    reporting the line item."""
    if not len(df):
        return pd.Series(np.nan, index=calendar, name=col)
    s = df.sort_values(["filed", "end"], kind="stable")
    s = s.groupby("filed", sort=True).tail(1)                 # per filing date: the most recent period
    s = s[s["end"] >= s["end"].cummax()]                      # an older comparative filed later never wins
    filed = pd.to_datetime(s["filed"])
    ser = pd.Series(s["val"].to_numpy(), index=filed)
    stamp = pd.Series(ser.index, index=ser.index)
    full = calendar.union(ser.index)
    vals = ser.reindex(full).ffill().reindex(calendar)
    last_filed = stamp.reindex(full).ffill().reindex(calendar)
    age = (calendar - pd.DatetimeIndex(last_filed)).days
    return vals.where(pd.Series(age, index=calendar) <= MAX_AGE_DAYS).rename(col)


def split_adjust(df: pd.DataFrame, splits: list) -> pd.DataFrame:
    """Put as-filed share counts on the same basis as split-adjusted prices:
    multiply each count by every split that happened AFTER it was filed."""
    if not len(df) or not splits:
        return df
    out = df.copy()
    factors = []
    for f in out["filed"]:
        fac = 1.0
        for d, r in splits:
            if _d(d) > f:
                fac *= r
        factors.append(fac)
    out["val"] = out["val"] * np.array(factors)
    return out


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
    splits = load_events(ticker).get("splits", [])
    sh = split_adjust(shares_series(data["shares"]), splits)
    alt = split_adjust(_pick(tags, SHARE_TAGS_INSTANT, "instant"), splits)
    dil = split_adjust(_pick(tags, SHARE_TAGS_FLOW, "flow_last"), splits)
    # cover-page count first; where it is missing (e.g. Alphabet, or before a
    # company started reporting it) fall back to the balance-sheet count, then
    # to the diluted count used for earnings per share
    shares = _to_daily(sh, calendar, "shares")
    diluted = _to_daily(dil, calendar, "diluted")
    shares = shares.fillna(_to_daily(alt, calendar, "alt")).fillna(diluted)
    # a cover-page count wildly different from the diluted count is a units error (thousands): use the diluted count
    ratio = shares / diluted
    cols["shares"] = shares.where(diluted.isna() | ratio.between(1 / 3, 3), diluted)
    # how many of the last four quarters were profitable (spots one-off loss quarters)
    q_ni = _pick(tags, FLOW_TAGS["net_income"], "flow")
    if len(q_ni) >= 4:
        pos = q_ni.copy()
        pos["val"] = (q_ni["val"] > 0).astype(float).rolling(4).sum()
        pos["filed"] = q_ni["filed"].rolling(4, min_periods=4).apply(lambda x: x.max(), raw=False) if False else \
            [max(q_ni["filed"].iloc[max(0, i - 3):i + 1]) for i in range(len(q_ni))]
        cols["ni_pos_quarters"] = _to_daily(pos.dropna(), calendar, "ni_pos_quarters")
    else:
        cols["ni_pos_quarters"] = pd.Series(np.nan, index=calendar)
    f = pd.DataFrame(cols)
    # LongTermDebtNoncurrent + current portion where the split is reported; otherwise the total
    f["debt"] = (f["debt_noncurrent"] + f["debt_st"].fillna(0)).where(f["debt_noncurrent"].notna(), f["debt_total"])
    f["fcf_ttm"] = f["ocf_ttm"] - f["capex_ttm"].fillna(0)
    f["fcf_ttm_1y"] = f["ocf_ttm_1y"] - f["capex_ttm_1y"].fillna(0)
    return f
