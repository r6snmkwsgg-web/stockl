# Score backtest: 55 quarterly rebalances, 2012-01-03 to 2025-07-01

Weights: quality 70%, value 20%, timing 10%; flag penalty 0 points per flag.

| Group | picks | avg 12-mo return | median 12-mo | avg vs SPY 12-mo | beat SPY (12-mo) | avg vs eligible 12-mo | avg 3-mo | beat SPY (3-mo) | lost >20% in 12-mo |
|---|---|---|---|---|---|---|---|---|---|
| Top 10 by score | 490 | +20.4% | +18.4% | +6.5% | 57% | +3.2% | +5.4% | 59% | 10% |
| Top 10, from today's top-100 | 490 | +20.4% | +18.4% | +6.5% | 57% | +3.2% | +5.4% | 59% | 10% |
| Top 10, from the fallen group | 0 | +nan% | +nan% | +nan% | nan% | +nan% | +nan% | nan% | nan% |
| Bottom 10 by score | 490 | +15.1% | +12.4% | +1.2% | 48% | -2.0% | +4.1% | 50% | 5% |
| Every eligible stock (average) | 3671 | +17.0% | +14.8% | +3.1% | 52% | -0.0% | +4.2% | 52% | 7% |

SPY itself averaged +13.9% (total return) over the same 12-month windows.

## Is the edge real? (top-10 basket, per rebalance date)

| Measure | dates | mean | t-stat | 90% bootstrap range | share positive |
|---|---|---|---|---|---|
| Quarter vs SPY (non-overlapping) | 49 | +2.16% | 2.63 | +0.84% to +3.51% | 61% |
| Quarter vs average eligible stock | 49 | +1.21% | 1.46 | -0.10% to +2.55% | 61% |
| 12-mo vs SPY, January dates only | 12 | +7.68% | 1.58 | -0.06% to +15.25% | 50% |
| 12-mo vs average eligible, January only | 12 | +4.62% | 0.92 | -3.61% to +12.54% | 58% |

A t-stat below about 2 means the edge cannot be told apart from luck with this much data.

## By score quintile (1 = best fifth, 5 = worst fifth)

| Quintile | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 1 | 755 | +20.2% | +6.4% | 56% |
| 2 | 725 | +15.8% | +2.1% | 52% |
| 3 | 723 | +17.2% | +3.3% | 52% |
| 4 | 725 | +16.7% | +2.9% | 54% |
| 5 | 743 | +14.7% | +0.9% | 48% |

## Top 10, by year of purchase

| Year | picks | avg 12-mo | avg vs SPY | beat SPY |
|---|---|---|---|---|
| 2013 | 30 | +31.8% | +10.5% | 67% |
| 2014 | 40 | +17.1% | +8.5% | 68% |
| 2015 | 40 | +1.2% | -4.0% | 50% |
| 2016 | 40 | +26.2% | +9.2% | 57% |
| 2017 | 40 | +38.7% | +21.6% | 78% |
| 2018 | 40 | +7.6% | +3.0% | 50% |
| 2019 | 40 | +33.4% | +21.7% | 78% |
| 2020 | 30 | +24.2% | -5.3% | 40% |
| 2021 | 40 | +9.2% | +4.0% | 57% |
| 2022 | 40 | +2.5% | +0.2% | 55% |
| 2023 | 40 | +35.4% | +7.3% | 50% |
| 2024 | 40 | +26.4% | +8.9% | 52% |
| 2025 | 30 | +13.2% | -6.7% | 27% |
## The 'undervalued on a dip' screen (quality, value and timing all >= 60)

145 stock-quarters, about 3.2 names per date on 46 of 55 dates: avg 12-mo +15.7%, median +12.6%, vs SPY +1.5%, beat SPY 47%, vs average stock -1.6%, lost >20% 13%.

## Top-10 portfolio, rebalanced quarterly, 0.2% cost per quarter

* CAGR +20.5% vs SPY +12.4%; total +883% vs +319%
* Max drawdown -27% vs SPY -24% (quarterly granularity)
* Beat SPY in 59% of quarters; 49 quarters
