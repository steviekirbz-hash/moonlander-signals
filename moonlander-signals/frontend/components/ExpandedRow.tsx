'use client';

import { motion } from 'framer-motion';
import { Activity, BarChart3, Zap, Target } from 'lucide-react';
import { Asset } from '@/lib/types';
import { FireIndicator } from './SignalIndicators';
import { formatFunding } from '@/lib/api';

interface ExpandedRowProps {
  asset: Asset;
}

export function ExpandedRow({ asset }: ExpandedRowProps) {
  const getRSIColor = (value: number) => {
    if (value < 30) return 'bg-emerald-500';
    if (value > 70) return 'bg-red-500';
    return 'bg-slate-500';
  };

  const getRSITextColor = (value: number) => {
    if (value < 30) return 'text-emerald-400';
    if (value > 70) return 'text-red-400';
    return 'text-slate-400';
  };

  const getFundingColor = (rate: number | null) => {
    if (rate === null) return 'text-slate-400';
    if (rate > 0.0001) return 'text-red-400';
    if (rate < -0.0001) return 'text-emerald-400';
    return 'text-slate-400';
  };

  const getCrowdPosition = (rate: number | null) => {
    if (rate === null) return { text: 'Unknown', color: 'text-slate-400' };
    if (rate > 0.0001) return { text: 'Crowded Long', color: 'text-red-400' };
    if (rate < -0.0001) return { text: 'Crowded Short', color: 'text-emerald-400' };
    return { text: 'Balanced', color: 'text-slate-400' };
  };

  const crowdPosition = getCrowdPosition(asset.funding_rate);

  return (
    <motion.div
      initial={{ opacity: 0, height: 0 }}
      animate={{ opacity: 1, height: 'auto' }}
      exit={{ opacity: 0, height: 0 }}
      transition={{ duration: 0.3 }}
      className="bg-slate-900/50 border-t border-slate-700/50 px-6 py-4"
    >
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        {/* RSI Detail */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.05 }}
          className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/30"
        >
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-3 flex items-center gap-2">
            <Activity size={14} /> RSI Multi-Timeframe
          </h4>
          <div className="space-y-2">
            {(['15m', '1h', '4h', '1d'] as const).map((tf) => (
              <div key={tf} className="flex items-center justify-between">
                <span className="text-slate-500 text-sm uppercase">{tf}</span>
                <div className="flex items-center gap-2">
                  <div className="w-20 h-2 bg-slate-700 rounded-full overflow-hidden">
                    <motion.div
                      className={`h-full rounded-full ${getRSIColor(asset.rsi[tf])}`}
                      initial={{ width: 0 }}
                      animate={{ width: `${asset.rsi[tf]}%` }}
                      transition={{ duration: 0.5, delay: 0.1 }}
                    />
                  </div>
                  <span className={`text-sm font-mono font-bold w-8 text-right ${getRSITextColor(asset.rsi[tf])}`}>
                    {asset.rsi[tf]}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Trend Alignment */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/30"
        >
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-3 flex items-center gap-2">
            <BarChart3 size={14} /> Trend Alignment
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">EMA Cross</span>
              <FireIndicator aligned={asset.ema_aligned} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">MACD</span>
              <FireIndicator aligned={asset.macd_aligned} />
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">RSI Aligned</span>
              <FireIndicator aligned={asset.rsi_aligned} />
            </div>
          </div>
        </motion.div>

        {/* Funding & Sentiment */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.15 }}
          className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/30"
        >
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-3 flex items-center gap-2">
            <Zap size={14} /> Funding & Sentiment
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Funding Rate</span>
              <span className={`font-mono font-bold ${getFundingColor(asset.funding_rate)}`}>
                {formatFunding(asset.funding_rate)}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Crowd Position</span>
              <span className={`text-sm font-semibold ${crowdPosition.color}`}>
                {crowdPosition.text}
              </span>
            </div>
            {asset.long_short_ratio !== null && (
              <div className="flex items-center justify-between">
                <span className="text-slate-400 text-sm">L/S Ratio</span>
                <span className="text-sm font-mono text-slate-300">
                  {asset.long_short_ratio.toFixed(2)}
                </span>
              </div>
            )}
          </div>
        </motion.div>

        {/* Liquidation Zones */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="bg-slate-800/50 rounded-xl p-4 border border-slate-700/30"
        >
          <h4 className="text-slate-400 text-xs uppercase tracking-wider mb-3 flex items-center gap-2">
            <Target size={14} /> Liquidation Magnet
          </h4>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-slate-400 text-sm">Nearest Zone</span>
              <span
                className={`text-sm font-semibold ${
                  asset.liq_zone === 'above'
                    ? 'text-emerald-400'
                    : asset.liq_zone === 'below'
                    ? 'text-red-400'
                    : 'text-slate-400'
                }`}
              >
                {asset.liq_zone === 'above'
                  ? '↑ Above Price'
                  : asset.liq_zone === 'below'
                  ? '↓ Below Price'
                  : 'Neutral'}
              </span>
            </div>
            <div className="text-xs text-slate-500">
              Price attracted toward liquidation clusters
            </div>
            <div className="text-xs text-slate-600">
              Confidence: {Math.round(asset.confidence * 100)}%
            </div>
          </div>
        </motion.div>
      </div>
    </motion.div>
  );
}
