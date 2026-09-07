# Research: can a change to the rules beat SPY?

*Follow-up to `REPORT.md`. Same data (100 large US stocks + SPY, 2010 to
4 September 2026), same engine, same account sizing as Version A ($10,000,
1% risk, up to 5 positions). Produced by `research_variants.py`; the full
table is in `results/variants.md` and every trade list in `results/variants/`.*

## 1. The short version

I tested 13 changes to the rules, including your actual goal ("get in, hold a
few days, take 20%") and a "buy the dip" version aimed at temporarily
undervalued stocks. Each was run four ways: without costs, with a 0.1% cost
per buy and sell, and then on the first half (2011 to 2018) and the second
half (2019 to 2026) separately, with costs.

* **None of them comes anywhere near SPY.** SPY compounded at 12.2% a year
  (9.2% in the first half, 15.8% in the second). The best variant after
  costs made 2.1% a year, and it made 4.6% a year in the first half and lost
  1.2% a year in the second.
* **"Take 20% profit in a few days" almost never happens with these stocks.**
  Of 1,468 trades that tried it (10-day maximum hold), 10 reached +20%. That
  is 0.7%. With a 20-day hold, 21 out of 1,010 (2.1%). Without a strategy at
  all, the chance that a top-100 stock's high gets 20% above today's close
  within 5 trading days is 0.4%, and within 10 days 1.2%, and most of those
  are in four names: PLTR, AMD, TSLA and MU.
* **The best ideas improve the trade, not the result.** Wider stops and a
  looser exit lift the win rate from 34% to 54% and cut the drawdown from
  38% to 19%, but the average trade is still only +0.4% before costs. A
  strategy that makes 0.4% a trade and trades 80 times a year makes about 4%
  a year before costs and 2% after. Holding the index makes 12% for doing
  nothing.
* **"Buy the dip" has the best per-trade edge before costs** (64% win rate,
  8.8% a year with no costs) and is the closest thing to your "undervalued"
  idea. But it trades 3,100 times, holding 3 days each, and 0.1% costs turn
  8.8% a year into -1.1%. It is a strategy that pays your broker.

## 2. Is there "always a way" to beat SPY by swing trading?

I cannot prove there isn't, and neither can anyone else. What I can say is
what the evidence in front of us shows, and it points the other way:

1. **The stocks do not move enough.** These are the 100 biggest companies.
   Their typical best gain over the next 5 days is 2.3%; over 10 days 3.5%.
   A 20% target on a stock that normally moves 3% needs either a very rare
   event (usually earnings, which rule 9 says to avoid) or a much smaller,
   wilder stock, which comes with much bigger losses and worse fills.
2. **A few days is not long enough for "undervalued" to matter.** Value is a
   months-to-years idea. Over a few days, price moves are mostly noise plus
   news. That is why the dip-buying version wins often but wins tiny.
3. **Costs are the whole game at this holding period.** Every variant here
   has a per-trade edge between 0% and 0.5%. A 0.1% cost per side (0.2% per
   round trip) wipes out or halves all of them. A $3,000 account paying even
   a few cents of spread per share is in the same position.
4. **The test is rigged in the strategy's favour and it still loses.** The
   100 stocks are today's winners (survivorship bias, see the main report),
   the fills are perfect, there are no taxes. If the real world were kinder
   than this test, that would be a first.
5. **Anything that looks good here is partly luck.** With 13 variants, one or
   two will look best by chance. The first-half / second-half split is the
   check: the best variant's edge lived in 2011 to 2018 and vanished in 2019
   to 2026. That is the classic signature of a pattern that was never really
   there.

To beat SPY you would need a per-trade edge several times larger than
anything here, and it would have to survive costs, survive a universe of
stocks chosen without hindsight, and survive both halves of the data. I did
not find one in this family of ideas. That is a finding, not a failure to
look.

## 3. What was tested

Every variant keeps the same stock universe, the SPY 200-day market filter,
the 1% risk sizing, 5 slots max, no margin. "ATR" is the average daily range
in dollars. "R" is the dollars risked at entry.

| Variant | What changed |
|---|---|
| base | The rules exactly as given (the main report). |
| no time stop | Drop the "must be +1R after 10 days" exit. |
| EMA exit only after +2R partial | Before the partial, only the stop can take you out. |
| stop = 2xATR only | Always use 2xATR for the stop, not "whichever is closer". |
| 2xATR + EMA exit after partial | Both changes above. |
| 3xATR stop (max 12%) + EMA exit after partial | Wider stop again. |
| trailing stop under 5-day low, no partial | Let winners run, trail the stop. |
| take 20% / 10% / 5% profit, max 10 or 20 days | Your goal: fixed profit target, 2xATR stop, then get out. |
| buy the dip, exit close > 5-day average | New setup: uptrending stock, RSI(2) below 10 (a sharp 2-3 day drop), buy next open, sell when it bounces. |
| buy the dip, take 20% / 5%, max 10 days | Same setup, fixed profit target. |

## 4. Results

CAGR = average yearly growth rate. "costs" = 0.1% slippage on every buy and
every sell. Max drawdown is for the no-cost run.

| Variant | trades | win% | avg win R | avg loss R | exp R | avg % per trade | days | maxDD | CAGR full, no costs | CAGR full, costs | CAGR 2011-18, costs | CAGR 2019-26, costs |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| base (rules as given) | 1420 | 34% | +1.47 | -0.72 | +0.01 | +0.04% | 8.1 | -38% | -0.0% | -4.2% | -1.9% | -6.9% |
| no time stop | 1319 | 32% | +1.59 | -0.71 | +0.03 | +0.11% | 9.0 | -35% | +1.1% | -4.4% | -2.3% | -7.2% |
| EMA exit only after +2R partial | 1182 | 41% | +1.52 | -0.99 | +0.05 | +0.09% | 10.3 | -41% | +1.6% | -2.8% | -1.4% | -5.8% |
| stop = 2xATR only (not 'closer') | 1703 | 35% | +1.03 | -0.49 | +0.04 | +0.14% | 7.9 | -29% | +3.0% | -2.7% | -0.6% | -5.8% |
| 2xATR stop + EMA exit after partial | 1244 | 47% | +1.10 | -0.86 | +0.06 | +0.25% | 11.3 | -25% | +3.1% | +0.6% | +1.8% | -0.3% |
| 3xATR stop (max 12%) + EMA exit after partial | 1341 | 54% | +0.68 | -0.65 | +0.06 | +0.38% | 11.2 | -19% | +4.5% | +2.1% | +4.6% | -1.2% |
| trailing stop under 5-day low, no partial | 1859 | 33% | +1.02 | -0.53 | -0.01 | -0.04% | 6.4 | -44% | -1.2% | -5.8% | -6.0% | -6.3% |
| take 20% profit, 2xATR stop, max 10 days | 1468 | 48% | +1.04 | -0.87 | +0.05 | +0.17% | 8.6 | -31% | +3.4% | -1.7% | +0.9% | -3.8% |
| take 20% profit, 2xATR stop, max 20 days | 1010 | 41% | +1.55 | -0.96 | +0.07 | +0.34% | 13.5 | -30% | +1.8% | -0.3% | +3.1% | -3.9% |
| take 10% profit, 2xATR stop, max 10 days | 1498 | 48% | +1.02 | -0.86 | +0.05 | +0.16% | 8.3 | -25% | +3.7% | -1.7% | +1.3% | -3.1% |
| take 5% profit, 2xATR stop, max 10 days | 1722 | 51% | +0.93 | -0.87 | +0.05 | +0.19% | 7.0 | -23% | +4.7% | -1.3% | +0.6% | -2.2% |
| buy the dip (RSI2<10), exit close > 5-day avg | 3109 | 64% | +0.44 | -0.63 | +0.05 | +0.26% | 3.2 | -19% | +8.8% | -1.1% | -1.0% | -1.3% |
| buy the dip (RSI2<10), take 20%, max 10 days | 1507 | 52% | +0.97 | -0.81 | +0.11 | +0.50% | 9.0 | -23% | +8.2% | +0.5% | +4.0% | -1.2% |
| buy the dip (RSI2<10), take 5%, max 10 days | 1781 | 53% | +0.88 | -0.83 | +0.08 | +0.41% | 7.2 | -23% | +7.3% | +1.4% | +1.8% | +0.2% |
| SPY buy & hold (no dividends) |  |  |  |  |  |  |  | -34% | +12.2% | +12.2% | +9.2% | +15.8% |

### How the profit-target trades ended (no-cost runs)

| Variant | trades | hit the target | stopped out | ran out of time | avg % per trade |
|---|---|---|---|---|---|
| take 20%, max 10 days | 1468 | 10 (0.7%) | 557 | 896 | +0.17% |
| take 20%, max 20 days | 1010 | 21 (2.1%) | 523 | 461 | +0.34% |
| take 10%, max 10 days | 1498 | 85 (5.7%) | 560 | 848 | +0.16% |
| take 5%, max 10 days | 1722 | 503 (29%) | 625 | 590 | +0.19% |
| buy the dip, take 20%, max 10 days | 1507 | 8 (0.5%) | 467 | 1027 | +0.50% |
| buy the dip, take 5%, max 10 days | 1781 | 533 (30%) | 556 | 688 | +0.41% |

A 20% target on these stocks is not a plan, it is a lottery ticket: 99% of
the time the trade ends some other way. Even a 5% target is reached less than
a third of the time.

### How often does a 20% move happen at all?

Chance that a stock's high reaches X% above today's close within the next n
trading days, averaged over all 100 stocks and every day 2011 to 2026:

| within n days | >= 5% | >= 10% | >= 20% | median best gain |
|---|---|---|---|---|
| 3 | 9.7% | 1.7% | 0.2% | 1.7% |
| 5 | 16.9% | 3.5% | 0.4% | 2.3% |
| 10 | 31.1% | 8.7% | 1.2% | 3.5% |
| 20 | 48.7% | 19.3% | 3.8% | 5.3% |

A picker five times better than chance would still hit 20% within 10 days
only 6% of the time.

## 5. What would actually be worth trying next

I am not saying stop. I am saying the next step is not another exit rule.

1. **Change the goal, not the rules.** "20% in a few days" is the wrong
   target for large caps. "3 to 5% in a week with a 55% win rate and tiny
   costs" is what the data supports, and it still only pays if costs are near
   zero and the position is large enough that a 0.4% edge means real money.
2. **Test on the stocks that actually make 20% moves,** which means mid and
   small caps. Expect wider spreads, worse fills, more gaps, and a universe
   that must be built without hindsight (the list of small caps *as of each
   year*, including the ones that later went to zero). If the edge survives
   that, it is real. Most do not.
3. **Get real earnings dates.** The biggest single-trade wins and losses in
   every run were earnings gaps. A strategy that is really "bet on earnings"
   should be tested as that, on purpose.
4. **Longer holds.** The main report and this one both show the same thing:
   the strategy's few big winners (+5R and up) came from trades that were
   allowed to run for weeks. That is a different strategy (position or
   trend trading), and it is the one that has a chance of matching the index.
5. **Whatever you test, use 0.1% costs from the first run and keep a half of
   the data you never look at until the end.** Every "great" backtest I have
   seen fails one of those two.

## 6. Swing trading only the best businesses (added later)

Once the fundamentals-based quality score existed (see `RESEARCH_SCORE.md`),
the obvious question was whether swing trading works if you only trade the
top-quality names. `research_swing_quality.py` takes the best short-hold rule
found above ("buy the dip": RSI(2) below 10 in an uptrend, buy the next open,
sell at the first close above the 5-day average or after 10 days, 2 x ATR
stop, 1% risk, 5 positions) and allows it only on stocks whose quality score
is in the top 30% that day. Results in `results/swing_quality.md`:

| Run | trades | per year | win rate | avg % per trade | days held | CAGR | SPY CAGR |
|---|---|---|---|---|---|---|---|
| no costs | 2182 | 160 | 65% | +0.24% | 3.2 | +5.7% | +12.9% |
| 0.1% cost per side | 2205 | 161 | 61% | +0.06% | 3.1 | -1.1% | +12.9% |
| 2013-18, with costs | 889 | 148 | 58% | -0.12% | 3.1 | -6.1% | +9.4% |
| 2019-26, with costs | 1317 | 172 | 63% | +0.13% | 3.1 | +1.3% | +15.8% |

Sixty-five percent of trades win, and it still loses to the index by a mile,
because the average trade makes a quarter of one percent and a round trip
costs a fifth of one percent. The same names held for months (the Bargain
Ledger basket) compounded at about 21% a year over the same period. Same
stocks, same "buy the dip" instinct; the difference is entirely how long you
hold and how often you pay the spread.
