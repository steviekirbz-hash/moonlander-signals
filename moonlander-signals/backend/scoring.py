"""
Scoring Engine
Combines all indicators into a final 7-tier confidence score
"""

from typing import Dict, Optional, List
from dataclasses import dataclass
import logging

from config import SCORING_WEIGHTS, SCORE_THRESHOLDS, TIMEFRAMES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SignalScore:
    """Final signal score for an asset"""
    score: int  # -3 to +3
    label: str  # "STRONG SHORT" to "STRONG LONG"
    composite_score: float  # Raw weighted score
    confidence: float  # 0-1 confidence level
    breakdown: Dict  # Detailed breakdown by indicator


SCORE_LABELS = {
    -3: "STRONG SHORT",
    -2: "SHORT",
    -1: "LEAN SHORT",
    0: "NEUTRAL",
    1: "LEAN LONG",
    2: "LONG",
    3: "STRONG LONG",
}


def count_aligned_timeframes(indicator_results: Dict[str, Dict], indicator_key: str) -> Dict:
    """
    Count how many timeframes are aligned bullish/bearish for a given indicator
    Returns alignment count and overall signal
    """
    bullish_count = 0
    bearish_count = 0
    neutral_count = 0
    total_strength = 0
    
    for tf, indicators in indicator_results.items():
        if not indicators or indicator_key not in indicators:
            continue
        
        ind = indicators[indicator_key]
        if not ind:
            continue
        
        signal = ind.get("signal", "neutral")
        strength = ind.get("strength", 0)
        
        if signal == "bullish":
            bullish_count += 1
        elif signal == "bearish":
            bearish_count += 1
        else:
            neutral_count += 1
        
        total_strength += strength
    
    total = bullish_count + bearish_count + neutral_count
    
    return {
        "bullish": bullish_count,
        "bearish": bearish_count,
        "neutral": neutral_count,
        "total": total,
        "aligned_bullish": bullish_count,
        "aligned_bearish": bearish_count,
        "avg_strength": total_strength / total if total > 0 else 0,
    }


def score_rsi_multi_tf(indicator_results: Dict[str, Dict]) -> Dict:
    """
    Score RSI across all timeframes
    Perfect alignment (all 4 TFs) = maximum score
    """
    alignment = count_aligned_timeframes(indicator_results, "rsi")
    
    # Calculate score based on alignment
    if alignment["aligned_bullish"] == 4:
        score = 1.0  # All bullish = strong long signal
    elif alignment["aligned_bullish"] == 3:
        score = 0.7
    elif alignment["aligned_bullish"] == 2 and alignment["aligned_bearish"] == 0:
        score = 0.4
    elif alignment["aligned_bearish"] == 4:
        score = -1.0  # All bearish = strong short signal
    elif alignment["aligned_bearish"] == 3:
        score = -0.7
    elif alignment["aligned_bearish"] == 2 and alignment["aligned_bullish"] == 0:
        score = -0.4
    else:
        score = alignment["avg_strength"] * 0.3  # Mixed signals
    
    # Collect RSI values for display
    rsi_values = {}
    for tf, indicators in indicator_results.items():
        if indicators and indicators.get("rsi"):
            rsi_values[tf] = indicators["rsi"].get("value", 50)
    
    return {
        "score": score,
        "alignment": alignment,
        "rsi_values": rsi_values,
        "fire_count": max(alignment["aligned_bullish"], alignment["aligned_bearish"]),
    }


