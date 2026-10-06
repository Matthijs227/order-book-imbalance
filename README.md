# Order-book imbalance: how far ahead does it predict, and who can use it?

A small, reproducible study on Nasdaq limit order book data (LOBSTER free samples, reconstructed from
TotalView-ITCH). The question: the classic short-horizon signal is level-1 order-book imbalance, more
size waiting on the bid than on the ask. How long does it predict the mid price, and is the predicted
move ever large enough to pay for crossing the spread?

## Data

[LOBSTER](https://lobsterdata.com) sample files for AAPL, AMZN, GOOG, INTC and MSFT on 21 June 2012:
every order message (add, cancel, execute) with the reconstructed book at 10 levels, 09:30 to 16:00.
The raw files are not in this repository; `download_samples.py` fetches them from the LOBSTER legacy
sample page.

## Method

- **Signal:** level-1 imbalance `(bid size - ask size) / (bid size + ask size)`, and the same over 5 levels.
- **Sampling:** for each horizon h, a grid of non-overlapping points h seconds apart (first 5 and last 10
  minutes of the session dropped). The book state used is the last one known at or before each grid
  point, so there is no look-ahead.
- **Target:** the mid-price return over the next h seconds, in basis points.
- **Statistics:** the correlation of imbalance with the next return (t-statistic from the correlation),
  and the difference in average return between the top and bottom imbalance deciles, compared with the
  round-trip cost of crossing the median quoted spread.

## Results

Level-1 imbalance, average over the five stocks:

| Horizon | Mean correlation | Top minus bottom decile move | Round trip for a taker (2 x half spread) |
|---|---|---|---|
| 1 s | 0.092 | +0.27 bps | 3.88 bps |
| 5 s | 0.113 | +0.74 bps | 3.88 bps |
| 10 s | 0.094 | +0.87 bps | 3.88 bps |
| 30 s | 0.076 | +1.06 bps | 3.87 bps |
| 60 s | 0.028 | +1.04 bps | 3.92 bps |
| 300 s | 0.003 | -1.43 bps | 4.04 bps |

Correlation by stock (level-1 imbalance):

| Horizon | AAPL | AMZN | GOOG | INTC | MSFT |
|---|---|---|---|---|---|
| 1 s | 0.038 (t 5.7) | 0.045 (t 6.7) | 0.030 (t 4.4) | 0.170 (t 25.9) | 0.178 (t 27.2) |
| 5 s | 0.041 (t 2.7) | 0.039 (t 2.6) | 0.017 (t 1.1) | 0.246 (t 17.0) | 0.222 (t 15.3) |
| 10 s | 0.018 (t 0.9) | 0.025 (t 1.2) | -0.006 (t -0.3) | 0.231 (t 11.2) | 0.203 (t 9.8) |
| 30 s | 0.023 (t 0.6) | 0.034 (t 0.9) | 0.023 (t 0.6) | 0.189 (t 5.3) | 0.112 (t 3.1) |
| 60 s | -0.036 (t -0.7) | -0.004 (t -0.1) | -0.007 (t -0.1) | 0.104 (t 2.0) | 0.080 (t 1.6) |
| 300 s | -0.182 (t -1.6) | -0.008 (t -0.1) | 0.067 (t 0.6) | 0.206 (t 1.8) | -0.067 (t -0.6) |

Median round trip by stock, in bps: AAPL 2.6, AMZN 5.4, GOOG 4.4, INTC 3.7, MSFT 3.3.

## Reading

- The signal is real but short-lived. In INTC and MSFT, low-priced stocks with a one-tick spread and
  deep queues, it is strong at 1 to 10 seconds and still visible at 30 seconds. In the high-priced
  names (AAPL, AMZN, GOOG) it is weak and gone within about 10 seconds.
- The predicted move never exceeds the cost of crossing the spread. Even the most extreme imbalance
  decile beats the opposite decile by only a few basis points, less than a taker's round trip.
- It is therefore a market maker's signal: useful for someone who earns the spread and decides which
  side to quote, or as an execution tool (post passively or cross now), not as a stand-alone trading
  signal for someone who pays the spread.
- Depth-5 imbalance is weaker than level 1 here (`results/imbalance_horizon.csv`).

## Caveats

One trading day, five stocks, 2012. This is an exploration and a toolkit, not evidence of a stable
effect. The t-statistics treat grid points as independent, and at 300 seconds there are only 74 of them.

## Reproduce

```
pip install -r requirements.txt
python download_samples.py      # about 30 MB of zips, about 600 MB unzipped, into data/ (git-ignored)
python imbalance_horizon.py     # prints the tables and writes results/imbalance_horizon.csv
```

Data: LOBSTER (lobsterdata.com). Code: MIT licence.
