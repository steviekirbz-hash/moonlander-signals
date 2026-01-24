'use client';

import { motion } from 'framer-motion';

export function Footer() {
  return (
    <motion.footer
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5, delay: 0.8 }}
      className="mt-8 text-center text-slate-600 text-xs"
    >
      <p>Data refreshes hourly • Not financial advice • Trade at your own risk</p>
      <p className="mt-1">
        Powered by Binance API • Built for{' '}
        <a
          href="https://moonlander.trade"
          target="_blank"
          rel="noopener noreferrer"
          className="text-cyan-500 hover:text-cyan-400 transition-colors"
        >
          moonlander.trade
        </a>
      </p>
    </motion.footer>
  );
}
