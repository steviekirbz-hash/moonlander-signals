// API client for fetching signals data

import { SignalsResponse, Asset, FearGreedData } from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || '';
const DEMO_MODE = process.env.NEXT_PUBLIC_DEMO_MODE === 'true';

export async function fetchSignals(): Promise<SignalsResponse> {
  if (API_BASE_URL && !DEMO_MODE) {
    try {
      console.log('Fetching from API:', `${API_BASE_URL}/signals`);
      const res = await fetch(`${API_BASE_URL}/signals`, {
        cache: 'no-store',
        headers: { 'Accept': 'application/json' },
      });

      if (res.ok) {
        const data = await res.json();
        console.log('API response:', data);
        
        if (data.assets && data.assets.length > 0) {
          return {
            generated_at: data.generated_at,
            total_assets: data.total_results || data.assets.length,
            fear_greed: data.fear_greed || null,
            summary: data.summary || calculateSummary(data.assets),
            assets: data.assets,
          };
        }
        console.log('API returned empty data, falling back to demo');
      }
    } catch (error) {
      console.error('Failed to fetch from API:', error);
    }
  }
  return generateDemoData();
}

// Legacy export for backward compatibility
export function formatFunding(value: number | undefined | null): string {
  if (value === undefined || value === null) return 'N/A';
  const percentage = value * 100;
  const sign = percentage >= 0 ? '+' : '';
  return `${sign}${percentage.toFixed(3)}%`;
}

// Legacy export for backward compatibility
export function formatPrice(price: number): string {
  if (price >= 1000) {
    return price.toLocaleString(undefined, { maximumFractionDigits: 0 });
  } else if (price >= 1) {
    return price.toLocaleString(undefined, { maximumFractionDigits: 2 });
  } else {
    return price.toLocaleString(undefined, { maximumFractionDigits: 6 });
  }
}

// Legacy export for backward compatibility
export function formatVolume(volume: number): string {
  if (volume >= 1e9) {
    return `$${(volume / 1e9).toFixed(2)}B`;
  } else if (volume >= 1e6) {
    return `$${(volume / 1e6).toFixed(2)}M`;
  } else if (volume >= 1e3) {
    return `$${(volume / 1e3).toFixed(2)}K`;
  }
  return `$${volume.toFixed(2)}`;
}

// Legacy export for backward compatibility
export function formatChange(change: number): string {
  const sign = change >= 0 ? '+' : '';
  return `${sign}${change.toFixed(2)}%`;
}

function calculateSummary(assets: Asset[]) {
  return {
    bullish: assets.filter(a => a.score > 0).length,
    bearish: assets.filter(a => a.score < 0).length,
    neutral: assets.filter(a => a.score === 0).length,
    strong_signals: assets.filter(a => Math.abs(a.score) >= 2).length,
    by_score: {
      '-3': assets.filter(a => a.score === -3).length,
      '-2': assets.filter(a => a.score === -2).length,
      '-1': assets.filter(a => a.score === -1).length,
      '0': assets.filter(a => a.score === 0).length,
      '1': assets.filter(a => a.score === 1).length,
      '2': assets.filter(a => a.score === 2).length,
      '3': assets.filter(a => a.score === 3).length,
    },
  };
}

