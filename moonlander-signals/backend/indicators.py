"""
Technical Indicators Calculator
Calculates RSI, EMA, MACD, Bollinger Bands, and volume indicators
"""

import numpy as np
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass

from config import INDICATORS


@dataclass
class IndicatorResult:
    """Container for indicator calculation results"""
    value: float
    signal: str  # 'bullish', 'bearish', 'neutral'
    strength: float  # -1 to 1 scale


def calculate_ema(prices: List[float], period: int) -> List[float]:
    """Calculate Exponential Moving Average"""
    if len(prices) < period:
        return []
    
    ema = []
    multiplier = 2 / (period + 1)
    
    # Start with SMA for first EMA value
    sma = sum(prices[:period]) / period
    ema.append(sma)
    
    # Calculate EMA for rest of prices
    for price in prices[period:]:
        ema_value = (price - ema[-1]) * multiplier + ema[-1]
        ema.append(ema_value)
    
    return ema


def calculate_sma(prices: List[float], period: int) -> List[float]:
    """Calculate Simple Moving Average"""
    if len(prices) < period:
        return []
    
    sma = []
    for i in range(period - 1, len(prices)):
        sma.append(sum(prices[i - period + 1:i + 1]) / period)
    
    return sma


def calculate_rsi(closes: List[float], period: int = None) -> Optional[IndicatorResult]:
    """
    Calculate Relative Strength Index
    Returns current RSI value and signal
    """
    if period is None:
        period = INDICATORS["rsi"]["period"]
    
    if len(closes) < period + 1:
        return None
    
    # Calculate price changes
    deltas = np.diff(closes)
    
    # Separate gains and losses
    gains = np.where(deltas > 0, deltas, 0)
    losses = np.where(deltas < 0, -deltas, 0)
    
    # Calculate average gain/loss using EMA
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    if avg_loss == 0:
        rsi = 100
    else:
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
    
    # Determine signal
    settings = INDICATORS["rsi"]
    if rsi <= settings["strong_oversold"]:
        signal = "bullish"
        strength = 1.0
    elif rsi <= settings["oversold"]:
        signal = "bullish"
        strength = 0.6
    elif rsi >= settings["strong_overbought"]:
        signal = "bearish"
        strength = -1.0
    elif rsi >= settings["overbought"]:
        signal = "bearish"
        strength = -0.6
    else:
        signal = "neutral"
        # Scale neutral zone: 50 = 0, closer to extremes = higher magnitude
        if rsi < 50:
            strength = (50 - rsi) / 50 * 0.3
        else:
            strength = (50 - rsi) / 50 * 0.3
    
    return IndicatorResult(value=round(rsi, 2), signal=signal, strength=strength)


def calculate_ema_trend(closes: List[float]) -> Optional[Dict]:
    """
    Calculate EMA crossover and trend
    Returns EMA values and signals
    """
    settings = INDICATORS["ema"]
    
    if len(closes) < settings["trend"] + 10:
        return None
    
    ema_fast = calculate_ema(closes, settings["fast"])
    ema_slow = calculate_ema(closes, settings["slow"])
    ema_trend = calculate_ema(closes, settings["trend"])
    
    if not ema_fast or not ema_slow or not ema_trend:
        return None
    
    current_price = closes[-1]
    current_fast = ema_fast[-1]
    current_slow = ema_slow[-1]
    current_trend = ema_trend[-1]
    
    # Previous values for crossover detection
    prev_fast = ema_fast[-2] if len(ema_fast) > 1 else current_fast
    prev_slow = ema_slow[-2] if len(ema_slow) > 1 else current_slow
    
    # Determine signals
    signals = {
        "ema_fast": current_fast,
        "ema_slow": current_slow,
        "ema_trend": current_trend,
        "price_above_trend": current_price > current_trend,
        "fast_above_slow": current_fast > current_slow,
        "bullish_cross": prev_fast <= prev_slow and current_fast > current_slow,
        "bearish_cross": prev_fast >= prev_slow and current_fast < current_slow,
    }
    
    # Calculate overall strength
    strength = 0
    if signals["price_above_trend"]:
        strength += 0.4
    else:
        strength -= 0.4
        
    if signals["fast_above_slow"]:
        strength += 0.4
    else:
        strength -= 0.4
    
    if signals["bullish_cross"]:
        strength += 0.2
    elif signals["bearish_cross"]:
        strength -= 0.2
    
    if strength > 0.2:
        signal = "bullish"
    elif strength < -0.2:
        signal = "bearish"
    else:
        signal = "neutral"
    
    return {
        **signals,
        "signal": signal,
        "strength": max(-1, min(1, strength)),
    }


