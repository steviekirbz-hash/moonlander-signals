# Moonlander Signals - Configuration
# All settings for the crypto signals platform

# =============================================================================
# MOONLANDER CRYPTO ASSETS (excluding stocks/ETFs)
# =============================================================================

MOONLANDER_ASSETS = [
    # Majors
    {"symbol": "BTC", "name": "Bitcoin", "category": "Major", "binance": "BTCUSDT"},
    {"symbol": "ETH", "name": "Ethereum", "category": "Major", "binance": "ETHUSDT"},
    {"symbol": "SOL", "name": "Solana", "category": "Major", "binance": "SOLUSDT"},
    {"symbol": "XRP", "name": "Ripple", "category": "Major", "binance": "XRPUSDT"},
    {"symbol": "ADA", "name": "Cardano", "category": "Major", "binance": "ADAUSDT"},
    {"symbol": "LTC", "name": "Litecoin", "category": "Major", "binance": "LTCUSDT"},
    {"symbol": "BCH", "name": "Bitcoin Cash", "category": "Major", "binance": "BCHUSDT"},
    {"symbol": "DOT", "name": "Polkadot", "category": "Major", "binance": "DOTUSDT"},
    {"symbol": "LINK", "name": "Chainlink", "category": "Major", "binance": "LINKUSDT"},
    {"symbol": "AVAX", "name": "Avalanche", "category": "Major", "binance": "AVAXUSDT"},
    {"symbol": "ATOM", "name": "Cosmos", "category": "Major", "binance": "ATOMUSDT"},
    {"symbol": "NEAR", "name": "Near Protocol", "category": "Major", "binance": "NEARUSDT"},
    {"symbol": "TON", "name": "Toncoin", "category": "Major", "binance": "TONUSDT"},
    {"symbol": "XLM", "name": "Stellar", "category": "Major", "binance": "XLMUSDT"},
    {"symbol": "XMR", "name": "Monero", "category": "Major", "binance": "XMRUSDT"},
    {"symbol": "ZEC", "name": "Zcash", "category": "Major", "binance": "ZECUSDT"},
    
    # Layer 1
    {"symbol": "SUI", "name": "Sui", "category": "Layer 1", "binance": "SUIUSDT"},
    {"symbol": "SEI", "name": "Sei", "category": "Layer 1", "binance": "SEIUSDT"},
    {"symbol": "APT", "name": "Aptos", "category": "Layer 1", "binance": "APTUSDT"},
    {"symbol": "BERA", "name": "Berachain", "category": "Layer 1", "binance": "BERAUSDT"},
    {"symbol": "S", "name": "Sonic", "category": "Layer 1", "binance": "SUSDT"},
    
    # Layer 2
    {"symbol": "OP", "name": "Optimism", "category": "Layer 2", "binance": "OPUSDT"},
    {"symbol": "ARB", "name": "Arbitrum", "category": "Layer 2", "binance": "ARBUSDT"},
    {"symbol": "POL", "name": "Polygon", "category": "Layer 2", "binance": "POLUSDT"},
    {"symbol": "LINEA", "name": "Linea", "category": "Layer 2", "binance": None},  # May not be on Binance
    
    # DeFi
    {"symbol": "AAVE", "name": "Aave", "category": "DeFi", "binance": "AAVEUSDT"},
    {"symbol": "UNI", "name": "Uniswap", "category": "DeFi", "binance": "UNIUSDT"},
    {"symbol": "CRV", "name": "Curve", "category": "DeFi", "binance": "CRVUSDT"},
    {"symbol": "PENDLE", "name": "Pendle", "category": "DeFi", "binance": "PENDLEUSDT"},
    {"symbol": "ENA", "name": "Ethena", "category": "DeFi", "binance": "ENAUSDT"},
    {"symbol": "ONDO", "name": "Ondo", "category": "DeFi", "binance": "ONDOUSDT"},
    {"symbol": "RAY", "name": "Raydium", "category": "DeFi", "binance": "RAYUSDT"},
    {"symbol": "HYPE", "name": "Hyperliquid", "category": "DeFi", "binance": "HYPEUSDT"},
    {"symbol": "WLFI", "name": "World Liberty Fi", "category": "DeFi", "binance": None},
    
    # AI / Infrastructure
    {"symbol": "FET", "name": "Fetch.ai", "category": "AI", "binance": "FETUSDT"},
    {"symbol": "RENDER", "name": "Render", "category": "AI", "binance": "RENDERUSDT"},
    {"symbol": "TAO", "name": "Bittensor", "category": "AI", "binance": "TAOUSDT"},
    {"symbol": "VIRTUAL", "name": "Virtual Protocol", "category": "AI", "binance": "VIRTUALUSDT"},
    {"symbol": "ELIZAOS", "name": "ElizaOS", "category": "AI", "binance": None},
    {"symbol": "FIL", "name": "Filecoin", "category": "Infrastructure", "binance": "FILUSDT"},
    {"symbol": "AXL", "name": "Axelar", "category": "Infrastructure", "binance": "AXLUSDT"},
    
    # Memecoins
    {"symbol": "DOGE", "name": "Dogecoin", "category": "Memecoin", "binance": "DOGEUSDT"},
    {"symbol": "SHIB", "name": "Shiba Inu", "category": "Memecoin", "binance": "SHIBUSDT"},
    {"symbol": "PEPE", "name": "Pepe", "category": "Memecoin", "binance": "PEPEUSDT"},
    {"symbol": "BONK", "name": "Bonk", "category": "Memecoin", "binance": "BONKUSDT"},
    {"symbol": "FLOKI", "name": "Floki", "category": "Memecoin", "binance": "FLOKIUSDT"},
    {"symbol": "WIF", "name": "Dogwifhat", "category": "Memecoin", "binance": "WIFUSDT"},
    {"symbol": "FARTCOIN", "name": "Fartcoin", "category": "Memecoin", "binance": "FARTCOINUSDT"},
    {"symbol": "PENGU", "name": "Pudgy Penguins", "category": "Memecoin", "binance": "PENGUUSDT"},
    {"symbol": "TRUMP", "name": "Trump", "category": "Memecoin", "binance": "TRUMPUSDT"},
    {"symbol": "MELANIA", "name": "Melania", "category": "Memecoin", "binance": "MELANIAUSDT"},
    {"symbol": "SPX6900", "name": "SPX6900", "category": "Memecoin", "binance": None},
    {"symbol": "PUMP", "name": "Pump", "category": "Memecoin", "binance": None},
    
    # Gaming
    {"symbol": "SAND", "name": "Sandbox", "category": "Gaming", "binance": "SANDUSDT"},
    
    # Other
    {"symbol": "HBAR", "name": "Hedera", "category": "Other", "binance": "HBARUSDT"},
    {"symbol": "VET", "name": "VeChain", "category": "Other", "binance": "VETUSDT"},
    {"symbol": "ALGO", "name": "Algorand", "category": "Other", "binance": "ALGOUSDT"},
    {"symbol": "KAITO", "name": "Kaito", "category": "Other", "binance": "KAITOUSDT"},
    {"symbol": "WLD", "name": "Worldcoin", "category": "Other", "binance": "WLDUSDT"},
    {"symbol": "CRO", "name": "Cronos", "category": "Other", "binance": "CROUSDT"},
    {"symbol": "PAXG", "name": "PAX Gold", "category": "Commodity", "binance": "PAXGUSDT"},
    {"symbol": "LION", "name": "Lion", "category": "Other", "binance": None},
    {"symbol": "CRCL", "name": "Circle", "category": "Other", "binance": None},
    {"symbol": "ASTER", "name": "Aster", "category": "Other", "binance": None},
    {"symbol": "AVNT", "name": "Avant", "category": "Other", "binance": None},
    {"symbol": "FIG", "name": "Fig", "category": "Other", "binance": None},
    {"symbol": "MET", "name": "Met", "category": "Other", "binance": None},
    {"symbol": "MON", "name": "Mon", "category": "Other", "binance": None},
    {"symbol": "SKY", "name": "Sky", "category": "Other", "binance": None},
    {"symbol": "XPL", "name": "XPL", "category": "Other", "binance": None},
    {"symbol": "ZORA", "name": "Zora", "category": "Other", "binance": None},
    {"symbol": "A", "name": "A Token", "category": "Other", "binance": None},
    
    # Commodities (crypto-wrapped)
    {"symbol": "XAU", "name": "Gold", "category": "Commodity", "binance": None},  # Use PAXG as proxy
    {"symbol": "XAG", "name": "Silver", "category": "Commodity", "binance": None},
]

