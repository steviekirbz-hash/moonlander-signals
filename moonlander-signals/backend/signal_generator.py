"""
Signal Generator for Moonlander Signals
Uses CoinGecko API for price data
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from coingecko_client import coingecko_client, CoinGeckoClient
from indicators import analyze_price_data
from scoring import calculate_signal_score, get_rsi_display
from config import ASSETS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates trading signals from CoinGecko data"""
    
    def __init__(self):
        self.client = coingecko_client
        self.signals_cache: Dict = {}
        self.last_update: Optional[datetime] = None
    
    async def process_single_asset(self, symbol: str, market_data: Dict) -> Optional[Dict]:
        """Process a single asset and generate signal"""
        try:
            asset_info = ASSETS.get(symbol, {})
            
            # Get OHLC data for technical analysis
            ohlc_data = await self.client.get_ohlc_for_asset(symbol, days=14)
            
            if not ohlc_data or len(ohlc_data) < 50:
                logger.warning(f"Insufficient OHLC data for {symbol}")
                return None
            
            # Extract close prices from OHLC [timestamp, open, high, low, close]
            prices = [candle[4] for candle in ohlc_data]
            
            # Run technical analysis
            analysis = analyze_price_data(prices, symbol)
            
            if not analysis:
                return None
            
            # Calculate signal score
            signal = calculate_signal_score(analysis, market_data)
            
            # Get RSI for display
            rsi_data = get_rsi_display(analysis.get("rsi"))
            
            # Build result
            result = {
                "symbol": symbol,
                "name": asset_info.get("name", symbol),
                "category": asset_info.get("category", "Other"),
                "price": market_data.get("price", 0),
                "change_24h": round(market_data.get("change_24h", 0), 2),
                "volume_24h": market_data.get("volume_24h", 0),
                "score": signal["score"],
                "label": signal["label"],
                "composite_score": signal["composite_score"],
                "confidence": signal["confidence"],
                "rsi": {
                    "15m": rsi_data["value"],  # We only have daily OHLC, so use same value
                    "1h": rsi_data["value"],
                    "4h": rsi_data["value"],
                    "1d": rsi_data["value"],
                },
                "rsi_aligned": 4 if abs(signal["score"]) >= 2 else (2 if signal["score"] != 0 else 0),
                "ema_aligned": 4 if signal["components"]["trend"] > 0.5 else (2 if signal["components"]["trend"] > 0 else 0),
                "macd_aligned": 4 if signal["components"]["macd"] > 0.5 else (2 if signal["components"]["macd"] > 0 else 0),
                "funding_rate": None,  # Not available from CoinGecko
                "long_short_ratio": None,
                "liq_zone": "above" if signal["score"] > 0 else ("below" if signal["score"] < 0 else "neutral"),
                "updated_at": datetime.utcnow().isoformat(),
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return None
    
    async def generate_all_signals(self) -> Dict:
        """Generate signals for all configured assets"""
        logger.info("Starting signal generation...")
        
        try:
            # First, get market data for all assets
            market_data = await self.client.get_all_market_data()
            logger.info(f"Fetched market data for {len(market_data)} assets")
            
            if not market_data:
                logger.error("Failed to fetch market data")
                return self._empty_response()
            
            # Process each asset with OHLC data
            assets = []
            processed = 0
            
            for symbol in market_data.keys():
                if symbol not in ASSETS:
                    continue
                
                result = await self.process_single_asset(symbol, market_data[symbol])
                
                if result:
                    assets.append(result)
                    processed += 1
                    logger.info(f"Processed {symbol}: {result['label']} (score: {result['score']})")
                
                # Small delay to respect rate limits
                await asyncio.sleep(0.5)
            
            # Sort by score (strongest signals first)
            assets.sort(key=lambda x: (-x["score"], -x["composite_score"]))
            
            # Calculate summary
            bullish = sum(1 for a in assets if a["score"] > 0)
            bearish = sum(1 for a in assets if a["score"] < 0)
            neutral = sum(1 for a in assets if a["score"] == 0)
            
            summary = {
                "bullish": bullish,
                "bearish": bearish,
                "neutral": neutral,
                "strong_signals": sum(1 for a in assets if abs(a["score"]) >= 2),
                "by_score": {
                    "-3": sum(1 for a in assets if a["score"] == -3),
                    "-2": sum(1 for a in assets if a["score"] == -2),
                    "-1": sum(1 for a in assets if a["score"] == -1),
                    "0": sum(1 for a in assets if a["score"] == 0),
                    "1": sum(1 for a in assets if a["score"] == 1),
                    "2": sum(1 for a in assets if a["score"] == 2),
                    "3": sum(1 for a in assets if a["score"] == 3),
                },
            }
            
            result = {
                "generated_at": datetime.utcnow().isoformat(),
                "total_assets": len(assets),
                "summary": summary,
                "assets": assets,
            }
            
            # Cache the results
            self.signals_cache = result
            self.last_update = datetime.utcnow()
            
            # Save to file
            self.save_signals(result)
            
            logger.info(f"Signal generation complete: {len(assets)} assets processed")
            return result
            
        except Exception as e:
            logger.error(f"Error generating signals: {e}")
            return self._empty_response()
    
    def _empty_response(self) -> Dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_assets": 0,
            "summary": {
                "bullish": 0,
                "bearish": 0,
                "neutral": 0,
                "strong_signals": 0,
                "by_score": {"-3": 0, "-2": 0, "-1": 0, "0": 0, "1": 0, "2": 0, "3": 0},
            },
            "assets": [],
        }
    
    def save_signals(self, data: Dict, filepath: str = "data/signals.json"):
        """Save signals to JSON file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        logger.info(f"Signals saved to {filepath}")
    
    def load_signals(self, filepath: str = "data/signals.json") -> Optional[Dict]:
        """Load signals from JSON file"""
        try:
            if os.path.exists(filepath):
                with open(filepath, "r") as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading signals: {e}")
        return None
    
    def get_cached_signals(self) -> Dict:
        """Get cached signals or load from file"""
        if self.signals_cache:
            return self.signals_cache
        
        loaded = self.load_signals()
        if loaded:
            self.signals_cache = loaded
            return loaded
        
        return self._empty_response()


# Global instance
signal_generator = SignalGenerator()


async def main():
    """Run signal generation"""
    generator = SignalGenerator()
    try:
        result = await generator.generate_all_signals()
        print(f"\nGenerated signals for {result['total_assets']} assets")
        print(f"Bullish: {result['summary']['bullish']}")
        print(f"Bearish: {result['summary']['bearish']}")
        print(f"Neutral: {result['summary']['neutral']}")
    finally:
        await generator.client.close()


if __name__ == "__main__":
    asyncio.run(main())
