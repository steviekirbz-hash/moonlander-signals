"""
Signal Generator
Main orchestrator that fetches data, calculates indicators, and generates signals
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
import logging

from config import MOONLANDER_ASSETS, DATA_OUTPUT_PATH
from binance_client import BinanceClient
from indicators import calculate_multi_timeframe_indicators
from scoring import calculate_final_score, SignalScore

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SignalGenerator:
    """Main class to generate trading signals for all assets"""
    
    def __init__(self):
        self.assets = MOONLANDER_ASSETS
        self.results = {}
        
    def get_tradeable_assets(self) -> List[Dict]:
        """Get only assets that have Binance data available"""
        return [a for a in self.assets if a.get("binance")]
    
    async def process_single_asset(
        self,
        client: BinanceClient,
        asset: Dict
    ) -> Optional[Dict]:
        """
        Process a single asset:
        1. Fetch all data from Binance
        2. Calculate indicators
        3. Generate score
        """
        symbol = asset["symbol"]
        binance_symbol = asset.get("binance")
        
        if not binance_symbol:
            logger.debug(f"Skipping {symbol} - no Binance symbol")
            return None
        
        try:
            # Fetch complete data
            data = await client.get_complete_asset_data(binance_symbol)
            
            if not data or not data.get("klines"):
                logger.warning(f"No data for {symbol}")
                return None
            
            # Calculate indicators across all timeframes
            indicators = calculate_multi_timeframe_indicators(data["klines"])
            
            if not indicators:
                logger.warning(f"Could not calculate indicators for {symbol}")
                return None
            
            # Calculate final score
            score_result = calculate_final_score(
                indicator_results=indicators,
                funding_data=data.get("funding"),
                oi_data=data.get("open_interest"),
                ls_ratio_data=data.get("long_short_ratio"),
            )
            
            # Get current price and 24h change
            ticker = data.get("ticker", {})
            
            # Extract RSI values for display
            rsi_values = {}
            for tf, ind in indicators.items():
                if ind and ind.get("rsi"):
                    rsi_values[tf] = ind["rsi"].get("value", 50)
            
            # Extract EMA alignment count
            ema_aligned = sum(
                1 for tf, ind in indicators.items()
                if ind and ind.get("ema") and ind["ema"].get("signal") == "bullish"
            ) if score_result.score > 0 else sum(
                1 for tf, ind in indicators.items()
                if ind and ind.get("ema") and ind["ema"].get("signal") == "bearish"
            )
            
            # Extract MACD alignment count
            macd_aligned = sum(
                1 for tf, ind in indicators.items()
                if ind and ind.get("macd") and ind["macd"].get("signal") == "bullish"
            ) if score_result.score > 0 else sum(
                1 for tf, ind in indicators.items()
                if ind and ind.get("macd") and ind["macd"].get("signal") == "bearish"
            )
            
            return {
                "symbol": symbol,
                "name": asset["name"],
                "category": asset["category"],
                "binance_symbol": binance_symbol,
                "price": ticker.get("price", 0),
                "change_24h": ticker.get("price_change_24h", 0),
                "volume_24h": ticker.get("quote_volume_24h", 0),
                "score": score_result.score,
                "label": score_result.label,
                "composite_score": score_result.composite_score,
                "confidence": score_result.confidence,
                "rsi": rsi_values,
                "rsi_aligned": score_result.breakdown["rsi"]["fire_count"],
                "ema_aligned": ema_aligned,
                "macd_aligned": macd_aligned,
                "funding_rate": data.get("funding", {}).get("funding_rate") if data.get("funding") else None,
                "long_short_ratio": data.get("long_short_ratio", {}).get("long_short_ratio") if data.get("long_short_ratio") else None,
                "liq_zone": "above" if score_result.score > 0 else "below" if score_result.score < 0 else "neutral",
                "updated_at": datetime.utcnow().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Error processing {symbol}: {e}")
            return None
    
    async def process_batch(
        self,
        client: BinanceClient,
        assets: List[Dict],
        batch_size: int = 5
    ) -> List[Dict]:
        """Process assets in batches to manage API rate limits"""
        results = []
        
        for i in range(0, len(assets), batch_size):
            batch = assets[i:i + batch_size]
            
            tasks = [
                self.process_single_asset(client, asset)
                for asset in batch
            ]
            
            batch_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in batch_results:
                if isinstance(result, Exception):
                    logger.error(f"Batch error: {result}")
                elif result:
                    results.append(result)
            
            # Small delay between batches
            if i + batch_size < len(assets):
                await asyncio.sleep(1)
        
        return results
    
    async def generate_all_signals(self) -> Dict:
        """
        Generate signals for all tradeable assets
        Returns complete signal data for the frontend
        """
        tradeable = self.get_tradeable_assets()
        logger.info(f"Processing {len(tradeable)} tradeable assets...")
        
        async with BinanceClient() as client:
            results = await self.process_batch(client, tradeable)
        
        # Sort by score (descending)
        results.sort(key=lambda x: (x["score"], x["composite_score"]), reverse=True)
        
        # Calculate summary stats
        bullish = len([r for r in results if r["score"] > 0])
        bearish = len([r for r in results if r["score"] < 0])
        neutral = len([r for r in results if r["score"] == 0])
        strong_signals = len([r for r in results if abs(r["score"]) >= 2])
        
        output = {
            "generated_at": datetime.utcnow().isoformat(),
            "total_assets": len(results),
            "summary": {
                "bullish": bullish,
                "bearish": bearish,
                "neutral": neutral,
                "strong_signals": strong_signals,
                "by_score": {
                    "-3": len([r for r in results if r["score"] == -3]),
                    "-2": len([r for r in results if r["score"] == -2]),
                    "-1": len([r for r in results if r["score"] == -1]),
                    "0": len([r for r in results if r["score"] == 0]),
                    "1": len([r for r in results if r["score"] == 1]),
                    "2": len([r for r in results if r["score"] == 2]),
                    "3": len([r for r in results if r["score"] == 3]),
                },
            },
            "assets": results,
        }
        
        logger.info(f"Generated signals: {bullish} bullish, {bearish} bearish, {neutral} neutral")
        
        return output
    
    def save_signals(self, data: Dict, output_path: str = None):
        """Save signals to JSON file"""
        if output_path is None:
            output_path = DATA_OUTPUT_PATH
        
        # Ensure directory exists
        os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(data, f, indent=2)
        
        logger.info(f"Saved signals to {output_path}")


async def main():
    """Main entry point"""
    generator = SignalGenerator()
    
    print("=" * 60)
    print("MOONLANDER SIGNALS - Signal Generator")
    print("=" * 60)
    print()
    
    # Generate signals
    signals = await generator.generate_all_signals()
    
    # Save to file
    generator.save_signals(signals, "data/signals.json")
    
    # Print summary
    print()
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total assets processed: {signals['total_assets']}")
    print(f"Bullish signals: {signals['summary']['bullish']}")
    print(f"Bearish signals: {signals['summary']['bearish']}")
    print(f"Neutral signals: {signals['summary']['neutral']}")
    print(f"Strong signals (±2 or ±3): {signals['summary']['strong_signals']}")
    print()
    
    # Print top signals
    print("TOP BULLISH SIGNALS:")
    print("-" * 40)
    for asset in signals["assets"][:5]:
        if asset["score"] > 0:
            print(f"  {asset['symbol']:8} | {asset['label']:12} | ${asset['price']:,.4f} | RSI: {asset['rsi'].get('4h', 'N/A')}")
    
    print()
    print("TOP BEARISH SIGNALS:")
    print("-" * 40)
    bearish = [a for a in signals["assets"] if a["score"] < 0]
    for asset in bearish[:5]:
        print(f"  {asset['symbol']:8} | {asset['label']:12} | ${asset['price']:,.4f} | RSI: {asset['rsi'].get('4h', 'N/A')}")
    
    print()
    print(f"Signals saved to: data/signals.json")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
