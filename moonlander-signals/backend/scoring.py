"""
Scoring Engine for Moonlander Signals
Generates -3 to +3 scores based on technical analysis

Indicators used:
- RSI (25%) - Overbought/Oversold
- MACD (15%) - Momentum & Crossovers
- Trend/EMA (20%) - Trend direction
- ADX (15%) - Trend strength modifier
- DeMark (15%) - Exhaustion/Reversal signals
- Volume (5%) - Confirmation
- Fear & Greed (5%) - Market sentiment
"""

import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


def score_rsi(rsi: Optional[float]) -> float:
    """
    Score RSI: oversold = bullish, overbought = bearish
    Returns -1 to +1
    """
    if rsi is None:
        return 0
    
    if rsi < 20:
        return 1.0  # Extremely oversold - very bullish
    elif rsi < 30:
        return 0.7  # Oversold - bullish
    elif rsi < 40:
        return 0.3  # Slightly oversold
    elif rsi < 60:
        return 0  # Neutral
    elif rsi < 70:
        return -0.3  # Slightly overbought
    elif rsi < 80:
        return -0.7  # Overbought - bearish
    else:
        return -1.0  # Extremely overbought - very bearish


def score_macd(macd: Optional[Dict]) -> float:
    """
    Score MACD signals
    Returns -1 to +1
    """
    if not macd:
        return 0
    
    score = 0
    
    # Histogram direction
    if macd.get("bullish"):
        score += 0.5
    else:
        score -= 0.5
    
    # Momentum (rising/falling)
    if macd.get("rising"):
        score += 0.3
    else:
        score -= 0.3
    
    # MACD line position
    if macd.get("macd_line", 0) > 0:
        score += 0.2
    else:
        score -= 0.2
    
    return max(-1, min(1, score))


def score_trend(trend: Dict) -> float:
    """
    Score EMA trend alignment
    Returns -1 to +1
    """
    if not trend:
        return 0
    
    trend_dir = trend.get("trend", "neutral")
    strength = trend.get("strength", 0)
    
    if trend_dir == "bullish":
        return strength
    elif trend_dir == "bearish":
        return -strength
    else:
        return 0


def score_bollinger(bollinger: Optional[Dict]) -> float:
    """
    Score Bollinger Band position (mean reversion)
    Returns -1 to +1
    """
    if not bollinger:
        return 0
    
    percent_b = bollinger.get("percent_b", 0.5)
    
    # Below lower band = oversold = bullish
    if percent_b < 0:
        return 0.8
    elif percent_b < 0.2:
        return 0.5
    elif percent_b < 0.4:
        return 0.2
    elif percent_b < 0.6:
        return 0  # Middle = neutral
    elif percent_b < 0.8:
        return -0.2
    elif percent_b < 1.0:
        return -0.5
    else:
        return -0.8  # Above upper band = overbought = bearish


def score_adx(adx_data: Optional[Dict], base_score: float) -> float:
    """
    ADX modifies the confidence of the existing signal
    Strong trends (high ADX) = more confidence in trend-following signals
    Weak trends (low ADX) = less confidence, favor mean reversion
    
    Returns a modifier multiplier (0.7 to 1.3)
    """
    if not adx_data:
        return 1.0  # No modification
    
    adx = adx_data.get("adx", 25)
    direction = adx_data.get("direction", "neutral")
    
    # Determine if base score aligns with ADX direction
    score_direction = "bullish" if base_score > 0 else ("bearish" if base_score < 0 else "neutral")
    aligned = (score_direction == direction) or score_direction == "neutral"
    
    if adx < 20:
        # Weak/no trend - reduce confidence in trend signals
        return 0.8
    elif adx < 25:
        # Developing trend
        return 0.9 if aligned else 0.85
    elif adx < 40:
        # Moderate trend
        return 1.1 if aligned else 0.9
    elif adx < 60:
        # Strong trend
        return 1.2 if aligned else 0.85
    else:
        # Very strong trend
        return 1.3 if aligned else 0.8