def calculate_macd(closes: List[float]) -> Optional[Dict]:
    """
    Calculate MACD (Moving Average Convergence Divergence)
    Returns MACD line, signal line, histogram, and signals
    """
    settings = INDICATORS["macd"]
    
    if len(closes) < settings["slow"] + settings["signal"] + 10:
        return None
    
    # Calculate EMAs
    ema_fast = calculate_ema(closes, settings["fast"])
    ema_slow = calculate_ema(closes, settings["slow"])
    
    if not ema_fast or not ema_slow:
        return None
    
    # Align arrays (EMA slow starts later)
    offset = settings["slow"] - settings["fast"]
    ema_fast_aligned = ema_fast[offset:]
    
    if len(ema_fast_aligned) != len(ema_slow):
        min_len = min(len(ema_fast_aligned), len(ema_slow))
        ema_fast_aligned = ema_fast_aligned[-min_len:]
        ema_slow = ema_slow[-min_len:]
    
    # MACD line = Fast EMA - Slow EMA
    macd_line = [f - s for f, s in zip(ema_fast_aligned, ema_slow)]
    
    # Signal line = EMA of MACD line
    signal_line = calculate_ema(macd_line, settings["signal"])
    
    if not signal_line:
        return None
    
    # Align MACD line with signal line
    macd_line = macd_line[-(len(signal_line)):]
    
    # Histogram = MACD line - Signal line
    histogram = [m - s for m, s in zip(macd_line, signal_line)]
    
    current_macd = macd_line[-1]
    current_signal = signal_line[-1]
    current_histogram = histogram[-1]
    prev_histogram = histogram[-2] if len(histogram) > 1 else current_histogram
    
    # Determine signals
    signals = {
        "macd_line": current_macd,
        "signal_line": current_signal,
        "histogram": current_histogram,
        "histogram_rising": current_histogram > prev_histogram,
        "macd_above_signal": current_macd > current_signal,
        "macd_above_zero": current_macd > 0,
    }
    
    # Calculate strength
    strength = 0
    
    if signals["macd_above_signal"]:
        strength += 0.3
    else:
        strength -= 0.3
    
    if signals["macd_above_zero"]:
        strength += 0.2
    else:
        strength -= 0.2
    
    if signals["histogram_rising"]:
        if current_histogram > 0:
            strength += 0.3  # Rising positive histogram = strong bullish
        else:
            strength += 0.2  # Rising negative histogram = weakening bearish
    else:
        if current_histogram < 0:
            strength -= 0.3  # Falling negative histogram = strong bearish
        else:
            strength -= 0.2  # Falling positive histogram = weakening bullish
    
    if strength > 0.2:
        signal = "bullish"
    elif strength < -0.2:
        signal = "bearish"
    else:
        signal = "neutral"
    
    return {
        **signals,
        "signal": signal,
        "strength": max(-1, min(1, strength)),
    }


def calculate_bollinger_bands(closes: List[float]) -> Optional[Dict]:
    """
    Calculate Bollinger Bands
    Returns bands, %B position, and signals
    """
    settings = INDICATORS["bollinger"]
    period = settings["period"]
    std_dev = settings["std_dev"]
    
    if len(closes) < period:
        return None
    
    # Calculate SMA (middle band)
    sma = calculate_sma(closes, period)
    
    if not sma:
        return None
    
    # Calculate standard deviation
    current_closes = closes[-period:]
    current_sma = sma[-1]
    std = np.std(current_closes)
    
    # Calculate bands
    upper_band = current_sma + (std * std_dev)
    lower_band = current_sma - (std * std_dev)
    
    current_price = closes[-1]
    
    # Calculate %B (where price is relative to bands)
    # %B = (Price - Lower Band) / (Upper Band - Lower Band)
    band_width = upper_band - lower_band
    if band_width == 0:
        percent_b = 0.5
    else:
        percent_b = (current_price - lower_band) / band_width
    
    # Determine signal based on %B
    if percent_b <= 0:
        signal = "bullish"  # Price at or below lower band
        strength = 0.8
    elif percent_b <= 0.2:
        signal = "bullish"  # Price near lower band
        strength = 0.5
    elif percent_b >= 1:
        signal = "bearish"  # Price at or above upper band
        strength = -0.8
    elif percent_b >= 0.8:
        signal = "bearish"  # Price near upper band
        strength = -0.5
    else:
        signal = "neutral"
        # Scale: 0.5 = 0, extremes = higher magnitude
        strength = (0.5 - percent_b) * 0.4
    
    return {
        "upper_band": upper_band,
        "middle_band": current_sma,
        "lower_band": lower_band,
        "percent_b": percent_b,
        "band_width": band_width,
        "signal": signal,
        "strength": strength,
    }


