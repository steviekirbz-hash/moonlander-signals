'use client';

import { motion } from 'framer-motion';
import { TrendingUp, TrendingDown, Minus, Flame } from 'lucide-react';
import { ScoreValue } from '@/lib/types';

interface ScoreBadgeProps {
  score: ScoreValue;
}

const SCORE_CONFIG: Record<number, {
  label: string;
  shortLabel: string;
  className: string;
  icon: typeof TrendingUp;
}> = {
  [-3]: {
    label: 'STRONG SHORT',
    shortLabel: 'STR SHORT',
    className: 'score-strong-short',
    icon: TrendingDown,
  },
  [-2]: {
    label: 'SHORT',
    shortLabel: 'SHORT',
    className: 'score-short',
    icon: TrendingDown,
  },
  [-1]: {
    label: 'LEAN SHORT',
    shortLabel: 'LEAN SHORT',
    className: 'score-lean-short',
    icon: TrendingDown,
  },
  [0]: {
    label: 'NEUTRAL',
    shortLabel: 'NEUTRAL',
    className: 'score-neutral',
    icon: Minus,
  },
  [1]: {
    label: 'LEAN LONG',
    shortLabel: 'LEAN LONG',
    className: 'score-lean-long',
    icon: TrendingUp,
  },
  [2]: {
    label: 'LONG',
    shortLabel: 'LONG',
    className: 'score-long',
    icon: TrendingUp,
  },
  [3]: {
    label: 'STRONG LONG',
    shortLabel: 'STR LONG',
    className: 'score-strong-long',
    icon: TrendingUp,
  },
};

export function ScoreBadge({ score }: ScoreBadgeProps) {
  const config = SCORE_CONFIG[score];
  const Icon = config.icon;

  return (
    <motion.div
      className={`score-badge ${config.className}`}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
    >
      <Icon size={14} />
      <span className="hidden sm:inline">{config.label}</span>
      <span className="sm:hidden">{config.shortLabel}</span>
    </motion.div>
  );
}

interface ScoreBarProps {
  score: ScoreValue;
}

export function ScoreBar({ score }: ScoreBarProps) {
  // Position on -3 to +3 scale (0-100%)
  const position = ((score + 3) / 6) * 100;

  const dotColor =
    score > 0
      ? 'bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.8)]'
      : score < 0
      ? 'bg-red-400 shadow-[0_0_8px_rgba(248,113,113,0.8)]'
      : 'bg-slate-400';

  return (
    <div className="w-20 h-2 bg-slate-700 rounded-full relative overflow-hidden">
      {/* Background gradient */}
      <div className="absolute inset-0 flex">
        <div className="w-1/2 bg-gradient-to-r from-red-600/30 to-slate-600/30" />
        <div className="w-1/2 bg-gradient-to-l from-emerald-600/30 to-slate-600/30" />
      </div>
      
      {/* Position indicator */}
      <motion.div
        className={`absolute top-0 h-full w-2 rounded-full ${dotColor}`}
        initial={{ left: '50%' }}
        animate={{ left: `calc(${position}% - 4px)` }}
        transition={{ duration: 0.5, ease: 'easeOut' }}
      />
    </div>
  );
}

interface FireIndicatorProps {
  aligned: number;
  max?: number;
}

export function FireIndicator({ aligned, max = 4 }: FireIndicatorProps) {
  return (
    <div className="flex gap-0.5">
      {Array.from({ length: max }).map((_, i) => (
        <motion.div
          key={i}
          initial={{ opacity: 0, scale: 0 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: i * 0.05 }}
        >
          <Flame
            size={14}
            className={`transition-all duration-300 ${
              i < aligned
                ? 'text-orange-400 drop-shadow-[0_0_6px_rgba(251,146,60,0.8)]'
                : 'text-slate-700'
            }`}
            style={i < aligned ? { animation: `fireFlicker 0.5s ease-in-out infinite ${i * 0.1}s` } : undefined}
          />
        </motion.div>
      ))}
    </div>
  );
}

interface RSICellProps {
  rsi: {
    '15m': number;
    '1h': number;
    '4h': number;
    '1d': number;
  };
}

export function RSICell({ rsi }: RSICellProps) {
  const getColor = (value: number) => {
    if (value < 30) return 'text-emerald-400';
    if (value < 35) return 'text-emerald-300/70';
    if (value > 70) return 'text-red-400';
    if (value > 65) return 'text-red-300/70';
    return 'text-slate-500';
  };

  const timeframes = ['15m', '1h', '4h', '1d'] as const;

  return (
    <div className="flex gap-2 text-xs font-mono">
      {timeframes.map((tf) => (
        <div key={tf} className="flex flex-col items-center min-w-[28px]">
          <span className="text-slate-600 uppercase text-[9px]">{tf}</span>
          <span className={`font-bold ${getColor(rsi[tf])}`}>{rsi[tf]}</span>
        </div>
      ))}
    </div>
  );
}
