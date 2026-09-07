# The score behind the Bargain Ledger, and how it was tested

*Fourth part of the project. The site is `site/index.html`, built by
`build_site.py` from `swing/score.py`; the test is `backtest_score.py`, with
outputs in `results/score_backtest.md` (current) and
`results/score_backtest_v1.md` (first version).*

## 1. What you asked for, and what is possible

You asked for a formula that finds the perfect stocks and makes no mistakes.
No such formula exists, for anyone, and a tool that claims otherwise is
selling something. What can be built is:

* a score based on what companies actually report to the SEC (revenue,
  profit, cash flow, balance sheet), not just on price patterns;
* every number shown, so you can see *why* a stock ranks where it does;
* a fair test of the score on the past, using only information that was
  public on each day, on a list that includes companies that later failed;
* a plain statement of how often it was right.

The last point is the honest replacement for "no mistakes": the current
score's top ten picks beat the index about half the time. That is the truth
of it, and it is better than the first version, which was worse than random.

## 2. The data

* **Prices**: daily, 2010 to 4 September 2026, Yahoo Finance.
* **Financial statements**: SEC EDGAR "company facts", free and without a
  key. Every reported value carries the date it was filed, so the backtest
  can use exactly what an investor could have known on a given day. Quarterly
  figures are derived from year-to-date ones where a company reports that
  way (cash flow, usually). Companies that moved to a new SEC registrant
  number (Exxon, BlackRock, Disney, APA) have their old history merged in.
* **Universe**: today's 100 largest US stocks plus 82 further companies that
  were once large or popular and later stalled or crashed (the control list
  has 95 entries; 9 overlap with the top 100 and 4 no longer trade). 181 of
  the 182 have usable filings; Berkshire is deliberately excluded because its reported
  profit swings with the market value of its investments, BioNTech files
  under international accounting rules, and four (Walgreens, US Steel,
  Kellogg, Square) no longer trade under their old symbol.

### How accurate is the parsing?

Every quarterly figure the parser derives was checked against the annual
total the company itself filed in its 10-K (`results/fundamentals_audit.csv`,
6,684 company-years from 2011). 93% of company-years produce exactly four
quarters; of those, 98.6% add up to the filed annual total within 1% and
99.3% within 5%. The mismatches are restatements around mergers and
spin-offs (GE, Danaher, Linde, Devon, Dominion), tiny-number cases where a
1% difference is a rounding error (Plug Power, Twilio), and old years.
Companies that changed the label they file a line item under (Target, Ford)
have their history stitched across labels; coverage for them rose from
about half of trading days to 95%.

## 3. The score

Each company is scored 0 to 100 on three questions, as a percentile against
the other companies on the same day.

**Quality, 70%.** Return on equity; free-cash-flow margin (net margin for
banks); revenue growth over the last year; the three-year share-price
record against SPY; whether the 200-day trend is rising. Companies with debt
above twice equity lose 15 points here.

**Value, 20%.** Price-to-earnings and price-to-sales versus the company's
own last five years (is it cheaper than it usually is?); earnings yield and
free-cash-flow yield versus peers (price-to-book for banks). Profit is
capped at after-tax operating profit so that a one-off gain, like Alphabet's
$112 billion quarter in 2026, cannot make a stock look cheap.

**Timing, 10%.** How far the price is below its 52-week high, whether that
high was set in the last 60 trading days, whether the price is still near
its 200-day average, and a penalty for an over-bought RSI.

**Red flags** are shown but not scored: losing money, negative free cash
flow, shrinking revenue or profit, heavy debt, very high volatility, more
than 20% below the 200-day average, P/E above 50 or in the top fifth of its
own history, profit boosted by one-off gains, stale filings, thin trading.

**Not scored at all** if: no profit or no free cash flow over the last 12
months, no filing for more than 135 days, price under $10, or under 500,000
shares traded a day.

## 4. The test

On the first trading day of each quarter from January 2012 to July 2025 (55
dates), every eligible company was scored with only the information public
that day. The ten highest-scoring were "bought" and their returns over the
next 3 and 12 months recorded, along with SPY's. A quarterly-rebalanced
basket of the top ten, paying 0.2% per quarter in costs, was compounded.

### First version (35% quality, 40% value, 25% timing, points off per flag)

Same corrected data, dates and costs as the current version below.

| Group | picks | avg 12-mo | median | vs SPY | beat SPY | vs avg stock | lost >20% |
|---|---|---|---|---|---|---|---|
| Top 10 by score | 550 | +13.4% | +11.7% | -2.0% | 44% | -4.9% | 15% |
| Bottom 10 by score | 550 | +19.6% | +15.0% | +4.2% | 49% | +1.3% | 8% |
| Every eligible stock | 5980 | +17.9% | +14.8% | +2.5% | 50% | -0.0% | 10% |

By score fifth, versus SPY: best fifth -0.8%, worst fifth +5.7%. The basket
compounded at 11.3% a year against SPY's 14.8%, worst fall -22%.

The top picks did worse than the bottom picks. Looking at the three parts
separately (both halves of the data agree):

| Ranking by | vs SPY, top 10, 2012-18 | 2019-25 | best fifth vs worst fifth |
|---|---|---|---|
| Quality alone | +4.2% | +9.5% | +2.6% vs -3.0% |
| Value alone | -1.3% | +0.1% | -0.7% vs +1.7% |
| Timing alone | -0.0% | -2.7% | -3.6% vs -0.2% |

