# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 550 | +18.8% | +15.6% | +3.4% | 51% | +0.5% | +5.6% | 55% | 14% |
| Top 10, from today's top-100 | 450 | +22.1% | +19.1% | +6.5% | 56% | +3.4% | +6.5% | 58% | 11% |
| Top 10, from the fallen group | 100 | +3.9% | -2.9% | -10.4% | 29% | -12.5% | +1.5% | 40% | 28% |
| Bottom 10 by score | 550 | +19.2% | +14.7% | +3.8% | 50% | +0.9% | +4.8% | 49% | 9% |
| Every eligible stock (average) | 5980 | +17.9% | +14.8% | +2.5% | 50% | -0.0% | +4.3% | 50% | 10% |

SPY itself averaged +15.4% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 55 | +1.80% | 2.00 | +0.36% to +3.31% | 62% |
| Quarter vs average eligible stock | 55 | +1.18% | 1.30 | -0.27% to +2.71% | 55% |
| 12-mo vs SPY, January dates only | 14 | +6.89% | 1.52 | -0.11% to +14.32% | 57% |
| 12-mo vs average eligible, January only | 14 | +3.81% | 0.85 | -2.79% to +11.26% | 57% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 1219 | +18.4% | +3.0% | 51% |
| 2 | 1185 | +17.9% | +2.5% | 50% |
| 3 | 1185 | +19.6% | +4.1% | 52% |
| 4 | 1185 | +16.3% | +0.9% | 49% |
| 5 | 1206 | +17.3% | +1.9% | 47% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2012 | 40 | +22.8% | +5.3% | 48% |
| 2013 | 40 | +35.9% | +13.0% | 68% |
| 2014 | 40 | +14.5% | +6.0% | 62% |
| 2015 | 40 | -4.2% | -9.4% | 38% |
| 2016 | 40 | +22.1% | +5.1% | 60% |
| 2017 | 40 | +33.6% | +16.6% | 65% |
| 2018 | 40 | -0.2% | -4.9% | 35% |
| 2019 | 40 | +37.9% | +26.2% | 80% |
| 2020 | 40 | +38.5% | -0.0% | 40% |
| 2021 | 40 | -3.0% | -8.3% | 48% |
| 2022 | 40 | -5.5% | -7.8% | 38% |
| 2023 | 40 | +25.3% | -2.8% | 35% |
| 2024 | 40 | +22.4% | +4.9% | 52% |
| 2025 | 30 | +24.3% | +4.4% | 40% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

341 stock-quarters, about 6.6 names per date on 52 of 55 dates: avg 12-mo +17.1%, median +10.6%, vs SPY -1.3%, beat SPY 44%, vs average stock -3.4%, lost >20% 15%.
From today's largest: 238 picks, vs SPY +4.3%, beat 53%. From the fallen group: 103 picks, vs SPY -14.4%, beat 24%.


## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +21.0% vs SPY +14.8%; total +1272% vs +567%
* Max drawdown -29% vs SPY -24% (quarterly granularity)
* Beat SPY in 60% of quarters; 55 quarters
