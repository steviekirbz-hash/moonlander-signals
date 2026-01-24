'use client';

import { motion } from 'framer-motion';
import { FireIndicator } from './SignalIndicators';

export function Legend() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.6 }}
      className="mt-6 p-4 bg-slate-900/50 rounded-xl border border-slate-800/50"
    >
      <h3 className="text-xs font-semibold text-slate-300 mb-3 uppercase tracking-wider">
        Signal Legend
      </h3>
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3 text-xs">
        <div className="flex items-center gap-2">
          <FireIndicator aligned={4} />
          <span className="text-slate-400">All timeframes aligned</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-emerald-400 font-mono">RSI &lt;30</span>
          <span className="text-slate-400">Oversold (Bullish)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-red-400 font-mono">RSI &gt;70</span>
          <span className="text-slate-400">Overbought (Bearish)</span>
        </div>
        <div className="flex items-center gap-2">
          <span className="text-red-400 font-mono">+0.05%</span>
          <span className="text-slate-400">Crowded longs (Bearish)</span>
        </div>
      </div>
    </motion.div>
  );
}
