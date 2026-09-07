# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 35%, value 40%, timing 25%; flag penalty 4 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 500 | +12.1% | +11.2% | -2.8% | 43% | -5.0% | +3.2% | 49% | 16% |
| Top 10, from today's top-100 | 338 | +15.7% | +13.0% | +1.7% | 49% | -0.8% | +3.7% | 51% | 14% |
| Top 10, from the fallen group | 162 | +4.7% | +3.4% | -12.1% | 31% | -13.6% | +2.2% | 44% | 20% |
| Bottom 10 by score | 500 | +18.0% | +13.6% | +3.1% | 49% | +0.9% | +3.6% | 50% | 9% |
| Every eligible stock (average) | 5482 | +17.0% | +13.3% | +1.8% | 49% | -0.0% | +4.2% | 50% | 10% |

SPY itself averaged +14.9% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 50 | -0.51% | -0.62 | -1.87% to +0.79% | 46% |
| Quarter vs average eligible stock | 50 | -1.03% | -1.51 | -2.17% to +0.06% | 42% |
| 12-mo vs SPY, January dates only | 12 | -2.03% | -0.43 | -9.45% to +5.81% | 42% |
| 12-mo vs average eligible, January only | 12 | -3.91% | -0.95 | -10.02% to +2.85% | 33% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 1119 | +13.7% | -1.4% | 45% |
| 2 | 1084 | +15.8% | +0.6% | 48% |
| 3 | 1088 | +17.0% | +1.8% | 51% |
| 4 | 1084 | +18.4% | +3.2% | 49% |
| 5 | 1107 | +20.2% | +5.0% | 50% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +26.2% | +5.0% | 57% |
| 2014 | 40 | +9.4% | +0.9% | 50% |
| 2015 | 40 | -3.9% | -9.1% | 38% |
| 2016 | 40 | +23.3% | +6.3% | 57% |
| 2017 | 40 | +19.3% | +2.2% | 42% |
| 2018 | 40 | -3.8% | -8.5% | 30% |
| 2019 | 40 | +18.4% | +6.6% | 55% |
| 2020 | 40 | +30.8% | -7.7% | 30% |
| 2021 | 40 | +8.6% | +3.4% | 57% |
| 2022 | 40 | +1.0% | -1.3% | 45% |
| 2023 | 40 | +7.3% | -20.8% | 20% |
| 2024 | 40 | +8.4% | -9.1% | 40% |
| 2025 | 30 | +17.8% | -2.1% | 47% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

325 stock-quarters, about 6.8 names per date on 48 of 55 dates: avg 12-mo +16.8%, median +10.2%, vs SPY -1.8%, beat SPY 43%, vs average stock -3.5%, lost >20% 15%.
From today's largest: 230 picks, vs SPY +4.5%, beat 53%. From the fallen group: 95 picks, vs SPY -17.3%, beat 20%.


## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +11.0% vs SPY +14.3%; total +269% vs +431%
* Max drawdown -22% vs SPY -24% (quarterly granularity)
* Beat SPY in 46% of quarters; 50 quarters
