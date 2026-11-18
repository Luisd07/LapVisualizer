import { defineConfig } from 'vitest/config'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  test: {
    environment: 'jsdom',
    setupFiles: './src/test/setup.ts',
  },
  server: {
    proxy: {
      // Any request to /api/* is forwarded to the FastAPI backend, so the
      // frontend never needs the backend's absolute URL — and there are no
      // CORS issues during development.
      '/api': 'http://localhost:8000',
    },
  },
})
