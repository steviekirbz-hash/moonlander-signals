// Types for Moonlander Signals

export interface RSIValues {
  '15m': number;
  '1h': number;
  '4h': number;
  '1d': number;
}

export interface Asset {
  symbol: string;
  name: string;
  category: string;
  binance_symbol: string;
  price: number;
  change_24h: number;
  volume_24h: number;
  score: number;
  label: string;
  composite_score: number;
  confidence: number;
  rsi: RSIValues;
  rsi_aligned: number;
  ema_aligned: number;
  macd_aligned: number;
  funding_rate: number | null;
  long_short_ratio: number | null;
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
  summary: Summary;
  assets: Asset[];
}

export interface FilteredSignalsResponse {
  generated_at: string;
  total_results: number;
  filters_applied: {
    category: string | null;
    min_score: number | null;
    max_score: number | null;
  };
  assets: Asset[];
}

export interface CategoryStats {
  count: number;
  bullish: number;
  bearish: number;
  neutral: number;
}

export interface CategoriesResponse {
  categories: Record<string, CategoryStats>;
}

export type ScoreValue = -3 | -2 | -1 | 0 | 1 | 2 | 3;

export type FilterType = 'all' | 'strong' | 'long' | 'short' | 'neutral';

export type SortField = 'score' | 'symbol' | 'price' | 'change_24h';

export type SortDirection = 'asc' | 'desc';
