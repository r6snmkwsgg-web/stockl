# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 480 | +17.3% | +15.3% | +4.0% | 54% | +2.5% | +4.2% | 54% | 6% |
| Top 10, from today's top-100 | 480 | +17.3% | +15.3% | +4.0% | 54% | +2.5% | +4.2% | 54% | 6% |
| Top 10, from the fallen group | 0 | +nan% | +nan% | +nan% | nan% | +nan% | +nan% | nan% | nan% |
| Bottom 10 by score | 480 | +12.7% | +10.7% | -0.6% | 46% | -2.1% | +3.5% | 49% | 5% |
| Every eligible stock (average) | 2897 | +14.6% | +13.1% | +1.9% | 52% | +0.0% | +3.6% | 51% | 6% |

SPY itself averaged +13.3% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 48 | +1.13% | 1.69 | +0.01% to +2.23% | 58% |
| Quarter vs average eligible stock | 48 | +0.63% | 1.23 | -0.16% to +1.46% | 56% |
| 12-mo vs SPY, January dates only | 12 | +3.91% | 1.18 | -1.37% to +9.11% | 67% |
| 12-mo vs average eligible, January only | 12 | +2.47% | 0.98 | -1.41% to +6.37% | 58% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 602 | +17.0% | +4.3% | 54% |
| 2 | 566 | +13.9% | +1.3% | 53% |
| 3 | 569 | +16.1% | +3.4% | 53% |
| 4 | 566 | +13.7% | +1.1% | 51% |
| 5 | 594 | +12.4% | -0.3% | 47% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +26.7% | +5.4% | 50% |
| 2014 | 40 | +17.7% | +9.2% | 70% |
| 2015 | 40 | +3.2% | -2.0% | 48% |
| 2016 | 40 | +21.8% | +4.8% | 52% |
| 2017 | 40 | +39.5% | +22.4% | 80% |
| 2018 | 40 | +10.7% | +6.0% | 62% |
| 2019 | 40 | +26.1% | +14.4% | 70% |
| 2020 | 20 | +33.8% | +9.9% | 60% |
| 2021 | 40 | +9.3% | +4.0% | 60% |
| 2022 | 40 | +1.4% | -0.9% | 48% |
| 2023 | 40 | +19.7% | -8.3% | 30% |
| 2024 | 40 | +15.6% | -1.9% | 48% |
| 2025 | 30 | +8.1% | -11.9% | 23% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

93 stock-quarters, about 2.4 names per date on 38 of 55 dates: avg 12-mo +10.7%, median +12.3%, vs SPY -2.2%, beat SPY 43%, vs average stock -3.8%, lost >20% 12%.

## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +16.0% vs SPY +11.9%; total +492% vs +284%
* Max drawdown -23% vs SPY -24% (quarterly granularity)
* Beat SPY in 56% of quarters; 48 quarters
