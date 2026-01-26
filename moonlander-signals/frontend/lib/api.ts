// API client for fetching signals data

import { SignalsResponse, CategoriesResponse, Asset } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

export async function fetchSignals(): Promise<SignalsResponse> {
  // Try to fetch from API first if we have a URL and not in demo mode
  if (API_BASE_URL && !DEMO_MODE) {
    try {
      console.log('Fetching from API:', `${API_BASE_URL}/signals`);
      const res = await fetch(`${API_BASE_URL}/signals`, {
        cache: 'no-store', // Always fetch fresh data
        headers: {
          'Accept': 'application/json',
        },
      });

      if (res.ok) {
        const data = await res.json();
        console.log('API response:', data);
        
        // Check if we got actual data
        if (data.assets && data.assets.length > 0) {
          // Transform API response to match expected format
          return {
            generated_at: data.generated_at,
            total_assets: data.total_results || data.assets.length,
            summary: data.summary || {
              bullish: data.assets.filter((a: Asset) => a.score > 0).length,
              bearish: data.assets.filter((a: Asset) => a.score < 0).length,
              neutral: data.assets.filter((a: Asset) => a.score === 0).length,
              strong_signals: data.assets.filter((a: Asset) => Math.abs(a.score) >= 2).length,
              by_score: {
                '-3': data.assets.filter((a: Asset) => a.score === -3).length,
                '-2': data.assets.filter((a: Asset) => a.score === -2).length,
                '-1': data.assets.filter((a: Asset) => a.score === -1).length,
                '0': data.assets.filter((a: Asset) => a.score === 0).length,
                '1': data.assets.filter((a: Asset) => a.score === 1).length,
                '2': data.assets.filter((a: Asset) => a.score === 2).length,
                '3': data.assets.filter((a: Asset) => a.score === 3).length,
              },
            },
            assets: data.assets,
          };
        }
        console.log('API returned empty data, falling back to demo');
      } else {
        console.error('API error:', res.status, res.statusText);
      }
    } catch (error) {
      console.error('Failed to fetch from API:', error);
    }
  } else {
    console.log('Using demo mode. API_URL:', API_BASE_URL, 'DEMO_MODE:', DEMO_MODE);
  }

  // Fall back to demo data
  return generateDemoData();
}

export async function fetchSignalBySymbol(symbol: string) {
  if (API_BASE_URL && !DEMO_MODE) {
    try {
      const res = await fetch(`${API_BASE_URL}/signals/${symbol}`);
      if (res.ok) {
        return res.json();
      }
    } catch (error) {
      console.error('Failed to fetch signal:', error);
    }
  }

  const data = generateDemoData();
  const asset = data.assets.find(a => a.symbol === symbol.toUpperCase());
  if (!asset) throw new Error('Asset not found');
  return { generated_at: data.generated_at, asset };
}

export async function fetchCategories(): Promise<CategoriesResponse> {
  if (API_BASE_URL && !DEMO_MODE) {
    try {
      const res = await fetch(`${API_BASE_URL}/categories`);
      if (res.ok) {
        return res.json();
      }
    } catch (error) {
      console.error('Failed to fetch categories:', error);
    }
  }

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

// Demo data generator for when API is not available
function generateDemoData(): SignalsResponse {
  const assetConfigs = [
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

  const generatedAssets: Asset[] = assetConfigs.map(assetConfig => {
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
      [-3]: 'STRONG SHORT',
      [-2]: 'SHORT',
      [-1]: 'LEAN SHORT',
      [0]: 'NEUTRAL',
      [1]: 'LEAN LONG',
      [2]: 'LONG',
      [3]: 'STRONG LONG',
    };

    const change24h = (Math.random() * 20 - 10);
    const price = assetConfig.basePrice * (1 + change24h / 100);

    // Generate RSI values that somewhat correlate with score
    const rsiBase = 50 - score * 10;
    const rsi = {
      '15m': Math.round(Math.max(10, Math.min(90, rsiBase + (Math.random() * 30 - 15)))),
      '1h': Math.round(Math.max(10, Math.min(90, rsiBase + (Math.random() * 25 - 12)))),
      '4h': Math.round(Math.max(10, Math.min(90, rsiBase + (Math.random() * 20 - 10)))),
      '1d': Math.round(Math.max(10, Math.min(90, rsiBase + (Math.random() * 15 - 7)))),
    };

    // Determine liq_zone based on score
    let liqZone: 'above' | 'below' | 'neutral';
    if (score > 0) {
      liqZone = 'above';
    } else if (score < 0) {
      liqZone = 'below';
    } else {
      liqZone = 'neutral';
    }

    return {
      symbol: assetConfig.symbol,
      name: assetConfig.name,
      category: assetConfig.category,
      binance_symbol: `${assetConfig.symbol}USDT`,
      price,
      change_24h: parseFloat(change24h.toFixed(2)),
      volume_24h: Math.random() * 1000000000,
      score,
      label: labels[score],
      composite_score: score * 0.2 + (Math.random() * 0.2 - 0.1),
      confidence: 0.5 + Math.random() * 0.5,
      rsi,
      rsi_aligned: Math.floor(Math.random() * 5),
      ema_aligned: Math.floor(Math.random() * 5),
      macd_aligned: Math.floor(Math.random() * 5),
      funding_rate: (Math.random() * 0.002 - 0.001),
      long_short_ratio: 0.5 + Math.random(),
      liq_zone: liqZone,
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
