# Backtest report: "pullback to the 20-day EMA" swing strategy

*Data: daily prices, 4 January 2010 to 4 September 2026. Universe: SPY plus
100 of the largest US stocks. Written for a beginner, so every term is
explained the first time it is used.*

## 1. The short version

**The strategy, tested exactly as written, does not make money.**

* Version A ($10,000 account, 1% risk, up to 5 positions) finished 16.7 years
  at $9,954. That is a total return of -0.5%. Simply holding SPY over the same
  period returned +580%.
* Version B ($3,000 account, 2% risk, up to 3 positions, max 40% in one
  stock) finished at $2,458, a total return of -18%.
* Both versions had a worst peak-to-trough fall ("max drawdown") of about 40%,
  which is worse than SPY's 34%, for no return.
* The SPY 200-day market filter did **not** help. Without it, version A made
  +3.9% instead of -0.5%, and version B was unchanged. The filter cut the
  worst years (2011, 2022) but also cut the good ones.
* These numbers charge **no commissions or slippage**. With a modest 0.1%
  cost on each buy and each sell, version A loses 51% and version B loses 68%.
* The results are, if anything, **flattered** by the way the test had to be
  built (see section 6). Real life would very likely be worse, not better.

Why does it fail? Not because the entries are bad, but because the exit rule
is extremely tight relative to the entry. The rules buy a stock the moment it
touches its 20-day EMA, then sell at the next open after any close below that
same EMA. Since the entry is by definition right at the EMA, a single ordinary
down day ends the trade. A quarter of all trades were over after one day and
half within four days. Winners average about +1.5R, losers about -0.7R, and
only a third of trades win, which nets out to roughly zero.

## 2. What was tested, in plain language

A "swing trade" holds a stock for a few days to a few weeks. This particular
strategy tries to buy strong stocks during a short rest (a "pullback") and
ride the next leg up.

Below is each rule you gave, and exactly how it was implemented. Where a rule
left room for interpretation I say what I chose. All numbers live in
`swing/strategy.py`.

**Rule 1, market filter.** New trades are only opened on days when SPY (an
ETF that tracks the S&P 500) closed above the average of its last 200 closes.
Since 2011 this was true on 83% of days. The "no filter" versions skip this
check.

**Rule 2, stock filter.** On the setup day the stock must have: close above
its 50, 150 and 200-day simple moving averages; 200-day average higher than it
was 20 trading days earlier; close at least 75% of the highest high of the
last 252 trading days (one year) and at least 130% of the lowest low; average
daily volume over the last 50 days above 500,000 shares; close above $10.

**Rule 3, the setup.** "Pulled back 3 to 8 days" is measured as: the highest
high of the last 15 trading days happened 3 to 8 days ago, and today's close
is below that high. "Touch the 20-day EMA within 1%" means today's low came
down to within 1% of the EMA (or below it) while the close stayed no more than
1% under it. The 20-day EMA must be above the 50-day SMA, and RSI(14), a 0 to
100 gauge of recent momentum, must be between 40 and 60.

**Rule 4, entry.** The next day, buy if the price trades above the setup
day's high. The fill is that high, or the open if the stock opened higher
already (a "gap up"). If several stocks trigger on the same day and there are
not enough free slots, the ones with the strongest 6-month return are taken
first.

**Rule 5, stop.** Two candidate stops are computed: 0.1% below the lowest low
of the pullback, and 2 x ATR(14) below the entry (ATR is the average daily
trading range in dollars). The stop is whichever is **closer** to the entry.
If it is more than 8% below the entry the trade is skipped. In practice the
average stop was 3.2% below the entry, the median 3.0%.

**Rule 6, position size.** Shares = (account value x risk%) / (entry - stop),
rounded down. The account value used is the total value at the previous
close. The account never borrows: if there is not enough cash, the position is
cut to what cash allows, and the trade is skipped if cash covers less than
half the intended size. (Your rules did not say what to do here; that is my
assumption.) The 6% total-open-risk cap counts each position's risk as
shares x (entry - current stop), so a position whose stop is at breakeven
counts as zero.

**Rule 7, exits.** Each day, in this order: (a) if a "sell at open" decision
was made at yesterday's close, sell everything at today's open; (b) if the
stock opened at or below the stop, sell at the open; if the day's low touched
the stop, sell at the stop; (c) if the stock had not yet reached +2R and
today's high reached it, sell half at +2R (or at the open if it gapped above
the target) and move the stop to the entry price; (d) at the close, if the
close is below the 20-day EMA, or if it is trading day 10 or later, half not
yet sold, and the close is less than +1R above entry, mark the trade to be
sold at tomorrow's open. If a stop and the +2R target are both touched in the
same day, the stop is assumed to have hit first (the pessimistic choice).

