"""
FastAPI Server for Moonlander Signals
Uses CoinGecko for market data
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from signal_generator import signal_generator
from coingecko_client import coingecko_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Cache settings
CACHE_DURATION = timedelta(minutes=30)  # Refresh every 30 minutes
last_refresh: Optional[datetime] = None
is_refreshing = False


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Moonlander Signals API...")
    
    # Load cached data on startup
    cached = signal_generator.load_signals()
    if cached:
        signal_generator.signals_cache = cached
        logger.info(f"Loaded {cached.get('total_assets', 0)} cached signals")
    
    # Generate fresh signals on startup (in background)
    asyncio.create_task(refresh_signals_background())
    
    yield
    
    # Cleanup
    await coingecko_client.close()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Moonlander Signals API",
    description="Multi-timeframe crypto trading signals powered by CoinGecko",
    version="2.0.0",
    lifespan=lifespan,
)

# CORS - allow all origins for the frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


async def refresh_signals_background():
    """Background task to refresh signals"""
    global last_refresh, is_refreshing
    
    if is_refreshing:
        return
    
    is_refreshing = True
    try:
        logger.info("Refreshing signals in background...")
        await signal_generator.generate_all_signals()
        last_refresh = datetime.utcnow()
        logger.info("Background refresh complete")
    except Exception as e:
        logger.error(f"Background refresh failed: {e}")
    finally:
        is_refreshing = False


@app.get("/")
async def root():
    """API information"""
    return {
        "name": "Moonlander Signals API",
        "version": "2.0.0",
        "status": "running",
        "data_source": "CoinGecko",
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
    cached = signal_generator.get_cached_signals()
    return {
        "status": "healthy",
        "cached_assets": cached.get("total_assets", 0),
        "last_update": cached.get("generated_at"),
        "is_refreshing": is_refreshing,
    }


@app.get("/signals")
async def get_signals(
    category: Optional[str] = Query(None, description="Filter by category"),
    min_score: Optional[int] = Query(None, ge=-3, le=3, description="Minimum score"),
    max_score: Optional[int] = Query(None, ge=-3, le=3, description="Maximum score"),
    sort_by: Optional[str] = Query("score", description="Sort field"),
    sort_dir: Optional[str] = Query("desc", description="Sort direction"),
    limit: Optional[int] = Query(None, ge=1, le=100, description="Limit results"),
):
    """Get all signals with optional filters"""
    
    # Check if we need to refresh
    global last_refresh
    if last_refresh is None or datetime.utcnow() - last_refresh > CACHE_DURATION:
        if not is_refreshing:
            asyncio.create_task(refresh_signals_background())
    
    data = signal_generator.get_cached_signals()
    assets = data.get("assets", [])
    
    # Apply filters
    if category:
        assets = [a for a in assets if a.get("category", "").lower() == category.lower()]
    
    if min_score is not None:
        assets = [a for a in assets if a.get("score", 0) >= min_score]
    
    if max_score is not None:
        assets = [a for a in assets if a.get("score", 0) <= max_score]
    
    # Sort
    reverse = sort_dir.lower() == "desc"
    if sort_by == "score":
        assets.sort(key=lambda x: (x.get("score", 0), x.get("composite_score", 0)), reverse=reverse)
    elif sort_by == "symbol":
        assets.sort(key=lambda x: x.get("symbol", ""), reverse=reverse)
    elif sort_by == "price":
        assets.sort(key=lambda x: x.get("price", 0), reverse=reverse)
    elif sort_by == "change_24h":
        assets.sort(key=lambda x: x.get("change_24h", 0), reverse=reverse)
    
    # Limit
    if limit:
        assets = assets[:limit]
    
    return {
        "generated_at": data.get("generated_at"),
        "total_results": len(assets),
        "filters_applied": {
            "category": category,
            "min_score": min_score,
            "max_score": max_score,
        },
        "summary": data.get("summary", {}),
        "assets": assets,
    }


@app.get("/signals/{symbol}")
async def get_signal_by_symbol(symbol: str):
    """Get signal for a specific asset"""
    data = signal_generator.get_cached_signals()
    assets = data.get("assets", [])
    
    symbol_upper = symbol.upper()
    for asset in assets:
        if asset.get("symbol") == symbol_upper:
            return {
                "generated_at": data.get("generated_at"),
                "asset": asset,
            }
    
    raise HTTPException(status_code=404, detail=f"Asset {symbol} not found")


@app.get("/summary")
async def get_summary():
    """Get market summary"""
    data = signal_generator.get_cached_signals()
    return {
        "generated_at": data.get("generated_at"),
        "total_assets": data.get("total_assets", 0),
        "summary": data.get("summary", {}),
    }


@app.get("/categories")
async def get_categories():
    """Get breakdown by category"""
    data = signal_generator.get_cached_signals()
    assets = data.get("assets", [])
    
    categories = {}
    for asset in assets:
        cat = asset.get("category", "Other")
        if cat not in categories:
            categories[cat] = {"count": 0, "bullish": 0, "bearish": 0, "neutral": 0}
        
        categories[cat]["count"] += 1
        score = asset.get("score", 0)
        if score > 0:
            categories[cat]["bullish"] += 1
        elif score < 0:
            categories[cat]["bearish"] += 1
        else:
            categories[cat]["neutral"] += 1
    
    return {"categories": categories}


@app.post("/refresh")
async def force_refresh():
    """Force refresh signals"""
    global is_refreshing
    
    if is_refreshing:
        return {
            "status": "already_refreshing",
            "message": "A refresh is already in progress",
        }
    
    # Start refresh in background
    asyncio.create_task(refresh_signals_background())
    
    return {
        "status": "started",
        "message": "Signal refresh started in background",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
