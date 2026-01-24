'use client';

import { motion } from 'framer-motion';
import { Summary } from '@/lib/types';

interface MarketSentimentProps {
  summary: Summary;
  totalAssets: number;
}

export function MarketSentiment({ summary, totalAssets }: MarketSentimentProps) {
  const { bullish, bearish, neutral, by_score } = summary;
  
  const sentiment = bullish > bearish + 5 ? 'BULLISH' : 
                    bearish > bullish + 5 ? 'BEARISH' : 'MIXED';
  
  const sentimentColor = sentiment === 'BULLISH' ? 'text-emerald-400' : 
                         sentiment === 'BEARISH' ? 'text-red-400' : 'text-amber-400';
  
  const glowClass = sentiment === 'BULLISH' ? 'shadow-[0_0_60px_rgba(16,185,129,0.2)]' : 
                    sentiment === 'BEARISH' ? 'shadow-[0_0_60px_rgba(239,68,68,0.2)]' : '';

  // Calculate percentages for the bar
  const segments = [
    { score: -3, count: by_score['-3'], color: 'bg-red-700', label: 'Strong Short' },
    { score: -2, count: by_score['-2'], color: 'bg-red-500', label: 'Short' },
    { score: -1, count: by_score['-1'], color: 'bg-red-400/70', label: 'Lean Short' },
    { score: 0, count: by_score['0'], color: 'bg-slate-500', label: 'Neutral' },
    { score: 1, count: by_score['1'], color: 'bg-emerald-400/70', label: 'Lean Long' },
    { score: 2, count: by_score['2'], color: 'bg-emerald-500', label: 'Long' },
    { score: 3, count: by_score['3'], color: 'bg-emerald-700', label: 'Strong Long' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.6, delay: 0.2 }}
      className={`bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 ${glowClass} transition-all duration-500 mb-6`}
    >
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-6">
        <div>
          <h2 className="text-slate-400 text-xs uppercase tracking-wider mb-1">
            Market Sentiment
          </h2>
          <motion.div
            className={`text-3xl font-black tracking-tight ${sentimentColor} font-display`}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            {sentiment}
          </motion.div>
        </div>
        
        {/* Quick stats */}
        <div className="flex gap-6 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.5 }}
          >
            <div className="text-emerald-400 text-2xl font-bold">{bullish}</div>
            <div className="text-[10px] text-slate-500 uppercase">Bullish</div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.6 }}
          >
            <div className="text-slate-400 text-2xl font-bold">{neutral}</div>
            <div className="text-[10px] text-slate-500 uppercase">Neutral</div>
          </motion.div>
          <motion.div
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.7 }}
          >
            <div className="text-red-400 text-2xl font-bold">{bearish}</div>
            <div className="text-[10px] text-slate-500 uppercase">Bearish</div>
          </motion.div>
        </div>
      </div>

      {/* 7-tier Sentiment Bar */}
      <div className="h-4 bg-slate-700 rounded-full overflow-hidden flex">
        {segments.map((segment, index) => {
          const width = (segment.count / totalAssets) * 100;
          return (
            <motion.div
              key={segment.score}
              className={`${segment.color} relative group cursor-pointer`}
              initial={{ width: 0 }}
              animate={{ width: `${width}%` }}
              transition={{ duration: 0.8, delay: 0.3 + index * 0.05 }}
              title={`${segment.label}: ${segment.count}`}
            >
              {/* Tooltip on hover */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-2 px-2 py-1 bg-slate-800 rounded text-[10px] text-white whitespace-nowrap opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                {segment.label}: {segment.count}
              </div>
            </motion.div>
          );
        })}
      </div>

      {/* Legend */}
      <motion.div
        className="flex flex-wrap justify-center gap-x-4 gap-y-2 mt-4 text-[10px]"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 1 }}
      >
        {segments.map((segment) => (
          <div key={segment.score} className="flex items-center gap-1">
            <div className={`w-3 h-3 rounded ${segment.color}`} />
            <span className="text-slate-500">
              {segment.label} ({segment.count})
            </span>
          </div>
        ))}
      </motion.div>
    </motion.div>
  );
}