# =============================================================================
# TIMEFRAMES
# =============================================================================

TIMEFRAMES = {
    "15m": {"binance": "15m", "periods_needed": 100},
    "1h": {"binance": "1h", "periods_needed": 100},
    "4h": {"binance": "4h", "periods_needed": 100},
    "1d": {"binance": "1d", "periods_needed": 100},
}

# =============================================================================
# INDICATOR SETTINGS
# =============================================================================

INDICATORS = {
    "rsi": {
        "period": 14,
        "oversold": 30,
        "overbought": 70,
        "strong_oversold": 25,
        "strong_overbought": 75,
    },
    "ema": {
        "fast": 9,
        "slow": 21,
        "trend": 50,
    },
    "macd": {
        "fast": 12,
        "slow": 26,
        "signal": 9,
    },
    "bollinger": {
        "period": 20,
        "std_dev": 2,
    },
    "volume": {
        "ma_period": 20,
    },
}

# =============================================================================
# SCORING WEIGHTS
# =============================================================================

SCORING_WEIGHTS = {
    "rsi_multi_tf": 0.20,           # 20% - RSI across all timeframes
    "ema_trend_multi_tf": 0.20,     # 20% - EMA trend across all timeframes
    "macd_multi_tf": 0.15,          # 15% - MACD across all timeframes
    "volume_confirmation": 0.10,     # 10% - Volume confirmation
    "bollinger_position": 0.10,      # 10% - Bollinger band position
    "liquidation_estimate": 0.10,    # 10% - Estimated liquidation zones
    "funding_sentiment": 0.15,       # 15% - Funding rate & sentiment
}

# =============================================================================
# SCORE THRESHOLDS
# =============================================================================

# Composite score ranges for final signal
SCORE_THRESHOLDS = {
    "strong_long": 0.6,      # >= 0.6 = Strong Long (+3)
    "long": 0.35,            # >= 0.35 = Long (+2)
    "lean_long": 0.15,       # >= 0.15 = Lean Long (+1)
    "lean_short": -0.15,     # <= -0.15 = Lean Short (-1)
    "short": -0.35,          # <= -0.35 = Short (-2)
    "strong_short": -0.6,    # <= -0.6 = Strong Short (-3)
}

# =============================================================================
# API SETTINGS
# =============================================================================

BINANCE_BASE_URL = "https://api.binance.com"
BINANCE_FUTURES_URL = "https://fapi.binance.com"

# Rate limiting
API_RATE_LIMIT_DELAY = 0.1  # seconds between requests

# =============================================================================
# CACHE SETTINGS
# =============================================================================

CACHE_DURATION_SECONDS = 3600  # 1 hour
DATA_OUTPUT_PATH = "data/signals.json"
