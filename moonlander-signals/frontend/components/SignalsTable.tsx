'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ChevronDown, ChevronUp, ArrowUpDown } from 'lucide-react';
import { Asset, SortField, SortDirection } from '@/lib/types';
import { formatPrice, formatPercent } from '@/lib/api';
import { ScoreBadge, ScoreBar, RSICell, FireIndicator } from './SignalIndicators';
import { ExpandedRow } from './ExpandedRow';

interface SignalsTableProps {
  assets: Asset[];
  sortBy: SortField;
  sortDir: SortDirection;
  onSort: (field: SortField) => void;
}

interface TableRowProps {
  asset: Asset;
  index: number;
  isExpanded: boolean;
  onToggle: () => void;
}

function TableRow({ asset, index, isExpanded, onToggle }: TableRowProps) {
  return (
    <>
      <motion.tr
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.3, delay: index * 0.02 }}
        className="border-b border-slate-800/50 hover:bg-slate-800/30 transition-all duration-200 cursor-pointer group"
        onClick={onToggle}
      >
        {/* Asset */}
        <td className="px-4 py-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center font-bold text-xs border border-slate-600/50 group-hover:border-cyan-500/30 transition-colors">
              {asset.symbol.slice(0, 3)}
            </div>
            <div>
              <div className="font-semibold text-white text-sm group-hover:text-cyan-400 transition-colors">
                {asset.symbol}
              </div>
              <div className="text-[10px] text-slate-500 hidden sm:block">{asset.name}</div>
            </div>
          </div>
        </td>

        {/* Category (hidden on mobile) */}
        <td className="px-4 py-3 hidden lg:table-cell">
          <span className="text-[10px] px-2 py-1 rounded-full bg-slate-800 text-slate-400 border border-slate-700">
            {asset.category}
          </span>
        </td>

        {/* Price */}
        <td className="px-4 py-3 font-mono">
          <div className="text-white font-semibold text-sm">${formatPrice(asset.price)}</div>
          <div
            className={`text-[10px] ${
              asset.change_24h >= 0 ? 'text-emerald-400' : 'text-red-400'
            }`}
          >
            {formatPercent(asset.change_24h)}
          </div>
        </td>

        {/* Signal */}
        <td className="px-4 py-3">
          <div className="flex items-center gap-3">
            <ScoreBadge score={asset.score as any} />
            <div className="hidden sm:block">
              <ScoreBar score={asset.score as any} />
            </div>
          </div>
        </td>

        {/* RSI (hidden on smaller screens) */}
        <td className="px-4 py-3 hidden xl:table-cell">
          <RSICell rsi={asset.rsi} />
        </td>

        {/* Trend Fire (hidden on mobile) */}
        <td className="px-4 py-3 hidden md:table-cell">
          <div className="flex items-center gap-3">
            <div className="flex flex-col items-center">
              <span className="text-[9px] text-slate-600 uppercase">EMA</span>
              <FireIndicator aligned={asset.ema_aligned} />
            </div>
            <div className="flex flex-col items-center">
              <span className="text-[9px] text-slate-600 uppercase">MACD</span>
              <FireIndicator aligned={asset.macd_aligned} />
            </div>
          </div>
        </td>

        {/* Funding (hidden on smaller screens) */}
        <td className="px-4 py-3 hidden lg:table-cell">
          <span
            className={`font-mono text-xs ${
              asset.funding_rate === null
                ? 'text-slate-500'
                : asset.funding_rate > 0.0001
                ? 'text-red-400'
                : asset.funding_rate < -0.0001
                ? 'text-emerald-400'
                : 'text-slate-500'
            }`}
          >
            {asset.funding_rate !== null
              ? `${asset.funding_rate > 0 ? '+' : ''}${(asset.funding_rate * 100).toFixed(4)}%`
              : 'N/A'}
          </span>
        </td>

        {/* Expand icon */}
        <td className="px-4 py-3">
          <motion.div
            animate={{ rotate: isExpanded ? 180 : 0 }}
            transition={{ duration: 0.2 }}
          >
            {isExpanded ? (
              <ChevronUp size={18} className="text-cyan-400" />
            ) : (
              <ChevronDown size={18} className="text-slate-600 group-hover:text-cyan-400 transition-colors" />
            )}
          </motion.div>
        </td>
      </motion.tr>

      {/* Expanded content */}
      <AnimatePresence>
        {isExpanded && (
          <tr>
            <td colSpan={8}>
              <ExpandedRow asset={asset} />
            </td>
          </tr>
        )}
      </AnimatePresence>
    </>
  );
}

interface SortHeaderProps {
  field: SortField;
  label: string;
  currentSort: SortField;
  sortDir: SortDirection;
  onSort: (field: SortField) => void;
  className?: string;
}

function SortHeader({ field, label, currentSort, sortDir, onSort, className = '' }: SortHeaderProps) {
  const isActive = currentSort === field;

  return (
    <th
      className={`px-4 py-3 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider cursor-pointer hover:text-cyan-400 transition-colors ${className}`}
      onClick={() => onSort(field)}
    >
      <div className="flex items-center gap-1">
        {label}
        <ArrowUpDown
          size={12}
          className={isActive ? 'text-cyan-400' : 'opacity-50'}
        />
      </div>
    </th>
  );
}

export function SignalsTable({ assets, sortBy, sortDir, onSort }: SignalsTableProps) {
  const [expandedRow, setExpandedRow] = useState<string | null>(null);

  const handleToggle = (symbol: string) => {
    setExpandedRow(expandedRow === symbol ? null : symbol);
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="bg-gradient-to-br from-slate-900/80 to-slate-900/40 rounded-2xl border border-slate-800/50 overflow-hidden backdrop-blur-sm"
    >
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700/50 bg-slate-900/50">
              <SortHeader
                field="symbol"
                label="Asset"
                currentSort={sortBy}
                sortDir={sortDir}
                onSort={onSort}
              />
              <th className="px-4 py-3 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider hidden lg:table-cell">
                Category
              </th>
              <SortHeader
                field="price"
                label="Price"
                currentSort={sortBy}
                sortDir={sortDir}
                onSort={onSort}
              />
              <SortHeader
                field="score"
                label="Signal"
                currentSort={sortBy}
                sortDir={sortDir}
                onSort={onSort}
              />
              <th className="px-4 py-3 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider hidden xl:table-cell">
                RSI
              </th>
              <th className="px-4 py-3 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider hidden md:table-cell">
                Trend Fire
              </th>
              <th className="px-4 py-3 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider hidden lg:table-cell">
                Funding
              </th>
              <th className="px-4 py-3 text-left text-[10px] font-semibold text-slate-400 uppercase tracking-wider w-10">
                {/* Expand column */}
              </th>
            </tr>
          </thead>
          <tbody>
            {assets.map((asset, index) => (
              <TableRow
                key={asset.symbol}
                asset={asset}
                index={index}
                isExpanded={expandedRow === asset.symbol}
                onToggle={() => handleToggle(asset.symbol)}
              />
            ))}
          </tbody>
        </table>
      </div>

      {assets.length === 0 && (
        <div className="text-center py-12 text-slate-500">
          No assets match your filters
        </div>
      )}
    </motion.div>
  );
}