def score_ema_multi_tf(indicator_results: Dict[str, Dict]) -> Dict:
    """
    Score EMA trend across all timeframes
    """
    alignment = count_aligned_timeframes(indicator_results, "ema")
    
    # Check for trend confirmation (price above/below trend EMA)
    trend_confirms = 0
    trend_denies = 0
    
    for tf, indicators in indicator_results.items():
        if indicators and indicators.get("ema"):
            ema = indicators["ema"]
            if ema.get("price_above_trend") and ema.get("fast_above_slow"):
                trend_confirms += 1
            elif not ema.get("price_above_trend") and not ema.get("fast_above_slow"):
                trend_denies += 1
    
    if alignment["aligned_bullish"] == 4:
        score = 1.0
    elif alignment["aligned_bullish"] >= 3:
        score = 0.65
    elif alignment["aligned_bearish"] == 4:
        score = -1.0
    elif alignment["aligned_bearish"] >= 3:
        score = -0.65
    else:
        score = alignment["avg_strength"] * 0.4
    
    # Boost if trend confirms
    if trend_confirms >= 3:
        score = min(1.0, score + 0.2)
    elif trend_denies >= 3:
        score = max(-1.0, score - 0.2)
    
    return {
        "score": score,
        "alignment": alignment,
        "trend_confirms": trend_confirms,
        "fire_count": max(alignment["aligned_bullish"], alignment["aligned_bearish"]),
    }


def score_macd_multi_tf(indicator_results: Dict[str, Dict]) -> Dict:
    """
    Score MACD across all timeframes
    """
    alignment = count_aligned_timeframes(indicator_results, "macd")
    
    # Check histogram direction
    histogram_rising = 0
    histogram_falling = 0
    
    for tf, indicators in indicator_results.items():
        if indicators and indicators.get("macd"):
            macd = indicators["macd"]
            if macd.get("histogram_rising"):
                histogram_rising += 1
            else:
                histogram_falling += 1
    
    if alignment["aligned_bullish"] == 4:
        score = 1.0
    elif alignment["aligned_bullish"] >= 3:
        score = 0.6
    elif alignment["aligned_bearish"] == 4:
        score = -1.0
    elif alignment["aligned_bearish"] >= 3:
        score = -0.6
    else:
        score = alignment["avg_strength"] * 0.35
    
    return {
        "score": score,
        "alignment": alignment,
        "histogram_rising": histogram_rising,
        "fire_count": max(alignment["aligned_bullish"], alignment["aligned_bearish"]),
    }


def score_volume(indicator_results: Dict[str, Dict]) -> Dict:
    """
    Score volume confirmation
    High volume on trending timeframes = stronger signal
    """
    volume_scores = []
    
    for tf, indicators in indicator_results.items():
        if indicators and indicators.get("volume"):
            volume = indicators["volume"]
            # Volume doesn't have direction, but confirms strength
            volume_scores.append(volume.get("strength", 0.3))
    
    if not volume_scores:
        return {"score": 0, "avg_volume_strength": 0}
    
    avg_strength = sum(volume_scores) / len(volume_scores)
    
    # Volume is a multiplier/confirmation, not a direction indicator
    # Return the strength which will be used to potentially boost other signals
    return {
        "score": 0,  # Volume doesn't directly contribute to direction
        "avg_volume_strength": avg_strength,
        "confirms_move": avg_strength > 0.5,
    }


def score_bollinger(indicator_results: Dict[str, Dict]) -> Dict:
    """
    Score Bollinger Band position
    Focus on higher timeframes for mean reversion signals
    """
    # Weight higher timeframes more
    tf_weights = {"15m": 0.1, "1h": 0.2, "4h": 0.3, "1d": 0.4}
    
    weighted_score = 0
    total_weight = 0
    
    for tf, indicators in indicator_results.items():
        if indicators and indicators.get("bollinger"):
            bollinger = indicators["bollinger"]
            weight = tf_weights.get(tf, 0.25)
            weighted_score += bollinger.get("strength", 0) * weight
            total_weight += weight
    
    if total_weight == 0:
        return {"score": 0}
    
    score = weighted_score / total_weight
    
    return {
        "score": score,
        "weighted_score": weighted_score,
    }


