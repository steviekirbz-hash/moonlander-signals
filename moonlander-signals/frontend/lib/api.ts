// API client for fetching signals data

import { SignalsResponse, FilteredSignalsResponse, CategoriesResponse } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';

// For static/demo mode when no API is available
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

export async function fetchSignals(): Promise<SignalsResponse> {
  if (DEMO_MODE) {
    return generateDemoData();
  }

  const res = await fetch(`${API_BASE_URL}/signals`, {
    next: { revalidate: 300 }, // Cache for 5 minutes
  });

  if (!res.ok) {
    throw new Error('Failed to fetch signals');
  }

  return res.json();
}

export async function fetchSignalBySymbol(symbol: string) {
  if (DEMO_MODE) {
    const data = generateDemoData();
    const asset = data.assets.find(a => a.symbol === symbol.toUpperCase());
    if (!asset) throw new Error('Asset not found');
    return { generated_at: data.generated_at, asset };
  }

  const res = await fetch(`${API_BASE_URL}/signals/${symbol}`);
  
  if (!res.ok) {
    throw new Error('Failed to fetch signal');
  }

  return res.json();
}

export async function fetchCategories(): Promise<CategoriesResponse> {
  if (DEMO_MODE) {
    const data = generateDemoData();
    const categories: Record<string, { count: number; bullish: number; bearish: number; neutral: number }> = {};
    
    data.assets.forEach(asset => {
      if (!categories[asset.category]) {
        categories[asset.category] = { count: 0, bullish: 0, bearish: 0, neutral: 0 };
      }
      categories[asset.category].count++;
      if (asset.score > 0) categories[asset.category].bullish++;
      else if (asset.score < 0) categories[asset.category].bearish++;
      else categories[asset.category].neutral++;
    });

    return { categories };
  }

  const res = await fetch(`${API_BASE_URL}/categories`);
  
  if (!res.ok) {
    throw new Error('Failed to fetch categories');
  }

  return res.json();
}