def calculate_volume_signal(volumes: List[float]) -> Optional[Dict]:
    """
    Calculate volume relative to moving average
    Returns volume analysis and signals
    """
    period = INDICATORS["volume"]["ma_period"]
    
    if len(volumes) < period:
        return None
    
    volume_ma = calculate_sma(volumes, period)
    
    if not volume_ma:
        return None
    
    current_volume = volumes[-1]
    current_ma = volume_ma[-1]
    
    # Volume ratio
    if current_ma == 0:
        volume_ratio = 1
    else:
        volume_ratio = current_volume / current_ma
    
    # Determine signal (volume confirms moves but doesn't indicate direction)
    if volume_ratio >= 2:
        signal = "high"
        strength = 1.0
    elif volume_ratio >= 1.5:
        signal = "above_average"
        strength = 0.6
    elif volume_ratio >= 0.8:
        signal = "average"
        strength = 0.3
    else:
        signal = "low"
        strength = 0.1
    
    return {
        "current_volume": current_volume,
        "volume_ma": current_ma,
        "volume_ratio": volume_ratio,
        "signal": signal,
        "strength": strength,
    }


def calculate_all_indicators(klines: List[Dict]) -> Optional[Dict]:
    """
    Calculate all indicators for a single timeframe
    """
    if not klines or len(klines) < 50:
        return None
    
    closes = [k["close"] for k in klines]
    volumes = [k["volume"] for k in klines]
    
    rsi = calculate_rsi(closes)
    ema = calculate_ema_trend(closes)
    macd = calculate_macd(closes)
    bollinger = calculate_bollinger_bands(closes)
    volume = calculate_volume_signal(volumes)
    
    return {
        "rsi": rsi.__dict__ if rsi else None,
        "ema": ema,
        "macd": macd,
        "bollinger": bollinger,
        "volume": volume,
        "latest_price": closes[-1],
        "latest_volume": volumes[-1],
    }


def calculate_multi_timeframe_indicators(klines_by_tf: Dict[str, List[Dict]]) -> Dict:
    """
    Calculate indicators across all timeframes
    """
    results = {}
    
    for timeframe, klines in klines_by_tf.items():
        indicators = calculate_all_indicators(klines)
        if indicators:
            results[timeframe] = indicators
    
    return results


# Test function
def test_indicators():
    """Test indicator calculations with sample data"""
    import random
    
    # Generate sample price data (random walk)
    np.random.seed(42)
    base_price = 100
    prices = [base_price]
    for _ in range(99):
        change = np.random.randn() * 2
        prices.append(prices[-1] + change)
    
    volumes = [random.uniform(1000, 5000) for _ in range(100)]
    
    print("Testing indicators with sample data...")
    print(f"Price range: ${min(prices):.2f} - ${max(prices):.2f}")
    print(f"Current price: ${prices[-1]:.2f}")
    print()
    
    # Test RSI
    rsi = calculate_rsi(prices)
    if rsi:
        print(f"RSI: {rsi.value:.2f} ({rsi.signal}, strength: {rsi.strength:.2f})")
    
    # Test EMA
    ema = calculate_ema_trend(prices)
    if ema:
        print(f"EMA: {ema['signal']} (strength: {ema['strength']:.2f})")
        print(f"  Fast/Slow: {ema['ema_fast']:.2f}/{ema['ema_slow']:.2f}")
    
    # Test MACD
    macd = calculate_macd(prices)
    if macd:
        print(f"MACD: {macd['signal']} (strength: {macd['strength']:.2f})")
        print(f"  Histogram: {macd['histogram']:.4f}")
    
    # Test Bollinger
    bollinger = calculate_bollinger_bands(prices)
    if bollinger:
        print(f"Bollinger: {bollinger['signal']} (%B: {bollinger['percent_b']:.2f})")
        print(f"  Bands: {bollinger['lower_band']:.2f} / {bollinger['middle_band']:.2f} / {bollinger['upper_band']:.2f}")
    
    # Test Volume
    volume = calculate_volume_signal(volumes)
    if volume:
        print(f"Volume: {volume['signal']} (ratio: {volume['volume_ratio']:.2f}x)")


if __name__ == "__main__":
    test_indicators()
