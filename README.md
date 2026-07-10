# Titan Deals — Frontend

Retail intelligence platform frontend. Search-first UI over an embedded
SQLite FTS5 backend — no cloud search service, no heavyweight JS runtime
on the data path.

## Stack

- Next.js 15 (App Router) + TypeScript
- Tailwind CSS
- Framer Motion (minimal, purposeful)
- Lucide icons

## Pages

- `/` — landing page: hero, live stats, architecture/moat section, trending
- `/deals` — search results with filters (store, discount, distance, category)
- `/dashboard` — live metrics, regional activity, recent ingestion table

## Run locally

```bash
npm install
npm run dev
```

Visit `http://localhost:3000`.

## Deploy to Vercel

1. Push this repo to GitHub:
   ```bash
   git init
   git remote add origin https://github.com/juliushill42/titan-deals-platform.git
   git add .
   git commit -m "Add Titan Deals intelligence frontend"
   git branch -M main
   git push -u origin main
   ```
2. In Vercel: **Import Repository** → framework auto-detected as Next.js.
3. Set the custom domain to `deals.titanuniversalai.com`.
4. Copy `.env.example` to `.env.local` and point `NEXT_PUBLIC_TITAN_API_URL`
   at the live FastAPI/SQLite FTS5 backend once it's wired in.

## Wiring in real data

All deal, stat, and heat map data currently lives in `lib/data.ts` as typed
mock data matching the shape the backend should return. Replace the static
imports in `app/deals/page.tsx`, `app/dashboard/page.tsx`, and
`components/Stats.tsx` with fetch calls to `NEXT_PUBLIC_TITAN_API_URL` —
the types in `lib/data.ts` (`Deal`, `stats` shape, `heatmap` shape) are the
contract the backend should match.

## Design system

| Token      | Value     |
|------------|-----------|
| Background | `#050505` |
| Panels     | `#101010` |
| Borders    | `#202020` |
| Titan Cyan | `#00D8FF` |
| Highlight  | `#00FFFF` |
| Green      | `#2EEA7D` |

Headings/body: Geist. Numbers/data: JetBrains Mono (loaded via CSS
variables in `app/globals.css` — swap in `next/font` for production if
you want self-hosted font files instead of a CDN).