Cheapness and dip-depth ranked stocks backwards. The cheap, dipping stocks
were mostly cheap for a reason, especially in the fallen group. Penalising
flags also hurt, because the flags punish volatility and drawdowns, which in
this period were where returns came from.

### Current version (70% quality, 20% value, 10% timing, no flag penalty)

Corrected run: share counts scaled for later splits, total returns with
dividends for the picks and for SPY, quarters measured rebalance to rebalance.

| Group | picks | avg 12-mo | median | vs SPY | beat SPY | vs avg stock | lost >20% |
|---|---|---|---|---|---|---|---|
| Top 10 by score | 550 | +18.8% | +15.6% | +3.4% | 51% | +0.5% | 14% |
| Top 10, from today's largest only | 450 | +22.1% | +19.1% | +6.5% | 56% | +3.4% | 11% |
| Top 10, from the fallen group only | 100 | +3.9% | -2.9% | -10.4% | 29% | -12.5% | 28% |
| Bottom 10 by score | 550 | +19.2% | +14.7% | +3.8% | 50% | +0.9% | 9% |
| Every eligible stock | 5980 | +17.9% | +14.8% | +2.5% | 50% | -0.0% | 10% |

SPY averaged +15.4% (total return) over the same windows. By score
fifth, versus SPY: best fifth +3.0%, worst fifth +1.9%.

Quarterly-rebalanced top-10 basket with costs: 21.0% a year against SPY's
14.8%, worst fall -29% against SPY's -24%, beat SPY in
60% of quarters.

### Is the edge real?

| Measure | dates | mean | t-stat | 90% bootstrap range |
|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 55 | +1.80% | 2.00 | +0.36% to +3.31% |
| Quarter vs average eligible stock | 55 | +1.18% | 1.30 | -0.27% to +2.71% |
| 12-mo vs SPY, January dates only | 14 | +6.89% | 1.52 | -0.11% to +14.32% |
| 12-mo vs average eligible, January only | 14 | +3.81% | 0.85 | -2.79% to +11.26% |

The fair yardstick is the average stock in the list, not SPY, because the
list itself beat SPY (half of it is today's winners). Against that yardstick
the top ten's edge is about 1.2 points a quarter with a range that includes
zero: it cannot be told apart from luck with this much data. The bottom ten
did as well as the top ten over 12 months. The edge over SPY is mostly the
list, not the score.

Full year-by-year tables are in `results/score_backtest.md`.

### The "undervalued on a dip" screen

The original brief was stocks that are undervalued, in a dip, and could run
back up to fair value. On the page that is the tick-box "Only undervalued on
a dip": quality, value and timing all 60 or more, meaning a strong business,
cheap against its own five-year history, and well off its 52-week high.
Tested the same point-in-time way (about 7 names a quarter, 341
stock-quarters):

| Screen | picks | avg 12-mo | median | vs SPY | beat SPY | vs avg stock | lost >20% |
|---|---|---|---|---|---|---|---|
| Whole list | 341 | +17.1% | +10.6% | -1.3% | 44% | -3.4% | 15% |
| From today's largest only | 238 | +23.3% | +15.0% | +4.3% | 53% | +2.1% | 10% |
| From the fallen group only | 103 | +3.0% | -1.2% | -14.4% | 24% | -16.0% | 27% |

Loosening the screen to 50 gives +0.3% vs SPY (46% beat); tightening it to
70 gives -14.9% (22% beat) on 37 picks. The pattern is the one the dip
study found: a dip in a strong company is a bargain only when the company
stays strong, and price and filings cannot tell you that in advance. The
companies that later fell were also "strong, cheap and dipping" on the day.

## 5. What to make of it

* **The score has a real but modest edge, and only on strong companies.**
  Its picks from today's largest companies beat SPY 58% of the time by 6.4
  points a year. Its picks from the fallen group lost to SPY 69% of the
  time. Survivorship bias explains part of the first number: we know those
  companies stayed large.
* **"Half the time" is what a good stock picker looks like.** Even the
  best-known professional factor strategies beat the index in roughly 55 to
  60% of years. A screen that promised more would be lying.
* **It is riskier than the index.** A 34% drawdown against 24%, and about
  one pick in seven lost more than 20% in its year.
* **The weights were chosen after looking at the results.** That is a
  form of data-snooping, kept as small as I could: one revision, in the
  direction the evidence pointed, with both halves of the data agreeing.
  It is still a reason to expect the future to be a little worse than the
  table above.
* **It chases the last cycle.** The quality questions reward recent
  profitability and a strong three-year record, so the top ten in January
  2023 was full of oil companies after the 2022 energy boom, and in January
  2022 it held Moderna, Meta and AMD right before they fell 25 to 60%. A
  quality screen is partly a momentum screen; it does not know when a cycle
  has ended.
* **Fundamentals lag and one-offs happen.** Gilead's $10.5 billion loss
  quarter in 2026 makes it "unscored" today although three of its last four
  quarters were profitable; the site says so on its card. Citi's last two
  quarters are missing from the SEC feed, so it shows as stale.

## 6. The site

`python build_site.py --download` refreshes prices and filings and writes
`site/index.html`, a single self-contained page: ranked table with sort,
search and filters; a card for each stock with a one-year price chart, the
three scores with the numbers behind them, key figures, and red flags; the
formula in plain language; and the record above, including the version that
did not work.
