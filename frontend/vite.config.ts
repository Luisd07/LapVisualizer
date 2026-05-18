import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Any request to /api/* is forwarded to the FastAPI backend, so the
      // frontend never needs the backend's absolute URL — and there are no
      // CORS issues during development.
      '/api': 'http://localhost:8000',
    },
  },
})
