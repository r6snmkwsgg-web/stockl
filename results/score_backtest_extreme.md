# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 500 | +15.7% | +10.1% | +0.7% | 45% | +1.6% | +3.6% | 50% | 20% |
| Top 10, from today's top-100 | 230 | +21.8% | +20.4% | +7.1% | 57% | +6.8% | +6.7% | 60% | 13% |
| Top 10, from the fallen group | 0 | +nan% | +nan% | +nan% | nan% | +nan% | +nan% | nan% | nan% |
| Bottom 10 by score | 500 | +10.5% | +6.4% | -4.5% | 39% | -3.6% | +2.5% | 48% | 23% |
| Every eligible stock (average) | 8453 | +14.4% | +9.9% | -1.2% | 44% | +0.0% | +3.2% | 46% | 17% |

SPY itself averaged +14.9% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 50 | -0.11% | -0.11 | -1.74% to +1.58% | 46% |
| Quarter vs average eligible stock | 50 | +0.25% | 0.26 | -1.25% to +1.90% | 48% |
| 12-mo vs SPY, January dates only | 12 | +0.21% | 0.05 | -6.64% to +7.42% | 33% |
| 12-mo vs average eligible, January only | 12 | +2.22% | 0.49 | -4.78% to +9.46% | 50% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 1710 | +17.0% | +1.4% | 47% |
| 2 | 1682 | +16.7% | +1.0% | 46% |
| 3 | 1676 | +15.2% | -0.4% | 46% |
| 4 | 1682 | +13.0% | -2.7% | 41% |
| 5 | 1703 | +10.2% | -5.4% | 37% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +29.7% | +8.5% | 53% |
| 2014 | 40 | +14.7% | +6.1% | 57% |
| 2015 | 40 | -9.1% | -14.3% | 30% |
| 2016 | 40 | +21.8% | +4.8% | 55% |
| 2017 | 40 | +37.1% | +20.1% | 72% |
| 2018 | 40 | -9.6% | -14.2% | 25% |
| 2019 | 40 | +14.7% | +2.9% | 57% |
| 2020 | 40 | +65.2% | +26.7% | 52% |
| 2021 | 40 | -4.9% | -10.1% | 28% |
| 2022 | 40 | +5.4% | +3.1% | 48% |
| 2023 | 40 | +16.7% | -11.4% | 32% |
| 2024 | 40 | +6.5% | -11.0% | 32% |
| 2025 | 30 | +20.3% | +0.3% | 37% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

745 stock-quarters, about 14.9 names per date on 50 of 55 dates: avg 12-mo +16.6%, median +8.4%, vs SPY -1.5%, beat SPY 42%, vs average stock -1.7%, lost >20% 18%.

## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +11.4% vs SPY +14.3%; total +284% vs +431%
* Max drawdown -36% vs SPY -24% (quarterly granularity)
* Beat SPY in 44% of quarters; 50 quarters
