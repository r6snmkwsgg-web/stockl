#!/usr/bin/env python3
"""Step 5: daily scan. Downloads fresh prices and prints today's setups.

Usage:
    python scan_today.py                 # download fresh data, then scan
    python scan_today.py --no-download   # scan the data already on disk
    python scan_today.py --account 3000 --risk 0.02 --max-position 0.40

For every stock that matches the setup at the latest close, it prints:
  * the buy-stop price (yesterday's high: only buy if price goes above it),
  * the planned stop, using the estimated entry,
  * the number of shares for your account size and risk percentage.
The setup only becomes a trade if the price actually trades above the trigger
on the next day. Check earnings dates yourself: the script cannot (see README).
"""
import argparse
import math

import pandas as pd

from swing.backtest import prepare
from swing.data import download_all, load_all
from swing.strategy import MAX_STOP_PCT, plan_trade
from swing.universe import ALL_TICKERS, MARKET

ap = argparse.ArgumentParser()
ap.add_argument("--account", type=float, default=3000)
ap.add_argument("--risk", type=float, default=0.02, help="risk per trade, 0.02 = 2%%")
ap.add_argument("--max-position", type=float, default=0.40, help="max share of account in one stock")
ap.add_argument("--no-download", action="store_true")
ap.add_argument("--source", choices=["auto", "stooq", "yahoo"], default="auto")
args = ap.parse_args()

if not args.no_download:
    print("Downloading fresh prices ...")
    download_all(ALL_TICKERS, source=args.source, verbose=False)

prices = load_all(ALL_TICKERS)
spy, stocks, calendar = prepare(prices, MARKET)
today = calendar[-1]
spy_row = spy.iloc[-1]
spy_sma = spy["Close"].rolling(200).mean().iloc[-1]

print(f"\nData as of the close on {today.date()}")
print(f"SPY close {spy_row['Close']:.2f} vs 200-day average {spy_sma:.2f} -> "
      f"market filter {'ON (ok to buy)' if spy_row['market_ok'] else 'OFF (do not open new trades)'}")

rows = []
for t, d in stocks.items():
    r = d.iloc[-1]
    if not bool(r["setup"]):
        continue
    trigger = float(r["High"])
    entry = trigger * 1.001             # assume we get filled a hair above the trigger
    plan = plan_trade(entry, float(r["pullback_low"]), float(r["atr14"]))
    if plan is None:
        rows.append(dict(ticker=t, close=r["Close"], buy_above=trigger, stop=None, shares=0,
                         note=f"setup, but stop would be >{MAX_STOP_PCT:.0%} away: skip"))
        continue
    stop, rps = plan
    shares = math.floor(args.account * args.risk / rps)
    shares = min(shares, math.floor(args.account * args.max_position / entry))
    rows.append(dict(ticker=t, close=r["Close"], buy_above=trigger, stop=stop,
                     stop_pct=rps / entry, shares=shares, risk_dollars=shares * rps,
                     cost=shares * entry, rsi=r["rsi14"], ret_6m=r["ret126"],
                     note="" if shares > 0 else "too expensive for this account size"))

if not rows:
    print("\nNo stocks match the setup today.")
else:
    df = pd.DataFrame(rows).sort_values("ret_6m", ascending=False)
    pd.set_option("display.width", 200)
    print(f"\n{len(df)} setup(s). Account ${args.account:,.0f}, risk {args.risk:.0%} per trade "
          f"= ${args.account * args.risk:,.0f} per trade.\n")
    for _, r in df.iterrows():
        if r["shares"] and r["stop"]:
            print(f"{r['ticker']:6s} close {r['close']:8.2f} | BUY only if price > {r['buy_above']:.2f} "
                  f"| stop {r['stop']:.2f} ({r['stop_pct']:.1%} away) | {int(r['shares'])} shares "
                  f"(~${r['cost']:,.0f}, risk ~${r['risk_dollars']:.0f}) | RSI {r['rsi']:.0f} "
                  f"| 6-mo return {r['ret_6m']:+.0%} {r['note']}")
        else:
            print(f"{r['ticker']:6s} close {r['close']:8.2f} | trigger {r['buy_above']:.2f} | {r['note']}")
    print("\nReminder: skip any stock with an earnings report in the next 10 trading days "
          "(check the company's investor site or a finance website).")
    if not spy_row["market_ok"]:
        print("Reminder: the market filter is OFF, so the rules say do NOT open these trades.")
