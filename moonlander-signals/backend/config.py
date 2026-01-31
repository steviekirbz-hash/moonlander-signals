"""
Configuration for Moonlander Signals
Asset definitions and settings
"""

# All Moonlander assets with metadata
ASSETS = {
    # Majors
    "BTC": {"name": "Bitcoin", "category": "Major"},
    "ETH": {"name": "Ethereum", "category": "Major"},
    "SOL": {"name": "Solana", "category": "Major"},
    "XRP": {"name": "Ripple", "category": "Major"},
    "ADA": {"name": "Cardano", "category": "Major"},
    "LTC": {"name": "Litecoin", "category": "Major"},
    "BCH": {"name": "Bitcoin Cash", "category": "Major"},
    "DOT": {"name": "Polkadot", "category": "Major"},
    "LINK": {"name": "Chainlink", "category": "Major"},
    "AVAX": {"name": "Avalanche", "category": "Major"},
    "ATOM": {"name": "Cosmos", "category": "Major"},
    "NEAR": {"name": "Near Protocol", "category": "Major"},
    "TON": {"name": "Toncoin", "category": "Major"},
    "XLM": {"name": "Stellar", "category": "Major"},
    "XMR": {"name": "Monero", "category": "Major"},
    "ZEC": {"name": "Zcash", "category": "Major"},
    
    # Layer 1
    "SUI": {"name": "Sui", "category": "Layer 1"},
    "SEI": {"name": "Sei", "category": "Layer 1"},
    "APT": {"name": "Aptos", "category": "Layer 1"},
    "BERA": {"name": "Berachain", "category": "Layer 1"},
    
    # Layer 2
    "OP": {"name": "Optimism", "category": "Layer 2"},
    "ARB": {"name": "Arbitrum", "category": "Layer 2"},
    "POL": {"name": "Polygon", "category": "Layer 2"},
    
    # DeFi
    "AAVE": {"name": "Aave", "category": "DeFi"},
    "UNI": {"name": "Uniswap", "category": "DeFi"},
    "CRV": {"name": "Curve", "category": "DeFi"},
    "PENDLE": {"name": "Pendle", "category": "DeFi"},
    "ENA": {"name": "Ethena", "category": "DeFi"},
    "ONDO": {"name": "Ondo", "category": "DeFi"},
    "RAY": {"name": "Raydium", "category": "DeFi"},
    "HYPE": {"name": "Hyperliquid", "category": "DeFi"},
    
    # AI
    "FET": {"name": "Fetch.ai", "category": "AI"},
    "RENDER": {"name": "Render", "category": "AI"},
    "TAO": {"name": "Bittensor", "category": "AI"},
    "VIRTUAL": {"name": "Virtual Protocol", "category": "AI"},
    
    # Infrastructure
    "FIL": {"name": "Filecoin", "category": "Infrastructure"},
    "AXL": {"name": "Axelar", "category": "Infrastructure"},
    
    # Memecoins
    "DOGE": {"name": "Dogecoin", "category": "Memecoin"},
    "SHIB": {"name": "Shiba Inu", "category": "Memecoin"},
    "PEPE": {"name": "Pepe", "category": "Memecoin"},
    "BONK": {"name": "Bonk", "category": "Memecoin"},
    "FLOKI": {"name": "Floki", "category": "Memecoin"},
    "WIF": {"name": "Dogwifhat", "category": "Memecoin"},
    "FARTCOIN": {"name": "Fartcoin", "category": "Memecoin"},
    "PENGU": {"name": "Pudgy Penguins", "category": "Memecoin"},
    "TRUMP": {"name": "Official Trump", "category": "Memecoin"},
    "MELANIA": {"name": "Official Melania", "category": "Memecoin"},
    
    # Gaming
    "SAND": {"name": "Sandbox", "category": "Gaming"},
    
    # Other
    "HBAR": {"name": "Hedera", "category": "Other"},
    "VET": {"name": "VeChain", "category": "Other"},
    "ALGO": {"name": "Algorand", "category": "Other"},
    "KAITO": {"name": "Kaito", "category": "Other"},
    "WLD": {"name": "Worldcoin", "category": "Other"},
    "CRO": {"name": "Cronos", "category": "Other"},
    
    # Commodity
    "PAXG": {"name": "PAX Gold", "category": "Commodity"},
}

# Timeframes for analysis (reference only - CoinGecko has limited timeframe data)
TIMEFRAMES = ["15m", "1h", "4h", "1d"]

# Scoring thresholds
SCORE_THRESHOLDS = {
    "strong_long": 0.6,
    "long": 0.35,
    "lean_long": 0.15,
    "neutral_upper": 0.15,
    "neutral_lower": -0.15,
    "lean_short": -0.15,
    "short": -0.35,
    "strong_short": -0.6,
}

# Indicator weights for scoring
INDICATOR_WEIGHTS = {
    "rsi": 0.25,
    "macd": 0.15,
    "trend": 0.20,
    "adx": 0.15,  # Applied as modifier
    "demark": 0.15,
    "volume": 0.05,
    "fear_greed": 0.05,
}
