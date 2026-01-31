"""
Technical Indicators for CoinGecko data
Includes RSI, MACD, Bollinger Bands, ADX, DeMark Sequential
"""

import logging
from typing import Dict, List, Optional
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


def calculate_adx(highs: List[float], lows: List[float], closes: List[float], period: int = 14) -> Optional[Dict]:
    """
    Calculate Average Directional Index (ADX)
    Measures trend strength (not direction)
    
    Returns:
        adx: 0-100 value (>25 = trending, >50 = strong trend)
        plus_di: +DI line
        minus_di: -DI line
        trending: boolean if ADX > 25
    """
    if len(highs) < period + 1 or len(lows) < period + 1 or len(closes) < period + 1:
        return None
    
    # Calculate True Range and Directional Movement
    tr_list = []
    plus_dm_list = []
    minus_dm_list = []
    
    for i in range(1, len(highs)):
        # True Range
        high_low = highs[i] - lows[i]
        high_close_prev = abs(highs[i] - closes[i-1])
        low_close_prev = abs(lows[i] - closes[i-1])
        tr = max(high_low, high_close_prev, low_close_prev)
        tr_list.append(tr)
        
        # Directional Movement
        up_move = highs[i] - highs[i-1]
        down_move = lows[i-1] - lows[i]
        
        plus_dm = up_move if up_move > down_move and up_move > 0 else 0
        minus_dm = down_move if down_move > up_move and down_move > 0 else 0
        
        plus_dm_list.append(plus_dm)
        minus_dm_list.append(minus_dm)
    
    if len(tr_list) < period:
        return None
    
    # Smooth the values using Wilder's smoothing
    def wilders_smooth(values: List[float], period: int) -> List[float]:
        smoothed = [sum(values[:period])]
        for i in range(period, len(values)):
            smoothed.append(smoothed[-1] - (smoothed[-1] / period) + values[i])
        return smoothed
    
    smoothed_tr = wilders_smooth(tr_list, period)
    smoothed_plus_dm = wilders_smooth(plus_dm_list, period)
    smoothed_minus_dm = wilders_smooth(minus_dm_list, period)
    
    if not smoothed_tr or smoothed_tr[-1] == 0:
        return None
    
    # Calculate +DI and -DI
    plus_di = (smoothed_plus_dm[-1] / smoothed_tr[-1]) * 100
    minus_di = (smoothed_minus_dm[-1] / smoothed_tr[-1]) * 100
    
    # Calculate DX
    di_sum = plus_di + minus_di
    if di_sum == 0:
        return None
    
    dx_list = []
    for i in range(len(smoothed_tr)):
        if smoothed_tr[i] == 0:
            continue
        pdi = (smoothed_plus_dm[i] / smoothed_tr[i]) * 100
        mdi = (smoothed_minus_dm[i] / smoothed_tr[i]) * 100
        di_s = pdi + mdi
        if di_s > 0:
            dx_list.append(abs(pdi - mdi) / di_s * 100)
    
    if len(dx_list) < period:
        return None
    
    # ADX is smoothed DX
    adx = sum(dx_list[-period:]) / period
    
    return {
        "adx": round(adx, 2),
        "plus_di": round(plus_di, 2),
        "minus_di": round(minus_di, 2),
        "trending": adx > 25,
        "strong_trend": adx > 50,
        "direction": "bullish" if plus_di > minus_di else "bearish",
    }