def score_liquidation_estimate(
    indicator_results: Dict[str, Dict],
    funding_data: Optional[Dict],
    oi_data: Optional[Dict]
) -> Dict:
    """
    Estimate liquidation pressure based on:
    - Price position relative to recent range
    - Open interest levels
    - Funding rate extremes
    """
    score = 0
    
    # Get current price and recent range from 4h timeframe
    if "4h" in indicator_results and indicator_results["4h"]:
        ind = indicator_results["4h"]
        bollinger = ind.get("bollinger")
        
        if bollinger:
            percent_b = bollinger.get("percent_b", 0.5)
            
            # If price is extended, liquidations may pull it back
            if percent_b > 0.9:
                # Extended high - shorts likely getting squeezed, but longs building
                # Liq clusters likely below = bearish magnet
                score = -0.3
            elif percent_b < 0.1:
                # Extended low - longs getting liquidated, shorts building
                # Liq clusters likely above = bullish magnet
                score = 0.3
    
    # Factor in funding rate
    if funding_data:
        funding_rate = funding_data.get("funding_rate", 0)
        
        # Extreme funding suggests crowded positioning
        if funding_rate > 0.0005:  # > 0.05%
            # Very positive = crowded longs = bearish (liq below)
            score -= 0.4
        elif funding_rate < -0.0005:  # < -0.05%
            # Very negative = crowded shorts = bullish (liq above)
            score += 0.4
        elif funding_rate > 0.0002:
            score -= 0.2
        elif funding_rate < -0.0002:
            score += 0.2
    
    return {
        "score": max(-1, min(1, score)),
        "funding_rate": funding_data.get("funding_rate") if funding_data else None,
    }


def score_funding_sentiment(
    funding_data: Optional[Dict],
    ls_ratio_data: Optional[Dict]
) -> Dict:
    """
    Score based on funding rate and long/short ratio
    Extreme positioning often precedes reversals
    """
    score = 0
    
    if funding_data:
        funding_rate = funding_data.get("funding_rate", 0)
        
        # Funding rate signal (contrarian)
        if funding_rate > 0.001:  # > 0.1%
            score -= 0.6  # Extremely crowded longs = bearish
        elif funding_rate > 0.0005:
            score -= 0.3
        elif funding_rate < -0.001:  # < -0.1%
            score += 0.6  # Extremely crowded shorts = bullish
        elif funding_rate < -0.0005:
            score += 0.3
    
    if ls_ratio_data:
        ls_ratio = ls_ratio_data.get("long_short_ratio", 1)
        
        # Extreme L/S ratios (contrarian)
        if ls_ratio > 2:
            score -= 0.3  # Too many longs
        elif ls_ratio > 1.5:
            score -= 0.15
        elif ls_ratio < 0.5:
            score += 0.3  # Too many shorts
        elif ls_ratio < 0.67:
            score += 0.15
    
    return {
        "score": max(-1, min(1, score)),
        "funding_rate": funding_data.get("funding_rate") if funding_data else None,
        "long_short_ratio": ls_ratio_data.get("long_short_ratio") if ls_ratio_data else None,
    }


def calculate_final_score(
    indicator_results: Dict[str, Dict],
    funding_data: Optional[Dict] = None,
    oi_data: Optional[Dict] = None,
    ls_ratio_data: Optional[Dict] = None
) -> SignalScore:
    """
    Calculate the final composite score combining all indicators
    Returns a SignalScore with -3 to +3 rating
    """
    # Calculate individual component scores
    rsi_score = score_rsi_multi_tf(indicator_results)
    ema_score = score_ema_multi_tf(indicator_results)
    macd_score = score_macd_multi_tf(indicator_results)
    volume_score = score_volume(indicator_results)
    bollinger_score = score_bollinger(indicator_results)
    liq_score = score_liquidation_estimate(indicator_results, funding_data, oi_data)
    funding_score = score_funding_sentiment(funding_data, ls_ratio_data)
    
    # Calculate weighted composite score
    weights = SCORING_WEIGHTS
    
    composite = (
        rsi_score["score"] * weights["rsi_multi_tf"] +
        ema_score["score"] * weights["ema_trend_multi_tf"] +
        macd_score["score"] * weights["macd_multi_tf"] +
        volume_score["score"] * weights["volume_confirmation"] +
        bollinger_score["score"] * weights["bollinger_position"] +
        liq_score["score"] * weights["liquidation_estimate"] +
        funding_score["score"] * weights["funding_sentiment"]
    )
    
    # Volume can boost signals if high
    if volume_score.get("confirms_move") and abs(composite) > 0.2:
        boost = 0.1 * (1 if composite > 0 else -1)
        composite = max(-1, min(1, composite + boost))
    
    # Convert composite (-1 to 1) to 7-tier score (-3 to 3)
    thresholds = SCORE_THRESHOLDS
    
    if composite >= thresholds["strong_long"]:
        final_score = 3
    elif composite >= thresholds["long"]:
        final_score = 2
    elif composite >= thresholds["lean_long"]:
        final_score = 1
    elif composite <= thresholds["strong_short"]:
        final_score = -3
    elif composite <= thresholds["short"]:
        final_score = -2
    elif composite <= thresholds["lean_short"]:
        final_score = -1
    else:
        final_score = 0
    
    # Calculate confidence based on indicator agreement
    agreements = [
        1 if rsi_score["score"] * composite > 0 else 0,
        1 if ema_score["score"] * composite > 0 else 0,
        1 if macd_score["score"] * composite > 0 else 0,
        1 if bollinger_score["score"] * composite > 0 else 0,
        1 if funding_score["score"] * composite > 0 else 0,
    ]
    confidence = sum(agreements) / len(agreements) if agreements else 0.5
    
    breakdown = {
        "rsi": rsi_score,
        "ema": ema_score,
        "macd": macd_score,
        "volume": volume_score,
        "bollinger": bollinger_score,
        "liquidation": liq_score,
        "funding": funding_score,
    }
    
    return SignalScore(
        score=final_score,
        label=SCORE_LABELS[final_score],
        composite_score=round(composite, 4),
        confidence=round(confidence, 2),
        breakdown=breakdown,
    )


