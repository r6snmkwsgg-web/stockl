"""Turn a list of trades and an equity curve into the numbers in the report."""
from __future__ import annotations

import numpy as np
import pandas as pd


def longest_losing_streak(trades: pd.DataFrame) -> int:
    best = cur = 0
    for r in trades.sort_values("exit_date")["R"]:
        cur = cur + 1 if r <= 0 else 0
        best = max(best, cur)
    return best


def yearly_returns(equity: pd.Series) -> pd.Series:
    """Percent change in account value for each calendar year."""
    year_end = equity.groupby(equity.index.year).last()
    prev = year_end.shift(1)
    prev.iloc[0] = equity.iloc[0]
    return (year_end / prev - 1)


def max_drawdown(equity: pd.Series) -> float:
    peak = equity.cummax()
    return float((equity / peak - 1).min())


def summarize(trades: pd.DataFrame, equity: pd.DataFrame, start_cash: float) -> dict:
    eq = equity["equity"]
    years = (eq.index[-1] - eq.index[0]).days / 365.25
    total = eq.iloc[-1] / start_cash - 1
    out = {
        "start_cash": start_cash,
        "end_equity": float(eq.iloc[-1]),
        "total_return": float(total),
        "cagr": float((eq.iloc[-1] / start_cash) ** (1 / years) - 1),
        "max_drawdown": max_drawdown(eq),
        "years": years,
        "n_trades": int(len(trades)),
    }
    if len(trades):
        wins = trades[trades["R"] > 0]
        losses = trades[trades["R"] <= 0]
        out.update({
            "win_rate": len(wins) / len(trades),
            "avg_win_R": float(wins["R"].mean()) if len(wins) else float("nan"),
            "avg_loss_R": float(losses["R"].mean()) if len(losses) else float("nan"),
            "expectancy_R": float(trades["R"].mean()),
            "avg_pnl_per_trade": float(trades["pnl"].mean()),
            "profit_factor": float(wins["pnl"].sum() / -losses["pnl"].sum()) if len(losses) and losses["pnl"].sum() < 0 else float("inf"),
            "longest_losing_streak": longest_losing_streak(trades),
            "avg_days_held": float(trades["days_held"].mean()),
            "trades_per_year": len(trades) / years,
            "exposure_pct": float((equity["n_pos"] > 0).mean()),
        })
    return out


def fmt_pct(x):
    return f"{x * 100:+.1f}%" if pd.notna(x) else "n/a"
