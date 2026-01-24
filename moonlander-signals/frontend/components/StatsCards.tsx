'use client';

import { motion } from 'framer-motion';
import { Activity, Flame, TrendingUp, TrendingDown, LucideIcon } from 'lucide-react';
import { Summary } from '@/lib/types';

interface StatsCardsProps {
  summary: Summary;
  totalAssets: number;
}

interface StatCardProps {
  icon: LucideIcon;
  label: string;
  value: number | string;
  subValue?: string;
  color: string;
  delay?: number;
}

function StatCard({ icon: Icon, label, value, subValue, color, delay = 0 }: StatCardProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay }}
      whileHover={{ scale: 1.02, y: -2 }}
      className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-4 border border-slate-700/50 hover:border-cyan-500/30 transition-all duration-300 group"
    >
      <div className="flex items-start justify-between mb-2">
        <motion.div
          className={`p-2 rounded-lg bg-slate-800 ${color}`}
          whileHover={{ scale: 1.1, rotate: 5 }}
          transition={{ type: 'spring', stiffness: 400 }}
        >
          <Icon size={18} />
        </motion.div>
      </div>
      
      <motion.div
        className="text-2xl font-bold text-white mb-0.5"
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: delay + 0.2 }}
      >
        {value}
      </motion.div>
      
      <div className="text-slate-500 text-xs">{label}</div>
      
      {subValue && (
        <div className="text-[10px] text-slate-600 mt-0.5">{subValue}</div>
      )}
    </motion.div>
  );
}

export function StatsCards({ summary, totalAssets }: StatsCardsProps) {
  return (
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
      <StatCard
        icon={Activity}
        label="Assets Tracked"
        value={totalAssets}
        subValue="Moonlander pairs"
        color="text-cyan-400"
        delay={0}
      />
      <StatCard
        icon={Flame}
        label="Strong Signals"
        value={summary.strong_signals}
        subValue="High confidence"
        color="text-orange-400"
        delay={0.1}
      />
      <StatCard
        icon={TrendingUp}
        label="Bullish"
        value={summary.bullish}
        subValue="Long bias"
        color="text-emerald-400"
        delay={0.2}
      />
      <StatCard
        icon={TrendingDown}
        label="Bearish"
        value={summary.bearish}
        subValue="Short bias"
        color="text-red-400"
        delay={0.3}
      />
    </div>
  );
}