def score_demark(demark: Optional[Dict]) -> float:
    """
    Score DeMark Sequential signal
    
    Sell Setup (S:1-9): Price falling, sellers getting exhausted
        → When complete (9), expect BULLISH reversal
    
    Buy Setup (B:1-9): Price rising, buyers getting exhausted  
        → When complete (9), expect BEARISH reversal
    
    Returns -1 to +1
    """
    if not demark or not demark.get("active"):
        return 0
    
    count = demark.get("count", 0)
    signal = demark.get("signal")  # 'bullish' or 'bearish'
    completed = demark.get("completed", False)
    
    if count < 6:
        # Early count - weak signal
        base_score = 0.1
    elif count < 8:
        # Building - moderate signal
        base_score = 0.3
    elif count == 8:
        # Almost complete - strong signal
        base_score = 0.5
    else:  # count >= 9
        # Complete setup - very strong signal
        base_score = 0.6
    
    # Apply direction
    if signal == "bullish":
        return base_score
    elif signal == "bearish":
        return -base_score
    else:
        return 0


def score_volume(volume_data: Optional[Dict]) -> float:
    """
    Score relative volume
    High volume confirms moves, low volume suggests weakness
    
    Returns -0.3 to +0.3 (acts as a confidence modifier on existing signal)
    """
    if not volume_data:
        return 0
    
    ratio = volume_data.get("ratio", 1.0)
    
    if ratio > 2.0:
        return 0.3  # Very high volume - strong confirmation
    elif ratio > 1.5:
        return 0.2  # High volume
    elif ratio > 1.2:
        return 0.1  # Above average
    elif ratio > 0.8:
        return 0  # Normal
    elif ratio > 0.5:
        return -0.1  # Below average
    else:
        return -0.2  # Low volume - weak conviction


def score_fear_greed(fg_value: Optional[int]) -> float:
    """
    Score Fear & Greed Index (contrarian indicator)
    
    Extreme Fear = Bullish (buy when others are fearful)
    Extreme Greed = Bearish (sell when others are greedy)
    
    Returns -0.3 to +0.3
    """
    if fg_value is None:
        return 0
    
    if fg_value <= 20:
        return 0.3  # Extreme fear - contrarian bullish
    elif fg_value <= 35:
        return 0.15  # Fear - slightly bullish
    elif fg_value <= 65:
        return 0  # Neutral
    elif fg_value <= 80:
        return -0.15  # Greed - slightly bearish
    else:
        return -0.3  # Extreme greed - contrarian bearish


def calculate_signal_score(analysis: Dict, market_data: Dict = None, fear_greed: int = None) -> Dict:
    """
    Calculate final signal score from technical analysis
    
    Weights:
    - RSI: 25%
    - MACD: 15%
    - Trend (EMA): 20%
    - ADX: 15% (as modifier)
    - DeMark: 15%
    - Volume: 5%
    - Fear & Greed: 5%
    
    Returns score -3 to +3 with label
    """
    if not analysis:
        return {
            "score": 0,
            "label": "NEUTRAL",
            "composite_score": 0,
            "confidence": 0,
            "components": {},
        }
    
    # Calculate base component scores
    rsi_score = score_rsi(analysis.get("rsi"))
    macd_score = score_macd(analysis.get("macd"))
    trend_score = score_trend(analysis.get("trend", {}))
    bollinger_score = score_bollinger(analysis.get("bollinger"))
    demark_score = score_demark(analysis.get("demark"))
    volume_score = score_volume(analysis.get("volume"))
    fg_score = score_fear_greed(fear_greed)
    
    # Base composite (before ADX modifier)
    base_composite = (
        rsi_score * 0.25 +
        macd_score * 0.15 +
        trend_score * 0.20 +
        bollinger_score * 0.05 +
        demark_score * 0.15 +
        volume_score * 0.05 +
        fg_score * 0.05
    )
    
    # Apply ADX as trend strength modifier
    adx_modifier = score_adx(analysis.get("adx"), base_composite)
    composite = base_composite * adx_modifier
    
    # Factor in 24h change if available (small weight)
    if market_data:
        change_24h = market_data.get("change_24h", 0)
        if change_24h:
            # Small boost/penalty based on recent performance
            change_factor = max(-0.15, min(0.15, change_24h / 50))
            composite = composite * 0.9 + change_factor * 0.1
    
    # Map composite to -3 to +3 score
    if composite >= 0.6:
        score = 3
        label = "STRONG LONG"
    elif composite >= 0.35:
        score = 2
        label = "LONG"
    elif composite >= 0.15:
        score = 1
        label = "LEAN LONG"
    elif composite >= -0.15:
        score = 0
        label = "NEUTRAL"
    elif composite >= -0.35:
        score = -1
        label = "LEAN SHORT"
    elif composite >= -0.6:
        score = -2
        label = "SHORT"
    else:
        score = -3
        label = "STRONG SHORT"
    
    # Calculate confidence based on indicator agreement
    scores = [rsi_score, macd_score, trend_score, demark_score]
    positive = sum(1 for s in scores if s > 0.1)
    negative = sum(1 for s in scores if s < -0.1)
    agreement = max(positive, negative) / len(scores)
    
    # ADX also affects confidence
    adx_data = analysis.get("adx", {})
    adx_value = adx_data.get("adx", 25) if adx_data else 25
    adx_confidence_boost = min(0.2, adx_value / 100)
    
    confidence = round(0.4 + (agreement * 0.4) + adx_confidence_boost, 2)
    confidence = min(1.0, confidence)
    
    return {
        "score": score,
        "label": label,
        "composite_score": round(composite, 4),
        "confidence": confidence,
        "components": {
            "rsi": round(rsi_score, 3),
            "macd": round(macd_score, 3),
            "trend": round(trend_score, 3),
            "demark": round(demark_score, 3),
            "adx_modifier": round(adx_modifier, 3),
            "volume": round(volume_score, 3),
            "fear_greed": round(fg_score, 3),
        },
    }


