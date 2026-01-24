'use client';

import { useState, useEffect, useMemo } from 'react';
import { fetchSignals } from '@/lib/api';
import { SignalsResponse, FilterType, SortField, SortDirection, Asset } from '@/lib/types';
import {
  AnimatedBackground,
  Header,
  StatsCards,
  MarketSentiment,
  FilterControls,
  SignalsTable,
  Legend,
  Footer,
  LoadingSkeleton,
} from '@/components';

export default function HomePage() {
  const [data, setData] = useState<SignalsResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter state
  const [filter, setFilter] = useState<FilterType>('all');
  const [categoryFilter, setCategoryFilter] = useState('all');
  const [searchQuery, setSearchQuery] = useState('');
  
  // Sort state
  const [sortBy, setSortBy] = useState<SortField>('score');
  const [sortDir, setSortDir] = useState<SortDirection>('desc');

  // Fetch data
  const loadData = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const signals = await fetchSignals();
      setData(signals);
    } catch (err) {
      setError('Failed to load signals. Please try again.');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Get unique categories
  const categories = useMemo(() => {
    if (!data) return [];
    const cats = new Set(data.assets.map((a) => a.category));
    return Array.from(cats).sort();
  }, [data]);

  // Filter and sort assets
  const filteredAssets = useMemo(() => {
    if (!data) return [];

    let assets = [...data.assets];

    // Apply signal filter
    switch (filter) {
      case 'long':
        assets = assets.filter((a) => a.score > 0);
        break;
      case 'short':
        assets = assets.filter((a) => a.score < 0);
        break;
      case 'neutral':
        assets = assets.filter((a) => a.score === 0);
        break;
      case 'strong':
        assets = assets.filter((a) => Math.abs(a.score) >= 2);
        break;
    }

    // Apply category filter
    if (categoryFilter !== 'all') {
      assets = assets.filter((a) => a.category === categoryFilter);
    }

    // Apply search
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      assets = assets.filter(
        (a) =>
          a.symbol.toLowerCase().includes(query) ||
          a.name.toLowerCase().includes(query)
      );
    }

    // Sort
    assets.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'score':
          comparison = a.score - b.score || a.composite_score - b.composite_score;
          break;
        case 'symbol':
          comparison = a.symbol.localeCompare(b.symbol);
          break;
        case 'price':
          comparison = a.price - b.price;
          break;
        case 'change_24h':
          comparison = a.change_24h - b.change_24h;
          break;
      }
      
      return sortDir === 'desc' ? -comparison : comparison;
    });

    return assets;
  }, [data, filter, categoryFilter, searchQuery, sortBy, sortDir]);

  const handleSort = (field: SortField) => {
    if (sortBy === field) {
      setSortDir(sortDir === 'desc' ? 'asc' : 'desc');
    } else {
      setSortBy(field);
      setSortDir('desc');
    }
  };

  const handleRefresh = () => {
    loadData();
  };

  // Show loading skeleton
  if (isLoading && !data) {
    return <LoadingSkeleton />;
  }

  // Show error
  if (error && !data) {
    return (
      <div className="min-h-screen bg-slate-950 text-white flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-400 mb-4">{error}</p>
          <button
            onClick={handleRefresh}
            className="px-4 py-2 bg-cyan-500 hover:bg-cyan-600 rounded-lg transition-colors"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <AnimatedBackground />
      
      <div className="relative z-10">
        <Header
          lastUpdate={data.generated_at}
          isLoading={isLoading}
          onRefresh={handleRefresh}
        />

        <main className="max-w-7xl mx-auto px-4 py-6">
          <StatsCards
            summary={data.summary}
            totalAssets={data.total_assets}
          />

          <MarketSentiment
            summary={data.summary}
            totalAssets={data.total_assets}
          />

          <FilterControls
            filter={filter}
            setFilter={setFilter}
            categoryFilter={categoryFilter}
            setCategoryFilter={setCategoryFilter}
            searchQuery={searchQuery}
            setSearchQuery={setSearchQuery}
            categories={categories}
            filteredCount={filteredAssets.length}
            totalCount={data.total_assets}
          />

          {/* Mobile results count */}
          <div className="md:hidden text-xs text-slate-500 mb-3">
            Showing {filteredAssets.length} of {data.total_assets} assets
          </div>

          <SignalsTable
            assets={filteredAssets}
            sortBy={sortBy}
            sortDir={sortDir}
            onSort={handleSort}
          />

          <Legend />

          <Footer />
        </main>
      </div>
    </div>
  );
}
