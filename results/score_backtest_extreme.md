# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 500 | +13.9% | +7.1% | -1.1% | 44% | +0.2% | +3.1% | 46% | 23% |
| Top 10, from today's top-100 | 143 | +19.6% | +15.0% | +4.6% | 55% | +4.0% | +6.1% | 57% | 15% |
| Top 10, from the fallen group | 0 | +nan% | +nan% | +nan% | nan% | +nan% | +nan% | nan% | nan% |
| Bottom 10 by score | 500 | +14.2% | +7.9% | -0.8% | 44% | +0.4% | +3.5% | 49% | 19% |
| Every eligible stock (average) | 14526 | +14.5% | +9.3% | -1.3% | 43% | -0.0% | +3.3% | 46% | 17% |

SPY itself averaged +14.9% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 50 | -0.57% | -0.49 | -2.50% to +1.38% | 42% |
| Quarter vs average eligible stock | 50 | -0.19% | -0.17 | -1.98% to +1.67% | 48% |
| 12-mo vs SPY, January dates only | 12 | -3.42% | -0.62 | -12.14% to +5.41% | 42% |
| 12-mo vs average eligible, January only | 12 | -1.02% | -0.20 | -9.24% to +7.43% | 42% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 2923 | +15.7% | -0.1% | 44% |
| 2 | 2896 | +14.9% | -0.9% | 43% |
| 3 | 2898 | +15.3% | -0.6% | 43% |
| 4 | 2896 | +13.1% | -2.7% | 41% |
| 5 | 2913 | +13.4% | -2.4% | 41% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +42.5% | +21.3% | 67% |
| 2014 | 40 | +18.7% | +10.1% | 60% |
| 2015 | 40 | -9.5% | -14.7% | 30% |
| 2016 | 40 | +21.7% | +4.7% | 50% |
| 2017 | 40 | +21.5% | +4.5% | 55% |
| 2018 | 40 | -10.0% | -14.7% | 25% |
| 2019 | 40 | +16.2% | +4.5% | 55% |
| 2020 | 40 | +56.2% | +17.7% | 45% |
| 2021 | 40 | -7.7% | -12.9% | 30% |
| 2022 | 40 | +1.8% | -0.5% | 45% |
| 2023 | 40 | +21.9% | -6.1% | 42% |
| 2024 | 40 | -2.8% | -20.3% | 25% |
| 2025 | 30 | +18.1% | -1.9% | 43% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

1317 stock-quarters, about 26.3 names per date on 50 of 55 dates: avg 12-mo +17.3%, median +8.9%, vs SPY -0.8%, beat SPY 43%, vs average stock -1.5%, lost >20% 17%.

## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +8.9% vs SPY +14.3%; total +190% vs +431%
* Max drawdown -36% vs SPY -24% (quarterly granularity)
* Beat SPY in 42% of quarters; 50 quarters
