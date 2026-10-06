"""
Order-book imbalance on LOBSTER samples (Nasdaq L3 reconstructed, 2012-06-21): how far ahead does it predict the
mid-price, and is the predicted move ever larger than the cost of crossing the spread?

One day, five stocks, 2012: an exploration and a toolkit, NOT evidence.
Run:  python download_samples.py && python imbalance_horizon.py
"""
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).parent / "data" / "unzipped"
H = [1, 5, 10, 30, 60, 300]                      # horizons in seconds


def load(tk: str) -> pd.DataFrame:
    d = next(ROOT.glob(f"LOBSTER_SampleFile_{tk}_*"))
    msg = pd.read_csv(next(d.glob("*message*")), header=None, usecols=[0], names=["t"])
    ob = pd.read_csv(next(d.glob("*orderbook*")), header=None, usecols=range(20))
    ob.columns = [f"{s}{k}{i}" for i in range(1, 6) for s, k in [("a", "p"), ("a", "s"), ("b", "p"), ("b", "s")]]
    df = pd.concat([msg, ob], axis=1)
    df = df[(df.ap1 < 9e9) & (df.bp1 > -9e9) & (df.ap1 > df.bp1)]          # drop empty-side placeholders
    df["mid"] = (df.ap1 + df.bp1) / 2 / 1e4
    df["spread_bps"] = (df.ap1 - df.bp1) / 1e4 / df.mid * 1e4
    df["imb1"] = (df.bs1 - df.as1) / (df.bs1 + df.as1)
    bsum = sum(df[f"bs{i}"] for i in range(1, 6)); asum = sum(df[f"as{i}"] for i in range(1, 6))
    df["imb5"] = (bsum - asum) / (bsum + asum)
    return df


def on_grid(df: pd.DataFrame, step: float) -> pd.DataFrame:
    """Last book state at each grid time (no look-ahead: state known at or before the grid point)."""
    grid = np.arange(34200 + 300, 57600 - 600, step)      # skip the first 5 and last 10 minutes
    i = np.searchsorted(df.t.values, grid, side="right") - 1
    g = df.iloc[i][["mid", "spread_bps", "imb1", "imb5"]].reset_index(drop=True)
    g["t"] = grid
    return g


rows = []
for tk in ["AAPL", "AMZN", "GOOG", "INTC", "MSFT"]:
    df = load(tk)
    for h in H:
        g = on_grid(df, h)                                  # NON-overlapping: one sample per horizon length
        fut = g.mid.shift(-1)
        g["ret_bps"] = (fut / g.mid - 1) * 1e4
        g = g.dropna()
        for sig in ["imb1", "imb5"]:
            c = g[sig].corr(g.ret_bps)
            n = len(g)
            top = g[g[sig] >= g[sig].quantile(0.9)].ret_bps.mean()
            bot = g[g[sig] <= g[sig].quantile(0.1)].ret_bps.mean()
            rows.append(dict(stock=tk, h_sec=h, signal=sig, n=n, corr=c, t=c * np.sqrt(n - 2) / np.sqrt(1 - c * c),
                             top10_minus_bot10_bps=top - bot, half_spread_bps=g.spread_bps.median() / 2))
r = pd.DataFrame(rows)
pd.set_option("display.width", 200)
print(r[r.signal == "imb1"].round(3).to_string(index=False))
print("\nDepth-5 imbalance:")
print(r[r.signal == "imb5"].round(3).to_string(index=False))
print("\nAverage over the 5 stocks (imb1): corr and the top-minus-bottom decile move vs the round-trip cost (2 x half spread)")
a = r[r.signal == "imb1"].groupby("h_sec")[["corr", "top10_minus_bot10_bps", "half_spread_bps"]].mean()
a["round_trip_bps"] = 2 * a.half_spread_bps
print(a.round(3).to_string())
(Path(__file__).parent / "results").mkdir(exist_ok=True)
r.to_csv(Path(__file__).parent / "results" / "imbalance_horizon.csv", index=False)
