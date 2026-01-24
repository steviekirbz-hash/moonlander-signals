'use client';

import { motion } from 'framer-motion';
import { Search } from 'lucide-react';
import { FilterType } from '@/lib/types';

interface FilterControlsProps {
  filter: FilterType;
  setFilter: (filter: FilterType) => void;
  categoryFilter: string;
  setCategoryFilter: (category: string) => void;
  searchQuery: string;
  setSearchQuery: (query: string) => void;
  categories: string[];
  filteredCount: number;
  totalCount: number;
}

export function FilterControls({
  filter,
  setFilter,
  categoryFilter,
  setCategoryFilter,
  searchQuery,
  setSearchQuery,
  categories,
  filteredCount,
  totalCount,
}: FilterControlsProps) {
  const filters: { key: FilterType; label: string }[] = [
    { key: 'all', label: 'All' },
    { key: 'strong', label: 'Strong' },
    { key: 'long', label: 'Long' },
    { key: 'short', label: 'Short' },
    { key: 'neutral', label: 'Neutral' },
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.3 }}
      className="flex flex-col md:flex-row gap-3 mb-4"
    >
      {/* Search */}
      <div className="relative flex-1 max-w-xs">
        <Search size={16} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-500" />
        <input
          type="text"
          placeholder="Search assets..."
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          className="w-full pl-10 pr-4 py-2 bg-slate-800/50 border border-slate-700 rounded-lg text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500/50 transition-colors"
        />
      </div>

      {/* Signal Filter Buttons */}
      <div className="flex gap-2 flex-wrap">
        {filters.map(({ key, label }) => (
          <motion.button
            key={key}
            onClick={() => setFilter(key)}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
              filter === key
                ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/50'
                : 'bg-slate-800/50 text-slate-400 border border-slate-700 hover:border-slate-600'
            }`}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
          >
            {label}
          </motion.button>
        ))}
      </div>

      {/* Category Dropdown */}
      <select
        value={categoryFilter}
        onChange={(e) => setCategoryFilter(e.target.value)}
        className="px-3 py-1.5 bg-slate-800/50 border border-slate-700 rounded-lg text-xs text-slate-400 focus:outline-none focus:border-cyan-500/50 cursor-pointer"
      >
        <option value="all">All Categories</option>
        {categories.map((cat) => (
          <option key={cat} value={cat}>
            {cat}
          </option>
        ))}
      </select>

      {/* Results count */}
      <div className="hidden md:flex items-center text-xs text-slate-500 ml-auto">
        Showing {filteredCount} of {totalCount} assets
      </div>
    </motion.div>
  );
}
