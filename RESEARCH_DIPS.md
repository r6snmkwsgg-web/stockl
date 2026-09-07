# Research: buying structurally strong stocks after a big dip

*Third part of the project, after `REPORT.md` and `RESEARCH.md`. Produced by
`research_dips.py`; today's candidates come from `scan_dips.py`. Full tables
in `results/dips_summary.md`, every event in `results/dips/`.*

## 1. The short version

The idea: point out strong companies whose share price has just taken a big
hit, on the theory that the dip is temporary and the price is cheap.

On today's 100 largest stocks it looks wonderful. On a control group of 91
companies that were once large or popular and later stalled or crashed, the
same rule mostly stops working. The difference between the two is hindsight.

| After a 20% dip in a "strong" stock | Today's top 100 | Fallen / lagging control |
|---|---|---|
| Events (2011-2026) | 563 | 392 |
| Average return next 12 months | +29.8% | +10.2% |
| **Median** return next 12 months | +21.5% | **-3.3%** |
| Average vs SPY, next 12 months | +11.8% | -1.5% |
| Share of events that beat SPY over 12 months | 51% | **26%** |
| Fell another 10%+ within 60 days | 49% | 61% |
| Lost more than 20% over the next year (fresh dips) | 7% | 32% |

Two things survive in both groups, and they are the honest findings:

1. **A fresh dip is better than a stale one.** If the 52-week high was set
   within the last 60 trading days, forward returns are higher in both
   universes. A stock that has been drifting down for a year is a different
   animal from one that just got knocked 20% off a recent high.
2. **The payoff is lottery-shaped.** The averages are held up by a handful of
   enormous rebounds (TSLA in 2020, NVDA in 2016, PLUG in 2019-20, CVNA in
   2020). The typical outcome is much smaller, and in the control group the
   typical outcome is a loss. Whether you get the rebound or the crash is
   decided by things a price chart does not show.

**What this means for "pointing out" dips.** The scanner can find them, and
today it finds seven. What it cannot do is tell a temporary dip from the
start of a permanent decline. In the control group, roughly one in three
"strong stock, big dip" events was followed by a further loss of 20% or more
within a year. Names on that list at the time: Peloton, Zoom, DocuSign,
Shopify, Snap, Roku, Carvana in late 2021, all of which were "structurally
strong" by the rule (3-year return far above SPY, rising 200-day average) the
day they qualified.

## 2. Definitions (price only, no fundamentals)

I do not have free access to earnings, cash flow or valuation data back to
2010, so "undervalued" here means "cheap relative to the stock's own trend".
A real valuation screen (price-to-earnings versus the company's own history
and its sector) would be the natural next step, and it is the piece that
could actually separate the Pelotons from the Nvidias. Price alone cannot.

* **Structurally strong**, judged only with data known on the day: the
  stock's 3-year return is higher than SPY's 3-year return, and its 200-day
  moving average is higher than it was 6 months ago.
* **Big dip:** the close is at least X% below the highest high of the last 52
  weeks. Tested at 10, 15, 20, 25 and 30%.
* **Fresh:** the 52-week high was set within the last 60 trading days.
* **Event:** the first day a stock satisfies all of the above. The same
  stock is not counted again for 60 trading days.
* **Measured:** the price change over the next 5, 20, 60, 120 and 250
  trading days, the same for SPY, the difference, and the worst further fall
  within 60 days.

Two universes:

* **Today's top 100**, the same list as the main report. Survivorship bias:
  these are the companies that won.
* **Fallen / lagging control**, 91 companies (`swing/control_universe.py`)
  that were large or widely followed at some point since 2010 and have since
  lagged, stalled or crashed: old-economy names like Ford, Boeing, 3M,
  Schlumberger, Kraft Heinz, Intel, Cisco, IBM; travel names; and the
  pandemic and meme era favourites. Four more could not be downloaded
  because they no longer trade under their old symbol (Walgreens went
  private, US Steel was bought, Kellogg split, Square renamed). Companies
  that went bankrupt are missing entirely, so even the control group is
  kinder than reality.

## 3. Results

### Today's top 100

