# 🌙 Moonlander Signals

**Multi-Timeframe Crypto Trading Intelligence**

Real-time trading signals for crypto assets available on [moonlander.trade](https://moonlander.trade). Combines technical analysis across multiple timeframes to generate confidence scores from Strong Short (-3) to Strong Long (+3).

![Moonlander Signals](https://img.shields.io/badge/Status-Ready%20to%20Deploy-brightgreen)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-MIT-green)

---

## ✨ Features

### 📊 Multi-Timeframe Analysis
- RSI, EMA, MACD across 15m, 1H, 4H, 1D timeframes
- Fire indicators 🔥🔥🔥🔥 show alignment
- When all timeframes agree, signals are stronger

### 📈 7-Tier Scoring System
| Score | Label | Description |
|-------|-------|-------------|
| +3 | **STRONG LONG** | Maximum bullish confluence |
| +2 | **LONG** | Clear bullish bias |
| +1 | **LEAN LONG** | Slight bullish edge |
| 0 | **NEUTRAL** | Mixed signals |
| -1 | **LEAN SHORT** | Slight bearish edge |
| -2 | **SHORT** | Clear bearish bias |
| -3 | **STRONG SHORT** | Maximum bearish confluence |

### 🎯 Smart Indicators
- **RSI Multi-TF** (20%) - Overbought/oversold across timeframes
- **EMA Trend** (20%) - 9/21 crossovers + price vs 50 EMA
- **MACD** (15%) - Momentum and histogram direction
- **Volume** (10%) - Confirms move strength
- **Bollinger Bands** (10%) - Mean reversion signals
- **Liquidation Zones** (10%) - Estimated liq magnets
- **Funding Rate** (15%) - Crowded positioning

### 💎 Premium UI
- Dark theme with neon accents
- Animated gradient backgrounds
- Smooth Framer Motion transitions
- Responsive on all devices
- Click-to-expand detailed breakdowns

---

## 🚀 Quick Start

### Option 1: Frontend Only (Demo Mode)

Deploy instantly to Vercel with generated demo data:

```bash
cd frontend
npm install
npm run dev
```

### Option 2: Full Stack (Live Data)

1. **Start the Backend:**
```bash
cd backend
pip install -r requirements.txt
python signal_generator.py  # Generate initial data
uvicorn api_server:app --port 8000
```

2. **Start the Frontend:**
```bash
cd frontend
npm install

# Edit .env.local:
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_DEMO_MODE=false

npm run dev
```

---

## 📁 Project Structure

```
moonlander-signals/
├── backend/                 # Python data pipeline
│   ├── config.py           # Assets, indicators, weights
│   ├── binance_client.py   # Async Binance API client
│   ├── indicators.py       # RSI, EMA, MACD, Bollinger
│   ├── scoring.py          # 7-tier scoring engine
│   ├── signal_generator.py # Main orchestrator
│   ├── api_server.py       # FastAPI REST API
│   └── requirements.txt
│
├── frontend/               # Next.js 14 app
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/         # React components
│   ├── lib/               # API client, types
│   ├── package.json
│   └── vercel.json
│
└── README.md
```

---

## 🌐 Deployment

### Deploy Frontend to Vercel (Free)

1. Push to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import repository → Select `frontend` folder
4. Deploy!

The frontend works standalone with demo data, or connect to your backend API.

### Deploy Backend

**Option A: Vercel Serverless**
- Convert to serverless functions
- Use Vercel Cron for hourly updates

**Option B: Railway / Render**
- Deploy as Docker container
- Set up cron job for updates

**Option C: VPS (DigitalOcean, etc.)**
```bash
# Install
pip install -r requirements.txt

# Run API
uvicorn api_server:app --host 0.0.0.0 --port 8000

# Cron for hourly updates
0 * * * * cd /path/to/backend && python signal_generator.py
```

---

## 📡 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `GET /signals` | GET | All signals with filters |
| `GET /signals/{symbol}` | GET | Single asset signal |
| `GET /summary` | GET | Market overview |
| `GET /categories` | GET | Category breakdown |
| `POST /refresh` | POST | Force data refresh |

### Query Parameters

```
GET /signals?category=Memecoin&min_score=2&sort_by=change_24h&sort_dir=desc&limit=10
```

---

## ⚙️ Configuration

### Adjust Scoring Weights

Edit `backend/config.py`:

```python
SCORING_WEIGHTS = {
    "rsi_multi_tf": 0.20,        # Increase for more RSI influence
    "ema_trend_multi_tf": 0.20,
    "macd_multi_tf": 0.15,
    "volume_confirmation": 0.10,
    "bollinger_position": 0.10,
    "liquidation_estimate": 0.10,
    "funding_sentiment": 0.15,
}
```

### Adjust Score Thresholds

```python
SCORE_THRESHOLDS = {
    "strong_long": 0.6,   # Composite score needed for +3
    "long": 0.35,         # For +2
    "lean_long": 0.15,    # For +1
    # etc.
}
```

---

## 🔮 Future Enhancements

- [ ] Add more exchanges (Bybit, OKX)
- [ ] Historical signal accuracy tracking
- [ ] Email/Telegram alerts for strong signals
- [ ] Custom watchlists
- [ ] Price target zones
- [ ] AI-powered signal commentary

---

## 📄 License

MIT - Feel free to use and modify!

---

## 🙏 Credits

- Data: [Binance API](https://binance.com)
- Built for: [moonlander.trade](https://moonlander.trade)
- UI Framework: [Next.js](https://nextjs.org) + [Tailwind CSS](https://tailwindcss.com)
- Animations: [Framer Motion](https://framer.com/motion)

---

**Happy Trading! 🚀**

*Not financial advice. Trade at your own risk.*
