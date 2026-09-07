#!/usr/bin/env python3
"""Research: does any change to the rules make this strategy work?

Every variant is run four ways on Version A sizing ($10,000, 1% risk, 5 slots):
  * full period, no costs
  * full period, 0.1% slippage per side ("costs")
  * first half  2011-2018, with costs   ("in-sample")
  * second half 2019-2026, with costs   ("out-of-sample")
If a variant only looks good in one half, it is probably luck, not edge.

WARNING about this kind of research: if you test enough variants, one of them
will look good by chance. That is called data mining. The half/half split is
the guard against it, but with ~12 variants it is only a partial guard.
"""
from dataclasses import replace
from pathlib import Path

import pandas as pd

from swing.backtest import Config, prepare, run
from swing.data import load_all
from swing.metrics import summarize
from swing.universe import ALL_TICKERS, MARKET

OUT = Path("results")
BASE = Config(name="base", start_cash=10_000, risk_pct=0.01, max_positions=5)

VARIANTS = {
    "base (rules as given)": BASE,
    "no time stop": replace(BASE, time_stop_days=None),
    "EMA exit only after +2R partial": replace(BASE, exit_rule="ema_after_partial"),
    "stop = 2xATR only (not 'closer')": replace(BASE, stop_mode="atr"),
    "2xATR stop + EMA exit after partial": replace(BASE, stop_mode="atr", exit_rule="ema_after_partial"),
    "3xATR stop (max 12%) + EMA exit after partial": replace(BASE, stop_mode="atr", atr_mult=3, max_stop_pct=0.12,
                                                             exit_rule="ema_after_partial"),
    "trailing stop under 5-day low, no partial": replace(BASE, stop_mode="atr", exit_rule="trail_low5", partial_R=None),
    "take 20% profit, 2xATR stop, max 10 days": replace(BASE, stop_mode="atr", exit_rule="none", partial_R=None,
                                                         time_stop_days=None, target_pct=0.20, max_hold_days=10),
    "take 20% profit, 2xATR stop, max 20 days": replace(BASE, stop_mode="atr", exit_rule="none", partial_R=None,
                                                         time_stop_days=None, target_pct=0.20, max_hold_days=20),
    "take 10% profit, 2xATR stop, max 10 days": replace(BASE, stop_mode="atr", exit_rule="none", partial_R=None,
                                                         time_stop_days=None, target_pct=0.10, max_hold_days=10),
    "take 5% profit, 2xATR stop, max 10 days": replace(BASE, stop_mode="atr", exit_rule="none", partial_R=None,
                                                        time_stop_days=None, target_pct=0.05, max_hold_days=10),
    "buy the dip (RSI2<10), exit close > 5-day avg": replace(BASE, setup_mode="mean_reversion", entry_mode="open",
                                                             stop_mode="atr", exit_rule="close_above_sma5",
                                                             partial_R=None, time_stop_days=None, max_hold_days=10),
    "buy the dip (RSI2<10), take 20%, max 10 days": replace(BASE, setup_mode="mean_reversion", entry_mode="open",
                                                            stop_mode="atr", exit_rule="none", partial_R=None,
                                                            time_stop_days=None, target_pct=0.20, max_hold_days=10),
    "buy the dip (RSI2<10), take 5%, max 10 days": replace(BASE, setup_mode="mean_reversion", entry_mode="open",
                                                           stop_mode="atr", exit_rule="none", partial_R=None,
                                                           time_stop_days=None, target_pct=0.05, max_hold_days=10),
}

RUNS = {
    "full, no costs": dict(),
    "full, costs": dict(slippage_pct=0.001),
    "2011-18, costs": dict(slippage_pct=0.001, start="2010-01-01", end="2018-12-31"),
    "2019-26, costs": dict(slippage_pct=0.001, start="2019-01-01"),
}


def main():
    prices = load_all(ALL_TICKERS)
    prepared = prepare(prices, MARKET)
    spy = prepared[0]["Close"]

    rows = []
    for vname, cfg in VARIANTS.items():
        row = {"variant": vname}
        for rname, kw in RUNS.items():
            c = replace(cfg, name=vname, **kw)
            trades, eq = run(prices, c, MARKET, prepared=prepared)
            s = summarize(trades, eq, c.start_cash)
            if rname == "full, no costs":
                row.update({"trades": s["n_trades"], "win%": s.get("win_rate", 0),
                            "avg win R": s.get("avg_win_R"), "avg loss R": s.get("avg_loss_R"),
                            "exp R": s.get("expectancy_R", 0), "avg % per trade": trades["pct"].mean() if len(trades) else 0,
                            "days": s.get("avg_days_held", 0), "maxDD": s["max_drawdown"]})
            row[f"CAGR {rname}"] = s["cagr"]
            if rname == "full, costs":
                row["maxDD costs"] = s["max_drawdown"]
            if len(trades):
                safe = "".join(ch if ch.isalnum() else "_" for ch in vname).strip("_")
                trades.to_csv(OUT / "variants" / f"{safe}__{rname.replace(', ', '_').replace(' ', '')}.csv", index=False)
        rows.append(row)
        print(f"{vname:48s} exp={row['exp R']:+.2f}R  CAGR nocost={row['CAGR full, no costs']:+.1%} "
              f"costs={row['CAGR full, costs']:+.1%}  11-18={row['CAGR 2011-18, costs']:+.1%}  19-26={row['CAGR 2019-26, costs']:+.1%}")

    # SPY reference for the same windows (price only)
    def cagr(s):
        yrs = (s.index[-1] - s.index[0]).days / 365.25
        return (s.iloc[-1] / s.iloc[0]) ** (1 / yrs) - 1
    ref = {"variant": "SPY buy & hold (no dividends)",
           "CAGR full, no costs": cagr(spy), "CAGR full, costs": cagr(spy),
           "CAGR 2011-18, costs": cagr(spy.loc[:"2018-12-31"]), "CAGR 2019-26, costs": cagr(spy.loc["2019-01-01":]),
           "maxDD": float((spy / spy.cummax() - 1).min())}
    rows.append(ref)

    df = pd.DataFrame(rows)
    df.to_csv(OUT / "variants.csv", index=False)
    cols = ["trades", "win%", "avg win R", "avg loss R", "exp R", "avg % per trade", "days", "maxDD",
            "CAGR full, no costs", "CAGR full, costs", "CAGR 2011-18, costs", "CAGR 2019-26, costs"]
    fmt = {"trades": "{:.0f}", "win%": "{:.0%}", "avg win R": "{:+.2f}", "avg loss R": "{:+.2f}", "exp R": "{:+.2f}",
           "avg % per trade": "{:+.2%}", "days": "{:.1f}", "maxDD": "{:.0%}"}
    md = ["| Variant | " + " | ".join(cols) + " |", "|---|" + "---|" * len(cols)]
    for _, r in df.iterrows():
        cells = []
        for c in cols:
            v = r.get(c)
            if v is None or v != v:
                cells.append("")
            else:
                cells.append((fmt.get(c) or "{:+.1%}").format(v))
        md.append(f"| {r['variant']} | " + " | ".join(cells) + " |")
    (OUT / "variants.md").write_text("\n".join(md) + "\n")
    print("Wrote results/variants.md")


if __name__ == "__main__":
    (OUT / "variants").mkdir(exist_ok=True)
    main()
