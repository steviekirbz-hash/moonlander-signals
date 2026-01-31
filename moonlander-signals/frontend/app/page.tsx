'use client';

import React, { useState, useEffect } from 'react';
import { 
  TrendingUp, TrendingDown, Minus, Flame, ChevronDown, ChevronUp, 
  Activity, BarChart3, Clock, RefreshCw, Search, ArrowUpDown,
  Gauge, AlertTriangle, Volume2
} from 'lucide-react';
import { fetchSignals } from '@/lib/api';
import { Asset, SignalsResponse, FearGreedData } from '@/lib/types';

// Score configuration
const SCORE_CONFIG: Record<string, { label: string; bg: string; glow: string; textColor: string; icon: React.ElementType }> = {
  '-3': { label: 'STRONG SHORT', bg: 'bg-gradient-to-r from-red-700 to-red-600', glow: 'shadow-[0_0_25px_rgba(185,28,28,0.6)]', textColor: 'text-red-100', icon: TrendingDown },
  '-2': { label: 'SHORT', bg: 'bg-gradient-to-r from-red-600 to-red-500', glow: 'shadow-[0_0_15px_rgba(220,38,38,0.4)]', textColor: 'text-red-100', icon: TrendingDown },
  '-1': { label: 'LEAN SHORT', bg: 'bg-gradient-to-r from-red-500/70 to-red-400/70', glow: '', textColor: 'text-red-100', icon: TrendingDown },
  '0': { label: 'NEUTRAL', bg: 'bg-gradient-to-r from-slate-600 to-slate-500', glow: '', textColor: 'text-slate-100', icon: Minus },
  '1': { label: 'LEAN LONG', bg: 'bg-gradient-to-r from-emerald-500/70 to-emerald-400/70', glow: '', textColor: 'text-emerald-100', icon: TrendingUp },
  '2': { label: 'LONG', bg: 'bg-gradient-to-r from-emerald-600 to-emerald-500', glow: 'shadow-[0_0_15px_rgba(16,185,129,0.4)]', textColor: 'text-emerald-100', icon: TrendingUp },
  '3': { label: 'STRONG LONG', bg: 'bg-gradient-to-r from-emerald-700 to-emerald-600', glow: 'shadow-[0_0_25px_rgba(4,120,87,0.6)]', textColor: 'text-emerald-100', icon: TrendingUp },
};

// Fear & Greed Card
function FearGreedCard({ data }: { data: FearGreedData | null | undefined }) {
  if (!data) return null;
  
  const value = data.value;
  const getColor = () => {
    if (value <= 20) return 'text-red-500';
    if (value <= 40) return 'text-orange-400';
    if (value <= 60) return 'text-slate-400';
    if (value <= 80) return 'text-emerald-400';
    return 'text-emerald-500';
  };
  
  const getGradient = () => {
    if (value <= 20) return 'from-red-600 to-red-500';
    if (value <= 40) return 'from-orange-500 to-orange-400';
    if (value <= 60) return 'from-slate-500 to-slate-400';
    if (value <= 80) return 'from-emerald-500 to-emerald-400';
    return 'from-emerald-600 to-emerald-500';
  };

  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-4 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300">
      <div className="flex items-center gap-2 mb-2">
        <Gauge size={18} className="text-amber-400" />
        <span className="text-slate-400 text-xs uppercase tracking-wider">Fear & Greed</span>
      </div>
      <div className="flex items-end gap-3 mb-2">
        <span className={`text-3xl font-black ${getColor()}`}>{value}</span>
        <span className={`text-sm font-semibold ${getColor()} mb-1`}>{data.classification}</span>
      </div>
      <div className="h-2 bg-slate-700 rounded-full overflow-hidden mb-2">
        <div className={`h-full bg-gradient-to-r ${getGradient()} transition-all duration-500`} style={{ width: `${value}%` }} />
      </div>
      <div className="flex items-center gap-1 text-xs">
        <span className="text-slate-500">24h:</span>
        <span className={data.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'}>
          {data.change_24h >= 0 ? '+' : ''}{data.change_24h}
        </span>
      </div>
    </div>
  );
}