def test_scoring():
    """Test the scoring engine with mock data"""
    # Create mock indicator results
    mock_results = {
        "15m": {
            "rsi": {"value": 25, "signal": "bullish", "strength": 0.8},
            "ema": {"signal": "bullish", "strength": 0.6, "price_above_trend": True, "fast_above_slow": True},
            "macd": {"signal": "bullish", "strength": 0.5, "histogram_rising": True},
            "bollinger": {"signal": "bullish", "strength": 0.4, "percent_b": 0.15},
            "volume": {"signal": "above_average", "strength": 0.6},
        },
        "1h": {
            "rsi": {"value": 28, "signal": "bullish", "strength": 0.7},
            "ema": {"signal": "bullish", "strength": 0.5, "price_above_trend": True, "fast_above_slow": True},
            "macd": {"signal": "bullish", "strength": 0.4, "histogram_rising": True},
            "bollinger": {"signal": "bullish", "strength": 0.3, "percent_b": 0.2},
            "volume": {"signal": "average", "strength": 0.3},
        },
        "4h": {
            "rsi": {"value": 35, "signal": "neutral", "strength": 0.2},
            "ema": {"signal": "bullish", "strength": 0.4, "price_above_trend": True, "fast_above_slow": True},
            "macd": {"signal": "bullish", "strength": 0.3, "histogram_rising": True},
            "bollinger": {"signal": "neutral", "strength": 0.1, "percent_b": 0.4},
            "volume": {"signal": "average", "strength": 0.3},
        },
        "1d": {
            "rsi": {"value": 42, "signal": "neutral", "strength": 0.1},
            "ema": {"signal": "neutral", "strength": 0.1, "price_above_trend": True, "fast_above_slow": False},
            "macd": {"signal": "neutral", "strength": 0.0, "histogram_rising": False},
            "bollinger": {"signal": "neutral", "strength": 0.0, "percent_b": 0.5},
            "volume": {"signal": "low", "strength": 0.1},
        },
    }
    
    mock_funding = {"funding_rate": -0.0003}  # Slightly negative = bullish
    mock_ls_ratio = {"long_short_ratio": 0.8}  # More shorts = bullish
    
    print("Testing scoring engine with mock bullish data...")
    result = calculate_final_score(mock_results, mock_funding, None, mock_ls_ratio)
    
    print(f"\nFinal Score: {result.score} ({result.label})")
    print(f"Composite: {result.composite_score}")
    print(f"Confidence: {result.confidence}")
    print("\nBreakdown:")
    for name, data in result.breakdown.items():
        print(f"  {name}: {data.get('score', 'N/A'):.2f}")


if __name__ == "__main__":
    test_scoring()
