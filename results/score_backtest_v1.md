# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 35%, value 40%, timing 25%; flag penalty 4 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 550 | +13.4% | +11.7% | -2.0% | 44% | -4.9% | +3.3% | 49% | 15% |
| Top 10, from today's top-100 | 374 | +16.0% | +12.9% | +1.5% | 48% | -1.7% | +3.8% | 52% | 14% |
| Top 10, from the fallen group | 176 | +7.7% | +5.2% | -9.5% | 35% | -11.8% | +2.0% | 44% | 19% |
| Bottom 10 by score | 550 | +19.6% | +15.0% | +4.2% | 49% | +1.3% | +4.1% | 49% | 8% |
| Every eligible stock (average) | 5980 | +17.9% | +14.8% | +2.5% | 50% | -0.0% | +4.3% | 50% | 10% |

SPY itself averaged +15.4% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 55 | -0.54% | -0.71 | -1.79% to +0.68% | 45% |
| Quarter vs average eligible stock | 55 | -1.17% | -1.85 | -2.21% to -0.16% | 42% |
| 12-mo vs SPY, January dates only | 14 | +0.40% | 0.09 | -6.96% to +8.15% | 43% |
| 12-mo vs average eligible, January only | 14 | -2.68% | -0.70 | -8.56% to +3.71% | 36% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 1219 | +14.6% | -0.8% | 46% |
| 2 | 1185 | +16.3% | +0.9% | 49% |
| 3 | 1185 | +18.4% | +3.0% | 53% |
| 4 | 1185 | +19.1% | +3.7% | 50% |
| 5 | 1206 | +21.1% | +5.7% | 51% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2012 | 40 | +18.6% | +1.1% | 42% |
| 2013 | 40 | +34.5% | +11.7% | 62% |
| 2014 | 40 | +9.4% | +0.9% | 50% |
| 2015 | 40 | -3.9% | -9.1% | 38% |
| 2016 | 40 | +23.3% | +6.3% | 57% |
| 2017 | 40 | +18.6% | +1.6% | 42% |
| 2018 | 40 | -3.8% | -8.5% | 30% |
| 2019 | 40 | +18.4% | +6.6% | 55% |
| 2020 | 40 | +30.8% | -7.7% | 30% |
| 2021 | 40 | +7.8% | +2.6% | 57% |
| 2022 | 40 | +1.0% | -1.3% | 45% |
| 2023 | 40 | +7.3% | -20.8% | 20% |
| 2024 | 40 | +8.4% | -9.1% | 40% |
| 2025 | 30 | +17.8% | -2.1% | 47% |

## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +11.3% vs SPY +14.8%; total +335% vs +567%
* Max drawdown -22% vs SPY -24% (quarterly granularity)
* Beat SPY in 45% of quarters; 55 quarters