// Score Badge
function ScoreBadge({ score }: { score: number }) {
  const config = SCORE_CONFIG[score.toString()] || SCORE_CONFIG['0'];
  const Icon = config.icon;
  return (
    <div className={`${config.bg} ${config.glow} px-2 py-1 rounded-lg flex items-center gap-1.5 font-semibold text-[10px] tracking-wide ${config.textColor}`}>
      <Icon size={12} />
      <span>{config.label}</span>
    </div>
  );
}

// ADX Cell
function ADXCell({ adx }: { adx: Asset['adx'] }) {
  if (!adx) return <span className="text-slate-600">—</span>;
  const value = adx.value;
  const getColor = () => {
    if (value < 20) return 'text-slate-500';
    if (value < 40) return 'text-yellow-400';
    if (value < 60) return 'text-orange-400';
    return 'text-red-400';
  };
  const getLabel = () => {
    if (value < 20) return 'Weak';
    if (value < 40) return 'Mod';
    if (value < 60) return 'Strong';
    return 'V.Strong';
  };
  return (
    <div className="flex flex-col items-center">
      <span className={`font-mono font-bold ${getColor()}`}>{Math.round(value)}</span>
      <span className="text-[9px] text-slate-500">{getLabel()}</span>
    </div>
  );
}

// DeMark Cell
function DemarkCell({ demark }: { demark: Asset['demark'] }) {
  if (!demark || !demark.count) return <span className="text-slate-600">—</span>;
  const isComplete = demark.completed;
  const isBullish = demark.signal === 'bullish';
  let colorClass = 'text-slate-400';
  if (demark.count >= 7) {
    colorClass = isBullish ? 'text-emerald-400' : 'text-red-400';
  }
  return (
    <div className="flex items-center gap-1">
      <span className={`font-mono font-bold ${colorClass}`}>{demark.display}</span>
      {isComplete && <Flame size={14} className={isBullish ? 'text-emerald-400' : 'text-red-400'} />}
    </div>
  );
}

// Volume Cell
function VolumeCell({ volume }: { volume: Asset['relative_volume'] }) {
  if (!volume) return <span className="text-slate-600">—</span>;
  const getColor = () => {
    if (volume.signal === 'high') return 'text-emerald-400';
    if (volume.signal === 'low') return 'text-red-400';
    return 'text-slate-400';
  };
  return (
    <div className="flex items-center gap-1">
      <Volume2 size={12} className={getColor()} />
      <span className={`font-mono text-xs ${getColor()}`}>{volume.display}</span>
    </div>
  );
}

// RSI Cell
function RSICell({ rsi }: { rsi: Asset['rsi'] }) {
  const getColor = (value: number) => {
    if (value < 30) return 'text-emerald-400';
    if (value > 70) return 'text-red-400';
    return 'text-slate-500';
  };
  return (
    <div className="flex gap-2 text-xs font-mono">
      {Object.entries(rsi).map(([tf, value]) => (
        <div key={tf} className="flex flex-col items-center min-w-[24px]">
          <span className="text-slate-600 uppercase text-[8px]">{tf}</span>
          <span className={`font-bold ${getColor(value)}`}>{Math.round(value)}</span>
        </div>
      ))}
    </div>
  );
}

