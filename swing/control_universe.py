"""A control group for the dip study: companies that were large or widely
followed at some point since 2010 and have since lagged, stalled or crashed,
but are still trading (delisted companies are not available for free).

If "buy a strong stock after a big dip" only works on today's winners and not
on these, the effect is survivorship bias, not an edge.
"""
FALLEN = [
    # old-economy large caps that went sideways or down for years
    "F", "GM", "HPQ", "EBAY", "BBY", "TGT", "KR", "WBA", "KHC", "MO", "BA", "MMM",
    "SLB", "HAL", "FCX", "MOS", "APA", "DVN", "OXY", "X", "AA", "PCG", "EXC", "D",
    "DUK", "CL", "KMB", "GIS", "K", "CPB", "VFC", "HAS", "PARA", "WBD", "NKE", "CVS",
    "HUM", "CI", "BIIB", "ILMN", "PFE", "MRK", "GILD", "INTC", "CSCO", "IBM", "T", "VZ",
    # travel / leisure
    "CCL", "RCL", "AAL", "DAL", "LUV", "LVS", "WYNN", "MGM",
    # pandemic-era and meme-era favourites
    "PTON", "ZM", "DOCU", "TDOC", "PYPL", "SHOP", "SNAP", "PINS", "ETSY", "W", "CHWY",
    "CVNA", "PLUG", "GME", "AMC", "HOOD", "COIN", "RBLX", "U", "AFRM", "UPST", "SOFI",
    "MRNA", "BNTX", "NVAX", "ROKU", "SQ", "TWLO", "OKTA", "ZS", "CRWD", "NET", "DDOG",
    "SNOW", "PATH", "ABNB", "DASH", "LYFT", "UBER",
    # added on request: widely followed "it always comes back" names
    "MSTR", "SNDK",
]
FALLEN = list(dict.fromkeys(FALLEN))
