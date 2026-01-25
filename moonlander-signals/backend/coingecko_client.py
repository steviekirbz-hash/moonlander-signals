"""
CoinGecko API Client for Moonlander Signals
Free API - no geographic restrictions
"""

import aiohttp
import asyncio
import logging
from typing import Dict, List, Optional, Any
from config import ASSETS, TIMEFRAMES

logger = logging.getLogger(__name__)

class CoinGeckoClient:
    """Async client for CoinGecko API"""
    
    BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Map our symbols to CoinGecko IDs
    SYMBOL_TO_ID = {
        "BTC": "bitcoin",
        "ETH": "ethereum",
        "SOL": "solana",
        "XRP": "ripple",
        "ADA": "cardano",
        "LTC": "litecoin",
        "BCH": "bitcoin-cash",
        "DOT": "polkadot",
        "LINK": "chainlink",
        "AVAX": "avalanche-2",
        "ATOM": "cosmos",
        "NEAR": "near",
        "TON": "the-open-network",
        "XLM": "stellar",
        "XMR": "monero",
        "ZEC": "zcash",
        "SUI": "sui",
        "SEI": "sei-network",
        "APT": "aptos",
        "BERA": "berachain",
        "OP": "optimism",
        "ARB": "arbitrum",
        "POL": "polygon-ecosystem-token",
        "AAVE": "aave",
        "UNI": "uniswap",
        "CRV": "curve-dao-token",
        "PENDLE": "pendle",
        "ENA": "ethena",
        "ONDO": "ondo-finance",
        "RAY": "raydium",
        "HYPE": "hyperliquid",
        "FET": "artificial-superintelligence-alliance",
        "RENDER": "render-token",
        "TAO": "bittensor",
        "VIRTUAL": "virtual-protocol",
        "FIL": "filecoin",
        "AXL": "axelar",
        "DOGE": "dogecoin",
        "SHIB": "shiba-inu",
        "PEPE": "pepe",
        "BONK": "bonk",
        "FLOKI": "floki",
        "WIF": "dogwifcoin",
        "FARTCOIN": "fartcoin",
        "PENGU": "pudgy-penguins",
        "TRUMP": "official-trump",
        "MELANIA": "official-melania-meme",
        "SAND": "the-sandbox",
        "HBAR": "hedera-hashgraph",
        "VET": "vechain",
        "ALGO": "algorand",
        "KAITO": "kaito",
        "WLD": "worldcoin-wld",
        "CRO": "crypto-com-chain",
        "PAXG": "pax-gold",
    }
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self._rate_limit_delay = 1.5  # CoinGecko free tier: ~30 calls/min
        
    async def _get_session(self) -> aiohttp.ClientSession:
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def _request(self, endpoint: str, params: Dict = None) -> Optional[Dict]:
        """Make a request to CoinGecko API"""
        session = await self._get_session()
        url = f"{self.BASE_URL}{endpoint}"
        
        try:
            await asyncio.sleep(self._rate_limit_delay)  # Rate limiting
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                elif response.status == 429:
                    logger.warning("Rate limited by CoinGecko, waiting...")
                    await asyncio.sleep(60)
                    return None
                else:
                    logger.warning(f"CoinGecko API error {response.status} for {endpoint}")
                    return None
        except asyncio.TimeoutError:
            logger.warning(f"Timeout fetching {endpoint}")
            return None
        except Exception as e:
            logger.error(f"Error fetching {endpoint}: {e}")
            return None
    
    async def get_price_data(self, coin_ids: List[str]) -> Optional[Dict]:
        """Get current price data for multiple coins"""
        ids_str = ",".join(coin_ids)
        params = {
            "ids": ids_str,
            "vs_currencies": "usd",
            "include_24hr_change": "true",
            "include_24hr_vol": "true",
            "include_market_cap": "true",
        }
        return await self._request("/simple/price", params)
    
    async def get_market_data(self, coin_ids: List[str]) -> Optional[List[Dict]]:
        """Get detailed market data for coins"""
        ids_str = ",".join(coin_ids)
        params = {
            "ids": ids_str,
            "vs_currency": "usd",
            "order": "market_cap_desc",
            "per_page": 100,
            "page": 1,
            "sparkline": "false",
            "price_change_percentage": "1h,24h,7d",
        }
        return await self._request("/coins/markets", params)
    
    async def get_ohlc(self, coin_id: str, days: int = 14) -> Optional[List]:
        """
        Get OHLC data for a coin
        Days: 1, 7, 14, 30, 90, 180, 365, max
        Returns: [[timestamp, open, high, low, close], ...]
        """
        params = {"vs_currency": "usd", "days": days}
        return await self._request(f"/coins/{coin_id}/ohlc", params)
    
    async def get_market_chart(self, coin_id: str, days: int = 14) -> Optional[Dict]:
        """
        Get market chart data (prices, market_caps, volumes)
        More granular than OHLC for shorter timeframes
        """
        params = {"vs_currency": "usd", "days": days}
        return await self._request(f"/coins/{coin_id}/market_chart", params)
    
    async def get_all_market_data(self) -> Dict[str, Dict]:
        """Fetch market data for all configured assets"""
        results = {}
        
        # Get list of valid CoinGecko IDs
        valid_ids = []
        symbol_to_id_map = {}
        
        for symbol, asset_info in ASSETS.items():
            coin_id = self.SYMBOL_TO_ID.get(symbol)
            if coin_id:
                valid_ids.append(coin_id)
                symbol_to_id_map[coin_id] = symbol
        
        # Fetch market data in batches
        batch_size = 50
        for i in range(0, len(valid_ids), batch_size):
            batch = valid_ids[i:i + batch_size]
            market_data = await self.get_market_data(batch)
            
            if market_data:
                for coin in market_data:
                    coin_id = coin.get("id")
                    symbol = symbol_to_id_map.get(coin_id)
                    if symbol:
                        results[symbol] = {
                            "price": coin.get("current_price", 0),
                            "change_24h": coin.get("price_change_percentage_24h", 0),
                            "change_1h": coin.get("price_change_percentage_1h_in_currency", 0),
                            "change_7d": coin.get("price_change_percentage_7d_in_currency", 0),
                            "volume_24h": coin.get("total_volume", 0),
                            "market_cap": coin.get("market_cap", 0),
                            "high_24h": coin.get("high_24h", 0),
                            "low_24h": coin.get("low_24h", 0),
                            "ath": coin.get("ath", 0),
                            "ath_change_percentage": coin.get("ath_change_percentage", 0),
                        }
            
            await asyncio.sleep(self._rate_limit_delay)
        
        return results
    
    async def get_ohlc_for_asset(self, symbol: str, days: int = 14) -> Optional[List]:
        """Get OHLC data for a specific asset"""
        coin_id = self.SYMBOL_TO_ID.get(symbol)
        if not coin_id:
            logger.warning(f"No CoinGecko ID for {symbol}")
            return None
        
        return await self.get_ohlc(coin_id, days)
    
    async def get_complete_asset_data(self, symbol: str) -> Optional[Dict]:
        """Get all available data for a single asset"""
        coin_id = self.SYMBOL_TO_ID.get(symbol)
        if not coin_id:
            return None
        
        # Get OHLC data (14 days gives us enough for indicators)
        ohlc = await self.get_ohlc(coin_id, days=14)
        
        # Get market chart for more granular data
        chart = await self.get_market_chart(coin_id, days=14)
        
        if not ohlc and not chart:
            return None
        
        return {
            "symbol": symbol,
            "coin_id": coin_id,
            "ohlc": ohlc or [],
            "prices": chart.get("prices", []) if chart else [],
            "volumes": chart.get("total_volumes", []) if chart else [],
        }


# Singleton instance
coingecko_client = CoinGeckoClient()