// Expanded Row
function ExpandedRow({ asset }: { asset: Asset }) {
  return (
    <div className="bg-slate-900/50 border-t border-slate-700/50 px-4 py-4 animate-slideDown">
      <div className="grid grid-cols-1 md:grid-cols-4 gap-3">
        {/* RSI */}
        <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/30">
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2 flex items-center gap-2">
            <Activity size={12} /> RSI Multi-TF
          </h4>
          <div className="space-y-1.5">
            {Object.entries(asset.rsi).map(([tf, value]) => (
              <div key={tf} className="flex items-center justify-between">
                <span className="text-slate-500 text-xs uppercase">{tf}</span>
                <div className="flex items-center gap-2">
                  <div className="w-16 h-1.5 bg-slate-700 rounded-full overflow-hidden">
                    <div className={`h-full rounded-full ${value < 30 ? 'bg-emerald-500' : value > 70 ? 'bg-red-500' : 'bg-slate-500'}`} style={{ width: `${value}%` }} />
                  </div>
                  <span className={`text-xs font-mono font-bold w-6 text-right ${value < 30 ? 'text-emerald-400' : value > 70 ? 'text-red-400' : 'text-slate-400'}`}>{Math.round(value)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* ADX */}
        <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/30">
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2 flex items-center gap-2">
            <BarChart3 size={12} /> ADX Trend
          </h4>
          {asset.adx ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">Value</span>
                <span className="text-white font-bold">{Math.round(asset.adx.value)}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">Strength</span>
                <span className={`text-xs font-semibold ${asset.adx.trend_strength === 'strong' || asset.adx.trend_strength === 'very strong' ? 'text-orange-400' : 'text-slate-400'}`}>{asset.adx.trend_strength}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">Direction</span>
                <span className={`text-xs font-semibold ${asset.adx.direction === 'bullish' ? 'text-emerald-400' : asset.adx.direction === 'bearish' ? 'text-red-400' : 'text-slate-400'}`}>{asset.adx.direction}</span>
              </div>
            </div>
          ) : <span className="text-slate-600">No data</span>}
        </div>

        {/* DeMark */}
        <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/30">
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2 flex items-center gap-2">
            <AlertTriangle size={12} /> DeMark
          </h4>
          {asset.demark && asset.demark.count > 0 ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">Count</span>
                <span className="text-white font-bold text-lg">{asset.demark.display}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">Type</span>
                <span className="text-slate-300 text-xs">{asset.demark.type === 'S' ? 'Sell Setup (Bullish)' : 'Buy Setup (Bearish)'}</span>
              </div>
              {asset.demark.completed && (
                <div className="flex items-center gap-2 mt-2 p-2 bg-slate-900/50 rounded-lg">
                  <Flame size={16} className={asset.demark.signal === 'bullish' ? 'text-emerald-400' : 'text-red-400'} />
                  <span className={`text-xs font-semibold ${asset.demark.signal === 'bullish' ? 'text-emerald-400' : 'text-red-400'}`}>
                    {asset.demark.signal === 'bullish' ? 'Bullish Reversal!' : 'Bearish Reversal!'}
                  </span>
                </div>
              )}
            </div>
          ) : <span className="text-slate-600">No active count</span>}
        </div>

        {/* Volume */}
        <div className="bg-slate-800/50 rounded-xl p-3 border border-slate-700/30">
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-2 flex items-center gap-2">
            <Volume2 size={12} /> Rel. Volume
          </h4>
          {asset.relative_volume ? (
            <div className="space-y-2">
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">vs 7d Avg</span>
                <span className={`font-bold text-lg ${asset.relative_volume.signal === 'high' ? 'text-emerald-400' : asset.relative_volume.signal === 'low' ? 'text-red-400' : 'text-slate-300'}`}>{asset.relative_volume.display}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-xs">Signal</span>
                <span className={`text-xs font-semibold ${asset.relative_volume.signal === 'high' ? 'text-emerald-400' : asset.relative_volume.signal === 'low' ? 'text-red-400' : 'text-slate-400'}`}>
                  {asset.relative_volume.signal === 'high' ? 'Above Avg' : asset.relative_volume.signal === 'low' ? 'Below Avg' : 'Normal'}
                </span>
              </div>
            </div>
          ) : <span className="text-slate-600">No data</span>}
        </div>
      </div>
    </div>
  );
}

// Asset Row
function AssetRow({ asset, isExpanded, onToggle }: { asset: Asset; isExpanded: boolean; onToggle: () => void }) {
  return (
    <>
      <tr className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-all duration-200 cursor-pointer group" onClick={onToggle}>
        <td className="px-3 py-2.5">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center font-bold text-[10px] border border-slate-600/50 group-hover:border-cyan-500/30">
              {asset.symbol.slice(0, 3)}
            </div>
            <div>
              <div className="font-semibold text-white text-xs group-hover:text-cyan-400">{asset.symbol}</div>
              <div className="text-[9px] text-slate-500 hidden sm:block">{asset.name}</div>
            </div>
          </div>
        </td>
        <td className="px-3 py-2.5 font-mono">
          <div className="text-white font-semibold text-xs">
            ${asset.price.toLocaleString(undefined, { maximumFractionDigits: asset.price > 100 ? 0 : asset.price > 1 ? 2 : 6 })}
          </div>
          <div className={`text-[9px] ${asset.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'}`}>
            {asset.change_24h >= 0 ? '+' : ''}{asset.change_24h.toFixed(2)}%
          </div>
        </td>
        <td className="px-3 py-2.5"><ScoreBadge score={asset.score} /></td>
        <td className="px-3 py-2.5 hidden xl:table-cell"><RSICell rsi={asset.rsi} /></td>
        <td className="px-3 py-2.5 hidden lg:table-cell"><ADXCell adx={asset.adx} /></td>
        <td className="px-3 py-2.5 hidden lg:table-cell"><DemarkCell demark={asset.demark} /></td>
        <td className="px-3 py-2.5 hidden md:table-cell"><VolumeCell volume={asset.relative_volume} /></td>
        <td className="px-3 py-2.5">
          {isExpanded ? <ChevronUp size={16} className="text-cyan-400" /> : <ChevronDown size={16} className="text-slate-600 group-hover:text-cyan-400" />}
        </td>
      </tr>
      {isExpanded && <tr><td colSpan={8}><ExpandedRow asset={asset} /></td></tr>}
    </>
  );
}

// Market Sentiment
function MarketSentiment({ assets }: { assets: Asset[] }) {
  const bullish = assets.filter(a => a.score > 0).length;
  const bearish = assets.filter(a => a.score < 0).length;
  const neutral = assets.filter(a => a.score === 0).length;
  const total = assets.length || 1;
  const sentiment = bullish > bearish + 3 ? 'BULLISH' : bearish > bullish + 3 ? 'BEARISH' : 'MIXED';
  const sentimentColor = sentiment === 'BULLISH' ? 'text-emerald-400' : sentiment === 'BEARISH' ? 'text-red-400' : 'text-amber-400';

  return (
    <div className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-5 border border-slate-700/50">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
        <div>
          <h2 className="text-slate-400 text-xs uppercase tracking-wider mb-1">Market Sentiment</h2>
          <div className={`text-3xl font-black tracking-tight ${sentimentColor}`}>{sentiment}</div>
        </div>
        <div className="flex gap-6 text-center">
          <div><div className="text-emerald-400 text-xl font-bold">{bullish}</div><div className="text-[9px] text-slate-500 uppercase">Bullish</div></div>
          <div><div className="text-slate-400 text-xl font-bold">{neutral}</div><div className="text-[9px] text-slate-500 uppercase">Neutral</div></div>
          <div><div className="text-red-400 text-xl font-bold">{bearish}</div><div className="text-[9px] text-slate-500 uppercase">Bearish</div></div>
        </div>
      </div>
      <div className="h-3 bg-slate-700 rounded-full overflow-hidden flex">
        <div className="bg-emerald-500 transition-all duration-700" style={{ width: `${(bullish / total) * 100}%` }} />
        <div className="bg-slate-500 transition-all duration-700" style={{ width: `${(neutral / total) * 100}%` }} />
        <div className="bg-red-500 transition-all duration-700" style={{ width: `${(bearish / total) * 100}%` }} />
      </div>
    </div>
  );
}

// Stats Card
function StatsCard({ icon: Icon, label, value, subValue, color }: { icon: React.ElementType; label: string; value: number | string; subValue?: string; color: string }) {
  return (
    <div className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-4 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300">
      <div className="flex items-start justify-between mb-2">
        <div className={`p-2 rounded-lg bg-slate-800 ${color}`}><Icon size={16} /></div>
      </div>
      <div className="text-xl font-bold text-white mb-0.5">{value}</div>
      <div className="text-slate-500 text-xs">{label}</div>
      {subValue && <div className="text-[9px] text-slate-600 mt-0.5">{subValue}</div>}
    </div>
  );
}

// Main Component
export default function MoonlanderSignals() {
  const [data, setData] = useState<SignalsResponse | null>(null);
  const [expandedRow, setExpandedRow] = useState<string | null>(null);
  const [filter, setFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [sortBy, setSortBy] = useState('score');
  const [sortDir, setSortDir] = useState<'asc' | 'desc'>('desc');
  const [isLoading, setIsLoading] = useState(true);

  const loadData = async () => {
    setIsLoading(true);
    try {
      const result = await fetchSignals();
      setData(result);
    } catch (error) {
      console.error('Error loading data:', error);
    }
    setIsLoading(false);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 5 * 60 * 1000);
    return () => clearInterval(interval);
  }, []);

  const handleSort = (column: string) => {
    if (sortBy === column) setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    else { setSortBy(column); setSortDir('desc'); }
  };

  const assets = data?.assets || [];
  
  let filteredAssets = assets
    .filter(a => {
      if (filter === 'long') return a.score > 0;
      if (filter === 'short') return a.score < 0;
      if (filter === 'neutral') return a.score === 0;
      if (filter === 'strong') return Math.abs(a.score) >= 2;
      return true;
    })
    .filter(a => searchQuery === '' || a.symbol.toLowerCase().includes(searchQuery.toLowerCase()) || a.name.toLowerCase().includes(searchQuery.toLowerCase()));

  filteredAssets = filteredAssets.sort((a, b) => {
    let comparison = 0;
    switch(sortBy) {
      case 'score': comparison = a.score - b.score; break;
      case 'symbol': comparison = a.symbol.localeCompare(b.symbol); break;
      case 'price': comparison = a.price - b.price; break;
      case 'adx': comparison = (a.adx?.value || 0) - (b.adx?.value || 0); break;
      default: comparison = a.score - b.score;
    }
    return sortDir === 'desc' ? -comparison : comparison;
  });

  const strongSignals = assets.filter(a => Math.abs(a.score) >= 2).length;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-cyan-500/10 rounded-full blur-[120px] animate-pulse" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-[120px] animate-pulse" style={{ animationDelay: '1s' }} />
      </div>

      <div className="relative z-10">
        {/* Header */}
        <header className="border-b border-slate-800/50 backdrop-blur-xl bg-slate-950/80 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="relative">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center shadow-[0_0_20px_rgba(6,182,212,0.4)]">
                    <span className="text-lg">🌙</span>
                  </div>
                  <div className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-slate-950 animate-pulse" />
                </div>
                <div>
                  <h1 className="text-lg font-black tracking-tight bg-gradient-to-r from-white via-cyan-200 to-white bg-clip-text text-transparent">MOONLANDER SIGNALS</h1>
                  <p className="text-slate-500 text-[10px] tracking-wider">Multi-Timeframe Crypto Intelligence</p>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <div className="hidden sm:flex items-center gap-2 text-slate-500 text-xs">
                  <Clock size={12} />
                  <span>{data?.generated_at ? new Date(data.generated_at).toLocaleTimeString() : '--:--'}</span>
                </div>
                <button onClick={loadData} className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/50 transition-all">
                  <RefreshCw size={16} className={`text-slate-400 hover:text-cyan-400 ${isLoading ? 'animate-spin' : ''}`} />
                </button>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 py-5">
          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-5">
            <StatsCard icon={Activity} label="Assets Tracked" value={assets.length} subValue="Moonlander pairs" color="text-cyan-400" />
            <StatsCard icon={Flame} label="Strong Signals" value={strongSignals} subValue="High confidence" color="text-orange-400" />
            <StatsCard icon={TrendingUp} label="Bullish" value={assets.filter(a => a.score > 0).length} subValue="Long bias" color="text-emerald-400" />
            <StatsCard icon={TrendingDown} label="Bearish" value={assets.filter(a => a.score < 0).length} subValue="Short bias" color="text-red-400" />
            <FearGreedCard data={data?.fear_greed} />
          </div>

          {/* Sentiment */}
          <div className="mb-5"><MarketSentiment assets={assets} /></div>

          {/* Filters */}
          <div className="flex flex-col md:flex-row gap-3 mb-4">
            <div className="relative flex-1 max-w-xs">
              <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
              <input type="text" placeholder="Search assets..." value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)} className="w-full pl-9 pr-3 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-xs text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50" />
            </div>
            <div className="flex gap-2 flex-wrap">
              {[{ key: 'all', label: 'All' }, { key: 'strong', label: 'Strong' }, { key: 'long', label: 'Long' }, { key: 'short', label: 'Short' }, { key: 'neutral', label: 'Neutral' }].map(({ key, label }) => (
                <button key={key} onClick={() => setFilter(key)} className={`px-3 py-1.5 rounded-lg text-[10px] font-medium transition-all ${filter === key ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50' : 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:border-slate-600'}`}>{label}</button>
              ))}
            </div>
          </div>

          <div className="text-[10px] text-slate-500 mb-2">Showing {filteredAssets.length} of {assets.length} assets</div>

          {/* Table */}
          <div className="bg-gradient-to-br from-slate-900/80 to-slate-900/40 rounded-2xl border border-slate-800/50 overflow-hidden">
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-slate-700/50 bg-slate-900/50">
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-cyan-400" onClick={() => handleSort('symbol')}><div className="flex items-center gap-1">Asset <ArrowUpDown size={10} /></div></th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-cyan-400" onClick={() => handleSort('price')}><div className="flex items-center gap-1">Price <ArrowUpDown size={10} /></div></th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-cyan-400" onClick={() => handleSort('score')}><div className="flex items-center gap-1">Signal <ArrowUpDown size={10} /></div></th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider hidden xl:table-cell">RSI</th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider hidden lg:table-cell cursor-pointer hover:text-cyan-400" onClick={() => handleSort('adx')}><div className="flex items-center gap-1">ADX <ArrowUpDown size={10} /></div></th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider hidden lg:table-cell">DeMark</th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider hidden md:table-cell">Volume</th>
                    <th className="px-3 py-2.5 text-left text-[9px] font-semibold text-slate-400 uppercase tracking-wider"></th>
                  </tr>
                </thead>
                <tbody>
                  {filteredAssets.map((asset) => (
                    <AssetRow key={asset.symbol} asset={asset} isExpanded={expandedRow === asset.symbol} onToggle={() => setExpandedRow(expandedRow === asset.symbol ? null : asset.symbol)} />
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Legend */}
          <div className="mt-5 p-4 bg-slate-900/50 rounded-xl border border-slate-800/50">
            <h3 className="text-[10px] font-semibold text-slate-300 mb-3 uppercase tracking-wider">Signal Legend</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-[10px]">
              <div className="flex items-center gap-2"><span className="text-emerald-400 font-mono">RSI &lt;30</span><span className="text-slate-400">Oversold (Bullish)</span></div>
              <div className="flex items-center gap-2"><span className="text-red-400 font-mono">RSI &gt;70</span><span className="text-slate-400">Overbought (Bearish)</span></div>
              <div className="flex items-center gap-2"><span className="text-orange-400 font-mono">ADX &gt;40</span><span className="text-slate-400">Strong Trend</span></div>
              <div className="flex items-center gap-2"><span className="text-yellow-400 font-mono">S:9! / B:9!</span><span className="text-slate-400">DeMark Exhaustion</span></div>
            </div>
          </div>

          {/* Footer */}
          <footer className="mt-6 text-center text-slate-600 text-[10px]">
            <p>Data refreshes every 30 minutes • Not financial advice • Trade at your own risk</p>
            <p className="mt-1">Powered by CoinGecko API • Built for moonlander.trade</p>
          </footer>
        </main>
      </div>
    </div>
  );
}