"R" means the dollars risked on the trade at entry (shares x (entry - stop)).
A trade that makes twice what it risked is a +2R trade; a stop-out is -1R.

**Rule 8, limits.** Max 5 (A) or 3 (B) open positions and max 6% total open
risk. Version B also caps any one position at 40% of the account.

**Rule 9, earnings.** **Not applied.** Historical earnings dates for 100
companies back to 2010 are not available free of charge without an API key,
so the backtest could not skip trades around earnings. The consequences are
discussed in section 6. The daily scanner reminds you to check manually.

**Other choices.** No commissions, no slippage (except in the "costs"
versions), no dividends, no taxes, no interest on cash. Prices are
split-adjusted. The account is valued every day at closing prices. Any
position still open on 4 September 2026 is closed at that day's close so the
final number is real.

## 3. Results

### Headline numbers

R = dollars risked at entry. "Expectancy" is the average R made per trade;
a trader needs it clearly above zero after costs.

| Metric | A | A no filter | B | B no filter | A with costs | B with costs | SPY buy & hold |
|---|---|---|---|---|---|---|---|
| Number of trades | 1420 | 1606 | 1147 | 1301 | 1468 | 1212 |  |
| Win rate | 33.5% | 34.5% | 32.8% | 33.2% | 32.4% | 30.8% |  |
| Average win (R) | +1.47 | +1.42 | +1.61 | +1.56 | +1.46 | +1.56 |  |
| Average loss (R) | -0.72 | -0.72 | -0.75 | -0.75 | -0.75 | -0.79 |  |
| Expectancy per trade (R) | +0.01 | +0.02 | +0.02 | +0.02 | -0.04 | -0.06 |  |
| Average profit per trade ($) | -0.03 | +0.24 | -0.47 | -0.42 | -3.48 | -1.69 |  |
| Profit factor (gross wins / gross losses) | 1.00 | 1.01 | 0.97 | 0.97 | 0.89 | 0.81 |  |
| Total return | -0.5% | +3.9% | -18.1% | -18.2% | -51.0% | -68.1% | +579.6% |
| CAGR (average yearly growth) | -0.0% | +0.2% | -1.2% | -1.2% | -4.2% | -6.6% | +12.2% |
| Max drawdown | -37.8% | -36.3% | -40.2% | -42.0% | -57.1% | -73.3% | -34.1% |
| Longest losing streak (trades) | 18 | 17 | 19 | 16 | 18 | 19 |  |
| Average days held | 8.1 | 8.0 | 7.8 | 7.7 | 7.9 | 7.3 |  |
| Trades per year | 85 | 96 | 69 | 78 | 88 | 73 |  |
| Time with at least one position open | 78% | 88% | 78% | 88% | 78% | 78% |  |
| Final account value ($) | 9,954 | 10,387 | 2,458 | 2,455 | 4,903 | 958 |  |

"With costs" = the same rules paying 0.1% slippage on every buy and every
sell (a realistic all-in cost for a small account using a zero-commission
broker; market orders in large stocks often cost less, but stop orders in a
falling market often cost more). Note the SPY column ignores dividends, which
would add roughly another 1.5% a year to it.

### Year by year

Return on the account in each calendar year. 2010 is zero because indicators
need a year of history before the first signal; 2026 is a part year.

| Year | A | A no filter | B | B no filter | A with costs | B with costs | SPY |
|---|---|---|---|---|---|---|---|
| 2011 | -15.0% | -23.2% | -4.5% | -11.3% | -18.9% | -12.4% | -0.2% |
| 2012 | +10.5% | +13.1% | -5.2% | -3.6% | +3.9% | -9.2% | +13.5% |
| 2013 | +22.9% | +17.5% | +19.6% | +20.3% | +20.0% | +12.0% | +29.7% |
| 2014 | -14.7% | -14.9% | -8.5% | -7.0% | -20.6% | -13.6% | +11.3% |
| 2015 | -7.8% | +9.1% | -12.0% | +6.9% | -16.0% | -22.7% | -0.8% |
| 2016 | +14.7% | +14.9% | +5.0% | +4.6% | +6.8% | +0.0% | +9.6% |
| 2017 | +22.2% | +21.9% | +18.9% | +7.3% | +25.4% | +4.8% | +19.4% |
| 2018 | -6.2% | -4.3% | -5.4% | -6.0% | -7.1% | -9.9% | -6.3% |
| 2019 | +3.7% | +10.7% | -5.7% | +2.3% | -2.3% | -5.4% | +28.8% |
| 2020 | -2.3% | -3.6% | +3.7% | -1.9% | -4.3% | -0.3% | +16.2% |
| 2021 | -13.7% | -12.3% | -1.1% | -3.5% | -14.6% | -16.9% | +27.0% |
| 2022 | -6.4% | -16.4% | -6.3% | -10.9% | -7.8% | -8.1% | -19.5% |
| 2023 | +9.2% | +18.4% | -3.0% | +6.9% | +2.1% | -2.8% | +24.3% |
| 2024 | -6.6% | -3.2% | -7.5% | -8.2% | -9.3% | +2.1% | +23.3% |
| 2025 | -0.5% | -1.6% | +2.8% | -1.1% | -11.6% | -13.5% | +16.4% |
| 2026 (to 4 Sep) | +0.3% | -7.4% | -5.0% | -9.5% | -3.1% | -8.1% | +12.9% |

