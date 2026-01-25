"""
Scoring Engine for Moonlander Signals
Generates -3 to +3 scores based on technical analysis
"""

import logging
from typing import Dict, Optional
from indicators import analyze_price_data

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


def score_momentum(momentum: Dict) -> float:
    """
    Score momentum/ROC
    Returns -1 to +1
    """
    if not momentum:
        return 0
    
    roc = momentum.get("roc", 0)
    
    # Normalize ROC to a score
    if roc > 20:
        return 1.0
    elif roc > 10:
        return 0.7
    elif roc > 5:
        return 0.4
    elif roc > 0:
        return 0.2
    elif roc > -5:
        return -0.2
    elif roc > -10:
        return -0.4
    elif roc > -20:
        return -0.7
    else:
        return -1.0


def calculate_signal_score(analysis: Dict, market_data: Dict = None) -> Dict:
    """
    Calculate final signal score from technical analysis
    
    Weights:
    - RSI: 25%
    - MACD: 20%
    - Trend (EMA): 25%
    - Bollinger: 15%
    - Momentum: 15%
    
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
    
    # Calculate component scores
    rsi_score = score_rsi(analysis.get("rsi"))
    macd_score = score_macd(analysis.get("macd"))
    trend_score = score_trend(analysis.get("trend", {}))
    bollinger_score = score_bollinger(analysis.get("bollinger"))
    momentum_score = score_momentum(analysis.get("momentum", {}))
    
    # Weighted composite (-1 to +1)
    composite = (
        rsi_score * 0.25 +
        macd_score * 0.20 +
        trend_score * 0.25 +
        bollinger_score * 0.15 +
        momentum_score * 0.15
    )
    
    # Factor in 24h change if available
    if market_data:
        change_24h = market_data.get("change_24h", 0)
        if change_24h:
            # Small boost/penalty based on recent performance
            change_factor = max(-0.2, min(0.2, change_24h / 50))
            composite = composite * 0.85 + change_factor * 0.15
    
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
    scores = [rsi_score, macd_score, trend_score, bollinger_score, momentum_score]
    positive = sum(1 for s in scores if s > 0.1)
    negative = sum(1 for s in scores if s < -0.1)
    agreement = max(positive, negative) / len(scores)
    confidence = round(0.4 + (agreement * 0.6), 2)  # 40-100%
    
    return {
        "score": score,
        "label": label,
        "composite_score": round(composite, 4),
        "confidence": confidence,
        "components": {
            "rsi": round(rsi_score, 3),
            "macd": round(macd_score, 3),
            "trend": round(trend_score, 3),
            "bollinger": round(bollinger_score, 3),
            "momentum": round(momentum_score, 3),
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
