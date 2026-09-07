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


# Sector labels (used for display and because financial companies need
# different valuation measures: cash flow is meaningless for a bank).
SECTORS = {
    **{t: "Technology" for t in ["AAPL", "MSFT", "NVDA", "AVGO", "ORCL", "CRM", "ADBE", "AMD", "CSCO", "ACN", "IBM",
                                 "NOW", "INTU", "QCOM", "TXN", "AMAT", "MU", "ADI", "LRCX", "KLAC", "PANW", "ANET",
                                 "PLTR", "INTC", "HPQ", "SHOP", "SNAP", "PINS", "ZM", "DOCU", "TWLO", "OKTA", "ZS",
                                 "CRWD", "NET", "DDOG", "SNOW", "PATH", "U", "RBLX", "ROKU", "PTON", "SQ", "PYPL",
                                 "COIN", "HOOD", "AFFRM", "AFRM", "UPST", "SOFI", "FISV", "ADP", "ETSY", "W", "CHWY",
                                 "EBAY", "CVNA", "TDOC", "ABNB", "DASH", "LYFT", "UBER", "GME", "AMC", "MSTR", "SNDK"]},
    **{t: "Communication" for t in ["GOOGL", "META", "NFLX", "CMCSA", "DIS", "TMUS", "VZ", "T", "PARA", "WBD"]},
    **{t: "Consumer" for t in ["AMZN", "TSLA", "WMT", "COST", "PG", "HD", "KO", "PEP", "MCD", "PM", "LOW", "TJX",
                               "SBUX", "MDLZ", "BKNG", "NKE", "TGT", "KR", "KHC", "MO", "CL", "KMB", "GIS", "K",
                               "CPB", "VFC", "HAS", "BBY", "F", "GM", "CCL", "RCL", "LVS", "WYNN", "MGM", "WBA"]},
    **{t: "Financials" for t in ["BRK-B", "JPM", "V", "MA", "BAC", "WFC", "GS", "MS", "AXP", "C", "SCHW", "BLK",
                                 "SPGI", "PGR", "CB", "MRSH", "BX", "ICE"]},
    **{t: "Health care" for t in ["LLY", "UNH", "JNJ", "ABBV", "MRK", "TMO", "ABT", "ISRG", "AMGN", "PFE", "DHR",
                                  "SYK", "BSX", "VRTX", "GILD", "MDT", "BMY", "REGN", "CVS", "HUM", "CI", "BIIB",
                                  "ILMN", "MRNA", "BNTX", "NVAX"]},
    **{t: "Industrials" for t in ["GE", "CAT", "RTX", "HON", "UNP", "ETN", "LMT", "DE", "BA", "MMM", "AAL", "DAL",
                                  "LUV", "X", "AA", "PLUG"]},
    **{t: "Energy & materials" for t in ["XOM", "CVX", "COP", "LIN", "SLB", "HAL", "FCX", "MOS", "APA", "DVN", "OXY"]},
    **{t: "Utilities & real estate" for t in ["NEE", "PLD", "PCG", "EXC", "D", "DUK"]},
}
try:                                   # mid- and small-cap lists, if present
    from .universe_extra import EXTRA_SECTORS
    for _t, _s in EXTRA_SECTORS.items():
        SECTORS.setdefault(_t, _s)
except Exception:                      # the lists are optional
    pass
FINANCIAL = {t for t, s in SECTORS.items() if s == "Financials"}
