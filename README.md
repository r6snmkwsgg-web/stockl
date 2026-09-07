# Swing-trading backtest: "pullback to the 20-day EMA"

This repo tests a simple swing-trading strategy on real daily prices of the
100 largest US stocks, from 2010 to today, and gives you a script that scans
for today's setups.

**Read `REPORT.md` first.** It explains the rules, the results and, just as
important, the reasons the results are probably better than what you would get
in real life. **Then read `RESEARCH.md`**, which tests 13 changes to the rules
(including "hold a few days, take 20%") to see whether anything beats SPY.

## What is in here

| File | What it does |
|---|---|
| `download_data.py` | Step 1. Downloads daily prices for SPY + 100 stocks into `data/prices/`. |
| `run_backtest.py` | Steps 2-4. Runs the strategy in every version and writes `results/`. |
| `scan_today.py` | Step 5. Downloads fresh prices and prints today's setups with entry, stop and share count. |
| `research_variants.py` | Runs 13 rule variants, with costs and a first-half / second-half split. Writes `results/variants.md`. |
| `RESEARCH.md` | Write-up of the variant research. |
| `swing/universe.py` | The list of 100 stocks. |
| `swing/data.py` | Download / load code (stooq with Yahoo fallback). |
| `swing/indicators.py` | Moving averages, RSI, ATR, 52-week high/low, pullback detection. |
| `swing/strategy.py` | The trading rules as code, with every number in one place. |
| `swing/backtest.py` | The day-by-day account simulation (entries, stops, sizing, exits). |
| `swing/metrics.py` | Win rate, expectancy, CAGR, drawdown, etc. |
| `results/` | Trade lists, equity curves, summary tables and a chart from the last run. |
| `REPORT.md` | The written report. |

## How to run it

```bash
pip install -r requirements.txt

# 1. get the data (about 3-5 minutes; Yahoo is used if stooq refuses)
python download_data.py

# 2-4. run the backtest, results go into results/
python run_backtest.py

# extra: test 13 rule variants (about a minute)
python research_variants.py

# 5. any day after the close: what matches the setup today?
python scan_today.py                       # $3,000 account, 2% risk (defaults)
python scan_today.py --account 10000 --risk 0.01
python scan_today.py --no-download         # reuse the data already on disk
```

## Data source, honestly

The task asked for stooq.com. From the cloud machine used to build this repo,
stooq answered its CSV download with "Access denied", so the results were built
from **Yahoo Finance's public chart endpoint** instead (no API key). The
downloader still tries stooq first and falls back to Yahoo, so from a home
computer it may well use stooq. Both give split-adjusted daily open / high /
low / close / volume.

Prices are split-adjusted but not dividend-adjusted, which is what you want for
this kind of test (the $10 filter and the stop distances use real prices).

## Earnings dates

Rule 9 (skip trades with earnings in the next 10 trading days) is **not**
applied. Historical earnings dates back to 2010 for 100 companies are not
available for free without an API key, so the backtest cannot honour the rule
and the scanner prints a reminder to check earnings yourself. See the report
for what this means for the results.
