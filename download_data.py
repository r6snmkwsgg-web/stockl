#!/usr/bin/env python3
"""Step 1: download daily prices for SPY + 100 large US stocks (2010 -> today).

Usage:
    python download_data.py            # try stooq first, fall back to Yahoo
    python download_data.py --source yahoo
    python download_data.py --source stooq
"""
import argparse
from collections import Counter

from swing.data import download_all
from swing.universe import ALL_TICKERS

ap = argparse.ArgumentParser()
ap.add_argument("--source", choices=["auto", "stooq", "yahoo"], default="auto")
args = ap.parse_args()

used = download_all(ALL_TICKERS, source=args.source)
print("\nSummary:", dict(Counter(used.values())))
failed = [t for t, s in used.items() if s == "FAILED"]
if failed:
    print("Failed tickers:", failed)
