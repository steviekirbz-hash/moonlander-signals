// Type definitions for Moonlander Signals V2

export interface FearGreedData {
  value: number;
  classification: string;
  change_24h: number;
  change_direction?: 'up' | 'down' | 'unchanged';
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
}

export interface RSIData {
  '15m': number;
  '1h': number;
  '4h': number;
  '1d': number;
}

export interface Asset {
  symbol: string;
  name: string;
  category: string;
  price: number;
  change_24h: number;
  volume_24h?: number;
  score: number;
  label: string;
  rsi: RSIData;
  adx?: ADXData;
  demark?: DemarkData;
  relative_volume?: VolumeData;
  ema_aligned: number;
  macd_aligned: number;
  updated_at?: string;
}

export interface Summary {
  bullish: number;
  bearish: number;
  neutral: number;
  strong_signals: number;
}

export interface SignalsResponse {
  generated_at: string;
  total_assets: number;
  fear_greed?: FearGreedData | null;
  summary: Summary;
  assets: Asset[];
}
