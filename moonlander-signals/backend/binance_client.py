"""
Binance API Client
Handles all data fetching from Binance Spot and Futures APIs
"""

import asyncio
import aiohttp
import time
from typing import Optional
from datetime import datetime
import logging

from config import (
    BINANCE_BASE_URL,
    BINANCE_FUTURES_URL,
    API_RATE_LIMIT_DELAY,
    TIMEFRAMES,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BinanceClient:
    """Async client for Binance API"""
    
    def __init__(self):
        self.base_url = BINANCE_BASE_URL
        self.futures_url = BINANCE_FUTURES_URL
        self.session: Optional[aiohttp.ClientSession] = None
        self.last_request_time = 0
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
            
    async def _rate_limit(self):
        """Ensure we don't exceed rate limits"""
        elapsed = time.time() - self.last_request_time
        if elapsed < API_RATE_LIMIT_DELAY:
            await asyncio.sleep(API_RATE_LIMIT_DELAY - elapsed)
        self.last_request_time = time.time()
        
    async def _get(self, url: str, params: dict = None) -> Optional[dict]:
        """Make a GET request with rate limiting"""
        await self._rate_limit()
        
        try:
            async with self.session.get(url, params=params, timeout=10) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.warning(f"API error {response.status} for {url}")
                    return None
        except asyncio.TimeoutError:
            logger.error(f"Timeout fetching {url}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def get_klines(
        self, 
        symbol: str, 
        interval: str, 
        limit: int = 100
    ) -> Optional[list]:
        """
        Fetch OHLCV (kline/candlestick) data
        
        Returns list of:
        [
            open_time, open, high, low, close, volume,
            close_time, quote_volume, trades, taker_buy_base,
            taker_buy_quote, ignore
        ]
        """
        url = f"{self.base_url}/api/v3/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit,
        }
        
        data = await self._get(url, params)
        
        if data:
            # Convert to more usable format
            return [
                {
                    "timestamp": int(candle[0]),
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5]),
                    "close_time": int(candle[6]),
                    "quote_volume": float(candle[7]),
                    "trades": int(candle[8]),
                }
                for candle in data
            ]
        return None
    
    async def get_ticker_24h(self, symbol: str) -> Optional[dict]:
        """Fetch 24h ticker statistics"""
        url = f"{self.base_url}/api/v3/ticker/24hr"
        params = {"symbol": symbol}
        
        data = await self._get(url, params)
        
        if data:
            return {
                "symbol": data["symbol"],
                "price": float(data["lastPrice"]),
                "price_change_24h": float(data["priceChangePercent"]),
                "high_24h": float(data["highPrice"]),
                "low_24h": float(data["lowPrice"]),
                "volume_24h": float(data["volume"]),
                "quote_volume_24h": float(data["quoteVolume"]),
            }
        return None
    
    async def get_funding_rate(self, symbol: str) -> Optional[dict]:
        """Fetch current funding rate from Binance Futures"""
        url = f"{self.futures_url}/fapi/v1/premiumIndex"
        params = {"symbol": symbol}
        
        data = await self._get(url, params)
        
        if data:
            return {
                "symbol": data["symbol"],
                "funding_rate": float(data["lastFundingRate"]),
                "mark_price": float(data["markPrice"]),
                "index_price": float(data["indexPrice"]),
                "next_funding_time": int(data["nextFundingTime"]),
            }
        return None
    
    async def get_open_interest(self, symbol: str) -> Optional[dict]:
        """Fetch open interest from Binance Futures"""
        url = f"{self.futures_url}/fapi/v1/openInterest"
        params = {"symbol": symbol}
        
        data = await self._get(url, params)
        
        if data:
            return {
                "symbol": data["symbol"],
                "open_interest": float(data["openInterest"]),
            }
        return None
    
    async def get_long_short_ratio(self, symbol: str, period: str = "1h") -> Optional[dict]:
        """Fetch long/short account ratio"""
        url = f"{self.futures_url}/futures/data/globalLongShortAccountRatio"
        params = {
            "symbol": symbol,
            "period": period,
            "limit": 1,
        }
        
        data = await self._get(url, params)
        
        if data and len(data) > 0:
            return {
                "symbol": symbol,
                "long_ratio": float(data[0]["longAccount"]),
                "short_ratio": float(data[0]["shortAccount"]),
                "long_short_ratio": float(data[0]["longShortRatio"]),
                "timestamp": int(data[0]["timestamp"]),
            }
        return None
    
    async def get_all_timeframe_data(
        self, 
        symbol: str
    ) -> Optional[dict]:
        """
        Fetch OHLCV data for all configured timeframes
        Returns dict with timeframe keys
        """
        results = {}
        
        for tf_name, tf_config in TIMEFRAMES.items():
            klines = await self.get_klines(
                symbol=symbol,
                interval=tf_config["binance"],
                limit=tf_config["periods_needed"],
            )
            
            if klines:
                results[tf_name] = klines
            else:
                logger.warning(f"Failed to fetch {tf_name} data for {symbol}")
                
        return results if results else None
    
    async def get_complete_asset_data(self, binance_symbol: str) -> Optional[dict]:
        """
        Fetch all data needed for an asset:
        - OHLCV across all timeframes
        - 24h ticker
        - Funding rate (if futures available)
        - Open interest
        - Long/short ratio
        """
        # Fetch all data concurrently
        klines_task = self.get_all_timeframe_data(binance_symbol)
        ticker_task = self.get_ticker_24h(binance_symbol)
        
        # Futures data - use try/except as not all symbols have futures
        funding_task = self.get_funding_rate(binance_symbol)
        oi_task = self.get_open_interest(binance_symbol)
        ls_ratio_task = self.get_long_short_ratio(binance_symbol)
        
        results = await asyncio.gather(
            klines_task,
            ticker_task,
            funding_task,
            oi_task,
            ls_ratio_task,
            return_exceptions=True,
        )
        
        klines_data, ticker_data, funding_data, oi_data, ls_ratio_data = results
        
        # Handle exceptions
        if isinstance(klines_data, Exception):
            logger.error(f"Klines error for {binance_symbol}: {klines_data}")
            klines_data = None
        if isinstance(ticker_data, Exception):
            ticker_data = None
        if isinstance(funding_data, Exception):
            funding_data = None
        if isinstance(oi_data, Exception):
            oi_data = None
        if isinstance(ls_ratio_data, Exception):
            ls_ratio_data = None
            
        if not klines_data or not ticker_data:
            return None
            
        return {
            "klines": klines_data,
            "ticker": ticker_data,
            "funding": funding_data,
            "open_interest": oi_data,
            "long_short_ratio": ls_ratio_data,
            "fetched_at": datetime.utcnow().isoformat(),
        }


async def test_client():
    """Test the Binance client"""
    async with BinanceClient() as client:
        # Test with BTC
        print("Testing BTC data fetch...")
        
        # Test klines
        klines = await client.get_klines("BTCUSDT", "1h", 10)
        if klines:
            print(f"✓ Klines: Got {len(klines)} candles")
            print(f"  Latest close: ${klines[-1]['close']:,.2f}")
        
        # Test ticker
        ticker = await client.get_ticker_24h("BTCUSDT")
        if ticker:
            print(f"✓ Ticker: ${ticker['price']:,.2f} ({ticker['price_change_24h']:+.2f}%)")
        
        # Test funding
        funding = await client.get_funding_rate("BTCUSDT")
        if funding:
            print(f"✓ Funding rate: {funding['funding_rate']*100:.4f}%")
        
        # Test complete data
        print("\nTesting complete data fetch...")
        complete = await client.get_complete_asset_data("BTCUSDT")
        if complete:
            print(f"✓ Complete data fetched successfully")
            print(f"  Timeframes: {list(complete['klines'].keys())}")


if __name__ == "__main__":
    asyncio.run(test_client())
