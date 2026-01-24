'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { RefreshCw, Clock, Menu, X } from 'lucide-react';

interface HeaderProps {
  lastUpdate: string;
  isLoading: boolean;
  onRefresh: () => void;
}

export function Header({ lastUpdate, isLoading, onRefresh }: HeaderProps) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const formatTime = (isoString: string) => {
    try {
      return new Date(isoString).toLocaleTimeString();
    } catch {
      return 'N/A';
    }
  };

  return (
    <header className="sticky top-0 z-50 border-b border-slate-800/50 backdrop-blur-xl bg-slate-950/80">
      <div className="max-w-7xl mx-auto px-4 py-3">
        <div className="flex items-center justify-between">
          {/* Logo */}
          <div className="flex items-center gap-3">
            <motion.div
              className="relative"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-purple-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                <span className="text-lg">🌙</span>
              </div>
              <motion.div
                className="absolute -bottom-0.5 -right-0.5 w-3 h-3 bg-emerald-500 rounded-full border-2 border-slate-950"
                animate={{ scale: [1, 1.2, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </motion.div>
            
            <div>
              <h1 className="text-lg font-black tracking-tight gradient-text font-display">
                MOONLANDER SIGNALS
              </h1>
              <p className="text-slate-500 text-[10px] tracking-wider uppercase">
                Multi-Timeframe Crypto Intelligence
              </p>
            </div>
          </div>

          {/* Desktop: Time & Refresh */}
          <div className="hidden sm:flex items-center gap-4">
            <div className="flex items-center gap-2 text-slate-500 text-xs">
              <Clock size={14} />
              <span>Updated {formatTime(lastUpdate)}</span>
            </div>
            
            <motion.button
              onClick={onRefresh}
              disabled={isLoading}
              className="p-2 rounded-lg bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-500/50 transition-all disabled:opacity-50"
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
            >
              <RefreshCw 
                size={16} 
                className={`text-slate-400 hover:text-cyan-400 transition-colors ${isLoading ? 'animate-spin' : ''}`} 
              />
            </motion.button>
          </div>

          {/* Mobile: Menu button */}
          <button
            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
            className="sm:hidden p-2 rounded-lg bg-slate-800 border border-slate-700"
          >
            {mobileMenuOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>

        {/* Mobile menu */}
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="sm:hidden mt-4 pt-4 border-t border-slate-800"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2 text-slate-500 text-xs">
                <Clock size={14} />
                <span>Updated {formatTime(lastUpdate)}</span>
              </div>
              
              <button
                onClick={() => {
                  onRefresh();
                  setMobileMenuOpen(false);
                }}
                disabled={isLoading}
                className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 text-xs text-slate-400"
              >
                <RefreshCw size={14} className={isLoading ? 'animate-spin' : ''} />
                Refresh
              </button>
            </div>
          </motion.div>
        )}
      </div>
    </header>
  );
}
