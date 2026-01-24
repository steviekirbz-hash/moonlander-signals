import type { Metadata } from 'next';
import { Inter, JetBrains_Mono, Space_Grotesk } from 'next/font/google';
import './globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
});

const jetbrainsMono = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-jetbrains',
});

const spaceGrotesk = Space_Grotesk({
  subsets: ['latin'],
  variable: '--font-space-grotesk',
});

export const metadata: Metadata = {
  title: 'Moonlander Signals | Multi-Timeframe Crypto Intelligence',
  description: 'Real-time trading signals for Moonlander crypto assets. Multi-timeframe analysis with RSI, EMA, MACD, and funding rate indicators.',
  keywords: ['crypto', 'trading', 'signals', 'moonlander', 'bitcoin', 'ethereum', 'technical analysis'],
  authors: [{ name: 'Moonlander Signals' }],
  openGraph: {
    title: 'Moonlander Signals',
    description: 'Multi-Timeframe Crypto Trading Intelligence',
    type: 'website',
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={`${inter.variable} ${jetbrainsMono.variable} ${spaceGrotesk.variable}`}>
      <body className="font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
