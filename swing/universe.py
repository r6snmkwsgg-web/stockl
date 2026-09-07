"""The list of stocks we test.

SPY (the S&P 500 ETF) is used as the "market" for the market filter.
The 100 stocks below are roughly the 100 largest, most-traded US companies
as of 2026. IMPORTANT: this is today's list, not the list as it was in 2010.
See the report for why that matters (survivorship bias).
"""

MARKET = "SPY"

STOCKS = [
    # Mega-cap tech / communication
    "AAPL", "MSFT", "NVDA", "AMZN", "GOOGL", "META", "TSLA", "AVGO", "ORCL",
    "NFLX", "CRM", "ADBE", "AMD", "CSCO", "ACN", "IBM", "NOW", "INTU", "QCOM",
    "TXN", "AMAT", "MU", "ADI", "LRCX", "KLAC", "PANW", "ANET", "PLTR", "INTC",
    "UBER", "CMCSA", "DIS", "TMUS", "VZ", "T",
    # Financials
    "BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "C", "SCHW",
    "BLK", "SPGI", "PGR", "CB", "MRSH", "BX", "ICE", "FISV", "ADP",
    # Health care
    "LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "ISRG", "AMGN", "PFE",
    "DHR", "SYK", "BSX", "VRTX", "GILD", "MDT", "BMY", "REGN",
    # Consumer
    "WMT", "COST", "PG", "HD", "KO", "PEP", "MCD", "PM", "LOW", "TJX", "SBUX",
    "MDLZ", "BKNG",
    # Industrials / energy / materials / utilities / real estate
    "XOM", "CVX", "COP", "GE", "CAT", "RTX", "HON", "UNP", "ETN", "LMT", "DE",
    "LIN", "NEE", "PLD",
]

assert len(STOCKS) == 100, len(STOCKS)
assert len(set(STOCKS)) == 100, "duplicate ticker"

ALL_TICKERS = [MARKET] + STOCKS