def get_rsi_display(rsi: Optional[float]) -> Dict:
    """Get RSI value formatted for display"""
    if rsi is None:
        return {"value": 50, "signal": "neutral"}
    
    if rsi < 30:
        signal = "oversold"
    elif rsi > 70:
        signal = "overbought"
    else:
        signal = "neutral"
    
    return {"value": round(rsi), "signal": signal}


def get_adx_display(adx_data: Optional[Dict]) -> Dict:
    """Get ADX formatted for display"""
    if not adx_data:
        return {"value": 0, "trend_strength": "none", "direction": "neutral"}
    
    adx = adx_data.get("adx", 0)
    
    if adx < 20:
        strength = "weak"
    elif adx < 40:
        strength = "moderate"
    elif adx < 60:
        strength = "strong"
    else:
        strength = "very strong"
    
    return {
        "value": adx,
        "trend_strength": strength,
        "direction": adx_data.get("direction", "neutral"),
        "trending": adx_data.get("trending", False),
    }


def get_demark_display(demark: Optional[Dict]) -> Dict:
    """Get DeMark Sequential formatted for display"""
    if not demark or not demark.get("active"):
        return {"count": 0, "type": None, "signal": None, "display": "—"}
    
    count = demark.get("count", 0)
    direction = demark.get("direction")  # 'sell' or 'buy'
    signal = demark.get("signal")  # 'bullish' or 'bearish'
    completed = demark.get("completed", False)
    
    # S = Sell setup (price falling, expect bullish reversal)
    # B = Buy setup (price rising, expect bearish reversal)
    type_label = "S" if direction == "sell" else "B"
    
    if completed:
        display = f"{type_label}:9!"
    else:
        display = f"{type_label}:{count}"
    
    return {
        "count": count,
        "type": type_label,
        "signal": signal,
        "display": display,
        "completed": completed,
    }


def get_volume_display(volume_data: Optional[Dict]) -> Dict:
    """Get relative volume formatted for display"""
    if not volume_data:
        return {"ratio": 1.0, "display": "1.0x", "signal": "normal"}
    
    ratio = volume_data.get("ratio", 1.0)
    signal = volume_data.get("signal", "normal")
    
    return {
        "ratio": ratio,
        "display": f"{ratio:.1f}x",
        "signal": signal,
        "current": volume_data.get("current", 0),
        "average": volume_data.get("average", 0),
    }
