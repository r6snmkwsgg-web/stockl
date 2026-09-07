# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 500 | +18.7% | +15.6% | +3.8% | 51% | +1.6% | +5.6% | 55% | 14% |
| Top 10, from today's top-100 | 410 | +21.7% | +18.8% | +6.6% | 56% | +4.4% | +6.6% | 59% | 11% |
| Top 10, from the fallen group | 90 | +5.0% | -2.2% | -9.2% | 29% | -10.8% | +1.3% | 39% | 26% |
| Bottom 10 by score | 500 | +16.3% | +11.8% | +1.4% | 47% | -0.8% | +4.2% | 49% | 9% |
| Every eligible stock (average) | 5482 | +17.0% | +13.3% | +1.8% | 49% | -0.0% | +4.2% | 50% | 10% |

SPY itself averaged +14.9% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 50 | +1.92% | 1.95 | +0.33% to +3.51% | 62% |
| Quarter vs average eligible stock | 50 | +1.40% | 1.40 | -0.20% to +3.02% | 54% |
| 12-mo vs SPY, January dates only | 12 | +7.09% | 1.38 | -0.97% to +15.21% | 58% |
| 12-mo vs average eligible, January only | 12 | +5.21% | 0.98 | -3.22% to +13.75% | 58% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 1119 | +17.9% | +2.8% | 50% |
| 2 | 1084 | +17.0% | +1.9% | 49% |
| 3 | 1088 | +18.9% | +3.7% | 51% |
| 4 | 1084 | +15.4% | +0.3% | 48% |
| 5 | 1107 | +15.7% | +0.5% | 45% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +31.5% | +10.3% | 67% |
| 2014 | 40 | +14.5% | +6.0% | 62% |
| 2015 | 40 | -4.2% | -9.4% | 38% |
| 2016 | 40 | +22.6% | +5.6% | 62% |
| 2017 | 40 | +33.6% | +16.6% | 65% |
| 2018 | 40 | -0.2% | -4.9% | 35% |
| 2019 | 40 | +37.9% | +26.2% | 80% |
| 2020 | 40 | +40.1% | +1.6% | 40% |
| 2021 | 40 | +4.4% | -0.9% | 52% |
| 2022 | 40 | -5.5% | -7.8% | 38% |
| 2023 | 40 | +26.6% | -1.4% | 38% |
| 2024 | 40 | +22.4% | +4.9% | 52% |
| 2025 | 30 | +24.3% | +4.4% | 40% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

325 stock-quarters, about 6.8 names per date on 48 of 55 dates: avg 12-mo +16.8%, median +10.2%, vs SPY -1.8%, beat SPY 43%, vs average stock -3.5%, lost >20% 15%.
From today's largest: 230 picks, vs SPY +4.5%, beat 53%. From the fallen group: 95 picks, vs SPY -17.3%, beat 20%.


## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +20.9% vs SPY +14.3%; total +972% vs +431%
* Max drawdown -29% vs SPY -24% (quarterly granularity)
* Beat SPY in 60% of quarters; 50 quarters
