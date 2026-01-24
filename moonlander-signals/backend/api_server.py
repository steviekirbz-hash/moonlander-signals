"""
FastAPI Server
Exposes signals data via REST API
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from signal_generator import SignalGenerator
from config import CACHE_DURATION_SECONDS


# Global cache
_cache = {
    "signals": None,
    "last_update": None,
}


async def refresh_signals():
    """Refresh signals data"""
    generator = SignalGenerator()
    signals = await generator.generate_all_signals()
    _cache["signals"] = signals
    _cache["last_update"] = datetime.utcnow()
    
    # Also save to file
    generator.save_signals(signals, "data/signals.json")
    
    return signals


async def get_cached_signals(force_refresh: bool = False):
    """Get signals from cache, refreshing if needed"""
    if force_refresh or _cache["signals"] is None:
        return await refresh_signals()
    
    # Check if cache is stale
    if _cache["last_update"]:
        age = datetime.utcnow() - _cache["last_update"]
        if age.total_seconds() > CACHE_DURATION_SECONDS:
            return await refresh_signals()
    
    return _cache["signals"]


async def periodic_refresh():
    """Background task to refresh signals periodically"""
    while True:
        try:
            await asyncio.sleep(CACHE_DURATION_SECONDS)
            print(f"[{datetime.utcnow().isoformat()}] Refreshing signals...")
            await refresh_signals()
            print(f"[{datetime.utcnow().isoformat()}] Signals refreshed successfully")
        except Exception as e:
            print(f"[{datetime.utcnow().isoformat()}] Error refreshing signals: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup: Load initial signals
    print("Starting Moonlander Signals API...")
    
    # Try to load from file first
    if os.path.exists("data/signals.json"):
        try:
            with open("data/signals.json", "r") as f:
                _cache["signals"] = json.load(f)
                _cache["last_update"] = datetime.utcnow()
                print("Loaded signals from cache file")
        except Exception as e:
            print(f"Could not load cache file: {e}")
    
    # Start background refresh task
    refresh_task = asyncio.create_task(periodic_refresh())
    
    yield
    
    # Shutdown
    refresh_task.cancel()
    print("Shutting down Moonlander Signals API...")


# Create FastAPI app
app = FastAPI(
    title="Moonlander Signals API",
    description="Crypto trading signals for Moonlander assets",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """API root - basic info"""
    return {
        "name": "Moonlander Signals API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/signals - Get all signals",
            "/signals/{symbol} - Get signal for specific asset",
            "/summary - Get market summary",
            "/refresh - Force refresh signals (POST)",
            "/health - Health check",
        ],
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "cache_loaded": _cache["signals"] is not None,
        "last_update": _cache["last_update"].isoformat() if _cache["last_update"] else None,
    }


@app.get("/signals")
async def get_signals(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[int] = Query(None, ge=-3, le=3, description="Minimum score filter"),
    max_score: Optional[int] = Query(None, ge=-3, le=3, description="Maximum score filter"),
    sort_by: str = Query("score", description="Sort field: score, symbol, price, change_24h"),
    sort_dir: str = Query("desc", description="Sort direction: asc or desc"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit number of results"),
):
    """
    Get all trading signals
    
    Optional filters:
    - category: Filter by asset category (Major, DeFi, Memecoin, etc.)
    - min_score/max_score: Filter by score range (-3 to 3)
    - sort_by: Sort by field
    - sort_dir: Sort direction
    - limit: Limit results
    """
    signals = await get_cached_signals()
    
    if not signals:
        raise HTTPException(status_code=503, detail="Signals not available")
    
    assets = signals["assets"]
    
    # Apply filters
    if category:
        assets = [a for a in assets if a["category"].lower() == category.lower()]
    
    if min_score is not None:
        assets = [a for a in assets if a["score"] >= min_score]
    
    if max_score is not None:
        assets = [a for a in assets if a["score"] <= max_score]
    
    # Sort
    reverse = sort_dir.lower() == "desc"
    if sort_by == "score":
        assets = sorted(assets, key=lambda x: (x["score"], x["composite_score"]), reverse=reverse)
    elif sort_by == "symbol":
        assets = sorted(assets, key=lambda x: x["symbol"], reverse=reverse)
    elif sort_by == "price":
        assets = sorted(assets, key=lambda x: x["price"], reverse=reverse)
    elif sort_by == "change_24h":
        assets = sorted(assets, key=lambda x: x["change_24h"], reverse=reverse)
    
    # Limit
    if limit:
        assets = assets[:limit]
    
    return {
        "generated_at": signals["generated_at"],
        "total_results": len(assets),
        "filters_applied": {
            "category": category,
            "min_score": min_score,
            "max_score": max_score,
        },
        "assets": assets,
    }


@app.get("/signals/{symbol}")
async def get_signal_by_symbol(symbol: str):
    """Get signal for a specific asset by symbol"""
    signals = await get_cached_signals()
    
    if not signals:
        raise HTTPException(status_code=503, detail="Signals not available")
    
    symbol_upper = symbol.upper()
    asset = next(
        (a for a in signals["assets"] if a["symbol"] == symbol_upper),
        None
    )
    
    if not asset:
        raise HTTPException(status_code=404, detail=f"Asset {symbol_upper} not found")
    
    return {
        "generated_at": signals["generated_at"],
        "asset": asset,
    }


@app.get("/summary")
async def get_summary():
    """Get market summary statistics"""
    signals = await get_cached_signals()
    
    if not signals:
        raise HTTPException(status_code=503, detail="Signals not available")
    
    return {
        "generated_at": signals["generated_at"],
        "total_assets": signals["total_assets"],
        "summary": signals["summary"],
        "last_update": _cache["last_update"].isoformat() if _cache["last_update"] else None,
        "cache_age_seconds": (datetime.utcnow() - _cache["last_update"]).total_seconds() if _cache["last_update"] else None,
    }


@app.get("/categories")
async def get_categories():
    """Get list of all categories with counts"""
    signals = await get_cached_signals()
    
    if not signals:
        raise HTTPException(status_code=503, detail="Signals not available")
    
    categories = {}
    for asset in signals["assets"]:
        cat = asset["category"]
        if cat not in categories:
            categories[cat] = {"count": 0, "bullish": 0, "bearish": 0, "neutral": 0}
        categories[cat]["count"] += 1
        if asset["score"] > 0:
            categories[cat]["bullish"] += 1
        elif asset["score"] < 0:
            categories[cat]["bearish"] += 1
        else:
            categories[cat]["neutral"] += 1
    
    return {
        "categories": categories,
    }


@app.post("/refresh")
async def force_refresh():
    """Force refresh signals (use sparingly)"""
    try:
        signals = await refresh_signals()
        return {
            "status": "success",
            "message": "Signals refreshed successfully",
            "generated_at": signals["generated_at"],
            "total_assets": signals["total_assets"],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to refresh: {str(e)}")


# Run with: uvicorn api_server:app --reload --port 8000
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