| Case | events | avg 60d | avg 250d | median 250d | vs SPY 60d | vs SPY 250d | beat SPY 250d | fell 10%+ more within 60d |
|---|---|---|---|---|---|---|---|---|
| control: strong stock, any day | 169180 | +4.3% | +17.9% | +14.7% | +1.3% | +5.6% | 53% | 32% |
| 10% below 52w high | 1703 | +5.7% | +21.0% | +16.2% | +1.7% | +7.0% | 51% | 38% |
| 15% below 52w high | 991 | +7.6% | +24.1% | +18.4% | +2.8% | +9.0% | 52% | 44% |
| 20% below 52w high | 563 | +10.3% | +29.8% | +21.5% | +4.0% | +11.8% | 51% | 49% |
| 20% below, high set <60d ago | 286 | +15.4% | +35.2% | +27.4% | +6.7% | +13.2% | 52% | 51% |
| 30% below 52w high | 202 | +18.2% | +43.0% | +36.6% | +7.5% | +17.5% | 55% | 54% |
| 30% below, high set <60d ago | 99 | +28.6% | +56.2% | +54.7% | +11.4% | +19.4% | 62% | 53% |
| 20% dip, 2011-2018 only | 168 | +7.2% | +23.3% | +20.8% | +3.0% | +10.2% | 61% | 43% |
| 20% dip, 2019-2026 only | 395 | +11.6% | +33.1% | +22.0% | +4.4% | +12.6% | 46% | 52% |
| 20% dip, excluding 2020 and 2022 | 381 | +10.3% | +26.4% | +20.3% | +4.6% | +11.4% | 49% | 42% |

Read on its own this says: the bigger the dip, the bigger the bounce, and it
holds in both halves of the data and outside the two crash years. Note even
here that "beat SPY over the next year" is a coin flip at 51%. The average is
big because the wins are big, not because they are frequent.

Note also the first row. On *any* day, a "strong" stock from this list
returned 17.9% over the next year, 5.6% more than SPY. That is not a strategy,
that is what "these are the 100 stocks that won" looks like in numbers.

### Fallen / lagging control, same rule

| Case | events | avg 60d | avg 250d | median 250d | vs SPY 60d | vs SPY 250d | beat SPY 250d | fell 10%+ more within 60d |
|---|---|---|---|---|---|---|---|---|
| control: strong stock, any day | 57403 | +3.3% | +10.3% | +2.1% | +0.2% | -1.4% | 35% | 46% |
| 10% below 52w high | 783 | +4.0% | +10.1% | -1.0% | +0.5% | -2.2% | 30% | 53% |
| 15% below 52w high | 550 | +5.1% | +10.4% | -2.5% | +1.3% | -1.9% | 28% | 56% |
| 20% below 52w high | 392 | +5.3% | +10.2% | -3.3% | +1.3% | -1.5% | 26% | 61% |
| 20% below, high set <60d ago | 173 | +9.8% | +25.6% | +3.4% | +4.3% | +10.0% | 33% | 66% |
| 30% below 52w high | 197 | +8.9% | +14.5% | -10.8% | +4.6% | +3.7% | 27% | 66% |
| 30% below, high set <60d ago | 78 | +15.1% | +32.0% | +4.1% | +8.2% | +14.9% | 30% | 69% |
| 20% dip, 2011-2018 only | 104 | +2.0% | +6.9% | +1.7% | -0.0% | -2.7% | 39% | 51% |
| 20% dip, 2019-2026 only | 288 | +6.5% | +11.6% | -7.5% | +1.8% | -1.0% | 22% | 64% |
| 20% dip, excluding 2020 and 2022 | 312 | +2.9% | +2.5% | -5.0% | -1.1% | -7.1% | 25% | 58% |

Same rule, different stocks: the median 12-month outcome after a 20% dip is
a 3% loss, only one dip in four beats the index, and outside the 2020 and
2022 crashes the average dip *underperformed SPY by 7%*. The "fresh dip"
rows still show a large average (+25.6%), but look at where it comes from:

* Best five outcomes: PLUG +925%, PLUG +679%, PLUG +411%, CVNA +266%,
  PLUG +254%. One stock, Plug Power, in 2019-2020, is most of the average.
* Worst five: CVNA -93%, SNAP -80%, SHOP -80%, ROKU -79%, DOCU -78%, all
  from dips in autumn 2021 that turned out to be the top.