function generateDemoData(): SignalsResponse {
  const assetConfigs = [
    { symbol: 'BTC', name: 'Bitcoin', category: 'Major', basePrice: 98500 },
    { symbol: 'ETH', name: 'Ethereum', category: 'Major', basePrice: 3250 },
    { symbol: 'SOL', name: 'Solana', category: 'Major', basePrice: 185 },
    { symbol: 'XRP', name: 'Ripple', category: 'Major', basePrice: 2.85 },
    { symbol: 'ADA', name: 'Cardano', category: 'Major', basePrice: 0.95 },
    { symbol: 'DOT', name: 'Polkadot', category: 'Major', basePrice: 7.2 },
    { symbol: 'LINK', name: 'Chainlink', category: 'Major', basePrice: 22 },
    { symbol: 'AVAX', name: 'Avalanche', category: 'Major', basePrice: 38 },
    { symbol: 'SUI', name: 'Sui', category: 'Layer 1', basePrice: 4.2 },
    { symbol: 'SEI', name: 'Sei', category: 'Layer 1', basePrice: 0.52 },
    { symbol: 'APT', name: 'Aptos', category: 'Layer 1', basePrice: 9.8 },
    { symbol: 'OP', name: 'Optimism', category: 'Layer 2', basePrice: 2.1 },
    { symbol: 'ARB', name: 'Arbitrum', category: 'Layer 2', basePrice: 0.95 },
    { symbol: 'AAVE', name: 'Aave', category: 'DeFi', basePrice: 285 },
    { symbol: 'UNI', name: 'Uniswap', category: 'DeFi', basePrice: 12.5 },
    { symbol: 'FET', name: 'Fetch.ai', category: 'AI', basePrice: 1.65 },
    { symbol: 'RENDER', name: 'Render', category: 'AI', basePrice: 7.8 },
    { symbol: 'TAO', name: 'Bittensor', category: 'AI', basePrice: 485 },
    { symbol: 'DOGE', name: 'Dogecoin', category: 'Memecoin', basePrice: 0.35 },
    { symbol: 'PEPE', name: 'Pepe', category: 'Memecoin', basePrice: 0.000018 },
    { symbol: 'SHIB', name: 'Shiba Inu', category: 'Memecoin', basePrice: 0.000022 },
    { symbol: 'WIF', name: 'Dogwifhat', category: 'Memecoin', basePrice: 2.1 },
    { symbol: 'BONK', name: 'Bonk', category: 'Memecoin', basePrice: 0.000032 },
  ];

  const generatedAssets: Asset[] = assetConfigs.map(config => {
    const rand = Math.random();
    let score: number;
    if (rand < 0.06) score = -3;
    else if (rand < 0.14) score = -2;
    else if (rand < 0.28) score = -1;
    else if (rand < 0.72) score = 0;
    else if (rand < 0.86) score = 1;
    else if (rand < 0.94) score = 2;
    else score = 3;

    const labels: { [key: number]: string } = {
      '-3': 'STRONG SHORT', '-2': 'SHORT', '-1': 'LEAN SHORT',
      '0': 'NEUTRAL', '1': 'LEAN LONG', '2': 'LONG', '3': 'STRONG LONG'
    };

    const rsiBase = 50 + (Math.random() - 0.5) * 60;
    const adxValue = 15 + Math.random() * 50;
    const demarkCount = Math.floor(Math.random() * 10);
    const demarkType = Math.random() > 0.5 ? 'S' : 'B';
    const volumeRatio = 0.5 + Math.random() * 2;

    return {
      symbol: config.symbol,
      name: config.name,
      category: config.category,
      price: config.basePrice * (0.95 + Math.random() * 0.1),
      change_24h: (Math.random() - 0.5) * 20,
      volume_24h: Math.random() * 1000000000,
      score,
      label: labels[score],
      composite_score: score * 0.2 + (Math.random() - 0.5) * 0.3,
      confidence: 0.5 + Math.random() * 0.4,
      rsi: {
        '15m': Math.max(10, Math.min(90, rsiBase + (Math.random() - 0.5) * 20)),
        '1h': Math.max(10, Math.min(90, rsiBase + (Math.random() - 0.5) * 15)),
        '4h': Math.max(10, Math.min(90, rsiBase + (Math.random() - 0.5) * 10)),
        '1d': Math.max(10, Math.min(90, rsiBase)),
      },
      adx: {
        value: adxValue,
        trend_strength: adxValue < 20 ? 'weak' : adxValue < 40 ? 'moderate' : adxValue < 60 ? 'strong' : 'very strong',
        direction: score > 0 ? 'bullish' : score < 0 ? 'bearish' : 'neutral',
        trending: adxValue > 25,
      },
      demark: {
        count: demarkCount,
        type: demarkCount > 0 ? demarkType : null,
        signal: demarkCount >= 7 ? (demarkType === 'S' ? 'bullish' : 'bearish') : null,
        display: demarkCount > 0 ? `${demarkType}:${demarkCount}${demarkCount >= 9 ? '!' : ''}` : '—',
        completed: demarkCount >= 9,
      },
      relative_volume: {
        ratio: volumeRatio,
        display: `${volumeRatio.toFixed(1)}x`,
        signal: volumeRatio > 1.5 ? 'high' : volumeRatio < 0.5 ? 'low' : 'normal',
      },
      rsi_aligned: Math.floor(Math.random() * 5),
      ema_aligned: Math.floor(Math.random() * 5),
      macd_aligned: Math.floor(Math.random() * 5),
      liq_zone: score > 0 ? 'above' : score < 0 ? 'below' : 'neutral',
      updated_at: new Date().toISOString(),
    };
  });

  generatedAssets.sort((a, b) => b.score - a.score);

  const fgValue = 20 + Math.floor(Math.random() * 60);

  return {
    generated_at: new Date().toISOString(),
    total_assets: generatedAssets.length,
    fear_greed: {
      value: fgValue,
      classification: fgValue <= 20 ? 'Extreme Fear' : fgValue <= 40 ? 'Fear' : fgValue <= 60 ? 'Neutral' : fgValue <= 80 ? 'Greed' : 'Extreme Greed',
      change_24h: Math.floor(Math.random() * 10) - 5,
      change_direction: Math.random() > 0.5 ? 'up' : 'down',
    },
    summary: calculateSummary(generatedAssets),
    assets: generatedAssets,
  };
}
