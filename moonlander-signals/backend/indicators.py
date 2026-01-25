"""
Technical Indicators for CoinGecko data
Simplified version that works with OHLC and price data
"""

import logging
from typing import Dict, List, Optional, Tuple
import math

logger = logging.getLogger(__name__)


def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
    """
    Calculate RSI from price list
    Returns value 0-100
    """
    if len(prices) < period + 1:
        return None
    
    # Calculate price changes
    changes = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    
    # Get recent changes for the period
    recent_changes = changes[-(period):]
    
    gains = [c if c > 0 else 0 for c in recent_changes]
    losses = [-c if c < 0 else 0 for c in recent_changes]
    
    avg_gain = sum(gains) / period
    avg_loss = sum(losses) / period
    
    if avg_loss == 0:
        return 100.0
    
    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))
    
    return round(rsi, 2)


def calculate_ema(prices: List[float], period: int) -> Optional[float]:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return None
    
    multiplier = 2 / (period + 1)
    ema = sum(prices[:period]) / period  # Start with SMA
    
    for price in prices[period:]:
        ema = (price - ema) * multiplier + ema
    
    return ema


def calculate_macd(prices: List[float]) -> Optional[Dict]:
    """
    Calculate MACD (12, 26, 9)
    Returns: macd_line, signal_line, histogram
    """
    if len(prices) < 35:  # Need enough data for 26 EMA + 9 signal
        return None
    
    ema_12 = calculate_ema(prices, 12)
    ema_26 = calculate_ema(prices, 26)
    
    if ema_12 is None or ema_26 is None:
        return None
    
    macd_line = ema_12 - ema_26
    
    # Calculate MACD values for signal line
    macd_values = []
    for i in range(26, len(prices)):
        subset = prices[:i+1]
        e12 = calculate_ema(subset, 12)
        e26 = calculate_ema(subset, 26)
        if e12 and e26:
            macd_values.append(e12 - e26)
    
    if len(macd_values) < 9:
        return None
    
    signal_line = calculate_ema(macd_values, 9)
    histogram = macd_line - signal_line if signal_line else 0
    
    return {
        "macd_line": macd_line,
        "signal_line": signal_line,
        "histogram": histogram,
        "bullish": histogram > 0,
        "rising": len(macd_values) >= 2 and macd_values[-1] > macd_values[-2],
    }


def calculate_bollinger_bands(prices: List[float], period: int = 20, std_dev: float = 2.0) -> Optional[Dict]:
    """Calculate Bollinger Bands"""
    if len(prices) < period:
        return None
    
    recent = prices[-period:]
    sma = sum(recent) / period
    
    # Calculate standard deviation
    variance = sum((p - sma) ** 2 for p in recent) / period
    std = math.sqrt(variance)
    
    upper = sma + (std_dev * std)
    lower = sma - (std_dev * std)
    current_price = prices[-1]
    
    # Calculate %B (position within bands)
    if upper != lower:
        percent_b = (current_price - lower) / (upper - lower)
    else:
        percent_b = 0.5
    
    return {
        "upper": upper,
        "middle": sma,
        "lower": lower,
        "percent_b": percent_b,
        "bandwidth": (upper - lower) / sma if sma > 0 else 0,
    }


def calculate_trend(prices: List[float]) -> Dict:
    """
    Determine trend based on EMAs and price action
    """
    if len(prices) < 50:
        return {"trend": "neutral", "strength": 0}
    
    ema_9 = calculate_ema(prices, 9)
    ema_21 = calculate_ema(prices, 21)
    ema_50 = calculate_ema(prices, 50)
    current = prices[-1]
    
    if not all([ema_9, ema_21, ema_50]):
        return {"trend": "neutral", "strength": 0}
    
    # Count bullish signals
    bullish_count = 0
    if ema_9 > ema_21:
        bullish_count += 1
    if ema_21 > ema_50:
        bullish_count += 1
    if current > ema_50:
        bullish_count += 1
    if current > ema_9:
        bullish_count += 1
    
    if bullish_count >= 3:
        trend = "bullish"
        strength = bullish_count / 4
    elif bullish_count <= 1:
        trend = "bearish"
        strength = (4 - bullish_count) / 4
    else:
        trend = "neutral"
        strength = 0.5
    
    return {
        "trend": trend,
        "strength": strength,
        "ema_9": ema_9,
        "ema_21": ema_21,
        "ema_50": ema_50,
        "price_vs_ema50": "above" if current > ema_50 else "below",
    }


def calculate_momentum(prices: List[float]) -> Dict:
    """Calculate momentum indicators"""
    if len(prices) < 14:
        return {"momentum": 0, "roc": 0}
    
    # Rate of change (14 period)
    roc = ((prices[-1] - prices[-14]) / prices[-14]) * 100 if prices[-14] != 0 else 0
    
    # Simple momentum
    momentum = prices[-1] - prices[-14]
    
    return {
        "momentum": momentum,
        "roc": round(roc, 2),
        "bullish": roc > 0,
    }


def calculate_volatility(prices: List[float], period: int = 14) -> float:
    """Calculate price volatility as percentage"""
    if len(prices) < period:
        return 0
    
    recent = prices[-period:]
    avg = sum(recent) / period
    
    if avg == 0:
        return 0
    
    # Calculate average true range approximation
    changes = [abs(recent[i] - recent[i-1]) / recent[i-1] * 100 
               for i in range(1, len(recent)) if recent[i-1] != 0]
    
    return round(sum(changes) / len(changes), 2) if changes else 0


def analyze_price_data(prices: List[float], symbol: str = "") -> Dict:
    """
    Complete technical analysis on price data
    Returns all indicators and signals
    """
    if not prices or len(prices) < 50:
        logger.warning(f"Insufficient price data for {symbol}: {len(prices) if prices else 0} points")
        return {}
    
    rsi = calculate_rsi(prices)
    macd = calculate_macd(prices)
    bollinger = calculate_bollinger_bands(prices)
    trend = calculate_trend(prices)
    momentum = calculate_momentum(prices)
    volatility = calculate_volatility(prices)
    
    return {
        "rsi": rsi,
        "macd": macd,
        "bollinger": bollinger,
        "trend": trend,
        "momentum": momentum,
        "volatility": volatility,
        "price": prices[-1] if prices else 0,
    }