def calculate_demark(closes: List[float]) -> Optional[Dict]:
    """
    Calculate DeMark Sequential (TD Sequential) Setup Phase (1-9)
    
    Sell Setup: 9 consecutive closes < close 4 bars earlier (bearish price action)
                When complete, suggests SELLERS EXHAUSTED â†’ expect bullish reversal
    
    Buy Setup: 9 consecutive closes > close 4 bars earlier (bullish price action)
               When complete, suggests BUYERS EXHAUSTED â†’ expect bearish reversal
    
    Returns:
        count: Current count (1-9)
        direction: 'sell' or 'buy' (describes the setup type, not the signal)
        signal: 'bullish' or 'bearish' (the expected reversal direction)
        active: Whether a count is in progress
        completed: Whether count reached 9
    """
    if len(closes) < 5:  # Need at least 5 bars (current + 4 lookback)
        return {"count": 0, "direction": None, "signal": None, "active": False, "completed": False}
    
    sell_count = 0  # Counting closes < close[i-4] (price falling)
    buy_count = 0   # Counting closes > close[i-4] (price rising)
    
    # Count from the most recent bars backwards to find active sequence
    # We need to find the current active count
    
    # Check the most recent sequence
    for i in range(len(closes) - 1, 3, -1):  # Start from end, need 4 bars lookback
        current_close = closes[i]
        compare_close = closes[i - 4]
        
        if current_close < compare_close:
            # This bar qualifies for sell setup
            if buy_count > 0:
                # Was counting buy, now reset
                buy_count = 0
            sell_count += 1
        elif current_close > compare_close:
            # This bar qualifies for buy setup
            if sell_count > 0:
                # Was counting sell, now reset
                sell_count = 0
            buy_count += 1
        else:
            # Equal - breaks the sequence
            sell_count = 0
            buy_count = 0
        
        # We only care about the current active sequence from the end
        # So we break once we've counted backwards through the active sequence
        if sell_count == 0 and buy_count == 0:
            break
    
    # Actually, let's recalculate going forward to get accurate count
    sell_count = 0
    buy_count = 0
    
    for i in range(4, len(closes)):
        current_close = closes[i]
        compare_close = closes[i - 4]
        
        if current_close < compare_close:
            if buy_count > 0:
                buy_count = 0
            sell_count += 1
            if sell_count >= 9:
                sell_count = 9  # Cap at 9 for setup phase
        elif current_close > compare_close:
            if sell_count > 0:
                sell_count = 0
            buy_count += 1
            if buy_count >= 9:
                buy_count = 9  # Cap at 9 for setup phase
        else:
            sell_count = 0
            buy_count = 0
    
    if sell_count > 0:
        return {
            "count": sell_count,
            "direction": "sell",  # Sell setup (price has been falling)
            "signal": "bullish",   # Expect bullish reversal (sellers exhausted)
            "active": True,
            "completed": sell_count >= 9,
        }
    elif buy_count > 0:
        return {
            "count": buy_count,
            "direction": "buy",   # Buy setup (price has been rising)
            "signal": "bearish",   # Expect bearish reversal (buyers exhausted)
            "active": True,
            "completed": buy_count >= 9,
        }
    else:
        return {
            "count": 0,
            "direction": None,
            "signal": None,
            "active": False,
            "completed": False,
        }


def calculate_relative_volume(volumes: List[float], period: int = 7) -> Optional[Dict]:
    """
    Calculate volume relative to recent average
    
    Returns:
        current: Current volume
        average: Average volume over period
        ratio: Current / Average (1.0 = normal, 2.0 = double average)
        signal: 'high', 'normal', or 'low'
    """
    if len(volumes) < period + 1:
        return None
    
    current_volume = volumes[-1]
    avg_volume = sum(volumes[-(period+1):-1]) / period
    
    if avg_volume == 0:
        return None
    
    ratio = current_volume / avg_volume
    
    if ratio > 1.5:
        signal = "high"
    elif ratio < 0.5:
        signal = "low"
    else:
        signal = "normal"
    
    return {
        "current": current_volume,
        "average": avg_volume,
        "ratio": round(ratio, 2),
        "signal": signal,
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


def analyze_ohlc_data(ohlc: List[List], symbol: str = "") -> Dict:
    """
    Complete technical analysis on OHLC data
    OHLC format: [[timestamp, open, high, low, close], ...]
    
    Returns all indicators and signals
    """
    if not ohlc or len(ohlc) < 50:
        logger.warning(f"Insufficient OHLC data for {symbol}: {len(ohlc) if ohlc else 0} points")
        return {}
    
    # Extract price arrays
    opens = [candle[1] for candle in ohlc]
    highs = [candle[2] for candle in ohlc]
    lows = [candle[3] for candle in ohlc]
    closes = [candle[4] for candle in ohlc]
    
    # Calculate all indicators
    rsi = calculate_rsi(closes)
    macd = calculate_macd(closes)
    bollinger = calculate_bollinger_bands(closes)
    trend = calculate_trend(closes)
    momentum = calculate_momentum(closes)
    volatility = calculate_volatility(closes)
    adx = calculate_adx(highs, lows, closes)
    demark = calculate_demark(closes)
    
    return {
        "rsi": rsi,
        "macd": macd,
        "bollinger": bollinger,
        "trend": trend,
        "momentum": momentum,
        "volatility": volatility,
        "adx": adx,
        "demark": demark,
        "price": closes[-1] if closes else 0,
    }
