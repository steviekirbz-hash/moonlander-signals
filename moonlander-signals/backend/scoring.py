"""
Scoring Engine for Moonlander Signals
Generates -3 to +3 scores based on technical analysis

Indicators used:
- RSI (30%) - Overbought/Oversold
- MACD (20%) - Momentum & Crossovers
- ADX (15%) - Trend strength modifier (with exhaustion detection)
- DeMark (20%) - Exhaustion/Reversal signals
- Volume (10%) - Confirmation
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


def score_adx(adx_data: Optional[Dict], base_score: float) -> float:
    """
    ADX modifies the confidence of the existing signal.
    
    Key insight: Very high ADX (>50) often signals trend EXHAUSTION,
    not strength. The trend may be overextended and due for reversal.
    
    ADX Interpretation:
    - 0-20: Weak/no trend - reduce confidence, favor mean reversion
    - 20-40: Healthy trend - boost confidence in trend direction
    - 40-50: Strong trend - moderate boost, watch for exhaustion
    - 50+: Potential exhaustion - reduce confidence, favor reversal
    
    Returns a modifier multiplier (0.7 to 1.2)
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
        # Mean reversion signals might be more reliable
        return 0.85
    elif adx < 30:
        # Developing trend - slight boost if aligned
        return 1.05 if aligned else 0.9
    elif adx < 40:
        # Healthy trend - good confidence
        return 1.15 if aligned else 0.9
    elif adx < 50:
        # Strong trend - but watch for exhaustion
        return 1.1 if aligned else 0.85
    elif adx < 60:
        # Very strong trend - likely overextended
        # Reduce confidence, trend may reverse soon
        return 0.9 if aligned else 1.0
    else:
        # Extreme ADX (>60) - high exhaustion risk
        # Actually favor counter-trend signals slightly
        return 0.8 if aligned else 1.1


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
        base_score = 0.15
    elif count < 8:
        # Building - moderate signal
        base_score = 0.35
    elif count == 8:
        # Almost complete - strong signal
        base_score = 0.55
    else:  # count >= 9
        # Complete setup - very strong reversal signal
        base_score = 0.75
    
    # Apply direction
    if signal == "bullish":
        return base_score
    elif signal == "bearish":
        return -base_score
    else:
        return 0


def score_volume(volume_data: Optional[Dict], price_direction: float = 0) -> float:
    """
    Score relative volume - now considers price direction
    
    High volume CONFIRMS the current move:
    - High volume + price up = bullish confirmation
    - High volume + price down = bearish confirmation
    - Low volume = weak conviction (reduces signal)
    
    Args:
        volume_data: Relative volume data
        price_direction: Positive for up move, negative for down move
    
    Returns -0.5 to +0.5
    """
    if not volume_data:
        return 0
    
    ratio = volume_data.get("ratio", 1.0)
    
    # Determine volume strength
    if ratio > 2.0:
        vol_strength = 0.5  # Very high volume
    elif ratio > 1.5:
        vol_strength = 0.35  # High volume
    elif ratio > 1.2:
        vol_strength = 0.2  # Above average
    elif ratio > 0.8:
        vol_strength = 0  # Normal - no signal
    elif ratio > 0.5:
        vol_strength = -0.15  # Below average - weak
    else:
        vol_strength = -0.25  # Very low volume - very weak
    
    # If we have price direction, volume confirms that direction
    if price_direction > 0 and vol_strength > 0:
        return vol_strength  # High volume confirms bullish
    elif price_direction < 0 and vol_strength > 0:
        return -vol_strength  # High volume confirms bearish
    else:
        # Low volume or no clear direction - just return weakness signal
        return vol_strength if vol_strength < 0 else 0


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
    
    Weights (updated - removed EMA/Bollinger):
    - RSI: 30%
    - MACD: 20%
    - DeMark: 20%
    - Volume: 10%
    - Fear & Greed: 5%
    - ADX: 15% (applied as modifier)
    
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
    
    # Get 24h change for volume direction
    change_24h = 0
    if market_data:
        change_24h = market_data.get("change_24h", 0) or 0
    
    # Calculate base component scores
    rsi_score = score_rsi(analysis.get("rsi"))
    macd_score = score_macd(analysis.get("macd"))
    demark_score = score_demark(analysis.get("demark"))
    volume_score = score_volume(analysis.get("volume"), change_24h)
    fg_score = score_fear_greed(fear_greed)
    
    # Base composite (before ADX modifier)
    # Weights: RSI 30%, MACD 20%, DeMark 20%, Volume 10%, F&G 5% = 85%
    # Remaining 15% is implicit in the ADX modifier
    base_composite = (
        rsi_score * 0.30 +
        macd_score * 0.20 +
        demark_score * 0.20 +
        volume_score * 0.10 +
        fg_score * 0.05
    )
    
    # Normalize to account for ADX portion
    base_composite = base_composite / 0.85
    
    # Apply ADX as trend strength/exhaustion modifier
    adx_modifier = score_adx(analysis.get("adx"), base_composite)
    composite = base_composite * adx_modifier
    
    # Map composite to -3 to +3 score
    if composite >= 0.55:
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
    elif composite >= -0.55:
        score = -2
        label = "SHORT"
    else:
        score = -3
        label = "STRONG SHORT"
    
    # Calculate confidence based on indicator agreement
    scores = [rsi_score, macd_score, demark_score]
    positive = sum(1 for s in scores if s > 0.1)
    negative = sum(1 for s in scores if s < -0.1)
    agreement = max(positive, negative) / len(scores)
    
    # ADX value affects confidence (but high ADX = less certain due to exhaustion risk)
    adx_data = analysis.get("adx", {})
    adx_value = adx_data.get("adx", 25) if adx_data else 25
    
    # Confidence peaks around ADX 30-40, lower at extremes
    if adx_value < 20:
        adx_confidence = 0.05
    elif adx_value < 40:
        adx_confidence = 0.15
    elif adx_value < 50:
        adx_confidence = 0.1
    else:
        adx_confidence = 0.05  # High ADX = more uncertainty
    
    confidence = round(0.4 + (agreement * 0.4) + adx_confidence, 2)
    confidence = min(1.0, confidence)
    
    return {
        "score": score,
        "label": label,
        "composite_score": round(composite, 4),
        "confidence": confidence,
        "components": {
            "rsi": round(rsi_score, 3),
            "macd": round(macd_score, 3),
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
    elif adx < 50:
        strength = "strong"
    else:
        strength = "exhausted"  # Changed from "very strong" to indicate potential exhaustion
    
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
