"""
Signal Generator for Moonlander Signals V2
Generates trading signals from CoinGecko data with multiple indicators
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime

from coingecko_client import coingecko_client
from indicators import (
    calculate_rsi, calculate_macd, calculate_bollinger_bands,
    calculate_trend, calculate_adx, calculate_demark, calculate_relative_volume
)
from scoring import calculate_composite_score, format_signal_output
from config import ASSETS
from fear_greed_client import fear_greed_client

logger = logging.getLogger(__name__)


def calculate_multi_period_rsi(closes: List[float]) -> Dict[str, Optional[float]]:
    """
    Calculate RSI with different periods to show momentum at different sensitivities.
    
    - RSI(7): Most reactive, shows very recent momentum
    - RSI(10): Reactive, short-term momentum  
    - RSI(14): Standard, medium-term momentum
    - RSI(21): Smoothest, longer-term momentum
    
    We label these as timeframes (15m, 1h, 4h, 1d) for UI purposes,
    but they're actually different RSI periods on daily data.
    """
    if not closes or len(closes) < 22:
        return {"15m": None, "1h": None, "4h": None, "1d": None}
    
    return {
        "15m": calculate_rsi(closes, period=7),   # Most reactive
        "1h": calculate_rsi(closes, period=10),   # Short-term
        "4h": calculate_rsi(closes, period=14),   # Standard
        "1d": calculate_rsi(closes, period=21),   # Smoothest
    }


async def generate_signal(asset_config: Dict) -> Optional[Dict]:
    """
    Generate trading signal for a single asset.
    
    Args:
        asset_config: Asset configuration from config.py
        
    Returns:
        Signal data dictionary or None if failed
    """
    symbol = asset_config["symbol"]
    coingecko_id = asset_config["coingecko_id"]
    
    try:
        # Fetch OHLC data (30 days of daily candles)
        ohlc = await coingecko_client.get_ohlc(coingecko_id, days=30)
        
        if not ohlc or len(ohlc) < 25:
            logger.warning(f"Insufficient OHLC data for {symbol}: {len(ohlc) if ohlc else 0} candles")
            return None
        
        # Extract price arrays
        timestamps = [candle[0] for candle in ohlc]
        opens = [candle[1] for candle in ohlc]
        highs = [candle[2] for candle in ohlc]
        lows = [candle[3] for candle in ohlc]
        closes = [candle[4] for candle in ohlc]
        
        # Get current price and 24h change from market data
        market_data = await coingecko_client.get_price(coingecko_id)
        current_price = market_data.get("price", closes[-1]) if market_data else closes[-1]
        change_24h = market_data.get("change_24h", 0) if market_data else 0
        volume_24h = market_data.get("volume_24h", 0) if market_data else 0
        
        # Calculate indicators
        rsi_multi = calculate_multi_period_rsi(closes)
        rsi_primary = rsi_multi.get("4h")  # Use RSI(14) as primary for scoring
        
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
        
        # Calculate composite score
        score_result = calculate_composite_score(
            rsi=rsi_primary,
            macd=macd,
            trend=trend,
            adx=adx,
            demark=demark,
            relative_volume=relative_volume,
        )
        
        # Format output
        signal = format_signal_output(
            symbol=symbol,
            name=asset_config["name"],
            category=asset_config["category"],
            price=current_price,
            change_24h=change_24h,
            volume_24h=volume_24h,
            rsi=rsi_multi,
            macd=macd,
            bollinger=bollinger,
            trend=trend,
            adx=adx,
            demark=demark,
            relative_volume=relative_volume,
            score_result=score_result,
        )
        
        logger.info(f"Processed {symbol}: {signal['label']} (score: {signal['score']}, RSI: {rsi_multi})")
        
        return signal
        
    except Exception as e:
        logger.error(f"Error generating signal for {symbol}: {e}")
        return None


async def generate_all_signals(fear_greed_data: Optional[Dict] = None) -> Dict:
    """
    Generate signals for all configured assets.
    
    Args:
        fear_greed_data: Pre-fetched Fear & Greed data (optional)
        
    Returns:
        Complete signals response with all assets
    """
    # Fetch Fear & Greed if not provided
    if fear_greed_data is None:
        fear_greed_data = await fear_greed_client.get_fear_greed()
    
    if fear_greed_data:
        logger.info(f"Fear & Greed Index: {fear_greed_data.get('value')} ({fear_greed_data.get('classification')})")
    
    signals = []
    
    for asset_config in ASSETS:
        signal = await generate_signal(asset_config)
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
    
    return {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "total_results": len(signals),
        "fear_greed": fear_greed_data,
        "summary": summary,
        "assets": signals,
    }


async def refresh_signals() -> Dict:
    """
    Force refresh all signals (called by /refresh endpoint).
    Clears cache and regenerates everything.
    """
    # Clear CoinGecko cache
    coingecko_client.clear_cache()
    
    # Generate fresh signals
    return await generate_all_signals()
