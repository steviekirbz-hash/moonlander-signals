"""
Fear & Greed Index Client
Fetches market sentiment data from alternative.me API
"""

import aiohttp
import asyncio
import logging
from typing import Dict, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class FearGreedClient:
    """Async client for Fear & Greed Index API"""
    
    BASE_URL = "https://api.alternative.me/fng/"
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.cache: Optional[Dict] = None
        self.cache_time: Optional[datetime] = None
        self.cache_duration = timedelta(minutes=30)  # Cache for 30 minutes
    
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def get_fear_greed(self, days: int = 2) -> Optional[Dict]:
        """
        Get Fear & Greed Index data
        
        Args:
            days: Number of days of data to fetch (default 2 for current + yesterday)
        
        Returns:
            {
                "value": 45,
                "classification": "Fear",
                "timestamp": "2026-01-29",
                "previous_value": 42,
                "previous_classification": "Fear",
                "change_24h": 3,
                "change_direction": "up"
            }
        """
        # Check cache first
        if (self.cache and self.cache_time and 
            datetime.utcnow() - self.cache_time < self.cache_duration):
            return self.cache
        
        session = await self._get_session()
        
        try:
            params = {"limit": days, "format": "json"}
            async with session.get(self.BASE_URL, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    if data.get("data") and len(data["data"]) > 0:
                        current = data["data"][0]
                        previous = data["data"][1] if len(data["data"]) > 1 else None
                        
                        current_value = int(current.get("value", 50))
                        previous_value = int(previous.get("value", current_value)) if previous else current_value
                        change = current_value - previous_value
                        
                        result = {
                            "value": current_value,
                            "classification": current.get("value_classification", "Neutral"),
                            "timestamp": current.get("timestamp"),
                            "previous_value": previous_value,
                            "previous_classification": previous.get("value_classification") if previous else None,
                            "change_24h": change,
                            "change_direction": "up" if change > 0 else ("down" if change < 0 else "unchanged"),
                        }
                        
                        # Cache the result
                        self.cache = result
                        self.cache_time = datetime.utcnow()
                        
                        logger.info(f"Fear & Greed Index: {current_value} ({result['classification']}), 24h change: {change:+d}")
                        return result
                    
                else:
                    logger.warning(f"Fear & Greed API error: {response.status}")
                    
        except asyncio.TimeoutError:
            logger.warning("Fear & Greed API timeout")
        except Exception as e:
            logger.error(f"Error fetching Fear & Greed: {e}")
        
        # Return cached data if available, even if stale
        if self.cache:
            logger.info("Returning stale Fear & Greed cache")
            return self.cache
        
        # Return default neutral if all else fails
        return {
            "value": 50,
            "classification": "Neutral",
            "timestamp": None,
            "previous_value": 50,
            "previous_classification": "Neutral",
            "change_24h": 0,
            "change_direction": "unchanged",
        }


def get_fear_greed_label(value: int) -> str:
    """Convert numeric value to classification label"""
    if value <= 20:
        return "Extreme Fear"
    elif value <= 40:
        return "Fear"
    elif value <= 60:
        return "Neutral"
    elif value <= 80:
        return "Greed"
    else:
        return "Extreme Greed"


def get_fear_greed_signal(value: int) -> float:
    """
    Convert Fear & Greed to a signal score component
    
    Extreme Fear (0-20) = Bullish (contrarian) → +0.3
    Fear (21-40) = Slightly Bullish → +0.15
    Neutral (41-60) = No signal → 0
    Greed (61-80) = Slightly Bearish → -0.15
    Extreme Greed (81-100) = Bearish (contrarian) → -0.3
    """
    if value <= 20:
        return 0.3  # Extreme fear = contrarian bullish
    elif value <= 40:
        return 0.15  # Fear = slightly bullish
    elif value <= 60:
        return 0  # Neutral
    elif value <= 80:
        return -0.15  # Greed = slightly bearish
    else:
        return -0.3  # Extreme greed = contrarian bearish


# Singleton instance
fear_greed_client = FearGreedClient()
