import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Proxy all /api/* requests to the backend during development
      // This avoids CORS issues and SSE buffering problems
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        // Critical for SSE (Server-Sent Events) — disable response buffering
        configure: (proxy) => {
          proxy.on('proxyRes', (proxyRes) => {
            // Remove any content-encoding that could buffer SSE stream
            if (proxyRes.headers['content-type']?.includes('text/event-stream')) {
              delete proxyRes.headers['content-encoding'];
            }
          });
        },
      },
    },
  },
})