The equity curves are in `results/equity_curves.png`. Every trade is listed in
`results/trades_<version>.csv` and the daily account value in
`results/equity_<version>.csv`.

### Does the SPY 200-day filter help?

Not in this test.

* Version A: with the filter -0.5%, without it +3.9%. Max drawdown 37.8% vs
  36.3%. The filter removed 186 trades (12%).
* Version B: -18.1% either way. Drawdown 40.2% with, 42.0% without.
* Where the filter earned its keep: 2011 (-15% vs -23%) and 2022 (-6% vs
  -16%), the two years SPY spent longest below its 200-day average.
* Where it cost: 2015 (-8% vs +9%), 2019, 2023. Those were choppy years
  where SPY dipped below the average, the filter switched off, and the
  strategy missed the rebounds.

So the filter does what it is designed to do (less damage in bear markets)
but it pays for that protection by missing recoveries, and over 16 years the
two effects cancel. With an expectancy near zero there is nothing for a
filter to improve; it only changes *which* zero-sum trades you take.

## 4. Why the strategy breaks even: what the trades look like

Version A, 1,420 trades:

| How the trade ended | Trades | Share | Average R |
|---|---|---|---|
| Close below the 20-day EMA, sold next open | 914 | 64% | +0.25 |
| Initial stop hit | 276 | 19% | -1.00 |
| 10-day time stop (not up 1R yet) | 132 | 9% | +0.61 |
| Gapped down through the stop | 49 | 3% | -1.29 |
| Breakeven stop after taking half at +2R | 43 | 3% | +1.00 |
| Still open at the end of the data | 5 | | +0.65 |

Only 19% of trades ever reached the +2R partial target. Half of all trades
were over within 4 trading days and a quarter after a single day.

The reason is the geometry of the rules. You buy on the day *after* the stock
touched its 20-day EMA, at a price a little above it. The exit is "first close
below the 20-day EMA". A stock that is resting on its EMA closes below it on
roughly half of ordinary days, so most trades are cut off for a small loss or
small gain long before the trend has a chance to resume. When a trade does
work, the same rule tends to sell after the first pause, so winners average
only about +1.5R. A 33% win rate with +1.5R winners and -0.7R losers is a coin
flip.

None of this is a criticism of the individual ideas (trend filter, pullback,
tight stop, partial profits). They are standard. It is the combination of a
touch-the-EMA entry with a close-below-the-EMA exit that gives the trade no
room to breathe. I did not test any changes to the rules because you asked
for exactly these; section 7 lists the changes I would look at first.

### The position-size trap

With a 1% risk and a 3% stop, a single position is about a third of the
account (median cost $3,091 on a $10,000 account). Cash runs out after three
positions, so the "max 5 positions" rule almost never bound (5 positions were
open on only 17% of days); cash did. Version A averaged 2.7 open positions.

Version B is worse. Two percent of $3,000 is $60 of risk; with a 3% stop that
is a $2,000 position, which the 40%-of-account cap cuts to $1,200. So the cap
means version B actually risked only about 0.9% per trade on the median trade
($26), not 2%. And a $1,200 position in a $300 stock is 4 shares, so "sell
half" often means "sell 2 shares". 14% of version B's trades had 3 shares or
fewer. Small accounts cannot follow these rules precisely.

## 5. Data: what was used and why not stooq

You asked for stooq.com. From the cloud machine used to build this,
stooq's CSV download endpoint answered "Access denied" for every request
(after passing its browser check), so it could not be used. The prices in this
repo come from **Yahoo Finance's public chart endpoint**, which needs no API
key and gives the same daily open/high/low/close/volume. `download_data.py`
still tries stooq first and falls back to Yahoo, so from a home computer it
may well work with stooq.

Two tickers in the original list have been renamed: Marsh McLennan is now
`MRSH` and Fiserv is now `FISV`. Both are included under their new symbols.
Companies that listed after 2010 (META 2012, PANW 2012, ABBV 2013, UBER 2019, PLTR 2020, and so on) simply enter the test when their
data begins.

Data quality note: one trade, TMUS in April 2013, lost 7.8R on a gap. That was
the MetroPCS merger and reverse split, so it is a data artefact rather than a
real trade. It is one trade of 1,420 and does not change any conclusion.

