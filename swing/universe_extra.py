"""Mid-cap and small-cap universes: the S&P MidCap 400 and S&P SmallCap 600
constituent lists (from Wikipedia, with GICS sectors), saved in
data/universes/. Chosen by an index committee, not by us, so the only
hindsight is that they are today's members.
"""
from pathlib import Path

GICS = {"Information Technology": "Technology", "Communication Services": "Communication", "Consumer Discretionary": "Consumer",
        "Consumer Staples": "Consumer", "Financials": "Financials", "Health Care": "Health care", "Industrials": "Industrials",
        "Energy": "Energy & materials", "Materials": "Energy & materials", "Utilities": "Utilities & real estate",
        "Real Estate": "Utilities & real estate"}
_DIR = Path(__file__).resolve().parent.parent / "data" / "universes"


def _read(name):
    f = _DIR / name
    out = {}
    if not f.exists():
        return out
    for line in f.read_text().splitlines():
        cells = line.split("\t")
        if len(cells) >= 3:
            t = cells[0].strip().replace(".", "-")
            out[t] = {"name": cells[1].strip(), "sector": GICS.get(cells[2].strip(), "Other")}
    return out


MID_INFO = _read("sp400.tsv")
SMALL_INFO = _read("sp600.tsv")
MID = sorted(MID_INFO)
SMALL = sorted(t for t in SMALL_INFO if t not in MID_INFO)
EXTRA_SECTORS = {**{t: v["sector"] for t, v in SMALL_INFO.items()}, **{t: v["sector"] for t, v in MID_INFO.items()}}
EXTRA_NAMES = {**{t: v["name"] for t, v in SMALL_INFO.items()}, **{t: v["name"] for t, v in MID_INFO.items()}}
