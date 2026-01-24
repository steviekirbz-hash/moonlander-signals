# 🌙 Moonlander Signals - Frontend

A Next.js 14 frontend for displaying crypto trading signals with a premium dark theme, dynamic animations, and real-time data visualization.

## ✨ Features

- **Dark Premium UI** - Sleek crypto-native design with neon accents
- **Dynamic Animations** - Smooth transitions powered by Framer Motion
- **Animated Background** - Floating gradient orbs and grid pattern
- **7-Tier Signal Scoring** - From Strong Short (-3) to Strong Long (+3)
- **Multi-Timeframe RSI** - Visual display across 15m, 1h, 4h, 1d
- **Fire Indicators** 🔥 - Shows timeframe alignment at a glance
- **Expandable Rows** - Click for detailed indicator breakdown
- **Responsive Design** - Works on mobile, tablet, and desktop
- **Search & Filter** - Find assets by name, category, or signal type

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) to view the app.

### Build for Production

```bash
npm run build
npm start
```

## 🌐 Deploy to Vercel

The easiest way to deploy is with Vercel:

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com)
3. Import your repository
4. Deploy!

Or use the Vercel CLI:

```bash
npm i -g vercel
vercel
```

## ⚙️ Configuration

### Environment Variables

Create a `.env.local` file:

```env
# API URL - your backend API endpoint
NEXT_PUBLIC_API_URL=https://your-api.com

# Demo mode - set to "true" for generated data (no API needed)
NEXT_PUBLIC_DEMO_MODE=false
```

### Demo Mode

By default, the frontend runs in demo mode with generated data. This is perfect for:
- Testing the UI without a backend
- Deploying a demo version
- Development

To connect to a real API:
1. Set `NEXT_PUBLIC_API_URL` to your backend URL
2. Set `NEXT_PUBLIC_DEMO_MODE=false`

## 📁 Project Structure

```
frontend/
├── app/
│   ├── globals.css      # Global styles + Tailwind
│   ├── layout.tsx       # Root layout with fonts
│   └── page.tsx         # Main page component
├── components/
│   ├── AnimatedBackground.tsx
│   ├── Header.tsx
│   ├── StatsCards.tsx
│   ├── MarketSentiment.tsx
│   ├── FilterControls.tsx
│   ├── SignalsTable.tsx
│   ├── SignalIndicators.tsx
│   ├── ExpandedRow.tsx
│   ├── Legend.tsx
│   ├── Footer.tsx
│   ├── LoadingSkeleton.tsx
│   └── index.ts
├── lib/
│   ├── api.ts           # API client + demo data generator
│   └── types.ts         # TypeScript types
├── package.json
├── tailwind.config.js
├── next.config.js
└── vercel.json
```

## 🎨 Customization

### Colors

Edit `tailwind.config.js` to customize the color palette:

```js
colors: {
  midnight: { /* dark backgrounds */ },
  neon: { /* accent colors */ },
  signal: { /* score colors */ },
}
```

### Fonts

The app uses three font families:
- **Inter** - Body text
- **JetBrains Mono** - Numbers and code
- **Space Grotesk** - Headlines

Change them in `app/layout.tsx`.

### Animations

Animation settings are in `tailwind.config.js` under `animation` and `keyframes`.

## 🔗 API Integration

The frontend expects the following API endpoints:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/signals` | GET | Get all signals |
| `/signals/{symbol}` | GET | Get single asset |
| `/categories` | GET | Get category breakdown |

See the backend README for full API documentation.

## 📱 Responsive Breakpoints

| Breakpoint | Width | Notes |
|------------|-------|-------|
| Mobile | < 640px | Simplified table, stacked layout |
| Tablet | 640-1024px | Most columns visible |
| Desktop | > 1024px | Full table with all columns |

## 🧪 Development Tips

1. **Hot Reload** - Changes reflect instantly in dev mode
2. **Demo Data** - Refresh to get new random data in demo mode
3. **TypeScript** - Full type safety throughout
4. **Component Dev** - Each component is self-contained

## 📄 License

MIT - Feel free to use and modify!

---

Built with ❤️ for [moonlander.trade](https://moonlander.trade)
