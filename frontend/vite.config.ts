import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
    },
  },
  server: {
    port: 5173,
    proxy: {
      '/health': 'http://localhost:5000',
      '/stocks': 'http://localhost:5000',
      '/history': 'http://localhost:5000',
      '/technical': 'http://localhost:5000',
      '/analytics': 'http://localhost:5000',
      '/forecast': 'http://localhost:5000',
      '/train': 'http://localhost:5000',
      '/metrics': 'http://localhost:5000',
      '/watchlist': 'http://localhost:5000',
    },
  },
})
