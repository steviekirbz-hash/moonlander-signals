'use client';

import { motion } from 'framer-motion';

export function LoadingSkeleton() {
  return (
    <div className="min-h-screen bg-slate-950 text-white">
      {/* Header skeleton */}
      <div className="border-b border-slate-800/50 bg-slate-950/80">
        <div className="max-w-7xl mx-auto px-4 py-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl skeleton" />
              <div>
                <div className="h-5 w-40 skeleton rounded mb-1" />
                <div className="h-3 w-32 skeleton rounded" />
              </div>
            </div>
            <div className="flex items-center gap-4">
              <div className="h-4 w-24 skeleton rounded" />
              <div className="w-8 h-8 skeleton rounded-lg" />
            </div>
          </div>
        </div>
      </div>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {/* Stats cards skeleton */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 mb-6">
          {[1, 2, 3, 4].map((i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1 }}
              className="bg-gradient-to-br from-slate-900 to-slate-800 rounded-xl p-4 border border-slate-700/50"
            >
              <div className="w-10 h-10 skeleton rounded-lg mb-2" />
              <div className="h-6 w-16 skeleton rounded mb-1" />
              <div className="h-3 w-24 skeleton rounded" />
            </motion.div>
          ))}
        </div>

        {/* Sentiment bar skeleton */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 rounded-2xl p-6 border border-slate-700/50 mb-6"
        >
          <div className="flex items-center justify-between mb-6">
            <div>
              <div className="h-3 w-24 skeleton rounded mb-2" />
              <div className="h-8 w-32 skeleton rounded" />
            </div>
            <div className="flex gap-6">
              {[1, 2, 3].map((i) => (
                <div key={i} className="text-center">
                  <div className="h-6 w-8 skeleton rounded mb-1 mx-auto" />
                  <div className="h-3 w-12 skeleton rounded" />
                </div>
              ))}
            </div>
          </div>
          <div className="h-4 skeleton rounded-full" />
        </motion.div>

        {/* Filter controls skeleton */}
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.4 }}
          className="flex flex-col md:flex-row gap-3 mb-4"
        >
          <div className="h-10 w-48 skeleton rounded-lg" />
          <div className="flex gap-2">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="h-8 w-16 skeleton rounded-lg" />
            ))}
          </div>
          <div className="h-8 w-32 skeleton rounded-lg" />
        </motion.div>

        {/* Table skeleton */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5 }}
          className="bg-gradient-to-br from-slate-900/80 to-slate-900/40 rounded-2xl border border-slate-800/50 overflow-hidden"
        >
          {/* Table header */}
          <div className="border-b border-slate-700/50 bg-slate-900/50 px-4 py-3">
            <div className="flex gap-4">
              {[1, 2, 3, 4, 5, 6].map((i) => (
                <div key={i} className="h-4 w-16 skeleton rounded" />
              ))}
            </div>
          </div>

          {/* Table rows */}
          {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
            <motion.div
              key={i}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 + i * 0.05 }}
              className="border-b border-slate-800/50 px-4 py-3"
            >
              <div className="flex items-center gap-4">
                <div className="w-9 h-9 skeleton rounded-lg" />
                <div className="flex-1">
                  <div className="h-4 w-16 skeleton rounded mb-1" />
                  <div className="h-3 w-24 skeleton rounded" />
                </div>
                <div className="h-6 w-20 skeleton rounded-lg" />
                <div className="h-4 w-24 skeleton rounded hidden md:block" />
                <div className="h-4 w-16 skeleton rounded hidden lg:block" />
              </div>
            </motion.div>
          ))}
        </motion.div>
      </main>
    </div>
  );
}