// Demo data generator for when API is not available
function generateDemoData(): SignalsResponse {
  const assets = [
    // Majors
    { symbol: 'BTC', name: 'Bitcoin', category: 'Major', basePrice: 98500 },
    { symbol: 'ETH', name: 'Ethereum', category: 'Major', basePrice: 3250 },
    { symbol: 'SOL', name: 'Solana', category: 'Major', basePrice: 185 },
    { symbol: 'XRP', name: 'Ripple', category: 'Major', basePrice: 2.85 },
    { symbol: 'ADA', name: 'Cardano', category: 'Major', basePrice: 0.95 },
    { symbol: 'LTC', name: 'Litecoin', category: 'Major', basePrice: 120 },
    { symbol: 'BCH', name: 'Bitcoin Cash', category: 'Major', basePrice: 480 },
    { symbol: 'DOT', name: 'Polkadot', category: 'Major', basePrice: 7.2 },
    { symbol: 'LINK', name: 'Chainlink', category: 'Major', basePrice: 22 },
    { symbol: 'AVAX', name: 'Avalanche', category: 'Major', basePrice: 38 },
    { symbol: 'ATOM', name: 'Cosmos', category: 'Major', basePrice: 9.5 },
    { symbol: 'NEAR', name: 'Near Protocol', category: 'Major', basePrice: 5.2 },
    { symbol: 'TON', name: 'Toncoin', category: 'Major', basePrice: 5.8 },
    { symbol: 'XLM', name: 'Stellar', category: 'Major', basePrice: 0.42 },
    { symbol: 'XMR', name: 'Monero', category: 'Major', basePrice: 195 },
    
    // Layer 1 & 2
    { symbol: 'SUI', name: 'Sui', category: 'Layer 1', basePrice: 4.2 },
    { symbol: 'SEI', name: 'Sei', category: 'Layer 1', basePrice: 0.52 },
    { symbol: 'APT', name: 'Aptos', category: 'Layer 1', basePrice: 9.8 },
    { symbol: 'OP', name: 'Optimism', category: 'Layer 2', basePrice: 2.1 },
    { symbol: 'ARB', name: 'Arbitrum', category: 'Layer 2', basePrice: 0.95 },
    { symbol: 'POL', name: 'Polygon', category: 'Layer 2', basePrice: 0.48 },
    
    // DeFi
    { symbol: 'AAVE', name: 'Aave', category: 'DeFi', basePrice: 285 },
    { symbol: 'UNI', name: 'Uniswap', category: 'DeFi', basePrice: 12.5 },
    { symbol: 'CRV', name: 'Curve', category: 'DeFi', basePrice: 0.85 },
    { symbol: 'PENDLE', name: 'Pendle', category: 'DeFi', basePrice: 5.2 },
    { symbol: 'ENA', name: 'Ethena', category: 'DeFi', basePrice: 1.15 },
    { symbol: 'ONDO', name: 'Ondo', category: 'DeFi', basePrice: 1.45 },
    { symbol: 'RAY', name: 'Raydium', category: 'DeFi', basePrice: 5.8 },
    { symbol: 'HYPE', name: 'Hyperliquid', category: 'DeFi', basePrice: 22 },
    
    // AI
    { symbol: 'FET', name: 'Fetch.ai', category: 'AI', basePrice: 1.65 },
    { symbol: 'RENDER', name: 'Render', category: 'AI', basePrice: 7.8 },
    { symbol: 'TAO', name: 'Bittensor', category: 'AI', basePrice: 485 },
    { symbol: 'VIRTUAL', name: 'Virtual Protocol', category: 'AI', basePrice: 2.8 },
    
    // Memecoins
    { symbol: 'DOGE', name: 'Dogecoin', category: 'Memecoin', basePrice: 0.35 },
    { symbol: 'SHIB', name: 'Shiba Inu', category: 'Memecoin', basePrice: 0.000022 },
    { symbol: 'PEPE', name: 'Pepe', category: 'Memecoin', basePrice: 0.000018 },
    { symbol: 'BONK', name: 'Bonk', category: 'Memecoin', basePrice: 0.000032 },
    { symbol: 'FLOKI', name: 'Floki', category: 'Memecoin', basePrice: 0.00018 },
    { symbol: 'WIF', name: 'Dogwifhat', category: 'Memecoin', basePrice: 2.1 },
    { symbol: 'FARTCOIN', name: 'Fartcoin', category: 'Memecoin', basePrice: 0.85 },
    { symbol: 'PENGU', name: 'Pudgy Penguins', category: 'Memecoin', basePrice: 0.032 },
    { symbol: 'TRUMP', name: 'Trump', category: 'Memecoin', basePrice: 38 },
    
    // Other
    { symbol: 'HBAR', name: 'Hedera', category: 'Other', basePrice: 0.28 },
    { symbol: 'VET', name: 'VeChain', category: 'Other', basePrice: 0.048 },
    { symbol: 'ALGO', name: 'Algorand', category: 'Other', basePrice: 0.38 },
    { symbol: 'WLD', name: 'Worldcoin', category: 'Other', basePrice: 2.2 },
    { symbol: 'CRO', name: 'Cronos', category: 'Other', basePrice: 0.12 },
    { symbol: 'FIL', name: 'Filecoin', category: 'Infrastructure', basePrice: 5.5 },
    
    // Gaming
    { symbol: 'SAND', name: 'Sandbox', category: 'Gaming', basePrice: 0.58 },
    
    // Commodity
    { symbol: 'PAXG', name: 'PAX Gold', category: 'Commodity', basePrice: 2750 },
  ];

  const generatedAssets = assets.map(asset => {
    // Generate weighted random score (more neutral, fewer extremes)
    const rand = Math.random();
    let score: number;
    if (rand < 0.06) score = -3;
    else if (rand < 0.14) score = -2;
    else if (rand < 0.28) score = -1;
    else if (rand < 0.72) score = 0;
    else if (rand < 0.86) score = 1;
    else if (rand < 0.94) score = 2;
    else score = 3;

    const labels: Record<number, string> = {
      '-3': 'STRONG SHORT',
      '-2': 'SHORT',
      '-1': 'LEAN SHORT',
      '0': 'NEUTRAL',
      '1': 'LEAN LONG',
      '2': 'LONG',
      '3': 'STRONG LONG',
    };

    const change24h = (Math.random() * 20 - 10);
    const price = asset.basePrice * (1 + change24h / 100);

    // Generate RSI values that somewhat correlate with score
    const rsiBase = 50 - score * 10;
    const rsi = {
      '15m': Math.max(10, Math.min(90, rsiBase + (Math.random() * 30 - 15))),
      '1h': Math.max(10, Math.min(90, rsiBase + (Math.random() * 25 - 12))),
      '4h': Math.max(10, Math.min(90, rsiBase + (Math.random() * 20 - 10))),
      '1d': Math.max(10, Math.min(90, rsiBase + (Math.random() * 15 - 7))),
    };

    return {
      symbol: asset.symbol,
      name: asset.name,
      category: asset.category,
      binance_symbol: `${asset.symbol}USDT`,
      price,
      change_24h: parseFloat(change24h.toFixed(2)),
      volume_24h: Math.random() * 1000000000,
      score,
      label: labels[score],
      composite_score: score * 0.2 + (Math.random() * 0.2 - 0.1),
      confidence: 0.5 + Math.random() * 0.5,
      rsi: {
        '15m': Math.round(rsi['15m']),
        '1h': Math.round(rsi['1h']),
        '4h': Math.round(rsi['4h']),
        '1d': Math.round(rsi['1d']),
      },
      rsi_aligned: Math.floor(Math.random() * 5),
      ema_aligned: Math.floor(Math.random() * 5),
      macd_aligned: Math.floor(Math.random() * 5),
      funding_rate: (Math.random() * 0.002 - 0.001),
      long_short_ratio: 0.5 + Math.random(),
      liq_zone: score > 0 ? 'above' : score < 0 ? 'below' : 'neutral' as const,
      updated_at: new Date().toISOString(),
    };
  });

  // Sort by score descending
  generatedAssets.sort((a, b) => b.score - a.score || b.composite_score - a.composite_score);

  const bullish = generatedAssets.filter(a => a.score > 0).length;
  const bearish = generatedAssets.filter(a => a.score < 0).length;
  const neutral = generatedAssets.filter(a => a.score === 0).length;

  return {
    generated_at: new Date().toISOString(),
    total_assets: generatedAssets.length,
    summary: {
      bullish,
      bearish,
      neutral,
      strong_signals: generatedAssets.filter(a => Math.abs(a.score) >= 2).length,
      by_score: {
        '-3': generatedAssets.filter(a => a.score === -3).length,
        '-2': generatedAssets.filter(a => a.score === -2).length,
        '-1': generatedAssets.filter(a => a.score === -1).length,
        '0': generatedAssets.filter(a => a.score === 0).length,
        '1': generatedAssets.filter(a => a.score === 1).length,
        '2': generatedAssets.filter(a => a.score === 2).length,
        '3': generatedAssets.filter(a => a.score === 3).length,
      },
    },
    assets: generatedAssets,
  };
}

// Utility for class names
export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ');
}

// Format price with appropriate decimals
export function formatPrice(price: number): string {
  if (price >= 1000) return price.toLocaleString(undefined, { maximumFractionDigits: 0 });
  if (price >= 1) return price.toLocaleString(undefined, { maximumFractionDigits: 2 });
  if (price >= 0.01) return price.toLocaleString(undefined, { maximumFractionDigits: 4 });
  return price.toLocaleString(undefined, { maximumFractionDigits: 6 });
}

// Format percentage
export function formatPercent(value: number): string {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${value.toFixed(2)}%`;
}

// Format funding rate
export function formatFunding(rate: number | null): string {
  if (rate === null) return 'N/A';
  const percent = rate * 100;
  const sign = percent >= 0 ? '+' : '';
  return `${sign}${percent.toFixed(4)}%`;
}
