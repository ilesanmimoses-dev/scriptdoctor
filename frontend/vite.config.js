import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    proxy: {
      '/analyze': 'http://127.0.0.1:8000',
      '/ai-summary': 'http://127.0.0.1:8000',
      '/upload': 'http://127.0.0.1:8000',
      '/health': 'http://127.0.0.1:8000',
      '/signup': 'http://127.0.0.1:8000',
      '/login': 'http://127.0.0.1:8000',
      '/history': 'http://127.0.0.1:8000',
      '/admin-stats': 'http://127.0.0.1:8000',
      '/schedule': 'http://127.0.0.1:8000',
      '/explain': 'http://127.0.0.1:8000',
      '/coverage': 'http://127.0.0.1:8000',
      '/report': 'http://127.0.0.1:8000',
      '/admin-reports': 'http://127.0.0.1:8000',
      '/compare': 'http://127.0.0.1:8000'
    }
  }
})