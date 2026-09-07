#!/usr/bin/env python3
"""Steps 2-4: run the backtest in every version and write the results.

Outputs (in results/):
  trades_<version>.csv     every trade, one row each
  equity_<version>.csv     account value every day
  summary.csv / summary.md the headline numbers for all versions side by side
  yearly_returns.csv / .md return for each calendar year
  equity_curves.png        chart of account value over time
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from swing.backtest import Config, prepare, run
from swing.data import load_all
from swing.metrics import summarize, yearly_returns
from swing.universe import ALL_TICKERS, MARKET

OUT = Path("results")
OUT.mkdir(exist_ok=True)

VERSIONS = {
    "A":          Config(name="A", start_cash=10_000, risk_pct=0.01, max_positions=5),
    "A_nofilter": Config(name="A_nofilter", start_cash=10_000, risk_pct=0.01, max_positions=5,
                         use_market_filter=False),
    "B":          Config(name="B", start_cash=3_000, risk_pct=0.02, max_positions=3,
                         max_position_pct=0.40),
    "B_nofilter": Config(name="B_nofilter", start_cash=3_000, risk_pct=0.02, max_positions=3,
                         max_position_pct=0.40, use_market_filter=False),
    # Same as A and B but paying 0.1% slippage on every buy and every sell.
    "A_costs":    Config(name="A_costs", start_cash=10_000, risk_pct=0.01, max_positions=5,
                         slippage_pct=0.001),
    "B_costs":    Config(name="B_costs", start_cash=3_000, risk_pct=0.02, max_positions=3,
                         max_position_pct=0.40, slippage_pct=0.001),
}


def main():
    prices = load_all(ALL_TICKERS)
    missing = [t for t in ALL_TICKERS if t not in prices]
    print(f"Loaded {len(prices)} tickers" + (f", missing: {missing}" if missing else ""))
    prepared = prepare(prices, MARKET)
    spy = prepared[0]

    summaries, yearly, curves = {}, {}, {}
    for key, cfg in VERSIONS.items():
        trades, equity = run(prices, cfg, MARKET, prepared=prepared)
        trades.to_csv(OUT / f"trades_{key}.csv", index=False)
        equity.to_csv(OUT / f"equity_{key}.csv")
        summaries[key] = summarize(trades, equity, cfg.start_cash)
        yearly[key] = yearly_returns(equity["equity"])
        curves[key] = equity["equity"]
        s = summaries[key]
        print(f"{key:11s} trades={s['n_trades']:4d} win={s.get('win_rate', 0):.1%} "
              f"exp={s.get('expectancy_R', 0):+.2f}R total={s['total_return']:+.1%} "
              f"CAGR={s['cagr']:+.1%} maxDD={s['max_drawdown']:.1%}")

    # SPY buy-and-hold for comparison (price only, dividends not included)
    spy_c = spy["Close"].loc[curves["A"].index]
    yearly["SPY_buy_hold"] = yearly_returns(spy_c)
    spy_total = spy_c.iloc[-1] / spy_c.iloc[0] - 1
    yrs = (spy_c.index[-1] - spy_c.index[0]).days / 365.25
    summaries["SPY_buy_hold"] = {
        "total_return": float(spy_total), "cagr": float((1 + spy_total) ** (1 / yrs) - 1),
        "max_drawdown": float((spy_c / spy_c.cummax() - 1).min()),
    }

    summary = pd.DataFrame(summaries)
    summary.to_csv(OUT / "summary.csv")
    yr = pd.DataFrame(yearly)
    yr.index.name = "year"
    yr.to_csv(OUT / "yearly_returns.csv")
    (OUT / "summary.json").write_text(json.dumps(summaries, indent=2, default=float))

    # Markdown tables for the report
    rows = [
        ("Number of trades", "n_trades", "{:.0f}"),
        ("Win rate", "win_rate", "{:.1%}"),
        ("Average win (R)", "avg_win_R", "{:+.2f}"),
        ("Average loss (R)", "avg_loss_R", "{:+.2f}"),
        ("Expectancy per trade (R)", "expectancy_R", "{:+.2f}"),
        ("Average profit per trade ($)", "avg_pnl_per_trade", "{:+.2f}"),
        ("Profit factor", "profit_factor", "{:.2f}"),
        ("Total return", "total_return", "{:+.1%}"),
        ("CAGR (yearly growth rate)", "cagr", "{:+.1%}"),
        ("Max drawdown", "max_drawdown", "{:.1%}"),
        ("Longest losing streak (trades)", "longest_losing_streak", "{:.0f}"),
        ("Average days held", "avg_days_held", "{:.1f}"),
        ("Trades per year", "trades_per_year", "{:.1f}"),
        ("Time with a position open", "exposure_pct", "{:.0%}"),
        ("Final account value ($)", "end_equity", "{:,.0f}"),
    ]
    cols = list(VERSIONS) + ["SPY_buy_hold"]
    md = ["| Metric | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for label, k, f in rows:
        cells = []
        for c in cols:
            v = summaries[c].get(k)
            cells.append(f.format(v) if v is not None and v == v else "")
        md.append(f"| {label} | " + " | ".join(cells) + " |")
    (OUT / "summary.md").write_text("\n".join(md) + "\n")

    md = ["| Year | " + " | ".join(yr.columns) + " |", "|---|" + "---|" * len(yr.columns)]
    for y, row in yr.iterrows():
        md.append(f"| {y} | " + " | ".join(f"{v:+.1%}" if v == v else "" for v in row) + " |")
    (OUT / "yearly_returns.md").write_text("\n".join(md) + "\n")

    fig, axes = plt.subplots(2, 1, figsize=(11, 9))
    for key in ["A", "A_nofilter"]:
        axes[0].plot(curves[key].index, curves[key], label=key)
    axes[0].set_title("Version A: $10,000 start, 1% risk, max 5 positions")
    for key in ["B", "B_nofilter"]:
        axes[1].plot(curves[key].index, curves[key], label=key)
    axes[1].set_title("Version B: $3,000 start, 2% risk, max 3 positions, max 40% in one stock")
    for ax in axes:
        ax.set_ylabel("Account value ($)"); ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout()
    fig.savefig(OUT / "equity_curves.png", dpi=120)
    print("Wrote results/ folder.")


if __name__ == "__main__":
    main()