## 6. Honesty section: why real results would probably be worse

**Survivorship bias, the big one.** The 100 stocks are the largest companies
*today*. Every one of them is a company that grew enormously between 2010 and
2026. In 2010 nobody could have known that NVDA, TSLA, AVGO, LLY or PLTR would
end up on this list, and the list of "100 largest stocks" back then contained
names like GE (at its peak), Citigroup, Exxon as the biggest company in the
world, Intel, IBM, AT&T, and others that went sideways or down for a decade.
Testing a "buy strong stocks" strategy on a list of stocks you already know
went up is like testing a horse-betting system only on horses you already know
won. **A strategy that only breaks even on a universe this favourable is a
serious warning sign.** With a realistic universe (the largest stocks as of
each date, including the ones that later shrank), the trend filter would have
kept you in more stocks that then fell.

**No earnings filter (rule 9).** Companies report earnings four times a year,
and the stock often gaps 5 to 15% overnight. The test could not skip trades
before earnings. Looking at the worst losses, this cut both ways: the largest
gap losses (NFLX -3.1R on its April 2024 report, NFLX -3.1R in April 2021,
AMD -2.8R in February 2026) were earnings gaps, but some of the biggest wins
were also earnings gaps in the right direction. Applying the rule would make
the loss distribution less scary (fewer -3R trades) but would also remove
roughly 15% of trading days from the calendar. The net effect on expectancy
is unknown; I would not assume it is positive.

**No costs in the main runs.** The cost run (0.1% per side) turns a break-even
system into a losing one, because the strategy trades about 85 times a year
and holds for 8 days. Any strategy this active is a costs strategy first and a
signal strategy second.

**Ideal fills.** Stops are assumed to fill exactly at the stop price unless
the stock gapped, and buy-stops exactly at the trigger. In real trading a stop
order becomes a market order and fills a little worse, especially on fast down
days. Partial exits at +2R are assumed filled exactly at the target.

**Cash-only, valued at the close.** No margin, no interest on idle cash (which
would have added a little in 2023-2026), dividends ignored (small effect for
8-day holds).

**Rule interpretation.** "Pulled back 3 to 8 days", "touch within 1%" and
"just below the pullback low" all needed precise definitions (section 2).
Different reasonable definitions would give different trade lists. I did not
tune these definitions to improve results; they are the first reasonable
version I wrote and were not changed after seeing the numbers.

**One data source.** Yahoo's free history has occasional bad prints. I did
not cross-check it against a second source.

**Sixteen years is one sample.** 2010-2026 was, apart from 2022, one long
bull market with the biggest stocks leading. Even a strategy that worked here
would need testing on other periods and other markets before trusting it.

## 7. What I would look at next (not tested; outside the brief)

1. **Give the trade room.** Exit on a close below the 20 EMA only *after* the
   +2R partial, and use the initial stop before that. Or trail the stop under
   the lowest low of the last 5 days instead of the EMA.
2. **Wider stops, smaller size.** A 3% stop on a stock that moves 2% a day is
   noise. Using 2 x ATR as the stop (not "whichever is closer") would cut the
   number of trades that stop out on the first down day.
3. **Fewer, better trades.** Require the pullback to be on falling volume, or
   require the stock to be in the top 20% by 6-month return.
4. **Realistic universe.** Rebuild the test with the top 100 stocks *as of
   each year*, from an old S&P 500 list. This is the change most likely to
   make the results worse, which is exactly why it is worth doing.
5. **Costs first.** Whatever the rules, include 0.1% per side from the start
   and only trust strategies that survive it.

## 8. Using the daily scanner

```bash
python scan_today.py                      # downloads fresh data, $3,000 at 2%
python scan_today.py --account 10000 --risk 0.01
```

It prints, for every stock that matched the setup at the last close: the
price it must trade above tomorrow to trigger a buy, the stop, how far away
the stop is, and the share count for your account and risk. Example output
from 4 September 2026:

```
SPY close 770.19 vs 200-day average 712.15 -> market filter ON (ok to buy)

ADP    close   277.62 | BUY only if price > 280.67 | stop 276.17 (1.7% away) | 4 shares (~$1,124, risk ~$19)
TMO    close   613.78 | BUY only if price > 615.74 | stop 598.92 (2.8% away) | 1 shares (~$616, risk ~$17)
AMZN   close   258.51 | BUY only if price > 261.12 | stop 251.68 (3.7% away) | 4 shares (~$1,046, risk ~$39)
ANET   close   193.78 | trigger 197.10 | setup, but stop would be >8% away: skip
```

The share counts show the small-account problem from section 4: the intended
risk is $60 a trade, but the 40% cap and whole-share rounding cut it to $17-39.

Given the results above, I would treat the scanner as a way to *study* the
setup, not as a signal to trade real money.
