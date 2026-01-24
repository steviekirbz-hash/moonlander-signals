# 🌙 Moonlander Signals - Backend

A Python-based crypto trading signals engine that calculates multi-timeframe technical indicators and generates confidence scores for assets available on [moonlander.trade](https://moonlander.trade).

## 📁 Project Structure

```
backend/
├── config.py           # All configuration (assets, indicators, weights)
├── binance_client.py   # Async Binance API client
├── indicators.py       # Technical indicator calculations
├── scoring.py          # Scoring engine (combines indicators → 7-tier score)
├── signal_generator.py # Main orchestrator
├── api_server.py       # FastAPI REST API
└── requirements.txt    # Python dependencies
```

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Generate Signals (One-time)

```bash
python signal_generator.py
```

This will:
- Fetch data for all 50+ tradeable Moonlander assets from Binance
- Calculate indicators across 4 timeframes (15m, 1h, 4h, 1d)
- Generate confidence scores (-3 to +3)
- Save results to `data/signals.json`

### 3. Run the API Server

```bash
uvicorn api_server:app --reload --port 8000
```

API will be available at `http://localhost:8000`

## 📊 How It Works

### Multi-Timeframe Analysis

Each indicator is calculated across **4 timeframes**: 15m, 1H, 4H, 1D

When all timeframes align, the signal is stronger (🔥🔥🔥🔥)

### Indicators Used

| Indicator | Weight | Description |
|-----------|--------|-------------|
| RSI (14) | 20% | Relative Strength Index across all TFs |
| EMA Trend | 20% | 9/21 EMA crossover + price vs 50 EMA |
| MACD | 15% | MACD line, signal, histogram direction |
| Volume | 10% | Volume vs 20-period MA (confirms moves) |
| Bollinger | 10% | Price position within Bollinger Bands |
| Liquidation Est. | 10% | Estimated liq zones from funding/OI |
| Funding/Sentiment | 15% | Funding rate + Long/Short ratio |

### Scoring System

| Score | Label | Meaning |
|-------|-------|---------|
| +3 | STRONG LONG | Maximum bullish confluence |
| +2 | LONG | Clear bullish bias |
| +1 | LEAN LONG | Slight bullish edge |
| 0 | NEUTRAL | Mixed signals |
| -1 | LEAN SHORT | Slight bearish edge |
| -2 | SHORT | Clear bearish bias |
| -3 | STRONG SHORT | Maximum bearish confluence |

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/health` | GET | Health check |
| `/signals` | GET | Get all signals (with filters) |
| `/signals/{symbol}` | GET | Get signal for specific asset |
| `/summary` | GET | Market summary stats |
| `/categories` | GET | List categories with counts |
| `/refresh` | POST | Force refresh signals |

### Example: Get Signals with Filters

```bash
# Get all signals
curl http://localhost:8000/signals

# Get only strong signals
curl "http://localhost:8000/signals?min_score=2"
curl "http://localhost:8000/signals?max_score=-2"

# Filter by category
curl "http://localhost:8000/signals?category=Memecoin"

# Sort by 24h change
curl "http://localhost:8000/signals?sort_by=change_24h&sort_dir=desc"
```

### Example Response

```json
{
  "generated_at": "2026-01-24T12:00:00Z",
  "total_results": 52,
  "assets": [
    {
      "symbol": "BTC",
      "name": "Bitcoin",
      "category": "Major",
      "price": 98500.00,
      "change_24h": 2.35,
      "score": 2,
      "label": "LONG",
      "composite_score": 0.4523,
      "confidence": 0.80,
      "rsi": {
        "15m": 32,
        "1h": 35,
        "4h": 42,
        "1d": 48
      },
      "ema_aligned": 3,
      "macd_aligned": 3,
      "funding_rate": -0.0002,
      "long_short_ratio": 0.85
    }
  ]
}
```

## ⚙️ Configuration

All settings are in `config.py`:

### Adjust Indicator Settings

```python
INDICATORS = {
    "rsi": {
        "period": 14,
        "oversold": 30,      # Adjust these thresholds
        "overbought": 70,
    },
    # ...
}
```

### Adjust Scoring Weights

```python
SCORING_WEIGHTS = {
    "rsi_multi_tf": 0.20,        # Increase RSI importance
    "ema_trend_multi_tf": 0.20,
    "funding_sentiment": 0.15,    # Decrease funding importance
    # ...
}
```

### Adjust Score Thresholds

```python
SCORE_THRESHOLDS = {
    "strong_long": 0.6,   # Make it harder to get Strong Long
    "long": 0.35,
    # ...
}
```

## 🔄 Automated Updates

### Option 1: Cron Job (Linux/Mac)

```bash
# Run every hour
0 * * * * cd /path/to/backend && python signal_generator.py
```

### Option 2: GitHub Actions

```yaml
name: Update Signals
on:
  schedule:
    - cron: '0 * * * *'  # Every hour

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: pip install -r backend/requirements.txt
      - run: python backend/signal_generator.py
      - run: |
          git config user.name github-actions
          git config user.email github-actions@github.com
          git add data/signals.json
          git commit -m "Update signals" || exit 0
          git push
```

### Option 3: Vercel Cron (if deploying to Vercel)

```json
// vercel.json
{
  "crons": [{
    "path": "/api/refresh",
    "schedule": "0 * * * *"
  }]
}
```

## 📈 Data Sources

| Data | Source | Rate Limit |
|------|--------|------------|
| OHLCV (all timeframes) | Binance Spot API | 1200/min |
| Funding Rate | Binance Futures API | 500/min |
| Open Interest | Binance Futures API | 500/min |
| Long/Short Ratio | Binance Futures API | 500/min |

## 🧪 Testing

```bash
# Test indicators
python -c "from indicators import test_indicators; test_indicators()"

# Test scoring
python -c "from scoring import test_scoring; test_scoring()"
```

## 🚧 Assets Not on Binance

Some Moonlander assets don't have Binance pairs:
- LINEA, WLFI, ELIZAOS, SPX6900, PUMP, LION, CRCL, ASTER, AVNT, FIG, MET, MON, SKY, XPL, ZORA, A, XAU, XAG

These are skipped in the current implementation. Future options:
1. Add CoinGecko fallback for price data
2. Use proxy assets (e.g., PAXG for XAU)
3. Scrape data from other sources

## 📝 License

MIT - Feel free to use and modify!

---

**Next Steps:** 
1. Deploy backend to a server (Vercel, Railway, or VPS)
2. Build frontend to consume the API
3. Set up hourly cron job for updates
