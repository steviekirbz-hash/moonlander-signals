"""
Signal Generator for Moonlander Signals
Uses CoinGecko API for price data + Fear & Greed Index
"""

import asyncio
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

from coingecko_client import coingecko_client, CoinGeckoClient
from fear_greed_client import fear_greed_client
from indicators import analyze_ohlc_data, calculate_relative_volume
from scoring import (
    calculate_signal_score, 
    get_rsi_display, 
    get_adx_display, 
    get_demark_display,
    get_volume_display
)
from config import ASSETS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Generates trading signals from CoinGecko data"""
    
    def __init__(self):
        self.client = coingecko_client
        self.fg_client = fear_greed_client
        self.signals_cache: Dict = {}
        self.fear_greed_cache: Dict = {}
        self.last_update: Optional[datetime] = None
    
    async def get_fear_greed(self) -> Dict:
        """Get current Fear & Greed Index"""
        try:
            fg_data = await self.fg_client.get_fear_greed()
            if fg_data:
                self.fear_greed_cache = fg_data
                return fg_data
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed: {e}")
        
        # Return cached or default
        return self.fear_greed_cache or {
            "value": 50,
            "classification": "Neutral",
            "change_24h": 0,
            "change_direction": "unchanged"
        }
    
    async def process_single_asset(self, symbol: str, market_data: Dict, fear_greed_value: int) -> Optional[Dict]:
        """Process a single asset and generate signal"""
        try:
            asset_info = ASSETS.get(symbol, {})
            
            # Get OHLC data for technical analysis
            ohlc_data = await self.client.get_ohlc_for_asset(symbol, days=30)
            
            if not ohlc_data or len(ohlc_data) < 50:
                logger.warning(f"Insufficient OHLC data for {symbol}")
                return None
            
            # Get volume data for relative volume calculation
            volumes = []
            chart_data = await self.client.get_market_chart(
                self.client.SYMBOL_TO_ID.get(symbol), 
                days=14
            )
            if chart_data and chart_data.get("total_volumes"):
                volumes = [v[1] for v in chart_data["total_volumes"]]
            
            # Run technical analysis on OHLC data
            analysis = analyze_ohlc_data(ohlc_data, symbol)
            
            if not analysis:
                return None
            
            # Add volume analysis
            if volumes and len(volumes) > 7:
                analysis["volume"] = calculate_relative_volume(volumes)
            
            # Calculate signal score with all indicators
            signal = calculate_signal_score(analysis, market_data, fear_greed_value)
            
            # Get display-formatted values
            rsi_data = get_rsi_display(analysis.get("rsi"))
            adx_data = get_adx_display(analysis.get("adx"))
            demark_data = get_demark_display(analysis.get("demark"))
            volume_data = get_volume_display(analysis.get("volume"))
            
            # Build result
            result = {
                "symbol": symbol,
                "name": asset_info.get("name", symbol),
                "category": asset_info.get("category", "Other"),
                "price": market_data.get("price", 0),
                "change_24h": round(market_data.get("change_24h", 0), 2),
                "volume_24h": market_data.get("volume_24h", 0),
                
                # Signal data
                "score": signal["score"],
                "label": signal["label"],
                "composite_score": signal["composite_score"],
                "confidence": signal["confidence"],
                
                # RSI (multi-timeframe display - using same value as approximation)
                "rsi": {
                    "15m": rsi_data["value"],
                    "1h": rsi_data["value"],
                    "4h": rsi_data["value"],
                    "1d": rsi_data["value"],
                },
                
                # New indicators
                "adx": adx_data,
                "demark": demark_data,
                "relative_volume": volume_data,
                
                # Alignment indicators (for fire display)
                "rsi_aligned": 4 if abs(signal["score"]) >= 2 else (2 if signal["score"] != 0 else 0),
                "ema_aligned": 4 if signal["components"]["trend"] > 0.5 else (2 if signal["components"]["trend"] > 0 else 0),
                "macd_aligned": 4 if signal["components"]["macd"] > 0.5 else (2 if signal["components"]["macd"] > 0 else 0),
                
                # Legacy fields (keeping for compatibility, but now N/A)
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
            # Fetch Fear & Greed Index first
            fear_greed = await self.get_fear_greed()
            fg_value = fear_greed.get("value", 50)
            logger.info(f"Fear & Greed Index: {fg_value} ({fear_greed.get('classification')})")
            
            # Get market data for all assets
            market_data = await self.client.get_all_market_data()
            logger.info(f"Fetched market data for {len(market_data)} assets")
            
            if not market_data:
                logger.error("Failed to fetch market data")
                return self._empty_response(fear_greed)
            
            # Process each asset with OHLC data
            assets = []
            processed = 0
            
            for symbol in market_data.keys():
                if symbol not in ASSETS:
                    continue
                
                result = await self.process_single_asset(symbol, market_data[symbol], fg_value)
                
                if result:
                    assets.append(result)
                    processed += 1
                    logger.info(f"Processed {symbol}: {result['label']} (score: {result['score']}, ADX: {result['adx']['value']}, DeMark: {result['demark']['display']})")
                
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
                "fear_greed": fear_greed,
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
            return self._empty_response(self.fear_greed_cache)
    
    def _empty_response(self, fear_greed: Dict = None) -> Dict:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "total_assets": 0,
            "fear_greed": fear_greed or {"value": 50, "classification": "Neutral", "change_24h": 0},
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
        print(f"Fear & Greed: {result['fear_greed']['value']} ({result['fear_greed']['classification']})")
        print(f"Bullish: {result['summary']['bullish']}")
        print(f"Bearish: {result['summary']['bearish']}")
        print(f"Neutral: {result['summary']['neutral']}")
    finally:
        await generator.client.close()
        await generator.fg_client.close()


if __name__ == "__main__":
    asyncio.run(main())
