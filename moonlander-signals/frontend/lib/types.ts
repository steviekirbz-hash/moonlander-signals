// Type definitions for Moonlander Signals

export interface FearGreedData {
  value: number;
  classification: string;
  change_24h: number;
  change_direction: 'up' | 'down' | 'unchanged';
  timestamp?: string;
  previous_value?: number;
  previous_classification?: string;
}

export interface ADXData {
  value: number;
  trend_strength: 'weak' | 'moderate' | 'strong' | 'very strong' | 'none';
  direction: 'bullish' | 'bearish' | 'neutral';
  trending: boolean;
}

export interface DemarkData {
  count: number;
  type: 'S' | 'B' | null;
  signal: 'bullish' | 'bearish' | null;
  display: string;
  completed: boolean;
}

export interface VolumeData {
  ratio: number;
  display: string;
  signal: 'high' | 'normal' | 'low';
  current?: number;
  average?: number;
}

export interface Asset {
  symbol: string;
  name: string;
  category: string;
  binance_symbol?: string;
  price: number;
  change_24h: number;
  volume_24h: number;
  score: number;
  label: string;
  composite_score: number;
  confidence: number;
  rsi: {
    '15m': number;
    '1h': number;
    '4h': number;
    '1d': number;
  };
  adx?: ADXData;
  demark?: DemarkData;
  relative_volume?: VolumeData;
  rsi_aligned: number;
  ema_aligned: number;
  macd_aligned: number;
  liq_zone: 'above' | 'below' | 'neutral';
  updated_at: string;
}

export interface Summary {
  bullish: number;
  bearish: number;
  neutral: number;
  strong_signals: number;
  by_score: {
    '-3': number;
    '-2': number;
    '-1': number;
    '0': number;
    '1': number;
    '2': number;
    '3': number;
  };
}

export interface SignalsResponse {
  generated_at: string;
  total_assets: number;
  fear_greed?: FearGreedData | null;
  summary: Summary;
  assets: Asset[];
}

export interface CategoriesResponse {
  categories: {
    [key: string]: {
      count: number;
      bullish: number;
      bearish: number;
      neutral: number;
    };
  };
}
