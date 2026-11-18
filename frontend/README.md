# LapVisualizer Frontend

React + TypeScript single-page app (Vite) for browsing and visualizing lap data
served by the LapVisualizer FastAPI backend. Uses React Router for navigation
and Recharts for charts.

## Setup

```bash
npm install
```

## Development

```bash
npm run dev
```

Starts the Vite dev server. Requests to `/api/*` are proxied to the backend at
`http://localhost:8000` (see `vite.config.ts`), so the backend must be running
(for example via `docker compose up -d server` from the repo root). No CORS
configuration is needed.

## Build

```bash
npm run build
```

Type-checks with `tsc -b` and produces a production bundle in `dist/`.

## Test

```bash
npm test
```

Runs the Vitest + React Testing Library suite (`npm test -- --run` for a single pass).

## Lint

```bash
npm run lint
```
