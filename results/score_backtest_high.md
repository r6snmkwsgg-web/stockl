# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 500 | +14.3% | +10.4% | -0.6% | 46% | +0.2% | +4.4% | 50% | 18% |
| Top 10, from today's top-100 | 256 | +19.2% | +16.0% | +3.7% | 52% | +4.4% | +5.7% | 56% | 13% |
| Top 10, from the fallen group | 0 | +nan% | +nan% | +nan% | nan% | +nan% | +nan% | nan% | nan% |
| Bottom 10 by score | 500 | +15.6% | +11.6% | +0.7% | 46% | +1.5% | +3.3% | 47% | 13% |
| Every eligible stock (average) | 9445 | +13.5% | +10.8% | -0.9% | 45% | -0.0% | +3.2% | 47% | 12% |

SPY itself averaged +14.9% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 50 | +0.68% | 0.66 | -0.97% to +2.35% | 52% |
| Quarter vs average eligible stock | 50 | +0.85% | 0.77 | -0.96% to +2.65% | 60% |
| 12-mo vs SPY, January dates only | 12 | -0.33% | -0.08 | -6.75% to +5.79% | 42% |
| 12-mo vs average eligible, January only | 12 | -0.18% | -0.05 | -6.25% to +5.46% | 50% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 1908 | +14.4% | -0.0% | 46% |
| 2 | 1883 | +13.3% | -1.1% | 44% |
| 3 | 1873 | +13.9% | -0.5% | 45% |
| 4 | 1883 | +12.3% | -2.1% | 43% |
| 5 | 1898 | +13.7% | -0.8% | 45% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +41.2% | +20.0% | 67% |
| 2014 | 40 | +20.7% | +12.1% | 68% |
| 2015 | 40 | -8.2% | -13.4% | 28% |
| 2016 | 40 | +19.9% | +2.9% | 50% |
| 2017 | 40 | +19.0% | +2.0% | 50% |
| 2018 | 40 | -8.3% | -13.0% | 22% |
| 2019 | 40 | +28.0% | +16.2% | 65% |
| 2020 | 40 | +24.6% | -13.9% | 35% |
| 2021 | 40 | +1.5% | -3.7% | 42% |
| 2022 | 40 | +0.5% | -1.8% | 45% |
| 2023 | 40 | +18.7% | -9.3% | 32% |
| 2024 | 40 | +12.2% | -5.3% | 45% |
| 2025 | 30 | +25.4% | +5.5% | 50% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

634 stock-quarters, about 12.7 names per date on 50 of 55 dates: avg 12-mo +10.5%, median +8.2%, vs SPY -4.0%, beat SPY 42%, vs average stock -3.3%, lost >20% 17%.

## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +15.1% vs SPY +14.3%; total +481% vs +431%
* Max drawdown -30% vs SPY -24% (quarterly granularity)
* Beat SPY in 52% of quarters; 50 quarters
