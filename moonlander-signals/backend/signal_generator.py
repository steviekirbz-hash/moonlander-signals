"""
Signal Generator for Moonlander Signals V2
Generates trading signals from CoinGecko data with multiple indicators
"""

import json
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime

from coingecko_client import coingecko_client
from indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_trend, calculate_adx, calculate_demark, calculate_relative_volume
)
from scoring import (
    calculate_signal_score, get_adx_display,
    get_demark_display, get_volume_display
)
from config import ASSETS
from fear_greed_client import fear_greed_client

logger = logging.getLogger(__name__)

CACHE_FILE = "signals_cache.json"


class SignalGenerator:
    """Generates and caches trading signals"""
    
    def __init__(self):
        self.signals_cache: Dict = {}
    
    def calculate_multi_period_rsi(self, closes: List[float]) -> Dict[str, Optional[float]]:
        """
        Calculate RSI with different periods to show momentum at different sensitivities.
        
        - RSI(7): Most reactive, shows very recent momentum (labeled as 15m)
        - RSI(10): Reactive, short-term momentum (labeled as 1h)
        - RSI(14): Standard, medium-term momentum (labeled as 4h)
        - RSI(21): Smoothest, longer-term momentum (labeled as 1d)
        """
        if not closes or len(closes) < 22:
            return {"15m": None, "1h": None, "4h": None, "1d": None}
        
        return {
            "15m": calculate_rsi(closes, period=7),   # Most reactive
            "1h": calculate_rsi(closes, period=10),   # Short-term
            "4h": calculate_rsi(closes, period=14),   # Standard
            "1d": calculate_rsi(closes, period=21),   # Smoothest
        }
    
    async def generate_signal(self, asset_config: Dict, fear_greed_value: Optional[int] = None) -> Optional[Dict]:
        """Generate trading signal for a single asset."""
        symbol = asset_config["symbol"]
        coingecko_id = asset_config["coingecko_id"]
        
        try:
            # Fetch OHLC data (30 days of daily candles)
            ohlc = await coingecko_client.get_ohlc(coingecko_id, days=30)
            
            if not ohlc or len(ohlc) < 25:
                logger.warning(f"Insufficient OHLC data for {symbol}: {len(ohlc) if ohlc else 0} candles")
                return None
            
            # Extract price arrays
            highs = [candle[2] for candle in ohlc]
            lows = [candle[3] for candle in ohlc]
            closes = [candle[4] for candle in ohlc]
            
            # Get current price and 24h change from market data
            market_data = await coingecko_client.get_price(coingecko_id)
            current_price = market_data.get("price", closes[-1]) if market_data else closes[-1]
            change_24h = market_data.get("change_24h", 0) if market_data else 0
            volume_24h = market_data.get("volume_24h", 0) if market_data else 0
            
            # Calculate multi-period RSI
            rsi_multi = self.calculate_multi_period_rsi(closes)
            rsi_primary = rsi_multi.get("4h")  # Use RSI(14) as primary for scoring
            
            # Calculate other indicators
            macd = calculate_macd(closes)
            bollinger = calculate_bollinger_bands(closes)
            trend = calculate_trend(closes)
            adx = calculate_adx(highs, lows, closes)
            demark = calculate_demark(closes)
            
            # Get volume data for relative volume calculation
            volume_data = await coingecko_client.get_market_chart(coingecko_id, days=14)
            relative_volume = None
            if volume_data and "total_volumes" in volume_data:
                volumes = [v[1] for v in volume_data["total_volumes"]]
                relative_volume = calculate_relative_volume(volumes)
            
            # Build analysis dict for scoring
            analysis = {
                "rsi": rsi_primary,
                "macd": macd,
                "bollinger": bollinger,
                "trend": trend,
                "adx": adx,
                "demark": demark,
                "volume": relative_volume,
            }
            
            # Calculate score using existing scoring function
            score_result = calculate_signal_score(
                analysis=analysis,
                market_data={"change_24h": change_24h},
                fear_greed=fear_greed_value
            )
            
            # Format output for API response
            signal = {
                "symbol": symbol,
                "name": asset_config["name"],
                "category": asset_config["category"],
                "price": current_price,
                "change_24h": round(change_24h, 2) if change_24h else 0,
                "volume_24h": volume_24h,
                "score": score_result["score"],
                "label": score_result["label"],
                "composite_score": score_result["composite_score"],
                "confidence": score_result["confidence"],
                "rsi": rsi_multi,  # Multi-period RSI for display
                "adx": get_adx_display(adx),
                "demark": get_demark_display(demark),
                "relative_volume": get_volume_display(relative_volume),
                "ema_aligned": 1 if trend and trend.get("trend") == "bullish" else 0,
                "macd_aligned": 1 if macd and macd.get("bullish") else 0,
                "updated_at": datetime.utcnow().isoformat() + "Z",
            }
            
            logger.info(f"Processed {symbol}: {signal['label']} (score: {signal['score']}, ADX: {adx.get('adx') if adx else 'N/A'}, DeMark: {get_demark_display(demark).get('display')})")
            
            return signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            return None
    
    async def generate_all_signals(self, fear_greed_data: Optional[Dict] = None) -> Dict:
        """Generate signals for all configured assets."""
        # Fetch Fear & Greed if not provided
        if fear_greed_data is None:
            fear_greed_data = await fear_greed_client.get_fear_greed()
        
        fear_greed_value = fear_greed_data.get("value") if fear_greed_data else None
        
        if fear_greed_data:
            logger.info(f"Fear & Greed Index: {fear_greed_value} ({fear_greed_data.get('classification')})")
        
        signals = []
        
        for asset_config in ASSETS:
            signal = await self.generate_signal(asset_config, fear_greed_value)
            if signal:
                signals.append(signal)
        
        # Sort by score (highest first)
        signals.sort(key=lambda x: x["score"], reverse=True)
        
        # Calculate summary
        summary = {
            "bullish": len([s for s in signals if s["score"] > 0]),
            "bearish": len([s for s in signals if s["score"] < 0]),
            "neutral": len([s for s in signals if s["score"] == 0]),
            "strong_signals": len([s for s in signals if abs(s["score"]) >= 2]),
        }
        
        result = {
            "generated_at": datetime.utcnow().isoformat() + "Z",
            "total_assets": len(signals),
            "fear_greed": fear_greed_data,
            "summary": summary,
            "assets": signals,
        }
        
        # Update cache
        self.signals_cache = result
        self.save_signals(result)
        
        return result
    
    def get_cached_signals(self) -> Dict:
        """Get cached signals or empty dict"""
        if self.signals_cache:
            return self.signals_cache
        return {
            "generated_at": None,
            "total_assets": 0,
            "fear_greed": {},
            "summary": {},
            "assets": [],
        }
    
    def save_signals(self, data: Dict) -> None:
        """Save signals to cache file"""
        try:
            with open(CACHE_FILE, 'w') as f:
                json.dump(data, f)
            logger.info(f"Saved {data.get('total_assets', 0)} signals to cache")
        except Exception as e:
            logger.error(f"Error saving cache: {e}")
    
    def load_signals(self) -> Optional[Dict]:
        """Load signals from cache file"""
        try:
            if os.path.exists(CACHE_FILE):
                with open(CACHE_FILE, 'r') as f:
                    data = json.load(f)
                logger.info(f"Loaded {data.get('total_assets', 0)} signals from cache")
                return data
        except Exception as e:
            logger.error(f"Error loading cache: {e}")
        return None


# Singleton instance - this is what api_server.py imports
signal_generator = SignalGenerator()