* 32% of fresh 20% dips lost more than 20% over the following year, against
  7% in the winners' universe.
* Only 34% of the control stocks had dips that beat SPY on average, against
  56% of the winners.

### Clustering

Dips arrive together. Of the 286 fresh 20% dips in the top-100 list, 56
happened in March 2020 alone and a third of them fall in five months. For
the 30% dips, 43 of 99 are March 2020. A hundred events that are mostly one
crash and its recovery is, statistically, a handful of events. That is why
the "excluding 2020 and 2022" rows are there: the top-100 effect survives,
the control-group effect does not.

## 4. What I take from this

* **The chart cannot tell you which dip is temporary.** "Strong 3-year
  record plus a big drop" describes NVDA in January 2016 and Peloton in
  November 2021 equally well. The winners' list makes the rule look like a
  gift because we already know who recovered.
* **The real edge, if there is one, is in the fundamentals**, which is
  exactly the part I could not test: is the company still growing, is the
  drop about the business or about the market, is it actually cheap on
  earnings. That is the research worth doing next, and it needs a paid or
  scraped fundamentals source.
* **Fresh dips in the market as a whole are different from fresh dips in one
  stock.** March 2020, late 2018, April 2025: when everything falls together,
  strong stocks rebounded in both universes. When a single stock falls on its
  own while the market is fine, the control group says the market is usually
  right about it.
* **Position for the distribution you actually face.** Roughly: 50 to 65%
  chance of a further 10% fall within three months, a one-in-three chance of
  a 20%+ loss over the year in the control group, and a small chance of a
  very large gain. That is a small-position, many-bets, long-holding-period
  shape, which is the opposite of "get in for a few days".

## 5. Today's scan

`python scan_dips.py --no-download` on the 4 September 2026 close:

```
7 structurally strong stock(s) at least 20% below their 52-week high:

KLAC   close    185.60 | -40% from 52w high 307.37 (47 trading days ago) | 3-yr return +272% vs SPY +71%
AMAT   close    454.71 | -39% from 52w high 739.67 (47 trading days ago) | 3-yr return +201% vs SPY +71%
INTC   close     95.80 | -33% from 52w high 142.35 (47 trading days ago) | 3-yr return +177% vs SPY +71%
LRCX   close    307.65 | -30% from 52w high 438.50 (47 trading days ago) | 3-yr return +348% vs SPY +71%
AVGO   close    357.90 | -28% from 52w high 495.00 (65 trading days ago) | 3-yr return +301% vs SPY +71%
CAT    close    813.94 | -24% from 52w high 1073.46 (47 trading days ago) | 3-yr return +188% vs SPY +71%
WMT    close    107.14 | -21% from 52w high 135.16 (75 trading days ago) | 3-yr return +99% vs SPY +71%
```

Five of the seven are one story (semiconductor equipment and chips, all
peaking on the same day 47 trading days ago). Historically, a group-wide
fresh dip while SPY itself is near its highs is the *single-stock* kind of
dip, not the March 2020 kind. I would want to know why the group fell before
calling it undervalued. The scanner tells you where to look, not what to buy.

## 6. "But MU, PLTR, MSTR and SNDK all dipped and came back"

They did, most recently. The fair question is how often that happened across
*every* big dip those same stocks ever had (`dip_examples.py`, full tables in
`results/dip_examples.md`):

| Stock | Separate 20%+ dips | Regained the old high within a year | A dip that failed |
|---|---|---|---|
| MU | 43 | 22 of 42 (52%) | Jan 2015: dipped 21%, then fell 67% more |
| PLTR | 17 | 6 of 14 (43%) | 2021: eight dips in a row, each followed by a further 30 to 75% fall |
| MSTR | 50 | 17 of 46 (37%) | every dip from Nov 2024 to Aug 2025 lost 56 to 74% over the next year |
| SNDK | 4 | 3 of 3 | listed February 2025; its whole history is one boom |

The dips you remember are the last ones before a run-up, remembered after the
run-up. In the same names, a 20% dip got back to its high within a year
roughly four to five times in ten, and when it did not, the further fall was
usually severe. The scanner can and does point at these stocks (Micron was
second on the Bargain Ledger on 4 September 2026); it cannot tell which kind
of dip this one is, and neither can a chart.
